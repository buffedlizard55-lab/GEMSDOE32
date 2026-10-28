#!/usr/bin/env python3
"""ARENA-EULER lane: 3 frozen experiments, 0 weekly slots. See preregistration doc."""
from __future__ import annotations

import gc, hashlib, json, sys, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "scripts"))
from gems32 import emitter, euler, features, holdout  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402
from gems32.pgrn_pu import two_polarity_feature_canary  # noqa: E402
from submission_writer import write_validated_submission  # noqa: E402

SEED, BUDGET, B_PX = 20261027, 37_654, 2.0
CHAMP = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"


def clean(d):
    return {k: clean(v) for k, v in d.items() if not str(k).startswith("_")} if isinstance(d, dict) else (
        [clean(v) for v in d] if isinstance(d, (list, tuple)) else (d.item() if isinstance(d, (np.floating, np.integer, np.bool_)) else d))


def qbudgets(foot, quad):
    c = np.array([int((foot & (quad == q)).sum()) for q in range(4)], float)
    e = c / c.sum() * BUDGET; r = np.floor(e).astype(int)
    for q in np.argsort(-(e - r))[:BUDGET - int(r.sum())]:
        r[q] += 1
    return {q: int(r[q]) for q in range(4)}


def Xrows(base, extra, idx, cols_extra=None):
    """cols_extra=None -> base only; else base+selected extra cols. idx sorted flat."""
    h, w, nb = base.shape
    ne = 0 if cols_extra is None else len(cols_extra)
    out = np.empty((idx.size, nb + ne), np.float32)
    rows, cols = idx // w, idx % w
    s = 0
    for y0 in range(0, h, 256):
        e = int(np.searchsorted(rows, min(h, y0 + 256), "left"))
        if e > s:
            rr, cc = rows[s:e] - y0, cols[s:e]
            out[s:e, :nb] = np.asarray(base[y0:y0 + 256], np.float32)[rr, cc]
            if ne:
                out[s:e, nb:] = np.asarray(extra[y0:y0 + 256], np.float32)[rr, cc][:, list(cols_extra)]
            s = e
        if s == idx.size:
            break
    return out


def fit_predict(base, extra, visible, train_mask, target_mask, use_euler, seed):
    rng = np.random.default_rng(seed)
    d_vis = distance_transform_edt(~visible)
    pos = np.flatnonzero(visible & train_mask)
    neg_pool = np.flatnonzero(train_mask & ~visible & (d_vis > 5))
    pos_s = rng.choice(pos, min(pos.size, 40000), replace=False)
    neg_s = rng.choice(neg_pool, min(neg_pool.size, pos_s.size * 4), replace=False)
    idx = np.sort(np.concatenate([pos_s, neg_s]))
    ymap = np.zeros(visible.size, np.int8); ymap[pos_s] = 1
    y = ymap[idx]
    cols = tuple(range(extra.shape[2])) if use_euler else None
    X = Xrows(base, extra, idx, cols)
    m = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.065, max_leaf_nodes=63,
                                       min_samples_leaf=80, l2_regularization=2.5,
                                       early_stopping=False, random_state=seed)
    wts = np.where(y == 1, 0.5 / max((y == 1).sum(), 1), 0.5 / max((y == 0).sum(), 1)) * y.size
    m.fit(X, y, sample_weight=wts)
    surf = np.zeros(visible.shape, np.float32)
    h, w = visible.shape
    for y0 in range(0, h, 128):
        sub = target_mask[y0:y0 + 128]
        if not sub.any():
            continue
        rr, cc = np.nonzero(sub)
        flat = np.sort((y0 + rr) * w + cc)
        # predict in sorted order then scatter back
        Xt = Xrows(base, extra, flat, cols)
        pr = m.predict_proba(Xt)[:, 1].astype(np.float32)
        surf.ravel()[flat] = pr
    del X, Xt, m; gc.collect()
    return surf, {"n_pos": int(pos_s.size), "n_neg": int(neg_s.size)}


def emit_q(surf, active, dvis, budget):
    elig = active & (dvis > B_PX) & np.isfinite(surf)
    g = np.where(elig, np.maximum(surf, 0), 0).astype(np.float32)
    if int((g > 0).sum()) < budget:
        raise RuntimeError("support < budget")
    mask, log = emitter.emit(g, budget=budget, prior_dti=0.0, min_sep_px=2.8)
    assert int(mask.sum()) == budget
    return mask, log.as_dict()


def paired(cand, ref):
    cb, rb = np.asarray(cand["_boots"], float), np.asarray(ref["_boots"], float)
    n = min(cb.size, rb.size); d = cb[:n] - rb[:n]
    return {"point_delta": float(cand["pooled_dti"] - ref["pooled_dti"]),
            "ci95": [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))],
            "prob_positive": float((d > 0).mean()), "n": int(n)}


def main():
    t0 = time.time(); stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ddir, wdir = data_dir(), work_dir()
    base = np.lib.format.open_memmap(wdir / "feature_stack.npy", mode="r")
    epath = wdir / "euler_stack.npy"
    if not epath.exists():
        euler.build_stack(ddir / "training_features.tif", epath)
    extra = np.lib.format.open_memmap(epath, mode="r")
    ctx = holdout.load_holdout_context(ddir)
    names = list(features.CHANNELS) + list(euler.CHANNELS)
    print("[canary] single-feature AUC screen", flush=True)
    canary = two_polarity_feature_canary(base, extra, ctx.labels, ctx.foot, ctx.quad, names, seed=SEED)
    print(f"  worst {canary['worst_channel']} {canary['worst_auc']:.4f} passed={canary['passed']}", flush=True)
    if not canary["passed"]:
        raise SystemExit("LEAKAGE CANARY FAIL — abort, no fit")

    with rasterio.open(CHAMP) as ds:
        champ_mask = np.isfinite(ds.read(1)) & (ds.read(1) > 0) if False else None
    with rasterio.open(CHAMP) as ds:
        a = ds.read(1); champ_mask = np.isfinite(a) & (a > 0) & ctx.foot
    champ_hr = holdout.evaluate_hide_and_recover(champ_mask, ctx, b_visible_px=B_PX, name="champion_02778")
    champ_sg = holdout.evaluate_sgmc_with_ci(champ_mask, ctx, name="champion_02778")
    print(f"[champion] HR={champ_hr['pooled_dti']:.6f} SGMCcal={champ_sg['sgmc_prevalence_calibrated_dti']:.6f}", flush=True)

    qb = qbudgets(ctx.foot, ctx.quad)
    collars = {q: binary_dilation(ctx.quad == q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX) & ctx.foot for q in range(4)}

    # EXP1 unsupervised Euler joint density
    joint = np.asarray(extra[:, :, 5], np.float32)
    m1 = np.zeros(ctx.foot.shape, bool)
    for q in range(4):
        mk, _ = emitter.emit(np.where(ctx.quad == q, joint, 0).astype(np.float32), budget=qb[q], prior_dti=0.0, min_sep_px=2.8)
        m1 |= mk
    # evaluator applies visible B gate; also zero catalogue for safety in SGMC eval input
    e1_hr = holdout.evaluate_hide_and_recover(m1, ctx, b_visible_px=B_PX, name="EXP1_EULER_ONLY")
    e1_sg = holdout.evaluate_sgmc_with_ci(m1 & ~ctx.labels, ctx, name="EXP1_EULER_ONLY")
    print(f"[EXP1] HR={e1_hr['pooled_dti']:.6f} SGMC={e1_sg['sgmc_prevalence_calibrated_dti']:.6f}", flush=True)

    # EXP2 / EXP3 per-cell OOF
    cells2, cells3, live_surf = {}, {}, np.zeros(ctx.foot.shape, np.float32)
    receipts = {}
    for cell in ctx.cells:
        q = cell.fold; vis = ctx.visible_by_cell[cell.key]
        train = ctx.foot & ~collars[q]; target = (ctx.quad == q)
        dvis = distance_transform_edt(~vis)
        s2, r2 = fit_predict(base, extra, vis, train, target, False, SEED + cell.fold)
        s3, r3 = fit_predict(base, extra, vis, train, target, True, SEED + 100 + cell.fold)
        cells2[cell.key], _ = emit_q(s2, target, dvis, qb[q])
        cells3[cell.key], _ = emit_q(s3, target, dvis, qb[q])
        receipts[cell.key] = {"base": r2, "euler": r3}
        print(f"  cell {cell.key} done {time.time()-t0:.0f}s", flush=True)
    e2_hr = holdout.evaluate_hide_and_recover(cells2, ctx, b_visible_px=B_PX, name="EXP2_BASE35_OOF")
    e3_hr = holdout.evaluate_hide_and_recover(cells3, ctx, b_visible_px=B_PX, name="EXP3_BASE35_EULER_OOF")
    print(f"[EXP2] HR={e2_hr['pooled_dti']:.6f}  [EXP3] HR={e3_hr['pooled_dti']:.6f}", flush=True)

    # Live surface: retrain per quadrant on full catalogue, stitch, emit final
    for q in range(4):
        train = ctx.foot & ~collars[q]
        s, _ = fit_predict(base, extra, ctx.labels, train, ctx.quad == q, True, SEED + 200 + q)
        live_surf[ctx.quad == q] = s[ctx.quad == q]
    np.save(wdir / "euler_live_surface.npy", live_surf)
    dlab = distance_transform_edt(~ctx.labels)
    live_mask, elog = emit_q(live_surf, ctx.foot, dlab, BUDGET)
    e3_sg = holdout.evaluate_sgmc_with_ci(live_mask, ctx, name="EXP3_LIVE")
    # SGMC for EXP2 control (full mask union of cells approx via live? use per-cell union)
    m2full = np.zeros(ctx.foot.shape, bool); m3full = np.zeros(ctx.foot.shape, bool)
    for k in cells2: m2full |= cells2[k]
    for k in cells3: m3full |= cells3[k]
    e2_sg = holdout.evaluate_sgmc_with_ci(m2full, ctx, name="EXP2_OOF_UNION")
    e3o_sg = holdout.evaluate_sgmc_with_ci(m3full, ctx, name="EXP3_OOF_UNION")
    print(f"[SGMC] EXP2={e2_sg['sgmc_prevalence_calibrated_dti']:.6f} EXP3oof={e3o_sg['sgmc_prevalence_calibrated_dti']:.6f} EXP3live={e3_sg['sgmc_prevalence_calibrated_dti']:.6f}", flush=True)

    results = {"champion_hr": clean(champ_hr), "champion_sgmc": clean(champ_sg),
               "exp1_hr": clean(e1_hr), "exp1_sgmc": clean(e1_sg),
               "exp2_hr": clean(e2_hr), "exp2_sgmc_oof_union": clean(e2_sg),
               "exp3_hr": clean(e3_hr), "exp3_sgmc_oof_union": clean(e3o_sg), "exp3_sgmc_live": clean(e3_sg),
               "paired_exp3_vs_champion_hr": paired(e3_hr, champ_hr),
               "paired_exp3_vs_exp2_hr": paired(e3_hr, e2_hr),
               "canary": clean(canary), "fit_receipts": receipts, "emit_log_live": clean(elog),
               "runtime_s": time.time() - t0}
    (evidence_dir() / "euler_lane_experiments.json").write_text(json.dumps(results, indent=2))
    np.save(wdir / "euler_live_mask.npy", live_mask)
    print(json.dumps({"exp3_vs_champ": results["paired_exp3_vs_champion_hr"],
                      "exp3_vs_exp2": results["paired_exp3_vs_exp2_hr"]}, indent=2))
    print(f"DONE {time.time()-t0:.0f}s -> evidence/euler_lane_experiments.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
