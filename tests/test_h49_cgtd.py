"""Unit and saved-artifact verification tests for Session H49-1-CGTD."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import cgtd, submission  # noqa: E402

H49_CARD = ROOT / "evidence" / "h49_cgtd_run_card.json"
H49_EXPS = ROOT / "evidence" / "h49_cgtd_experiments.json"
H49_AUDIT9 = ROOT / "evidence" / "nine_site_refreshed_audit_20261027.json"
H49_FORENSICS = ROOT / "evidence" / "livescore_forensics_20261027.json"
H49_TIF = (
    ROOT
    / "docs"
    / "downloads"
    / "gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.tif"
)
H49_ZIP = (
    ROOT
    / "docs"
    / "downloads"
    / "gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.zip"
)


def test_msub_93_col_indices_strictly_exclude_all_13_lidar_channels():
    """Verify M_Sub has exactly 80 channels and excludes all 13 1 m LiDAR-dependent cols."""
    assert len(cgtd.CGTD_EXTRA_CHANNELS) == 10
    assert len(cgtd.MSUB_93_COL_INDICES) == 80
    assert len(cgtd.LIDAR_DEPENDENT_GLOBAL_COLS_93) == 13
    assert set(cgtd.MSUB_93_COL_INDICES).isdisjoint(cgtd.LIDAR_DEPENDENT_GLOBAL_COLS_93)
    assert len(cgtd.MSUB_93_COL_INDICES) + len(cgtd.LIDAR_DEPENDENT_GLOBAL_COLS_93) == 93


def test_geothermometry_disequilibrium_projects_up_gradient_and_drops_catalogue_column():
    """Cold spring with high chalcedony/quartz geothermometer projects up-slope & drops dist_known_fault_px."""
    yy, xx = np.mgrid[0:64, 0:64].astype(np.float32)
    foot = np.ones((64, 64), dtype=bool)
    # Structural elevation rises toward +x (East range block); deep basin toward -x (West playa).
    det_elev = (1200.0 + 18.0 * xx).astype(np.float32)
    depth_base = np.maximum(800.0 - 12.0 * xx, 20.0).astype(np.float32)
    struct_wall = np.full((64, 64), 0.75, dtype=np.float32)
    playa_gate = np.ones((64, 64), dtype=np.float32)

    with tempfile.TemporaryDirectory() as tmpdir:
        ddir = Path(tmpdir)
        ext = ddir / "external"
        ext.mkdir(parents=True, exist_ok=True)
        # Include `dist_known_fault_px` to verify _build_upgrad_geotherm_diseq drops it on load
        (ext / "gdr_wellspring_in_footprint.csv").write_text(
            "row,col,temp_c,geothermquartz_c,geothermchalc_c,geothermcat_c,dist_known_fault_px\n"
            "32,32,20.0,155.0,148.0,140.0,0.0\n"
        )
        out, receipt = cgtd._build_upgrad_geotherm_diseq(
            ddir=ddir,
            det_elev=det_elev,
            depth_base=depth_base,
            struct_wall=struct_wall,
            playa_gate=playa_gate,
            foot=foot,
        )

    assert out.shape == (64, 64)
    assert np.isfinite(out).all()
    assert receipt["disequilibrium_gt_50c_stations"] == 1
    # Up-gradient (+x, col 38) receives strictly stronger disequilibrium plume than down-slope (-x, col 26)
    assert float(out[32, 38]) > float(out[32, 26])


def test_stationary_cgtd_tail_noisyor_rescues_blind_conduits_vs_multiplicative():
    """Tail Noisy-OR strictly rescues top-2% blind conduits where p_sup is small (~0.02)."""
    h, w = 80, 80
    foot = np.ones((h, w), dtype=bool)
    foot[0, :] = False  # verify outside-footprint zeroing
    visible = np.zeros((h, w), dtype=bool)
    visible[12:18, 20] = True

    p_sup = np.full((h, w), 0.02, dtype=np.float32)
    p_sup[10, :] = 0.55  # exposed range-front scarp sets realistic q99.35 anchor

    cgtd_stack = np.zeros((h, w, 10), dtype=np.float32)
    fbgr_stack = np.zeros((h, w, 12), dtype=np.float32)
    trhv_stack = np.zeros((h, w, 8), dtype=np.float32)
    trhv_stack[:, :, 4] = 1.0  # road-free everywhere

    # Sharp 1-px blind hydrothermal conduit along row 52, cols 25..55 (in top 2% of r_vent)
    cgtd_stack[52, 25:55, 9] = 0.98
    cgtd_stack[52, 25:55, 8] = 0.95
    fbgr_stack[52, 25:55, 11] = 0.92

    surf_mult = cgtd.build_stationary_cgtd_surface(
        p_sup=p_sup,
        cgtd_stack=cgtd_stack,
        fbgr_stack=fbgr_stack,
        trhv_stack=trhv_stack,
        visible_mask=visible,
        foot=foot,
        mode="multiplicative",
        sharpen_crest=False,
    )
    surf_or = cgtd.build_stationary_cgtd_surface(
        p_sup=p_sup,
        cgtd_stack=cgtd_stack,
        fbgr_stack=fbgr_stack,
        trhv_stack=trhv_stack,
        visible_mask=visible,
        foot=foot,
        mode="noisyor",
        lambda_vent=0.90,
        w_tip_relay=0.0,
        sharpen_crest=False,
    )

    assert np.isfinite(surf_mult).all() and np.isfinite(surf_or).all()
    assert float(surf_or.min()) >= 0.0 and float(surf_or.max()) <= 1.0
    assert float(surf_or[0, :].max()) == 0.0  # outside footprint stays exact 0
    # Background pixels (r_vent == 0) are UNTOUCHED by tail-activated Noisy-OR
    assert np.isclose(float(surf_or[35, 35]), float(p_sup[35, 35]), atol=1e-4)
    # Blind conduit crest (52, 40) is rescued well above multiplicative mode
    assert float(surf_or[52, 40]) > float(surf_mult[52, 40]) + 0.15


def test_saved_h49_cgtd_bundle_run_card_and_release_sync():
    """Verify exact SHA-256, 13/13 GeoTIFF checks, Run Card gates, and site/registry sync."""
    assert H49_TIF.is_file(), f"Missing {H49_TIF}"
    assert H49_ZIP.is_file(), f"Missing {H49_ZIP}"
    assert H49_CARD.is_file() and H49_EXPS.is_file() and H49_AUDIT9.is_file() and H49_FORENSICS.is_file()

    expected_sha = "4d8d7c051caf60fbd6cf24a4eceb8c921209a25225634fc54df143e5d8e511fd"
    actual_sha = hashlib.sha256(H49_TIF.read_bytes()).hexdigest()
    assert actual_sha == expected_sha

    tmpl = ROOT / ".cache" / "gems_data" / "sample_submission.tif"
    if tmpl.is_file():
        chk = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_submission.py"), "--strict-finite", str(H49_TIF)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert chk.returncode == 0, f"check_submission failed: {chk.stdout} {chk.stderr}"

    with rasterio.open(H49_TIF) as ds:
        assert ds.count == 1
        assert ds.dtypes == ("float32",)
        assert ds.shape == (3730, 3292)
        assert str(ds.crs) == "EPSG:32611"
        assert tuple(ds.transform)[:6] == (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
        assert ds.nodata is None
        arr = ds.read(1)
    assert bool(np.isfinite(arr).all()) is True
    assert float(arr.min()) == 0.0
    assert float(arr.max()) == 1.0
    assert int((arr > 0.5).sum()) == 37_654

    with zipfile.ZipFile(H49_ZIP) as zf:
        tif_members = [m for m in zf.namelist() if m.lower().endswith(".tif")]
        assert tif_members == [H49_TIF.name]

    rc = json.loads(H49_CARD.read_text())
    assert rc["raster_sha256"] == expected_sha
    assert rc["verdict"] == "negative"
    assert rc["ok_to_submit"] is False
    assert rc["download_for_research_ok"] is True
    assert rc["submission_note_length"] <= 140
    assert len(rc["submission_note"]) <= 140
    assert rc["leakage_canary"]["passed"] is True
    assert rc["leakage_canary"]["n_features_tested"] == 93
    assert rc["leakage_canary"]["max_oriented_auc"] <= 0.90

    hr = rc["holdout_dti"]["primary_hide_and_recover"]["pooled_dti"]
    sg = rc["holdout_dti"]["off_catalogue_sgmc"]["prevalence_calibrated_dti"]
    assert hr > 0.099202  # beats 0.2778 Champion on HIDE-RECOVER-v3.0
    assert sg > 0.064121  # beats 0.2778 Champion on blind off-catalogue SGMC-CAL-v3.0

    uq = rc["correlation_and_overlap_vs_registry"]
    assert uq["genuine_pre_placement_surface_passed"] is True
    assert uq["external_cross_site_unique_passed"] is True
    assert uq["max_external_cross_site_3px_dot_overlap"] <= 0.70
    assert uq["genuine_final_dots_passed"] is False  # 73.33% intra-repo vs H48-FBGR
    assert uq["literal_all_rasters_final_passed"] is False

    # Verify forensics receipt has all 19 audited rasters (15 live-scored + 4 unscored)
    forensics = json.loads(H49_FORENSICS.read_text())
    assert len(forensics["rasters"]) == 19
    assert sum(1 for r in forensics["rasters"] if r["live_score"] is not None) == 15

    # Verify fail-closed sync across status, submission_build, and current_release_review
    status = json.loads((ROOT / "registry" / "current_status.json").read_text())
    sub_b = json.loads((ROOT / "registry" / "submission_build.json").read_text())
    rel_rev = json.loads((ROOT / "evidence" / "current_release_review.json").read_text())
    assert status["any_file_ok_to_submit"] is False
    assert status["newest_unique"]["ok_to_submit"] is False
    assert sub_b["ok_to_submit"] is False
    assert rel_rev["submission_authorization"]["ok_to_download_and_submit"] is False
    if status.get("newest_unique", {}).get("run_card") == "evidence/h49_cgtd_run_card.json":
        assert sub_b["file"]["sha256"] == expected_sha
        assert rel_rev["artifact"]["sha256"] == expected_sha


def test_h49_runner_fails_closed_without_an_explicit_lane_assignment():
    env = dict(os.environ)
    env.pop("GEMSDOE32_ASSIGNED_LANE_ID", None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_h49_cgtd.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "H49-1-CGTD" in result.stderr
