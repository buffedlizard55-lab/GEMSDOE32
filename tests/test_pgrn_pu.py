from __future__ import annotations

import numpy as np
import pytest

from gems32.pgrn_pu import (
    compose_physics_guarded_surface,
    extract_feature_rows,
    select_training_indices,
)


def test_physics_guard_protects_high_concordance_unlabelled_pixels():
    visible = np.zeros((20, 20), bool)
    visible[2, 2] = True
    train = np.ones_like(visible)
    prior = np.linspace(0, 1, visible.size, dtype=np.float32).reshape(visible.shape)
    idx, y, receipt = select_training_indices(
        visible,
        train,
        prior,
        reliable_negative_quantile=0.6,
        rng=np.random.default_rng(4),
        halo_exclude_px=1.0,
        max_positive=10,
        negative_ratio=1000,
    )
    neg_idx = idx[y == 0]
    assert receipt.n_positive_sample == 1
    assert np.all(prior.ravel()[neg_idx] <= receipt.physical_threshold)
    assert not np.any(prior.ravel()[neg_idx] > np.quantile(prior, 0.8))
    assert np.ravel_multi_index((2, 2), visible.shape) in idx[y == 1]


def test_training_selection_uses_visible_halo_not_hidden_catalogue():
    visible = np.zeros((15, 15), bool)
    visible[2, 2] = True
    # A would-be hidden fault at (12,12) is deliberately not supplied.
    prior = np.zeros(visible.shape, np.float32)
    train = np.ones_like(visible)
    idx, y, _ = select_training_indices(
        visible,
        train,
        prior,
        reliable_negative_quantile=0.8,
        rng=np.random.default_rng(2),
        halo_exclude_px=2.0,
        max_positive=10,
        negative_ratio=1000,
    )
    neg = set(idx[y == 0].tolist())
    assert np.ravel_multi_index((2, 3), visible.shape) not in neg
    assert np.ravel_multi_index((12, 12), visible.shape) in neg


def test_extract_rows_preserves_sorted_index_order():
    base = np.arange(6 * 7 * 2, dtype=np.float32).reshape(6, 7, 2)
    extra = (1000 + np.arange(6 * 7, dtype=np.float32)).reshape(6, 7, 1)
    idx = np.array([0, 8, 19, 41], dtype=np.int64)
    X = extract_feature_rows(base, extra, idx, chunk_rows=2)
    np.testing.assert_array_equal(X[:, :2], base.reshape(-1, 2)[idx])
    np.testing.assert_array_equal(X[:, 2:], extra.reshape(-1, 1)[idx])
    with pytest.raises(ValueError, match="sorted"):
        extract_feature_rows(base, extra, idx[::-1], chunk_rows=2)


def test_physics_fusion_is_finite_bounded_and_rewards_prior():
    posterior = np.full((3, 4), 0.4, np.float32)
    prior = np.tile(np.linspace(0, 1, 4, dtype=np.float32), (3, 1))
    gate = np.ones_like(prior)
    foot = np.ones_like(prior, bool)
    foot[0, 0] = False
    out = compose_physics_guarded_surface(posterior, prior, gate, foot)
    assert np.isfinite(out).all()
    assert out.min() >= 0 and out.max() <= 1
    assert out[2, -1] > out[2, 0]
    assert out[0, 0] == 0
