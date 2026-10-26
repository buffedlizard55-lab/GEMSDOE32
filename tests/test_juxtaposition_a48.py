"""Unit tests for the A48-H1 JXSTEP juxtaposition transform (synthetic, no data needed)."""
import numpy as np

from gems32.juxtaposition import JX_CHANNELS, build_jx_stack, step_score


def _step_field(shape=(80, 80), col=40, lo=0.0, hi=10.0):
    f = np.full(shape, lo, dtype=np.float32)
    f[:, col:] = hi
    return f


def _ramp_field(shape=(80, 80)):
    return np.tile(np.linspace(0, 10, shape[1], dtype=np.float32), (shape[0], 1))


def test_step_beats_ramp_at_same_total_relief():
    valid = np.ones((80, 80), bool)
    s_step, _ = step_score(_step_field(), valid)
    s_ramp, _ = step_score(_ramp_field(), valid)
    # concentrated step at the boundary column
    assert s_step[40, 40] > 3.0
    # a pure ramp of the same total relief must score far lower per pixel
    assert float(s_ramp.max()) < 0.35 * float(s_step.max())
    # and a flat field scores exactly zero
    s_flat, _ = step_score(np.zeros((80, 80), np.float32), valid)
    assert float(s_flat.max()) == 0.0


def test_build_jx_stack_channels_and_concordance(tmp_path):
    h = w = 80
    stack = np.zeros((h, w, 35), np.float32)
    # depth (idx14) and gravity (idx12) step at col 40 with OPPOSITE signs (deeper = lower g)
    stack[:, :, 14] = _step_field((h, w), 40, 100.0, 900.0)
    stack[:, :, 12] = _step_field((h, w), 40, 5.0, -20.0)
    stack[:, :, 16] = _step_field((h, w), 40, 0.1, 2.0)      # cond
    stack[:, :, 5] = _step_field((h, w), 40, 10.0, 25.0)     # tc
    dem = np.zeros((h, w), np.float32)
    dem[:, 40:] = np.random.default_rng(0).normal(0, 3, (h, w - 40)).astype(np.float32)
    stack[:, :, 11] = dem                                     # rough east, smooth west, ~no step in mean
    foot = np.ones((h, w), bool)
    out = build_jx_stack(stack, foot, tmp_path / "jx.npy", log=lambda *a: None)
    assert out.shape == (h, w, 7)
    assert list(JX_CHANNELS) == ["jx_step_depth", "jx_step_grav", "jx_step_cond",
                                  "jx_step_tc", "jx_step_rough", "jx_concordant", "jx_quiescent"]
    conc = np.asarray(out[:, :, 5])
    # concordance peaks on the shared juxtaposition line, not in the field interiors
    assert conc[40, 40] > conc[40, 20] and conc[40, 40] > conc[40, 65]
    # footprint erosion: border rim is zeroed
    assert float(np.abs(np.asarray(out[0:4, :, :])).max()) == 0.0
    # quiescent never exceeds concordant
    assert float((np.asarray(out[:, :, 6]) - conc).max()) <= 1e-6
