#!/usr/bin/env python3
"""Run the frozen three-arm A9-H1 MDRC-PGRN-PU experiment and emit one fail-closed GeoTIFF.

No competition slot is used. Every catalogue-dependent training, exclusion, and
emission operation is derived from each holdout cell's visible fault segments.
"""
from __future__ import annotations

import gc
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import emitter, features, holdout, mdrc  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402
from gems32.pgrn_pu import (  # noqa: E402
    compose_physics_guarded_surface,
    extract_feature_rows,
    fit_reliable_negative_model,
    predict_models_on_mask,
    select_training_indices,
    two_polarity_feature_canary,
)
from gems32.registry_audit import audit_final_dots, audit_surface, load_manifest  # noqa: E402
from gemsdoe32.submission import validate_submission_geotiff  # noqa: E402
from submission_writer import write_validated_submission  # noqa: E402

SEED = 20261026
BUDGET = 37_654
B_VISIBLE_PX = 2.0
SUPPORT_CAP_FULL = 230_000
SUPPORT_CAP_CELL = 72_000
QUANTILES = (0.60, 0.70, 0.80)
ARMS = {
    "EXP1_PGRN80": (0.80,),
    "EXP2_PGRN60": (0.60,),
    "EXP3_PGRN_BAG": (0.60, 0.70, 0.80),
}
MAX_RUNTIME_SECONDS = 2 * 60 * 60


def _json_clean(value):
    if isinstance(value, dict):
        return {str(k): _json_clean(v) for k, v in value.items() if not str(k).startswith("_")}
    if isinstance(value, (list, tuple)):
        return [_json_clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    return value


def _quadrant_budgets(foot: np.ndarray, quad: np.ndarray) -> dict[int, int]:
    counts = np.array([int((foot & (quad == q)).sum()) for q in range(4)], dtype=np.float64)
    exact = counts / counts.sum() * BUDGET
    result = np.floor(exact).astype(int)
    for q in np.argsort(-(exact - result))[: BUDGET - int(result.sum())]:
        result[q] += 1
    assert int(result.sum()) == BUDGET
    return {q: int(result[q]) for q in range(4)}


def _emit_surface(
    surface: np.ndarray,
    active: np.ndarray,
    d_visible: np.ndarray,
    *,
    budget: int,
    support_cap: int,
) -> tuple[np.ndarray, dict]:
    eligible = np.asarray(active, bool) & (np.asarray(d_visible) > B_VISIBLE_PX) & np.isfinite(surface)
    gated = np.where(eligible, np.maximum(surface, 0.0), 0.0).astype(np.float32)
    positive = gated > 0.0
    npos = int(positive.sum())
    if npos < budget:
        raise RuntimeError(f"only {npos:,} eligible positive support pixels for budget {budget:,}")
    if npos > support_cap:
        vals = gated[positive]
        threshold = float(np.partition(vals, vals.size - support_cap)[vals.size - support_cap])
        gated = np.where(gated >= threshold, gated, 0.0).astype(np.float32)
    mask, log = emitter.emit(gated, budget=budget, prior_dti=0.0)
    if int(mask.sum()) != budget:
        raise RuntimeError(f"emitter returned {int(mask.sum())} rather than budget {budget}")
    return mask, log.as_dict()


def _arm_posterior(predictions: dict[float, np.ndarray], quantiles: tuple[float, ...]) -> np.ndarray:
    return np.mean(np.stack([predictions[q] for q in quantiles], axis=0), axis=0, dtype=np.float32)


def _surface_for_arm(
    predictions: dict[float, np.ndarray],
    quantiles: tuple[float, ...],
    prior: np.ndarray,
    gate: np.ndarray,
    footprint: np.ndarray,
) -> np.ndarray:
    raw = _arm_posterior(predictions, quantiles)
    fused = compose_physics_guarded_surface(raw, prior, gate, footprint)
    return mdrc.sharpen_ridge_crest(fused, footprint)


def _fit_quantile_models(
    base: np.ndarray,
    extra: np.ndarray,
    visible: np.ndarray,
    train_mask: np.ndarray,
    physical_prior: np.ndarray,
    *,
    seed: int,
) -> tuple[dict[float, object], dict[str, dict]]:
    models = {}
    receipts = {}
    for i, q in enumerate(QUANTILES):
        idx, y, receipt = select_training_indices(
            visible,
            train_mask,
            physical_prior,
            reliable_negative_quantile=q,
            rng=np.random.default_rng(seed + i * 1009),
            halo_exclude_px=5.0,
            max_positive=50_000,
            negative_ratio=4,
        )
        X = extract_feature_rows(base, extra, idx)
        models[q] = fit_reliable_negative_model(X, y, seed=seed + i * 1009)
        receipts[f"q{q:.2f}"] = receipt.as_dict()
        del X, idx, y
        gc.collect()
    return models, receipts


def _paired_bootstrap_delta(candidate: dict, reference: dict) -> dict:
    cb = np.asarray(candidate["_boots"], dtype=np.float64)
    rb = np.asarray(reference["_boots"], dtype=np.float64)
    n = min(cb.size, rb.size)
    delta = cb[:n] - rb[:n]
    return {
        "point_delta": float(candidate["pooled_dti"] - reference["pooled_dti"]),
        "ci95": [float(np.percentile(delta, 2.5)), float(np.percentile(delta, 97.5))],
        "paired_replicates": int(n),
    }


def _hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    started = time.time()
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ddir, wdir, edir, outdir = data_dir(), work_dir(), evidence_dir(), downloads_dir()
    base_path = wdir / "feature_stack.npy"
    extra_path = wdir / "mdrc_extra_stack.npy"
    for required in (ddir / "training_features.tif", ddir / "labels.tif", ddir / "sample_submission.tif", base_path, extra_path):
        if not required.is_file():
            raise FileNotFoundError(f"required input/cache absent: {required}")

    print("[A9 setup] loading shared fold context and cached 57-channel feature stack", flush=True)
    ctx = holdout.load_holdout_context(ddir)
    if ctx.visible_by_cell is None or len(ctx.visible_by_cell) != len(ctx.cells):
        raise RuntimeError("shared holdout context did not expose all fold-visible catalogues")
    base = np.lib.format.open_memmap(base_path, mode="r")
    extra = np.lib.format.open_memmap(extra_path, mode="r")
    domains = mdrc.unsupervised_domain_surfaces(extra, ctx.foot)
    prior = domains["MDRC_Unsup_4Domain"]
    corrob_gate = domains["_gate"]
    del domains

    print("[A9 G1] two-polarity single-feature leakage canary", flush=True)
    channel_names = list(features.CHANNELS) + list(mdrc.MDRC_EXTRA_CHANNELS)
    canary = two_polarity_feature_canary(
        base, extra, ctx.labels, ctx.foot, ctx.quad, channel_names, seed=SEED
    )
    print(f"  worst={canary['worst_channel']} AUC={canary['worst_auc']:.5f}; passed={canary['passed']}", flush=True)
    if not canary["passed"]:
        raise RuntimeError("leakage canary failed; no model was fitted")

    q_budgets = _quadrant_budgets(ctx.foot, ctx.quad)
    collars = {
        q: binary_dilation(ctx.quad == q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX) & ctx.foot
        for q in range(4)
    }
    cell_masks: dict[str, dict[str, np.ndarray]] = {arm: {} for arm in ARMS}
    fit_receipts: dict[str, dict] = {}
    cell_cache = wdir / "arena9_pgrn_cell_masks.npz"
    cell_receipt_cache = wdir / "arena9_pgrn_cell_fits.json"

    if cell_cache.exists() and cell_receipt_cache.exists():
        print("[A9 EXP1-3] reusing deterministic fold-visible cell cache", flush=True)
        cached = np.load(cell_cache)
        for arm in ARMS:
            for cell in ctx.cells:
                cell_masks[arm][cell.key] = cached[f"{arm}__{cell.key}"]
        fit_receipts = json.loads(cell_receipt_cache.read_text())
    else:
        print("[A9 EXP1-3] fitting each holdout cell from fold-visible faults only", flush=True)
        for cell_i, cell in enumerate(ctx.cells):
            if time.time() - started > MAX_RUNTIME_SECONDS:
                raise TimeoutError("two-hour experiment budget reached before completing holdout fits")
            q = cell.fold
            visible = ctx.visible_by_cell[cell.key]
            train_mask = ctx.foot & ~collars[q]
            # Hidden test and hidden training components are absent from visible by construction.
            models, receipts = _fit_quantile_models(
                base,
                extra,
                visible,
                train_mask,
                prior,
                seed=SEED + 10_000 * (cell_i + 1),
            )
            target = (ctx.quad == q) & ctx.foot
            predictions = predict_models_on_mask(models, base, extra, target)
            rs, cs = cell.bbox
            fit_receipts[cell.key] = {
                "fold": q,
                "draw": cell.seed,
                "visible_positive_pixels": int(visible.sum()),
                "hidden_truth_pixels": int(cell.n_truth),
                "train_region_pixels": int(train_mask.sum()),
                "quantiles": receipts,
            }
            pred_sub = {qq: arr[rs, cs] for qq, arr in predictions.items()}
            prior_sub, gate_sub = prior[rs, cs], corrob_gate[rs, cs]
            foot_sub = ctx.foot[rs, cs]
            for arm, qset in ARMS.items():
                surface_sub = _surface_for_arm(pred_sub, qset, prior_sub, gate_sub, foot_sub)
                mask_sub, _ = _emit_surface(
                    surface_sub,
                    cell.active_sub,
                    cell.d_visible_sub,
                    budget=q_budgets[q],
                    support_cap=SUPPORT_CAP_CELL,
                )
                cell_masks[arm][cell.key] = mask_sub
            del models, predictions, pred_sub
            gc.collect()
            print(f"  {cell.key}: fit q60/q70/q80; budget={q_budgets[q]:,}", flush=True)
        np.savez_compressed(
            cell_cache,
            **{
                f"{arm}__{cell.key}": cell_masks[arm][cell.key]
                for arm in ARMS
                for cell in ctx.cells
            },
        )
        cell_receipt_cache.write_text(json.dumps(fit_receipts, indent=2) + "\n")

    holdout_results = {}
    for arm in ARMS:
        result = holdout.evaluate_hide_and_recover(
            cell_masks[arm],
            ctx,
            b_visible_px=B_VISIBLE_PX,
            n_boot=2000,
            seed=SEED,
            name=arm,
        )
        holdout_results[arm] = result
        print(
            f"  {arm}: HOLDOUT-DTI={result['pooled_dti']:.6f} "
            f"CI95={result['ci95_cluster_bootstrap']} n={result['n_withheld_positives']}",
            flush=True,
        )

    # Arm selection is frozen to primary hide-and-recover DTI; SGMC is not consulted.
    selected_arm = max(ARMS, key=lambda a: holdout_results[a]["pooled_dti"])
    print(f"[A9 selection] {selected_arm} selected by primary holdout only", flush=True)

    # Exact-evaluator references.
    d28_path = ddir / "scored" / "gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
    d28 = holdout.read_binary(d28_path) & ctx.foot
    champion_hr = holdout.evaluate_hide_and_recover(
        d28, ctx, b_visible_px=2.0, n_boot=2000, seed=SEED, name="CHAMPION_h33-2-b2_rule"
    )
    paired_vs_champion = _paired_bootstrap_delta(holdout_results[selected_arm], champion_hr)
    h38_card = json.loads((edir / "h38_run_card.json").read_text())
    h38_best = float(h38_card["holdout_dti"]["primary_hide_and_recover"]["pooled_dti"])

    full_pred_paths = {q: wdir / f"arena9_pgrn_full_q{int(q * 100):02d}.npy" for q in QUANTILES}
    live_receipt_cache = wdir / "arena9_pgrn_live_fits.json"
    if all(p.exists() for p in full_pred_paths.values()) and live_receipt_cache.exists():
        print("[A9 full OOF] reusing deterministic full-map prediction cache", flush=True)
        full_predictions = {q: np.load(path) for q, path in full_pred_paths.items()}
        live_fit_receipts = json.loads(live_receipt_cache.read_text())
    else:
        print("[A9 full OOF] fitting q60/q70/q80 outside each buffered prediction quadrant", flush=True)
        full_predictions = {q: np.zeros(ctx.foot.shape, dtype=np.float32) for q in QUANTILES}
        live_fit_receipts = {}
        for q in range(4):
            if time.time() - started > MAX_RUNTIME_SECONDS:
                raise TimeoutError("two-hour experiment budget reached before full-map OOF completion")
            train_mask = ctx.foot & ~collars[q]
            models, receipts = _fit_quantile_models(
                base,
                extra,
                ctx.labels,
                train_mask,
                prior,
                seed=SEED + 500_000 + 10_000 * q,
            )
            target = (ctx.quad == q) & ctx.foot
            predictions = predict_models_on_mask(models, base, extra, target)
            for qq in QUANTILES:
                full_predictions[qq][target] = predictions[qq][target]
            live_fit_receipts[holdout.FOLD_NAMES[q]] = receipts
            del models, predictions
            gc.collect()
            print(f"  live fold {holdout.FOLD_NAMES[q]} complete", flush=True)
        for q, path in full_pred_paths.items():
            np.save(path, full_predictions[q])
        live_receipt_cache.write_text(json.dumps(live_fit_receipts, indent=2) + "\n")

    full_surfaces = {
        arm: _surface_for_arm(full_predictions, qset, prior, corrob_gate, ctx.foot)
        for arm, qset in ARMS.items()
    }
    selected_surface = full_surfaces[selected_arm]

    print("[A9 G4a] refreshing and checking all focus-registry surfaces before final placement", flush=True)
    manifest_path = ROOT / "registry" / "focus_registry_manifest.json"
    manifest = load_manifest(manifest_path)
    surface_audit = audit_surface(
        selected_surface,
        ctx.foot,
        manifest,
        root=ROOT,
        template_tif=ddir / "sample_submission.tif",
    )
    print(
        f"  surface registry={surface_audit['registry_rasters']} "
        f"worst |rho|={surface_audit['worst_abs_spearman']:.5f}; passed={surface_audit['passed']}",
        flush=True,
    )

    # Complete each experiment's independent SGMC falsification result after selection.
    full_masks = {}
    sgmc_results = {}
    d_full = distance_transform_edt(~ctx.labels).astype(np.float32)
    emission_logs = {}
    for arm, surface in full_surfaces.items():
        mask, elog = _emit_surface(
            surface,
            ctx.foot,
            d_full,
            budget=BUDGET,
            support_cap=SUPPORT_CAP_FULL,
        )
        full_masks[arm] = mask
        emission_logs[arm] = elog
        sg = holdout.evaluate_sgmc_with_ci(mask, ctx, n_boot=2000, seed=SEED, name=arm)
        sgmc_results[arm] = sg
        print(
            f"  {arm}: SGMC-cal HOLDOUT-DTI={sg['sgmc_prevalence_calibrated_dti']:.6f} "
            f"CI95={sg['sgmc_calibrated_ci95']}",
            flush=True,
        )

    selected_mask = full_masks[selected_arm]
    champion_file = outdir / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    champion_mask = holdout.read_binary(champion_file) & ctx.foot
    champion_sg = holdout.evaluate_sgmc_with_ci(
        champion_mask, ctx, n_boot=2000, seed=SEED, name="CHAMPION_h33-h33-2-b2"
    )

    print("[A9 G4b] literal all-registry final-dot check", flush=True)
    final_audit = audit_final_dots(
        selected_surface,
        selected_mask,
        ctx.foot,
        manifest,
        root=ROOT,
        template_tif=ddir / "sample_submission.tif",
    )
    print(
        f"  worst |rho|={final_audit['worst_abs_spearman']:.5f}; "
        f"worst 3px={final_audit['worst_within_3px_fraction']:.5f}; passed={final_audit['passed']}",
        flush=True,
    )

    selected_hr = holdout_results[selected_arm]
    selected_sg = sgmc_results[selected_arm]
    gates_pre_format = {
        "G1_leakage_canary": bool(canary["passed"]),
        "G2_holdout_beats_champion_and_repo_best": bool(
            selected_hr["pooled_dti"] > champion_hr["pooled_dti"]
            and selected_hr["pooled_dti"] > h38_best
            and paired_vs_champion["ci95"][0] > 0.0
        ),
        "G3_sgmc_beats_champion": bool(
            selected_sg["sgmc_prevalence_calibrated_dti"]
            > champion_sg["sgmc_prevalence_calibrated_dti"]
        ),
        "G4_surface_registry_unique": bool(surface_audit["passed"]),
        "G4_final_registry_unique": bool(final_audit["passed"]),
    }
    likely_verdict = "promote" if all(gates_pre_format.values()) else "negative"
    hr_short = selected_hr["pooled_dti"]
    sg_short = selected_sg["sgmc_prevalence_calibrated_dti"]
    note = (
        f"GEMS32 A9 PGRN-PU 37654d | HR {hr_short:.4f} SGMC {sg_short:.4f} | "
        + ("PROMOTE; selector required" if likely_verdict == "promote" else "research; DO-NOT-SUBMIT")
    )
    if len(note) > 140:
        raise RuntimeError(f"submission note exceeds 140 chars: {len(note)}")

    print("[A9 G5] writing through shared submission_writer and validating whole-array [0,1]", flush=True)
    timestamp_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = write_validated_submission(
        selected_mask,
        slug="arena9-pgrn-pu37654",
        timestamp_tag=timestamp_tag,
        candidate_meta={
            "candidate_id": f"A9-{selected_arm}",
            "description": "Physics-Guarded Reliable-Negative PU MDRC; fold-visible training and B=2 emission",
            "submission_note_zeros": note,
            "submission_note_nan": note,
            "catalogue_hidden_mean": selected_hr["pooled_dti"],
            "catalogue_hidden_per_quadrant": selected_hr["per_quadrant_dti"],
            "sgmc_prevalence_calibrated_dti": selected_sg["sgmc_prevalence_calibrated_dti"],
            "drift_corrected_holdout_mean": selected_hr["pooled_dti"],
            "drift_corrected_per_quadrant": selected_hr["per_quadrant_dti"],
            "predicted_leaderboard_dti": None,
            "ei_drift_corrected": None,
            "slot_decision": "SELECTOR-REQUIRED" if likely_verdict == "promote" else "HOLD-DO-NOT-SUBMIT",
        },
        ddir=ddir,
        out_dir=outdir,
    )
    zeros_path = outdir / bundle["zeros_tif"]["filename"]
    independent = validate_submission_geotiff(
        zeros_path,
        ddir / "sample_submission.tif",
        strict_whole_array_finite=True,
    )
    g5 = bool(bundle["zeros_tif"]["all_checks_passed"] and independent.passed)
    gates = gates_pre_format | {"G5_format_and_range": g5}
    verdict = "promote" if all(gates.values()) else "negative"
    if verdict != likely_verdict:
        raise RuntimeError("format gate changed verdict after submission note was frozen")

    # A promotion recommendation is not authorization to spend a weekly slot.
    ok_to_download = True
    ok_to_submit = False
    selector_required = True
    sub_name = f"GEMSDOE32-A9-PGRN-PU-{bundle['content_digest8'].upper()}"

    run_card = {
        "schema_version": "gems-parallel-runcard-v3",
        "generated_utc": generated_utc,
        "branch": "arena/70e716e8-gemsdoe32",
        "lane_id": "A9-H1-MDRC-PGRN-PU",
        "hypothesis": (
            "Blind and piedmont-concealed faults can retain concordant 1 m LiDAR scarp, magnetic-tilt, "
            "gravity/basement/MT, and hydrothermal-alteration ridges even when absent from the catalogue; "
            "protecting high-concordance unlabelled pixels from the negative class prevents PU suppression."
        ),
        "mechanism": (
            "57 leak-screened channels -> per-draw/per-fold visible-positive plus >500 m low-MDRC reliable-negative "
            "HistGB bags (q60/q70/q80) -> soft label-free physical guard -> 1-px ridge-crest sharpening -> "
            "fold-visible B=2 -> exact 300 m triangular-kernel CELF at 37,654 dots."
        ),
        "named_non_fault_mimic": (
            "Fluvial terrace risers, incised alluvial-fan channels, intact volcanic-flow margins, and "
            "unfaulted lithologic contacts."
        ),
        "experiments_used": 3,
        "experiments_budget": 3,
        "runtime_seconds": round(time.time() - started, 1),
        "weekly_slots_used": 0,
        "selected_experiment": selected_arm,
        "selection_rule": "maximum primary GEMSDOE32-HIDE-RECOVER-v3.0 pooled DTI; SGMC not used for selection",
        "experiments": {
            arm: {
                "quantiles": list(ARMS[arm]),
                "holdout_dti": _json_clean(holdout_results[arm]),
                "sgmc_holdout_dti": _json_clean(sgmc_results[arm]),
                "full_map_emitted_pixels": int(full_masks[arm].sum()),
                "emission": _json_clean(emission_logs[arm]),
            }
            for arm in ARMS
        },
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": holdout.HIDE_RECOVER_EVALUATOR_VERSION,
            "n_withheld_positives": int(selected_hr["n_withheld_positives"]),
            "selected_pooled_dti": float(selected_hr["pooled_dti"]),
            "selected_ci95": selected_hr["ci95_cluster_bootstrap"],
            "champion_02778_same_evaluator": float(champion_hr["pooled_dti"]),
            "champion_ci95": champion_hr["ci95_cluster_bootstrap"],
            "paired_delta_vs_champion": paired_vs_champion,
            "repository_best_h38_same_evaluator": h38_best,
            "beats_repository_best": bool(selected_hr["pooled_dti"] > h38_best),
        },
        "off_catalogue_holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": holdout.SGMC_EVALUATOR_VERSION,
            "n_withheld_positives": int(selected_sg["n_withheld_positives"]),
            "selected_prevalence_calibrated_dti": float(selected_sg["sgmc_prevalence_calibrated_dti"]),
            "selected_ci95": selected_sg["sgmc_calibrated_ci95"],
            "champion_prevalence_calibrated_dti": float(champion_sg["sgmc_prevalence_calibrated_dti"]),
            "champion_ci95": champion_sg["sgmc_calibrated_ci95"],
        },
        "leakage_canary": _json_clean(canary),
        "fold_local_training_receipts": fit_receipts,
        "live_oof_training_receipts": live_fit_receipts,
        "correlation_overlap_vs_registry": {
            "manifest_generated_utc": manifest.get("generated_utc"),
            "manifest_refs": manifest.get("refs"),
            "surface_before_placement": _json_clean(surface_audit),
            "final_dots": _json_clean(final_audit),
        },
        "raster_filename": zeros_path.name,
        "raster_path": str(zeros_path.relative_to(ROOT)),
        "raster_sha256": bundle["zeros_tif"]["sha256"],
        "zip_filename": bundle["zeros_zip"]["filename"],
        "zip_sha256": bundle["zeros_zip"]["sha256"],
        "nan_twin_filename": bundle["nan_tif"]["filename"],
        "validator_output": {
            "shared_writer_all_checks_passed": bool(bundle["zeros_tif"]["all_checks_passed"]),
            "independent_validator_passed": bool(independent.passed),
            "independent_validator": independent.to_dict(),
            "crs": bundle["zeros_tif"]["crs"],
            "shape": bundle["zeros_tif"]["shape"],
            "transform": bundle["zeros_tif"]["transform"],
            "dtype": bundle["zeros_tif"]["dtype"],
            "nodata": bundle["zeros_tif"]["nodata"],
            "full_grid_finite_pixels": bundle["zeros_tif"]["full_grid_finite_pixels"],
            "in_footprint_nan_count": 0,
            "min": bundle["zeros_tif"]["in_footprint_min"],
            "max": bundle["zeros_tif"]["in_footprint_max"],
            "on_catalogue_positive_pixels": bundle["zeros_tif"]["on_catalogue_positive_pixels"],
            "within_200m_visible_catalogue_pixels": int((d_full[selected_mask] <= B_VISIBLE_PX).sum()),
        },
        "automated_gates": gates,
        "submission_name": sub_name,
        "submission_note": note,
        "submission_note_length": len(note),
        "ok_to_download_for_research": ok_to_download,
        "ok_to_submit_to_live_portal": ok_to_submit,
        "selector_required": selector_required,
        "verdict": verdict,
        "decision": (
            "DOWNLOAD FOR RESEARCH / AUDIT: YES; SUBMIT TO LIVE PORTAL: NO — negative gate result"
            if verdict == "negative"
            else "DOWNLOAD: YES; DO NOT UPLOAD YET — promotion recommendation requires separate weekly-slot selector"
        ),
    }
    card_path = edir / "arena9_run_card.json"
    # Keep exactly one authoritative complete run card. Release registries are projected from it by
    # scripts/update_arena9_release.py; duplicating the 450+ KiB JSON under registry/ risks drift.
    card_path.write_text(json.dumps(_json_clean(run_card), indent=2) + "\n")

    print("\n[A9 FINAL]", flush=True)
    print(f"  artifact: {zeros_path.relative_to(ROOT)}", flush=True)
    print(f"  sha256:   {bundle['zeros_tif']['sha256']}", flush=True)
    print(f"  name:     {sub_name}", flush=True)
    print(f"  note:     {note} ({len(note)}/140)", flush=True)
    print(f"  gates:    {gates}", flush=True)
    print(f"  verdict:  {verdict.upper()} | ok_to_submit_to_live_portal={ok_to_submit}", flush=True)
    print(f"  run card: {card_path.relative_to(ROOT)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
