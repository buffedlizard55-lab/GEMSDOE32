"""Unit and saved-artifact verification tests for Session H48-1-FBGR."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial.distance import pdist

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import emitter, fbgr  # noqa: E402

H48_CARD = ROOT / "evidence" / "h48_fbgr_run_card.json"
H48_EXPS = ROOT / "evidence" / "h48_fbgr_experiments.json"
H48_FORENSICS = ROOT / "evidence" / "livescore_forensics_20261027.json"
H48_TIF = (
    ROOT
    / "docs"
    / "downloads"
    / "gemsdoe32-h48-fbgr-dualcover-axial28-37654-20261027T180500Z-4d38a240-zeros.tif"
)
H48_ZIP = (
    ROOT
    / "docs"
    / "downloads"
    / "gemsdoe32-h48-fbgr-dualcover-axial28-37654-20261027T180500Z-4d38a240-zeros.zip"
)


def test_fourier_upward_continuation_attenuates_high_frequencies_and_preserves_zero_mean():
    yy, xx = np.mgrid[0:64, 0:64].astype(np.float32)
    low_freq = np.sin(2.0 * np.pi * xx / 64.0)
    high_freq = np.sin(2.0 * np.pi * xx / 4.0)
    field = np.float32(3.5) + low_freq + high_freq
    foot = np.ones(field.shape, dtype=bool)

    uc_500, uc_2000 = fbgr.harmonic_upward_continue_pair_f32(
        field, foot, heights_m=(500.0, 2000.0), dx_m=100.0, pad_px=16
    )

    assert uc_500.shape == field.shape
    assert uc_2000.shape == field.shape
    assert np.isclose(float(uc_500.mean()), 0.0, atol=0.08)
    assert np.isclose(float(uc_2000.mean()), 0.0, atol=0.08)
    assert float(uc_2000.std()) < float(uc_500.std()) < float(field.std())


def test_block_robust_zscore_removes_inter_block_calibration_offsets():
    rng = np.random.default_rng(48)
    base_sig = rng.normal(0.0, 1.0, size=(120, 120)).astype(np.float32)
    blocks = np.ones((120, 120), dtype=np.int16)
    blocks[:, 60:] = 2
    biased = base_sig.copy()
    biased[:, :60] = biased[:, :60] * 1.5 + 10.0
    biased[:, 60:] = biased[:, 60:] * 3.0 - 25.0
    foot = np.ones((120, 120), dtype=bool)

    z = fbgr._block_zscore_f32(biased, blocks, foot)
    corr = float(np.corrcoef(z.ravel(), base_sig.ravel())[0, 1])
    assert corr > 0.99
    assert abs(float(np.median(z[:, :60]) - np.median(z[:, 60:]))) < 0.15


def test_msub_col_indices_strictly_exclude_all_lidar_channels():
    assert len(fbgr.MSUB_COL_INDICES) == 71
    assert set(fbgr.MSUB_COL_INDICES).isdisjoint(fbgr.LIDAR_DEPENDENT_GLOBAL_COLS)
    assert len(fbgr.MSUB_COL_INDICES) + len(fbgr.LIDAR_DEPENDENT_GLOBAL_COLS) == 83


def test_sharpen_probability_crest_and_min_sep_emitter_enforce_axial_spacing():
    shape = (40, 40)
    foot = np.ones(shape, dtype=bool)
    yy, xx = np.mgrid[0:40, 0:40].astype(np.float32)
    ribbon = np.exp(-0.5 * ((xx - 20.0) / 2.2) ** 2).astype(np.float32) * np.float32(0.8)

    sharp = fbgr.sharpen_probability_crest(ribbon, foot, crest_boost=0.45)
    assert sharp.min() >= 0.0 and sharp.max() <= 1.0
    # Center crest column (x=20) retains higher relative contrast over flank (x=22)
    assert float((sharp[:, 20] / np.maximum(sharp[:, 22], 1e-6)).mean()) > float(
        (ribbon[:, 20] / np.maximum(ribbon[:, 22], 1e-6)).mean()
    )

    emitted, _ = emitter.emit(sharp, budget=10, prior_dti=0.0, min_sep_px=2.8)
    pts = np.column_stack(np.nonzero(emitted))
    assert pts.shape[0] == 10
    min_d = float(pdist(pts).min())
    assert min_d >= 2.8 - 1e-6


def test_h48_run_card_and_saved_geotiff_pass_all_automated_checks():
    assert H48_CARD.is_file()
    assert H48_EXPS.is_file()
    assert H48_FORENSICS.is_file()
    assert H48_TIF.is_file()
    assert H48_ZIP.is_file()

    card = json.loads(H48_CARD.read_text())
    assert card["schema_version"] == "gems-parallel-runcard-v3"
    assert card["candidate_id"] == "H48-1-FBGR"
    assert card["experiments_used"] == 3
    assert card["experiments_budget_cap"] == 3
    assert card["weekly_slots_used"] == 0
    assert card["leakage_canary"]["passed"] is True
    assert card["leakage_canary"]["n_features_tested"] == 83
    assert card["leakage_canary"]["max_oriented_auc"] <= 0.90
    assert len(card["submission_note"]) <= 140

    hd = card["holdout_dti"]
    assert hd["primary_hide_and_recover"]["pooled_dti"] > hd["incumbent_02778_same_evaluator"]["pooled_dti"]
    assert hd["paired_delta_vs_02778_champion"]["ci95"][0] > 0.0
    assert hd["paired_delta_vs_exp2_no_min_sep"]["ci95"][0] > 0.0
    assert hd["detached_600m_segments"]["pooled_dti"] > hd["incumbent_detached_600m"]["pooled_dti"]

    un = card["correlation_and_overlap_vs_registry"]
    assert un["genuine_pre_placement_surface_passed"] is True
    assert un["genuine_final_dots_passed"] is True
    assert un["focus_site_genuine_final_passed"] is True
    assert un["max_abs_surface_spearman"] <= 0.90
    assert un["max_genuine_3px_dot_overlap"] <= 0.70
    assert un["max_focus_site_3px_dot_overlap"] <= 0.70
    assert un["literal_all_rasters_final_passed"] is False

    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["download_for_research_ok"] is True

    sha = hashlib.sha256(H48_TIF.read_bytes()).hexdigest()
    assert sha == card["raster_sha256"]
    with rasterio.open(H48_TIF) as ds:
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert ds.shape == (3730, 3292)
        assert str(ds.crs) == "EPSG:32611"
        assert ds.nodata is None
        arr = ds.read(1)
    assert bool(np.isfinite(arr).all()) is True
    assert float(arr.min()) == 0.0
    assert float(arr.max()) == 1.0
    assert int((arr > 0).sum()) == 37_654

    with zipfile.ZipFile(H48_ZIP) as zf:
        tif_members = [m for m in zf.namelist() if m.lower().endswith(".tif")]
        assert tif_members == [H48_TIF.name]


def test_h48_runner_fails_closed_without_an_explicit_lane_assignment():
    env = dict(os.environ)
    env.pop("GEMSDOE32_ASSIGNED_LANE_ID", None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_h48_fbgr.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "no explicit H48-1-FBGR method paragraph" in result.stderr
