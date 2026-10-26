#!/usr/bin/env python3
"""Round-6 Experiment 1: R6-1 signed cross-profile STEP detector (frozen in
docs/research/hypotheses-round6.md BEFORE this build).

Label-free single-layer (band 12 det_elev) step-vs-ramp field -> champion
emission geometry (B=2, Poisson 2.8px, 37,654 dots) -> frozen gates:
(a) SGMC off-catalogue exact DTI vs champion + paired component-bootstrap CI,
(b) lane uniqueness vs every detector raster on disk, (c) dual portal validators.
Verdict promote only if ALL pass; negative is a deliverable. No slot is spent.
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
from scipy import ndimage
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32.holdout import evaluate_candidate_holdout, load_holdout_context, read_binary
from gems32.metric import ALPHA, BETA, EPS, kernel
from gems32.paths import data_dir, docs_dir, evidence_dir
from gems32.pfonly import dot_thin, pooled_dti_from_folds, robust_unit
from gems32.release_gate import compare_registry
from gems32.submission import audit_geotiff, write_submission_pair

BUDGET = 37_654
SENTINEL = np.float32(-3.4028234663852886e38)
CHAMPION = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
LANE = ("R6-1 label-free det_elev cross-profile step-vs-ramp detector, "
        "B=2 catalogue exclusion, field-ordered Poisson thinning 2.8px at 37,654 dots")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def shift(a: np.ndarray, dy: int, dx: int) -> np.ndarray:
    return ndimage.shift(a, shift=(dy, dx), order=0, mode="nearest")


def step_field(dem: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Frozen R6-1 formula (hypotheses-round6.md section 2.1)."""
    med = float(np.median(dem[foot]))
    filled = np.where(foot, dem, med).astype(np.float32)
    sm = ndimage.gaussian_filter(filled, 1.0, mode="nearest")
    best = np.zeros(sm.shape, dtype=np.float32)
    for ny, nx in ((1, 0), (0, 1), (1, 1), (1, -1)):
        mp = 0.5 * (shift(sm, -2 * ny, -2 * nx) + shift(sm, -3 * ny, -3 * nx))
        mm = 0.5 * (shift(sm, 2 * ny, 2 * nx) + shift(sm, 3 * ny, 3 * nx))
        wp = shift(sm, -6 * ny, -6 * nx)
        wm = shift(sm, 6 * ny, 6 * nx)
        step = np.abs(mp - mm)
        r = np.abs(wp - wm) / np.maximum(step, 1e-9)
        score = step * np.clip(2.0 - r, 0.0, 1.0)
        best = np.maximum(best, score.astype(np.float32))
    # structure-tensor coherence (sigma=2), same construction as gems32.features
    gx = ndimage.gaussian_filter(sm, 2.0, order=(0, 1), mode="nearest")
    gy = ndimage.gaussian_filter(sm, 2.0, order=(1, 0), mode="nearest")
    jxx = ndimage.gaussian_filter(gx * gx, 2.0, mode="nearest")
    jyy = ndimage.gaussian_filter(gy * gy, 2.0, mode="nearest")
    jxy = ndimage.gaussian_filter(gx * gy, 2.0, mode="nearest")
    tr = jxx + jyy + 1e-12
    coh = (np.sqrt(np.maximum(((jxx - jyy) * 0.5) ** 2 + jxy ** 2, 0.0)) / tr).astype(np.float32)
    field = robust_unit(best, foot) * coh
    field[~foot] = 0.0
    return field.astype(np.float32)


def rank_auc(scores: np.ndarray, y: np.ndarray) -> float:
    """Mann-Whitney AUC via ranks (no sklearn dependency). y: bool positives."""
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(scores.size, dtype=np.float64)
    ranks[order] = np.arange(1, scores.size + 1, dtype=np.float64)
    # average ranks for ties
    s_sorted = scores[order]
    i = 0
    r_sorted = ranks[order]
    while i < scores.size:
        j = i + 1
        while j < scores.size and s_sorted[j] == s_sorted[i]:
            j += 1
        if j - i > 1:
            r_sorted[i:j] = r_sorted[i:j].mean()
        i = j
    ranks[order] = r_sorted
    n1 = int(y.sum()); n0 = int(y.size - n1)
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def density_surface(dots: np.ndarray) -> np.ndarray:
    yy, xx = np.mgrid[-3:4, -3:4]
    k = np.maximum(1.0 - np.hypot(yy, xx) / 3.0, 0.0).astype(np.float32)
    return ndimage.convolve(dots.astype(np.float32), k, mode="constant")


def registry_paths() -> list[Path]:
    dl = sorted((docs_dir() / "downloads").glob("*-zeros.tif"))
    scored = sorted((data_dir() / "scored").glob("*.tif"))
    scored = [p for p in scored if "lattice" not in p.name]  # lattice: diagnostic only (IR-R6-03)
    return dl + scored


def compare_all(surface: np.ndarray, dots, foot: np.ndarray, stage: str) -> dict:
    rows, passed = [], True
    for p in registry_paths():
        other = read_binary(p)
        res = compare_registry(surface, dots, foot,
                               {p.name: (density_surface(other), other)}, stage=stage)
        rows.extend(res["comparisons"])
        passed = passed and bool(res["passed"])
        r = res["comparisons"][0]
        log(f"  {stage} vs {p.name[:52]:52s} rho={r['spearman']} within3={r['within_3px_fraction']} dup={r['duplicate']}")
    return {"stage": stage, "comparisons": rows, "passed": passed, "n_registry": len(rows)}


def sgmc_paired_bootstrap(ctx, cand: np.ndarray, champ: np.ndarray, n_boot: int = 2000) -> dict:
    truth = ctx.sgmc_off & ctx.foot & ~ctx.labels
    comp, n_comp = ndimage.label(truth, structure=np.ones((3, 3), int))
    tc = ctx.sgmc_truth_coords
    d_cand = distance_transform_edt(~(cand & ~ctx.labels))
    d_champ = distance_transform_edt(~(champ & ~ctx.labels))
    cred_c = kernel(d_cand[tc]); cred_h = kernel(d_champ[tc])
    ids = comp[tc]
    tp_c = np.bincount(ids, weights=cred_c, minlength=n_comp + 1)
    tp_h = np.bincount(ids, weights=cred_h, minlength=n_comp + 1)
    nn = np.bincount(ids, minlength=n_comp + 1).astype(np.float64)
    fp_c = float((1.0 - ctx.sgmc_k_dg[cand & ~ctx.labels]).sum())
    fp_h = float((1.0 - ctx.sgmc_k_dg[champ & ~ctx.labels]).sum())

    def dti(tp, fp, n):
        return tp / (tp + ALPHA * fp + BETA * (n - tp) + EPS)

    n_tot = float(nn.sum())
    d_c, d_h = dti(float(tp_c.sum()), fp_c, n_tot), dti(float(tp_h.sum()), fp_h, n_tot)
    pool = np.flatnonzero(nn > 0)
    rng = np.random.default_rng(6)
    diffs = np.empty(n_boot)
    for b in range(n_boot):
        pick = rng.choice(pool, size=pool.size, replace=True)
        nb = float(nn[pick].sum())
        diffs[b] = dti(float(tp_c[pick].sum()), fp_c, nb) - dti(float(tp_h[pick].sum()), fp_h, nb)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return {"candidate_sgmc_dti": float(d_c), "champion_sgmc_dti": float(d_h),
            "paired_diff": float(d_c - d_h), "paired_diff_ci95": [float(lo), float(hi)],
            "n_truth_px": int(n_tot), "n_truth_components": int(pool.size),
            "ci_note": "FP held at full-truth value; CI is a lower bound on width"}


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    log(f"data_dir={ddir}")
    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    labels = read_binary(ddir / "labels.tif") & foot
    with rasterio.open(ddir / "training_features.tif") as ds:
        assert "det_elev" in (ds.descriptions[11] or ""), ds.descriptions[11]
        raw12 = ds.read(12); raw19 = ds.read(19)
    valid12 = np.isfinite(raw12) & (raw12 > SENTINEL * np.float32(0.5))
    dem = np.where(valid12, raw12, 0.0).astype(np.float32)
    log("building R6-1 step field ...")
    field = step_field(dem, foot)
    log(f"field: finite={np.isfinite(field).all()} max={field.max():.4f} "
        f"support={int((field > 0).sum())}px")

    # leakage canary
    rng = np.random.default_rng(6)
    pos_idx = np.flatnonzero(labels)
    neg_pool = np.flatnonzero(foot & ~labels)
    neg_idx = rng.choice(neg_pool, size=min(240_000, neg_pool.size), replace=False)
    idx = np.concatenate([pos_idx, neg_idx]); y = np.zeros(idx.size, bool); y[:pos_idx.size] = True
    canaries = {}
    for nm, arr in (("R6-1 step field", field), ("band12 det_elev", np.where(valid12, raw12, 0.0)),
                    ("band19 det_elev_slope", np.where(np.isfinite(raw19), raw19, 0.0))):
        canaries[nm] = rank_auc(np.asarray(arr, dtype=np.float64).ravel()[idx], y)
        log(f"canary AUC {nm}: {canaries[nm]:.4f}")
    canary_pass = all(v <= 0.90 for v in canaries.values())

    log("surface uniqueness (stage=surface) ...")
    surf_check = compare_all(field, None, foot, "surface") if canary_pass else {"passed": False, "comparisons": []}

    cand = np.zeros(foot.shape, bool)
    if canary_pass and surf_check["passed"]:
        dist_cat = distance_transform_edt(~labels)
        eligible = foot & (dist_cat > 2.0) & (field > 0)
        log(f"emitting {BUDGET} dots (eligible={int(eligible.sum())}px) ...")
        cand = dot_thin(field, eligible, BUDGET, min_dist=2.8)
        log(f"emitted {int(cand.sum())} dots; on-catalogue={int((cand & labels).sum())}")

    log("loading holdout context + evaluating candidate & champion ...")
    ctx = load_holdout_context(ddir)
    champ = read_binary(CHAMPION)
    ev_c = evaluate_candidate_holdout(cand, ctx, "R6-1-stepprofile") if cand.any() else None
    ev_h = evaluate_candidate_holdout(champ, ctx, "champion-h33-2-b2")
    boot = sgmc_paired_bootstrap(ctx, cand, champ) if cand.any() else None
    pooled_c = pooled_dti_from_folds(ev_c["catalogue_hidden_folds"]) if ev_c else None
    pooled_h = pooled_dti_from_folds(ev_h["catalogue_hidden_folds"])
    if boot:
        log(f"SGMC exact DTI cand={boot['candidate_sgmc_dti']:.5f} champ={boot['champion_sgmc_dti']:.5f} "
            f"diff={boot['paired_diff']:+.5f} CI95={boot['paired_diff_ci95']}")
    gate_a = bool(boot and boot["candidate_sgmc_dti"] > boot["champion_sgmc_dti"])

    log("final-dot uniqueness (stage=final) ...")
    dens_c = density_surface(cand) if cand.any() else field
    fin_check = compare_all(dens_c, cand, foot, "final") if cand.any() else {"passed": False, "comparisons": []}
    # lattice diagnostic (never gated; IR-R6-03)
    lat = read_binary(ddir / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif")
    d_lat = distance_transform_edt(~lat)
    lattice_diag = {"footprint_within3px": float((d_lat[foot] <= 3).mean()),
                    "candidate_within3px": float((d_lat[cand] <= 3).mean()) if cand.any() else None,
                    "champion_within3px": float((d_lat[champ] <= 3).mean())}

    verdict = "promote" if (canary_pass and surf_check.get("passed") and fin_check.get("passed") and gate_a) else "negative"
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = "r6-stepprofile-b2-37654"
    note = f"R6-1 STEP 37654d B2 zeros | det_elev step-vs-ramp | SGMC-DTI {boot['candidate_sgmc_dti']:.4f} vs champ {boot['champion_sgmc_dti']:.4f} | {verdict.upper()}" if boot else "R6-1 STEP failed pre-gate"
    assert len(note) <= 140, len(note)
    bundle = None
    if cand.any():
        meta = {
            "candidate_id": f"GEMSDOE32-R6-STEP-{ts}",
            "description": LANE,
            "submission_note_zeros": note, "submission_note_nan": note,
            "catalogue_hidden_mean": ev_c["catalogue_hidden_mean"],
            "catalogue_hidden_per_quadrant": ev_c["catalogue_hidden_per_quadrant"],
            "sgmc_prevalence_calibrated_dti": ev_c["sgmc_prevalence_calibrated_dti"],
            "drift_corrected_holdout_mean": ev_c["drift_corrected_holdout_mean"],
            "drift_corrected_per_quadrant": ev_c["drift_corrected_per_quadrant"],
            "predicted_leaderboard_dti": None, "ei_drift_corrected": None,
            "slot_decision": verdict,
        }
        bundle = write_submission_pair(cand, foot, labels, ddir / "sample_submission.tif",
                                       docs_dir() / "downloads", slug, ts, meta)
        # zip of the zeros variant (single GeoTIFF inside)
        zname = bundle["zeros_tif"]["filename"]
        zpath = docs_dir() / "downloads" / zname
        with zipfile.ZipFile(zpath.with_suffix(".zip"), "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(zpath, arcname=zname)
        log(f"written {zname} sha256={bundle['zeros_tif']['sha256']}")

    card = {
        "hypothesis": "R6-1: concentrated cross-strike elevation steps (step-vs-ramp profile geometry in det_elev) trace weak/buried piedmont scarps missing from USGS/INGENIOUS, which mapped only strong breaks.",
        "mechanism": LANE,
        "named_nonfault_mimic": "Pleistocene Lake Lahontan shoreline terraces and road cuts (contour-following steps with no fault).",
        "lane": LANE, "experiment": "Round-6 Experiment 1 of <=3 (frozen in docs/research/hypotheses-round6.md)",
        "holdout": {
            "evaluator_version": "gems32.holdout draws 20/21 (4 quadrants, 15px collar, 12px erosion) + gems32.metric exact SGMC; alpha=0.2 beta=0.8 R=3px",
            "primary_sgmc": boot, "gate_a_pass": gate_a,
            "catalogue_hidden_pooled_candidate": pooled_c, "catalogue_hidden_pooled_champion": pooled_h,
            "catalogue_hidden_note": "REPORTED ONLY: provably perverse for B-gated files (IR-32-INSTR-03); never gated.",
            "candidate_full": ev_c, "champion_full": ev_h,
        },
        "leakage_canaries": canaries, "canary_pass_le_0.90": canary_pass,
        "correlation_overlap_vs_registry": {"surface": surf_check, "final": fin_check,
                                            "lattice_diagnostic_not_gated": lattice_diag},
        "raster_sha256": bundle["zeros_tif"]["sha256"] if bundle else None,
        "validator_output": bundle["zeros_tif"] if bundle else None,
        "submission_name": f"GEMSDOE32-R6-STEP-{bundle['content_digest8'].upper()}" if bundle else None,
        "note_le140": note, "note_chars": len(note),
        "verdict": verdict,
        "ok_to_download_and_submit": verdict == "promote",
        "slot_used": False, "selector_required": True,
        "champion_live_score_label": "0.2778 [OWNER-REPORT; no receipt in repo, IR-32-SCORE-01]",
        "candidate_live_score": "NONE - never submitted; no organizer score exists. HOLDOUT-DTI is not a leaderboard score.",
        "runtime_s": round(time.time() - t0, 1),
    }
    out = evidence_dir() / "round6_run_card.json"
    out.write_text(json.dumps(card, indent=2, default=str))
    log(f"VERDICT={verdict} card={out}")
    print(json.dumps({"verdict": verdict, "gate_a_sgmc": gate_a, "canary": canary_pass,
                      "surface": surf_check.get("passed"), "final": fin_check.get("passed"),
                      "file": bundle["zeros_tif"]["filename"] if bundle else None,
                      "sha256": card["raster_sha256"], "note": note}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
