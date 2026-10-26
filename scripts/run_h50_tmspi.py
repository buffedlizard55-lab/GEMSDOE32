#!/usr/bin/env python3
"""ARENA48-H1-TMSPI — 3-experiment holdout validation of the local-wavenumber contact skeleton.

Lane paragraph (Protocol Rule 1):
ARENA48-H1-TMSPI — Unsupervised dual-field Thurston–Smith (1997) source-parameter local-wavenumber
contact skeleton: compute Miller–Singh TDR on magnetics (tmi_vg, tmi_hg) and isostatic gravity
(iso_grav_anom_vg, iso_grav_anom_slope) solely as the parent of k=|∇TDR|, retain Euler-N≈0
contacts in the 0.4–6 km SPI depth window, weight by the Wijns (2005) theta-map edge strength
(π/2 − arccos(HG/AS)), take the geometric mean of magnetic and gravity contact credibilities,
skeletonize by 3×3 morphological NMS (not Steger, not TDR zero-crossings), and pack 37,654 dots
by exact 300 m CELF. Catalogue rasters are never read during feature construction.

Does not allocate a DrivenData weekly slot. Verdict is promote only if every gate in
gems32.release_gate.promotion_decision passes.
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
from gems32 import tmspi  # noqa: E402
from gems32.emitter import emit  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir  # noqa: E402
from gems32.release_gate import REQUIRED_VALIDATOR_CHECKS, promotion_decision  # noqa: E402
from gems32.submission import audit_geotiff, write_submission_pair  # noqa: E402
from gems32.tmspi import BAND_ISO_GRAV_SLOPE, BAND_ISO_GRAV_VG, BAND_TMI_HG, BAND_TMI_VG  # noqa: E402

LANE = "ARENA48-H1-TMSPI"
BUDGET = 37654
B_GATE_PX = 2.0
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
CHAMPION_TIF = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
CANARY_LIMIT = 0.90
SPEARMAN_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
N_BOOT = 1000
SEED = 50


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


def uniqueness_vs_downloads(
    surface: np.ndarray,
    dots: np.ndarray,
    foot: np.ndarray,
    downloads: Path,
) -> dict:
    """Full-footprint Spearman + directional 3-px overlap vs every local *-zeros.tif."""
    from scipy.stats import rankdata

    rows = []
    genuine_overlap = []
    genuine_rho = []
    lattice_overlap = None
    lattice_name = None
    surf_f = np.asarray(surface[foot], np.float64)
    if np.ptp(surf_f) > 0:
        rz = rankdata(surf_f, method="average").astype(np.float64)
        rz -= rz.mean()
        rz /= float(np.linalg.norm(rz))
    else:
        rz = None
    for path in sorted(downloads.glob("*-zeros.tif")):
        if "h50-tmspi" in path.name:
            continue
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or ds.shape != foot.shape:
                    continue
                arr = ds.read(1)
        except Exception as exc:
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
        overlap = None
        if dots.any() and other_dots.any():
            overlap = float((distance_transform_edt(~other_dots)[dots] <= 3).mean())
        is_lattice = ("lattice" in path.name.lower()) or n_dots >= 100_000
        rec = {
            "file": path.name,
            "n_dots": n_dots,
            "spearman": rho,
            "within_3px": overlap,
            "is_lattice": is_lattice,
        }
        rows.append(rec)
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
        max_rho is not None
        and max_rho <= SPEARMAN_LIMIT
        and max_ov is not None
        and max_ov <= OVERLAP_LIMIT
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


def evaluate_mask(mask: np.ndarray, ctx: HO.HoldoutContext, name: str) -> dict:
    vis = HO.evaluate_visible_gated_holdout(
        mask, ctx, b_gate_px=B_GATE_PX, full_map_mask=mask, n_boot=N_BOOT, seed=SEED, name=name
    )
    hr = HO.evaluate_hide_and_recover(mask, ctx, b_visible_px=B_GATE_PX, n_boot=N_BOOT, seed=SEED, name=name)
    sg = HO.evaluate_sgmc_with_ci(mask, ctx, n_boot=N_BOOT, seed=SEED, name=name)
    return {"visible_gated": vis, "hide_and_recover": hr, "sgmc": sg}


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    out_dir = downloads_dir()
    ev_dir = evidence_dir()
    feats = ddir / "training_features.tif"
    sample = ddir / "sample_submission.tif"
    labels_p = ddir / "labels.tif"
    if not feats.is_file() or not sample.is_file() or not labels_p.is_file():
        raise SystemExit(f"missing core rasters in {ddir}")

    print(f"[h50] data_dir={ddir}")
    ctx = HO.load_holdout_context(ddir)
    foot, labels = ctx.foot, ctx.labels
    print(f"[h50] foot={int(foot.sum())} labels={int(labels.sum())} sgmc={ctx.sgmc_n_truth}")

    with rasterio.open(feats) as ds:
        tmi_hg = _load_band(ds, BAND_TMI_HG, foot)
        tmi_vg = _load_band(ds, BAND_TMI_VG, foot)
        grav_hg = _load_band(ds, BAND_ISO_GRAV_SLOPE, foot)
        grav_vg = _load_band(ds, BAND_ISO_GRAV_VG, foot)
    print("[h50] bands loaded (3,5,9,11); building TM-SPI fields")

    fields = tmspi.build_experiment_fields(tmi_hg, tmi_vg, grav_hg, grav_vg, foot)
    for k in ("mag_support", "grav_support", "concordance_support"):
        print(f"[h50] {k} nonzero={int((fields[k] > 0).sum())}")

    # Rule 4 canary against withheld-style catalogue pixels (public labels). AUC>0.90 = leakage.
    canary = tmspi.leakage_canary_aucs(fields, labels, foot, max_neg=200_000, seed=SEED)
    canary_max = max(canary.values())
    canary_pass = canary_max <= CANARY_LIMIT
    print(f"[h50] canary max={canary_max:.4f} pass={canary_pass} {canary}")
    if not canary_pass:
        print("[h50] STOP: leakage canary failed")
        (ev_dir / "h50_tmspi_run_card.json").write_text(json.dumps({
            "hypothesis_id": LANE, "verdict": "negative", "ok_to_submit": False,
            "leakage_canary": {"passed": False, "aucs": canary, "max": canary_max},
        }, indent=2) + "\n")
        return 2

    champ = _load_mask(CHAMPION_TIF, foot) if CHAMPION_TIF.is_file() else None
    print(f"[h50] champion dots={int(champ.sum()) if champ is not None else 'MISSING'}")

    experiments = [
        ("EXP1_MAG_TMSPI", "mag_surface", "mag_support"),
        ("EXP2_GRAV_TMSPI", "grav_surface", "grav_support"),
        ("EXP3_DUAL_CONCORDANCE", "concordance_surface", "concordance_support"),
    ]
    results = []
    for exp_id, surf_key, sup_key in experiments:
        surface = fields[surf_key]
        support = fields[sup_key]
        n_sup = int((support > 0).sum())
        print(f"[h50] {exp_id} emit budget={BUDGET} support={n_sup}")
        if n_sup == 0:
            results.append({"id": exp_id, "status": "empty_support"})
            continue
        dots, log = emit(support, budget=BUDGET, prior_dti=0.0)
        dots = dots & foot & ~labels
        n_dots = int(dots.sum())
        print(f"[h50] {exp_id} emitted={n_dots} stopped={log.stopped_by}")
        champ_ov = None
        if champ is not None and n_dots:
            champ_ov = float((distance_transform_edt(~champ)[dots] <= 3).mean())
            print(f"[h50] {exp_id} 3px vs champion={champ_ov:.4f}")
            if champ_ov > OVERLAP_LIMIT:
                print(f"[h50] {exp_id} logged as lane-duplicate vs champion (>{OVERLAP_LIMIT})")
        print(f"[h50] {exp_id} holdout…")
        ev = evaluate_mask(dots, ctx, exp_id)
        vg = ev["visible_gated"]
        print(
            f"[h50] {exp_id} HOLDOUT-DTI vis-gated={vg['pooled_dti']:.5f} "
            f"CI={vg['ci95']} HR={ev['hide_and_recover']['pooled_dti']:.5f} "
            f"SGMC-cal={ev['sgmc']['sgmc_prevalence_calibrated_dti']:.5f}"
        )
        results.append({
            "id": exp_id,
            "status": "ran",
            "n_support": n_sup,
            "n_dots": n_dots,
            "stopped_by": log.stopped_by,
            "surface_key": surf_key,
            "dots": dots,
            "surface": surface,
            "champion_3px": champ_ov,
            "eval": ev,
        })

    ran = [r for r in results if r.get("status") == "ran"]
    if not ran:
        raise SystemExit("all experiments stopped before emission")

    champ_eval = None
    if champ is not None:
        print("[h50] scoring champion on the same evaluators")
        champ_eval = evaluate_mask(champ, ctx, "champion_h33_b2")
        print(
            f"[h50] champion vis-gated={champ_eval['visible_gated']['pooled_dti']:.5f} "
            f"HR={champ_eval['hide_and_recover']['pooled_dti']:.5f} "
            f"SGMC-cal={champ_eval['sgmc']['sgmc_prevalence_calibrated_dti']:.5f}"
        )

    # Selected lane candidate is EXP3 (dual concordance). Fall back to best vis-gated if EXP3 missing.
    primary = next((r for r in ran if r["id"] == "EXP3_DUAL_CONCORDANCE"), ran[-1])
    dots = primary["dots"]
    surface = primary["surface"]
    vg = primary["eval"]["visible_gated"]
    hr = primary["eval"]["hide_and_recover"]
    sg = primary["eval"]["sgmc"]
    print("[h50] full local-registry uniqueness (surface + final dots)")
    uniq = uniqueness_vs_downloads(surface, dots, foot, out_dir)
    print(
        f"[h50] genuine rho={uniq['max_genuine_abs_spearman']} "
        f"3px={uniq['max_genuine_3px_overlap']} vs {uniq['worst_genuine_peer']} "
        f"lattice={uniq['lattice_overlap']}"
    )
    if uniq["max_genuine_abs_spearman"] is not None and uniq["max_genuine_abs_spearman"] > SPEARMAN_LIMIT:
        print("[h50] STOP: surface Spearman > 0.90 — lane duplicate")
    if uniq["max_genuine_3px_overlap"] is not None and uniq["max_genuine_3px_overlap"] > OVERLAP_LIMIT:
        print(f"[h50] logged as lane-duplicate vs {uniq['worst_genuine_peer']}")

    paired = None
    if champ_eval is not None:
        paired = paired_delta_ci(vg["cells"], champ_eval["visible_gated"]["cells"])
        print(f"[h50] paired Δ vs champion {paired}")

    slug = "h50-tmspi-dualconcord-37654"
    note = (
        f"H50 TM-SPI dual-concord {primary['n_dots']}d B2 | "
        f"HR={hr['pooled_dti']:.4f} vis={vg['pooled_dti']:.4f} | research"
    )[:140]
    meta = {
        "candidate_id": LANE,
        "description": "ARENA48-H1-TMSPI dual-field local-wavenumber contact skeleton",
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
    print("[h50] writing submission pair")
    bundle = write_submission_pair(
        mask=dots,
        foot=foot,
        labels=labels,
        template_tif=sample,
        out_dir=out_dir,
        slug=slug,
        timestamp_tag=TIMESTAMP,
        candidate_meta=meta,
    )
    zeros_name = bundle["zeros_tif"]["filename"]
    zeros_path = out_dir / zeros_name
    audit = audit_geotiff(zeros_path, foot, labels, mode="zeros", template_tif=sample)
    zip_path = zeros_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(zeros_path, arcname=zeros_path.name)

    validator = {
        "single_band": True,
        "finite": True,
        "range_0_1": True,
        "crs_match": True,
        "shape_match": True,
        "transform_match": True,
    }
    validator.update({k: bool(v) for k, v in audit["checks"].items() if k in REQUIRED_VALIDATOR_CHECKS})
    # Map audit checks onto the required names.
    validator["single_band"] = bool(audit["checks"]["single_band"])
    validator["finite"] = bool(audit["checks"]["in_footprint_all_finite"] and audit["checks"]["validator_range_0_1_guaranteed"])
    validator["range_0_1"] = bool(audit["checks"]["in_footprint_range_0_1"] and audit["checks"]["validator_range_0_1_guaranteed"])
    validator["crs_match"] = bool(audit["checks"]["crs_epsg_32611"])
    validator["shape_match"] = bool(audit["checks"]["dimensions_3730x3292"])
    validator["transform_match"] = bool(audit["checks"]["exact_reference_grid_match"])

    surface_check = {
        "stage": "surface",
        "passed": bool(
            uniq["max_genuine_abs_spearman"] is not None
            and uniq["max_genuine_abs_spearman"] <= SPEARMAN_LIMIT
        ),
    }
    final_check = {
        "stage": "final",
        "passed": bool(uniq["genuine_pass"] and uniq["literal_lattice_pass"]),
    }
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
        inc = holdout_blob
        same_eval = False
        paired_ci = None

    decision = promotion_decision(
        lane=LANE,
        surface_check=surface_check,
        final_check=final_check,
        canary_aucs=list(canary.values()),
        holdout=holdout_blob,
        incumbent=inc,
        same_evaluation=same_eval,
        validator=validator,
        paired_delta_ci95=paired_ci,
    )
    verdict = decision["verdict"]
    ok_to_submit = False  # selector_required; never self-promote a weekly slot
    print(f"[h50] promotion_decision={verdict} gates={decision['gates']}")

    digest8 = zeros_name.split("-")[-2] if "-zeros.tif" in zeros_name else audit["sha256"][:8]
    submission_name = f"GEMSDOE32-H50-TMSPI-{digest8.upper()}"
    hours = (time.time() - t0) / 3600.0

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

    experiments_out = []
    for r in results:
        if r.get("status") != "ran":
            experiments_out.append({k: v for k, v in r.items() if k not in {"dots", "surface"}})
            continue
        experiments_out.append({
            "id": r["id"],
            "n_support": r["n_support"],
            "n_dots": r["n_dots"],
            "stopped_by": r["stopped_by"],
            "champion_3px": r.get("champion_3px"),
            "eval": _strip(r["eval"]),
        })

    run_card = {
        "protocol_version": "parallel-run-v1-20261026",
        "hypothesis_id": LANE,
        "hypothesis": (
            "Unsupervised dual-field Thurston–Smith local-wavenumber (SPI) contact skeleton "
            "weighted by the Wijns (2005) theta-map edge strength and geometrically concordant "
            "across magnetics (tmi_hg, tmi_vg) and isostatic gravity (iso_grav_anom_slope, "
            "iso_grav_anom_vg), morphological-NMS 1-px crests, 37,654-dot 300 m CELF, B=2."
        ),
        "mechanism": (
            "Buried sub-vertical basement contacts retain amplitude-independent theta-map peaks "
            "and Euler-N≈0 local-wavenumber depths of 0.4–6 km even where Quaternary scarps are "
            "absent; requiring magnetic∩gravity concordance rejects single-domain lithologic edges."
        ),
        "named_non_fault_mimic": (
            "Unfaulted pluton walls and tabular basalt flow margins (magnetic-only) and unfaulted "
            "basin-fill density contrasts (gravity-only); rejected by dual-field geometric-mean concordance."
        ),
        "lane": LANE,
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
            },
            "hide_and_recover": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": hr["evaluator_version"],
                "n_withheld_positives": int(hr["n_withheld_positives"]),
                "pooled_dti": float(hr["pooled_dti"]),
                "ci95_cluster_bootstrap": [float(x) for x in hr["ci95_cluster_bootstrap"]],
            },
            "sgmc_off_catalogue": {
                "label": "HOLDOUT-DTI",
                "evaluator_version": sg["evaluator_version"],
                "n_withheld_positives": int(sg["n_withheld_positives"]),
                "sgmc_raw_pooled_dti": float(sg["sgmc_raw_pooled_dti"]),
                "sgmc_prevalence_calibrated_dti": float(sg["sgmc_prevalence_calibrated_dti"]),
                "sgmc_calibrated_ci95": [float(x) for x in sg["sgmc_calibrated_ci95"]],
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
            "n_files_checked": uniq["n_files"],
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
        "budget": {
            "experiments_used": len(ran),
            "max": 3,
            "hours": round(hours, 3),
        },
        "experiments": experiments_out,
        "verdict": verdict,
        "ok_to_submit": ok_to_submit,
        "decision_banner": (
            "DO NOT SUBMIT — audit/research artifact"
            if verdict != "promote"
            else "HOLD — selector required; no weekly slot spent"
        ),
        "gates": decision["gates"],
        "promotion_decision": decision,
        "artifacts": {
            "primary_zeros_tif": str(zeros_path.relative_to(ROOT)),
            "primary_zeros_sha256": audit["sha256"],
            "primary_zeros_bytes": zeros_path.stat().st_size,
            "nan_companion_tif": bundle["nan_tif"]["filename"],
            "zip_archive": str(zip_path.relative_to(ROOT)),
            "audit_json": str((out_dir / zeros_name.replace("-zeros.tif", "-audit.json")).relative_to(ROOT))
            if False else None,
            "emitted_dots": int(dots.sum()),
            "on_catalogue_dots": int((dots & labels).sum()),
        },
    }
    card_path = ev_dir / "h50_tmspi_run_card.json"
    card_path.write_text(json.dumps(run_card, indent=2) + "\n")
    audit_sidecar = out_dir / zeros_name.replace("-zeros.tif", "-audit.json")
    audit_sidecar.write_text(json.dumps({"run_card": str(card_path), "audit": audit, "bundle": {
        k: ({kk: vv for kk, vv in val.items() if kk != "array"} if isinstance(val, dict) else val)
        for k, val in bundle.items()
    }}, indent=2, default=str) + "\n")
    run_card["artifacts"]["audit_json"] = str(audit_sidecar.relative_to(ROOT))
    card_path.write_text(json.dumps(run_card, indent=2) + "\n")
    print(f"[h50] wrote {zeros_path.name} sha256={audit['sha256'][:16]}… verdict={verdict} hours={hours:.2f}")
    print(json.dumps({k: run_card[k] for k in ("verdict", "ok_to_submit", "raster_filename", "raster_sha256", "submission_name", "submission_note")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
