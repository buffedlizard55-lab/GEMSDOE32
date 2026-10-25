#!/usr/bin/env python3
"""Round-5 experiment 2 — H-SUP-SGMC (frozen addendum: docs/research/hypotheses-round5.md §2c).

Identical pipeline to H-CVF2 (`scripts/run_hcvf2.py`) except supervision: positives are the
catalogue UNION SGMC-off-catalogue pixels from the NORTH quadrants (NW, NE) only.  The south
quadrants' SGMC pixels are never shown to any fold; the primary gate (a') is the exact pooled
DTI against south-only SGMC-off-catalogue truth, candidate vs champion at matched mass
(37,654), with a paired component-bootstrap CI of the difference (FP held at its full-truth
value, so the CI is a lower bound on width).  Full-map SGMC (train-contaminated here) and
catalogue-hidden (perverse for B-gated candidates, §2b) are reported, never gated on.

Outputs: field/mask under .cache/gems_work/, the submission pair under docs/downloads/,
receipt at evidence/hsupsgmc_run.json.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.ndimage import binary_dilation, distance_transform_edt, label as cc_label
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import detector, emitter, holdout, submission  # noqa: E402
from gems32.metric import ALPHA, BETA, dti_binary, kernel  # noqa: E402

G = Path(os.environ.get("GEMS_DATA_DIR", ROOT / ".cache" / "gems_data"))
WORK = ROOT / ".cache" / "gems_work"
STACK_PATH = WORK / "feature_stack.npy"
FIELD_PATH = WORK / "hsupsgmc_field.npy"
BUDGET, B_GATE_PX, SUPPORT_CAP, SEED = 37_654, 2, 500_000, 20261025
NORTH, SOUTH = (0, 1), (2, 3)
N_BOOT = 400

REGISTRY_RASTERS = {
    "CHAMPION_h33-2-b2_0.2778": ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "ANDERSON36_0.2750": G / "scored/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
    "SOLO28_h27-4_0.2708": G / "scored/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif",
    "RUNG30_h36-1_0.2710": G / "scored/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif",
    "EULER28_h38-1_0.2707": G / "scored/gems28-h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-allfinite.tif",
    "H33D33_0.2632": G / "scored/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "D28_d2-8_0.2600": G / "scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
    "D15_0.2477": G / "scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "TGC27_0.2449": G / "scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "H19-5_0.1922": G / "scored/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
    "H32D_slotplan_unscored": ROOT / "docs/downloads/gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-zeros.tif",
    "PROBE_S1_anchor02600": ROOT / "docs/downloads/gems32-probe-S1-ANCHOR-identical-to-live-02600.tif",
    "LAZYGREEDY_44090_unscored": ROOT / "docs/downloads/gems32-lazygreedy-maxcov-44090-supconfined-zeros.tif",
    "H-CVF2_round5_exp1": ROOT / "docs/downloads/gemsdoe32-hcvf2-cvgbm35-b2-greedy37654-20261025T202730Z-f9b36c7e-zeros.tif",
}


def load_mask(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0)


def density_surface(mask: np.ndarray) -> np.ndarray:
    yy, xx = np.mgrid[-3:4, -3:4]
    k = np.maximum(1.0 - np.hypot(yy, xx) / 3.0, 0.0).astype(np.float32)
    return ndimage.convolve(mask.astype(np.float32), k, mode="constant")


def south_sgmc_eval(mask: np.ndarray, truth: np.ndarray, domain: np.ndarray,
                    comp: np.ndarray, n_comp: int, rng: np.random.Generator,
                    boot_idx: np.ndarray) -> dict:
    """Exact south-SGMC DTI + paired-bootstrap-ready per-rep DTIs (FP fixed at full-truth value)."""
    exact = dti_binary(mask, truth, valid=domain, known=None)
    active_pred = mask & domain
    dp = distance_transform_edt(~active_pred)
    t_yx = np.nonzero(truth & domain)
    credit_px = kernel(dp[t_yx])                      # per-truth-pixel credit under this mask
    comp_at_truth = comp[t_yx]
    size_c = np.bincount(comp_at_truth, minlength=n_comp + 1).astype(np.float64)
    tp_c = np.bincount(comp_at_truth, weights=credit_px, minlength=n_comp + 1)
    reps = []
    for chosen in boot_idx:                            # chosen: component ids, with repetition
        mult = np.bincount(chosen, minlength=n_comp + 1).astype(np.float64)
        tp = float(mult @ tp_c); n = float(mult @ size_c)
        reps.append(tp / (tp + ALPHA * exact["fp"] + BETA * (n - tp) + 1e-12))
    return {"dti": exact["dti"], "tp": exact["tp"], "fp": exact["fp"], "fn": exact["fn"],
            "n_truth": exact["n_truth"], "coverage": exact["coverage"],
            "boot_dtis": reps}


def main() -> int:
    t0 = time.time()
    receipt: dict = {"experiment": "H-SUP-SGMC (round-5 experiment 2 of <=3)",
                     "preregistration": "docs/research/hypotheses-round5.md §2c",
                     "started_utc": datetime.now(timezone.utc).isoformat(),
                     "budget_px": BUDGET, "b_gate_px": B_GATE_PX, "support_cap_px": SUPPORT_CAP,
                     "leakage_canary": "reused from experiment 1 (identical 35 channels; worst AUC 0.6217 <= 0.90) — evidence/hcvf2_run.json"}
    print("[1/7] loading stack/labels/footprint/quadrants/SGMC", flush=True)
    stack = np.lib.format.open_memmap(STACK_PATH, mode="r")
    labels = load_mask(G / "labels.tif")
    with rasterio.open(G / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(G / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgm = ds.read(1) > 0
    quad = holdout.quadrant_ids(foot)
    near = binary_dilation(labels, iterations=holdout.NEAR_LABEL_PX)
    sgmc_off = sgm & ~labels & ~near & foot
    north = np.isin(quad, NORTH)
    pos_aug = labels | (sgmc_off & north)
    receipt["supervision"] = {"catalogue_px": int(labels.sum()),
                              "sgmc_off_px_total": int(sgmc_off.sum()),
                              "sgmc_off_north_px_used_as_positives": int((sgmc_off & north).sum()),
                              "sgmc_off_south_px_held_out_for_validation": int((sgmc_off & ~north & np.isin(quad, SOUTH)).sum()),
                              "augmented_positive_px": int(pos_aug.sum())}
    d_cat = distance_transform_edt(~labels)

    print("[2/7] 4-quadrant spatial-CV GBM with SGMC-north-augmented positives", flush=True)
    spec = detector.DetectorSpec()
    receipt["detector_spec"] = spec.as_dict()
    field = np.zeros(labels.shape, dtype=np.float32)
    fold_rows = {}
    for q in range(4):
        collar = binary_dilation(quad == q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX)
        train_mask = foot & ~collar
        frng = np.random.default_rng(SEED + 100 + q)
        X, y = detector.sample_training_rows(stack, pos_aug, train_mask, spec, frng)
        det = detector.Detector(spec).fit(X, y)
        rows = np.flatnonzero((quad == q).any(axis=1))
        pred_q = np.zeros(labels.shape, dtype=np.float32)
        for y0 in range(int(rows[0]), int(rows[-1]) + 1, 200):
            y1 = min(y0 + 200, int(rows[-1]) + 1)
            pred_q[y0:y1] = det.predict_field(stack, y0, y1)
        field[quad == q] = pred_q[quad == q]
        fold_rows[f"quadrant_{q}"] = {"train_pos_sampled": int((y == 1).sum()),
                                      "train_neg_sampled": int((y == 0).sum())}
        print(f"    fold {q}: {int((y==1).sum()):,} pos / {int((y==0).sum()):,} neg", flush=True)
        del X, y, det, pred_q
    receipt["cv_folds"] = fold_rows
    field[~foot] = 0.0
    np.save(FIELD_PATH, field)
    receipt["field"] = {"path": str(FIELD_PATH), "min": float(field.min()), "max": float(field.max()),
                        "mean_in_footprint": float(field[foot].mean()),
                        "sha256_npy": hashlib.sha256(FIELD_PATH.read_bytes()).hexdigest()}

    print("[3/7] emission (identical law to experiment 1)", flush=True)
    gated = field.copy()
    gated[d_cat <= B_GATE_PX] = 0.0
    gated[~foot] = 0.0
    flat_g = gated.ravel()
    if int((flat_g > 0).sum()) > SUPPORT_CAP:
        thr = np.partition(flat_g, flat_g.size - SUPPORT_CAP)[flat_g.size - SUPPORT_CAP]
        gated = np.where(gated >= thr, gated, 0.0).astype(np.float32)
    receipt["support_px_after_gates"] = int((gated > 0).sum())
    mask, elog = emitter.emit(gated, budget=BUDGET, prior_dti=0.0)
    receipt["emission"] = elog.as_dict()
    receipt["emitted_px"] = int(mask.sum())
    receipt["emitted_on_catalogue_px"] = int((mask & labels).sum())
    receipt["emitted_within_2px_of_catalogue"] = int((d_cat[mask] <= 2).sum())
    del gated

    print("[4/7] PRIMARY GATE (a'): south-only SGMC exact DTI + paired component bootstrap", flush=True)
    south_domain = np.isin(quad, SOUTH) & foot & ~labels
    south_truth = sgmc_off & south_domain
    comp, n_comp = cc_label(south_truth, structure=np.ones((3, 3), int))
    rng = np.random.default_rng(SEED + 7)
    boot_idx = rng.integers(1, n_comp + 1, size=(N_BOOT, n_comp))
    comparators = {
        "H-SUP-SGMC": mask,
        "CHAMPION_h33-2-b2": load_mask(REGISTRY_RASTERS["CHAMPION_h33-2-b2_0.2778"]),
        "H-CVF2_exp1": load_mask(REGISTRY_RASTERS["H-CVF2_round5_exp1"]),
        "SOLO28_h27-4": load_mask(REGISTRY_RASTERS["SOLO28_h27-4_0.2708"]),
        "D28_d2-8": load_mask(REGISTRY_RASTERS["D28_d2-8_0.2600"]),
    }
    south = {}
    for nm, m in comparators.items():
        r = south_sgmc_eval(m, south_truth, south_domain, comp, n_comp, rng, boot_idx)
        south[nm] = r
        dots_south = int((m & south_domain).sum())
        print(f"    {nm:18s} south_dots={dots_south:>6,} south_SGMC_DTI={r['dti']:.5f} coverage={r['coverage']:.4f} (n_truth={r['n_truth']:,})", flush=True)
    diffs = np.array(south["H-SUP-SGMC"]["boot_dtis"]) - np.array(south["CHAMPION_h33-2-b2"]["boot_dtis"])
    receipt["south_sgmc_gate"] = {
        "domain": "quadrants SW+SE, footprint, off-catalogue; truth = SGMC pixels >300m from catalogue",
        "n_truth_px": int(south["H-SUP-SGMC"]["n_truth"]), "n_truth_components": int(n_comp),
        "per_candidate": {k: {kk: (float(vv) if isinstance(vv, float) else vv)
                               for kk, vv in v.items() if kk != "boot_dtis"} for k, v in south.items()},
        "paired_diff_candidate_minus_champion": {
            "point": float(south["H-SUP-SGMC"]["dti"] - south["CHAMPION_h33-2-b2"]["dti"]),
            "boot_ci95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))],
            "frac_reps_positive": float((diffs > 0).mean()), "n_boot": N_BOOT,
            "ci_caveat": "component bootstrap over truth; FP held at full-truth value (CI is a lower bound on width)"},
    }
    gate_a = bool(south["H-SUP-SGMC"]["dti"] > south["CHAMPION_h33-2-b2"]["dti"])
    receipt["gate_a_prime_south_sgmc_beats_champion"] = gate_a

    print("[5/7] full holdout table for the record (labelled, not gated on)", flush=True)
    ctx = holdout.load_holdout_context(G)
    table = {}
    for nm, m in comparators.items():
        r = holdout.evaluate_candidate_holdout(m, ctx, name=nm)
        table[nm] = {k: r[k] for k in ("emitted_pixels", "on_catalogue_pixels", "catalogue_hidden_mean",
                                       "sgmc_prevalence_calibrated_dti", "sgmc_off_catalogue_raw_dti",
                                       "sgmc_off_catalogue_coverage", "drift_corrected_holdout_mean")}
        print(f"    {nm:18s} cat(perverse)={r['catalogue_hidden_mean']:.5f} sgmc_full={r['sgmc_prevalence_calibrated_dti']:.5f} drift={r['drift_corrected_holdout_mean']:.5f}", flush=True)
    receipt["holdout_for_the_record"] = table
    receipt["holdout_labels"] = {
        "catalogue_hidden_mean": "PERVERSE for B-gated candidates (hypotheses-round5.md §2b); not a gate",
        "sgmc_prevalence_calibrated_dti": "TRAIN-CONTAMINATED for H-SUP-SGMC on north quadrants; not a gate"}

    print("[6/7] lane uniqueness vs registry rasters", flush=True)
    dens_cand = density_surface(mask)
    uniq, worst_rho, worst_frac = {}, 0.0, 0.0
    for nm, path in REGISTRY_RASTERS.items():
        rm = load_mask(path)
        dt_r = distance_transform_edt(~rm)
        frac3 = float((dt_r[mask] <= 3).mean())
        dens_r = density_surface(rm)
        rho_dots = float(spearmanr(dens_cand[foot], dens_r[foot]).statistic)
        rho_field = float(spearmanr(field[foot], dens_r[foot]).statistic)
        uniq[nm] = {"frac_my_dots_within_3px": frac3, "spearman_density_final_dots": rho_dots,
                    "spearman_density_belief_field": rho_field, "registry_dots": int(rm.sum())}
        worst_rho = max(worst_rho, abs(rho_dots), abs(rho_field)); worst_frac = max(worst_frac, frac3)
        print(f"    vs {nm:28s} within3px={frac3:.4f} rho_dots={rho_dots:+.4f} rho_field={rho_field:+.4f}", flush=True)
        del rm, dt_r, dens_r
    receipt["uniqueness"] = {"per_raster": uniq, "worst_abs_spearman": worst_rho,
                             "worst_frac_within_3px": worst_frac,
                             "thresholds": {"spearman_max": 0.90, "frac_within_3px_max": 0.70}}
    gate_b = bool(worst_rho <= 0.90 and worst_frac <= 0.70)
    receipt["gate_b_prime_lane_uniqueness"] = gate_b

    print("[7/7] writing submission pair (12-point audit fail-closed)", flush=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slot = "PROMOTE-CANDIDATE" if (gate_a and gate_b) else "DO-NOT-SUBMIT"
    full = holdout.evaluate_candidate_holdout(mask, ctx, name="H-SUP-SGMC")
    meta = {
        "candidate_id": "H-SUP-SGMC",
        "description": ("Round-5 experiment 2: 4-quadrant spatial-CV HistGB over the 35-channel stack with "
                        "SGMC-north-augmented supervision; B=2 catalogue gate; lazy-greedy 300m-kernel "
                        "max-coverage at 37,654 dots. Primary validation = held-out SOUTH SGMC DTI "
                        "(see evidence/hsupsgmc_run.json). No organizer score exists."),
        "submission_note_zeros": ("GEMSDOE32 H-SUP-SGMC | CV-GBM+SGMCsup B=2 greedy {dots} dots; "
                                  "south-SGMC holdout gate in evidence; UNSCORED {slot}"),
        "submission_note_nan": ("GEMSDOE32 H-SUP-SGMC (nan twin) | CV-GBM+SGMCsup B=2 greedy {dots} dots; "
                                "south-SGMC holdout gate in evidence; UNSCORED {slot}"),
        "catalogue_hidden_mean": full["catalogue_hidden_mean"],
        "catalogue_hidden_per_quadrant": full["catalogue_hidden_per_quadrant"],
        "sgmc_prevalence_calibrated_dti": full["sgmc_prevalence_calibrated_dti"],
        "drift_corrected_holdout_mean": full["drift_corrected_holdout_mean"],
        "drift_corrected_per_quadrant": full["drift_corrected_per_quadrant"],
        "predicted_leaderboard_dti": None,
        "ei_drift_corrected": None,
        "slot_decision": slot,
    }
    bundle = submission.write_submission_pair(
        mask, foot, labels, G / "sample_submission.tif", ROOT / "docs" / "downloads",
        slug="hsupsgmc-cvgbm35-b2-greedy37654", timestamp_tag=ts, candidate_meta=meta)
    receipt["submission_bundle"] = bundle
    receipt["gate_c_prime_portal_audit_12pt"] = bool(bundle["zeros_tif"]["all_checks_passed"]
                                                      and bundle["nan_tif"]["all_checks_passed"])
    receipt["submission_note"] = bundle["submission_note_zeros"]
    receipt["submission_note_chars"] = len(bundle["submission_note_zeros"])
    receipt["verdict"] = "promote" if (gate_a and gate_b and receipt["gate_c_prime_portal_audit_12pt"]) else "negative"
    receipt["verdict_reason"] = (f"gate_a'(south-SGMC>champion)={gate_a} "
                                 f"[cand {south['H-SUP-SGMC']['dti']:.5f} vs champ {south['CHAMPION_h33-2-b2']['dti']:.5f}], "
                                 f"gate_b'(uniqueness)={gate_b}, gate_c'(audit)={receipt['gate_c_prime_portal_audit_12pt']}")
    receipt["seconds_total"] = round(time.time() - t0, 1)
    (ROOT / "evidence" / "hsupsgmc_run.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps({"verdict": receipt["verdict"], "reason": receipt["verdict_reason"],
                      "zeros_tif": bundle["zeros_tif"]["filename"], "sha256": bundle["zeros_tif"]["sha256"],
                      "note": bundle["submission_note_zeros"], "note_chars": len(bundle["submission_note_zeros"])}, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
