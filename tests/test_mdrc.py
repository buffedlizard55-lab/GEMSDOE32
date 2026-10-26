"""Unit and integration tests for Arena8a (MDRC), visible-only holdout v3, and automated verification."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

from gems32 import holdout, mdrc

ROOT = Path(__file__).resolve().parents[1]


def test_visible_only_holdout_resolves_b_gate_paradox():
    """Synthetic proof that visible-only B-gating fixes IR-32-INSTR-03."""
    h, w = 80, 80
    foot = np.ones((h, w), dtype=bool)
    visible = np.zeros((h, w), dtype=bool)
    visible[20, 15:65] = True

    hidden_truth = np.zeros((h, w), dtype=bool)
    hidden_truth[55, 15:65] = True
    full_cat = visible | hidden_truth

    d_vis = distance_transform_edt(~visible).astype(np.float32)
    d_hid = distance_transform_edt(~hidden_truth).astype(np.float32)
    k_dg = np.maximum(1.0 - d_hid / 3.0, 0.0).astype(np.float32)
    ty, tx = np.nonzero(hidden_truth)

    cell = holdout.PreparedCell(
        key="draw20_fold0",
        fold=0,
        seed=20,
        bbox=(slice(0, h), slice(0, w)),
        active_sub=foot & ~visible,
        truth_coords=(ty, tx),
        k_dg_sub=k_dg,
        n_truth=int(hidden_truth.sum()),
        visible_sub=visible,
        d_visible_sub=d_vis,
        visible_full=visible,
    )
    ctx = holdout.HoldoutContext(
        foot=foot,
        labels=full_cat,
        sgmc_off=np.zeros((h, w), dtype=bool),
        near_visible=visible,
        quad=np.zeros((h, w), dtype=np.int8),
        quad_bboxes={0: (slice(0, h), slice(0, w))},
        cells=[cell],
        sgmc_truth_coords=(np.array([], int), np.array([], int)),
        sgmc_k_dg=np.zeros((h, w), dtype=np.float32),
        sgmc_n_truth=0,
        sgmc_quad_truth_coords={0: (np.array([], int), np.array([], int))},
        sgmc_quad_n_truth={0: 0},
    )

    # Candidate emits dots near BOTH visible and hidden faults (2 px offset = off-visible on hidden!)
    raw_cand = np.zeros((h, w), dtype=bool)
    raw_cand[21, 15:65:3] = True   # 1 px from visible fault (wasted flank)
    raw_cand[56, 15:65:3] = True   # 1 px from hidden truth (genuine discovery!)

    # Broken full-catalogue B=2 gate deletes BOTH 21 and 56 -> DTI == 0!
    d_full = distance_transform_edt(~full_cat)
    broken_b2 = raw_cand & (d_full > 2.0)
    res_broken = holdout.evaluate_visible_only_holdout(broken_b2, ctx, b_collar_px=0.0, n_boot=50)
    assert res_broken["pooled"]["pooled_dti"] == 0.0

    # Repaired visible-only B=2 deletes wasted row 21 (`d_vis=1 <= 2`) while preserving row 56 (`d_vis=36 > 2`)!
    res_b0 = holdout.evaluate_visible_only_holdout(raw_cand, ctx, b_collar_px=0.0, n_boot=50)
    res_b2 = holdout.evaluate_visible_only_holdout(raw_cand, ctx, b_collar_px=2.0, n_boot=50)
    assert res_b2["pooled"]["pooled_dti"] > res_b0["pooled"]["pooled_dti"] > 0.25


def test_corroboration_gate_suppresses_single_domain_mimic():
    foot = np.ones((32, 32), dtype=bool)
    d1 = np.zeros((32, 32), dtype=np.float32)
    d2 = np.zeros((32, 32), dtype=np.float32)
    d3 = np.zeros((32, 32), dtype=np.float32)
    d4 = np.zeros((32, 32), dtype=np.float32)

    # Single-domain fluvial mimic at (8, 8)
    d1[8, 8] = 0.95
    # Two-domain corroborated fault at (20, 20)
    d1[20, 20] = 0.85
    d2[20, 20] = 0.80

    gate = mdrc.multi_domain_corroboration_gate(d1, d2, d3, d4, foot)
    assert gate.shape == (32, 32)
    assert float(gate[20, 20]) > 1.75 * float(gate[8, 8])
    assert np.all((gate >= 0.55) & (gate <= 1.0))


def test_sharpen_ridge_crest_concentrates_flanks_into_crest():
    h, w = 64, 64
    foot = np.ones((h, w), dtype=bool)
    foot[:4, :] = False
    line = np.zeros((h, w), dtype=np.float32)
    line[10:54, 32] = 1.0
    broad = gaussian_filter(line, sigma=2.2)
    broad /= float(broad.max())

    sharp = mdrc.sharpen_ridge_crest(broad, foot)
    assert sharp.dtype == np.float32
    assert np.all(sharp[~foot] == 0.0)
    assert np.all((sharp >= 0.0) & (sharp <= 1.0))
    # Crest-to-flank ratio at 2 px off-axis must strictly increase after sharpening
    ratio_before = float(broad[32, 32] / max(broad[32, 34], 1e-6))
    ratio_after = float(sharp[32, 32] / max(sharp[32, 34], 1e-6))
    assert ratio_after > ratio_before


def test_arena8a_automated_submission_verification():
    spec = importlib.util.spec_from_file_location(
        "verify_arena8a_submission",
        ROOT / "scripts" / "verify_arena8a_submission.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)

    res = mod.verify_all()
    assert res["ok"], f"Automated verification failed: {res['errors']}"
    assert res["audit_12_ok"] is True
    assert res["strict_finite_ok"] is True
    assert res["ok_to_download"] is True

    rc = res["run_card"]
    assert rc["submission_note_length"] <= 140
    assert len(rc["submission_note"]) <= 140
    assert rc["validator_output"]["in_footprint_nan_count"] == 0
    assert rc["validator_output"]["min_value"] >= 0.0
    assert rc["validator_output"]["max_value"] <= 1.0
    assert rc["validator_output"]["on_catalogue_positive_pixels"] == 0
    assert rc["validator_output"]["within_200m_of_catalogue_pixels"] == 0
    assert rc["correlation_and_overlap_vs_registry"]["worst_abs_surface_spearman_before_placement"] <= 0.90
    assert rc["correlation_and_overlap_vs_registry"]["worst_frac_within_3px_genuine_models"] <= 0.70
    assert rc["verdict"] in ("promote", "negative")
    assert (rc["verdict"] == "promote") == bool(rc["ok_to_submit"])
