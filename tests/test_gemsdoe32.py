"""Comprehensive test suite for gemsdoe32 modules."""

import numpy as np
import pytest
from pathlib import Path

from gemsdoe32.metric import (
    compute_dti,
    compute_dti_components,
    dti_from_counts,
    triangular_kernel,
)
from gemsdoe32.surrogate import BayesOptSurrogate, EvaluationRecord
from gemsdoe32.emission import poisson_disk_select, score_ordered_dots
from gemsdoe32.geology import compute_dilation_tendency, compute_vent_corridor_prior
from gemsdoe32.scarp import compute_profile_curvature, extract_scarp_features
from gemsdoe32.losses import MetricShapedBoundaryLoss, CombinedTverskyBoundaryLoss
from gemsdoe32.verification import OFFICIAL_SOURCES


def test_triangular_kernel():
    assert triangular_kernel(0.0, 300.0) == 1.0
    assert triangular_kernel(150.0, 300.0) == 0.5
    assert triangular_kernel(300.0, 300.0) == 0.0
    assert triangular_kernel(400.0, 300.0) == 0.0


def test_dti_from_counts():
    score = dti_from_counts(10.0, 5.0, 2.0, alpha=0.2, beta=0.8)
    # Denominator: 10 + 0.2*5 + 0.8*2 = 10 + 1 + 1.6 = 12.6
    # Score: 10 / 12.6 = 0.79365
    assert pytest.approx(score, rel=1e-3) == 10.0 / 12.6


def test_compute_dti_exact_match():
    truth = np.zeros((20, 20), dtype=bool)
    truth[10, 10] = True
    preds = np.zeros((20, 20), dtype=np.float32)
    preds[10, 10] = 1.0

    score = compute_dti(preds, truth, pixel_m=100.0, radius_m=300.0)
    # Exact 1 pixel match: TP=1, FP=0, FN=0 -> 1.0 / (1.0 + 0 + 0) = 1.0
    assert pytest.approx(score, rel=1e-3) == 1.0


def test_compute_dti_near_miss():
    truth = np.zeros((20, 20), dtype=bool)
    truth[10, 10] = True
    preds = np.zeros((20, 20), dtype=np.float32)
    preds[10, 11] = 1.0  # 1 pixel = 100m away, within 300m

    comp = compute_dti_components(preds, truth, pixel_m=100.0, radius_m=300.0)
    # distance = 100m -> kernel = 1 - 100/300 = 2/3
    # TP weight = 2/3
    # FP weight = 1 - 2/3 = 1/3
    # FN weight = 1 - 2/3 = 1/3
    # Denominator = (2/3) + 0.2*(1/3) + 0.8*(1/3) = (2/3) + 1.0*(1/3) = 1.0
    # Score = (2/3) / 1.0 = 2/3 = 0.6666...
    assert pytest.approx(comp.score, rel=1e-2) == 2.0 / 3.0


def test_poisson_disk_spacing():
    grid = np.random.RandomState(42).uniform(0, 1, size=(50, 50)).astype(np.float32)
    valid = np.ones((50, 50), dtype=bool)

    dots = poisson_disk_select(grid, valid, min_distance_px=3.0)
    indices = np.argwhere(dots)

    # Check that no two dots are closer than 3.0 pixels
    for i in range(len(indices)):
        for j in range(i + 1, len(indices)):
            dist = np.linalg.norm(indices[i] - indices[j])
            assert dist >= 3.0 - 1e-4, f"Distance {dist} < 3.0 between {indices[i]} and {indices[j]}"


def test_dilation_tendency():
    # ESE Shmin = 115 deg.
    # Strike perpendicular to Shmin: 115 - 90 = 25 deg -> Td = 1.0
    # Strike parallel to Shmin: 115 deg -> Td = 0.0
    td = compute_dilation_tendency(np.array([25.0, 115.0, 205.0]), shmin_azimuth_deg=115.0)
    assert pytest.approx(td[0], abs=1e-2) == 1.0
    assert pytest.approx(td[1], abs=1e-2) == 0.0
    assert pytest.approx(td[2], abs=1e-2) == 1.0


def test_surrogate_gp_expected_improvement():
    surrogate = BayesOptSurrogate(ei_submission_threshold=0.005)

    # Add benchmark points
    records = [
        EvaluationRecord(
            candidate_id="h19-5",
            timestamp_utc="2026-09-30T00:00:00Z",
            design_vector={"spacing_px": 1.0, "prob_threshold": 0.95, "scarp_weight": 0.2, "vent_weight": 0.1, "dilation_weight": 0.1, "loss_boundary_weight": 0.0},
            holdout_dti=0.1922,
            live_score=0.1922,
            submitted=True,
        ),
        EvaluationRecord(
            candidate_id="d1.5",
            timestamp_utc="2026-10-02T00:00:00Z",
            design_vector={"spacing_px": 1.5, "prob_threshold": 0.95, "scarp_weight": 0.2, "vent_weight": 0.1, "dilation_weight": 0.1, "loss_boundary_weight": 0.0},
            holdout_dti=0.2477,
            live_score=0.2477,
            submitted=True,
        ),
        EvaluationRecord(
            candidate_id="d2.8",
            timestamp_utc="2026-10-02T12:00:00Z",
            design_vector={"spacing_px": 2.8, "prob_threshold": 0.95, "scarp_weight": 0.3, "vent_weight": 0.2, "dilation_weight": 0.3, "loss_boundary_weight": 0.2},
            holdout_dti=0.2600,
            live_score=0.2600,
            submitted=True,
        ),
    ]

    for r in records:
        surrogate.add_evaluation(r)

    surrogate.fit()
    mean, std = surrogate.predict({"spacing_px": 2.8, "prob_threshold": 0.95, "scarp_weight": 0.3, "vent_weight": 0.2, "dilation_weight": 0.3, "loss_boundary_weight": 0.2})
    assert mean > 0.20

    ei = surrogate.expected_improvement({"spacing_px": 3.0, "prob_threshold": 0.96, "scarp_weight": 0.4, "vent_weight": 0.3, "dilation_weight": 0.4, "loss_boundary_weight": 0.3})
    assert isinstance(ei, float)
    assert ei >= 0.0


def test_official_sources_integrity():
    assert len(OFFICIAL_SOURCES) >= 5
    for src in OFFICIAL_SOURCES:
        assert src.url.startswith("https://")
        assert src.title
        assert src.organization
