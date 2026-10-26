from __future__ import annotations

import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from gems32.submission import sha256_file

ROOT = Path(__file__).resolve().parents[1]


def test_round6_run_card_and_protocol_contract():
    rc_path = ROOT / "evidence" / "h36_tdr_pds_run_card.json"
    latest_path = ROOT / "docs" / "data" / "latest-run-card.json"
    assert rc_path.is_file() and latest_path.is_file()

    rc = json.loads(rc_path.read_text())
    latest = json.loads(latest_path.read_text())
    status = json.loads((ROOT / "registry" / "current_status.json").read_text())
    assert status["any_file_ok_to_submit"] is False
    assert latest["verdict"] == "negative"
    assert "hypothesis" in latest and "raster_sha256" in latest

    # Required Parallel-Run Protocol Rule 7 fields
    for k in (
        "hypothesis",
        "mechanism",
        "named_non_fault_mimic",
        "holdout_dti",
        "correlation_and_overlap_vs_registry",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "submission_note",
        "verdict",
    ):
        assert k in rc and rc[k], f"Missing required run card field: {k}"

    assert rc["experiments_used"] <= 3
    assert rc["weekly_slots_used"] == 0
    assert len(rc["submission_note"]) <= 140
    assert rc["verdict"] == "negative"
    assert rc["download_ok"] is True
    assert rc["ok_to_submit"] is False

    # Leakage canary <= 0.90
    assert rc["leakage_canary"]["passed"] is True
    assert rc["leakage_canary"]["max_oriented_auc"] <= 0.90

    # Holdout DTI label + evaluator version + withheld count + 95% CI
    h = rc["holdout_dti"]
    assert h["metric_label"] == "HOLDOUT-DTI"
    assert h["evaluator_version"] == "GEMSDOE32-HOLDOUT-v3-visible-gated"
    prim = h["primary_visible_gated_pooled"]
    assert prim["n_withheld_positives"] == 22232
    assert prim["ci95"][0] <= prim["dti"] <= prim["ci95"][1]

    # Genuine 44-raster uniqueness passed; literal calibration lattice triggered fail-closed negative
    u = rc["correlation_and_overlap_vs_registry"]
    assert u["genuine_surface_gate_passed"] is True
    assert u["genuine_max_abs_surface_spearman"] <= 0.90
    assert u["genuine_final_dot_gate_passed"] is True
    assert u["genuine_max_dot_overlap_within_3px"] <= 0.70


def test_round6_unique_geotiff_and_zip_portal_ready():
    rc = json.loads((ROOT / "evidence" / "h36_tdr_pds_run_card.json").read_text())
    st = json.loads((ROOT / "registry" / "current_status.json").read_text())["newest_unique"]

    tif_path = ROOT / rc["artifacts"]["primary_zeros_tif"]
    nan_path = ROOT / rc["artifacts"]["nan_companion_tif"]
    zip_path = ROOT / rc["artifacts"]["zip_archive"]

    assert tif_path.is_file() and nan_path.is_file() and zip_path.is_file()
    # H36 remains an archived negative artifact; the current latest candidate is H46.
    assert st["file"] != rc["artifacts"]["primary_zeros_tif"]
    assert sha256_file(tif_path) == rc["raster_sha256"]

    with rasterio.open(tif_path) as ds:
        assert str(ds.crs) == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert ds.nodata is None
        arr = ds.read(1)

    assert arr.size == 12_279_160
    assert int(np.isfinite(arr).sum()) == 12_279_160
    assert int(np.isnan(arr).sum()) == 0
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int((arr > 0).sum()) == 37_654

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert names == [tif_path.name]


def test_no_contradictory_promote_banners_on_site_or_readme():
    for rel in ("index.html", "docs/index.html", "docs/executive-summary.html"):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        assert "OK TO DOWNLOAD AND SUBMIT" not in txt, f"Contradictory banner remains in {rel}"
        assert "GEMSDOE32-GEO-CONDUIT-2D0D0C5E" not in txt, f"Stale hardcoded conduit ID in {rel}"

    readme_active = (ROOT / "README.md").read_text(encoding="utf-8").split("<details>")[0]
    assert "OK TO DOWNLOAD AND SUBMIT" not in readme_active
    assert "GEMSDOE32-GEO-CONDUIT-2D0D0C5E" not in readme_active
