"""Unit tests for ARENA49-H1-PCG phase congruency (synthetic, no data files)."""
import numpy as np

from gems32 import pcg


def _foot(shape):
    f = np.zeros(shape, bool)
    f[2:-2, 2:-2] = True
    return f


def test_constant_field_has_zero_pc():
    foot = _foot((64, 64))
    field = np.full((64, 64), 3.7)
    out = pcg.phase_congruency(field, foot, nscale=3, norient=4)
    assert out["pc"].shape == field.shape
    assert np.all(out["pc"] == 0.0)


def test_step_edge_pc_high_at_edge_and_amplitude_invariant():
    foot = _foot((96, 96))
    results = []
    for amp in (1.0, 20.0):
        field = np.zeros((96, 96))
        field[:, 48:] = amp
        out = pcg.phase_congruency(field, foot, nscale=4, norient=6)
        pc = out["pc"]
        assert np.isfinite(pc).all()
        assert pc.min() >= 0.0 and pc.max() <= 1.0
        edge = pc[20:76, 48].mean()
        away = pc[20:76, 20].mean()
        results.append(edge)
        assert edge > 0.3, f"PC at a clean step should be high, got {edge}"
        assert edge > 3.0 * max(away, 1e-9)
    # Amplitude invariance: PC at the edge barely moves when contrast x20.
    assert abs(results[0] - results[1]) < 0.25


def test_smooth_ramp_has_lower_pc_than_step():
    foot = _foot((96, 96))
    step = np.zeros((96, 96)); step[:, 48:] = 5.0
    ramp = np.tile(np.linspace(0.0, 5.0, 96), (96, 1))
    pc_step = pcg.phase_congruency(step, foot, nscale=4, norient=6)["pc"]
    pc_ramp = pcg.phase_congruency(ramp, foot, nscale=4, norient=6)["pc"]
    assert pc_step[20:76, 48].mean() > pc_ramp[20:76, 48].mean()


def test_concordance_downweights_single_domain():
    foot = _foot((32, 32))
    dem = np.zeros((32, 32)); dem[16, 16] = 1.0
    grav_zero = np.zeros((32, 32))
    both = dem.copy()
    single = pcg.geometric_mean_concordance(dem, grav_zero, foot)[16, 16]
    dual = pcg.geometric_mean_concordance(dem, both, foot)[16, 16]
    assert dual > single


def test_percentile_support_and_eroded_domain():
    foot = _foot((40, 40))
    field = np.arange(1600, dtype=float).reshape(40, 40)
    sup = pcg.percentile_support(field, foot, 90.0)
    assert (sup[~foot] == 0).all()
    assert (sup > 0).sum() < (field[foot] > 0).sum()
    dom = pcg.eroded_domain(foot, 3)
    assert dom.sum() < foot.sum()
    assert not dom[0].any()


def test_canary_keys_present_in_experiment_fields():
    rng = np.random.default_rng(0)
    foot = _foot((48, 48))
    dem = rng.normal(size=(48, 48)).cumsum(axis=1)
    grav = rng.normal(size=(48, 48)).cumsum(axis=0)
    fields = pcg.build_experiment_fields(dem, grav, foot)
    for k in pcg.CHANNEL_CANARY_KEYS:
        assert k in fields
        assert np.isfinite(fields[k]).all()
    assert fields["dem_support"].shape == foot.shape
