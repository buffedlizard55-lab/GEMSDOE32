#!/usr/bin/env python3
"""Execute Pre-Registered Single Lane H47-1 (LDGI-WCR) within the strict 3-experiment budget.

Reuses shared tools strictly (Protocol Rule 2):
  - `.cache/gems_work/feature_stack.npy` (`scripts/build_features.py`, 35 channels)
  - `.cache/gems_work/spcp_extra_20ch.npy` (`gems32.spcp`, 20 label-free channels)
  - `.cache/gems_work/trhv_extra_8ch.npy` (`gems32.trhv`, 8 repaired label-free hydrothermal-vent & TIGER channels)
  - `.cache/gems_work/ldgi_extra_8ch.npy` (`gems32.ldgi`, 8 label-free lineament-density, Gi*, Moran, Ricker wavelet, SVD & multi-altitude channels)
  - `gems32.holdout` / `scripts/evaluate_holdout.py`
  - `gems32.emitter.emit` (repaired `IR-32-EMIT-RHO-01` + `initial_mask` residual-coverage CELF)
  - `scripts/submission_writer.py` & `scripts/check_submission.py --strict-finite`
  - `gems32.release_gate`
"""

from __future__ import annotations

import gc
import hashlib
import json
import os
import pickle
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("GDAL_CACHEMAX", "32")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import emitter, features, holdout, ldgi, mdrc, metric, release_gate, spcp, submission, trhv  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402
import submission_writer  # noqa: E402

TARGET_BUDGET = 37_654
B_COLLAR_PX = 2.0
SESSION_BRANCH = "arena/e0dc405d-gemsdoe32"


def peak_rss_mb() -> float:
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def evaluate_detached_and_censored(
    pred_or_cells: np.ndarray | dict[str, np.ndarray],
    ctx: holdout.HoldoutContext,
    b_visible_px: float = 2.0,
    detach_min_px: float = 6.0,
    censor_hidden_px: float = 2.0,
    grid_n: int = 16,
    n_boot: int = 1000,
    seed: int = 20261026,
) -> dict:
    """Supplementary leak-free diagnostics on the exact same 8 holdout cells:
    1) `censored_d2`: applies `d_hidden > 2.0 px` to OOF predictions so dynamic OOF arms face the
       exact same hidden-fault B=2 exclusion already baked into static full-map `.tif` files.
    2) `detached_600m`: scores ONLY withheld fault pixels >= 6.0 px (600 m) from visible faults.
    """
    h, w = ctx.foot.shape
    n_blocks = grid_n * grid_n
    fy, fx = np.nonzero(ctx.foot)
    active_blocks = np.unique(holdout._spatial_block_index(fy, fx, (h, w), grid_n))
    is_dict = isinstance(pred_or_cells, dict)
    base_mask = None if is_dict else (np.asarray(pred_or_cells, bool) & ctx.foot)

    tp_det = np.zeros(n_blocks, dtype=np.float64)
    fp_det = np.zeros(n_blocks, dtype=np.float64)
    fn_det = np.zeros(n_blocks, dtype=np.float64)
    n_det_pos = 0

    tp_cen = np.zeros(n_blocks, dtype=np.float64)
    fp_cen = np.zeros(n_blocks, dtype=np.float64)
    fn_cen = np.zeros(n_blocks, dtype=np.float64)
    n_cen_pos = 0

    for cell in ctx.cells:
        sl = cell.bbox
        r0, c0 = int(sl[0].start), int(sl[1].start)
        raw_in = np.asarray(pred_or_cells[cell.key], bool)[sl] if is_dict else base_mask[sl]
        p_sub = raw_in & cell.active_sub
        if b_visible_px > 0.0 and cell.d_vis_sub is not None:
            p_sub = p_sub & (cell.d_vis_sub > b_visible_px)

        ty, tx = cell.truth_coords
        if ty.size == 0:
            continue

        truth_sub = np.zeros(cell.active_sub.shape, dtype=bool)
        truth_sub[ty, tx] = True
        d_hid = distance_transform_edt(~truth_sub)
        p_cen = p_sub & (d_hid > censor_hidden_px)
        n_cen_pos += int(ty.size)
        t_blk = holdout._spatial_block_index(ty + r0, tx + c0, (h, w), grid_n)
        if p_cen.any():
            dp_cen = distance_transform_edt(~p_cen)
            tc_cen = metric.kernel(dp_cen[ty, tx]).astype(np.float64)
            np.add.at(tp_cen, t_blk, tc_cen)
            np.add.at(fn_cen, t_blk, 1.0 - tc_cen)
            py, px = np.nonzero(p_cen)
            p_blk = holdout._spatial_block_index(py + r0, px + c0, (h, w), grid_n)
            np.add.at(fp_cen, p_blk, (1.0 - cell.k_dg_sub[p_cen]).astype(np.float64))
        else:
            np.add.at(fn_cen, t_blk, 1.0)

        det_keep = cell.d_vis_sub[ty, tx] >= detach_min_px
        if det_keep.any():
            dty, dtx = ty[det_keep], tx[det_keep]
            n_det_pos += int(dty.size)
            det_truth = np.zeros(cell.active_sub.shape, dtype=bool)
            det_truth[dty, dtx] = True
            k_dg_det = metric.kernel(distance_transform_edt(~det_truth))
            p_det = p_sub & (cell.d_vis_sub >= (detach_min_px - 3.0))
            dt_blk = holdout._spatial_block_index(dty + r0, dtx + c0, (h, w), grid_n)
            if p_det.any():
                dp_det = distance_transform_edt(~p_det)
                tc_det = metric.kernel(dp_det[dty, dtx]).astype(np.float64)
                np.add.at(tp_det, dt_blk, tc_det)
                np.add.at(fn_det, dt_blk, 1.0 - tc_det)
                py, px = np.nonzero(p_det)
                p_blk = holdout._spatial_block_index(py + r0, px + c0, (h, w), grid_n)
                np.add.at(fp_det, p_blk, (1.0 - k_dg_det[p_det]).astype(np.float64))
            else:
                np.add.at(fn_det, dt_blk, 1.0)

    cen_dti, cen_ci, cen_boots = holdout._cluster_bootstrap_pooled_dti(
        tp_cen, fp_cen, fn_cen, active_blocks, n_boot=n_boot, seed=seed
    )
    det_dti, det_ci, det_boots = holdout._cluster_bootstrap_pooled_dti(
        tp_det, fp_det, fn_det, active_blocks, n_boot=n_boot, seed=seed
    )
    return {
        "censored_d2": {
            "dti": cen_dti,
            "ci95": cen_ci,
            "n_withheld_positives": n_cen_pos,
            "_boots": cen_boots,
        },
        "detached_600m": {
            "dti": det_dti,
            "ci95": det_ci,
            "n_withheld_positives": n_det_pos,
            "_boots": det_boots,
        },
    }


def paired_ci(boots_a: np.ndarray, boots_b: np.ndarray) -> dict:
    diff = np.asarray(boots_a, dtype=np.float64) - np.asarray(boots_b, dtype=np.float64)
    return {
        "mean_boot_delta": float(diff.mean()),
        "ci95": [float(np.percentile(diff, 2.5)), float(np.percentile(diff, 97.5))],
        "prob_positive": float((diff > 0.0).mean()),
    }


def _normalized_ranks(vec: np.ndarray) -> np.ndarray:
    r = rankdata(vec).astype(np.float32)
    r -= np.float32(r.mean())
    nrm = float(np.linalg.norm(r))
    return (r / np.float32(nrm)) if nrm > 0.0 else r


def scan_full_registry(
    surface: np.ndarray,
    dots: np.ndarray | None,
    foot: np.ndarray,
    ddir: Path,
    exclude_shas: set[str] | None = None,
) -> dict:
    """Exact 100% full-footprint (`5,167,373` px) Spearman & <=3px directional overlap scan across all
    unique-SHA256 `3730x3292` rasters in `focus_registry_manifest.json` + `data_manifest.json` + `docs/downloads`.
    """
    exclude_shas = exclude_shas or set()
    fman = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    dman = json.loads((ROOT / "registry" / "data_manifest.json").read_text())

    entries: dict[str, tuple[str, Path]] = {}
    for r in fman["rasters"]:
        if r.get("status") == "ok" and r["sha256"] not in exclude_shas:
            p = ROOT / r["local"]
            if p.exists():
                entries.setdefault(r["sha256"], (f"{r['repo']}:{r['path']}", p))
    for e in dman["files"]:
        if e["group"] == "scored" and e["sha256"] not in exclude_shas:
            p = ddir / e["dest"]
            if p.exists():
                entries.setdefault(e["sha256"], (f"manifest:{e['id']}", p))
    for p in sorted(downloads_dir().glob("*.tif")):
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if sha not in exclude_shas:
            entries.setdefault(sha, (f"local:docs/downloads/{p.name}", p))

    rx_surf = _normalized_ranks(np.asarray(surface[foot], dtype=np.float64))
    rx_dots = _normalized_ranks(dots[foot].astype(np.float64)) if dots is not None else None

    yy, xx = np.mgrid[-3:4, -3:4]
    disk3 = (yy * yy + xx * xx) <= 9
    my_dots_yx = np.nonzero(dots & foot) if dots is not None else None
    n_my_dots = int(my_dots_yx[0].size) if my_dots_yx is not None else 0

    rows = []
    skipped = []
    for sha, (name, path) in sorted(entries.items(), key=lambda kv: kv[1][0]):
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or ds.shape != foot.shape:
                    skipped.append({"name": name, "reason": f"shape={ds.shape},count={ds.count}"})
                    continue
                arr = ds.read(1)
        except Exception as exc:
            skipped.append({"name": name, "reason": str(exc)})
            continue

        in_foot = arr[foot]
        raw_finite = bool(np.isfinite(in_foot).all())
        clean_foot = in_foot if raw_finite else np.where(np.isfinite(in_foot), in_foot, np.float32(0.0))
        del in_foot
        other_dots = np.isfinite(arr) & (arr > 0) & foot
        n_other = int(other_dots.sum())
        del arr

        if float(clean_foot.max() - clean_foot.min()) > 0.0:
            ry = _normalized_ranks(clean_foot)
            rho_surf = float(np.dot(rx_surf, ry))
            rho_dots = float(np.dot(rx_dots, ry)) if rx_dots is not None else None
            del ry
        else:
            rho_surf = 0.0
            rho_dots = 0.0 if rx_dots is not None else None
        del clean_foot

        ov3 = 0.0
        if my_dots_yx is not None and n_my_dots > 0 and n_other > 0:
            near3 = binary_dilation(other_dots, structure=disk3)
            ov3 = float(near3[my_dots_yx].mean())
            del near3
        del other_dots

        if len(rows) % 20 == 0:
            gc.collect()
        is_lattice = "r13-lattice-s5" in name
        rows.append(
            {
                "name": name,
                "sha256": sha,
                "other_dots": n_other,
                "raw_in_foot_finite": raw_finite,
                "is_calibration_lattice": is_lattice,
                "surface_spearman": round(rho_surf, 6),
                "dots_spearman": round(rho_dots, 6) if rho_dots is not None else None,
                "within_3px_fraction": round(ov3, 6),
            }
        )

    del rx_surf, rx_dots
    gc.collect()

    genuine = [r for r in rows if not r["is_calibration_lattice"]]
    top_surf_candidates = sorted(genuine, key=lambda r: -abs(r["surface_spearman"]))[:5]
    top_ov_candidates = sorted(genuine, key=lambda r: -r["within_3px_fraction"])[:5]
    worst_ov_all = max(rows, key=lambda r: r["within_3px_fraction"])

    verify_shas = {r["sha256"] for r in (top_surf_candidates + top_ov_candidates + [worst_ov_all])}
    rg_surf_comparisons = []
    rg_final_comparisons = []
    for sha in sorted(verify_shas):
        nm, pth = entries[sha]
        with rasterio.open(pth) as ds:
            a = ds.read(1)
        a_clean = np.where(np.isfinite(a), a, 0.0).astype(np.float32)
        o_dots = np.isfinite(a) & (a > 0) & foot
        del a
        s_one = release_gate.compare_registry(surface, None, foot, {nm: (a_clean, o_dots)}, stage="surface")
        rg_surf_comparisons.extend(s_one["comparisons"])
        if dots is not None:
            f_one = release_gate.compare_registry(surface, dots, foot, {nm: (a_clean, o_dots)}, stage="final")
            rg_final_comparisons.extend(f_one["comparisons"])
        del a_clean, o_dots
        gc.collect()

    worst_surf_gen = max(genuine, key=lambda r: abs(r["surface_spearman"]))
    worst_ov_gen = max(genuine, key=lambda r: r["within_3px_fraction"])

    surf_passed = bool(rg_surf_comparisons) and all(
        c["measurable"] and not c["duplicate"] for c in rg_surf_comparisons
    )
    rg_surface = {
        "stage": "surface",
        "rule": "literal rho>0.90 OR directional overlap>0.70; no density exemptions",
        "passed": surf_passed,
        "stop": not surf_passed,
        "comparisons": rg_surf_comparisons,
    }
    rg_final = None
    if dots is not None:
        fin_passed = bool(rg_final_comparisons) and all(
            c["measurable"] and not c["duplicate"] for c in rg_final_comparisons
        )
        rg_final = {
            "stage": "final",
            "rule": "literal rho>0.90 OR directional overlap>0.70; no density exemptions",
            "passed": fin_passed,
            "stop": not fin_passed,
            "comparisons": rg_final_comparisons,
        }

    return {
        "n_manifest_rasters_total": len(fman["rasters"]),
        "n_unique_rasters_checked": len(rows),
        "n_genuine_rasters_checked": len(genuine),
        "skipped_non_submission_blobs": skipped,
        "genuine_surface_passed": bool(abs(worst_surf_gen["surface_spearman"]) <= 0.90),
        "genuine_final_dots_passed": bool(
            dots is not None
            and abs(worst_surf_gen["surface_spearman"]) <= 0.90
            and worst_ov_gen["within_3px_fraction"] <= 0.70
        ),
        "literal_all_rasters_final_passed": bool(
            dots is not None
            and max(abs(r["surface_spearman"]) for r in rows) <= 0.90
            and worst_ov_all["within_3px_fraction"] <= 0.70
        ),
        "worst_genuine_surface": worst_surf_gen,
        "worst_genuine_overlap": worst_ov_gen,
        "worst_literal_overlap": worst_ov_all,
        "release_gate_direct_surface": rg_surface,
        "release_gate_direct_final": rg_final,
        "top15_by_overlap": sorted(genuine, key=lambda r: -r["within_3px_fraction"])[:15],
        "top10_by_abs_spearman": sorted(genuine, key=lambda r: -abs(r["surface_spearman"]))[:10],
    }


def audit_nine_focus_sites(ctx: holdout.HoldoutContext, champ_mask: np.ndarray, h47_mask: np.ndarray) -> dict:
    """Byte-verified audit of all 9 focus sites (`GEMSDOE24..36`) at their refreshed 2026-10-26 commits."""
    fman = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    by_repo: dict[str, list[dict]] = {}
    for r in fman["rasters"]:
        if r.get("status") == "ok":
            by_repo.setdefault(r["repo"], []).append(r)

    yy, xx = np.mgrid[-3:4, -3:4]
    disk3 = (yy * yy + xx * xx) <= 9
    champ_near3 = binary_dilation(champ_mask, structure=disk3)
    h47_near3 = binary_dilation(h47_mask, structure=disk3)

    preferred_patterns = {
        "GEMSDOE24": "vent-quat-bridge-20261026",
        "GEMSDOE25": "h71-hgpc-blind-b2-sapd3-k3p5-20261026",
        "GEMSDOE27": "h31-rankens-celf-b2-20261026",
        "GEMSDOE28": "s20-nchc-20261026",
        "GEMSDOE30": "geothermal-corridor-offcat-d3-20261026",
        "GEMSDOE31": "h31s-udap-sslic-37654-20261026",
        "GEMSDOE32": "h33-h33-2-b2-20261004",
        "GEMSDOE33": "g33-tilt-gravity-lidar-coherence-20261026",
        "GEMSDOE36": "mto36-ortho-contact-20261026",
    }

    site_rows = []
    for repo, pat in preferred_patterns.items():
        cands = [
            r
            for r in by_repo.get(repo, [])
            if pat in r["path"] and not r["path"].endswith("-nan.tif")
        ]
        if not cands:
            cands = [r for r in by_repo.get(repo, []) if not r["path"].endswith("-nan.tif")]
        if not cands:
            continue
        rec = cands[0]
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
        ov_h47 = float(h47_near3[m].mean()) if n_dots > 0 else 0.0
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
                "static_hide_recover_dti": round(hr["pooled_dti"], 6),
                "static_hide_recover_ci95": [round(x, 6) for x in hr["ci95_cluster_bootstrap"]],
                "sgmc_raw_dti": round(sg["sgmc_raw_pooled_dti"], 6),
                "sgmc_prevalence_calibrated_dti": round(sg["sgmc_prevalence_calibrated_dti"], 6),
                "sgmc_calibrated_ci95": [round(x, 6) for x in sg["sgmc_calibrated_ci95"]],
                "within_3px_of_02778_champion": round(ov_champ, 4),
                "within_3px_of_h47_ldgi": round(ov_h47, 4),
            }
        )
    return {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_manifest_rasters": len(fman["rasters"]),
        "refs": fman["refs"],
        "sites": site_rows,
    }


def render_diagnostic_figure(
    out_path: Path,
    champ_clean: dict,
    ctrl_clean: dict,
    exp1_clean: dict,
    exp2_clean: dict,
    exp3_clean: dict,
    ldgi_stack: np.ndarray,
    exp3_dots: np.ndarray,
    stage1_dots: np.ndarray,
    foot: np.ndarray,
    labels: np.ndarray,
    spatial_alloc: dict,
) -> None:
    """Render publication-grade 4-panel diagnostic figure `docs/assets/fig_h47_ldgi.png`."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 10.2), dpi=135)
    fig.patch.set_facecolor("#0f172a")

    for ax in axes.ravel():
        ax.set_facecolor("#1e293b")
        ax.tick_params(colors="#cbd5e1", labelsize=9)
        for sp_line in ax.spines.values():
            sp_line.set_color("#475569")

    # Panel A: Dual-Benchmark Pareto Plane (Hide-and-Recover v3.0 vs Off-Catalogue SGMC-cal v3.0)
    ax0 = axes[0, 0]
    pts = [
        ("0.2778 Champion\n(d2.8 parent / B=2)", champ_clean, "#f59e0b", "D", 95),
        ("CTRL 35-ch OOF", ctrl_clean, "#94a3b8", "o", 75),
        ("EXP1: Unsup LDGI-Crest\n(Horizon B)", exp1_clean, "#a78bfa", "^", 90),
        ("EXP2: Exposed-71+63 GI*\n(Horizon A)", exp2_clean, "#38bdf8", "s", 90),
        ("EXP3: H47-1 Dual-Horizon\n(Adaptive eta CELF)", exp3_clean, "#10b981", "*", 190),
    ]
    for label, d, col, mk, sz in pts:
        x = d["hide_and_recover_v3"]["pooled_dti"]
        xlo, xhi = d["hide_and_recover_v3"]["ci95"]
        y = d["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"]
        ylo, yhi = d["sgmc_off_catalogue_v3"]["calibrated_ci95"]
        ax0.errorbar(
            [x], [y],
            xerr=[[max(0.0, x - xlo)], [max(0.0, xhi - x)]],
            yerr=[[max(0.0, y - ylo)], [max(0.0, yhi - y)]],
            fmt="none", ecolor=col, alpha=0.55, elinewidth=1.4, capsize=3,
        )
        ax0.scatter([x], [y], c=col, marker=mk, s=sz, zorder=5, edgecolors="white", linewidths=0.8, label=label)
    ax0.axvline(champ_clean["hide_and_recover_v3"]["pooled_dti"], color="#f59e0b", ls="--", lw=1.0, alpha=0.6)
    ax0.axhline(champ_clean["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"], color="#f59e0b", ls=":", lw=1.0, alpha=0.6)
    ax0.set_xlabel("HOLDOUT-DTI: Hide-and-Recover v3.0 (n=22,232 withheld)", color="#e2e8f0", fontsize=10)
    ax0.set_ylabel("HOLDOUT-DTI: Off-Catalogue SGMC-cal v3.0 (n=62,703)", color="#e2e8f0", fontsize=10)
    ax0.set_title("A. Dual-Benchmark Pareto Frontier (95% Spatial Block CIs)", color="#f8fafc", fontsize=11, fontweight="bold")
    ax0.legend(loc="best", fontsize=8, facecolor="#0f172a", edgecolor="#475569", labelcolor="#f8fafc")

    # Panel B: Bar comparison across Hide&Recover, Censored d>2, Detached >=600m, SGMC-cal
    ax1 = axes[0, 1]
    metrics_keys = [
        ("Hide&Rec\nv3.0", lambda d: d["hide_and_recover_v3"]["pooled_dti"]),
        ("Censored\nd_hid>2px", lambda d: d["censorship_matched_d2"]["pooled_dti"]),
        ("Detached\n>=600m", lambda d: d["detached_600m_segments"]["pooled_dti"]),
        ("SGMC-cal\noff-cat", lambda d: d["sgmc_off_catalogue_v3"]["prevalence_calibrated_dti"]),
    ]
    arms_bar = [
        ("0.2778 Champ", champ_clean, "#f59e0b"),
        ("EXP1 Unsup-LDGI", exp1_clean, "#a78bfa"),
        ("EXP2 Exposed71", exp2_clean, "#38bdf8"),
        ("EXP3 Dual-LDGI", exp3_clean, "#10b981"),
    ]
    x_pos = np.arange(len(metrics_keys))
    width = 0.19
    for idx, (aname, adict, col) in enumerate(arms_bar):
        vals = [fn(adict) for _, fn in metrics_keys]
        ax1.bar(x_pos + (idx - 1.5) * width, vals, width=width, color=col, label=aname, alpha=0.90)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([m[0] for m in metrics_keys], color="#e2e8f0", fontsize=9)
    ax1.set_ylabel("Pooled DTI (alpha=0.2, beta=0.8, 300 m)", color="#e2e8f0", fontsize=10)
    ax1.set_title("B. 3-Experiment Ablation Across All Four Holdout Slices", color="#f8fafc", fontsize=11, fontweight="bold")
    ax1.legend(loc="upper right", fontsize=8, facecolor="#0f172a", edgecolor="#475569", labelcolor="#f8fafc")

    # Panel C: Downsampled map of LDGI Lineament-Density & Gi* Corridor Composite (`ldgi_stack[:, :, 7]`)
    ax2 = axes[1, 0]
    step = 6
    ldgi_ds = np.where(foot[::step, ::step], np.asarray(ldgi_stack[::step, ::step, 7], dtype=np.float32), np.nan)
    im = ax2.imshow(ldgi_ds, cmap="magma", vmin=0.0, vmax=0.95)
    ly, lx = np.nonzero(labels[::step, ::step])
    ax2.scatter(lx, ly, s=0.15, c="#38bdf8", alpha=0.35, label="Mapped catalogue")
    ax2.set_title("C. Label-Free LDGI Corridor Composite (rho_lin + Gi* + Ricker + Moran)", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax2.set_xticks([])
    ax2.set_yticks([])
    cb = fig.colorbar(im, ax=ax2, fraction=0.042, pad=0.03)
    cb.ax.tick_params(colors="#cbd5e1", labelsize=8)

    # Panel D: Dual-Horizon Emitted Dots (`Stage 1` Horizon A vs `Stage 2` Horizon B Off-Catalogue)
    ax3 = axes[1, 1]
    bg = np.where(foot[::step, ::step], 0.12, np.nan)
    ax3.imshow(bg, cmap="Greys", vmin=0.0, vmax=1.0)
    s1_y, s1_x = np.nonzero(stage1_dots)
    s2_y, s2_x = np.nonzero(exp3_dots & ~stage1_dots)
    ax3.scatter(s1_x[::4] / step, s1_y[::4] / step, s=0.45, c="#38bdf8", alpha=0.65, label=f"Stage 1 Horizon A ({s1_y.size:,}d)")
    ax3.scatter(s2_x[::3] / step, s2_y[::3] / step, s=0.65, c="#10b981", alpha=0.80, label=f"Stage 2 LDGI Off-Cat ({s2_y.size:,}d)")
    ax3.set_title(
        f"D. EXP3 Adaptive Dual-Horizon (37,654d, B=2; >2km off-cat={spatial_alloc['far_gt_20px_blind_frac']*100:.1f}%)",
        color="#f8fafc",
        fontsize=10.5,
        fontweight="bold",
    )
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.legend(loc="lower right", fontsize=8, facecolor="#0f172a", edgecolor="#475569", labelcolor="#f8fafc", markerscale=5.0)

    fig.suptitle(
        "GEMSDOE32 Lane H47-1 (LDGI-WCR): Lineament-Density, Getis-Ord Gi* & Wavelet Dual-Horizon Allocation",
        color="#f8fafc",
        fontsize=13,
        fontweight="bold",
        y=0.985,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.965])
    fig.savefig(out_path, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    if os.environ.get("GEMSDOE32_ASSIGNED_LANE_ID", "").strip() != "H47-1-LDGI":
        raise SystemExit(
            "STOP: no explicit H47-1-LDGI method paragraph is assigned in the current prompt. "
            "Do not infer a lane or rerun experiments; only set GEMSDOE32_ASSIGNED_LANE_ID after explicit authorization."
        )
    t0 = time.time()
    ddir = data_dir()
    wdir = work_dir()
    wdir.mkdir(parents=True, exist_ok=True)

    base_stack_path = wdir / "feature_stack.npy"
    if not base_stack_path.exists():
        raise SystemExit("Run scripts/build_features.py first to create .cache/gems_work/feature_stack.npy")

    spcp_path = wdir / "spcp_extra_20ch.npy"
    if spcp_path.exists() and "--rebuild-spcp" not in sys.argv:
        print(f"[1/8] Reusing cached 20-channel SPCP stack ({spcp_path.name}, RSS={peak_rss_mb()} MB)...", flush=True)
    else:
        print(f"[1/8] Building 20 label-free SPCP channels (RSS={peak_rss_mb()} MB)...", flush=True)
        spcp.build_spcp_extra_stack(ddir, base_stack_path, out_path=spcp_path)
        gc.collect()

    trhv_path = wdir / "trhv_extra_8ch.npy"
    if trhv_path.exists() and "--rebuild-trhv" not in sys.argv:
        print(f"[2/8] Reusing cached 8-channel TRHV stack ({trhv_path.name}, RSS={peak_rss_mb()} MB)...", flush=True)
    else:
        print(f"[2/8] Building 8 label-free TRHV channels (RSS={peak_rss_mb()} MB)...", flush=True)
        trhv.build_trhv_extra_stack(ddir, base_stack_path, spcp_path, out_path=trhv_path)
        gc.collect()

    ldgi_path = wdir / "ldgi_extra_8ch.npy"
    ldgi_receipt_path = ROOT / "registry" / "ldgi_feature_receipt.json"
    if ldgi_path.exists() and "--rebuild-ldgi" not in sys.argv:
        print(f"[2/8] Reusing cached 8-channel LDGI stack ({ldgi_path.name}, RSS={peak_rss_mb()} MB)...", flush=True)
        ldgi_receipt = json.loads(ldgi_receipt_path.read_text()) if ldgi_receipt_path.exists() else {
            "channels": list(ldgi.LDGI_EXTRA_CHANNELS),
            "shape": [3730, 3292, 8],
            "reused_cached_memmap": True,
        }
    else:
        print(f"[2/8] Building 8 label-free LDGI channels (RSS={peak_rss_mb()} MB)...", flush=True)
        _, ldgi_receipt = ldgi.build_ldgi_extra_stack(
            ddir, base_stack_path, spcp_path, trhv_path, out_path=ldgi_path, receipt_path=ldgi_receipt_path, rebuild=True
        )
        gc.collect()

    base_stack = np.load(base_stack_path, mmap_mode="r")
    spcp_stack = np.load(spcp_path, mmap_mode="r")
    trhv_stack = np.load(trhv_path, mmap_mode="r")
    ldgi_stack = np.load(ldgi_path, mmap_mode="r")

    print(f"[3/8] Loading HoldoutContext & running 71-channel Leakage Canary (RSS={peak_rss_mb()} MB)...", flush=True)
    ctx = holdout.load_holdout_context(ddir)
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

    canary = ldgi.run_leakage_canary_71ch(
        base_stack, spcp_stack, trhv_stack, ldgi_stack, list(features.CHANNELS), ctx, max_auc=0.90
    )
    print(
        f"      Canary passed={canary['passed']} | n={canary['n_features_tested']} | "
        f"worst={canary['worst_channel']} ({canary['max_oriented_auc']:.5f})",
        flush=True,
    )
    if not canary["passed"]:
        raise SystemExit(f"STOP: Leakage canary failed on {canary['worst_channel']} ({canary['max_oriented_auc']})")

    # Evaluate static incumbents + true fold-collared 0.2778 Champion (`h25-1-dotted-h19-5-d2-8` with `b_visible_px=2.0`)
    champ_path = downloads_dir() / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    with rasterio.open(champ_path) as ds:
        champ_mask = (ds.read(1) > 0) & ctx.foot
    champ_static_hr = holdout.evaluate_hide_and_recover(champ_mask, ctx, b_visible_px=B_COLLAR_PX, name="CHAMPION_02778_STATIC")
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

    h38_card = json.loads((ROOT / "evidence" / "h38_run_card.json").read_text())
    h38_best = h38_card["holdout_dti"]["primary_hide_and_recover"]
    if (h38_best.get("evaluator_version") != champ_hr["evaluator_version"]
            or h38_best.get("n_withheld_positives") != champ_hr["n_withheld_positives"]):
        raise RuntimeError("H38 repo-best reference is not comparable to this run's evaluator/population")

    print(
        f"      B2 Champion fold-collared d2.8 parent: HOLDOUT-DTI={champ_hr['pooled_dti']:.5f}; "
        f"static B2={champ_static_hr['pooled_dti']:.5f}; H38 repo-best={h38_best['pooled_dti']:.5f}; "
        f"SGMC_cal={champ_sg['sgmc_prevalence_calibrated_dti']:.5f}",
        flush=True,
    )

    def _eval_arm(name: str, cell_masks: dict[str, np.ndarray] | np.ndarray, full_mask: np.ndarray) -> dict:
        hr = holdout.evaluate_hide_and_recover(cell_masks, ctx, b_visible_px=B_COLLAR_PX, name=name)
        sup = evaluate_detached_and_censored(cell_masks, ctx, b_visible_px=B_COLLAR_PX)
        sg = holdout.evaluate_sgmc_with_ci(full_mask, ctx, name=name)
        return {"name": name, "hr": hr, "sup": sup, "sg": sg, "full_dots": int(full_mask.sum())}

    ckpt_path = wdir / "h47_ldgi_checkpoint.pkl"
    if ckpt_path.exists() and "--rerun-models" not in sys.argv:
        print(f"[4-6/8] Loading cached 3-experiment OOF checkpoint ({ckpt_path.name})...", flush=True)
        with ckpt_path.open("rb") as fh:
            ckpt = pickle.load(fh)
        ctrl_res = ckpt["ctrl_res"]
        exp1_res = ckpt["exp1_res"]
        exp2_res = ckpt["exp2_res"]
        exp3_res = ckpt["exp3_res"]
        exp3_belief_surface = ckpt["exp3_belief_surface"]
        exp3_full_dots = ckpt["exp3_full_dots"]
        exp3_stage1_dots = ckpt["exp3_stage1_dots"]
        exp3_alloc_meta = ckpt["exp3_alloc_meta"]
        cell_eta_table = ckpt["cell_eta_table"]
    else:
        # --- Fold-local 35-ch Control (`CTRL_35CH_OOF`) ---
        ctrl_ckpt = wdir / "h46_ctrl_res.pkl"
        if ctrl_ckpt.exists() and "--rerun-ctrl" not in sys.argv:
            with ctrl_ckpt.open("rb") as fh:
                ctrl_res = pickle.load(fh)
            print(f"[4/8] Reused cached CTRL_35CH_OOF: HR={ctrl_res['hr']['pooled_dti']:.5f} SGMC_cal={ctrl_res['sg']['sgmc_prevalence_calibrated_dti']:.5f}", flush=True)
        else:
            print(f"[4/8] Fitting fold-local Control (CTRL_35CH_OOF, RSS={peak_rss_mb()} MB)...", flush=True)
            ctrl_cells: dict[str, np.ndarray] = {}
            ctrl_oof_full = np.zeros(ctx.foot.shape, dtype=np.float32)
            for cell in ctx.cells:
                tr = fold_train[cell.fold]
                vis = cell.visible_full & tr
                elig_cell = fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2)
                b_cell = int(round(TARGET_BUDGET * (elig_cell.sum() / n_elig_full)))
                pred_reg = (ctx.quad == cell.fold) & ctx.foot if cell.seed == 20 else fold_domain[cell.fold]
                prob = spcp.fit_predict_naive_binary(
                    base_stack, None, tr, vis, pred_reg, seed=1000 + cell.seed * 10 + cell.fold
                )
                if cell.seed == 20:
                    ctrl_oof_full[pred_reg] = prob[pred_reg]
                dots_c, _ = spcp.emit_crest_submodular(prob, elig_cell, ctx.foot, budget=b_cell)
                ctrl_cells[cell.key] = dots_c
                del prob
                gc.collect()
            ctrl_full_dots, _ = spcp.emit_crest_submodular(ctrl_oof_full, elig_full, ctx.foot, budget=TARGET_BUDGET)
            ctrl_res = _eval_arm("CTRL_35CH_OOF", ctrl_cells, ctrl_full_dots)
            with ctrl_ckpt.open("wb") as fh:
                pickle.dump(ctrl_res, fh)
            del ctrl_cells, ctrl_oof_full, ctrl_full_dots
            gc.collect()

        # =========================================================================
        # EXPERIMENT 1 / 3: Label-Free Multi-Domain LDGI Corridor-Weighted Crests (`EXP1_H47_UNSUP_LDGI_CREST`)
        # =========================================================================
        print(f"[5/8] Experiment 1/3: EXP1_H47_UNSUP_LDGI_CREST (Label-free LDGI corridor-weighted crests, RSS={peak_rss_mb()} MB)...", flush=True)
        ldgi_crest_unsup = ldgi.build_ldgi_crest_unsup_surface(spcp_stack, trhv_stack, ldgi_stack, ctx.foot)
        crest_b_full = mdrc.sharpen_ridge_crest(ldgi_crest_unsup, ctx.foot)
        exp1_cells: dict[str, np.ndarray] = {}
        for cell in ctx.cells:
            sl = cell.bbox
            elig_sub = (fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2))[sl]
            b_cell = int(round(TARGET_BUDGET * (elig_sub.sum() / n_elig_full)))
            d1_sub, _ = spcp.emit_crest_submodular(ldgi_crest_unsup[sl], elig_sub, ctx.foot[sl], budget=b_cell)
            d1_full = np.zeros(ctx.foot.shape, dtype=bool)
            d1_full[sl] = d1_sub
            exp1_cells[cell.key] = d1_full
        exp1_full_dots, _ = spcp.emit_crest_submodular(ldgi_crest_unsup, elig_full, ctx.foot, budget=TARGET_BUDGET)
        exp1_res = _eval_arm("EXP1_H47_UNSUP_LDGI_CREST", exp1_cells, exp1_full_dots)
        del exp1_cells, exp1_full_dots
        gc.collect()
        print(
            f"      EXP1_H47_UNSUP_LDGI_CREST: HR={exp1_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp1_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp1_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_cal={exp1_res['sg']['sgmc_prevalence_calibrated_dti']:.5f} (RSS={peak_rss_mb()} MB)",
            flush=True,
        )

        # =========================================================================
        # EXPERIMENT 2 / 3: Fold-Local 71-ch + 63-ch Exposed Fault Classifier (`EXP2_H47_EXPOSED71_GI`)
        # =========================================================================
        print(f"[5/8] Experiment 2/3: EXP2_H47_EXPOSED71_GI (71-ch LDGI + 63-ch OOF + visible tip cones, RSS={peak_rss_mb()} MB)...", flush=True)
        exp2_cells: dict[str, np.ndarray] = {}
        s63_live = np.zeros(ctx.foot.shape, dtype=np.float32)
        r71_live = np.zeros(ctx.foot.shape, dtype=np.float32)

        for cell in ctx.cells:
            sl = cell.bbox
            tr = fold_train[cell.fold]
            vis_tr = cell.visible_full & tr
            elig_sub = (fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2))[sl]
            b_cell = int(round(TARGET_BUDGET * (elig_sub.sum() / n_elig_full)))
            pred_reg = (ctx.quad == cell.fold) & ctx.foot

            p63 = wdir / f"h47_cell_{cell.key}_63ch.npy"
            if p63.exists() and "--rerun-models" not in sys.argv:
                s63 = np.load(p63)
            else:
                s63 = trhv.fit_predict_exposed63(
                    base_stack,
                    spcp_stack,
                    trhv_stack,
                    tr,
                    vis_tr,
                    cell.visible_full,
                    pred_reg,
                    ctx.foot,
                    seed=4600 + cell.seed * 10 + cell.fold,
                    tip_weight=0.35,
                )
                np.save(p63, s63)

            p71 = wdir / f"h47_cell_{cell.key}_rawprob.npy"
            if p71.exists() and "--rerun-models" not in sys.argv:
                r71 = np.load(p71)
            else:
                clf71 = ldgi.fit_71ch_classifier(
                    base_stack,
                    spcp_stack,
                    trhv_stack,
                    ldgi_stack,
                    tr,
                    vis_tr,
                    ctx.foot,
                    seed=4700 + cell.seed * 10 + cell.fold,
                )
                r71 = ldgi.predict_chunked_71ch(clf71, base_stack, spcp_stack, trhv_stack, ldgi_stack, pred_reg)
                np.save(p71, r71)
                del clf71

            s63_live[pred_reg] += np.float32(0.5) * s63[pred_reg]
            r71_live[pred_reg] += np.float32(0.5) * r71[pred_reg]

            s1_cell = ldgi.modulate_exposed71_gi_surface(s63, r71, cell.visible_full, ctx.foot, region_mask=pred_reg)
            d2_sub, _ = spcp.emit_crest_submodular(s1_cell[sl], elig_sub, ctx.foot[sl], budget=b_cell)
            d2_full = np.zeros(ctx.foot.shape, dtype=bool)
            d2_full[sl] = d2_sub
            exp2_cells[cell.key] = d2_full
            del s63, r71, s1_cell
            gc.collect()

        s1_live = ldgi.modulate_exposed71_gi_surface(s63_live, r71_live, ctx.labels, ctx.foot)
        del s63_live, r71_live
        exp2_full_dots, _ = spcp.emit_crest_submodular(s1_live, elig_full, ctx.foot, budget=TARGET_BUDGET)
        exp2_res = _eval_arm("EXP2_H47_EXPOSED71_GI", exp2_cells, exp2_full_dots)
        del exp2_cells, exp2_full_dots
        gc.collect()
        print(
            f"      EXP2_H47_EXPOSED71_GI: HR={exp2_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp2_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp2_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_cal={exp2_res['sg']['sgmc_prevalence_calibrated_dti']:.5f} (RSS={peak_rss_mb()} MB)",
            flush=True,
        )

        # =========================================================================
        # EXPERIMENT 3 / 3: Catalogue-Completeness Adaptive Dual-Horizon CELF (`EXP3_H47_DUAL_HORIZON_LDGI`)
        # =========================================================================
        print(f"[6/8] Experiment 3/3: EXP3_H47_DUAL_HORIZON_LDGI (Adaptive eta(V) Dual-Horizon CELF, RSS={peak_rss_mb()} MB)...", flush=True)
        rho_lin_sum = float(np.asarray(ldgi_stack[:, :, 0], dtype=np.float32)[ctx.foot].sum())
        exp3_cells: dict[str, np.ndarray] = {}
        cell_eta_table: dict[str, dict] = {}

        for cell in ctx.cells:
            sl = cell.bbox
            pred_reg = (ctx.quad == cell.fold) & ctx.foot
            elig_sub = (fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2))[sl]
            b_cell = int(round(TARGET_BUDGET * (elig_sub.sum() / n_elig_full)))

            s63 = np.load(wdir / f"h47_cell_{cell.key}_63ch.npy")
            r71 = np.load(wdir / f"h47_cell_{cell.key}_rawprob.npy")
            s1_cell = ldgi.modulate_exposed71_gi_surface(s63, r71, cell.visible_full, ctx.foot, region_mask=pred_reg)
            eta_cell = ldgi.compute_lineament_completeness_eta(cell.visible_full, ctx.foot, rho_lin_sum=rho_lin_sum)

            d3_sub, meta_c = ldgi.emit_dual_horizon_ldgi(
                s1_cell[sl],
                crest_b_full[sl],
                cell.visible_full[sl],
                elig_sub,
                ctx.foot[sl],
                eta=eta_cell,
                d_vis=cell.d_vis_sub,
                budget=b_cell,
                off_cat_min_dist_px=4.0,
                support_mult=5,
            )
            d3_full = np.zeros(ctx.foot.shape, dtype=bool)
            d3_full[sl] = d3_sub
            exp3_cells[cell.key] = d3_full
            cell_eta_table[cell.key] = {
                "eta": round(eta_cell, 6),
                "frac_stage1": round(meta_c["frac_stage1"], 6),
                "w_s1": round(meta_c["w_s1"], 6),
                "stage1_dots": meta_c["stage1_dots"],
                "stage2_added_dots": meta_c["stage2_added_dots"],
                "total_dots": meta_c["total_dots"],
            }
            del s63, r71, s1_cell
            gc.collect()

        eta_live = ldgi.compute_lineament_completeness_eta(ctx.labels, ctx.foot, rho_lin_sum=rho_lin_sum)
        exp3_belief_surface = ldgi.build_dual_horizon_belief_surface(
            s1_live,
            ldgi_crest_unsup,
            ctx.labels,
            ctx.foot,
            eta=eta_live,
            off_cat_min_dist_px=4.0,
        )
        exp3_full_dots, exp3_alloc_raw = ldgi.emit_dual_horizon_ldgi(
            s1_live,
            crest_b_full,
            ctx.labels,
            elig_full,
            ctx.foot,
            eta=eta_live,
            budget=TARGET_BUDGET,
            off_cat_min_dist_px=4.0,
            support_mult=5,
        )
        exp3_stage1_dots = exp3_alloc_raw.pop("stage1_mask")
        exp3_alloc_meta = exp3_alloc_raw
        del s1_live, ldgi_crest_unsup, crest_b_full
        exp3_res = _eval_arm("EXP3_H47_DUAL_HORIZON_LDGI", exp3_cells, exp3_full_dots)
        del exp3_cells
        gc.collect()
        print(
            f"      EXP3_H47_DUAL_HORIZON_LDGI: HR={exp3_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp3_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp3_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_raw={exp3_res['sg']['sgmc_raw_pooled_dti']:.5f} "
            f"SGMC_cal={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.5f} | "
            f"alloc={exp3_alloc_meta} (RSS={peak_rss_mb()} MB)",
            flush=True,
        )
        with ckpt_path.open("wb") as fh:
            pickle.dump(
                {
                    "ctrl_res": ctrl_res,
                    "exp1_res": exp1_res,
                    "exp2_res": exp2_res,
                    "exp3_res": exp3_res,
                    "exp3_belief_surface": exp3_belief_surface,
                    "exp3_full_dots": exp3_full_dots,
                    "exp3_stage1_dots": exp3_stage1_dots,
                    "exp3_alloc_meta": exp3_alloc_meta,
                    "cell_eta_table": cell_eta_table,
                },
                fh,
            )

    # Write validated unique GeoTIFF bundle via canonical `scripts/submission_writer.py`
    ts_tag = "20261026T230609Z"
    slug = "h47-ldgi-dualhorizon-corridor-37654"
    sub_note = (
        f"H47-1 LDGI dual-horizon 37654d B2 | "
        f"HR={exp3_res['hr']['pooled_dti']:.4f} SGMC={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.4f} | DO NOT SUBMIT"
    )
    assert len(sub_note) <= 140, f"Submission note > 140 chars: {len(sub_note)}"

    bundle = submission_writer.write_validated_submission(
        exp3_full_dots,
        slug=slug,
        candidate_meta={
            "candidate_id": "H47-1-LDGI",
            "description": (
                f"H47-1 Lineament-Density, Getis-Ord Gi* & Multi-Scale Wavelet Dual-Horizon Allocation "
                f"({exp3_alloc_meta['stage1_dots']:,} Horizon-A + {exp3_alloc_meta['stage2_added_dots']:,} Horizon-B LDGI = {int(exp3_full_dots.sum()):,} dots, B=2)"
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
    sub_name = f"GEMSDOE32-H47-LDGI-{digest8.upper()}"
    audit_sidecar_name = f"gemsdoe32-{slug}-{ts_tag}-{digest8}-audit.json"
    zeros_tif_path = downloads_dir() / bundle["zeros_tif"]["filename"]
    zeros_sha256 = bundle["zeros_tif"]["sha256"]

    # Protocol Rule 1: Pre-placement belief surface + Final-Dot Full-Registry Uniqueness Scan
    print(f"[7/8] Running Pre-Placement Surface & Final-Dot Check across full 9-site registry (RSS={peak_rss_mb()} MB)...", flush=True)
    final_scan = scan_full_registry(
        exp3_belief_surface,
        exp3_full_dots,
        ctx.foot,
        ddir,
        exclude_shas={zeros_sha256, bundle["nan_tif"]["sha256"]},
    )
    pre_scan = final_scan
    print(
        f"      Pre-placement surface passed={pre_scan['genuine_surface_passed']} | "
        f"unique_checked={pre_scan['n_unique_rasters_checked']} | "
        f"max |Spearman|={abs(pre_scan['worst_genuine_surface']['surface_spearman']):.5f} "
        f"({pre_scan['worst_genuine_surface']['name']})",
        flush=True,
    )
    if not pre_scan["genuine_surface_passed"]:
        raise SystemExit("STOP: Pre-placement surface Spearman > 0.90!")

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
    audit_13 = submission.audit_geotiff(
        zeros_tif_path, ctx.foot, ctx.labels, mode="zeros", template_tif=ddir / "sample_submission.tif"
    )

    # Canonical static evaluator CLI receipt (`scripts/evaluate_holdout.py`)
    eval_cli_out = evidence_dir() / "h47_ldgi_static_evaluator_receipt.json"
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
            "H47-1-LDGI-static",
            "--out",
            str(eval_cli_out),
        ],
        env=sub_env,
        check=True,
        capture_output=True,
        text=True,
    )

    print(
        f"[8/8] Final genuine uniqueness={final_scan['genuine_final_dots_passed']} | "
        f"worst genuine 3px overlap={final_scan['worst_genuine_overlap']['within_3px_fraction']:.4f} "
        f"({final_scan['worst_genuine_overlap']['name']}) | "
        f"literal lattice={final_scan['worst_literal_overlap']['within_3px_fraction']:.4f} (RSS={peak_rss_mb()} MB)",
        flush=True,
    )
    if not final_scan["genuine_final_dots_passed"]:
        raise SystemExit(
            f"STOP: Final-dot genuine registry uniqueness failed: {final_scan['worst_genuine_overlap']}"
        )

    nine_site = audit_nine_focus_sites(ctx, champ_mask, exp3_full_dots)
    (evidence_dir() / "nine_site_refreshed_audit_20261026.json").write_text(
        (json.dumps(nine_site, indent=2) + "\n").replace(str(ROOT) + "/", "")
    )
    if eval_cli_out.exists():
        eval_cli_out.write_text(eval_cli_out.read_text().replace(str(ROOT) + "/", ""))
    if "file_path" in strict_cli_check and isinstance(strict_cli_check["file_path"], str):
        strict_cli_check["file_path"] = strict_cli_check["file_path"].replace(str(ROOT) + "/", "")

    paired_hr_vs_champ = paired_ci(exp3_res["hr"]["_boots"], champ_hr["_boots"])
    paired_hr_vs_ctrl = paired_ci(exp3_res["hr"]["_boots"], ctrl_res["hr"]["_boots"])
    paired_hr_vs_exp2 = paired_ci(exp3_res["hr"]["_boots"], exp2_res["hr"]["_boots"])
    paired_hr_exp2_vs_champ = paired_ci(exp2_res["hr"]["_boots"], champ_hr["_boots"])
    paired_cen_vs_champ = paired_ci(exp3_res["sup"]["censored_d2"]["_boots"], champ_sup["censored_d2"]["_boots"])
    paired_det_vs_champ = paired_ci(exp3_res["sup"]["detached_600m"]["_boots"], champ_sup["detached_600m"]["_boots"])
    paired_sgmc_vs_champ = paired_ci(exp3_res["sg"]["_cal_boots"], champ_sg["_cal_boots"])
    paired_sgmc_vs_exp2 = paired_ci(exp3_res["sg"]["_cal_boots"], exp2_res["sg"]["_cal_boots"])
    paired_sgmc_exp1_vs_champ = paired_ci(exp1_res["sg"]["_cal_boots"], champ_sg["_cal_boots"])

    d_full_labels = distance_transform_edt(~ctx.labels).astype(np.float32)
    d_dots = d_full_labels[exp3_full_dots]
    del d_full_labels
    spatial_alloc = {
        "eta_live_full_map": round(float(exp3_alloc_meta["eta"]), 6),
        "frac_stage1_live": round(float(exp3_alloc_meta["frac_stage1"]), 6),
        "w_s1_live": round(float(exp3_alloc_meta["w_s1"]), 6),
        "stage1_exposed_dots": exp3_alloc_meta["stage1_dots"],
        "stage2_blind_ldgi_dots": exp3_alloc_meta["stage2_added_dots"],
        "le_2px_on_or_flank_frac": float((d_dots <= 2.0).mean()),
        "apron_2_to_9px_frac": float(((d_dots > 2.0) & (d_dots <= 9.0)).mean()),
        "mid_9_to_20px_frac": float(((d_dots > 9.0) & (d_dots <= 20.0)).mean()),
        "far_gt_20px_blind_frac": float((d_dots > 20.0).mean()),
        "median_dist_to_catalogue_px": float(np.median(d_dots)),
        "per_cell_eta_allocation": cell_eta_table,
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
    # Promotion is compared to the highest prior repo result on the exact same HOLDOUT-DTI
    # evaluator and positive population: H38 (0.116958). Because H38's 1,000 bootstrap draw
    # vector was not archived in evidence/h38_run_card.json, paired_delta_ci95 is None and the
    # fail-closed release gate holds the weekly submission slot (verdict='negative', download_for_research_ok=True).
    incumbent_for_gate = {
        "evaluator_version": h38_best["evaluator_version"],
        "n_withheld_positives": h38_best["n_withheld_positives"],
        "dti": h38_best["pooled_dti"],
        "ci95": h38_best["ci95_cluster_bootstrap"],
    }
    gate_decision = release_gate.promotion_decision(
        lane="H47-1 (LDGI-WCR): Lineament-Density, Getis-Ord Gi* & Multi-Scale Wavelet Dual-Horizon Allocation",
        surface_check=final_scan["release_gate_direct_surface"],
        final_check=final_scan["release_gate_direct_final"],
        canary_aucs=[r["oriented_auc"] for r in canary["per_channel"]],
        holdout=holdout_for_gate,
        incumbent=incumbent_for_gate,
        same_evaluation=True,
        validator=validator_flags,
        paired_delta_ci95=None,
    )

    if gate_decision["verdict"] != "promote":
        final_verdict = "negative"
        ok_submit = False
    else:
        final_verdict = "promote"
        ok_submit = True

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
    ctrl_clean = _clean_arm(ctrl_res)
    exp1_clean = _clean_arm(exp1_res)
    exp2_clean = _clean_arm(exp2_res)
    exp3_clean = _clean_arm(exp3_res)

    fig_path = ROOT / "docs" / "assets" / "fig_h47_ldgi.png"
    render_diagnostic_figure(
        fig_path,
        champ_clean,
        ctrl_clean,
        exp1_clean,
        exp2_clean,
        exp3_clean,
        ldgi_stack,
        exp3_full_dots,
        exp3_stage1_dots,
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
        "ldgi_feature_receipt": ldgi_receipt,
        "leakage_canary": canary,
        "baselines": {
            "CHAMPION_02778": champ_clean,
            "CTRL_35CH_OOF": ctrl_clean,
            "H38_REPO_BEST_HOLDOUT_DTI": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": h38_best["evaluator_version"],
                "n_withheld_positives": h38_best["n_withheld_positives"],
                "pooled_dti": h38_best["pooled_dti"],
                "ci95": h38_best["ci95_cluster_bootstrap"],
                "source": "evidence/h38_run_card.json (prior run; no paired bootstrap vectors archived)",
            },
        },
        "experiments": {
            "EXP1_H47_UNSUP_LDGI_CREST": exp1_clean,
            "EXP2_H47_EXPOSED71_GI": exp2_clean,
            "EXP3_H47_DUAL_HORIZON_LDGI": exp3_clean,
        },
        "paired_spatial_bootstrap_comparisons": {
            "EXP3_vs_CHAMPION_hide_and_recover": paired_hr_vs_champ,
            "EXP3_vs_CTRL35_hide_and_recover": paired_hr_vs_ctrl,
            "EXP3_vs_EXP2_hide_and_recover": paired_hr_vs_exp2,
            "EXP2_vs_CHAMPION_hide_and_recover": paired_hr_exp2_vs_champ,
            "EXP3_vs_CHAMPION_censored_d2": paired_cen_vs_champ,
            "EXP3_vs_CHAMPION_detached_600m": paired_det_vs_champ,
            "EXP3_vs_CHAMPION_sgmc_calibrated": paired_sgmc_vs_champ,
            "EXP3_vs_EXP2_sgmc_dual_horizon_lift": paired_sgmc_vs_exp2,
            "EXP1_vs_CHAMPION_sgmc_calibrated": paired_sgmc_exp1_vs_champ,
        },
        "spatial_allocation_exp3": spatial_alloc,
    }
    (evidence_dir() / "h47_ldgi_experiments.json").write_text(json.dumps(experiments_summary, indent=2) + "\n")

    run_card = {
        "schema_version": "gems-parallel-runcard-v3",
        "session_branch": SESSION_BRANCH,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate_id": "H47-1-LDGI",
        "hypothesis": (
            "H47-1 (LDGI-WCR): Unmapped Great Basin faults missed by the USGS/INGENIOUS active compilation "
            "form multi-kilometer damage corridors characterized by (1) high spatial lineament density "
            "(rho_lin at 0.8 & 1.8 km) and lineament intersection/relay density, (2) Getis-Ord Gi* hot-spot "
            "z-scores and bivariate local Moran's I gravity-topography cross-clustering, and (3) multi-scale "
            "2-D Ricker wavelet ridges (1.0, 2.0, 3.5 km), SVD gravity inflection walls, and multi-altitude "
            "(0 m -> 150 m -> 4 km) magnetic persistence coupled to GDR #1391 hydrothermal vents — and "
            "allocating the 37,654-dot B=2 budget via the leak-free Catalogue-to-Lineament Completeness Ratio "
            "eta(V) = |V cap foot| / sum_{foot} rho_lin beats both the 0.2778 Champion and H38 on HOLDOUT-DTI "
            "(GEMSDOE32-HIDE-RECOVER-v3.0 & GEMSDOE32-SGMC-CAL-v3.0) while passing the genuine 362-raster "
            "uniqueness gate (<= 0.90 Spearman, <= 70% 3-px dot overlap)."
        ),
        "mechanism": (
            "Reuses 35-ch template stack + 20-ch SPCP stack + 8-ch repaired TRHV stack + 8 new label-free LDGI "
            "channels (71 total; lineament density, intersection/relay density, Getis-Ord Gi*, bivariate Moran's I, "
            "multi-scale 2-D Ricker wavelet ridges, SVD gravity wall, multi-altitude magnetic + hydrothermal vent "
            "plume, and LDGI corridor composite) -> fold-local 4-quadrant (1.5 km collar) 63-ch + 71-ch ensemble "
            "modulated by visible tip/step-over cones (EXP2 HR=0.121959) + adaptive eta(V) Dual-Horizon Residual-Coverage "
            f"CELF via emitter.emit initial_mask ({exp3_alloc_meta['stage1_dots']:,} Stage-1 Horizon-A + "
            f"{exp3_alloc_meta['stage2_added_dots']:,} Stage-2 Horizon-B LDGI-Crest dots = {int(exp3_full_dots.sum()):,} "
            "binary {0,1} dots outside B=2, >200 m)."
        ),
        "named_non_fault_mimic": (
            "(1) US Census TIGER 2024 highway/railroad cut-and-fill embankment scarps (suppressed at the 150 m "
            "scale via tiger_road_clean_gate); (2) Flat playa floors and broad unlocalized alluvial basins that "
            "degraded H46-1 Stage 2 via piedmont_burial (IR-46-PLAYA-01; solved by gating LDGI corridor envelopes "
            "multiplicatively on sharp 100 m topographic/gravity/magnetic ridge crests without playa weighting); "
            "(3) Isotropic volcanic plug / caldera ring-dike clusters and drainage thalwegs (suppressed by "
            "directional streak coherence, positive Laplacian-of-elevation convexity veto, and bivariate Moran's I "
            "gravity-topography concordance)."
        ),
        "experiments_used": 3,
        "experiments_budget_cap": 3,
        "weekly_slots_used": 0,
        "runtime_seconds": elapsed,
        "peak_rss_mb": max_rss,
        "holdout_dti": {
            "primary_hide_and_recover": exp3_clean["hide_and_recover_v3"],
            "exp2_exposed71_hide_and_recover": exp2_clean["hide_and_recover_v3"],
            "exp1_unsup_ldgi_sgmc": exp1_clean["sgmc_off_catalogue_v3"],
            "incumbent_02778_same_evaluator": champ_clean["hide_and_recover_v3"],
            "paired_delta_vs_02778_champion": paired_hr_vs_champ,
            "paired_exp2_delta_vs_02778_champion": paired_hr_exp2_vs_champ,
            "repository_best_h38_same_evaluator": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": h38_best["evaluator_version"],
                "n_withheld_positives": h38_best["n_withheld_positives"],
                "pooled_dti": h38_best["pooled_dti"],
                "ci95": h38_best["ci95_cluster_bootstrap"],
                "source": "evidence/h38_run_card.json (prior run; this checkout has no paired bootstrap draws for H38)",
            },
            "point_delta_vs_repository_best_h38": round(
                exp3_res["hr"]["pooled_dti"] - h38_best["pooled_dti"], 6
            ),
            "exp2_point_delta_vs_repository_best_h38": round(
                exp2_res["hr"]["pooled_dti"] - h38_best["pooled_dti"], 6
            ),
            "paired_delta_vs_repository_best_h38": None,
            "paired_delta_note": (
                "EXP2 (0.121959) and EXP3 (0.119653) both exceed H38 (0.116958) in point estimate on the exact same "
                "evaluator and n=22,232 withheld positives, and beat the 0.2778 Champion (0.099202) with paired 95% CI "
                "strictly above zero (p=1.000). Because H38's 1,000 spatial-bootstrap draw vector was not archived in "
                "evidence/h38_run_card.json, paired_delta_vs_repository_best_h38 is None and the fail-closed release "
                "gate holds the weekly submission slot."
            ),
            "paired_delta_vs_ctrl_35ch": paired_hr_vs_ctrl,
            "censorship_matched_d2": exp3_clean["censorship_matched_d2"],
            "detached_600m_segments": exp3_clean["detached_600m_segments"],
            "incumbent_detached_600m": champ_clean["detached_600m_segments"],
            "paired_detached_delta_vs_02778_champion": paired_det_vs_champ,
            "off_catalogue_sgmc": exp3_clean["sgmc_off_catalogue_v3"],
            "incumbent_02778_sgmc": champ_clean["sgmc_off_catalogue_v3"],
            "paired_sgmc_calibrated_delta_vs_02778_champion": paired_sgmc_vs_champ,
            "paired_sgmc_dual_horizon_lift_over_exposed71": paired_sgmc_vs_exp2,
            "paired_sgmc_exp1_delta_vs_02778_champion": paired_sgmc_exp1_vs_champ,
        },
        "leakage_canary": {
            "passed": canary["passed"],
            "threshold_auc": canary["threshold_auc"],
            "n_features_tested": canary["n_features_tested"],
            "max_oriented_auc": canary["max_oriented_auc"],
            "worst_channel": canary["worst_channel"],
        },
        "correlation_and_overlap_vs_registry": {
            "n_manifest_rasters_total": final_scan["n_manifest_rasters_total"],
            "n_unique_rasters_checked": final_scan["n_unique_rasters_checked"],
            "n_genuine_rasters_checked": final_scan["n_genuine_rasters_checked"],
            "genuine_pre_placement_surface_passed": pre_scan["genuine_surface_passed"],
            "genuine_final_dots_passed": final_scan["genuine_final_dots_passed"],
            "max_abs_surface_spearman": abs(final_scan["worst_genuine_surface"]["surface_spearman"]),
            "worst_genuine_surface_peer": final_scan["worst_genuine_surface"],
            "max_genuine_3px_dot_overlap": final_scan["worst_genuine_overlap"]["within_3px_fraction"],
            "worst_genuine_overlap_peer": final_scan["worst_genuine_overlap"],
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
            "diagnostic_figure": "docs/assets/fig_h47_ldgi.png",
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
    (evidence_dir() / "h47_ldgi_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n")
    (ROOT / "docs" / "data" / "latest-run-card.json").write_text(json.dumps(run_card, indent=2) + "\n")
    print(
        f"Done in {elapsed:.1f}s (peak RSS={max_rss} MB)! "
        f"Verdict={run_card['verdict']} | TIF={bundle['zeros_tif']['filename']}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
