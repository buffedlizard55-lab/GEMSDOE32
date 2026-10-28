import numpy as np

from gems32.euler import euler_solve


def test_euler_recovers_step_contact_depth_order():
    # Synthetic buried step: potential of a vertical contact smoothed at two depths.
    # The deeper (more blurred) step must return larger z0 than the shallow step.
    from scipy.ndimage import gaussian_filter
    rng = np.random.default_rng(0)
    base = np.zeros((80, 80), np.float32); base[:, 40:] = 100.0
    shallow = gaussian_filter(base, 1.0) + rng.normal(0, 0.5, base.shape).astype(np.float32)
    deep = gaussian_filter(base, 6.0) + rng.normal(0, 0.5, base.shape).astype(np.float32)
    foot = np.ones(base.shape, bool)
    zs = float(np.median(euler_solve(shallow, foot)["z0_m"][35:45, 38:42]))
    zd = float(np.median(euler_solve(deep, foot)["z0_m"][35:45, 38:42]))
    assert np.isfinite([zs, zd]).all()
    assert zd > zs  # blur width grows with source depth (Euler homogeneity)
