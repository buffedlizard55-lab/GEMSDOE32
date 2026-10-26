"""Synthetic-field unit tests for ARENA48-H1-TMSPI (no competition rasters required)."""
from __future__ import annotations

import numpy as np

from gems32.tmspi import (
    K_HI,
    K_LO,
    geometric_mean_concordance,
    leakage_canary_aucs,
    local_wavenumber,
    miller_singh_tdr,
    morphological_nms,
    spi_contact_weight,
    theta_edge_strength,
    wijns_theta_map,
)


def _vertical_contact(n: int = 64, x0: int = 32, amp: float = 10.0) -> tuple[np.ndarray, np.ndarray]:
    """Synthetic vertical contact: step in x, HG peaks on the wall, VG ~ 0 on the wall."""
    x = np.arange(n, dtype=np.float64)
    field = amp * np.tanh((x - x0) / 1.5)
    field = np.broadcast_to(field, (n, n)).copy()
    gy, gx = np.gradient(field)
    hg = np.hypot(gx, gy)
    vg = np.gradient(field, axis=0) * 0.05  # nearly 2-D contact
    return hg, vg


def test_wijns_theta_is_small_on_a_vertical_contact():
    hg, vg = _vertical_contact()
    theta = wijns_theta_map(hg, vg)
    edge = theta_edge_strength(hg, vg)
    wall = theta[:, 32]
    far = theta[:, 8]
    assert float(np.mean(wall)) < float(np.mean(far))
    assert float(np.mean(edge[:, 32])) > float(np.mean(edge[:, 8]))
    assert theta.min() >= -1e-9 and theta.max() <= 0.5 * np.pi + 1e-9


def test_spi_window_rejects_too_shallow_and_too_deep():
    k_in = np.array([0.05])          # z = 20 px = 2 km, in-band
    k_shallow = np.array([0.8])      # z = 1.25 px = 125 m
    k_deep = np.array([0.005])       # z = 200 px = 20 km
    w_in = float(spi_contact_weight(k_in)[0])
    w_sh = float(spi_contact_weight(k_shallow)[0])
    w_dp = float(spi_contact_weight(k_deep)[0])
    assert w_in > 0.8
    assert w_sh < 0.2
    assert w_dp < 0.2
    assert K_LO < K_HI


def test_local_wavenumber_finite_and_nonnegative():
    tdr = miller_singh_tdr(*_vertical_contact())
    k = local_wavenumber(tdr, sigma=1.0)
    assert np.isfinite(k).all()
    assert (k >= 0).all()


def test_morphological_nms_collapses_a_3px_ribbon_to_the_crest():
    field = np.zeros((21, 21), np.float64)
    field[10, 4:17] = 1.0
    field[9, 4:17] = 0.4
    field[11, 4:17] = 0.4
    foot = np.ones_like(field, bool)
    nms = morphological_nms(field, foot, size=3)
    assert int((nms > 0).sum()) == 13
    assert (nms[10, 4:17] > 0).all()
    assert (nms[9] == 0).all() and (nms[11] == 0).all()


def test_concordance_ranks_dual_domain_above_single_domain():
    foot = np.ones((8, 8), bool)
    mag = np.zeros((8, 8))
    grav = np.zeros((8, 8))
    mag[2, 2] = 1.0
    grav[2, 2] = 1.0
    mag[5, 5] = 1.0  # magnetic-only
    out = geometric_mean_concordance(mag, grav, foot)
    assert float(out[2, 2]) > float(out[5, 5]) > 0.0


def test_canary_random_channel_is_near_half():
    rng = np.random.default_rng(0)
    foot = np.ones((40, 40), bool)
    pos = np.zeros((40, 40), bool)
    pos[10:12, 10:30] = True
    ch = {
        "mag_theta_edge": rng.random((40, 40)),
        "mag_k": rng.random((40, 40)),
        "mag_spi_weight": rng.random((40, 40)),
        "mag_belief": rng.random((40, 40)),
        "grav_theta_edge": rng.random((40, 40)),
        "grav_k": rng.random((40, 40)),
        "grav_spi_weight": rng.random((40, 40)),
        "grav_belief": rng.random((40, 40)),
        "concordance": rng.random((40, 40)),
    }
    aucs = leakage_canary_aucs(ch, pos, foot, max_neg=400, seed=1)
    assert set(aucs) == set(ch)
    assert all(0.0 <= v <= 1.0 for v in aucs.values())
    assert max(aucs.values()) < 0.90
