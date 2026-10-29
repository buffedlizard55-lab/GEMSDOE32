"""Tests for the overlap and phi helpers used by scripts/focus9_exec_table_20261029.py.

Expected values are worked out by hand from the synthetic grids below, not read back from the
script, so a regression in the helper fails the test.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import focus9_exec_table_20261029 as t  # noqa: E402


def _grid(points, shape=(1, 20)):
    g = np.zeros(shape, dtype=bool)
    for r, c in points:
        g[r, c] = True
    return g


def test_near_px_is_three():
    # The 70% duplicate rule and the README define "within 3 px"; guard the constant.
    assert t.NEAR_PX == 3


def test_directional_overlap_half_within_radius():
    # a dots at col 0 and col 9; b dot at col 2 -> distances 2 (within) and 7 (outside).
    a = _grid([(0, 0), (0, 9)])
    b = _grid([(0, 2)])
    assert t.directional_overlap(a, b) == pytest.approx(0.5)


def test_directional_overlap_is_directional():
    # a = {2}, b = {0, 9}: a's only dot is 2 px from b's col-0 dot -> overlap 1.0 one way.
    # Reverse: b's dot at col 9 is 7 px from a -> overlap 0.5. The metric is not symmetric.
    a = _grid([(0, 2)])
    b = _grid([(0, 0), (0, 9)])
    assert t.directional_overlap(a, b) == pytest.approx(1.0)
    assert t.directional_overlap(b, a) == pytest.approx(0.5)


def test_directional_overlap_identical_is_one():
    a = _grid([(0, 3), (0, 15)])
    assert t.directional_overlap(a, a) == pytest.approx(1.0)


def test_directional_overlap_empty_returns_none():
    a = _grid([(0, 3)])
    empty = np.zeros_like(a)
    assert t.directional_overlap(a, empty) is None
    assert t.directional_overlap(empty, a) is None


def test_phi_identical_is_one_and_complement_is_minus_one():
    foot = np.ones((1, 4), dtype=bool)
    a = np.array([[1, 0, 1, 0]], dtype=bool)
    assert t.phi(a, a, foot) == pytest.approx(1.0)
    assert t.phi(a, ~a, foot) == pytest.approx(-1.0)


def test_phi_constant_input_returns_none():
    foot = np.ones((1, 4), dtype=bool)
    a = np.array([[1, 0, 1, 0]], dtype=bool)
    assert t.phi(a, np.zeros_like(a), foot) is None


def test_phi_ignores_cells_outside_footprint():
    foot = np.array([[1, 1, 1, 0]], dtype=bool)
    a = np.array([[1, 0, 1, 1]], dtype=bool)  # last cell outside footprint
    b = np.array([[1, 0, 1, 0]], dtype=bool)
    assert t.phi(a, b, foot) == pytest.approx(1.0)
