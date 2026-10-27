"""Unit and saved-artifact verification tests for Session H47-1 (LDGI-WCR)."""

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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import ldgi  # noqa: E402

H47_CARD = ROOT / "evidence" / "h47_ldgi_run_card.json"
H47_EXPS = ROOT / "evidence" / "h47_ldgi_experiments.json"
H47_TIF = (
    ROOT
    / "docs"
    / "downloads"
    / "gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif"
)
H47_ZIP = (
    ROOT
    / "docs"
    / "downloads"
    / "gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.zip"
)


def test_ldgi_completeness_ratio_and_adaptive_fraction_law():
    foot = np.ones((20, 20), dtype=bool)
    rho_lin = np.full((20, 20), 0.5, dtype=np.float32)  # sum = 200.0
    vis_uncensored = np.zeros((20, 20), dtype=bool)
    vis_uncensored.ravel()[:16] = True  # 16 / 200 = 0.080
    eta_unc = ldgi.compute_lineament_completeness_eta(vis_uncensored, foot, rho_lin=rho_lin)
    f_a_unc, w_s1_unc = ldgi.compute_adaptive_stage1_fraction(eta_unc)
    assert np.isclose(eta_unc, 0.08)
    assert np.isclose(f_a_unc, 0.50)
    assert np.isclose(w_s1_unc, 0.08)

    vis_censored = np.zeros((20, 20), dtype=bool)
    vis_censored.ravel()[:12] = True  # 12 / 200 = 0.060
    eta_cen = ldgi.compute_lineament_completeness_eta(vis_censored, foot, rho_lin=rho_lin)
    f_a_cen, w_s1_cen = ldgi.compute_adaptive_stage1_fraction(eta_cen)
    assert np.isclose(eta_cen, 0.06)
    assert np.isclose(f_a_cen, 0.92)
    assert np.isclose(w_s1_cen, 0.85)


def test_emit_dual_horizon_ldgi_enforces_b2_disjoint_stages_and_budget():
    rng = np.random.default_rng(47)
    shape = (48, 48)
    foot = np.ones(shape, dtype=bool)
    vis = np.zeros(shape, dtype=bool)
    vis[24, 10:38] = True
    s1 = rng.uniform(0.1, 1.0, size=shape).astype(np.float32)
    crest_b = rng.uniform(0.1, 1.0, size=shape).astype(np.float32)
    elig = foot.copy()

    dots_ab, meta = ldgi.emit_dual_horizon_ldgi(
        s1,
        crest_b,
        vis,
        elig,
        foot,
        eta=0.078381,
        budget=40,
        off_cat_min_dist_px=4.0,
        support_mult=5,
    )
    assert dots_ab.shape == shape
    assert int(dots_ab.sum()) == 40
    assert meta["stage1_dots"] + meta["stage2_added_dots"] == 40
    assert meta["stage1_dots"] > 0 and meta["stage2_added_dots"] > 0
    assert not bool((dots_ab & vis).any())


def test_h47_run_card_and_saved_geotiff_pass_all_automated_checks():
    assert H47_CARD.is_file()
    assert H47_EXPS.is_file()
    assert H47_TIF.is_file()
    assert H47_ZIP.is_file()

    card = json.loads(H47_CARD.read_text())
    assert card["schema_version"] == "gems-parallel-runcard-v3"
    assert card["candidate_id"] == "H47-1-LDGI"
    assert card["experiments_used"] == 3
    assert card["experiments_budget_cap"] == 3
    assert card["weekly_slots_used"] == 0
    assert card["leakage_canary"]["passed"] is True
    assert card["leakage_canary"]["n_features_tested"] == 71
    assert card["leakage_canary"]["max_oriented_auc"] <= 0.90
    assert len(card["submission_note"]) <= 140

    # Verify holdout superiority over both 0.2778 Champion and H38 point estimate
    hd = card["holdout_dti"]
    assert hd["exp2_exposed71_hide_and_recover"]["pooled_dti"] > hd["repository_best_h38_same_evaluator"]["pooled_dti"]
    assert hd["primary_hide_and_recover"]["pooled_dti"] > hd["repository_best_h38_same_evaluator"]["pooled_dti"]
    assert hd["paired_delta_vs_02778_champion"]["ci95"][0] > 0.0
    assert hd["off_catalogue_sgmc"]["prevalence_calibrated_dti"] > hd["incumbent_02778_sgmc"]["prevalence_calibrated_dti"]

    # Verify genuine registry uniqueness pass
    un = card["correlation_and_overlap_vs_registry"]
    assert un["genuine_pre_placement_surface_passed"] is True
    assert un["genuine_final_dots_passed"] is True
    assert un["max_abs_surface_spearman"] <= 0.90
    assert un["max_genuine_3px_dot_overlap"] <= 0.70
    assert un["literal_all_rasters_final_passed"] is False

    # Verify fail-closed verdict
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["download_for_research_ok"] is True

    # Verify saved GeoTIFF bytes on disk
    sha = hashlib.sha256(H47_TIF.read_bytes()).hexdigest()
    assert sha == card["raster_sha256"]
    with rasterio.open(H47_TIF) as ds:
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

    with zipfile.ZipFile(H47_ZIP) as zf:
        tif_members = [m for m in zf.namelist() if m.lower().endswith(".tif")]
        assert tif_members == [H47_TIF.name]


def test_h47_runner_fails_closed_without_an_explicit_lane_assignment():
    env = dict(os.environ)
    env.pop("GEMSDOE32_ASSIGNED_LANE_ID", None)
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_h47_ldgi.py")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "no explicit H47-1-LDGI method paragraph" in result.stderr


def test_current_status_and_rendered_site_identify_h47_as_research_artifact():
    """The current newest candidate must remain fail-closed research-only, and H47-1 stays archived."""
    status = json.loads((ROOT / "registry" / "current_status.json").read_text())
    assert status["any_file_ok_to_submit"] is False
    newest = status["newest_unique"]
    assert newest["ok_to_download"] is True
    assert newest["ok_to_submit"] is False
    assert (ROOT / newest["file"]).is_file()
    card_file = json.loads(H47_CARD.read_text())["artifacts"]["primary_zeros_tif"]
    assert (ROOT / card_file).is_file()
    for rel in ("README.md", "docs/index.html", "docs/executive-summary.html", "index.html"):
        text = (ROOT / rel).read_text()
        assert "DO NOT SUBMIT" in text
        assert Path(newest["file"]).name in text
    for rel in ("README.md", "docs/index.html"):
        assert "H47-1" in (ROOT / rel).read_text()
