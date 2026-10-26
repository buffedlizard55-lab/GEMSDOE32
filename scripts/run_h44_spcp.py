#!/usr/bin/env python3
"""Execute Pre-Registered Single Lane H44-1 (SPCP) within the strict 3-experiment budget.

Reuses shared tools strictly (Protocol Rule 2):
  - `.cache/gems_work/feature_stack.npy` (`scripts/build_features.py`)
  - `gems32.holdout` / `scripts/evaluate_holdout.py`
  - `gems32.emitter.emit`
  - `scripts/submission_writer.py` & `scripts/check_submission.py --strict-finite`
  - `gems32.release_gate`
"""

from __future__ import annotations

import gc
import hashlib
import json
import os
import pickle
import subprocess
import sys
import time
from pathlib import Path

os.environ.setdefault("GDAL_CACHEMAX", "32")

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import features, holdout, metric, release_gate, spcp, submission  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402
import submission_writer  # noqa: E402

TARGET_BUDGET = 37_654
B_COLLAR_PX = 2.0


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
    1) `detached_600m`: scores ONLY withheld fault pixels >= 6.0 px (600 m) from visible faults
       (eliminates near-trace gap-filling bias `IR-42-INSTR-01`).
    2) `censored_d2`: applies `d_hidden > 2.0 px` to OOF predictions so dynamic OOF arms face the
       exact same hidden-fault B=2 exclusion already baked into static full-map `.tif` files.
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

        # --- (A) Censorship-matched (`d_hidden > censor_hidden_px`) ---
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

        # --- (B) Detached-only (`d_visible >= detach_min_px`) ---
        det_keep = cell.d_vis_sub[ty, tx] >= detach_min_px
        if det_keep.any():
            dty, dtx = ty[det_keep], tx[det_keep]
            n_det_pos += int(dty.size)
            det_truth = np.zeros(cell.active_sub.shape, dtype=bool)
            det_truth[dty, dtx] = True
            k_dg_det = metric.kernel(distance_transform_edt(~det_truth))
            # Restrict evaluation region away from non-detached hidden fragments (>=4 px from attached hidden)
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
    r = rankdata(vec).astype(np.float64)
    r -= r.mean()
    nrm = float(np.linalg.norm(r))
    return (r / nrm) if nrm > 0.0 else r


def scan_full_registry(
    surface: np.ndarray,
    dots: np.ndarray | None,
    foot: np.ndarray,
    ddir: Path,
    exclude_shas: set[str] | None = None,
) -> dict:
    """Memory-lean, exact full-footprint Spearman & <=3px directional overlap scan across all
    unique-SHA256 `3730x3292` rasters in `registry/focus_registry_manifest.json` + `data_manifest.json`.
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

    # Exact 100% full-footprint (5,167,373 pixels, zero sampling!) Spearman & <=3px overlap
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
        is_lattice = ("r13-lattice-s5" in name)
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

    # Direct exact cross-verification with `gems32.release_gate.compare_registry` one raster at a time
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
    worst_ov_all = max(rows, key=lambda r: r["within_3px_fraction"])

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


def audit_nine_focus_sites(ctx: holdout.HoldoutContext, champ_mask: np.ndarray, h44_mask: np.ndarray) -> dict:
    """Apples-to-apples byte-verified audit of all 9 focus sites' best historical & newest 2026-10-26 TIFs."""
    fman = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    by_repo: dict[str, list[dict]] = {}
    for r in fman["rasters"]:
        if r.get("status") == "ok":
            by_repo.setdefault(r["repo"], []).append(r)

    yy, xx = np.mgrid[-3:4, -3:4]
    disk3 = (yy * yy + xx * xx) <= 9
    champ_near3 = binary_dilation(champ_mask, structure=disk3)
    h44_near3 = binary_dilation(h44_mask, structure=disk3)

    # Pick representative newest 2026-10-25/26 primary TIF per focus repo
    preferred_patterns = {
        "GEMSDOE24": "dprf1-stitched-oof-tworegime-20261026",
        "GEMSDOE25": "h71-hgpc-blind-b2-sapd3-k3p5-20261026",
        "GEMSDOE27": "h31-drcg-wl-celf28-20261026",
        "GEMSDOE28": "s20-nchc-20261026",
        "GEMSDOE30": "FFL1-fusion_edge-44090-20261026",
        "GEMSDOE31": "h31s-udap-sslic-37654-20261026",
        "GEMSDOE32": "h33-h33-2-b2-20261004",
        "GEMSDOE33": "a33-r2-csht-transfer-37654-20261026",
        "GEMSDOE36": "atvr36-20261026.tif",
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
        ov_h44 = float(h44_near3[m].mean()) if n_dots > 0 else 0.0
        site_rows.append(
            {
                "repo": repo,
                "head_ref": fman["refs"].get(repo, "")[:12],
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
                "within_3px_of_h44_spcp": round(ov_h44, 4),
            }
        )
    return {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "refs": fman["refs"],
        "sites": site_rows,
    }


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    wdir = work_dir()
    wdir.mkdir(parents=True, exist_ok=True)

    base_stack_path = wdir / "feature_stack.npy"
    if not base_stack_path.exists():
        raise SystemExit("Run scripts/build_features.py first to create .cache/gems_work/feature_stack.npy")

    extra_path = wdir / "spcp_extra_20ch.npy"
    if extra_path.exists() and "--rebuild-features" not in sys.argv:
        print("[1/7] Reusing cached 20-channel SPCP stack (.cache/gems_work/spcp_extra_20ch.npy)...", flush=True)
        extra_stack = np.load(extra_path, mmap_mode="r")
        assert extra_stack.shape[2] == len(spcp.SPCP_EXTRA_CHANNELS)
        extra_receipt = {
            "n_extra_channels": len(spcp.SPCP_EXTRA_CHANNELS),
            "channel_names": list(spcp.SPCP_EXTRA_CHANNELS),
            "shape": list(extra_stack.shape),
            "reused_cached_memmap": True,
        }
    else:
        print("[1/7] Building 20 label-free SPCP channels...", flush=True)
        _, extra_receipt = spcp.build_spcp_extra_stack(ddir, base_stack_path, out_path=extra_path)
        gc.collect()

    base_stack = np.load(base_stack_path, mmap_mode="r")
    extra_stack = np.load(extra_path, mmap_mode="r")

    print("[2/7] Loading HoldoutContext (draws 20/21 x 4 quadrants, 1.5 km collar)...", flush=True)
    ctx = holdout.load_holdout_context(ddir)
    disk2 = spcp._disk_mask(B_COLLAR_PX)
    elig_full = ctx.foot & ~binary_dilation(ctx.labels, structure=disk2)
    n_elig_full = int(elig_full.sum())

    # Precompute fold training regions & evaluation domains matching `load_holdout_context`
    fold_train: dict[int, np.ndarray] = {}
    fold_domain: dict[int, np.ndarray] = {}
    for f in holdout.FOLDS:
        q = ctx.quad == f
        collar = binary_dilation(q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX) & ctx.foot
        fold_train[f] = ctx.foot & ~collar
        fold_domain[f] = binary_erosion(q, iterations=holdout.DOMAIN_ERODE) & ctx.foot

    print("[3/7] Running Protocol Rule 4 Leakage Canary on all 55 channels...", flush=True)
    canary = spcp.run_leakage_canary(base_stack, extra_stack, list(features.CHANNELS), ctx, max_auc=0.90)
    print(
        f"      Canary passed={canary['passed']} | n={canary['n_features_tested']} | "
        f"worst={canary['worst_channel']} ({canary['max_oriented_auc']:.5f})",
        flush=True,
    )
    if not canary["passed"]:
        raise SystemExit(f"STOP: Leakage canary failed on {canary['worst_channel']} ({canary['max_oriented_auc']})")

    # Load 0.2778 Champion static mask for baseline comparison
    champ_path = downloads_dir() / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    with rasterio.open(champ_path) as ds:
        champ_mask = (ds.read(1) > 0) & ctx.foot
    champ_hr = holdout.evaluate_hide_and_recover(champ_mask, ctx, b_visible_px=B_COLLAR_PX, name="CHAMPION_02778")
    champ_sup = evaluate_detached_and_censored(champ_mask, ctx, b_visible_px=B_COLLAR_PX)
    champ_sg = holdout.evaluate_sgmc_with_ci(champ_mask, ctx, name="CHAMPION_02778")
    print(
        f"      Baseline CHAMPION_02778: HR={champ_hr['pooled_dti']:.5f} "
        f"Detached={champ_sup['detached_600m']['dti']:.5f} "
        f"SGMC_raw={champ_sg['sgmc_raw_pooled_dti']:.5f} SGMC_cal={champ_sg['sgmc_prevalence_calibrated_dti']:.5f}",
        flush=True,
    )

    # Helper to evaluate a per-cell OOF dict + full-map emission mask
    def _eval_arm(name: str, cell_masks: dict[str, np.ndarray], full_mask: np.ndarray) -> dict:
        hr = holdout.evaluate_hide_and_recover(cell_masks, ctx, b_visible_px=B_COLLAR_PX, name=name)
        sup = evaluate_detached_and_censored(cell_masks, ctx, b_visible_px=B_COLLAR_PX)
        sg = holdout.evaluate_sgmc_with_ci(full_mask, ctx, name=name)
        return {"name": name, "hr": hr, "sup": sup, "sg": sg, "full_dots": int(full_mask.sum())}

    ckpt_path = wdir / "h44_stage5_checkpoint.pkl"
    if ckpt_path.exists() and "--rerun-models" not in sys.argv:
        print("[4-5/7] Loading cached 3-experiment OOF checkpoint (.cache/gems_work/h44_stage5_checkpoint.pkl)...", flush=True)
        with ckpt_path.open("rb") as fh:
            ckpt = pickle.load(fh)
        ctrl_res = ckpt["ctrl_res"]
        exp1_res = ckpt["exp1_res"]
        exp2_res = ckpt["exp2_res"]
        exp3_res = ckpt["exp3_res"]
        exp3_oof_surface = ckpt["exp3_oof_surface"]
        exp3_full_dots = ckpt["exp3_full_dots"]
        print(
            f"      EXP3_H44_SARPU_SPCP (cached): HR={exp3_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp3_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp3_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_cal={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.5f}",
            flush=True,
        )
    else:
        # --- Control: Fold-local 35-channel template HistGB ---
        print("[4/7] Fitting fold-local Control (CTRL_35CH_OOF)...", flush=True)
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
        del ctrl_cells, ctrl_oof_full, ctrl_full_dots
        gc.collect()
        print(
            f"      CTRL_35CH_OOF: HR={ctrl_res['hr']['pooled_dti']:.5f} "
            f"Cen={ctrl_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={ctrl_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_cal={ctrl_res['sg']['sgmc_prevalence_calibrated_dti']:.5f}",
            flush=True,
        )

        # =========================================================================
        # EXPERIMENT 1 / 3: Label-Free Physical Curvature & Conduit Crest (`EXP1_H44_UNSUP_SPCP`)
        # =========================================================================
        print("[5/7] Experiment 1/3: EXP1_H44_UNSUP_SPCP (label-free physical composite)...", flush=True)
        unsup_surface = np.asarray(extra_stack[:, :, -1], dtype=np.float32)
        exp1_cells: dict[str, np.ndarray] = {}
        for cell in ctx.cells:
            elig_cell = fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2)
            b_cell = int(round(TARGET_BUDGET * (elig_cell.sum() / n_elig_full)))
            dots_c, _ = spcp.emit_crest_submodular(unsup_surface, elig_cell, ctx.foot, budget=b_cell)
            exp1_cells[cell.key] = dots_c
        exp1_full_dots, exp1_crest = spcp.emit_crest_submodular(
            unsup_surface, elig_full, ctx.foot, budget=TARGET_BUDGET
        )
        exp1_res = _eval_arm("EXP1_H44_UNSUP_SPCP", exp1_cells, exp1_full_dots)
        del exp1_cells, exp1_full_dots, exp1_crest, unsup_surface
        gc.collect()
        print(
            f"      EXP1_H44_UNSUP_SPCP: HR={exp1_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp1_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp1_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_cal={exp1_res['sg']['sgmc_prevalence_calibrated_dti']:.5f}",
            flush=True,
        )

        # =========================================================================
        # EXPERIMENT 2 / 3: Naive Binary 55-Channel OOF (`EXP2_H44_NAIVE_BIN55`)
        # =========================================================================
        print("[5/7] Experiment 2/3: EXP2_H44_NAIVE_BIN55 (naive y=0 binary 55-ch ablation)...", flush=True)
        exp2_cells: dict[str, np.ndarray] = {}
        exp2_oof_full = np.zeros(ctx.foot.shape, dtype=np.float32)
        for cell in ctx.cells:
            tr = fold_train[cell.fold]
            vis = cell.visible_full & tr
            elig_cell = fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2)
            b_cell = int(round(TARGET_BUDGET * (elig_cell.sum() / n_elig_full)))
            pred_reg = (ctx.quad == cell.fold) & ctx.foot if cell.seed == 20 else fold_domain[cell.fold]
            prob = spcp.fit_predict_naive_binary(
                base_stack, extra_stack, tr, vis, pred_reg, seed=2000 + cell.seed * 10 + cell.fold
            )
            if cell.seed == 20:
                exp2_oof_full[pred_reg] = prob[pred_reg]
            dots_c, _ = spcp.emit_crest_submodular(prob, elig_cell, ctx.foot, budget=b_cell)
            exp2_cells[cell.key] = dots_c
            del prob
            gc.collect()
        exp2_full_dots, _ = spcp.emit_crest_submodular(exp2_oof_full, elig_full, ctx.foot, budget=TARGET_BUDGET)
        exp2_res = _eval_arm("EXP2_H44_NAIVE_BIN55", exp2_cells, exp2_full_dots)
        del exp2_cells, exp2_oof_full, exp2_full_dots
        gc.collect()
        print(
            f"      EXP2_H44_NAIVE_BIN55: HR={exp2_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp2_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp2_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_cal={exp2_res['sg']['sgmc_prevalence_calibrated_dti']:.5f}",
            flush=True,
        )

        # =========================================================================
        # EXPERIMENT 3 / 3: Full Fold-Local SAR-PU Propensity-Debiased SPCP (`EXP3_H44_SARPU_SPCP`)
        # =========================================================================
        print("[5/7] Experiment 3/3: EXP3_H44_SARPU_SPCP (SAR-PU propensity-debiased SPCP)...", flush=True)
        exp3_cells: dict[str, np.ndarray] = {}
        exp3_oof_surface = np.zeros(ctx.foot.shape, dtype=np.float32)
        for cell in ctx.cells:
            tr = fold_train[cell.fold]
            vis = cell.visible_full & tr
            elig_cell = fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2)
            b_cell = int(round(TARGET_BUDGET * (elig_cell.sum() / n_elig_full)))
            pred_reg = (ctx.quad == cell.fold) & ctx.foot
            blended, _ = spcp.fit_predict_sarpu_spcp(
                base_stack,
                extra_stack,
                tr,
                vis,
                pred_reg,
                ctx.foot,
                seed=3000 + cell.seed * 10 + cell.fold,
            )
            exp3_oof_surface[pred_reg] += 0.5 * blended[pred_reg]
            dots_c, _ = spcp.emit_crest_submodular(blended, elig_cell, ctx.foot, budget=b_cell)
            exp3_cells[cell.key] = dots_c
            del blended
            gc.collect()

        exp3_full_dots, _ = spcp.emit_crest_submodular(
            exp3_oof_surface, elig_full, ctx.foot, budget=TARGET_BUDGET
        )
        exp3_res = _eval_arm("EXP3_H44_SARPU_SPCP", exp3_cells, exp3_full_dots)
        del exp3_cells
        gc.collect()
        print(
            f"      EXP3_H44_SARPU_SPCP: HR={exp3_res['hr']['pooled_dti']:.5f} "
            f"Cen={exp3_res['sup']['censored_d2']['dti']:.5f} "
            f"Det={exp3_res['sup']['detached_600m']['dti']:.5f} "
            f"SGMC_raw={exp3_res['sg']['sgmc_raw_pooled_dti']:.5f} "
            f"SGMC_cal={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.5f}",
            flush=True,
        )
        with ckpt_path.open("wb") as fh:
            pickle.dump(
                {
                    "ctrl_res": ctrl_res,
                    "exp1_res": exp1_res,
                    "exp2_res": exp2_res,
                    "exp3_res": exp3_res,
                    "exp3_oof_surface": exp3_oof_surface,
                    "exp3_full_dots": exp3_full_dots,
                },
                fh,
            )

    # Protocol Rule 1: Check pre-placement surface!
    print("[6/7] Running 289-raster Pre-Placement Surface Check across all 9 focus repos...", flush=True)
    pre_scan = scan_full_registry(exp3_oof_surface, None, ctx.foot, ddir)
    print(
        f"      Pre-placement surface passed={pre_scan['genuine_surface_passed']} | "
        f"max |Spearman|={abs(pre_scan['worst_genuine_surface']['surface_spearman']):.5f} "
        f"({pre_scan['worst_genuine_surface']['name']})",
        flush=True,
    )
    if not pre_scan["genuine_surface_passed"]:
        raise SystemExit("STOP: Pre-placement surface Spearman > 0.90!")

    # Write validated unique GeoTIFF via canonical `scripts/submission_writer.py`
    ts_tag = "20261026T053000Z"
    slug = "h44-spcp-sarpu-curvconduit-37654"
    sub_note = (
        f"H44-1 SPCP SAR-PU curv+conduit 37654d B2 | "
        f"HR={exp3_res['hr']['pooled_dti']:.4f} SGMC={exp3_res['sg']['sgmc_prevalence_calibrated_dti']:.4f} | DO NOT SUBMIT"
    )
    assert len(sub_note) <= 140, f"Note too long: {len(sub_note)}"

    bundle = submission_writer.write_validated_submission(
        exp3_full_dots,
        slug=slug,
        candidate_meta={
            "candidate_id": "H44-1-SPCP",
            "description": "H44-1 SAR-PU Propensity-Debiased Potential-Field Curvature Tensor & Hydrothermal-Conduit Breach (37,654 dots, B=2)",
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
    sub_name = f"GEMSDOE32-H44-SPCP-{digest8.upper()}"
    audit_sidecar_name = f"gemsdoe32-{slug}-{ts_tag}-{digest8}-audit.json"
    zeros_tif_path = downloads_dir() / bundle["zeros_tif"]["filename"]
    zeros_sha256 = bundle["zeros_tif"]["sha256"]

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

    # Also evaluate emitted static `.tif` via canonical `scripts/evaluate_holdout.py` CLI
    eval_cli_out = evidence_dir() / "h44_spcp_static_evaluator_receipt.json"
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
            "H44-1-SPCP-static",
            "--out",
            str(eval_cli_out),
        ],
        env=sub_env,
        check=True,
        capture_output=True,
        text=True,
    )

    print("[7/7] Running Final-Dot 289-Raster Scan + 9-Site Apples-to-Apples Audit...", flush=True)
    final_scan = scan_full_registry(
        exp3_oof_surface, exp3_full_dots, ctx.foot, ddir, exclude_shas={zeros_sha256, bundle["nan_tif"]["sha256"]}
    )
    print(
        f"      Final genuine uniqueness={final_scan['genuine_final_dots_passed']} | "
        f"worst genuine 3px overlap={final_scan['worst_genuine_overlap']['within_3px_fraction']:.4f} "
        f"({final_scan['worst_genuine_overlap']['name']}) | "
        f"literal lattice={final_scan['worst_literal_overlap']['within_3px_fraction']:.4f}",
        flush=True,
    )

    nine_site = audit_nine_focus_sites(ctx, champ_mask, exp3_full_dots)
    (evidence_dir() / "nine_site_live_audit_20261026.json").write_text(
        (json.dumps(nine_site, indent=2) + "\n").replace(str(ROOT) + "/", "")
    )
    if eval_cli_out.exists():
        eval_cli_out.write_text(eval_cli_out.read_text().replace(str(ROOT) + "/", ""))
    if "file_path" in strict_cli_check and isinstance(strict_cli_check["file_path"], str):
        strict_cli_check["file_path"] = strict_cli_check["file_path"].replace(str(ROOT) + "/", "")

    # Paired bootstrap CIs on exact matched 256 spatial blocks
    paired_hr_vs_champ = paired_ci(exp3_res["hr"]["_boots"], champ_hr["_boots"])
    paired_hr_vs_ctrl = paired_ci(exp3_res["hr"]["_boots"], ctrl_res["hr"]["_boots"])
    paired_hr_vs_exp2 = paired_ci(exp3_res["hr"]["_boots"], exp2_res["hr"]["_boots"])
    paired_cen_vs_champ = paired_ci(exp3_res["sup"]["censored_d2"]["_boots"], champ_sup["censored_d2"]["_boots"])
    paired_det_vs_champ = paired_ci(exp3_res["sup"]["detached_600m"]["_boots"], champ_sup["detached_600m"]["_boots"])
    paired_sgmc_vs_champ = paired_ci(exp3_res["sg"]["_cal_boots"], champ_sg["_cal_boots"])
    paired_sgmc_vs_exp2 = paired_ci(exp3_res["sg"]["_cal_boots"], exp2_res["sg"]["_cal_boots"])

    # Spatial distance-to-catalogue allocation profile
    d_full_labels = distance_transform_edt(~ctx.labels).astype(np.float32)
    d_dots = d_full_labels[exp3_full_dots]
    del d_full_labels
    spatial_alloc = {
        "le_2px_on_or_flank_frac": float((d_dots <= 2.0).mean()),
        "apron_2_to_9px_frac": float(((d_dots > 2.0) & (d_dots <= 9.0)).mean()),
        "mid_9_to_20px_frac": float(((d_dots > 9.0) & (d_dots <= 20.0)).mean()),
        "far_gt_20px_blind_frac": float((d_dots > 20.0).mean()),
        "median_dist_to_catalogue_px": float(np.median(d_dots)),
    }

    # Official fail-closed `release_gate.promotion_decision` (using literal all-registry check including lattice-s5)
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
        lane="H44-1 (SPCP): SAR-PU Propensity-Debiased Potential-Field Curvature Tensor & Hydrothermal-Conduit Breach",
        surface_check=final_scan["release_gate_direct_surface"],
        final_check=final_scan["release_gate_direct_final"],
        canary_aucs=[r["oriented_auc"] for r in canary["per_channel"]],
        holdout=holdout_for_gate,
        incumbent=incumbent_for_gate,
        same_evaluation=True,
        validator=validator_flags,
        paired_delta_ci95=paired_hr_vs_champ["ci95"],
    )

    elapsed = round(time.time() - t0, 2)

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
    experiments_summary = {
        "session_branch": "arena/744ab113-gemsdoe32",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_seconds": elapsed,
        "experiments_used": 3,
        "experiments_budget_cap": 3,
        "extra_feature_receipt": extra_receipt,
        "leakage_canary": canary,
        "baselines": {
            "CHAMPION_02778": champ_clean,
            "CTRL_35CH_OOF": _clean_arm(ctrl_res),
        },
        "experiments": {
            "EXP1_H44_UNSUP_SPCP": _clean_arm(exp1_res),
            "EXP2_H44_NAIVE_BIN55": _clean_arm(exp2_res),
            "EXP3_H44_SARPU_SPCP": _clean_arm(exp3_res),
        },
        "paired_spatial_bootstrap_comparisons": {
            "EXP3_vs_CHAMPION_hide_and_recover": paired_hr_vs_champ,
            "EXP3_vs_CTRL35_hide_and_recover": paired_hr_vs_ctrl,
            "EXP3_vs_EXP2_hide_and_recover": paired_hr_vs_exp2,
            "EXP3_vs_CHAMPION_censored_d2": paired_cen_vs_champ,
            "EXP3_vs_CHAMPION_detached_600m": paired_det_vs_champ,
            "EXP3_vs_CHAMPION_sgmc_calibrated": paired_sgmc_vs_champ,
            "EXP3_vs_EXP2_sgmc_sarpu_lift": paired_sgmc_vs_exp2,
        },
        "spatial_allocation_exp3": spatial_alloc,
    }
    (evidence_dir() / "h44_spcp_experiments.json").write_text(json.dumps(experiments_summary, indent=2) + "\n")

    # Authoritative Protocol Rule 5 Run Card (`evidence/h44_spcp_run_card.json`)
    run_card = {
        "schema_version": "gems-parallel-runcard-v3",
        "session_branch": "arena/744ab113-gemsdoe32",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "candidate_id": "H44-1-SPCP",
        "hypothesis": (
            "H44-1 (SPCP): Blind basin-floor and hydrothermally altered Great Basin faults missing from the "
            "USGS/INGENIOUS surface scarp catalogue concentrate along strike-concordant Phillips (2007) principal "
            "negative-curvature crests of isostatic gravity (Band 05) and RTP magnetics (Band 02), hydrothermal "
            "magnetite-destruction troughs paired with GeoDAWN K-on-Th potassic metasomatism, nuisance-residualized "
            "MT conductivity clay-cap edges (Band 17), and Lahontan-contour-orthogonal 1 m 3DEP LiDAR scarplets — "
            "recoverable only when supervised training is debiased for photogeologic mapping propensity e(z) via "
            "fold-local Bekker-Davis SAR-PU learning (curing IR-A8A-PU-BIAS-01)."
        ),
        "mechanism": (
            "Reuses 35-ch cached template stack + 20 label-free SPCP curvature/hydrothermal/LiDAR channels (55 total, "
            "0 catalogue/SGMC inputs) -> fold-local 4-quadrant (1.5 km collar) SAR-PU observability propensity e(z) "
            "estimation + reliable-negative screening + inverse-propensity positive weighting + cover-adaptive "
            "exponent lambda(z)=0.22+0.34*(1-e_tilde) blending P_SARPU with unsupervised multi-physics crests -> "
            "1-px oriented cross-strike parabolic crest concentration -> fold-local B=2 (>200 m) exclusion -> "
            "exact 300 m triangular-kernel lazy-greedy submodular packing (37,654 binary {0,1} dots)."
        ),
        "named_non_fault_mimic": (
            "Pleistocene Lake Lahontan horizontal wave-cut shoreline benches (suppressed by sin^2(theta_scarp - "
            "theta_contour) contour-orthogonality veto) and unaltered granitic pluton / ash-flow tuff margins & "
            "flat conductive saline playas (suppressed by K-on-Th residualization, elevation/depth MT residualization, "
            "and cross-domain gravity-magnetic strike concordance)."
        ),
        "experiments_used": 3,
        "experiments_budget_cap": 3,
        "runtime_seconds": elapsed,
        "holdout_dti": {
            "primary_hide_and_recover": experiments_summary["experiments"]["EXP3_H44_SARPU_SPCP"]["hide_and_recover_v3"],
            "incumbent_02778_same_evaluator": champ_clean["hide_and_recover_v3"],
            "paired_delta_vs_02778_champion": paired_hr_vs_champ,
            "paired_delta_vs_ctrl_35ch": paired_hr_vs_ctrl,
            "censorship_matched_d2": experiments_summary["experiments"]["EXP3_H44_SARPU_SPCP"]["censorship_matched_d2"],
            "detached_600m_segments": experiments_summary["experiments"]["EXP3_H44_SARPU_SPCP"]["detached_600m_segments"],
            "incumbent_detached_600m": champ_clean["detached_600m_segments"],
            "paired_detached_delta_vs_02778_champion": paired_det_vs_champ,
            "off_catalogue_sgmc": experiments_summary["experiments"]["EXP3_H44_SARPU_SPCP"]["sgmc_off_catalogue_v3"],
            "incumbent_02778_sgmc": champ_clean["sgmc_off_catalogue_v3"],
            "paired_sgmc_calibrated_delta_vs_02778_champion": paired_sgmc_vs_champ,
            "paired_sgmc_sarpu_lift_over_naive_bin55": paired_sgmc_vs_exp2,
        },
        "leakage_canary": {
            "passed": canary["passed"],
            "threshold_auc": canary["threshold_auc"],
            "n_features_tested": canary["n_features_tested"],
            "max_oriented_auc": canary["max_oriented_auc"],
            "worst_channel": canary["worst_channel"],
        },
        "correlation_and_overlap_vs_registry": {
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
        "ok_to_submit": bool(gate_decision["verdict"] == "promote"),
        "verdict": gate_decision["verdict"],
    }
    (evidence_dir() / "h44_spcp_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n")
    print(f"Done in {elapsed:.1f}s! Verdict={run_card['verdict']} | TIF={bundle['zeros_tif']['filename']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
