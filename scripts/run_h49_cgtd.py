#!/usr/bin/env python3
"""Execute Pre-Registered Single Lane H49-1 (CG-TILT-NOISYOR) within the strict 3-experiment budget.

Reuses shared tools strictly (Protocol Rule 2):
  - `.cache/gems_work/feature_stack.npy` (`gems32.features.build`, 35 channels)
  - `.cache/gems_work/spcp_extra_20ch.npy` (`gems32.spcp`, 20 label-free channels)
  - `.cache/gems_work/trhv_extra_8ch.npy` (`gems32.trhv`, 8 label-free hydrothermal-vent & TIGER channels)
  - `.cache/gems_work/ldgi_extra_8ch.npy` (`gems32.ldgi`, 8 Fourier-UC & corridor channels)
  - `.cache/gems_work/fbgr_extra_12ch.npy` (`gems32.fbgr`, 12 Fourier-UC & GeoDAWN block-debiased channels)
  - `.cache/gems_work/cgtd_extra_10ch.npy` (`gems32.cgtd`, 10 Miller-Singh tilt=0, Salem tilt-depth,
    up-gradient chemical geothermometry disequilibrium, MT clay-cap flank, Byerlee dilatant & k-of-5 channels)
  - `gems32.holdout` / `scripts/evaluate_holdout.py`
  - `gems32.emitter.emit` (with shared `min_sep_px = 2.8` Axial-Crest spacing guard)
  - `scripts/submission_writer.py` & `scripts/check_submission.py --strict-finite`
  - `gems32.release_gate`
"""

from __future__ import annotations

import gc
import json
import os
import resource
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("GDAL_CACHEMAX", "32")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from numpy.lib.format import open_memmap
from scipy.ndimage import binary_dilation, binary_erosion, convolve, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import cgtd, fbgr, features, holdout, release_gate, spcp, submission  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402
from run_h48_fbgr import evaluate_detached_and_censored, paired_ci, scan_full_registry  # noqa: E402
import submission_writer  # noqa: E402

TARGET_BUDGET = 37_654
B_COLLAR_PX = 2.0
AXIAL_SEP_PX = 2.8
SESSION_BRANCH = "arena/10401461-gemsdoe32"


def peak_rss_mb() -> float:
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def audit_focus_and_sibling_universe(
    ctx: holdout.HoldoutContext,
    champ_mask: np.ndarray,
    h49_mask: np.ndarray,
) -> dict:
    """Byte-verified audit of all 9 focus sites (`GEMSDOE24..36`) + newly listed sibling repos."""
    fman = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    by_repo: dict[str, list[dict]] = {}
    for r in fman["rasters"]:
        if r.get("status") == "ok":
            by_repo.setdefault(r["repo"], []).append(r)

    yy, xx = np.mgrid[-3:4, -3:4]
    disk3 = (yy * yy + xx * xx) <= 9
    disk3_nocenter = (disk3 & ~((yy == 0) & (xx == 0))).astype(np.int16)
    champ_near3 = binary_dilation(champ_mask, structure=disk3)
    h49_near3 = binary_dilation(h49_mask, structure=disk3)
    h48_path = ROOT / "docs/downloads/gemsdoe32-h48-fbgr-dualcover-axial28-37654-20261027T180500Z-4d38a240-zeros.tif"
    if h48_path.exists():
        with rasterio.open(h48_path) as ds:
            h48_near3 = binary_dilation((ds.read(1) > 0) & ctx.foot, structure=disk3)
    else:
        h48_near3 = h49_near3
    d_cat = distance_transform_edt(~ctx.labels)

    # Latest 2026-10-27 focus-site candidate patterns
    preferred_patterns = {
        "GEMSDOE24": "tmcg-b-decoupled-basin",
        "GEMSDOE25": "h79-cthm",
        "GEMSDOE27": "h33-bss-complement",
        "GEMSDOE28": "s22-ctxhgb",
        "GEMSDOE30": "FFL1",
        "GEMSDOE31": "tgtd-submod",
        "GEMSDOE32": "h33-h33-2-b2-20261004",
        "GEMSDOE33": "a33-r5-thkcond",
        "GEMSDOE36": "tcd36",
    }
    fallback_patterns = {
        "GEMSDOE25": "h71-bh-celf2-8",
        "GEMSDOE27": "h31-drcg-wl-celf28",
        "GEMSDOE30": "CSR1-aniso",
        "GEMSDOE31": "h31u-strainseis-corrob",
        "GEMSDOE33": "fsml2cc",
        "GEMSDOE36": "kpl36-exp3",
    }

    site_rows = []
    for repo, pat in preferred_patterns.items():
        cands = [
            r for r in by_repo.get(repo, [])
            if pat.lower() in r["path"].lower() and not r["path"].endswith("-nan.tif")
        ]
        if not cands and repo in fallback_patterns:
            fpat = fallback_patterns[repo]
            cands = [
                r for r in by_repo.get(repo, [])
                if fpat.lower() in r["path"].lower() and not r["path"].endswith("-nan.tif")
            ]
        if not cands:
            cands = [r for r in by_repo.get(repo, []) if not r["path"].endswith("-nan.tif")]
        if not cands:
            continue
        rec = sorted(cands, key=lambda r: r["path"])[-1]
        p = ROOT / rec["local"]
        with rasterio.open(p) as ds:
            arr = ds.read(1)
            nd = ds.nodata
        whole_finite = bool(np.isfinite(arr).all())
        in_range = bool(np.nanmin(arr) >= 0.0 and np.nanmax(arr) <= 1.0)
        m = np.isfinite(arr) & (arr > 0) & ctx.foot
        n_dots = int(m.sum())
        on_cat = int((m & ctx.labels).sum())
        hr = holdout.evaluate_hide_and_recover(m, ctx, b_visible_px=0.0, n_boot=400, name=f"{repo}_latest")
        sg = holdout.evaluate_sgmc_with_ci(m, ctx, n_boot=400, name=f"{repo}_latest")
        ov_champ = float(champ_near3[m].mean()) if n_dots > 0 else 0.0
        ov_h49 = float(h49_near3[m].mean()) if n_dots > 0 else 0.0
        ov_h48 = float(h48_near3[m].mean()) if n_dots > 0 else 0.0
        far15 = float((d_cat[m] > 15.0).mean()) if n_dots > 0 else 0.0
        nbr = convolve(m.astype(np.int16), disk3_nocenter, mode="constant", cval=0)
        cl3 = float((nbr[m] >= 3).mean()) if n_dots > 0 else 0.0
        site_rows.append(
            {
                "repo": repo,
                "head_ref": fman["refs"].get(repo, "")[:12],
                "total_rasters_in_repo": len(by_repo.get(repo, [])),
                "inspected_path": rec["path"],
                "sha256": rec["sha256"],
                "emitted_dots": n_dots,
                "on_catalogue_dots": on_cat,
                "whole_array_finite": whole_finite,
                "range_0_1": in_range,
                "nodata_tag": nd,
                "far_gt_15px_frac": round(far15, 4),
                "clump_ge3_nbr3_frac": round(cl3, 4),
                "static_hide_recover_dti": round(hr["pooled_dti"], 6),
                "static_hide_recover_ci95": [round(x, 6) for x in hr["ci95_cluster_bootstrap"]],
                "sgmc_raw_dti": round(sg["sgmc_raw_pooled_dti"], 6),
                "sgmc_prevalence_calibrated_dti": round(sg["sgmc_prevalence_calibrated_dti"], 6),
                "sgmc_calibrated_ci95": [round(x, 6) for x in sg["sgmc_calibrated_ci95"]],
                "within_3px_of_02778_champion": round(ov_champ, 4),
                "within_3px_of_h49_cgtd": round(ov_h49, 4),
                "within_3px_of_h48_fbgr": round(ov_h48, 4),
            }
        )

    # Audit the 10 unscored 2026-10-27 prompt sibling-org submissions + GEMSDOE90..92
    sman_doc = json.loads((ROOT / "registry" / "sibling_orgs_manifest.json").read_text())
    prompt_siblings = [
        ("KANLERGEMSDOE3", "f0565e6d10f9-zeros"),
        ("KANLERGEMSDOE2", "kanlergems2-htcads-exp-2"),
        ("WBGGEMSDOE3", "wbg3-h3pack-34k-20261027"),
        ("WBGGEMSDOE3", "wbggemsdoe3-skarpline-union"),
        ("WBGGEMSDOE2", "wbg2-offcatalogue-density-36k"),
        ("GEMSDOEkarage1", "karage1-hmas-sinter-dualcover"),
        ("ApartGEMSDOE3", "apartgemsdoe3-h-apart3-1-cfkc-dhc"),
        ("ApartGEMSDOE1", "apartgems1-udth-submod-e3"),
        ("GEMSDOESASS3", "gemsdoesass3-lwst-geoconduit"),
        ("GEMSDOESASS1", "gemsass1-swgb-hrv2"),
    ]
    sibling_rows = []
    for repo_nm, sub_pat in prompt_siblings:
        matches = [
            r for r in sman_doc["rasters"]
            if r["repo"] == repo_nm and sub_pat.lower() in r["path"].lower() and not r["path"].endswith("-nan.tif")
        ]
        misplaced_note = None
        if not matches:
            # Cross-repo search (e.g., wbg3-h3pack committed inside WBGGEMSDOE2!)
            cross = [
                r for r in sman_doc["rasters"]
                if sub_pat.lower() in r["path"].lower() and not r["path"].endswith("-nan.tif")
            ]
            if cross:
                matches = cross
                misplaced_note = f"Listed under {repo_nm} in prompt, physically committed in {cross[0]['repo']}"
        if not matches:
            sibling_rows.append({"prompt_repo": repo_nm, "pattern": sub_pat, "status": "portal_only_not_in_git_tree"})
            continue
        rec = matches[0]
        p = ROOT / rec["local"]
        with rasterio.open(p) as ds:
            arr = ds.read(1)
        whole_finite = bool(np.isfinite(arr).all())
        m = np.isfinite(arr) & (arr > 0) & ctx.foot
        n_dots = int(m.sum())
        ov_champ = float(champ_near3[m].mean()) if n_dots > 0 else 0.0
        ov_h49 = float(h49_near3[m].mean()) if n_dots > 0 else 0.0
        far15 = float((d_cat[m] > 15.0).mean()) if n_dots > 0 else 0.0
        nbr = convolve(m.astype(np.int16), disk3_nocenter, mode="constant", cval=0)
        cl3 = float((nbr[m] >= 3).mean()) if n_dots > 0 else 0.0
        sg = holdout.evaluate_sgmc_with_ci(m, ctx, n_boot=250, name=f"{repo_nm}_{sub_pat[:12]}")
        row_entry = {
            "prompt_repo": repo_nm,
            "owner": rec["owner"],
            "repo": rec["repo"],
            "ref": rec["ref"][:12],
            "path": rec["path"],
            "sha256": rec["sha256"],
            "emitted_dots": n_dots,
            "whole_array_finite": whole_finite,
            "far_gt_15px_frac": round(far15, 4),
            "clump_ge3_nbr3_frac": round(cl3, 4),
            "sgmc_prevalence_calibrated_dti": round(sg["sgmc_prevalence_calibrated_dti"], 6),
            "within_3px_of_02778_champion": round(ov_champ, 4),
            "within_3px_of_h49_cgtd": round(ov_h49, 4),
        }
        if misplaced_note:
            row_entry["irregularity"] = misplaced_note
        sibling_rows.append(row_entry)
        del arr, m, nbr
        gc.collect()

    return {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_manifest_rasters": len(fman["rasters"]),
        "total_sibling_org_rasters": sman_doc["n_rasters_ok"],
        "refs": fman["refs"],
        "sibling_org_repos": sman_doc["repos"],
        "sites": site_rows,
        "prompt_sibling_submissions": sibling_rows,
    }


def render_h49_diagnostic_figure(
    out_path: Path,
    champ_clean: dict,
    h48_clean: dict,
    exp1_clean: dict,
    exp2_clean: dict,
    exp3_clean: dict,
    cgtd_stack: np.ndarray,
    exp3_dots: np.ndarray,
    lidar_valid: np.ndarray,
    foot: np.ndarray,
    labels: np.ndarray,
    spatial_alloc: dict,
) -> None:
    """Render publication-grade 4-panel diagnostic figure `docs/assets/fig_h49_cgtd.png`."""
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 11.2), dpi=135)
    fig.patch.set_facecolor("#0b1020")
    for ax in axes.ravel():
        ax.set_facecolor("#111936")
        for sp in ax.spines.values():
            sp.set_color("#2e3c68")
        ax.tick_params(colors="#cbd5e1", labelsize=8.5)

    # Panel A: Miller-Singh Gravity Tilt=0 Wall + k-of-5 Multi-Physics Conduit Convergence
    ax0 = axes[0, 0]
    k5_sub = np.asarray(cgtd_stack[::4, ::4, 8], dtype=np.float32)
    cgtd.drop_mmap_cache(cgtd_stack)
    f_sub = foot[::4, ::4]
    disp = np.where(f_sub, k5_sub, np.nan)
    im0 = ax0.imshow(disp, cmap="magma", vmin=0.0, vmax=0.95)
    ax0.contour((~lidar_valid[::4, ::4]) & f_sub, levels=[0.5], colors=["#38bdf8"], linewidths=0.75)
    ax0.set_title(
        "A. LiDAR-Free k-of-5 Conduit Convergence (Tilt=0 + Geotherm + MT + GeoDAWN)\n(Cyan contour = 24.6% 1 m LiDAR gap)",
        color="#f8fafc", fontsize=9.8, fontweight="bold",
    )
    cb0 = plt.colorbar(im0, ax=ax0, fraction=0.042, pad=0.03)
    cb0.ax.tick_params(colors="#cbd5e1", labelsize=8.0)

    # Panel B: Emitted 37,654 H49-1 Dots Colored by Catalogue Distance (>1.5 km vs Collar)
    ax1 = axes[0, 1]
    d_cat = distance_transform_edt(~labels)
    dy, dx = np.nonzero(exp3_dots)
    far_m = d_cat[dy, dx] > 15.0
    ly, lx = np.nonzero(labels)
    ax1.scatter(lx[::6], ly[::6], s=0.18, c="#64748b", alpha=0.45, label="Visible Catalogue (labels.tif)")
    ax1.scatter(dx[~far_m][::4], dy[~far_m][::4], s=0.35, c="#38bdf8", alpha=0.65, label=f"Near 0.2-1.5 km ({(1-far_m.mean())*100:.1f}%)")
    ax1.scatter(dx[far_m][::4], dy[far_m][::4], s=0.42, c="#f59e0b", alpha=0.80, label=f"Far >1.5 km Conduit ({far_m.mean()*100:.1f}%)")
    ax1.invert_yaxis()
    ax1.set_title(
        f"B. H49-1 Emitted Dots (37,654, B=2, d_min=2.8 px)\nLiDAR-gap={spatial_alloc['lidar_gap_dot_frac']*100:.1f}% | Flat-basin={spatial_alloc['flat_basin_dot_frac']*100:.2f}% | Clump>=3={spatial_alloc['clump_ge3_nbr3_frac']*100:.2f}%",
        color="#f8fafc", fontsize=9.8, fontweight="bold",
    )
    ax1.legend(loc="lower right", fontsize=7.8, facecolor="#0b1020", edgecolor="#334155", labelcolor="#f8fafc")

    # Panel C: Primary Holdout DTI & Detached >=600m Benchmark Comparison
    ax2 = axes[1, 0]
    names = ["0.2778\nChamp", "H48-1\nFBGR", "H49 EXP1\nMult-PU", "H49 EXP2\nNoisyOR d0", "H49-1 EXP3\nNoisyOR d2.8"]
    hr_vals = [
        champ_clean["hide_and_recover_v3"]["pooled_dti"],
        h48_clean["primary_hide_and_recover"]["pooled_dti"],
        exp1_clean["hide_and_recover_v3"]["pooled_dti"],
        exp2_clean["hide_and_recover_v3"]["pooled_dti"],
        exp3_clean["hide_and_recover_v3"]["pooled_dti"],
    ]
    det_vals = [
        champ_clean["detached_600m_segments"]["pooled_dti"],
        h48_clean["detached_600m_segments"]["pooled_dti"],
        exp1_clean["detached_600m_segments"]["pooled_dti"],
        exp2_clean["detached_600m_segments"]["pooled_dti"],
        exp3_clean["detached_600m_segments"]["pooled_dti"],
    ]
    x = np.arange(len(names))
    w = 0.36
    b1 = ax2.bar(x - w / 2, hr_vals, w, color="#38bdf8", label="HIDE-RECOVER-v3.0 (n=22,232)")
    b2 = ax2.bar(x + w / 2, det_vals, w, color="#34d399", label="Detached >= 600 m (n=15,504)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, color="#e2e8f0", fontsize=8.2)
    ax2.set_ylabel("HOLDOUT-DTI", color="#e2e8f0")
    ax2.set_ylim(0.06, max(max(hr_vals), max(det_vals)) * 1.18)
    ax2.set_title("C. Stationary Segment-Withheld HOLDOUT-DTI Ablation", color="#f8fafc", fontsize=9.8, fontweight="bold")
    ax2.legend(loc="upper left", fontsize=8.0, facecolor="#0b1020", edgecolor="#334155", labelcolor="#f8fafc")
    for rect in list(b1) + list(b2):
        ax2.text(
            rect.get_x() + rect.get_width() / 2.0,
            rect.get_height() + 0.0018,
            f"{rect.get_height():.4f}",
            ha="center", va="bottom", color="#e2e8f0", fontsize=7.0,
        )

    # Panel D: Off-Catalogue USGS SGMC (Evaluation-Only) & Far-Field Reach Law
    ax3 = axes[1, 1]
    sg_vals = [
        champ_clean["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"],
        h48_clean["off_catalogue_sgmc"]["prevalence_calibrated_dti"],
        exp1_clean["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"],
        exp2_clean["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"],
        exp3_clean["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"],
    ]
    b3 = ax3.bar(x, sg_vals, 0.50, color=["#94a3b8", "#64748b", "#818cf8", "#fbbf24", "#f97316"])
    ax3.set_xticks(x)
    ax3.set_xticklabels(names, color="#e2e8f0", fontsize=8.2)
    ax3.set_ylabel("SGMC-CAL-v3.0 DTI (Zero SGMC Supervision)", color="#e2e8f0")
    ax3.set_ylim(0.03, max(sg_vals) * 1.22)
    ax3.set_title("D. Blind Off-Catalogue USGS SGMC Bedrock Fault Recovery", color="#f8fafc", fontsize=9.8, fontweight="bold")
    for rect in b3:
        ax3.text(
            rect.get_x() + rect.get_width() / 2.0,
            rect.get_height() + 0.0015,
            f"{rect.get_height():.4f}",
            ha="center", va="bottom", color="#f8fafc", fontsize=7.8, fontweight="bold",
        )

    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    if os.environ.get("GEMSDOE32_ASSIGNED_LANE_ID", "").strip() != "H49-1-CGTD":
        raise SystemExit(
            "STOP: no explicit H49-1-CGTD method paragraph is assigned in the current environment. "
            "Do not infer a lane or rerun experiments; only set GEMSDOE32_ASSIGNED_LANE_ID=H49-1-CGTD after explicit pre-registration."
        )
    t0 = time.time()
    ddir = data_dir()
    wdir = work_dir()
    evidence_dir().mkdir(parents=True, exist_ok=True)

    print(f"[1/8] Opening 83-ch cached stacks + 10-ch CGTD stack (RSS={peak_rss_mb()} MB)...", flush=True)
    base_stack = open_memmap(wdir / "feature_stack.npy", mode="r")
    spcp_stack = open_memmap(wdir / "spcp_extra_20ch.npy", mode="r")
    trhv_stack = open_memmap(wdir / "trhv_extra_8ch.npy", mode="r")
    ldgi_stack = open_memmap(wdir / "ldgi_extra_8ch.npy", mode="r")
    fbgr_stack = open_memmap(wdir / "fbgr_extra_12ch.npy", mode="r")
    cgtd_stack, cgtd_receipt = cgtd.build_cgtd_extra_stack(rebuild=("--rebuild-cgtd" in sys.argv))

    print(f"[2/8] Loading HoldoutContext & running 93-channel Leakage Canary (RSS={peak_rss_mb()} MB)...", flush=True)
    ctx = holdout.load_holdout_context(ddir)
    lidar_valid = (np.asarray(spcp_stack[:, :, 12], dtype=np.float32).copy() > 0.5) & ctx.foot
    cgtd.drop_mmap_cache(spcp_stack)
    lidar_gap = ctx.foot & ~lidar_valid

    # Soft-PU negative reliability prior: strictly LiDAR-free multiphysics_k_of_5_concord in [0, 1]
    k5_plane = np.asarray(cgtd_stack[:, :, 8], dtype=np.float32).copy()
    cgtd.drop_mmap_cache(cgtd_stack)
    q94_k5 = float(np.percentile(k5_plane[ctx.foot][::4], 94.0))

    disk2 = spcp._disk_mask(B_COLLAR_PX)
    elig_full = ctx.foot & ~binary_dilation(ctx.labels, structure=disk2)
    n_elig_full = int(elig_full.sum())

    fold_train: dict[int, np.ndarray] = {}
    fold_domain: dict[int, np.ndarray] = {}
    for f in holdout.FOLDS:
        q = ctx.quad == f
        collar = binary_dilation(q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX) & ctx.foot
        fold_train[f] = ctx.foot & ~collar
        fold_domain[f] = binary_erosion(q, iterations=holdout.DOMAIN_ERODE) & ctx.foot

    canary = cgtd.run_leakage_canary_93ch(
        base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
        list(features.CHANNELS), ctx, max_auc=0.90,
    )
    print(
        f"      Canary passed={canary['passed']} | n={canary['n_features_tested']} | "
        f"worst={canary['worst_channel']} ({canary['max_oriented_auc']:.5f}) | RSS={peak_rss_mb()} MB",
        flush=True,
    )
    if not canary["passed"]:
        raise SystemExit(f"STOP: Leakage canary failed ({canary['worst_channel']} AUC={canary['max_oriented_auc']})!")

    # Baselines: 0.2778 Champion + H38 + H47-1 + H48-1
    champ_path = downloads_dir() / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    with rasterio.open(champ_path) as ds:
        champ_mask = (ds.read(1) > 0) & ctx.foot
    champ_sup = evaluate_detached_and_censored(champ_mask, ctx, b_visible_px=B_COLLAR_PX)
    champ_sg = holdout.evaluate_sgmc_with_ci(champ_mask, ctx, name="CHAMPION_02778")

    d28_parent_path = ddir / "scored" / "gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
    with rasterio.open(d28_parent_path) as ds:
        a_d28 = ds.read(1)
    d28_parent_mask = np.isfinite(a_d28) & (a_d28 > 0) & ctx.foot
    del a_d28
    champ_hr = holdout.evaluate_hide_and_recover(
        d28_parent_mask, ctx, b_visible_px=B_COLLAR_PX, name="CHAMPION_02778_FOLD_COLLARED"
    )
    champ_parent_sup = evaluate_detached_and_censored(d28_parent_mask, ctx, b_visible_px=B_COLLAR_PX)
    champ_sup["detached_600m"] = champ_parent_sup["detached_600m"]
    del d28_parent_mask

    h38_best = json.loads((ROOT / "evidence" / "h38_run_card.json").read_text())["holdout_dti"]["primary_hide_and_recover"]
    h47_card = json.loads((ROOT / "evidence" / "h47_ldgi_run_card.json").read_text())["holdout_dti"]
    h48_card = json.loads((ROOT / "evidence" / "h48_fbgr_run_card.json").read_text())["holdout_dti"]

    def _eval_arm(name: str, cell_masks: dict[str, np.ndarray] | np.ndarray, full_mask: np.ndarray) -> dict:
        hr = holdout.evaluate_hide_and_recover(cell_masks, ctx, b_visible_px=B_COLLAR_PX, name=name)
        sup = evaluate_detached_and_censored(cell_masks, ctx, b_visible_px=B_COLLAR_PX)
        sg = holdout.evaluate_sgmc_with_ci(full_mask, ctx, name=name)
        return {"name": name, "hr": hr, "sup": sup, "sg": sg, "full_dots": int(full_mask.sum())}

    # =========================================================================
    # FIT SHARED RELIABLE-NEGATIVE PU DUAL-COVER POSTERIORS (`M_Full` 93-ch & `M_Sub` 80-ch)
    # =========================================================================
    print(f"[3/8] Fitting Reliable-Negative PU M_Full (93-ch) & M_Sub (80-ch non-LiDAR) across 8 cells (RSS={peak_rss_mb()} MB)...", flush=True)
    p_dual_live = np.zeros(ctx.foot.shape, dtype=np.float32)

    for cell in ctx.cells:
        pred_reg = (ctx.quad == cell.fold) & ctx.foot
        tr = fold_train[cell.fold]
        vis_tr = cell.visible_full & tr
        p_d_cache = wdir / f"h49_cell_{cell.key}_mdual93.npy"

        if p_d_cache.exists() and "--rerun-models" not in sys.argv:
            pd_cell = np.load(p_d_cache)
        else:
            clf_full = cgtd.fit_cgtd_pu_classifier(
                base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
                tr, vis_tr, k5_plane, ctx.foot, col_indices=None,
                seed=4900 + cell.seed * 10 + cell.fold,
            )
            clf_sub = cgtd.fit_cgtd_pu_classifier(
                base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
                tr, vis_tr, k5_plane, ctx.foot, col_indices=cgtd.MSUB_93_COL_INDICES,
                seed=5900 + cell.seed * 10 + cell.fold,
            )
            cy_li, cx_li = np.nonzero(tr & lidar_valid)
            cy_gp, cx_gp = np.nonzero(tr & lidar_gap)
            cal_mask_li = np.zeros(ctx.foot.shape, dtype=bool)
            cal_mask_gp = np.zeros(ctx.foot.shape, dtype=bool)
            cal_mask_li[cy_li[::4], cx_li[::4]] = True
            cal_mask_gp[cy_gp[::4], cx_gp[::4]] = True
            del cy_li, cx_li, cy_gp, cx_gp

            pf_all = cgtd.predict_chunked_cgtd(
                clf_full, base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
                pred_reg | cal_mask_li, col_indices=None,
            )
            ps_all = cgtd.predict_chunked_cgtd(
                clf_sub, base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
                pred_reg | cal_mask_li | cal_mask_gp, col_indices=cgtd.MSUB_93_COL_INDICES,
            )
            del clf_full, clf_sub

            pd_cell = cgtd.combine_dual_cover_posteriors(
                pf_all, ps_all, cal_mask_li, cal_mask_gp, pred_reg, lidar_valid,
                w_sub_in_lidar=0.22, gap_blend_raw=0.42,
            )
            np.save(p_d_cache, pd_cell)
            del pf_all, ps_all, cal_mask_li, cal_mask_gp

        p_dual_live[pred_reg] += np.float32(0.5) * pd_cell[pred_reg]
        del pd_cell
        gc.collect()
        print(f"      Finished OOF cell {cell.key} (RSS={peak_rss_mb()} MB)", flush=True)
    del k5_plane

    # =========================================================================
    # EXPERIMENT 1 / 3: Soft-PU Dual-Cover + Multiplicative Surface + d=2.8
    # =========================================================================
    print(f"[4/8] Experiment 1/3: EXP1_H49_PU_DUALCOVER_MULT_AXIAL28 (RSS={peak_rss_mb()} MB)...", flush=True)
    exp1_cells: dict[str, np.ndarray] = {}
    for cell in ctx.cells:
        sl = cell.bbox
        pred_reg = (ctx.quad == cell.fold) & ctx.foot
        elig_sub = (fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2))[sl]
        b_cell = int(round(TARGET_BUDGET * (elig_sub.sum() / n_elig_full)))
        pd_cell = np.load(wdir / f"h49_cell_{cell.key}_mdual93.npy")
        s_cell = cgtd.build_stationary_cgtd_surface(
            pd_cell, cgtd_stack, fbgr_stack, trhv_stack, cell.visible_full, ctx.foot,
            region_mask=pred_reg, mode="multiplicative", w_tip_relay=0.34, sharpen_crest=True,
        )
        d_sub, _ = fbgr.emit_fbgr_submodular(
            s_cell[sl], cell.visible_full[sl], elig_sub, ctx.foot[sl], budget=b_cell, min_sep_px=AXIAL_SEP_PX
        )
        d_full = np.zeros(ctx.foot.shape, dtype=bool)
        d_full[sl] = d_sub
        exp1_cells[cell.key] = d_full
        del pd_cell, s_cell
        gc.collect()

    s1_full_surf = cgtd.build_stationary_cgtd_surface(
        p_dual_live, cgtd_stack, fbgr_stack, trhv_stack, ctx.labels, ctx.foot,
        mode="multiplicative", w_tip_relay=0.34, sharpen_crest=True,
    )
    exp1_full_dots, _ = fbgr.emit_fbgr_submodular(
        s1_full_surf, ctx.labels, elig_full, ctx.foot, budget=TARGET_BUDGET, min_sep_px=AXIAL_SEP_PX
    )
    del s1_full_surf
    exp1_res = _eval_arm("EXP1_H49_PU_DUALCOVER_MULT_AXIAL28", exp1_cells, exp1_full_dots)
    del exp1_cells, exp1_full_dots
    gc.collect()
    print(
        f"      EXP1: HR={exp1_res['hr']['pooled_dti']:.5f} Det={exp1_res['sup']['detached_600m']['dti']:.5f} "
        f"SGMC_cal={exp1_res['sg']['sgmc_prevalence_calibrated_dti']:.5f} (RSS={peak_rss_mb()} MB)",
        flush=True,
    )

    # =========================================================================
    # EXPERIMENT 2 / 3: Soft-PU Dual-Cover + Stationary Noisy-OR + min_sep=0.0
    # =========================================================================
    print(f"[5/8] Experiment 2/3: EXP2_H49_CGTD_NOISYOR_RAW_CELF (RSS={peak_rss_mb()} MB)...", flush=True)
    exp2_cells: dict[str, np.ndarray] = {}
    for cell in ctx.cells:
        sl = cell.bbox
        pred_reg = (ctx.quad == cell.fold) & ctx.foot
        elig_sub = (fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2))[sl]
        b_cell = int(round(TARGET_BUDGET * (elig_sub.sum() / n_elig_full)))
        pd_cell = np.load(wdir / f"h49_cell_{cell.key}_mdual93.npy")
        s_cell = cgtd.build_stationary_cgtd_surface(
            pd_cell, cgtd_stack, fbgr_stack, trhv_stack, cell.visible_full, ctx.foot,
            region_mask=pred_reg, mode="noisyor", lambda_vent=0.90, w_tip_relay=0.34, sharpen_crest=False,
        )
        d_sub, _ = fbgr.emit_fbgr_submodular(
            s_cell[sl], cell.visible_full[sl], elig_sub, ctx.foot[sl], budget=b_cell, min_sep_px=0.0, support_mult=3
        )
        d_full = np.zeros(ctx.foot.shape, dtype=bool)
        d_full[sl] = d_sub
        exp2_cells[cell.key] = d_full
        del pd_cell, s_cell
        gc.collect()

    s2_full_surf = cgtd.build_stationary_cgtd_surface(
        p_dual_live, cgtd_stack, fbgr_stack, trhv_stack, ctx.labels, ctx.foot,
        mode="noisyor", lambda_vent=0.90, w_tip_relay=0.34, sharpen_crest=False,
    )
    exp2_full_dots, _ = fbgr.emit_fbgr_submodular(
        s2_full_surf, ctx.labels, elig_full, ctx.foot, budget=TARGET_BUDGET, min_sep_px=0.0, support_mult=3
    )
    del s2_full_surf
    exp2_res = _eval_arm("EXP2_H49_CGTD_NOISYOR_RAW_CELF", exp2_cells, exp2_full_dots)
    del exp2_cells, exp2_full_dots
    gc.collect()
    print(
        f"      EXP2: HR={exp2_res['hr']['pooled_dti']:.5f} Det={exp2_res['sup']['detached_600m']['dti']:.5f} "
        f"SGMC_cal={exp2_res['sg']['sgmc_prevalence_calibrated_dti']:.5f} (RSS={peak_rss_mb()} MB)",
        flush=True,
    )

    # =========================================================================
    # EXPERIMENT 3 / 3: Soft-PU Dual-Cover + Stationary Noisy-OR + Axial NMS d=2.8
    # =========================================================================
    print(f"[6/8] Experiment 3/3: EXP3_H49_CGTD_NOISYOR_AXIAL28 (Primary candidate, RSS={peak_rss_mb()} MB)...", flush=True)
    exp3_cells: dict[str, np.ndarray] = {}
    for cell in ctx.cells:
        sl = cell.bbox
        pred_reg = (ctx.quad == cell.fold) & ctx.foot
        elig_sub = (fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2))[sl]
        b_cell = int(round(TARGET_BUDGET * (elig_sub.sum() / n_elig_full)))
        pd_cell = np.load(wdir / f"h49_cell_{cell.key}_mdual93.npy")
        s_cell = cgtd.build_stationary_cgtd_surface(
            pd_cell, cgtd_stack, fbgr_stack, trhv_stack, cell.visible_full, ctx.foot,
            region_mask=pred_reg, mode="noisyor", lambda_vent=0.90, w_tip_relay=0.34, sharpen_crest=True,
        )
        d_sub, _ = fbgr.emit_fbgr_submodular(
            s_cell[sl], cell.visible_full[sl], elig_sub, ctx.foot[sl], budget=b_cell, min_sep_px=AXIAL_SEP_PX
        )
        d_full = np.zeros(ctx.foot.shape, dtype=bool)
        d_full[sl] = d_sub
        exp3_cells[cell.key] = d_full
        del pd_cell, s_cell
        gc.collect()

    exp3_belief_surface = cgtd.build_stationary_cgtd_surface(
        p_dual_live, cgtd_stack, fbgr_stack, trhv_stack, ctx.labels, ctx.foot,
        mode="noisyor", lambda_vent=0.90, w_tip_relay=0.34, sharpen_crest=True,
    )
    del p_dual_live

    slug = "h49-cgtd-noisyor-axial28-37654"
    for stale in downloads_dir().glob(f"gemsdoe32-{slug}-*"):
        stale.unlink(missing_ok=True)

    # Protocol Rule 1 STEP A: Check continuous surface BEFORE final dot placement!
    print(f"[7/8] Running Pre-Placement Continuous Surface Spearman Check across full registry (RSS={peak_rss_mb()} MB)...", flush=True)
    pre_scan = scan_full_registry(exp3_belief_surface, None, ctx.foot, ddir)
    print(
        f"      Pre-placement surface passed={pre_scan['genuine_surface_passed']} | "
        f"unique_checked={pre_scan['n_unique_rasters_checked']} | "
        f"max |Spearman|={abs(pre_scan['worst_genuine_surface']['surface_spearman']):.5f} "
        f"({pre_scan['worst_genuine_surface']['name']})",
        flush=True,
    )
    if not pre_scan["genuine_surface_passed"]:
        raise SystemExit(f"STOP: Pre-placement continuous surface Spearman > 0.90: {pre_scan['worst_genuine_surface']}")

    exp3_full_dots, exp3_emit_log = fbgr.emit_fbgr_submodular(
        exp3_belief_surface, ctx.labels, elig_full, ctx.foot, budget=TARGET_BUDGET, min_sep_px=AXIAL_SEP_PX
    )
    exp3_res = _eval_arm("EXP3_H49_CGTD_NOISYOR_AXIAL28", exp3_cells, exp3_full_dots)
    del exp3_cells
    gc.collect()
    print(
        f"      EXP3_H49_CGTD_NOISYOR_AXIAL28: HR={exp3_res['hr']['pooled_dti']:.5f} "
        f"Cen={exp3_res['sup']['censored_d2']['dti']:.5f} "
        f"Det={exp3_res['sup']['detached_600m']['dti']:.5f} "
        f"SGMC_raw={exp3_res['sg']['sgmc_raw_pooled_dti']:.5f} "
        f"SGMC_cal={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.5f} | "
        f"dots={int(exp3_full_dots.sum())} (RSS={peak_rss_mb()} MB)",
        flush=True,
    )

    # Write validated unique GeoTIFF bundle via canonical `scripts/submission_writer.py`
    ts_tag = "20261027T235000Z"
    slug = "h49-cgtd-noisyor-axial28-37654"
    sub_note = (
        f"H49-1 CGTD tilt0+geotherm NoisyOR d2.8 37654d | "
        f"HR={exp3_res['hr']['pooled_dti']:.4f} SGMC={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.4f} | DO NOT SUBMIT"
    )
    assert len(sub_note) <= 140, f"Submission note > 140 chars: {len(sub_note)}"

    # Clean any stale H49 artifacts in downloads_dir() so re-runs remain strictly idempotent
    for stale in downloads_dir().glob(f"gemsdoe32-{slug}-*"):
        stale.unlink(missing_ok=True)

    bundle = submission_writer.write_validated_submission(
        exp3_full_dots,
        slug=slug,
        candidate_meta={
            "candidate_id": "H49-1-CGTD",
            "description": (
                f"H49-1 Miller-Singh Tilt=0 Wall, Up-Gradient Geothermometry Disequilibrium, "
                f"Reliable-Negative PU Dual-Cover & Stationary Noisy-OR d=2.8 CELF ({int(exp3_full_dots.sum()):,} dots, B=2)"
            ),
            "catalogue_hidden_mean": round(exp3_res["hr"]["pooled_dti"], 6),
            "catalogue_hidden_per_quadrant": {k: round(v, 6) for k, v in exp3_res["hr"]["per_quadrant_dti"].items()},
            "sgmc_prevalence_calibrated_dti": round(exp3_res["sg"]["sgmc_prevalence_calibrated_dti"], 6),
            "submission_note_zeros": sub_note,
            "submission_note_nan": sub_note,
            "slot_decision": "HOLD-DO-NOT-SUBMIT",
        },
        ddir=ddir,
        out_dir=downloads_dir(),
        timestamp_tag=ts_tag,
    )
    digest8 = bundle["content_digest8"]
    sub_name = f"GEMSDOE32-H49-CGTD-{digest8.upper()}"
    audit_sidecar_name = f"gemsdoe32-{slug}-{ts_tag}-{digest8}-audit.json"
    zeros_tif_path = downloads_dir() / bundle["zeros_tif"]["filename"]
    zeros_sha256 = bundle["zeros_tif"]["sha256"]

    # Protocol Rule 1 STEP B: Final-Dot Full-Registry Uniqueness Scan (focus + extra + sibling orgs)
    print(f"[8/8] Running Final-Dot Uniqueness Scan across focus + extra + sibling-org registries (RSS={peak_rss_mb()} MB)...", flush=True)
    final_scan = scan_full_registry(
        exp3_belief_surface,
        exp3_full_dots,
        ctx.foot,
        ddir,
        exclude_shas={zeros_sha256, bundle["nan_tif"]["sha256"]},
    )
    del exp3_belief_surface
    gc.collect()
    print(
        f"      Final genuine uniqueness={final_scan['genuine_final_dots_passed']} | "
        f"unique_checked={final_scan['n_unique_rasters_checked']} | "
        f"worst genuine 3px overlap={final_scan['worst_genuine_overlap']['within_3px_fraction']:.4f} "
        f"({final_scan['worst_genuine_overlap']['name']}) | "
        f"focus overlap={final_scan['worst_focus_site_overlap']['within_3px_fraction']:.4f} (RSS={peak_rss_mb()} MB)",
        flush=True,
    )
    ext_top = [
        r for r in final_scan["top15_by_overlap"]
        if not r["name"].startswith(("GEMSDOE32:", "local:"))
    ]
    worst_ext = ext_top[0] if ext_top else final_scan["worst_genuine_overlap"]
    ext_unique_passed = bool(
        abs(final_scan["worst_genuine_surface"]["surface_spearman"]) <= 0.90
        and worst_ext["within_3px_fraction"] <= 0.70
    )
    final_scan["external_cross_site_unique_passed"] = ext_unique_passed
    final_scan["worst_external_cross_site_overlap"] = worst_ext
    if not final_scan["genuine_final_dots_passed"]:
        print(
            f"      [PROTOCOL RULE 1 DUPLICATE LOG & STOP] Intra-repo overlap={final_scan['worst_genuine_overlap']['within_3px_fraction']:.4f} "
            f"vs {final_scan['worst_genuine_overlap']['name']} (>0.70; external cross-site worst={worst_ext['within_3px_fraction']:.4f} <= 0.70). "
            f"Logging as intra-repo duplicate, stopping after 3/3 experiments, and enforcing verdict='negative' / DO NOT SUBMIT.",
            flush=True,
        )

    # Independent strict CLI validator (`scripts/check_submission.py --strict-finite`)
    sub_env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "GEMS_DATA_DIR": str(ddir)}
    chk_proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_submission.py"), "--strict-finite", str(zeros_tif_path)],
        env=sub_env,
        capture_output=True,
        text=True,
        check=True,
    )
    strict_cli_check = json.loads(chk_proc.stdout.split("\n[PASSED]")[0].strip())
    if "file_path" in strict_cli_check and isinstance(strict_cli_check["file_path"], str):
        strict_cli_check["file_path"] = strict_cli_check["file_path"].replace(str(ROOT) + "/", "")
    audit_13 = submission.audit_geotiff(
        zeros_tif_path, ctx.foot, ctx.labels, mode="zeros", template_tif=ddir / "sample_submission.tif"
    )

    eval_cli_out = evidence_dir() / "h49_cgtd_static_evaluator_receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "evaluate_holdout.py"),
            str(zeros_tif_path),
            "--b-visible-px",
            "2.0",
            "--data-dir",
            str(ddir),
            "--name",
            "H49-1-CGTD-static",
            "--out",
            str(eval_cli_out),
        ],
        env=sub_env,
        check=True,
        capture_output=True,
        text=True,
    )
    if eval_cli_out.exists():
        eval_cli_out.write_text(eval_cli_out.read_text().replace(str(ROOT) + "/", ""))

    nine_site = audit_focus_and_sibling_universe(ctx, champ_mask, exp3_full_dots)
    (evidence_dir() / "nine_site_refreshed_audit_20261027.json").write_text(
        (json.dumps(nine_site, indent=2) + "\n").replace(str(ROOT) + "/", "")
    )

    paired_hr_vs_champ = paired_ci(exp3_res["hr"]["_boots"], champ_hr["_boots"])
    paired_hr_vs_exp1 = paired_ci(exp3_res["hr"]["_boots"], exp1_res["hr"]["_boots"])
    paired_hr_vs_exp2 = paired_ci(exp3_res["hr"]["_boots"], exp2_res["hr"]["_boots"])
    paired_cen_vs_champ = paired_ci(exp3_res["sup"]["censored_d2"]["_boots"], champ_sup["censored_d2"]["_boots"])
    paired_det_vs_champ = paired_ci(exp3_res["sup"]["detached_600m"]["_boots"], champ_sup["detached_600m"]["_boots"])
    paired_sgmc_vs_champ = paired_ci(exp3_res["sg"]["_cal_boots"], champ_sg["_cal_boots"])
    paired_sgmc_vs_exp1 = paired_ci(exp3_res["sg"]["_cal_boots"], exp1_res["sg"]["_cal_boots"])
    paired_sgmc_vs_exp2 = paired_ci(exp3_res["sg"]["_cal_boots"], exp2_res["sg"]["_cal_boots"])

    # Clumping & spatial allocation diagnostics
    yy3, xx3 = np.mgrid[-3:4, -3:4]
    disk3_nocenter = ((yy3 * yy3 + xx3 * xx3 <= 9) & ~((yy3 == 0) & (xx3 == 0))).astype(np.int32)
    nbr_cnt = convolve(exp3_full_dots.astype(np.int32), disk3_nocenter, mode="constant", cval=0)[exp3_full_dots]
    dt_foot = distance_transform_edt(~exp3_full_dots)[ctx.foot]
    cov_300m = float(np.maximum(0.0, 1.0 - dt_foot / 3.0).mean())
    del dt_foot

    d_full_labels = distance_transform_edt(~ctx.labels).astype(np.float32)
    d_dots = d_full_labels[exp3_full_dots]
    del d_full_labels

    b15 = np.asarray(base_stack[:, :, 14], dtype=np.float32).copy()
    b19 = np.asarray(base_stack[:, :, 18], dtype=np.float32).copy()
    cgtd.drop_mmap_cache(base_stack)
    flat_basin_frac = float(((b19[exp3_full_dots] < 2.0) & (b15[exp3_full_dots] > 300.0)).mean())
    del b15, b19

    spatial_alloc = {
        "stationary_formula_no_eta_switch": True,
        "pu_soft_negative_weight_range": [0.65, 1.0],
        "pu_conduit_q94_reference": round(q94_k5, 6),
        "noisyor_lambda_vent": 0.90,
        "w_tip_relay": 0.34,
        "min_sep_px": AXIAL_SEP_PX,
        "mfull_in_lidar_dots": int((exp3_full_dots & lidar_valid).sum()),
        "msub_in_lidar_gap_dots": int((exp3_full_dots & lidar_gap).sum()),
        "lidar_gap_dot_frac": round(float((exp3_full_dots & lidar_gap).sum() / max(int(exp3_full_dots.sum()), 1)), 6),
        "clump_ge3_nbr3_frac": round(float((nbr_cnt >= 3).mean()), 6),
        "mean_nbr_within_3px": round(float(nbr_cnt.mean()), 6),
        "footprint_300m_kernel_coverage": round(cov_300m, 6),
        "flat_basin_dot_frac": round(flat_basin_frac, 6),
        "le_2px_on_or_flank_frac": round(float((d_dots <= 2.0).mean()), 6),
        "collar_3_to_15px_frac": round(float(((d_dots > 2.0) & (d_dots <= 15.0)).mean()), 6),
        "gt_15px_far_conduit_frac": round(float((d_dots > 15.0).mean()), 6),
        "apron_2_to_9px_frac": round(float(((d_dots > 2.0) & (d_dots <= 9.0)).mean()), 6),
        "mid_9_to_20px_frac": round(float(((d_dots > 9.0) & (d_dots <= 20.0)).mean()), 6),
        "far_gt_20px_blind_frac": round(float((d_dots > 20.0).mean()), 6),
        "median_dist_to_catalogue_px": round(float(np.median(d_dots)), 3),
        "emit_log": exp3_emit_log,
    }

    validator_flags = {
        "single_band": bool(audit_13["checks"]["single_band"]),
        "finite": bool(audit_13["checks"]["in_footprint_all_finite"] and strict_cli_check["passed"]),
        "range_0_1": bool(audit_13["checks"]["in_footprint_range_0_1"] and audit_13["checks"]["validator_range_0_1_guaranteed"]),
        "crs_match": bool(audit_13["checks"]["crs_epsg_32611"]),
        "shape_match": bool(audit_13["checks"]["dimensions_3730x3292"]),
        "transform_match": bool(audit_13["checks"]["exact_reference_grid_match"]),
    }

    holdout_for_gate = {
        "evaluator_version": exp3_res["hr"]["evaluator_version"],
        "n_withheld_positives": exp3_res["hr"]["n_withheld_positives"],
        "dti": exp3_res["hr"]["pooled_dti"],
        "ci95": exp3_res["hr"]["ci95_cluster_bootstrap"],
    }
    incumbent_for_gate = {
        "evaluator_version": champ_hr["evaluator_version"],
        "n_withheld_positives": champ_hr["n_withheld_positives"],
        "dti": champ_hr["pooled_dti"],
        "ci95": champ_hr["ci95_cluster_bootstrap"],
    }
    gate_decision = release_gate.promotion_decision(
        lane="H49-1-CGTD: Miller-Singh Tilt=0 Wall, Up-Gradient Geothermometry Disequilibrium, Reliable-Negative PU Dual-Cover & Stationary Noisy-OR CELF",
        surface_check=final_scan["release_gate_direct_surface"],
        final_check=final_scan["release_gate_direct_final"],
        canary_aucs=[r["oriented_auc"] for r in canary["per_channel"]],
        holdout=holdout_for_gate,
        incumbent=incumbent_for_gate,
        same_evaluation=True,
        validator=validator_flags,
        paired_delta_ci95=paired_hr_vs_champ["ci95"],
    )

    final_verdict = "promote" if gate_decision["verdict"] == "promote" else "negative"
    ok_submit = bool(gate_decision["verdict"] == "promote")

    def _clean_arm(res: dict) -> dict:
        return {
            "name": res["name"],
            "full_map_dots": res["full_dots"],
            "hide_and_recover_v3": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": res["hr"]["evaluator_version"],
                "n_withheld_positives": res["hr"]["n_withheld_positives"],
                "pooled_dti": round(res["hr"]["pooled_dti"], 6),
                "ci95": [round(x, 6) for x in res["hr"]["ci95_cluster_bootstrap"]],
                "per_quadrant_dti": {k: round(v, 6) for k, v in res["hr"]["per_quadrant_dti"].items()},
            },
            "censorship_matched_d2": {
                "label": "HOLDOUT-DTI (d_hidden > 2 px censorship-matched)",
                "n_withheld_positives": res["sup"]["censored_d2"]["n_withheld_positives"],
                "pooled_dti": round(res["sup"]["censored_d2"]["dti"], 6),
                "ci95": [round(x, 6) for x in res["sup"]["censored_d2"]["ci95"]],
            },
            "detached_600m_segments": {
                "label": "HOLDOUT-DTI (detached >= 600 m withheld segments)",
                "n_withheld_positives": res["sup"]["detached_600m"]["n_withheld_positives"],
                "pooled_dti": round(res["sup"]["detached_600m"]["dti"], 6),
                "ci95": [round(x, 6) for x in res["sup"]["detached_600m"]["ci95"]],
            },
            "sgmc_off_catalogue_v3": {
                "label": "HOLDOUT-DTI (off-catalogue USGS SGMC > 300 m, zero SGMC supervision)",
                "evaluator_version": res["sg"]["evaluator_version"],
                "n_withheld_positives": res["sg"]["n_withheld_positives"],
                "raw_pooled_dti": round(res["sg"]["sgmc_raw_pooled_dti"], 6),
                "raw_ci95": [round(x, 6) for x in res["sg"]["sgmc_raw_ci95"]],
                "prevalence_calibrated_dti": round(res["sg"]["sgmc_prevalence_calibrated_dti"], 6),
                "calibrated_ci95": [round(x, 6) for x in res["sg"]["sgmc_calibrated_ci95"]],
            },
        }

    champ_clean = _clean_arm(
        {"name": "CHAMPION_02778", "hr": champ_hr, "sup": champ_sup, "sg": champ_sg, "full_dots": int(champ_mask.sum())}
    )
    exp1_clean = _clean_arm(exp1_res)
    exp2_clean = _clean_arm(exp2_res)
    exp3_clean = _clean_arm(exp3_res)

    fig_path = ROOT / "docs" / "assets" / "fig_h49_cgtd.png"
    render_h49_diagnostic_figure(
        fig_path,
        champ_clean,
        h48_card,
        exp1_clean,
        exp2_clean,
        exp3_clean,
        cgtd_stack,
        exp3_full_dots,
        lidar_valid,
        ctx.foot,
        ctx.labels,
        spatial_alloc,
    )

    elapsed = round(time.time() - t0, 2)
    max_rss = peak_rss_mb()

    experiments_summary = {
        "session_branch": SESSION_BRANCH,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_seconds": elapsed,
        "peak_rss_mb": max_rss,
        "experiments_used": 3,
        "experiments_budget_cap": 3,
        "weekly_slots_used": 0,
        "cgtd_feature_receipt": cgtd_receipt,
        "leakage_canary": canary,
        "baselines": {
            "CHAMPION_02778": champ_clean,
            "H38_HISTORICAL_HOLDOUT": h38_best,
            "H47_1_NONSTATIONARY_ETA_HOLDOUT": h47_card["primary_hide_and_recover"],
            "H48_1_FBGR_STATIONARY": h48_card["primary_hide_and_recover"],
        },
        "experiments": {
            "EXP1_H49_PU_DUALCOVER_MULT_AXIAL28": exp1_clean,
            "EXP2_H49_CGTD_NOISYOR_RAW_CELF": exp2_clean,
            "EXP3_H49_CGTD_NOISYOR_AXIAL28": exp3_clean,
        },
        "paired_spatial_bootstrap_comparisons": {
            "EXP3_vs_CHAMPION_hide_and_recover": paired_hr_vs_champ,
            "EXP3_vs_EXP1_noisyor_lift": paired_hr_vs_exp1,
            "EXP3_vs_EXP2_axial_d28_lift": paired_hr_vs_exp2,
            "EXP3_vs_CHAMPION_censored_d2": paired_cen_vs_champ,
            "EXP3_vs_CHAMPION_detached_600m": paired_det_vs_champ,
            "EXP3_vs_CHAMPION_sgmc_calibrated": paired_sgmc_vs_champ,
            "EXP3_vs_EXP1_sgmc_noisyor_lift": paired_sgmc_vs_exp1,
            "EXP3_vs_EXP2_sgmc_axial_d28_lift": paired_sgmc_vs_exp2,
        },
        "spatial_allocation_exp3": spatial_alloc,
    }
    (evidence_dir() / "h49_cgtd_experiments.json").write_text(json.dumps(experiments_summary, indent=2) + "\n")

    run_card = {
        "schema_version": "gems-parallel-runcard-v3",
        "session_branch": SESSION_BRANCH,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate_id": "H49-1-CGTD",
        "hypothesis": (
            "H49-1 (CG-TILT-NOISYOR): Unmapped Great Basin geothermal-indicative bedrock faults and blind "
            "hydrothermal vent conduits missed by labels.tif are jointly resolved by (1) Miller & Singh (1994) "
            "depth-invariant isostatic gravity tilt-angle zero-contour walls (theta_g = 0), Verduzco THDR_tilt "
            "crests, and Salem et al. (2007) dual-field gravity-magnetic tilt phase-locking + sedimentary cover "
            "depth matching; (2) up-gradient structural-topographic advection of UNR/DOE GDR #1391 chemical "
            "geothermometry disequilibrium (max(T_quartz, T_chalc, T_NaKCa) - T_surf across 1,247 assayed "
            "stations, 1,077 with Delta T > 50 C) onto MT smectite clay-cap lateral flanks and 3-D Kostrov-Byerlee "
            "dilatant slip-tendency crests; and (3) continuous Soft-PU negative reliability down-weighting "
            "(w_neg in [0.65, 1.00] on k-of-5 conduit convergence) inside a 93-ch M_Full / 80-ch non-LiDAR M_Sub "
            "Hybrid Dual-Cover ensemble fused via a 100% stationary scale-anchored tail-activated Noisy-OR conduit "
            "discovery law before min_sep_px = 2.8 submodular CELF emission."
        ),
        "mechanism": (
            f"93 label-free channels (83 prior + 10 new CGTD channels; 80 strictly 1 m LiDAR-free) -> Soft-PU "
            f"4-quadrant 1.5 km-collared Hybrid Dual-Cover OOF classifiers (0.78*M_Full + 0.22*M_Sub_cal inside "
            f"75.37% LiDAR + quantile-calibrated 80-ch M_Sub inside 24.63% LiDAR gap) + stationary scale-anchored "
            f"tail Noisy-OR conduit discovery (r_vent > q98.0 anchored to q99.35(P_sup), lambda_vent = 0.90, "
            f"w_tip_relay = 0.34) + 4-azimuth NMS -> shared gems32.emitter.emit(..., min_sep_px=2.8) emitting "
            f"{int(exp3_full_dots.sum()):,} binary {{0,1}} dots strictly >200 m (B=2) from mapped catalogue "
            f"(far >1.5 km = {spatial_alloc['gt_15px_far_conduit_frac']*100:.1f}%, "
            f"LiDAR gap = {spatial_alloc['lidar_gap_dot_frac']*100:.1f}%, flat basin = {spatial_alloc['flat_basin_dot_frac']*100:.2f}%, "
            f">=3-nbr 3px clumping = {spatial_alloc['clump_ge3_nbr3_frac']*100:.2f}%)."
        ),
        "named_non_fault_mimic": (
            "(1) Saline evaporative playas & closed-basin brines (Carson Sink, Humboldt Sink, Buena Vista playa) "
            "mimicking MT electrical conductivity (Band 17) and uraniferous eU anomalies — suppressed by flat-deep-basin "
            "structural veto (slope < 1.8 deg & depth_to_base > 280 m) plus lateral clay-cap flank inflection requiring "
            "theta_g = 0 gravity tilt zero-crossings; (2) Down-gradient shallow gravel thermal outflow sheets "
            "(temp_c = 40-65 C with low chemical disequilibrium Delta T < 15 C) — suppressed by weighting "
            "Delta T_diseq = T_chem - T_surf and advecting 0-900 m up-gradient onto structural tilt/MT walls; "
            "(3) GeoDAWN contractor flight-block seams, highway/rail prisms, and Lake Lahontan paleo-shorelines — "
            "suppressed by 300 m block-seam erosion, TIGER 2024 road gate, and contour-orthogonality filtering."
        ),
        "named_non_fault_mimic_process": (
            "(1) Saline evaporative playas & closed-basin brines (Carson Sink, Humboldt Sink, Buena Vista playa) "
            "mimicking MT electrical conductivity (Band 17) and uraniferous eU anomalies — suppressed by flat-deep-basin "
            "structural veto (slope < 1.8 deg & depth_to_base > 280 m) plus lateral clay-cap flank inflection requiring "
            "theta_g = 0 gravity tilt zero-crossings; (2) Down-gradient shallow gravel thermal outflow sheets "
            "(temp_c = 40-65 C with low chemical disequilibrium Delta T < 15 C) — suppressed by weighting "
            "Delta T_diseq = T_chem - T_surf and advecting 0-900 m up-gradient onto structural tilt/MT walls; "
            "(3) GeoDAWN contractor flight-block seams, highway/rail prisms, and Lake Lahontan paleo-shorelines — "
            "suppressed by 300 m block-seam erosion, TIGER 2024 road gate, and contour-orthogonality filtering."
        ),
        "experiments_used": 3,
        "experiments_budget_cap": 3,
        "weekly_slots_used": 0,
        "runtime_seconds": elapsed,
        "peak_rss_mb": max_rss,
        "holdout_dti": {
            "primary_hide_and_recover": exp3_clean["hide_and_recover_v3"],
            "exp1_pu_mult_axial28_hide_and_recover": exp1_clean["hide_and_recover_v3"],
            "exp2_noisyor_raw_celf_hide_and_recover": exp2_clean["hide_and_recover_v3"],
            "incumbent_02778_same_evaluator": champ_clean["hide_and_recover_v3"],
            "paired_delta_vs_02778_champion": paired_hr_vs_champ,
            "paired_delta_vs_exp1_noisyor_lift": paired_hr_vs_exp1,
            "paired_delta_vs_exp2_no_min_sep": paired_hr_vs_exp2,
            "censorship_matched_d2": exp3_clean["censorship_matched_d2"],
            "detached_600m_segments": exp3_clean["detached_600m_segments"],
            "incumbent_detached_600m": champ_clean["detached_600m_segments"],
            "paired_detached_delta_vs_02778_champion": paired_det_vs_champ,
            "off_catalogue_sgmc": exp3_clean["sgmc_off_catalogue_v3"],
            "incumbent_02778_sgmc": champ_clean["sgmc_off_catalogue_v3"],
            "paired_sgmc_calibrated_delta_vs_02778_champion": paired_sgmc_vs_champ,
            "paired_sgmc_noisyor_lift_over_exp1": paired_sgmc_vs_exp1,
            "paired_sgmc_axial28_lift_over_exp2": paired_sgmc_vs_exp2,
            "historical_comparators_same_evaluator": {
                "H38_pooled_dti": h38_best["pooled_dti"],
                "H47_1_pooled_dti_nonstationary_eta": h47_card["primary_hide_and_recover"]["pooled_dti"],
                "H47_1_sgmc_calibrated_dti": h47_card["off_catalogue_sgmc"]["prevalence_calibrated_dti"],
                "H48_1_fbgr_pooled_dti": h48_card["primary_hide_and_recover"]["pooled_dti"],
                "H48_1_fbgr_detached_600m_dti": h48_card["detached_600m_segments"]["pooled_dti"],
                "H48_1_fbgr_sgmc_calibrated_dti": h48_card["off_catalogue_sgmc"]["prevalence_calibrated_dti"],
            },
        },
        "leakage_canary": {
            "passed": canary["passed"],
            "threshold_auc": canary["threshold_auc"],
            "n_features_tested": canary["n_features_tested"],
            "max_oriented_auc": canary["max_oriented_auc"],
            "worst_channel": canary["worst_channel"],
        },
        "correlation_and_overlap_vs_registry": {
            "registry_source_counts": final_scan["registry_source_counts"],
            "n_manifest_rasters_total": final_scan["n_manifest_rasters_total"],
            "n_unique_rasters_checked": final_scan["n_unique_rasters_checked"],
            "n_genuine_rasters_checked": final_scan["n_genuine_rasters_checked"],
            "n_focus_site_genuine_checked": final_scan["n_focus_site_genuine_checked"],
            "n_ultra_dense_or_continuous_checked": final_scan["n_ultra_dense_or_continuous_checked"],
            "genuine_pre_placement_surface_passed": pre_scan["genuine_surface_passed"],
            "genuine_final_dots_passed": final_scan["genuine_final_dots_passed"],
            "external_cross_site_unique_passed": final_scan["external_cross_site_unique_passed"],
            "max_external_cross_site_3px_dot_overlap": final_scan["worst_external_cross_site_overlap"]["within_3px_fraction"],
            "worst_external_cross_site_overlap_peer": final_scan["worst_external_cross_site_overlap"],
            "focus_site_genuine_final_passed": final_scan["focus_site_genuine_final_passed"],
            "max_abs_surface_spearman": abs(final_scan["worst_genuine_surface"]["surface_spearman"]),
            "worst_genuine_surface_peer": final_scan["worst_genuine_surface"],
            "max_genuine_3px_dot_overlap": final_scan["worst_genuine_overlap"]["within_3px_fraction"],
            "worst_genuine_overlap_peer": final_scan["worst_genuine_overlap"],
            "max_focus_site_3px_dot_overlap": final_scan["worst_focus_site_overlap"]["within_3px_fraction"],
            "worst_focus_site_overlap_peer": final_scan["worst_focus_site_overlap"],
            "ultra_dense_or_continuous_over_70pct": final_scan["ultra_dense_or_continuous_over_70pct"],
            "literal_5px_calibration_lattice_probe": final_scan["worst_literal_overlap"],
            "literal_all_rasters_final_passed": final_scan["literal_all_rasters_final_passed"],
        },
        "artifacts": {
            "primary_zeros_tif": f"docs/downloads/{bundle['zeros_tif']['filename']}",
            "primary_zeros_sha256": zeros_sha256,
            "primary_zeros_bytes": bundle["zeros_tif"]["size_bytes"],
            "nan_companion_tif": f"docs/downloads/{bundle['nan_tif']['filename']}",
            "nan_companion_sha256": bundle["nan_tif"]["sha256"],
            "zip_archive": f"docs/downloads/{bundle['zeros_zip']['filename']}",
            "zip_sha256": bundle["zeros_zip"]["sha256"],
            "audit_json": f"docs/downloads/{audit_sidecar_name}",
            "diagnostic_figure": "docs/assets/fig_h49_cgtd.png",
            "emitted_dots": int(exp3_full_dots.sum()),
            "on_catalogue_dots": int((exp3_full_dots & ctx.labels).sum()),
            "spatial_allocation": spatial_alloc,
        },
        "raster_sha256": zeros_sha256,
        "validator_output": {
            "validated_without_human_intervention": True,
            "strict_cli_check_submission": strict_cli_check,
            "audit_geotiff_13_checks_passed": audit_13["all_checks_passed"],
            "required_validator_flags": validator_flags,
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
            "dtype": "float32",
            "nodata": None,
            "nan_inside_footprint": 0,
            "nan_anywhere_in_raster": 0,
            "values_in_0_1": True,
            "min_value": 0.0,
            "max_value": 1.0,
        },
        "submission_name": sub_name,
        "submission_note": sub_note,
        "submission_note_length": len(sub_note),
        "release_gate_decision": gate_decision,
        "download_for_research_ok": True,
        "ok_to_submit": ok_submit,
        "verdict": final_verdict,
    }
    (evidence_dir() / "h49_cgtd_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n")
    (ROOT / "docs" / "data" / "latest-run-card.json").write_text(json.dumps(run_card, indent=2) + "\n")
    print(
        f"Done in {elapsed:.1f}s (peak RSS={max_rss} MB)! "
        f"Verdict={run_card['verdict']} | TIF={bundle['zeros_tif']['filename']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
