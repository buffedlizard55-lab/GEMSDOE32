"""The official competition metric, its algebra, and the marginal emission rule.

Everything here is derived from the competition problem description
(https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/, "Performance
metric" section), quoted verbatim where it matters:

    k(d) = (1 - d/R)_+ ,  R = 300 m  (3 px at 100 m)
    TP_w = sum_{g in G} max_{x: d(x,g) <= R} p(x) k(d(x,g))
    FP_w = sum_{x: p(x) > 0} p(x) [1 - max_{g in G} k(d(x,g))]
    FN_w = sum_{g in G} [1 - max_{x: d(x,g) <= R} p(x) k(d(x,g))]
    DTI(a,b) = TP_w / (TP_w + a FP_w + b FN_w + eps),  a = 0.2, b = 0.8

Two consequences are used throughout this repository and are proved in
``docs/research.html`` and ``tests/test_metric.py``:

1.  Norm identity.  Because ``FN_w = |G| - TP_w`` exactly,

        DTI = T / (0.2 (T + S - M) + 0.8 K)

    with ``T = TP_w``, ``S = sum_x p(x)``, ``M = sum_x p(x) max_g k(d(x,g))``, ``K = |G|``.

2.  Marginal emission rule.  Adding one unit of prediction mass at a pixel whose realised
    kernel weight toward the best ground-truth pixel is ``k`` changes the denominator by
    exactly ``0.2`` (``d(D) = 0.2 dT + 0.2 dF = 0.2 k + 0.2 (1 - k)``), so

        dDTI > 0  <=>  k > 0.2 * DTI .

    With no ground truth available, use the *expected* weight:
    ``emit pixel iff E[k] > 0.2 * DTI``.  At the group's current best (0.26) the bar is
    0.052; at the current public leaderboard #1 (0.3262) it is 0.065.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

ALPHA = 0.2
BETA = 0.8
RADIUS_PX = 3.0          # 300 m at 100 m pixels
EPS = 1e-12


def kernel(d_px: np.ndarray | float) -> np.ndarray | float:
    """Triangular kernel ``k(d) = max(1 - d/R, 0)`` in **pixel** units (R = 3 px)."""
    return np.maximum(1.0 - np.asarray(d_px, dtype=np.float64) / RADIUS_PX, 0.0)


def _offsets(radius_px: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integer offsets with Euclidean distance <= radius, plus their kernel weights."""
    r = int(np.floor(radius_px))
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    dy = dy.ravel().astype(np.int64)
    dx = dx.ravel().astype(np.int64)
    dist = np.hypot(dy, dx)
    keep = dist <= radius_px
    return dy[keep], dx[keep], kernel(dist[keep])


_OFF = _offsets(RADIUS_PX)


def _shift(arr: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """Shift ``arr`` by (dy, dx), filling with 0.

    Filling with 0 is exact here because every array shifted this way is non-negative, so
    ``np.maximum`` over the shifted copies reproduces the published kernel dilation
    ``max_{x: d(x,g)<=R} p(x) k(d(x,g))`` including its empty-disk case (value 0).
    """
    out = np.zeros_like(arr)
    h, w = arr.shape
    ys0, ys1 = max(0, dy), min(h, h + dy)
    xs0, xs1 = max(0, dx), min(w, w + dx)
    out[ys0:ys1, xs0:xs1] = arr[max(0, -dy):min(h, h - dy), max(0, -dx):min(w, w - dx)]
    return out


def components(pred: np.ndarray, truth: np.ndarray) -> dict:
    """Exact ``TP_w``, ``FP_w``, ``FN_w`` and the algebra terms for one raster pair.

    ``pred``  : float array in [0, 1]; ``truth`` : boolean array (the hidden label raster).
    Both are on the same 100 m grid.  ``pred`` may contain 0 (and NaN outside the
    footprint, which is treated as 0).
    """
    p = np.asarray(pred, dtype=np.float64)
    p = np.where(np.isfinite(p), p, 0.0)
    g = np.asarray(truth).astype(bool)
    if p.shape != g.shape:
        raise ValueError("pred and truth must share a shape")

    # --- TP_w: per ground-truth pixel, the best kernel-weighted prediction in its 3-px disk
    weighted = p * 1.0
    best = np.zeros(p.shape)
    dy, dx, kw = _OFF
    # For each offset (dy,dx) the contribution to pixel (y,x) is p(y+dy, x+dx) * k(dist)
    for d, e, kk in zip(dy, dx, kw):
        np.maximum(best, _shift(weighted, -d, -e) * kk, out=best)
    best = np.clip(best, 0.0, 1.0)
    tp = float(best[g].sum())

    # --- FP_w: prediction mass with the kernel weight toward the *nearest* truth pixel removed
    if g.any():
        from scipy import ndimage
        dist_to_g = ndimage.distance_transform_edt(~g)
        k_near = kernel(dist_to_g)
    else:                                  # degenerate: no truth at all
        k_near = np.zeros(p.shape)
    fp = float((p * (1.0 - k_near)).sum())

    fn = float(g.sum()) - tp

    k_total = float(g.sum())
    s = float(p.sum())
    m = float((p * k_near).sum())
    return {
        "TP_w": tp, "FP_w": fp, "FN_w": fn,
        "K": k_total, "S": s, "M": m,
        "credit_per_unit_mass": (tp / s) if s else 0.0,
        "marginal_bar": ALPHA * dti(tp, fp, fn),
    }


def dti(tp: float, fp: float, fn: float) -> float:
    """Distance-weighted Tversky index from the three published components."""
    return float(tp / (tp + ALPHA * fp + BETA * fn + EPS))


def dti_components(tp: float, fp: float, fn: float) -> float:
    return dti(tp, fp, fn)


def dti_algebra(t: float, s: float, m: float, k: float) -> float:
    """Equivalent closed form ``T / (0.2 (T + S - M) + 0.8 K)`` (see module docstring)."""
    return float(t / (ALPHA * (t + s - m) + BETA * k + EPS))


def score(pred: np.ndarray, truth: np.ndarray) -> float:
    c = components(pred, truth)
    return dti(c["TP_w"], c["FP_w"], c["FN_w"])


def dti_binary(mask: np.ndarray, truth: np.ndarray) -> float:
    """DTI of a 0/1 emission mask against a boolean truth raster."""
    return score(np.asarray(mask, dtype=np.float64), truth)


@dataclass(frozen=True)
class CreditAudit:
    """Per-pixel credit accounting used to judge an emitter without the hidden labels."""
    n_emitted: int
    total_mass: float
    redundancy_fraction: float
    mean_self_kernel: float


def credit_audit(mask: np.ndarray) -> CreditAudit:
    """Kernel-structure audit of an emission mask (no truth required).

    ``mean_self_kernel`` is the mean, over emitted pixels, of the kernel weight that the
    *other* emitted pixels already provide at the pixel's own location.  It is the
    emission-side analogue of ``M``: the share of mass that is duplicated coverage.
    """
    m = np.asarray(mask, dtype=np.float64)
    pos = m > 0
    n = int(pos.sum())
    if n == 0:
        return CreditAudit(0, 0.0, 0.0, 0.0)
    best = np.zeros(m.shape)
    dy, dx, kw = _OFF
    for d, e, kk in zip(dy, dx, kw):
        if d == 0 and e == 0:
            continue                        # exclude the pixel's own mass
        np.maximum(best, _shift(m, -d, -e) * kk, out=best)
    red = np.clip(best, 0.0, 1.0)           # weight supplied by *neighbours* only
    return CreditAudit(
        n_emitted=n,
        total_mass=float(m.sum()),
        redundancy_fraction=float((red[pos] > 0).mean()),
        mean_self_kernel=float(red[pos].mean()),
    )
