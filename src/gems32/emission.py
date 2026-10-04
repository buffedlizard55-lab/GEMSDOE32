"""Emitters: how a detector field becomes a legal 0/1 prediction raster.

The decision rule is analytic.  With ``D = 0.2 (T + S - M) + 0.8 K`` (see ``metric.py``), adding
one unit of prediction mass at a pixel changes ``D`` by exactly 0.2, so

    dDTI > 0  <=>  dT > 0.2 * dS * DTI  <=>  credit per unit mass  >  0.2 * DTI .

Let ``c* = 0.2 * DTI`` be the **credit bar**.  It is 0.052 at the group's claimed best (0.26) and
0.065 at the current public leaderboard #1 (0.3262).  Every emitter below is a way of estimating
the left-hand side without the hidden labels.  Two structural consequences drive the design:

* mass that is *not* the best covering pixel of some hidden truth pixel is pure cost, so
  duplicates must be pruned -- this is why dotting a thick surface helps;
* a single pixel can be the best cover for several truth pixels (a fault network is 1 px wide,
  so a pixel on a straight trace can serve 3-5 truth pixels at once), so credit is *not*
  proportional to the number of emitted pixels; only the greedy/marginal view is correct.
"""
from __future__ import annotations

from typing import Iterable, Tuple

import numpy as np

from . import metric as M


# --------------------------------------------------------------------------------------- helpers
def threshold_field(field: np.ndarray, q: float, footprint: np.ndarray | None = None) -> np.ndarray:
    """Boolean support at the ``q`` quantile of a field inside the footprint."""
    f = np.asarray(field, dtype=np.float32)
    m = footprint if footprint is not None else np.isfinite(f)
    vals = f[m]
    if vals.size == 0:
        return np.zeros(f.shape, bool)
    tau = np.quantile(vals, 1.0 - q)
    return m & (f >= tau)


def topk_mask(field: np.ndarray, n: int, footprint: np.ndarray | None = None) -> np.ndarray:
    """Exactly ``n`` highest-field pixels inside the footprint (ties broken by raster index)."""
    f = np.asarray(field, dtype=np.float32).copy()
    m = footprint if footprint is not None else np.isfinite(f)
    f[~m] = -np.inf
    flat = f.ravel()
    if n >= int(m.sum()):
        return m.copy()
    idx = np.argpartition(flat, -n)[-n:]
    out = np.zeros(flat.size, bool)
    out[idx] = True
    return out.reshape(f.shape)


# --------------------------------------------------------------------------------------- emitters
def dot_thin(support: np.ndarray, min_dist: float) -> np.ndarray:
    """Canonical raster-order Poisson-disk thinning (the incumbent rule, kept for comparison).

    Keeps a pixel iff no already-kept pixel is closer than ``min_dist``, walking candidates in
    ascending raster index; the field never influences the layout.
    """
    ys, xs = np.nonzero(support)
    if ys.size == 0:
        return np.zeros(support.shape, bool)
    r2 = min_dist * min_dist
    cell = max(1.0, float(min_dist))
    grid: dict = {}
    out = np.zeros(support.shape, bool)
    r = int(np.ceil(min_dist))
    for i in range(ys.size):
        y, x = int(ys[i]), int(xs[i])
        cy, cx = int(y // cell), int(x // cell)
        ok = True
        for gy in range(cy - 2, cy + 3):
            for gx in range(cx - 2, cx + 3):
                for (ky, kx) in grid.get((gy, gx), ()):
                    dy, dx = y - ky, x - kx
                    if dy * dy + dx * dx < r2:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            out[y, x] = True
            grid.setdefault((cy, cx), []).append((y, x))
    return out


def dot_thin_matched(field: np.ndarray, n_target: int, footprint: np.ndarray,
                     min_dist: float = 2.8, tol: float = 0.10) -> np.ndarray:
    """Incumbent ``dot_thin`` rule calibrated to emit ~``n_target`` pixels.

    The group's own density sweep showed the shipped artifact is the maximum of its family, so a
    rule comparison at unequal mass is not informative; this driver binary-searches the support
    quantile so the raster-order cascade emits the same number of pixels as the arms it is
    compared with.
    """
    lo, hi = 0.0, 1.0
    best = None
    for _ in range(14):
        q = 0.5 * (lo + hi)
        sup = threshold_field(field, q, footprint)
        m = dot_thin(sup, min_dist)
        n = int(m.sum())
        if best is None or abs(n - n_target) < abs(best[0] - n_target):
            best = (n, m)
        if n > n_target * (1 + tol):
            hi = q                     # too many kept -> shrink the support
        elif n < n_target * (1 - tol):
            lo = q
        else:
            break
    return best[1]


def _kernel_offsets() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    r = int(M.RADIUS_PX)
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    dy, dx = dy.ravel(), dx.ravel()
    d = np.hypot(dy, dx)
    k = d <= M.RADIUS_PX
    return dy[k].astype(int), dx[k].astype(int), M.kernel(d[k])


_OFF = _kernel_offsets()


def _cover_update(pred: np.ndarray, dy: int, dx: int) -> np.ndarray:
    """Roll ``pred`` by (dy, dx) with zero fill (used for neighbour coverage maps)."""
    out = np.zeros_like(pred, dtype=np.float32)
    h, w = pred.shape
    ys0, ys1 = max(0, dy), min(h, h + dy)
    xs0, xs1 = max(0, dx), min(w, w + dx)
    out[ys0:ys1, xs0:xs1] = pred[max(0, -dy):min(h, h - dy), max(0, -dx):min(w, w - dx)]
    return out


def coverage_credit(field: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Expected credit ``E[sum_q max(0, k(x,q) - C(q))]`` for a single candidate pixel.

    This is the metric's own true-positive gain with the detector probability acting as a
    surrogate for the (unknown) truth indicator, exactly as in the group's H37-1 objective:
    ``gain(x) = sum_q p(q) max(0, k(|x-q|) - C(q))`` with ``C(q)`` the coverage already
    supplied by the emitted set.  For an empty starting set ``C = 0`` and
    ``gain(x) = sum_q p(q) k(|x-q|)``, i.e. a kernel correlation of the field.
    """
    f = np.asarray(field, dtype=np.float32) * footprint
    gain = np.zeros_like(f)
    for dy, dx, k in _OFF:
        gain += k * _cover_update(f, dy, dx)
    return gain * footprint


def greedy_cover(field: np.ndarray, n: int, footprint: np.ndarray, min_dist: float = 0.0,
                 seed: int = 0, verbose: bool = False) -> np.ndarray:
    """Lazy-greedy maximum expected coverage at a fixed pixel budget ``n``.

    ``gain(x | S) = sum_q p(q) max(0, k(x,q) - C(q))`` is monotone and submodular, so the greedy
    order carries the (1 - 1/e) guarantee; lazily re-evaluated here.  ``min_dist`` > 0 disables
    candidates within that radius of an already-chosen pixel (the group's packing used the kernel
    itself as the exclusion, i.e. min_dist = 0 with C(q) doing the work).
    """
    f = np.asarray(field, dtype=np.float32) * footprint
    C = np.zeros_like(f)                                  # coverage already supplied at each q
    chosen = np.zeros(f.shape, bool)
    n = int(min(n, f.size))
    gain = coverage_credit(f, footprint)
    blocked = np.zeros(f.shape, bool)
    for _ in range(n):
        g = np.where(chosen | blocked, -np.inf, gain)
        i = int(np.argmax(g))
        if not np.isfinite(g.reshape(-1)[i]) or g.reshape(-1)[i] <= 0:
            break
        y, x = divmod(i, f.shape[1])
        chosen[y, x] = True
        # update coverage and the gain of the neighbourhood only (cheap because R = 3 px)
        for dy, dx, k in _OFF:
            yy, xx = y + dy, x + dx
            if 0 <= yy < f.shape[0] and 0 <= xx < f.shape[1]:
                newC = max(C[yy, xx], k)
                if newC > C[yy, xx]:
                    C[yy, xx] = newC
        if min_dist > 0:
            r = int(np.ceil(min_dist))
            y0, y1 = max(0, y - r), min(f.shape[0], y + r + 1)
            x0, x1 = max(0, x - r), min(f.shape[1], x + r + 1)
            blocked[y0:y1, x0:x1] = True
        gain = coverage_credit(f, footprint) * (1.0 - C)     # full recompute: exact and simple
    return chosen


def credit_bar_emit(field: np.ndarray, bar: float, footprint: np.ndarray,
                    min_dist: float = 2.8) -> np.ndarray:
    """Metric-native threshold emission: keep pixels whose expected credit clears the bar.

    ``field`` is read as a *per-pixel expected kernel credit toward the hidden truth* (a
    probability-like quantity in [0, 1]); the rule emits a pixel iff
    ``field(x) > bar``, then thins at ``min_dist`` so that the emitted set does not pay twice for
    the same hidden truth pixel.
    """
    support = footprint & (np.asarray(field, np.float32) > bar)
    if min_dist > 0:
        support = dot_thin(support, min_dist)
    return support


def masked_along_support(field: np.ndarray, support: np.ndarray, keep_frac: float,
                         rng: np.random.Generator) -> np.ndarray:
    """Random sub-selection of a support (content-blind control)."""
    out = np.zeros(support.shape, bool)
    ys, xs = np.nonzero(support)
    if ys.size == 0:
        return out
    take = rng.random(ys.size) < keep_frac
    out[ys[take], xs[take]] = True
    return out


def as_float(mask: np.ndarray) -> np.ndarray:
    return np.asarray(mask, dtype=np.float32)
