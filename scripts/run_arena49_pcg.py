#!/usr/bin/env python3
"""ARENA49-H1-PCG — 3-experiment holdout validation of the phase-congruency skeleton.

Lane paragraph (Protocol Rule 1, adopted in the pre-registration because the
session prompt's own method paragraph was absent — IR-ARENA49-LANE-01):
ARENA49-H1-PCG — Kovesi (1999) log-Gabor phase congruency (amplitude-invariant
Fourier phase alignment, 4 scales x 6 orientations, frequency-spread weighting)
on Band 12 det_elev and Band 13 iso_grav_anom of the official
training_features.tif, floored geometric-mean dual-field concordance,
percentile-90 support, shared 300 m CELF emitter at a 37,654-dot budget,
full-catalogue B=2 gate on the final file (visible-only per-cell gate inside
holdout scoring).  Catalogue rasters are never read during feature construction.

Pre-registration: docs/research/arena49-pc-preregistration-20261026.md
Shared tools only: gems32.holdout (evaluator), gems32.emitter (CELF),
gems32.submission (writer/audit), gems32.release_gate (promotion decision).
Does not allocate a DrivenData weekly slot.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import holdout as HO  # noqa: E402
from gems32 import pcg  # noqa: E402
from gems32 import tmspi  # noqa: E402  (shared band sanitiser only)
from gems32.emitter import emit  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir  # noqa: E402
from gems32.release_gate import REQUIRED_VALIDATOR_CHECKS, promotion_decision  # noqa: E402
from gems32.submission import audit_geotiff, write_submission_pair  # noqa: E402

LANE = "ARENA49-H1-PCG"
BUDGET = 37654
B_GATE_PX = 2.0
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
CHAMPION_TIF = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
CANARY_LIMIT = 0.90
SPEARMAN_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
N_BOOT = 1000
SEED = 49


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_band(ds, index: int, foot: np.ndarray) -> np.ndarray:
    return tmspi.sanitize_band(ds.read(index), foot)


def _load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0) & foot


def _dti_from_rows(rows: list[tuple[float, float, int]]) -> float:
    tp = sum(r[0] for r in rows)
    fp = sum(r[1] for r in rows)
    n = sum(r[2] for r in rows)
    fn = float(n) - tp
    return float(tp / (tp + 0.2 * fp + 0.8 * fn + 1e-12))


def paired_delta_ci(cand_cells: dict, champ_cells: dict, n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    keys = [k for k in cand_cells if k in champ_cells]
    a = [(float(cand_cells[k]["tp"]), float(cand_cells[k]["fp"]), int(cand_cells[k]["n_truth"])) for k in keys]
    b = [(float(champ_cells[k]["tp"]), float(champ_cells[k]["fp"]), int(champ_cells[k]["n_truth"])) for k in keys]
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot, np.float64)
    n = len(keys)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        boots[i] = _dti_from_rows([a[j] for j in idx]) - _dti_from_rows([b[j] for j in idx])
    return {
        "delta_mean": float(boots.mean()),
        "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
        "p_pos": float((boots > 0).mean()),
        "n_cells": n,
    }


def evaluate_mask(mask: np.ndarray, ctx: HO.HoldoutContext, name: str) -> dict:
    vis = HO.evaluate_visible_gated_holdout(
        mask, ctx, b_gate_px=B_GATE_PX, full_map_mask=mask, n_boot=N_BOOT, seed=20261026, name=name
    )
    hr = HO.evaluate_hide_and_recover(mask, ctx, b_visible_px=B_GATE_PX, n_boot=N_BOOT, seed=20261026, name=name)
    sg = HO.evaluate_sgmc_with_ci(mask, ctx, n_boot=N_BOOT, seed=20261026, name=name)
    return {"visible_gated": vis, "hide_and_recover": hr, "sgmc": sg}


def uniqueness_vs_registry(
    surface: np.ndarray,
    dots: np.ndarray,
    foot: np.ndarray,
    downloads: Path,
    scored_dir: Path,
) -> dict:
    """Full-footprint Spearman + directional 3-px overlap vs genuine local rasters.

    Peers: every docs/downloads/*-zeros.tif (excluding this lane's own files)
    plus every restored .cache scored raster.  The 5-px calibration lattice is
    reported separately (IR-42-UNIQ-01), never silently exempted.
    """
    from scipy.stats import rankdata

    rows = []
    genuine_overlap: list[tuple[float, str]] = []
    genuine_rho: list[float] = []
    lattice_overlap = None
    lattice_name = None
    surf_f = np.asarray(surface[foot], np.float64)
    if np.ptp(surf_f) > 0:
        rz = rankdata(surf_f, method="average").astype(np.float64)
        rz -= rz.mean()
        rz /= float(np.linalg.norm(rz))
    else:
        rz = None

    peers: list[Path] = []
    if downloads.is_dir():
        peers += sorted(downloads.glob("*-zeros.tif"))
    if scored_dir.is_dir():
        peers += sorted(scored_dir.glob("*.tif"))

    for path in peers:
        if "arena49-pcg" in path.name:
            continue
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or ds.shape != foot.shape:
                    continue
                arr = ds.read(1)
        except Exception as exc:  # noqa: BLE001 - recorded, not hidden
            rows.append({"file": path.name, "status": f"read_error:{type(exc).__name__}"})
            continue
        other_dots = np.isfinite(arr) & (arr > 0) & foot
        n_dots = int(other_dots.sum())
        rho = None
        other_s = np.nan_to_num(arr, nan=0.0)[foot].astype(np.float64)
        if rz is not None and np.ptp(other_s) > 0:
            oz = rankdata(other_s, method="average").astype(np.float64)
            oz -= oz.mean()
            nrm = float(np.linalg.norm(oz))
            if nrm > 0:
                rho = float(rz @ (oz / nrm))
        del other_s
        overlap = None
        if dots.any() and other_dots.any():
            overlap = float((distance_transform_edt(~other_dots)[dots] <= 3).mean())
        is_lattice = ("lattice" in path.name.lower()) or n_dots >= 100_000
        rows.append({
            "file": path.name,
            "source": str(path.parent.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path.parent),
            "n_dots": n_dots,
            "spearman": rho,
            "within_3px": overlap,
            "is_lattice": is_lattice,
        })
        if is_lattice:
            if overlap is not None and (lattice_overlap is None or overlap > lattice_overlap):
                lattice_overlap = overlap
                lattice_name = path.name
            continue
        if 1_000 <= n_dots <= 90_000:
            if rho is not None:
                genuine_rho.append(abs(rho))
            if overlap is not None:
                genuine_overlap.append((overlap, path.name))
    max_rho = max(genuine_rho) if genuine_rho else None
    max_ov, worst = (max(genuine_overlap) if genuine_overlap else (None, None))
    genuine_pass = (
        max_rho is not None and max_rho <= SPEARMAN_LIMIT
        and max_ov is not None and max_ov <= OVERLAP_LIMIT
    )
    return {
        "n_files": len(rows),
        "max_genuine_abs_spearman": max_rho,
        "max_genuine_3px_overlap": max_ov,
        "worst_genuine_peer": worst,
        "genuine_pass": bool(genuine_pass),
        "lattice_overlap": lattice_overlap,
        "lattice_name": lattice_name,
        "literal_lattice_pass": bool(lattice_overlap is not None and lattice_overlap <= OVERLAP_LIMIT),
        "comparisons": rows,
    }


def _strip(ev: dict) -> dict:
    vis = ev["visible_gated"]
    return {
        "visible_gated": {
            "evaluator_version": vis["evaluator_version"],
            "pooled_dti": vis["pooled_dti"],
            "ci95": vis["ci95"],
            "n_withheld_positives": vis["n_withheld_positives"],
        },
        "hide_and_recover": {
            "evaluator_version": ev["hide_and_recover"]["evaluator_version"],
            "pooled_dti": ev["hide_and_recover"]["pooled_dti"],
            "ci95_cluster_bootstrap": ev["hide_and_recover"]["ci95_cluster_bootstrap"],
            "n_withheld_positives": ev["hide_and_recover"]["n_withheld_positives"],
        },
        "sgmc": {
            "evaluator_version": ev["sgmc"]["evaluator_version"],
            "sgmc_raw_pooled_dti": ev["sgmc"]["sgmc_raw_pooled_dti"],
            "sgmc_raw_ci95": ev["sgmc"]["sgmc_raw_ci95"],
            "sgmc_prevalence_calibrated_dti": ev["sgmc"]["sgmc_prevalence_calibrated_dti"],
            "sgmc_calibrated_ci95": ev["sgmc"]["sgmc_calibrated_ci95"],
            "n_withheld_positives": ev["sgmc"]["n_withheld_positives"],
        },
    }


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    out_dir = downloads_dir()
    ev_dir = evidence_dir()
    feats = ddir / "training_features.tif"
    sample = ddir / "sample_submission.tif"
    labels_p = ddir / "labels.tif"
    for p in (feats, sample, labels_p, ddir / "external" / "derived_sgmc_faults_100m_u8.tif"):
        if not p.is_file():
            raise SystemExit(f"missing restored raster {p} — run scripts/restore_data.py first")

    print(f"[pcg] data_dir={ddir}", flush=True)
    ctx = HO.load_holdout_context(ddir)
    foot, labels = ctx.foot, ctx.labels
    print(f"[pcg] foot={int(foot.sum())} labels={int(labels.sum())} sgmc={ctx.sgmc_n_truth}", flush=True)

    with rasterio.open(feats) as ds:
        det_elev = _load_band(ds, pcg.BAND_DET_ELEV, foot)
        iso_grav = _load_band(ds, pcg.BAND_ISO_GRAV_ANOM, foot)
    print("[pcg] bands loaded (12,13); building PC fields (2 FFT filter banks)", flush=True)

    fields = pcg.build_experiment_fields(det_elev, iso_grav, foot)
    del det_elev, iso_grav
    for k in ("dem_support", "grav_support", "concordance_support"):
        print(f"[pcg] {k} nonzero={int((fields[k] > 0).sum())}", flush=True)

    canary = pcg.leakage_canary_aucs(fields, labels, foot, max_neg=200_000, seed=SEED)
    canary_max = max(canary.values())
    canary_pass = canary_max <= CANARY_LIMIT
    print(f"[pcg] canary max={canary_max:.4f} pass={canary_pass} {canary}", flush=True)
    if not canary_pass:
        (ev_dir / "arena49_pcg_run_card.json").write_text(json.dumps({
            "hypothesis_id": LANE, "verdict": "negative", "ok_to_submit": False,
            "leakage_canary": {"passed": False, "aucs": canary, "max_single_feature_auc": canary_max},
            "reason": "leakage canary failed (Rule 4); stopped before placement",
        }, indent=2) + "\n")
        print("[pcg] STOP: leakage canary failed", flush=True)
        return 2

    champ = _load_mask(CHAMPION_TIF, foot) if CHAMPION_TIF.is_file() else None
    print(f"[pcg] champion dots={int(champ.sum()) if champ is not None else 'MISSING'}", flush=True)
    d_labels = distance_transform_edt(~labels)

    experiments = [
        ("EXP1_DEM_PCG", "dem_surface", "dem_support"),
        ("EXP2_GRAV_PCG", "grav_surface", "grav_support"),
        ("EXP3_DUAL_PCG", "concordance_surface", "concordance_support"),
    ]
    results = []
    for exp_id, surf_key, sup_key in experiments:
        surface = fields[surf_key]
        support = fields[sup_key]
        n_sup = int((support > 0).sum())
        print(f"[pcg] {exp_id} emit budget={BUDGET} support={n_sup}", flush=True)
        if n_sup == 0:
            results.append({"id": exp_id, "status": "empty_support"})
            continue
        # Pre-placement surface check vs the champion (full registry check is
        # run on the primary EXP3 surface below, before its file is written).
        if champ is not None:
            from scipy.stats import spearmanr
            rho_c = float(spearmanr(surface[foot], champ[foot].astype(float)).statistic)
            print(f"[pcg] {exp_id} surface Spearman vs champion={rho_c:.4f}", flush=True)
            if abs(rho_c) > SPEARMAN_LIMIT:
                print(f"[pcg] {exp_id} logged as lane-duplicate on surface; not placed", flush=True)
                results.append({"id": exp_id, "status": "surface_duplicate_vs_champion", "champion_spearman": rho_c})
                continue
        dots, log = emit(support, budget=BUDGET, prior_dti=0.0)
        dots = dots & foot & ~labels
        n_dots = int(dots.sum())
        print(f"[pcg] {exp_id} emitted={n_dots} stopped={log.stopped_by}", flush=True)
        champ_ov = None
        if champ is not None and n_dots:
            champ_ov = float((distance_transform_edt(~champ)[dots] <= 3).mean())
            print(f"[pcg] {exp_id} 3px vs champion={champ_ov:.4f}", flush=True)
            if champ_ov > OVERLAP_LIMIT:
                print(f"[pcg] {exp_id} logged as lane-duplicate vs champion (>{OVERLAP_LIMIT})", flush=True)
        ev = evaluate_mask(dots, ctx, exp_id)
        vg = ev["visible_gated"]
        print(
            f"[pcg] {exp_id} HOLDOUT-DTI vis-gated={vg['pooled_dti']:.5f} CI={vg['ci95']} "
            f"HR={ev['hide_and_recover']['pooled_dti']:.5f} "
            f"SGMC-cal={ev['sgmc']['sgmc_prevalence_calibrated_dti']:.5f}", flush=True
        )
        results.append({
            "id": exp_id, "status": "ran", "n_support": n_sup, "n_dots": n_dots,
            "stopped_by": log.stopped_by, "surface_key": surf_key,
            "dots": dots, "surface": surface, "champion_3px": champ_ov, "eval": ev,
        })

    ran = [r for r in results if r.get("status") == "ran"]
    if not ran:
        raise SystemExit("all experiments stopped before emission")

    champ_eval = None
    if champ is not None:
        print("[pcg] scoring champion on the same evaluators", flush=True)
        champ_eval = evaluate_mask(champ, ctx, "champion_h33_b2")
        print(
            f"[pcg] champion vis-gated={champ_eval['visible_gated']['pooled_dti']:.5f} "
            f"HR={champ_eval['hide_and_recover']['pooled_dti']:.5f} "
            f"SGMC-cal={champ_eval['sgmc']['sgmc_prevalence_calibrated_dti']:.5f}", flush=True
        )

    primary = next((r for r in ran if r["id"] == "EXP3_DUAL_PCG"), ran[-1])
    raw_dots = primary["dots"]
    surface = primary["surface"]
    # Final file: full-catalogue B=2 gate applied to the emitted dots.
    final_dots = raw_dots & (d_labels > B_GATE_PX)
    print(f"[pcg] final B2 dots={int(final_dots.sum())} (raw emitted {int(raw_dots.sum())})", flush=True)

    print("[pcg] full registry uniqueness (primary surface + final dots)", flush=True)
    uniq = uniqueness_vs_registry(surface, final_dots, foot, out_dir, ddir / "scored")
    print(
        f"[pcg] genuine rho={uniq['max_genuine_abs_spearman']} 3px={uniq['max_genuine_3px_overlap']} "
        f"vs {uniq['worst_genuine_peer']} lattice={uniq['lattice_overlap']} ({uniq['lattice_name']})",
        flush=True,
    )

    vg = primary["eval"]["visible_gated"]
    hr = primary["eval"]["hide_and_recover"]
    sg = primary["eval"]["sgmc"]
    paired = None
    if champ_eval is not None:
        paired = paired_delta_ci(vg["cells"], champ_eval["visible_gated"]["cells"])
        print(f"[pcg] paired delta vs champion {paired}", flush=True)

    slug = "arena49-pcg-dualconcord-37654"
    note = (
        f"ARENA49 PCG dual-concord {int(final_dots.sum())}d B2 | "
        f"HR={hr['pooled_dti']:.4f} vis={vg['pooled_dti']:.4f} | research"
    )[:140]
    meta = {
        "candidate_id": LANE,
        "description": "ARENA49-H1-PCG dual-field phase-congruency step skeleton",
        "submission_note_zeros": note,
        "submission_note_nan": note,
        "slot_decision": "HOLD-DO-NOT-SUBMIT",
        "catalogue_hidden_mean": float(vg["pooled_dti"]),
        "catalogue_hidden_per_quadrant": {},
        "sgmc_prevalence_calibrated_dti": float(sg["sgmc_prevalence_calibrated_dti"]),
        "drift_corrected_holdout_mean": float(vg["pooled_dti"]),
        "drift_corrected_per_quadrant": {},
        "predicted_leaderboard_dti": None,
        "ei_drift_corrected": None,
    }
    print("[pcg] writing submission pair via shared writer", flush=True)
    bundle = write_submission_pair(
        mask=final_dots, foot=foot, labels=labels, template_tif=sample,
        out_dir=out_dir, slug=slug, timestamp_tag=TIMESTAMP, candidate_meta=meta,
    )
    zeros_name = bundle["zeros_tif"]["filename"]
    zeros_path = out_dir / zeros_name
    audit = audit_geotiff(zeros_path, foot, labels, mode="zeros", template_tif=sample)
    zip_path = zeros_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(zeros_path, arcname=zeros_path.name)

    validator = {
        "single_band": bool(audit["checks"]["single_band"]),
        "finite": bool(audit["checks"]["in_footprint_all_finite"] and audit["checks"]["validator_range_0_1_guaranteed"]),
        "range_0_1": bool(audit["checks"]["in_footprint_range_0_1"] and audit["checks"]["validator_range_0_1_guaranteed"]),
        "crs_match": bool(audit["checks"]["crs_epsg_32611"]),
        "shape_match": bool(audit["checks"]["dimensions_3730x3292"]),
        "transform_match": bool(audit["checks"]["exact_reference_grid_match"]),
    }
    surface_check = {
        "stage": "surface",
        "passed": bool(uniq["max_genuine_abs_spearman"] is not None and uniq["max_genuine_abs_spearman"] <= SPEARMAN_LIMIT),
    }
    final_check = {"stage": "final", "passed": bool(uniq["genuine_pass"])}
    holdout_blob = {
        "dti": float(vg["pooled_dti"]),
        "ci95": [float(vg["ci95"][0]), float(vg["ci95"][1])],
        "n_withheld_positives": int(vg["n_withheld_positives"]),
        "evaluator_version": str(vg["evaluator_version"]),
    }
    if champ_eval is not None:
        inc = {
            "dti": float(champ_eval["visible_gated"]["pooled_dti"]),
            "ci95": [float(x) for x in champ_eval["visible_gated"]["ci95"]],
            "n_withheld_positives": int(champ_eval["visible_gated"]["n_withheld_positives"]),
            "evaluator_version": str(champ_eval["visible_gated"]["evaluator_version"]),
        }
        same_eval = inc["evaluator_version"] == holdout_blob["evaluator_version"] and inc["n_withheld_positives"] == holdout_blob["n_withheld_positives"]
        paired_ci = paired["ci95"] if paired else None
    else:
        inc, same_eval, paired_ci = holdout_blob, False, None

    decision = promotion_decision(
        lane=LANE, surface_check=surface_check, final_check=final_check,
        canary_aucs=list(canary.values()), holdout=holdout_blob, incumbent=inc,
        same_evaluation=same_eval, validator=validator, paired_delta_ci95=paired_ci,
    )
    # Release verdict is stricter than the shared promotion decision: it also
    # requires the literal-lattice disposition and a separate slot selector.
    promotion_verdict = decision["verdict"]
    verdict = "promote" if (promotion_verdict == "promote" and uniq["literal_lattice_pass"]) else "negative"
    ok_to_submit = False  # selector_required; this session never spends a slot
    print(f"[pcg] promotion_decision={promotion_verdict} release_verdict={verdict} gates={decision['gates']}", flush=True)

    digest8 = zeros_name.split("-")[-2] if "-zeros.tif" in zeros_name else audit["sha256"][:8]
    submission_name = f"GEMSDOE32-ARENA49-PCG-{digest8.upper()}"
    hours = (time.time() - t0) / 3600.0

    experiments_out = []
    for r in results:
        if r.get("status") != "ran":
            experiments_out.append({k: v for k, v in r.items() if k not in {"dots", "surface"}})
            continue
        experiments_out.append({
            "id": r["id"], "n_support": r["n_support"], "n_dots": r["n_dots"],
            "stopped_by": r["stopped_by"], "champion_3px": r.get("champion_3px"),
            "eval": _strip(r["eval"]),
        })

    run_card = {
        "protocol_version": "parallel-run-v1-20261026",
        "hypothesis_id": LANE,
        "hypothesis": (
            "Kovesi (1999) log-Gabor phase-congruency step skeleton (4 scales x 6 orientations, "
            "frequency-spread weighting, amplitude-invariant) on det_elev (Band 12) and "
            "iso_grav_anom (Band 13), floored geometric-mean dual-field concordance, "
            "percentile-90 support, 37,654-dot 300 m CELF, B=2."
        ),
        "mechanism": (
            "Fault steps offset both the detrended surface and the basement density field. "
            "Phase congruency marks a step wherever Fourier components align in phase, "
            "independent of throw amplitude, so low-throw, sediment-blanketed scarps and buried "
            "basement steps rank as strongly as range-front scarps; requiring DEM+gravity "
            "concordance rejects single-domain steps."
        ),
        "named_non_fault_mimic": (
            "Pleistocene Lake Lahontan wave-cut shoreline benches (DEM-only steps) and unfaulted "
            "basin-fill density contacts (gravity-only steps); down-weighted by dual-field "
            "geometric-mean concordance."
        ),
        "lane": LANE,
        "lane_adoption_note": "IR-ARENA49-LANE-01: session prompt contained no method paragraph; Rank-1 hypothesis adopted as lane in the frozen pre-registration.",
        "preregistration": "docs/research/arena49-pc-preregistration-20261026.md",
        "holdout_dti": {
            "primary_visible_gated": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": vg["evaluator_version"],
                "n_withheld_positives": int(vg["n_withheld_positives"]),
                "pooled_dti": float(vg["pooled_dti"]),
                "ci95": [float(vg["ci95"][0]), float(vg["ci95"][1])],
                "champion_same_evaluator": None if champ_eval is None else float(champ_eval["visible_gated"]["pooled_dti"]),
                "champion_ci95": None if champ_eval is None else [float(x) for x in champ_eval["visible_gated"]["ci95"]],
                "paired_delta": paired,
                "note": "Flat-mask instrument: candidate and champion are both scored as saved masks with the per-cell visible-only B=2 gate. This is not the callable/OOF champion number (IR-45-EVAL-02) and is not a live-score projection.",
            },
            "hide_and_recover": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": hr["evaluator_version"],
                "n_withheld_positives": int(hr["n_withheld_positives"]),
                "pooled_dti": float(hr["pooled_dti"]),
                "ci95_cluster_bootstrap": [float(x) for x in hr["ci95_cluster_bootstrap"]],
                "champion_same_evaluator": None if champ_eval is None else float(champ_eval["hide_and_recover"]["pooled_dti"]),
            },
            "sgmc_off_catalogue": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": sg["evaluator_version"],
                "n_withheld_positives": int(sg["n_withheld_positives"]),
                "sgmc_raw_pooled_dti": float(sg["sgmc_raw_pooled_dti"]),
                "sgmc_prevalence_calibrated_dti": float(sg["sgmc_prevalence_calibrated_dti"]),
                "sgmc_calibrated_ci95": [float(x) for x in sg["sgmc_calibrated_ci95"]],
                "champion_same_evaluator": None if champ_eval is None else float(champ_eval["sgmc"]["sgmc_prevalence_calibrated_dti"]),
            },
        },
        "leakage_canary": {
            "n_channels_tested": len(canary),
            "aucs": canary,
            "max_single_feature_auc": canary_max,
            "threshold": CANARY_LIMIT,
            "passed": canary_pass,
        },
        "correlation_and_overlap_vs_registry": {
            "max_genuine_abs_spearman": uniq["max_genuine_abs_spearman"],
            "max_genuine_3px_dot_overlap": uniq["max_genuine_3px_overlap"],
            "worst_genuine_overlap_peer": uniq["worst_genuine_peer"],
            "genuine_final_passed": uniq["genuine_pass"],
            "lattice_overlap": uniq["lattice_overlap"],
            "lattice_name": uniq["lattice_name"],
            "literal_lattice_passed": uniq["literal_lattice_pass"],
            "literal_lattice_note": "Synthetic 5-px calibration covering grid; dense maps fail by pigeonhole (IR-42-UNIQ-01, champion/random ~0.999). Reported, not exempted.",
            "n_files_checked": uniq["n_files"],
            "comparisons": uniq["comparisons"],
        },
        "raster_filename": zeros_name,
        "raster_sha256": audit["sha256"],
        "validator_output": {
            "validated_without_human_intervention": True,
            "crs": audit["crs"],
            "shape": audit["shape"],
            "transform": audit["transform"],
            "dtype": audit["dtype"],
            "nodata": audit["nodata"],
            "positive_pixels": audit["emitted_positive_pixels"],
            "on_catalogue_pixels": audit["on_catalogue_positive_pixels"],
            "checks": audit["checks"],
            "all_checks_passed": audit["all_checks_passed"],
        },
        "submission_name": submission_name,
        "submission_note": note,
        "submission_note_length": len(note),
        "budget": {"experiments_used": len(ran), "max": 3, "hours": round(hours, 3)},
        "experiments": experiments_out,
        "verdict": verdict,
        "promotion_decision_verdict": promotion_verdict,
        "release_verdict": (
            f"{verdict} — HOLD: promotion_decision={promotion_verdict} on shared gates, but "
            "separate weekly-slot selector approval and IR-42-UNIQ-01 literal-lattice "
            "disposition are required; 0 slots used"
        ),
        "ok_to_submit": ok_to_submit,
        "decision_banner": (
            "DO NOT SUBMIT YET — HOLD for selector + lattice disposition "
            f"(promotion_decision={promotion_verdict}; release verdict {verdict})"
        ),
        "gates": decision["gates"],
        "promotion_decision": decision,
        "artifacts": {
            "primary_zeros_tif": str(zeros_path.relative_to(ROOT)),
            "primary_zeros_sha256": audit["sha256"],
            "primary_zeros_bytes": zeros_path.stat().st_size,
            "nan_companion_tif": bundle["nan_tif"]["filename"],
            "zeros_zip": zip_path.name,
            "zeros_zip_sha256": _sha256(zip_path),
            "audit_sidecar": f"gemsdoe32-{slug}-{TIMESTAMP}-{bundle['content_digest8']}-audit.json",
        },
    }
    (ev_dir / "arena49_pcg_run_card.json").write_text(json.dumps(run_card, indent=2) + "\n")
    print(json.dumps({
        "verdict": verdict, "ok_to_submit": ok_to_submit, "file": zeros_name,
        "sha256": audit["sha256"], "dots": audit["emitted_positive_pixels"],
        "holdout_vis": holdout_blob, "sgmc_cal": float(sg["sgmc_prevalence_calibrated_dti"]),
        "unique_genuine_3px": uniq["max_genuine_3px_overlap"],
        "unique_genuine_rho": uniq["max_genuine_abs_spearman"],
        "lattice": uniq["lattice_overlap"], "hours": round(hours, 3),
    }, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
