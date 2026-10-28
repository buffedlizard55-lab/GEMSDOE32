"""Unit tests for H51-1 EWSP physical operators & fold-local Williams-Pollard fracture kernels."""

from __future__ import annotations

import numpy as np

from gems32 import ewsp


def test_screened_poisson_anisotropy_along_strike() -> None:
    h, w = 96, 96
    foot = np.ones((h, w), dtype=bool)
    src = np.zeros((h, w), dtype=np.float32)
    src[48, 48] = 1.0
    # Strike strictly North-South (along y-axis: uy=1, ux=0)
    uy = np.ones((h, w), dtype=np.float32)
    ux = np.zeros((h, w), dtype=np.float32)
    perm = np.ones((h, w), dtype=np.float32)

    phi = ewsp.solve_anisotropic_screened_poisson_f32(
        src, uy, ux, perm, foot, l_par_px=15.0, l_perp_px=3.0, n_iter=24
    )
    assert phi.shape == (h, w)
    assert phi.dtype == np.float32
    assert np.isfinite(phi).all()
    # Response 12 px along strike (y-axis) must strongly exceed response 12 px across strike (x-axis)
    assert float(phi[48 + 12, 48]) > 2.5 * float(phi[48, 48 + 12])


def test_baranov_pseudogravity_demag_step_finite_and_localized() -> None:
    h, w = 80, 80
    foot = np.ones((h, w), dtype=bool)
    # Sharp density step at x = 40 in grav_iso, while RTP has a local demagnetization trough at x = 40
    xx = np.broadcast_to(np.arange(w, dtype=np.float32)[None, :], (h, w))
    grav_iso = np.tanh((xx - 40.0) / 2.0).astype(np.float32) * 10.0
    rtp = (-8.0 * np.exp(-(((xx - 40.0) / 4.0) ** 2))).astype(np.float32)

    step = ewsp.baranov_pseudogravity_demag_step_f32(rtp, grav_iso, foot, pad_px=16)
    assert step.shape == (h, w)
    assert np.isfinite(step).all()
    assert float(step.min()) >= 0.0 and float(step.max()) <= 1.0
    assert float(step[:, 39:42].mean()) > 3.0 * float(step[:, 10:20].mean())


def test_gabriel_conduit_corridor_connects_strike_aligned_nodes() -> None:
    h, w = 80, 80
    foot = np.ones((h, w), dtype=bool)
    uy = np.ones((h, w), dtype=np.float32)
    ux = np.zeros((h, w), dtype=np.float32)
    # Four nodes: two aligned N-S along col 40 (rows 20 and 50) + two offset E-W
    nr = np.array([20, 50, 35, 35], dtype=np.int32)
    nc = np.array([40, 40, 10, 70], dtype=np.int32)
    nw = np.array([1.0, 1.0, 0.8, 0.8], dtype=np.float32)

    cor = ewsp.build_gabriel_conduit_corridor_f32(nr, nc, nw, uy, ux, foot, min_dist_px=5.0, max_dist_px=60.0)
    assert cor.shape == (h, w)
    assert np.isfinite(cor).all()
    # Midpoint of N-S segment (35, 40) is illuminated because nodes (35, 10) & (35, 70) are outside diametral disk (r=15)
    assert float(cor[35, 40]) > 0.25


def test_williams_pollard_elastostatic_coplanar_and_two_segment_relay() -> None:
    h, w = 96, 96
    foot = np.ones((h, w), dtype=bool)
    vis = np.zeros((h, w), dtype=bool)
    # Segment 1: N-S from row 15..35 at col 44 (tip at row 35 pointing south)
    vis[15:36, 44] = True
    # Segment 2: en-echelon stepped N-S from row 55..75 at col 50 (tip at row 55 pointing north)
    vis[55:76, 50] = True

    w_cop, w_rel = ewsp.compute_williams_pollard_elastostatic(vis, foot, max_reach_px=32)
    assert w_cop.shape == (h, w) and w_rel.shape == (h, w)
    assert np.isfinite(w_cop).all() and np.isfinite(w_rel).all()
    # Coplanar tip propagates south of (35, 44) at (41, 44) much stronger than off-side (25, 25)
    assert float(w_cop[41, 44]) > 0.35
    assert float(w_cop[25, 25]) == 0.0
    # Relay ramp midpoint (45, 47) between the two opposing segment tips has strong mutual relay stress
    assert float(w_rel[45, 47]) > float(w_rel[8, 44])


def test_emit_ewsp_dots_hits_exact_budget_and_spacing() -> None:
    h, w = 64, 64
    elig = np.ones((h, w), dtype=bool)
    rng = np.random.default_rng(7)
    surf = rng.uniform(0.05, 1.0, size=(h, w)).astype(np.float32)
    dots, log_d = ewsp.emit_ewsp_dots(surf, elig, budget=40, min_sep_px=2.8)
    assert int(dots.sum()) == 40
    assert log_d["n_emitted"] == 40
    ry, rx = np.nonzero(dots)
    d2 = (ry[:, None] - ry[None, :]) ** 2 + (rx[:, None] - rx[None, :]) ** 2
    np.fill_diagonal(d2, 9999)
    assert float(np.sqrt(d2.min())) >= 2.8 - 1e-6

