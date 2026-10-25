#!/usr/bin/env python3
"""Round-5 experiment 1 — H-CVF2 (see docs/research/hypotheses-round5.md, frozen before build).

Lane: spatially-CV 35-channel GBM belief field (`gems32.features` + `gems32.detector`),
emitted under the champion's proven emission law: B=2 catalogue gate, exact lazy-greedy
300 m-kernel maximum-coverage (`gems32.emitter.emit`), exactly 37,654 dots (the champion's
mass).  Validated against the frozen gates:

  (a) HOLDOUT-DTI vs the champion at matched mass on catalogue_hidden AND SGMC instruments
      (`gems32.holdout.evaluate_candidate_holdout`, draws 20/21), pooled DTI + 95 % CI;
  (b) lane uniqueness: Spearman <= 0.90 (density surfaces) and <= 70 % dots within 3 px
      vs every registry raster, checked on the field surface and on the final dots;
  (c) portal validity: the 12-point audit inside `gems32.submission.write_submission_pair`
      (raises on failure) — the independent `scripts/check_submission.py` is run afterwards.

A leakage canary (per-channel AUC > 0.90 stops the build) runs before any training.
Outputs: belief field + emission mask under .cache/gems_work/, the submission pair under
docs/downloads/, and the full receipt at evidence/hcvf2_run.json.
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
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import detector, emitter, features, holdout, submission  # noqa: E402
from gems32.metric import ALPHA, BETA  # noqa: E402

G = Path(os.environ.get("GEMS_DATA_DIR", ROOT / ".cache" / "gems_data"))
WORK = ROOT / ".cache" / "gems_work"
STACK_PATH = WORK / "feature_stack.npy"
FIELD_PATH = WORK / "hcvf2_field.npy"
BUDGET = 37_654            # the champion's exact emitted mass (matched comparison)
B_GATE_PX = 2              # B=2: zero field within 200 m of the catalogue
SUPPORT_CAP = 500_000      # emitter support = top field pixels (13x budget)
AUC_CANARY = 0.90
SEED = 20261025

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
}


def load_mask(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0)


def density_surface(mask: np.ndarray) -> np.ndarray:
    """300 m triangular-kernel dot-density surface of a binary mask (float32)."""
    yy, xx = np.mgrid[-3:4, -3:4]
    k = np.maximum(1.0 - np.hypot(yy, xx) / 3.0, 0.0).astype(np.float32)
    return ndimage.convolve(mask.astype(np.float32), k, mode="constant")


def pooled_dti_ci(folds: dict, n_boot: int = 2000, seed: int = SEED) -> dict:
    cells = [(v["tp"], v["fp"], v["n_truth"]) for v in folds.values()]
    def pooled(cs):
        tp = sum(c[0] for c in cs); fp = sum(c[1] for c in cs); n = sum(c[2] for c in cs)
        return tp / (tp + ALPHA * fp + BETA * (n - tp) + 1e-12)
    rng = np.random.default_rng(seed)
    boots = [pooled([cells[i] for i in rng.integers(0, len(cells), len(cells))]) for _ in range(n_boot)]
    return {"pooled_dti": float(pooled(cells)),
            "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))],
            "n_cells": len(cells), "n_withheld_positives": int(sum(c[2] for c in cells)),
            "ci_method": "bootstrap over the 8 holdout cells (draws 20/21 x 4 quadrants), 2000 reps"}


def main() -> int:
    t0 = time.time()
    receipt: dict = {"experiment": "H-CVF2 (round-5 experiment 1 of <=3)",
                     "preregistration": "docs/research/hypotheses-round5.md",
                     "started_utc": datetime.now(timezone.utc).isoformat(),
                     "budget_px": BUDGET, "b_gate_px": B_GATE_PX, "support_cap_px": SUPPORT_CAP}
    print("[1/7] loading stack, labels, footprint, quadrants")
    stack = np.lib.format.open_memmap(STACK_PATH, mode="r")
    labels = load_mask(G / "labels.tif")
    with rasterio.open(G / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    quad = holdout.quadrant_ids(foot)
    d_cat = distance_transform_edt(~labels)
    rng = np.random.default_rng(SEED)

    print("[2/7] leakage canary: per-channel AUC (catalogue vs sampled non-catalogue)")
    from sklearn.metrics import roc_auc_score
    pos_idx = np.flatnonzero(labels & foot)
    neg_pool = np.flatnonzero(foot & ~labels)
    neg_idx = rng.choice(neg_pool, size=240_000, replace=False)
    flat = stack.reshape(-1, stack.shape[2])
    quad_flat = quad.reshape(-1)
    canary = {}
    worst = 0.0
    for ci, name in enumerate(features.CHANNELS):
        pv = np.asarray(flat[pos_idx, ci], dtype=np.float64)
        nv = np.asarray(flat[neg_idx, ci], dtype=np.float64)
        y = np.r_[np.ones(pv.size), np.zeros(nv.size)]
        auc = float(roc_auc_score(y, np.r_[pv, nv]))
        auc = max(auc, 1.0 - auc)  # direction-free: a channel may be sign-flipped
        per_q = []
        for q in range(4):
            pq = np.asarray(flat[pos_idx[quad_flat[pos_idx] == q], ci], dtype=np.float64)
            nq = np.asarray(flat[neg_idx[quad_flat[neg_idx] == q], ci], dtype=np.float64)
            if pq.size and nq.size:
                a = float(roc_auc_score(np.r_[np.ones(pq.size), np.zeros(nq.size)], np.r_[pq, nq]))
                per_q.append(max(a, 1.0 - a))
        canary[name] = {"auc_pooled": auc, "auc_max_quadrant": float(max(per_q))}
        worst = max(worst, auc, float(max(per_q)))
        print(f"    {name:14s} AUC pooled={auc:.4f} max-quadrant={max(per_q):.4f}")
    receipt["leakage_canary"] = {"channels": canary, "worst_auc": worst, "threshold": AUC_CANARY,
                                 "n_pos": int(pos_idx.size), "n_neg": int(neg_idx.size),
                                 "passed": bool(worst <= AUC_CANARY)}
    if worst > AUC_CANARY:
        receipt["verdict"] = "negative"
        receipt["verdict_reason"] = f"leakage canary failed: worst channel AUC {worst:.4f} > {AUC_CANARY}"
        (ROOT / "evidence" / "hcvf2_run.json").write_text(json.dumps(receipt, indent=1))
        print("CANARY FAILED — stopping before training."); return 2

    print("[3/7] 4-quadrant spatial-CV GBM field (DetectorSpec defaults, untuned)")
    spec = detector.DetectorSpec()
    receipt["detector_spec"] = spec.as_dict()
    field = np.zeros(labels.shape, dtype=np.float32)
    fold_rows = {}
    for q in range(4):
        collar = binary_dilation(quad == q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX)
        train_mask = foot & ~collar
        frng = np.random.default_rng(SEED + q)
        X, y = detector.sample_training_rows(stack, labels, train_mask, spec, frng)
        det = detector.Detector(spec).fit(X, y)
        rows = np.flatnonzero((quad == q).any(axis=1))
        pred_q = np.zeros(labels.shape, dtype=np.float32)
        for y0 in range(int(rows[0]), int(rows[-1]) + 1, 200):
            y1 = min(y0 + 200, int(rows[-1]) + 1)
            pred_q[y0:y1] = det.predict_field(stack, y0, y1)
        field[quad == q] = pred_q[quad == q]
        fold_rows[f"quadrant_{q}"] = {"train_pos_sampled": int((y == 1).sum()),
                                      "train_neg_sampled": int((y == 0).sum()),
                                      "predicted_px": int((quad == q).sum())}
        print(f"    fold {q}: trained on {int((y==1).sum()):,} pos / {int((y==0).sum()):,} neg -> predicted quadrant {q}")
        del X, y, det, pred_q
    receipt["cv_folds"] = fold_rows
    field[~foot] = 0.0
    np.save(FIELD_PATH, field)
    receipt["field"] = {"path": str(FIELD_PATH), "min": float(field.min()), "max": float(field.max()),
                        "mean_in_footprint": float(field[foot].mean()),
                        "sha256_npy": hashlib.sha256(FIELD_PATH.read_bytes()).hexdigest()}

    print("[4/7] emission: B=2 gate + top-500k support + lazy-greedy max-coverage @ 37,654")
    gated = field.copy()
    gated[d_cat <= B_GATE_PX] = 0.0
    gated[~foot] = 0.0
    flat_g = gated.ravel()
    if int((flat_g > 0).sum()) > SUPPORT_CAP:
        thr = np.partition(flat_g, flat_g.size - SUPPORT_CAP)[flat_g.size - SUPPORT_CAP]
        gated = np.where(gated >= thr, gated, 0.0).astype(np.float32)
    receipt["support_px_after_gates"] = int((gated > 0).sum())
    t_emit = time.time()
    mask, elog = emitter.emit(gated, budget=BUDGET, prior_dti=0.0)
    receipt["emission"] = elog.as_dict() if hasattr(elog, "as_dict") else str(elog)
    receipt["emission_seconds"] = round(time.time() - t_emit, 1)
    receipt["emitted_px"] = int(mask.sum())
    receipt["emitted_on_catalogue_px"] = int((mask & labels).sum())
    receipt["emitted_within_2px_of_catalogue"] = int((d_cat[mask] <= 2).sum())
    del gated

    print("[5/7] holdout validation (candidate vs champion/solo/anderson/d28)")
    ctx = holdout.load_holdout_context(G)
    table = {}
    cand = {
        "H-CVF2": mask,
        "CHAMPION_h33-2-b2": load_mask(REGISTRY_RASTERS["CHAMPION_h33-2-b2_0.2778"]),
        "SOLO28_h27-4": load_mask(REGISTRY_RASTERS["SOLO28_h27-4_0.2708"]),
        "ANDERSON36": load_mask(REGISTRY_RASTERS["ANDERSON36_0.2750"]),
        "D28_d2-8": load_mask(REGISTRY_RASTERS["D28_d2-8_0.2600"]),
    }
    for nm, m in cand.items():
        r = holdout.evaluate_candidate_holdout(m, ctx, name=nm)
        r["pooled"] = pooled_dti_ci(r["catalogue_hidden_folds"])
        table[nm] = r
        print(f"    {nm:18s} dots={r['emitted_pixels']:>6,} cat_hidden={r['catalogue_hidden_mean']:.5f} "
              f"sgmc_cal={r['sgmc_prevalence_calibrated_dti']:.5f} drift={r['drift_corrected_holdout_mean']:.5f} "
              f"pooled={r['pooled']['pooled_dti']:.5f} CI95={r['pooled']['ci95']}")
    receipt["holdout"] = {k: {kk: vv for kk, vv in v.items() if kk != "catalogue_hidden_folds"}
                          for k, v in table.items()}
    for k, v in table.items():
        receipt["holdout"][k]["catalogue_hidden_folds"] = v["catalogue_hidden_folds"]
    paired = [table["H-CVF2"]["catalogue_hidden_folds"][c]["dti"] -
              table["CHAMPION_h33-2-b2"]["catalogue_hidden_folds"][c]["dti"]
              for c in table["H-CVF2"]["catalogue_hidden_folds"]]
    receipt["paired_cell_dti_diff_vs_champion"] = {
        "per_cell": [float(x) for x in paired], "mean": float(np.mean(paired)),
        "cells_won": int(sum(1 for x in paired if x > 0)), "cells": len(paired)}
    gate_a = (table["H-CVF2"]["catalogue_hidden_mean"] > table["CHAMPION_h33-2-b2"]["catalogue_hidden_mean"]
              and table["H-CVF2"]["sgmc_prevalence_calibrated_dti"] > table["CHAMPION_h33-2-b2"]["sgmc_prevalence_calibrated_dti"])
    receipt["gate_a_holdout_beats_champion_both_instruments"] = bool(gate_a)

    print("[6/7] lane uniqueness vs registry rasters (field surface + final dots)")
    dens_cand = density_surface(mask)
    dt_cand_field = field  # belief surface before placement
    uniq = {}
    worst_rho, worst_frac = 0.0, 0.0
    for nm, path in REGISTRY_RASTERS.items():
        rm = load_mask(path)
        dt_r = distance_transform_edt(~rm)
        frac3 = float((dt_r[mask] <= 3).mean())
        dens_r = density_surface(rm)
        rho_dots = float(spearmanr(dens_cand[foot], dens_r[foot]).statistic)
        rho_field = float(spearmanr(dt_cand_field[foot], dens_r[foot]).statistic)
        uniq[nm] = {"frac_my_dots_within_3px": frac3, "spearman_density_final_dots": rho_dots,
                    "spearman_density_belief_field": rho_field, "registry_dots": int(rm.sum())}
        worst_rho = max(worst_rho, abs(rho_dots), abs(rho_field)); worst_frac = max(worst_frac, frac3)
        print(f"    vs {nm:28s} within3px={frac3:.4f} rho_dots={rho_dots:+.4f} rho_field={rho_field:+.4f}")
        del rm, dt_r, dens_r
    receipt["uniqueness"] = {"per_raster": uniq, "worst_abs_spearman": worst_rho,
                             "worst_frac_within_3px": worst_frac,
                             "thresholds": {"spearman_max": 0.90, "frac_within_3px_max": 0.70}}
    gate_b = bool(worst_rho <= 0.90 and worst_frac <= 0.70)
    receipt["gate_b_lane_uniqueness"] = gate_b

    print("[7/7] writing submission pair via repo writer (12-point audit fail-closed)")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slot = "PROMOTE-CANDIDATE" if (gate_a and gate_b) else "DO-NOT-SUBMIT"
    meta = {
        "candidate_id": "H-CVF2",
        "description": ("Round-5 lane H-CVF2: 4-quadrant spatial-CV HistGB field over the 35-channel "
                        "structural stack, B=2 catalogue gate, exact lazy-greedy 300m-kernel "
                        "max-coverage emission at the champion's 37,654-dot budget. "
                        "No organizer score exists; all numbers are HOLDOUT-DTI proxies."),
        "submission_note_zeros": ("GEMSDOE32 H-CVF2 | CV-GBM 35ch B=2 greedy {dots} dots; "
                                  "HOLDOUT cat {cat_hid:.4f} sgmc {sgmc_cal:.4f}; UNSCORED {slot}"),
        "submission_note_nan": ("GEMSDOE32 H-CVF2 (nan-outside twin) | CV-GBM 35ch B=2 greedy {dots} dots; "
                                "HOLDOUT cat {cat_hid:.4f} sgmc {sgmc_cal:.4f}; UNSCORED {slot}"),
        "catalogue_hidden_mean": table["H-CVF2"]["catalogue_hidden_mean"],
        "catalogue_hidden_per_quadrant": table["H-CVF2"]["catalogue_hidden_per_quadrant"],
        "sgmc_prevalence_calibrated_dti": table["H-CVF2"]["sgmc_prevalence_calibrated_dti"],
        "drift_corrected_holdout_mean": table["H-CVF2"]["drift_corrected_holdout_mean"],
        "drift_corrected_per_quadrant": table["H-CVF2"]["drift_corrected_per_quadrant"],
        "predicted_leaderboard_dti": None,
        "ei_drift_corrected": None,
        "slot_decision": slot,
    }
    bundle = submission.write_submission_pair(
        mask, foot, labels, G / "sample_submission.tif", ROOT / "docs" / "downloads",
        slug="hcvf2-cvgbm35-b2-greedy37654", timestamp_tag=ts, candidate_meta=meta)
    receipt["submission_bundle"] = bundle
    receipt["gate_c_portal_audit_12pt"] = bool(bundle["zeros_tif"]["all_checks_passed"]
                                                and bundle["nan_tif"]["all_checks_passed"])
    note = bundle["submission_note_zeros"]
    receipt["submission_note"] = note
    receipt["submission_note_chars"] = len(note)
    receipt["verdict"] = "promote" if (gate_a and gate_b and receipt["gate_c_portal_audit_12pt"]) else "negative"
    receipt["verdict_reason"] = (
        f"gate_a(holdout>champion both instruments)={gate_a}, gate_b(uniqueness)={gate_b}, "
        f"gate_c(12-pt audit)={receipt['gate_c_portal_audit_12pt']}")
    receipt["seconds_total"] = round(time.time() - t0, 1)
    (ROOT / "evidence" / "hcvf2_run.json").write_text(json.dumps(receipt, indent=1))
    print(json.dumps({"verdict": receipt["verdict"], "reason": receipt["verdict_reason"],
                      "zeros_tif": bundle["zeros_tif"]["filename"], "sha256": bundle["zeros_tif"]["sha256"],
                      "note": note, "note_chars": len(note)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
