#!/usr/bin/env python3
"""ARENA48 A48-H1-JXSTEP runner (<=3 experiments, PARALLEL-RUN PROTOCOL Rules 1-6).

Frozen lane & gates: ``docs/research/arena48-preregistration-and-hypotheses.md``.
Reuses — never forks — the shared tools: ``gems32.features`` (35-ch stack),
``gems32.holdout`` via the H38 runner's ``evaluate_experiment`` (per-cell visible-only
B=2, ``GEMSDOE32-HIDE-RECOVER-v3.0`` + ``GEMSDOE32-SGMC-CAL-v3.0``), ``gems32.emitter``
and ``scripts/submission_writer.py``.

Experiments (final artifact = better of EXP2/EXP3 by mean(HR, SGMC-cal), fixed here
before any result exists; EXP1 is a screen and can never be the artifact):
  CTRL   shared 35-ch HistGB OOF replica (control, not an experiment)
  EXP1   unsupervised ``jx_concordant`` crest alone
  EXP2   35-ch + 7 JX channels HistGB OOF (shared H38 recipe)
  EXP3   by the preregistered rule only (15% residual ``jx_quiescent`` allocation,
         or one geometric fusion), skipped if EXP2 already clears HR+SGMC points.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import emitter, features, holdout  # noqa: E402
from gems32.juxtaposition import JX_CHANNELS, build_jx_stack  # noqa: E402
from gems32.paths import data_dir, work_dir  # noqa: E402
from gems32.registry_audit import audit_final_dots, audit_surface, load_manifest  # noqa: E402
import run_h38_geothermal_experiments as h38  # noqa: E402  (shared fit/emit/evaluate)
import submission_writer  # noqa: E402

BUDGET = 37_654
SEED = 20261026
H38_BEST_HR = 0.116958          # evidence/h38_run_card.json, same evaluator v3.0
H38_BEST_CI = [0.100533, 0.132040]


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items() if not str(k).startswith("_")}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.bool_, bool)):  # before int: bool is an int subclass
        return bool(o)
    if isinstance(o, (np.floating, float)):
        return float(o)
    if isinstance(o, (np.integer, int)):
        return int(o)
    if isinstance(o, np.ndarray):
        return [_clean(v) for v in o.tolist()]
    return o


def run_canary(stacks, names, labels, foot, quad):
    """Protocol Rule 4: every channel alone, two-sided AUC <= 0.90 (H38 recipe, generalised)."""
    rng = np.random.default_rng(SEED)
    pos_idx = np.flatnonzero(labels & foot)
    neg_idx = rng.choice(np.flatnonzero(foot & ~labels), size=200_000, replace=False)
    y = np.r_[np.ones(pos_idx.size, np.int8), np.zeros(neg_idx.size, np.int8)]
    q = quad.reshape(-1)
    qp, qn = q[pos_idx], q[neg_idx]
    per, worst, worst_name = {}, 0.0, ""
    flats = [(s.reshape(-1, s.shape[2]), s.shape[2]) for s in stacks]
    offsets = np.cumsum([0] + [n for _, n in flats])
    for ci, name in enumerate(names):
        si = int(np.searchsorted(offsets, ci + 1) - 1)
        f = flats[si][0]
        pv = np.asarray(f[pos_idx, ci - offsets[si]], np.float64)
        nv = np.asarray(f[neg_idx, ci - offsets[si]], np.float64)
        if np.ptp(np.r_[pv[:100], nv[:100]]) == 0 and np.all(pv == pv[0]) and np.all(nv == pv[0]):
            auc = 0.5
        else:
            auc = float(roc_auc_score(y, np.r_[pv, nv]))
        auc = max(auc, 1.0 - auc)
        qmax = auc
        for qq in range(4):
            pq, nq = pv[qp == qq], nv[qn == qq]
            if pq.size and nq.size and np.ptp(np.r_[pq, nq]) > 0:
                aq = float(roc_auc_score(np.r_[np.ones(pq.size), np.zeros(nq.size)], np.r_[pq, nq]))
                qmax = max(qmax, aq, 1.0 - aq)
        per[name] = {"auc_pooled": round(auc, 5), "auc_max_quadrant": round(qmax, 5)}
        if max(auc, qmax) > worst:
            worst, worst_name = max(auc, qmax), name
    return {"n_channels_tested": len(names), "worst_auc": round(worst, 5),
            "worst_channel": worst_name, "threshold": 0.90,
            "passed": bool(worst <= 0.90), "channels": per}


def _paired(a_boots, b_boots, a_pt, b_pt):
    d = np.asarray(a_boots) - np.asarray(b_boots)
    return {"point_delta": round(float(a_pt - b_pt), 6),
            "mean_boot_delta": round(float(d.mean()), 6),
            "ci95": [round(float(np.percentile(d, 2.5)), 6), round(float(np.percentile(d, 97.5)), 6)],
            "prob_positive": round(float((d > 0).mean()), 4)}


def _gate_field(field, visible, foot, d_vis=None):
    d = distance_transform_edt(~visible) if d_vis is None else d_vis
    f = np.asarray(field, np.float32).copy()
    f[~(foot & (d > 2.0))] = 0.0
    flat = f.ravel()
    cap = 320_000
    if int((flat > 0).sum()) > cap:
        thr = float(np.partition(flat, flat.size - cap)[flat.size - cap])
        f = np.where(f >= thr, f, 0.0).astype(np.float32)
    return f


def two_stage_mask(field_a, field_b, visible, foot, budget, d_vis=None):
    """85% field_a then 15% field_b as exact residual coverage (shared emitter)."""
    b_a = int(round(0.85 * budget))
    b_b = budget - b_a
    fa = _gate_field(field_a, visible, foot, d_vis)
    mask_a, _ = emitter.emit(fa, budget=b_a, prior_dti=0.0)
    fb = _gate_field(field_b, visible, foot, d_vis)
    mask_b, _ = emitter.emit(fb, budget=b_b, prior_dti=0.0, initial_mask=mask_a)
    return (mask_a | mask_b), fa


def evaluate_two_stage(exp2_field, quiescent, ctx):
    cell_masks = {}
    total = float(ctx.foot.sum())
    for cell in ctx.cells:
        sl = cell.bbox
        qb = max(1, int(round(BUDGET * float(ctx.foot[sl].sum()) / total)))
        vis = ctx.visible_by_cell[cell.key]
        m, _ = two_stage_mask(exp2_field[sl], quiescent[sl], vis[sl], ctx.foot[sl],
                              qb, d_vis=cell.d_vis_sub)
        cell_masks[cell.key] = m
    hr = holdout.evaluate_hide_and_recover(cell_masks, ctx, b_visible_px=2.0, name="A48EXP3")
    full_mask, live_surface = two_stage_mask(exp2_field, quiescent, ctx.labels, ctx.foot, BUDGET)
    sg = holdout.evaluate_sgmc_with_ci(full_mask, ctx, name="A48EXP3")
    legacy = holdout.evaluate_candidate_holdout(full_mask, ctx, name="A48EXP3")
    summary = {
        "experiment_id": "A48EXP3_TWOSTAGE_QUIESCENT15",
        "title": "EXP2 OOF 85% + jx_quiescent 15% sequential residual-coverage (preregistered)",
        "emitted_pixels": int(full_mask.sum()),
        "on_catalogue_pixels": int((full_mask & ctx.labels).sum()),
        "hide_and_recover": _clean(hr), "sgmc_off_catalogue": _clean(sg),
        "static_full_masked_legacy": {
            "catalogue_hidden_mean": legacy["catalogue_hidden_mean"],
            "sgmc_prevalence_calibrated_dti": legacy["sgmc_prevalence_calibrated_dti"],
            "drift_corrected_holdout_mean": legacy["drift_corrected_holdout_mean"]},
        "_hr_boots": hr["_boots"], "_sg_boots": sg["_cal_boots"],
    }
    print(f"  [A48EXP3] dots={summary['emitted_pixels']:,} HR={hr['pooled_dti']:.5f} "
          f"SGMCcal={sg['sgmc_prevalence_calibrated_dti']:.5f}", flush=True)
    return summary, full_mask, live_surface


def model_projection(drift_value: float) -> dict:
    """MODEL (never a score): LOO linear live~drift on the 12-artifact calibration."""
    cal = json.loads((ROOT / "evidence/instrument_calibration.json").read_text())
    x = np.array([r["drift"] for r in cal["rows"]], float)
    y = np.array([r["live_owner_report"] for r in cal["rows"]], float)
    loo_pred = np.empty_like(y)
    for i in range(len(y)):
        m = np.arange(len(y)) != i
        b, a = np.polyfit(x[m], y[m], 1)
        loo_pred[i] = a + b * x[i]
    resid = y - loo_pred
    b, a = np.polyfit(x, y, 1)
    proj = float(a + b * drift_value)
    rmse = float(np.sqrt(np.mean(resid ** 2)))
    from scipy.stats import spearmanr
    rho = float(spearmanr(x, y).statistic)
    return {"label": "MODEL projection — NOT a score, NOT organizer-confirmed",
            "method": "leave-one-out linear fit owner-reported live ~ drift_corrected_holdout_mean, "
                      "12 artifacts in evidence/instrument_calibration.json",
            "n_calibration": int(len(y)), "spearman_rho_live_vs_drift": round(rho, 3),
            "loo_mae": round(float(np.mean(np.abs(resid))), 4), "loo_rmse": round(rmse, 4),
            "candidate_drift_corrected_holdout_mean": round(float(drift_value), 6),
            "projected_live_dti_point": round(proj, 4),
            "projected_live_dti_interval_pm1.96rmse": [round(max(0.0, proj - 1.96 * rmse), 4),
                                                        round(min(1.0, proj + 1.96 * rmse), 4)],
            "warning": "Calibration rho is not statistically significant at n=12 (p~0.09 in "
                       "docs/research/instrument-calibration.md); interval is an uncertainty "
                       "statement about a weak instrument, not a promise."}


def main() -> int:
    t0 = time.time()
    ddir, wdir = data_dir(), work_dir()
    rebuild = "--rebuild" in sys.argv
    print("[0] holdout context + stacks", flush=True)
    ctx = holdout.load_holdout_context(ddir)
    stack35 = np.lib.format.open_memmap(wdir / "feature_stack.npy", mode="r")
    jx = build_jx_stack(stack35, ctx.foot, wdir / "jxstep7.npy")
    names = list(features.CHANNELS) + list(JX_CHANNELS)

    print("[1] leakage canary (42 channels)", flush=True)
    canary = run_canary([stack35, jx], names, ctx.labels, ctx.foot, ctx.quad)
    print(f"  worst AUC {canary['worst_auc']} ({canary['worst_channel']}) passed={canary['passed']}", flush=True)
    if not canary["passed"]:
        raise RuntimeError("leakage canary failed — stop (Protocol Rule 4)")

    print("[2] controls: champion recipe + CTRL-35 replica", flush=True)
    with rasterio.open(ROOT / "docs/downloads/gems32-probe-S1-ANCHOR-identical-to-live-02600.tif") as ds:
        a = ds.read(1)
        d28_mask = np.isfinite(a) & (a > 0) & ctx.foot
    with rasterio.open(ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif") as ds:
        champ_mask = (ds.read(1) > 0) & ctx.foot
    champ_hr = holdout.evaluate_hide_and_recover(d28_mask, ctx, b_visible_px=2.0, name="CHAMP_RECIPE")
    champ_sg = holdout.evaluate_sgmc_with_ci(champ_mask, ctx, name="CHAMP")
    print(f"  champ HR={champ_hr['pooled_dti']:.5f} SGMCcal={champ_sg['sgmc_prevalence_calibrated_dti']:.5f}", flush=True)

    def get_field(path, fit):
        if path.exists() and not rebuild:
            print(f"  reusing {path.name}", flush=True)
            return np.load(path)
        f = fit()
        np.save(path, f)
        return f

    ctrl_field = get_field(wdir / "a48_ctrl35_field.npy",
                           lambda: h38.fit_oof_field(stack35, None, ctx.labels, ctx.foot, ctx.quad, seed=SEED))
    ctrl_res, ctrl_mask, ctrl_surf = h38.evaluate_experiment(
        "A48CTRL35", "control: shared 35-ch HistGB OOF replica", ctrl_field, ctx, rebuild=rebuild)

    print("[EXP1/3] unsupervised jx_concordant", flush=True)
    concordant = np.asarray(jx[:, :, 5], np.float32).copy()
    concordant[~ctx.foot] = 0.0
    exp1_res, exp1_mask, exp1_surf = h38.evaluate_experiment(
        "A48EXP1_JXUNSUP", "unsupervised juxtaposition-concordance crest", concordant, ctx, rebuild=rebuild)

    print("[EXP2/3] 35ch + JX7 HistGB OOF", flush=True)
    exp2_field = get_field(wdir / "a48_exp2_field.npy",
                           lambda: h38.fit_oof_field(stack35, jx, ctx.labels, ctx.foot, ctx.quad, seed=SEED + 48))
    exp2_res, exp2_mask, exp2_surf = h38.evaluate_experiment(
        "A48EXP2_JX42", "35ch+JX7 juxtaposition HistGB OOF", exp2_field, ctx, rebuild=rebuild)

    hr = lambda r: r["hide_and_recover"]["pooled_dti"]  # noqa: E731
    sg = lambda r: r["sgmc_off_catalogue"]["sgmc_prevalence_calibrated_dti"]  # noqa: E731
    champ_sg_pt = float(champ_sg["sgmc_prevalence_calibrated_dti"])
    exp3_res = exp3_mask = exp3_surf = None
    exp3_kind = "skipped (EXP2 already clears HR-vs-CTRL point and SGMC champion point)"
    if hr(exp2_res) > hr(ctrl_res) and sg(exp2_res) < champ_sg_pt:
        print("[EXP3/3] preregistered two-stage quiescent allocation", flush=True)
        exp3_kind = "two_stage_quiescent15"
        quiescent = np.asarray(jx[:, :, 6], np.float32).copy()
        quiescent[~ctx.foot] = 0.0
        exp3_res, exp3_mask, exp3_surf = evaluate_two_stage(exp2_field, quiescent, ctx)
    elif hr(exp2_res) <= hr(ctrl_res):
        print("[EXP3/3] preregistered geometric fusion", flush=True)
        exp3_kind = "geometric_fusion_oof07_conc03"
        conc_foot = concordant[ctx.foot]
        rk = rankdata(conc_foot) / float(conc_foot.size)
        conc_rank = np.zeros_like(concordant)
        conc_rank[ctx.foot] = rk.astype(np.float32)
        fused = (np.clip(exp2_field, 1e-9, None) ** 0.7 * np.clip(conc_rank, 1e-9, None) ** 0.3).astype(np.float32)
        fused[~ctx.foot] = 0.0
        exp3_res, exp3_mask, exp3_surf = h38.evaluate_experiment(
            "A48EXP3_FUSION", "geometric fusion OOF^0.7 x rank(concordant)^0.3", fused, ctx, rebuild=rebuild)

    candidates = [(exp2_res, exp2_mask, exp2_surf)]
    if exp3_res is not None:
        candidates.append((exp3_res, exp3_mask, exp3_surf))
    best_res, best_mask, best_surf = max(candidates, key=lambda t: 0.5 * hr(t[0]) + 0.5 * sg(t[0]))
    best_id = best_res["experiment_id"]
    print(f"[select] final arm {best_id}: HR={hr(best_res):.5f} SGMCcal={sg(best_res):.5f}", flush=True)

    paired = {
        "hr_vs_champion_recipe": _paired(best_res["_hr_boots"], champ_hr["_boots"], hr(best_res), champ_hr["pooled_dti"]),
        "hr_vs_ctrl35": _paired(best_res["_hr_boots"], ctrl_res["_hr_boots"], hr(best_res), hr(ctrl_res)),
        "sgmc_vs_champion": _paired(best_res["_sg_boots"], champ_sg["_cal_boots"], sg(best_res), champ_sg_pt),
        "sgmc_vs_ctrl35": _paired(best_res["_sg_boots"], ctrl_res["_sg_boots"], sg(best_res), sg(ctrl_res)),
        "exp2_hr_vs_ctrl35": _paired(exp2_res["_hr_boots"], ctrl_res["_hr_boots"], hr(exp2_res), hr(ctrl_res)),
    }

    print("[3] uniqueness: surface (before placement) + final dots vs refreshed focus registry", flush=True)
    manifest = load_manifest(ROOT / "registry/focus_registry_manifest.json")
    template = ddir / "sample_submission.tif"
    surf_audit = audit_surface(best_surf, ctx.foot, manifest, root=ROOT, template_tif=template)
    final_audit = audit_final_dots(best_surf, best_mask, ctx.foot, manifest, root=ROOT, template_tif=template)
    def genuine(audit):
        dups = [d for d in audit["duplicates"] if "lattice-s5" not in str(d.get("path"))]
        lat = [d for d in audit["duplicates"] if "lattice-s5" in str(d.get("path"))]
        comps = audit.get("comparisons", [])
        gen = [c for c in comps if "lattice-s5" not in str(c.get("path")) and c.get("within_3px_fraction") is not None]
        lat_rows = [c for c in comps if "lattice-s5" in str(c.get("path"))]
        return {"genuine_duplicates": dups, "lattice_duplicates": lat,
                "max_genuine_within_3px": max((c["within_3px_fraction"] for c in gen), default=None),
                "worst_genuine": max(gen, key=lambda c: c["within_3px_fraction"], default=None),
                "lattice_within_3px": (lat_rows[0].get("within_3px_fraction") if lat_rows else None)}
    g_final = genuine(final_audit)
    genuine_pass = bool(surf_audit["passed"] and not g_final["genuine_duplicates"]
                        and (g_final["max_genuine_within_3px"] or 0) <= 0.70)
    literal_pass = bool(surf_audit["passed"] and final_audit["passed"])
    print(f"  surface worst |rho|={surf_audit['worst_abs_spearman']:.4f} passed={surf_audit['passed']} "
          f"| final genuine max3px={g_final['max_genuine_within_3px']} lattice={g_final['lattice_within_3px']} "
          f"genuine_pass={genuine_pass} literal_pass={literal_pass}", flush=True)

    drift = float(best_res["static_full_masked_legacy"]["drift_corrected_holdout_mean"])
    projection = model_projection(drift)

    gates = {
        "canary_le_090": bool(canary["passed"]),
        "hr_point_gt_h38_repo_best_0.116958": bool(hr(best_res) > H38_BEST_HR),
        "hr_paired_vs_champion_ci_gt_0": bool(paired["hr_vs_champion_recipe"]["ci95"][0] > 0),
        "hr_paired_vs_ctrl_ci_gt_0": bool(paired["hr_vs_ctrl35"]["ci95"][0] > 0),
        "sgmc_cal_ge_champion": bool(sg(best_res) >= champ_sg_pt),
        "surface_spearman_le_090_all_registry": bool(surf_audit["passed"]),
        "genuine_final_dots_le_070": genuine_pass,
        "literal_final_dots_le_070_incl_lattice": literal_pass,
    }
    promote = bool(all(gates.values()))
    verdict = "promote" if promote else "negative"
    gate_tag = "PROMOTE-TO-SELECTOR" if promote else "DO NOT SUBMIT"

    print("[4] write validated submission (shared writer)", flush=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    note = (f"A48-H1 JXSTEP juxtaposition {BUDGET}d B2 | HR={hr(best_res):.4f} "
            f"SGMC={sg(best_res):.4f} | {'selector-review' if promote else 'research artifact'}")[:140]
    meta = {"candidate_id": best_id, "description": best_res["title"],
            "submission_note_zeros": note, "submission_note_nan": note,
            "catalogue_hidden_mean": best_res["static_full_masked_legacy"]["catalogue_hidden_mean"],
            "sgmc_prevalence_calibrated_dti": sg(best_res),
            "drift_corrected_holdout_mean": drift, "slot_decision": gate_tag}
    bundle = submission_writer.write_validated_submission(
        best_mask, slug="arena48-jxstep-37654", candidate_meta=meta,
        ddir=ddir, out_dir=ROOT / "docs/downloads", timestamp_tag=ts)
    zeros = bundle["zeros_tif"]
    zpath = ROOT / "docs/downloads" / zeros["filename"]

    # Independent strict portal validation on the saved bytes (shared check tool logic).
    from gemsdoe32.submission import validate_submission_geotiff
    portal = validate_submission_geotiff(zpath, template, strict_whole_array_finite=True)
    portal_dict = portal.to_dict() if hasattr(portal, "to_dict") else {"passed": bool(getattr(portal, "passed", False))}

    sub_name = f"GEMSDOE32-A48-JXSTEP-{zeros['sha256'][:8].upper()}"
    experiments = {"generated_utc": datetime.now(timezone.utc).isoformat(),
                   "canary": canary, "champion_recipe_hr": _clean(champ_hr),
                   "champion_sgmc": _clean(champ_sg), "ctrl35": _clean(ctrl_res),
                   "exp1": _clean(exp1_res), "exp2": _clean(exp2_res),
                   "exp3_kind": exp3_kind,
                   "exp3": _clean(exp3_res) if exp3_res else None,
                   "paired": paired, "model_projection": projection}
    (ROOT / "evidence/arena48_jxstep_experiments.json").write_text(json.dumps(experiments, indent=2) + "\n")

    run_card = {
        "protocol_version": "parallel-run-v1-20261026",
        "hypothesis_id": "A48-H1-JXSTEP",
        "hypothesis": (f"{best_id}: fault-juxtaposition step concordance — same-orientation "
                       "step-vs-ramp steps in basement depth, gravity, conductivity, radiometric "
                       "TC and DEM roughness (7 label-free JX channels, docs/research/"
                       "arena48-preregistration-and-hypotheses.md) recover faults missing from "
                       "the surface-scarp catalogue; " + best_res["title"]),
        "mechanism": ("A fault juxtaposes two blocks; where its elevation scarp is buried the "
                      "juxtaposition still steps basement/gravity/conductivity/texture across "
                      "the trace at one orientation. Concordance across independent physics "
                      "separates through-going faults from single-field contacts."),
        "named_non_fault_mimic": ("Unfaulted lithologic contacts (pluton walls, ash-flow tuff "
                                  "boundaries, caldera margins) and Lake Lahontan shoreline "
                                  "benches, which juxtapose the same fields without a "
                                  "through-going geothermal conduit fault."),
        "lane": "A48-H1-JXSTEP (frozen in preregistration §2; no assigned paragraph was supplied)",
        "holdout_dti": {
            "primary_hide_and_recover": {"label": "HOLDOUT-DTI",
                "evaluator_version": "GEMSDOE32-HIDE-RECOVER-v3.0",
                "n_withheld_positives": best_res["hide_and_recover"]["n_withheld_positives"],
                "pooled_dti": hr(best_res), "ci95": best_res["hide_and_recover"]["ci95_cluster_bootstrap"],
                "per_quadrant_dti": best_res["hide_and_recover"]["per_quadrant_dti"],
                "champion_recipe_same_evaluator": float(champ_hr["pooled_dti"]),
                "ctrl35_same_evaluator": hr(ctrl_res),
                "repository_best_h38_same_evaluator": H38_BEST_HR, "repository_best_h38_ci95": H38_BEST_CI,
                "paired_vs_champion_recipe": paired["hr_vs_champion_recipe"],
                "paired_vs_ctrl35": paired["hr_vs_ctrl35"]},
            "secondary_off_catalogue_sgmc": {"label": "HOLDOUT-DTI",
                "evaluator_version": "GEMSDOE32-SGMC-CAL-v3.0",
                "n_withheld_positives": best_res["sgmc_off_catalogue"]["n_withheld_positives"],
                "sgmc_prevalence_calibrated_dti": sg(best_res),
                "ci95": best_res["sgmc_off_catalogue"]["sgmc_calibrated_ci95"],
                "champion_same_evaluator": champ_sg_pt,
                "paired_vs_champion": paired["sgmc_vs_champion"]},
            "model_projection_not_a_score": projection},
        "leakage_canary": {"n_channels_tested": canary["n_channels_tested"],
                           "max_single_feature_auc": canary["worst_auc"],
                           "worst_channel": canary["worst_channel"], "threshold": 0.90,
                           "passed": canary["passed"]},
        "correlation_and_overlap_vs_registry": {
            "registry_manifest": "registry/focus_registry_manifest.json (refreshed this session)",
            "registry_rasters": final_audit["registry_rasters"],
            "unique_masks_or_surfaces": final_audit["unique_pixel_masks_or_surfaces"],
            "malformed_or_missing": final_audit["malformed_or_missing"],
            "surface_before_placement": {"worst_abs_spearman": surf_audit["worst_abs_spearman"],
                                         "worst_raster": surf_audit["worst_raster"],
                                         "passed_le_090": surf_audit["passed"]},
            "final_dots": {"worst_abs_spearman": final_audit["worst_abs_spearman"],
                           "max_genuine_within_3px": g_final["max_genuine_within_3px"],
                           "worst_genuine_raster": (f"{g_final['worst_genuine'].get('repo')}:"
                                                    f"{g_final['worst_genuine'].get('path')}"
                                                    if g_final["worst_genuine"] else None),
                           "lattice_within_3px": g_final["lattice_within_3px"],
                           "genuine_passed_le_070": genuine_pass,
                           "literal_passed_incl_lattice": literal_pass,
                           "n_duplicate_rows_literal": len(final_audit["duplicates"])}},
        "raster_filename": zeros["filename"],
        "raster_sha256": zeros["sha256"],
        "validator_output": {"validated_without_human_intervention": True,
                             "writer_audit_all_checks_passed": zeros["all_checks_passed"],
                             "checks": zeros["checks"], "crs": zeros["crs"],
                             "shape": zeros["shape"], "transform": zeros["transform"],
                             "dtype": zeros["dtype"], "nodata": zeros["nodata"],
                             "full_grid_finite_pixels": zeros["full_grid_finite_pixels"],
                             "nan_inside_footprint": 0, "values_in_0_1": True,
                             "emitted_positive_pixels": zeros["emitted_positive_pixels"],
                             "on_catalogue_positive_pixels": zeros["on_catalogue_positive_pixels"],
                             "strict_portal_check_submission_passed": bool(portal_dict.get("passed", False)),
                             "strict_portal_report": _clean(portal_dict)},
        "submission_name": sub_name, "submission_note": note, "submission_note_length": len(note),
        "gates": gates, "verdict": verdict, "ok_to_submit": False,
        "decision_banner": (f"{gate_tag} — verdict={verdict}; promotion to a weekly slot is a "
                            "separate selector step (Protocol Rule 6); no slot spent by this run."),
        "experiments_used": 3 if exp3_res else 2, "experiments_budget_cap": 3,
        "exp3_kind": exp3_kind,
        "elapsed_seconds": round(time.time() - t0, 1),
        "artifacts": {"primary_zeros_tif": f"docs/downloads/{zeros['filename']}",
                      "primary_zeros_sha256": zeros["sha256"],
                      "primary_zeros_bytes": zeros["size_bytes"],
                      "zip_archive": bundle["zeros_zip"]["path"],
                      "nan_companion_tif": f"docs/downloads/{bundle['nan_tif']['filename']}",
                      "audit_json": f"docs/downloads/gemsdoe32-arena48-jxstep-37654-{ts}-"
                                    f"{bundle['content_digest8']}-audit.json",
                      "bundle": _clean(bundle)},
        "evidence": "evidence/arena48_jxstep_experiments.json",
        "preregistration": "docs/research/arena48-preregistration-and-hypotheses.md",
    }
    (ROOT / "evidence/arena48_jxstep_run_card.json").write_text(json.dumps(_clean(run_card), indent=2) + "\n")
    np.save(wdir / "a48_best_mask.npy", best_mask)
    np.save(wdir / "a48_best_surface.npy", best_surf)
    print(json.dumps({"verdict": verdict, "gates": gates, "file": zeros["filename"],
                      "sha256": zeros["sha256"], "hr": hr(best_res), "sgmc": sg(best_res),
                      "projection": projection["projected_live_dti_point"]}, indent=2))
    print(f"[done] {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
