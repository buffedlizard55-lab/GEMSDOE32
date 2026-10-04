"""Spatially blocked hide-and-recover harness scored with the *official* metric.

Protocol (preregistered in ``registry/preregistration.json`` before the run):

* the raster is split into four quadrant blocks; for each fold the block's catalogue pixels are
  removed from the training region together with a buffer of ``buffer_px``, so the detector can
  only learn from faults it can see outside the block;
* the detector scores the block; emission arms turn the field into a 0/1 raster at a matched
  budget; every arm is scored against the hidden catalogue pixels *inside the block* with the
  official distance-weighted Tversky index (``gems32.metric``);
* arms are compared **pairwise within fold**; the report keeps the raw per-fold numbers so any
  reader can recompute the deltas.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from . import emission as E
from . import metric as M


def quadrant_blocks(shape, pad: int = 0):
    h, w = shape
    hy, hw = h // 2, w // 2
    out = []
    for i, (y0, y1) in enumerate([(0, hy), (hy, h), (0, hy), (hy, h)]):
        xr = [(0, hw), (0, hw), (hw, w), (hw, w)][i]
        out.append((y0, y1, xr[0], xr[1]))
    return out


def block_train_mask(shape, block, buffer_px: int) -> np.ndarray:
    y0, y1, x0, x1 = block
    m = np.ones(shape, bool)
    m[max(0, y0 - buffer_px):min(shape[0], y1 + buffer_px),
      max(0, x0 - buffer_px):min(shape[1], x1 + buffer_px)] = False
    return m


@dataclass
class ArmResult:
    name: str
    dti: float
    n_px: int
    credit: float = 0.0
    extra: dict = field(default_factory=dict)


def greedy_cover_adaptive(field: np.ndarray, footprint: np.ndarray, max_n: int,
                          stop_bar: float | None = None, min_dist: float = 0.0):
    """Greedy maximum-expected-coverage packing with an *adaptive* stopping rule.

    Objective (identical to the metric's true-positive term, with the field standing in for the
    unknown truth indicator):  ``gain(x | S) = sum_q p(q) max(0, k(x,q) - C(q))``.
    The loop stops at ``max_n`` pixels or -- the new element here -- as soon as the best
    remaining marginal expected credit falls below ``stop_bar = 0.2 * DTI_est`` (the analytic
    credit bar of ``metric.py``).  Returns the mask and the marginal-gain trace.
    """
    f = np.asarray(field, dtype=np.float32) * footprint
    C = np.zeros(f.shape, np.float32)
    chosen = np.zeros(f.shape, bool)
    blocked = np.zeros(f.shape, bool)
    dy, dx, kw = E._OFF
    n = int(min(max_n, int(footprint.sum())))
    # initial gain = kernel correlation of the field
    gain = np.zeros(f.shape, np.float32)
    for d, e, k in zip(dy, dx, kw):
        gain += k * E._cover_update(f, d, e)
    gain *= footprint

    trace = []
    H, W = f.shape
    for _ in range(n):
        g = np.where(chosen | blocked, -np.inf, gain)
        i = int(np.argmax(g))
        v = float(g.reshape(-1)[i])
        if not np.isfinite(v) or v <= 0.0:
            break
        if stop_bar is not None and v < stop_bar:
            trace.append({"stopped": True, "marginal": v, "bar": stop_bar, "n": int(chosen.sum())})
            break
        trace.append({"stopped": False, "marginal": v})
        y, x = divmod(i, W)
        chosen[y, x] = True
        # --- exact incremental update of C and gain in the ±R neighbourhood of the chosen pixel
        for d, e, k in zip(dy, dx, kw):
            qy, qx = y + d, x + e
            if not (0 <= qy < H and 0 <= qx < W):
                continue
            old = C[qy, qx]
            if k <= old:
                continue
            new = k
            C[qy, qx] = new
            wq = f[qy, qx]
            if wq == 0:
                continue
            for d2, e2, k2 in zip(dy, dx, kw):
                xy, xx = qy + d2, qx + e2
                if 0 <= xy < H and 0 <= xx < W:
                    dg = wq * (max(0.0, k2 - new) - max(0.0, k2 - old))
                    if dg:
                        gain[xy, xx] += dg
        if min_dist > 0:
            r = int(np.ceil(min_dist))
            blocked[max(0, y - r):min(H, y + r + 1), max(0, x - r):min(W, x + r + 1)] = True
    return chosen, trace


def run_fold(field: np.ndarray, truth: np.ndarray, footprint: np.ndarray, budget: int,
             prior_dti: float, rho: float, rng: np.random.Generator, seed: int = 0) -> dict:
    """Score every emission arm on one block against the hidden truth.

    Mass-matched protocol: the greedy arms define the reference counts, and every rival geometry is
    re-emitted at the *same* pixel count as the arm it is compared with, so no contrast can be won
    by simply emitting more or fewer pixels.
    """
    from scipy import ndimage
    from sklearn.metrics import roc_auc_score

    bar = M.ALPHA * prior_dti
    arms: dict[str, dict] = {}

    def add(name, mask, extra=None):
        m = np.asarray(mask, np.float32)
        arms[name] = {"dti": float(M.score(m, truth)), "n_px": int((m > 0).sum()),
                      "credit": float(M.components(m, truth)["TP_w"]), **(extra or {})}

    a1, tr1 = E.greedy_cover_fast(field, footprint, budget, stop_bar=None)
    n1 = int(a1.sum())
    add("A1_greedy_fixed_budget", a1, {"marginal_last": float(tr1[-1]["marginal"]) if tr1 else None})

    a2, tr2 = E.greedy_cover_fast(field, footprint, budget, stop_bar=bar)
    n2 = int(a2.sum())
    add("A2_greedy_live_bar", a2, {"bar": bar,
                                   "trace_tail": tr2[-1] if tr2 else None})

    a3, tr3 = E.greedy_cover_fast(field, footprint, budget, stop_bar=bar / (1.0 + rho))
    add("A3_greedy_discovery_bar", a3, {"bar": bar / (1.0 + rho), "rho": rho,
                                        "trace_tail": tr3[-1] if tr3 else None})

    # --- the incumbent's own rule (raster-order deterministic dot-thin), mass-matched to both
    for tag, n in (("n1", n1), ("n2", n2)):
        if n <= 0:
            continue
        m = E.dot_thin_matched(field, n, footprint, min_dist=2.8)
        add(f"A0_dot_thin_matched_{tag}", m)

    nms = (field >= ndimage.maximum_filter(field, size=3)) & footprint & (field > 0)
    a5 = E.topk_mask(np.where(nms, field, 0.0).astype(np.float32), n1, footprint)
    add("A5_nms_ridge_matched_n1", a5)

    ctrl = E.masked_along_support(field > 0, footprint, 1.0, rng)
    if ctrl.sum() > 0:
        cs = E.topk_mask(np.asarray(ctrl, np.float32), n1, footprint)
        add("A4_random_control_n1", cs)

    fp = np.asarray(footprint, bool)
    auc = float(roc_auc_score(truth[fp].astype(int), field[fp])) if truth[fp].any() else float("nan")
    return {"arms": arms, "bar": bar, "budget": budget, "auc": auc,
            "n_truth": int(truth.sum()), "n1": n1, "n2": n2, "seed": seed}


def summarise(results: list[dict]) -> dict:
    """Paired contrasts across folds, with the pre-registered promotion rule."""
    names = sorted({a for r in results for a in r["arms"]})
    means = {a: float(np.mean([r["arms"][a]["dti"] for r in results if a in r["arms"]])) for a in names}
    mean_n = {a: float(np.mean([r["arms"][a]["n_px"] for r in results if a in r["arms"]])) for a in names}
    contrasts = {}
    pairs = [("A1_greedy_fixed_budget", "A0_dot_thin_matched_n1"),
             ("A2_greedy_live_bar", "A0_dot_thin_matched_n2"),
             ("A1_greedy_fixed_budget", "A5_nms_ridge_matched_n1"),
             ("A2_greedy_live_bar", "A3_greedy_discovery_bar"),
             ("A1_greedy_fixed_budget", "A4_random_control_n1")]
    for hi, lo in pairs:
        d = [r["arms"][hi]["dti"] - r["arms"][lo]["dti"] for r in results
             if hi in r["arms"] and lo in r["arms"]]
        contrasts[f"{hi}_minus_{lo}"] = {
            "mean": float(np.mean(d)) if d else float("nan"),
            "per_fold": [round(float(x), 6) for x in d],
            "folds_positive": int(sum(1 for x in d if x > 0)), "n_folds": len(d)}
    primary = contrasts["A1_greedy_fixed_budget_minus_A0_dot_thin_matched_n1"]
    return {"arms_mean": means, "arms_mean_n_px": mean_n, "contrasts": contrasts,
            "primary": primary,
            "promotion_pass": bool(primary["mean"] > 0 and primary["folds_positive"] >= 3,
                                   ) if primary["n_folds"] else False,
            "auc_mean": float(np.mean([r["auc"] for r in results])),
            "n_truth_mean": float(np.mean([r["n_truth"] for r in results]))}
