#!/usr/bin/env python3
"""H45-1 Two-Regime Split-Budget Allocation (single pre-registered experiment).

Pre-registration (frozen before execution): docs/research/h45-tworegime-preregistration-20261026.md

Reuses shared tools, does not fork them (Protocol Rule 2):
  - `.cache/gems_work/feature_stack.npy`             scripts/build_features.py
  - `spcp.build_spcp_extra_stack` / `run_leakage_canary`   gems32.spcp (H44 SPCP stack, 55-ch canary)
  - `spcp.fit_predict_naive_binary` (EXP2 arm)       gems32.spcp
  - `spcp.fit_predict_sarpu_spcp(return_propensity)` (EXP3 arm, propensity exposed by a
                                                       backward-compatible keyword added in this session)
  - `spcp.emit_crest_submodular` -> `emitter.emit`   gems32.spcp / gems32.emitter
  - `holdout.evaluate_hide_and_recover`, `evaluate_sgmc_with_ci`, `h44.evaluate_detached_and_censored`
  - `h44.paired_ci`, `h44.scan_full_registry`         scripts/run_h44_spcp.py (import, no re-run)
  - `submission_writer.write_validated_submission`, `scripts/check_submission.py --strict-finite`

Writes ONLY H45 artifacts: evidence/h45_tworegime_run_card.json and H45-named downloads.
It never overwrites H44 evidence.
"""

from __future__ import annotations

import gc
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("GDAL_CACHEMAX", "32")

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import features, holdout, spcp, submission  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402
import submission_writer  # noqa: E402
import run_h44_spcp as h44  # noqa: E402  (module-level code is definitions only)

TARGET_BUDGET = 37_654
B_COLLAR_PX = 2.0
REGIME_E = 0.5
SLUG = "h45-tworegime-split-37654"
CHAMP_NAME = "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
# Published H44 numbers (README section 8.2 / evidence/h44_spcp_run_card.json), used only for replica checks.
H44_PUBLISHED = {
    "EXP2_HR": 0.107700,
    "EXP3_HR": 0.069841,
    "EXP3_SGMC_CAL": 0.077736,
    "CHAMP_SGMC_CAL": 0.064121,
}
REPLICA_TOL = 0.002


def _jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return None
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj


def _eval_arm(name: str, cell_masks, full_mask: np.ndarray, ctx) -> dict:
    hr = holdout.evaluate_hide_and_recover(cell_masks, ctx, b_visible_px=B_COLLAR_PX, name=name)
    sup = h44.evaluate_detached_and_censored(cell_masks, ctx, b_visible_px=B_COLLAR_PX)
    sg = holdout.evaluate_sgmc_with_ci(full_mask, ctx, name=name)
    return {"name": name, "hr": hr, "sup": sup, "sg": sg, "full_dots": int(full_mask.sum())}


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    t0 = time.time()
    run_utc = datetime.now(timezone.utc)
    ts_tag = run_utc.strftime("%Y%m%dT%H%M%SZ")
    ddir = data_dir()
    wdir = work_dir()
    base_stack_path = wdir / "feature_stack.npy"
    if not base_stack_path.exists():
        raise SystemExit("Run scripts/build_features.py first.")

    extra_path = wdir / "spcp_extra_20ch.npy"
    if not extra_path.exists():
        print("[1] Building 20-channel SPCP stack (shared H44 builder)...", flush=True)
        spcp.build_spcp_extra_stack(ddir, base_stack_path, out_path=extra_path)
        gc.collect()
    base_stack = np.load(base_stack_path, mmap_mode="r")
    extra_stack = np.load(extra_path, mmap_mode="r")

    print("[2] Loading HoldoutContext (4 quadrants x 2 draws, 1.5 km collar)...", flush=True)
    ctx = holdout.load_holdout_context(ddir)
    disk2 = spcp._disk_mask(B_COLLAR_PX)
    elig_full = ctx.foot & ~binary_dilation(ctx.labels, structure=disk2)
    n_elig_full = int(elig_full.sum())
    fold_train: dict[int, np.ndarray] = {}
    fold_domain: dict[int, np.ndarray] = {}
    from scipy.ndimage import binary_erosion

    for f in holdout.FOLDS:
        q = ctx.quad == f
        collar = binary_dilation(q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX) & ctx.foot
        fold_train[f] = ctx.foot & ~collar
        fold_domain[f] = binary_erosion(q, iterations=holdout.DOMAIN_ERODE) & ctx.foot

    print("[3] Leakage canary, 55 channels (shared canary, C1)...", flush=True)
    canary = spcp.run_leakage_canary(base_stack, extra_stack, list(features.CHANNELS), ctx, max_auc=0.90)
    print(
        f"    passed={canary['passed']} n={canary['n_features_tested']} "
        f"worst={canary['worst_channel']} ({canary['max_oriented_auc']:.5f})",
        flush=True,
    )
    if not canary["passed"]:
        raise SystemExit(f"STOP (C1): leakage canary failed on {canary['worst_channel']}")

    champ_path = downloads_dir() / CHAMP_NAME
    with rasterio.open(champ_path) as ds:
        champ_mask = (ds.read(1) > 0) & ctx.foot
    champ_hr = holdout.evaluate_hide_and_recover(champ_mask, ctx, b_visible_px=B_COLLAR_PX, name="CHAMPION_02778")
    champ_sup = h44.evaluate_detached_and_censored(champ_mask, ctx, b_visible_px=B_COLLAR_PX)
    champ_sg = holdout.evaluate_sgmc_with_ci(champ_mask, ctx, name="CHAMPION_02778")
    print(
        f"    champion HR={champ_hr['pooled_dti']:.5f} SGMC_cal={champ_sg['sgmc_prevalence_calibrated_dti']:.5f}",
        flush=True,
    )

    # ---- fold-local fits (same seeds and prediction regions as H44 EXP2 / EXP3) ----
    print("[4] Fold-local fits: naive (EXP2 replica) + SAR-PU (EXP3 replica) + propensity e(z)...", flush=True)
    naive_oof = np.zeros(ctx.foot.shape, dtype=np.float32)
    spcp_oof = np.zeros(ctx.foot.shape, dtype=np.float32)
    e_oof = np.zeros(ctx.foot.shape, dtype=np.float32)
    cells_exp2: dict[str, np.ndarray] = {}
    cells_exp3: dict[str, np.ndarray] = {}
    cells_h45: dict[str, np.ndarray] = {}
    regime_log: list[dict] = []
    for cell in ctx.cells:
        tr = fold_train[cell.fold]
        vis = cell.visible_full & tr
        elig_cell = fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2)
        n_el = int(elig_cell.sum())
        b_cell = int(round(TARGET_BUDGET * (n_el / n_elig_full)))
        pred_quad = (ctx.quad == cell.fold) & ctx.foot
        pred_dom = pred_quad if cell.seed == 20 else fold_domain[cell.fold]  # EXP2 convention

        naive = spcp.fit_predict_naive_binary(
            base_stack, extra_stack, tr, vis, pred_dom, seed=2000 + cell.seed * 10 + cell.fold
        )
        blended, _p_sarpu, e_pred = spcp.fit_predict_sarpu_spcp(
            base_stack,
            extra_stack,
            tr,
            vis,
            pred_quad,
            ctx.foot,
            seed=3000 + cell.seed * 10 + cell.fold,
            return_propensity=True,
        )

        # EXP2 and EXP3 replicas, exactly as H44 emitted them per cell
        d2, _ = spcp.emit_crest_submodular(naive, elig_cell, ctx.foot, budget=b_cell)
        d3, _ = spcp.emit_crest_submodular(blended, elig_cell, ctx.foot, budget=b_cell)
        cells_exp2[cell.key] = d2
        cells_exp3[cell.key] = d3

        # Two-regime split: budget proportional to eligible area in each propensity regime
        A = elig_cell & (e_pred >= REGIME_E)
        B = elig_cell & (e_pred < REGIME_E)
        n_a = int(A.sum())
        b_a = int(round(b_cell * (n_a / n_el))) if n_el else 0
        b_b = b_cell - b_a
        dA, _ = spcp.emit_crest_submodular(naive, A, ctx.foot, budget=b_a)
        dB, _ = spcp.emit_crest_submodular(blended, B, ctx.foot, budget=b_b)
        cells_h45[cell.key] = dA | dB
        regime_log.append(
            {
                "cell": cell.key,
                "b_cell": b_cell,
                "eligible_px": n_el,
                "regime_A_px": n_a,
                "regime_B_px": int(B.sum()),
                "b_A": b_a,
                "b_B": b_b,
                "dots_A": int(dA.sum()),
                "dots_B": int(dB.sum()),
            }
        )

        if cell.seed == 20:
            naive_oof[pred_quad] = naive[pred_quad]
        spcp_oof[pred_quad] += np.float32(0.5) * blended[pred_quad]
        e_oof[pred_quad] += np.float32(0.5) * e_pred[pred_quad]
        del naive, blended, e_pred, d2, d3, dA, dB
        gc.collect()
        print(f"    {cell.key}: budget={b_cell} A={n_a} b_A={b_a} b_B={b_b}", flush=True)

    # ---- full-map (final candidate) emission, stitched OOF, full-catalogue B=2 exclusion ----
    print("[5] Full-map emission (EXP2 replica, EXP3 replica, H45 two-regime)...", flush=True)
    exp2_full, _ = spcp.emit_crest_submodular(naive_oof, elig_full, ctx.foot, budget=TARGET_BUDGET)
    exp3_full, _ = spcp.emit_crest_submodular(spcp_oof, elig_full, ctx.foot, budget=TARGET_BUDGET)
    A_full = elig_full & (e_oof >= REGIME_E)
    B_full = elig_full & (e_oof < REGIME_E)
    n_af = int(A_full.sum())
    b_af = int(round(TARGET_BUDGET * (n_af / n_elig_full)))
    b_bf = TARGET_BUDGET - b_af
    dAf, _ = spcp.emit_crest_submodular(naive_oof, A_full, ctx.foot, budget=b_af)
    dBf, _ = spcp.emit_crest_submodular(spcp_oof, B_full, ctx.foot, budget=b_bf)
    h45_full = dAf | dBf
    print(
        f"    full dots: EXP2={int(exp2_full.sum())} EXP3={int(exp3_full.sum())} H45={int(h45_full.sum())} "
        f"(A px={n_af}, b_A={b_af}, b_B={b_bf})",
        flush=True,
    )

    # ---- holdout arms (HIDE-RECOVER-v3.0, detached >=600 m, censorship-matched, SGMC) ----
    print("[6] Scoring arms on the shared holdout evaluator...", flush=True)
    arm_exp2 = _eval_arm("EXP2_REPLICA_NAIVE_BIN55", cells_exp2, exp2_full, ctx)
    arm_exp3 = _eval_arm("EXP3_REPLICA_SARPU_SPCP", cells_exp3, exp3_full, ctx)
    arm_h45 = _eval_arm("H45_TWOREGIME_SPLIT", cells_h45, h45_full, ctx)
    print(
        f"    EXP2 HR={arm_exp2['hr']['pooled_dti']:.5f}  EXP3 HR={arm_exp3['hr']['pooled_dti']:.5f}  "
        f"H45 HR={arm_h45['hr']['pooled_dti']:.5f}",
        flush=True,
    )
    print(
        f"    SGMC_cal: EXP2={arm_exp2['sg']['sgmc_prevalence_calibrated_dti']:.5f} "
        f"EXP3={arm_exp3['sg']['sgmc_prevalence_calibrated_dti']:.5f} "
        f"H45={arm_h45['sg']['sgmc_prevalence_calibrated_dti']:.5f}",
        flush=True,
    )

    # Replica checks (void if the baseline does not reproduce)
    replica = {
        "exp2_hr_abs_diff_vs_published": abs(arm_exp2["hr"]["pooled_dti"] - H44_PUBLISHED["EXP2_HR"]),
        "exp3_hr_abs_diff_vs_published": abs(arm_exp3["hr"]["pooled_dti"] - H44_PUBLISHED["EXP3_HR"]),
        "exp3_sgmc_cal_abs_diff_vs_published": abs(
            arm_exp3["sg"]["sgmc_prevalence_calibrated_dti"] - H44_PUBLISHED["EXP3_SGMC_CAL"]
        ),
        "champion_sgmc_cal_abs_diff_vs_published": abs(
            champ_sg["sgmc_prevalence_calibrated_dti"] - H44_PUBLISHED["CHAMP_SGMC_CAL"]
        ),
        "tolerance": REPLICA_TOL,
    }
    replica["passed"] = bool(
        replica["exp2_hr_abs_diff_vs_published"] <= REPLICA_TOL
        and replica["exp3_hr_abs_diff_vs_published"] <= REPLICA_TOL
        and replica["exp3_sgmc_cal_abs_diff_vs_published"] <= REPLICA_TOL
        and replica["champion_sgmc_cal_abs_diff_vs_published"] <= 0.001
    )
    print(f"    baseline replica check passed={replica['passed']}", flush=True)

    # Paired spatial-block bootstrap CIs
    p_hr_vs_exp2 = h44.paired_ci(arm_h45["hr"]["_boots"], arm_exp2["hr"]["_boots"])
    p_hr_vs_exp3 = h44.paired_ci(arm_h45["hr"]["_boots"], arm_exp3["hr"]["_boots"])
    p_sg_vs_champ = h44.paired_ci(arm_h45["sg"]["_cal_boots"], champ_sg["_cal_boots"])
    p_sg_vs_exp3 = h44.paired_ci(arm_h45["sg"]["_cal_boots"], arm_exp3["sg"]["_cal_boots"])

    # ---- Pre-placement surface (C5) on the composite regime-ranked surface ----
    print("[7] Pre-placement surface check against registry (C5)...", flush=True)
    rank_naive = spcp._rank_unit_f32(naive_oof, ctx.foot)
    rank_spcp = spcp._rank_unit_f32(spcp_oof, ctx.foot)
    surface = np.where(e_oof >= REGIME_E, rank_naive, rank_spcp).astype(np.float32)
    surface = np.where(ctx.foot, surface, np.float32(0.0))
    del rank_naive, rank_spcp
    pre_scan = h44.scan_full_registry(surface, None, ctx.foot, ddir)
    print(
        f"    surface passed={pre_scan['genuine_surface_passed']} "
        f"max|rho|={abs(pre_scan['worst_genuine_surface']['surface_spearman']):.5f} "
        f"({pre_scan['worst_genuine_surface']['name']})",
        flush=True,
    )

    # ---- Write the candidate (format C8) ----
    print("[8] Writing validated GeoTIFF via shared writer...", flush=True)
    note = (
        f"H45-1 two-regime split 37654d B2 | HR={arm_h45['hr']['pooled_dti']:.4f} "
        f"SGMC={arm_h45['sg']['sgmc_prevalence_calibrated_dti']:.4f} | DO NOT SUBMIT"
    )
    assert len(note) <= 140, len(note)
    bundle = submission_writer.write_validated_submission(
        h45_full,
        slug=SLUG,
        candidate_meta={
            "candidate_id": "H45-1-TWOREGIME",
            "description": "H45-1 two-regime split-budget: naive 55-ch crest in propensity-exposed regime, "
            "SAR-PU SPCP crest in blind regime (37,654 dots, B=2)",
            "catalogue_hidden_mean": round(arm_h45["hr"]["pooled_dti"], 6),
            "catalogue_hidden_per_quadrant": {k: round(v, 6) for k, v in arm_h45["hr"]["per_quadrant_dti"].items()},
            "sgmc_prevalence_calibrated_dti": round(arm_h45["sg"]["sgmc_prevalence_calibrated_dti"], 6),
            "submission_note_zeros": note,
            "submission_note_nan": note,
            "slot_decision": "NOT-AUTHORIZED (C7 literal lattice and selector pending)",
        },
        ddir=ddir,
        out_dir=downloads_dir(),
        timestamp_tag=ts_tag,
    )
    digest8 = bundle["content_digest8"]
    zeros_path = downloads_dir() / bundle["zeros_tif"]["filename"]
    nan_path = downloads_dir() / bundle["nan_tif"]["filename"]
    zeros_sha = bundle["zeros_tif"]["sha256"]
    nan_sha = bundle["nan_tif"]["sha256"]
    zip_info = bundle["zeros_zip"]

    sub_env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "GEMS_DATA_DIR": str(ddir)}
    chk = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_submission.py"), "--strict-finite", str(zeros_path)],
        env=sub_env,
        capture_output=True,
        text=True,
    )
    strict_passed = chk.returncode == 0
    strict_report = chk.stdout.split("\n[PASSED]")[0].split("\n[FAILED]")[0].strip()
    try:
        strict_report_json = json.loads(strict_report)
    except json.JSONDecodeError:
        strict_report_json = {"raw": strict_report[:2000]}
    audit = submission.audit_geotiff(zeros_path, ctx.foot, ctx.labels, mode="zeros", template_tif=ddir / "sample_submission.tif")
    audit_checks = audit["checks"]
    fmt_ok = bool(
        strict_passed
        and audit_checks["single_band"]
        and audit_checks["in_footprint_all_finite"]
        and audit_checks["in_footprint_range_0_1"]
        and audit_checks["crs_epsg_32611"]
        and audit_checks["dimensions_3730x3292"]
        and audit_checks["exact_reference_grid_match"]
    )
    with rasterio.open(zeros_path) as ds:
        raw = ds.read(1)
        raster_facts = {
            "crs": ds.crs.to_string() if ds.crs else None,
            "shape": [int(ds.height), int(ds.width)],
            "transform": [float(v) for v in ds.transform[:6]],
            "dtype": ds.dtypes[0],
            "band_count": int(ds.count),
            "nodata": ds.nodata,
        }
    finite_all = int(np.isfinite(raw).sum())
    raster_facts.update(
        {
            "finite_cells": finite_all,
            "total_cells": int(raw.size),
            "nan_cells": int(np.isnan(raw).sum()),
            "min": float(np.nanmin(raw)),
            "max": float(np.nanmax(raw)),
            "positive_pixels": int((raw > 0).sum()),
        }
    )
    audit_path = downloads_dir() / f"gemsdoe32-{SLUG}-{ts_tag}-{digest8}-audit.json"
    audit_path.write_text(json.dumps({"strict_cli": strict_report_json, "audit_geotiff": _jsonable(audit)}, indent=2) + "\n")

    # ---- Final-dot uniqueness (C6 genuine, C7 literal lattice) ----
    print("[9] Final-dot registry scan (C6 genuine, C7 literal lattice)...", flush=True)
    final_scan = h44.scan_full_registry(
        surface, h45_full, ctx.foot, ddir, exclude_shas={zeros_sha, nan_sha}
    )
    print(
        f"    genuine final={final_scan['genuine_final_dots_passed']} "
        f"worst genuine 3px={final_scan['worst_genuine_overlap']['within_3px_fraction']:.4f} "
        f"({final_scan['worst_genuine_overlap']['name']}) "
        f"literal lattice 3px={final_scan['worst_literal_overlap']['within_3px_fraction']:.4f}",
        flush=True,
    )

    n_rasters_present = sum(1 for r in json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())["rasters"]
                            if (ROOT / r["local"]).exists())
    n_rasters_manifest = len(json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())["rasters"])

    # ---- Pre-registered criteria C1..C8 ----
    crit = {
        "C1_leakage_canary": bool(canary["passed"]),
        "C2_hr_beats_exp2_replica_paired_ci_lb_gt_0": bool(
            arm_h45["hr"]["pooled_dti"] > arm_exp2["hr"]["pooled_dti"] and p_hr_vs_exp2["ci95"][0] > 0
        ),
        "C3_sgmc_cal_beats_champion_paired_ci_lb_gt_0": bool(
            arm_h45["sg"]["sgmc_prevalence_calibrated_dti"] > champ_sg["sgmc_prevalence_calibrated_dti"]
            and p_sg_vs_champ["ci95"][0] > 0
        ),
        "C4_detached_600m_not_below_exp2_replica": bool(
            arm_h45["sup"]["detached_600m"]["dti"] >= arm_exp2["sup"]["detached_600m"]["dti"]
        ),
        "C5_surface_all_genuine_registry_rasters_le_0_90": bool(pre_scan["genuine_surface_passed"]),
        "C6_final_dots_le_70pct_all_genuine_registry_rasters": bool(final_scan["genuine_final_dots_passed"]),
        "C7_literal_lattice_le_70pct": bool(final_scan["literal_all_rasters_final_passed"]),
        "C8_format_strict_finite_and_grid": bool(fmt_ok),
    }
    gates_all = all(crit.values())
    baseline_void = not replica["passed"]
    verdict = "promote" if (gates_all and not baseline_void) else "negative"
    if baseline_void:
        verdict = "void-baseline-not-reproduced"

    coverage = {
        "registry_manifest_rasters": n_rasters_manifest,
        "registry_rasters_present_locally": n_rasters_present,
        "registry_rasters_checked_genuine": int(final_scan["n_genuine_rasters_checked"]),
        "registry_rasters_skipped": final_scan["skipped_non_submission_blobs"],
        "coverage_complete": bool(n_rasters_present == n_rasters_manifest),
    }
    if not coverage["coverage_complete"]:
        verdict = "void-registry-incomplete"

    dots_on_cat = int((h45_full & ctx.labels).sum())
    run_card = {
        "schema_version": 1,
        "generated_utc": run_utc.isoformat(),
        "lane_id": "H45-1 (two-regime split-budget; provisional lane, see preregistration section 0)",
        "preregistration": "docs/research/h45-tworegime-preregistration-20261026.md",
        "hypothesis": "Routing each budget regime by fold-local SAR-PU observability propensity e(z) "
        "(>=0.5 naive 55-ch crest, <0.5 SAR-PU SPCP crest) wins both HIDE-RECOVER and off-catalogue SGMC.",
        "mechanism": "fold-local e(z) -> budget split by eligible area -> per-regime 1-px crest submodular emission "
        "-> stitched OOF -> full-catalogue B=2 exclusion -> 37,654 dots",
        "named_non_fault_mimic": "near-trace gap-filling on exposed fronts (detached >=600 m and censorship-matched "
        "checks) and alluvial/playa or pluton ring curvature in blind basins (SGMC diagnostic)",
        "evaluator": {
            "holdout": holdout.HIDE_RECOVER_EVALUATOR_VERSION,
            "alpha_beta_kernel": "alpha=0.2 beta=0.8 300 m triangular",
            "b_visible_px": B_COLLAR_PX,
            "withheld_positives": int(arm_h45["hr"]["n_withheld_positives"]),
            "label": "HOLDOUT-DTI (local evaluator; not organizer-confirmed)",
        },
        "canary": {"passed": canary["passed"], "n_channels": canary["n_features_tested"],
                   "worst_channel": canary["worst_channel"], "max_oriented_auc": canary["max_oriented_auc"]},
        "baseline_replica": replica,
        "arms": {
            "CHAMPION_02778_static": {
                "hr": _jsonable({k: champ_hr[k] for k in ("pooled_dti", "ci95_cluster_bootstrap", "n_withheld_positives")}),
                "sgmc_cal": _jsonable({k: champ_sg[k] for k in ("sgmc_prevalence_calibrated_dti", "sgmc_calibrated_ci95")}),
                "detached_600m_dti": float(champ_sup["detached_600m"]["dti"]),
            },
            "EXP2_REPLICA_NAIVE_BIN55": {
                "full_map_dots": arm_exp2["full_dots"],
                "hr": _jsonable({k: arm_exp2["hr"][k] for k in ("pooled_dti", "ci95_cluster_bootstrap", "n_withheld_positives")}),
                "sgmc_cal": _jsonable({k: arm_exp2["sg"][k] for k in ("sgmc_prevalence_calibrated_dti", "sgmc_calibrated_ci95")}),
                "detached_600m_dti": float(arm_exp2["sup"]["detached_600m"]["dti"]),
            },
            "EXP3_REPLICA_SARPU_SPCP": {
                "full_map_dots": arm_exp3["full_dots"],
                "hr": _jsonable({k: arm_exp3["hr"][k] for k in ("pooled_dti", "ci95_cluster_bootstrap", "n_withheld_positives")}),
                "sgmc_cal": _jsonable({k: arm_exp3["sg"][k] for k in ("sgmc_prevalence_calibrated_dti", "sgmc_calibrated_ci95")}),
                "detached_600m_dti": float(arm_exp3["sup"]["detached_600m"]["dti"]),
            },
            "H45_TWOREGIME_SPLIT": {
                "full_map_dots": arm_h45["full_dots"],
                "dots_on_catalogue": dots_on_cat,
                "hr": _jsonable({k: arm_h45["hr"][k] for k in ("pooled_dti", "ci95_cluster_bootstrap", "n_withheld_positives", "per_quadrant_dti")}),
                "censorship_matched_d2_dti": float(arm_h45["sup"]["censored_d2"]["dti"]),
                "detached_600m_dti": float(arm_h45["sup"]["detached_600m"]["dti"]),
                "sgmc_cal": _jsonable({k: arm_h45["sg"][k] for k in ("sgmc_prevalence_calibrated_dti", "sgmc_calibrated_ci95", "sgmc_raw_pooled_dti")}),
            },
        },
        "paired_ci": {
            "H45_minus_EXP2_HR": p_hr_vs_exp2,
            "H45_minus_EXP3_HR": p_hr_vs_exp3,
            "H45_minus_CHAMPION_SGMC_CAL": p_sg_vs_champ,
            "H45_minus_EXP3_SGMC_CAL": p_sg_vs_exp3,
        },
        "regime_split": {
            "rule": f"e(z) >= {REGIME_E} -> naive crest; else SAR-PU crest; budget by eligible-area share",
            "full_map_regime_A_px": n_af,
            "full_map_b_A": b_af,
            "full_map_b_B": b_bf,
            "per_cell": regime_log,
        },
        "uniqueness": {
            "pre_placement_surface": {
                "rule": "max |Spearman| over genuine registry rasters <= 0.90 (composite regime-ranked surface)",
                "passed": bool(pre_scan["genuine_surface_passed"]),
                "worst_genuine_surface": _jsonable(pre_scan["worst_genuine_surface"]),
            },
            "final_dots": {
                "rule": "<=70% of dots within 3 px of any genuine registry raster's dots",
                "passed_genuine": bool(final_scan["genuine_final_dots_passed"]),
                "worst_genuine_overlap": _jsonable(final_scan["worst_genuine_overlap"]),
                "literal_lattice_overlap": _jsonable(final_scan["worst_literal_overlap"]),
                "literal_all_rasters_passed": bool(final_scan["literal_all_rasters_final_passed"]),
            },
            "coverage": coverage,
            "top10_by_abs_spearman": _jsonable(final_scan["top10_by_abs_spearman"]),
            "top15_by_overlap": _jsonable(final_scan["top15_by_overlap"]),
        },
        "validator": {
            "strict_cli_passed": strict_passed,
            "strict_cli_report": strict_report_json,
            "audit_checks": _jsonable(audit_checks),
            "raster": raster_facts,
        },
        "artifacts": {
            "zeros_tif": {"filename": zeros_path.name, "sha256": zeros_sha, "bytes": zeros_path.stat().st_size},
            "nan_tif": {"filename": nan_path.name, "sha256": nan_sha},
            "zip": {"filename": zip_info["filename"], "sha256": zip_info["sha256"]},
            "audit_json": audit_path.name,
        },
        "submission_name": f"GEMSDOE32-H45-TWOREGIME-{digest8.upper()}",
        "submission_note": note,
        "submission_note_length": len(note),
        "criteria": crit,
        "criteria_all_passed": gates_all,
        "release_verdict_fail_closed": verdict,
        "ok_to_download_for_research": True,
        "ok_to_submit_to_live_portal": False,
        "slot_used": False,
        "selector_required": True,
        "experiments_used": 1,
        "experiments_budget": 3,
        "runtime_seconds": round(time.time() - t0, 1),
        "irregularities": [
            "Lane paragraph absent from the supplied prompt; lane is provisional (README section 8.4 next step 1).",
            "Literal 5-px calibration lattice gate (C7) is unsatisfiable for dense maps; reported, not exempted.",
        ],
    }
    out = evidence_dir() / "h45_tworegime_run_card.json"
    out.write_text(json.dumps(run_card, indent=2) + "\n")
    print(f"[done] {run_card['release_verdict_fail_closed']} in {run_card['runtime_seconds']}s -> {out.name}", flush=True)
    print(json.dumps(run_card["criteria"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
