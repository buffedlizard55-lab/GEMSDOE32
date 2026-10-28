"""End-to-end automated regression tests for H51-1-EWSP deliverables, GeoTIFF bytes, Run Card, and Pages UI."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

from gems32.byte_audit import inspect_saved_raster

ROOT = Path(__file__).resolve().parents[1]

H51_TIF_REL = "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif"
H51_ZIP_REL = "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.zip"
H51_NAN_REL = "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-nan.tif"
H51_AUD_REL = "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-audit.json"
H51_SHA256 = "f66f65e469deda8ab34c380f46ffd2af23feb95a0ac45230f9829d2950651740"


def test_h51_geotiff_bytes_are_strictly_portal_valid_without_human_intervention() -> None:
    tif_path = ROOT / H51_TIF_REL
    assert tif_path.is_file()
    assert (ROOT / H51_ZIP_REL).is_file()
    assert (ROOT / H51_NAN_REL).is_file()
    assert (ROOT / H51_AUD_REL).is_file()
    assert hashlib.sha256(tif_path.read_bytes()).hexdigest() == H51_SHA256

    measured = inspect_saved_raster(tif_path)
    assert measured["strict_primary_passed"] is True
    assert measured["single_band_float32"] is True
    assert measured["crs"] == "EPSG:32611"
    assert measured["shape"] == [3730, 3292]
    assert measured["nodata"] is None
    assert measured["finite_cells"] == 12279160
    assert measured["total_cells"] == 12279160
    assert measured["min"] == 0.0
    assert measured["max"] == 1.0
    assert measured["positive_pixels"] == 37654

    with rasterio.open(tif_path) as ds:
        arr = ds.read(1)
        assert arr.dtype == np.float32
        assert np.isfinite(arr).all()
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
        uniq_vals = set(np.unique(arr).tolist())
        assert uniq_vals == {0.0, 1.0}


def test_h51_run_card_protocol_fields_and_discrete_uniqueness() -> None:
    rc_path = ROOT / "evidence" / "h51_ewsp_run_card.json"
    assert rc_path.is_file()
    rc = json.loads(rc_path.read_text())

    # Required Protocol Rule 5 Run Card fields
    for key in (
        "hypothesis",
        "mechanism",
        "named_non_fault_mimic_process",
        "holdout_dti",
        "correlation_and_overlap_vs_registry",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "submission_note",
        "verdict",
    ):
        assert key in rc, f"Missing Run Card key: {key}"

    assert rc["raster_sha256"] == H51_SHA256
    assert rc["verdict"] == "negative"
    assert rc["ok_to_submit"] is False
    assert rc["experiments_used"] == 3
    assert rc["weekly_slots_used"] == 0
    assert 1 <= len(rc["submission_note"]) <= 140

    # Leakage canary Rule 4
    assert rc["leakage_canary"]["passed"] is True
    assert rc["leakage_canary"]["n_features_tested"] == 45
    assert rc["leakage_canary"]["max_oriented_auc"] <= 0.90

    # Strict Holdout Rule 3 labeling & paired win vs 0.2778 Champion
    hr = rc["holdout_dti"]["primary_hide_and_recover"]
    inc = rc["holdout_dti"]["incumbent_02778_same_evaluator"]
    paired = rc["holdout_dti"]["paired_delta_vs_02778_champion"]
    assert hr["label"] == "HOLDOUT-DTI"
    assert hr["evaluator_version"] == "GEMSDOE32-HIDE-RECOVER-v3.0"
    assert hr["n_withheld_positives"] == 22232
    assert hr["pooled_dti"] > inc["pooled_dti"]
    assert paired["ci95"][0] > 0.0

    # Uniqueness Rule 1 across all 610 discrete <=100k detector rasters
    uq = rc["correlation_and_overlap_vs_registry"]
    assert uq["n_genuine_rasters_checked"] >= 600
    assert uq["genuine_pre_placement_surface_passed"] is True
    assert uq["max_abs_surface_spearman"] <= 0.90
    assert uq["genuine_final_dots_passed"] is True
    assert uq["max_genuine_3px_dot_overlap"] <= 0.70
    assert uq["max_focus_site_3px_dot_overlap"] <= 0.70
    assert uq["literal_all_rasters_final_passed"] is False


def test_registry_timestamps_are_monotonic_and_pages_feature_h51_at_top() -> None:
    status = json.loads((ROOT / "registry" / "current_status.json").read_text())
    release = json.loads((ROOT / "evidence" / "current_release_review.json").read_text())
    build = json.loads((ROOT / "registry" / "submission_build.json").read_text())

    built_utc = status["newest_unique"]["built_utc"]
    updated_utc = status["updated_utc"]
    reviewed_utc = release["reviewed_utc"]
    assert reviewed_utc >= updated_utc >= built_utc
    assert build["sync"]["synced_utc"] == reviewed_utc
    assert status["leaderboard_top"]["score"] == 0.4544

    tif_name = Path(H51_TIF_REL).name
    for rel in ("docs/index.html", "docs/executive-summary.html", "docs/nine-site-review.html", "index.html"):
        text = (ROOT / rel).read_text()
        assert "DO NOT SUBMIT" in text
        assert tif_name in text
        if rel in ("docs/index.html", "docs/executive-summary.html"):
            assert "0.4544" in text
            # Top-of-page header notice must contain both DO NOT SUBMIT and the direct H51 download link
            header_slice = text[:4500]
            assert "DO NOT SUBMIT" in header_slice
            assert tif_name in header_slice
