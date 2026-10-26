"""H46 TRHV artifact/provenance contract and its reusable low-level point-import primitives."""
from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from pyproj import CRS, Transformer

from gems32 import trhv

ROOT = Path(__file__).resolve().parents[1]
H46_STEM = "gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275"
H46_TIF = ROOT / "docs" / "downloads" / f"{H46_STEM}-zeros.tif"
H46_ZIP = ROOT / "docs" / "downloads" / f"{H46_STEM}-zeros.zip"
H46_AUDIT = ROOT / "docs" / "downloads" / f"{H46_STEM}-audit.json"
H46_CARD = ROOT / "evidence" / "h46_trhv_run_card.json"
EXPECTED_SHA = "9f42346d3acecb8d873fb35c70d988ae0afeb99781c6104c644d8cf9f85e0dc3"


def _shp_header(file_length_bytes: int) -> bytes:
    h = bytearray(100)
    struct.pack_into(">i", h, 0, 9994)
    struct.pack_into(">i", h, 24, file_length_bytes // 2)
    struct.pack_into("<ii", h, 28, 1000, 1)
    return bytes(h)


def _dbf_bytes(records: list[dict[str, str]]) -> bytes:
    fields = [("F2mDAB", "C", 8), ("T2m", "C", 8)]
    header_len = 32 + 32 * len(fields) + 1
    record_len = 1 + sum(length for _, _, length in fields)
    b = bytearray(header_len)
    b[0] = 3
    struct.pack_into("<IHH", b, 4, len(records), header_len, record_len)
    pos = 32
    for name, kind, length in fields:
        desc = bytearray(32)
        desc[:len(name)] = name.encode("ascii")
        desc[11] = ord(kind)
        desc[16] = length
        b[pos:pos+32] = desc
        pos += 32
    b[pos] = 0x0D
    for row in records:
        b.extend(b" ")
        for name, _, length in fields:
            val = str(row.get(name, "")).encode("ascii")[:length]
            b.extend(val.ljust(length, b" "))
    b.extend(b"\x1a")
    return bytes(b)


def _write_point_zip(path: Path, points: list[tuple[float, float]], records: list[dict[str, str]], epsg=4269):
    shp_records = []
    for i, (x, y) in enumerate(points, 1):
        content = struct.pack("<i2d", 1, x, y)
        shp_records.append(struct.pack(">2i", i, len(content)//2) + content)
    shp = _shp_header(100 + sum(map(len, shp_records))) + b"".join(shp_records)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("probe.shp", shp)
        zf.writestr("probe.dbf", _dbf_bytes(records))
        zf.writestr("probe.prj", CRS.from_epsg(epsg).to_wkt())


def test_point_shapefile_zip_parser_preserves_geometry_attributes_and_rejects_wrong_crs(tmp_path):
    path = tmp_path / "probes.zip"
    _write_point_zip(
        path,
        [(-117.0, 39.0), (-118.0, 40.0)],
        [{"F2mDAB": "2.5", "T2m": "18.0"}, {"F2mDAB": "-1.0", "T2m": "20.0"}],
    )
    x, y, attrs = trhv.read_point_shapefile_zip(path)
    assert x.tolist() == pytest.approx([-117.0, -118.0])
    assert y.tolist() == pytest.approx([39.0, 40.0])
    assert attrs[0]["F2mDAB"] == "2.5"
    assert attrs[1]["T2m"] == "20.0"

    bad = tmp_path / "bad-crs.zip"
    _write_point_zip(bad, [(-117.0, 39.0)], [{"F2mDAB": "2.5", "T2m": "18.0"}], epsg=4326)
    with pytest.raises(ValueError, match="EPSG:4269"):
        trhv.read_point_shapefile_zip(bad)


def test_project_points_to_exact_template_grid():
    transform = from_origin(243350.0, 4508550.0, 100.0, 100.0)
    to_geo = Transformer.from_crs("EPSG:32611", "EPSG:4269", always_xy=True)
    lon, lat = to_geo.transform(243350.0 + 25 * 100 + 50, 4508550.0 - 18 * 100 - 50)
    row, col, keep = trhv._project_points_to_grid(
        np.array([lon]), np.array([lat]), transform, (64, 64)
    )
    assert keep.tolist() == [True]
    assert row.tolist() == [18]
    assert col.tolist() == [25]


def test_paleo_deposit_weights_downweight_shoreline_tufa():
    assert trhv._deposit_hydrothermal_weight("Sinter") == 1.0
    assert trhv._deposit_hydrothermal_weight("silicified zone") == 1.0
    assert trhv._deposit_hydrothermal_weight("Travertine") == 0.80
    assert trhv._deposit_hydrothermal_weight("Tufa") == 0.35


def test_completed_h46_run_card_is_negative_complete_and_hash_bound():
    card = json.loads(H46_CARD.read_text())
    assert card["candidate_id"] == "H46-1-TRHV"
    assert card["experiments_used"] == 3 == card["experiments_budget_cap"]
    assert card["weekly_slots_used"] == 0
    assert card["leakage_canary"]["passed"] is True
    assert card["leakage_canary"]["n_features_tested"] == 63
    assert card["leakage_canary"]["max_oriented_auc"] <= 0.90
    assert card["holdout_dti"]["primary_hide_and_recover"]["evaluator_version"] == "GEMSDOE32-HIDE-RECOVER-v3.0"
    assert card["holdout_dti"]["primary_hide_and_recover"]["n_withheld_positives"] == 22_232
    assert card["holdout_dti"]["point_delta_vs_repository_best_h38"] < 0
    assert card["holdout_dti"]["paired_delta_vs_repository_best_h38"] is None
    assert card["protocol_audit"]["assigned_single_method_paragraph_present_in_prompt_context"] is False
    assert len(card["protocol_audit"]["preregistration_deviations"]) >= 3
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert len(card["submission_note"]) <= 140
    assert card["raster_sha256"] == EXPECTED_SHA


def test_h46_saved_bytes_pass_format_but_fail_literal_release_gate():
    assert H46_TIF.is_file() and H46_ZIP.is_file() and H46_AUDIT.is_file()
    assert hashlib.sha256(H46_TIF.read_bytes()).hexdigest() == EXPECTED_SHA
    with rasterio.open(H46_TIF) as ds:
        arr = ds.read(1)
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert str(ds.crs) == "EPSG:32611"
        assert ds.shape == (3730, 3292)
        assert ds.transform == from_origin(243350, 4508550, 100, 100)
        assert ds.nodata is None
    assert np.isfinite(arr).all()
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int((arr > 0).sum()) == 37_654

    with zipfile.ZipFile(H46_ZIP) as zf:
        tif_members = [n for n in zf.namelist() if n.lower().endswith(".tif")]
        assert tif_members == [H46_TIF.name]

    card = json.loads(H46_CARD.read_text())
    gates = card["release_gate_decision"]["gates"]
    assert gates["format"] is True
    assert gates["surface"] is True
    assert gates["final"] is False
    assert gates["holdout_vs_repository_best"] is False
    assert gates["paired_improvement_vs_repository_best"] is False
    assert gates["lane"] is False
    assert card["correlation_and_overlap_vs_registry"]["literal_all_rasters_final_passed"] is False


def test_focus_site_winner_overlap_receipt_proves_literal_70_percent_stop():
    receipt = json.loads((ROOT / "evidence" / "focus_site_winner_overlap_20261026.json").read_text())
    assert len(receipt["historical_winners"]) == 9
    assert receipt["minimum_pairwise_directional_overlap"] > 0.70
    exact = {tuple(row["pair"]): row for row in receipt["exact_mask_relations"]}
    assert exact[("GEMSDOE25", "GEMSDOE30")]["xor_positive_pixels"] == 0
    assert exact[("GEMSDOE31", "GEMSDOE32")]["xor_positive_pixels"] == 2545
    assert exact[("GEMSDOE32", "GEMSDOE36")]["xor_positive_pixels"] == 1200


def test_h46_runner_fails_closed_without_an_explicit_lane_assignment():
    env = dict(os.environ)
    env.pop("GEMSDOE32_ASSIGNED_LANE_ID", None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_h46_trhv.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "no explicit H46-1-TRHV method paragraph" in result.stderr


def test_current_status_and_rendered_site_identify_h46_as_research_only():
    status = json.loads((ROOT / "registry" / "current_status.json").read_text())
    assert status["any_file_ok_to_submit"] is False
    card_file = json.loads(H46_CARD.read_text())["artifacts"]["primary_zeros_tif"]
    # H46 stays a research-only artifact; a later session (H47) may own newest_unique, but nothing is cleared.
    h46 = status.get("h46_candidate") or status["newest_unique"]
    assert h46["file"] == card_file
    assert h46["ok_to_download"] is True
    assert h46["ok_to_submit"] is False
    assert status["newest_unique"]["ok_to_submit"] is False
    for rel in ("README.md", "docs/index.html", "docs/executive-summary.html", "index.html"):
        text = (ROOT / rel).read_text()
        assert "DO NOT SUBMIT" in text
        assert "H46" in text
        assert Path(card_file).name in text
