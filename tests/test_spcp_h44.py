"""CI-safe unit and artifact-integrity tests for H44-1 (SPCP + SAR-PU)."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from gems32.spcp import (
    OBSERVABILITY_INDICES_IN_BASE,
    OBSERVABILITY_INDICES_IN_EXTRA,
    SPCP_EXTRA_CHANNELS,
    fit_predict_naive_binary,
    fit_predict_sarpu_spcp,
    principal_negative_curvature_and_strike,
    principal_positive_trough_curvature,
)

ROOT = Path(__file__).resolve().parents[1]
H44_STEM = "gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a"
H44_ZEROS = ROOT / "docs" / "downloads" / f"{H44_STEM}-zeros.tif"
H44_NAN = ROOT / "docs" / "downloads" / f"{H44_STEM}-nan.tif"
H44_ZIP = ROOT / "docs" / "downloads" / f"{H44_STEM}-zeros.zip"
H44_AUDIT = ROOT / "docs" / "downloads" / f"{H44_STEM}-audit.json"
H44_SHA256 = "386a4aad59a5c742b28541835892f9f6e0cb306cbbe4e296741bbad8e4bff235"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_spcp_channel_catalog_has_20_unique_names() -> None:
    assert len(SPCP_EXTRA_CHANNELS) == 20
    assert len(set(SPCP_EXTRA_CHANNELS)) == 20
    assert all(0 <= idx < 35 for idx in OBSERVABILITY_INDICES_IN_BASE)
    assert all(0 <= idx < 20 for idx in OBSERVABILITY_INDICES_IN_EXTRA)


def test_phillips_curvature_crest_and_trough_recover_synthetic_anomalies() -> None:
    _, xx = np.mgrid[0:64, 0:64].astype(np.float32)
    # North-south horizontal-gradient ridge centered at col x = 32
    ridge = np.exp(-0.5 * ((xx - 32.0) / 2.2) ** 2).astype(np.float32)
    crest, theta = principal_negative_curvature_and_strike(ridge, sigma=1.5)
    assert crest.shape == (64, 64) and crest.dtype == np.float32
    assert theta.shape == (64, 64) and theta.dtype == np.float32
    assert float(crest[32, 32]) > 5.0 * float(crest[32, 16]) + 1e-4
    # Ridge runs along row-axis (N-S => strike angle near +/-pi/2 => |sin(theta)| near 1)
    assert abs(float(np.sin(theta[32, 32]))) > 0.95

    # Hydrothermal demagnetization trough (-ridge) must peak in positive trough curvature
    trough = principal_positive_trough_curvature(-ridge, sigma=1.5)
    assert trough.shape == (64, 64) and trough.dtype == np.float32
    assert float(trough[32, 32]) > 5.0 * float(trough[32, 16]) + 1e-4


def test_sarpu_recovers_blind_positives_suppressed_by_naive_binary() -> None:
    rng = np.random.default_rng(20261026)
    h, w = 80, 80
    base = rng.normal(0.0, 0.25, size=(h, w, 35)).astype(np.float32)
    extra = rng.uniform(0.0, 0.25, size=(h, w, 20)).astype(np.float32)

    # Subsurface fault physics present everywhere f_phys > 1.0, regardless of surface exposure
    f_phys = rng.normal(0.0, 1.0, size=(h, w)).astype(np.float32)
    exposure = rng.uniform(0.0, 1.0, size=(h, w)).astype(np.float32)
    base[:, :, 0] = f_phys
    # Populate observability indices with surface exposure (high in exposed ranges, low in blind basins)
    for b_idx in OBSERVABILITY_INDICES_IN_BASE:
        base[:, :, b_idx] = exposure
    for e_idx in OBSERVABILITY_INDICES_IN_EXTRA:
        extra[:, :, e_idx] = exposure
    # Unsupervised multi-physics composite tracks subsurface fault physics
    extra[:, :, -1] = 1.0 / (1.0 + np.exp(-2.0 * f_phys)).astype(np.float32)

    true_fault = f_phys > 1.0
    # Catalogue only observes faults where surface exposure is high (SAR-PU mapping bias)
    visible_faults = true_fault & (exposure > 0.65)
    foot = np.ones((h, w), dtype=bool)

    p_naive = fit_predict_naive_binary(
        base, extra, foot, visible_faults, foot, seed=11, neg_halo_px=1.0, max_pos=2000
    )
    p_sarpu, e_pred = fit_predict_sarpu_spcp(
        base, extra, foot, visible_faults, foot, foot, seed=11, neg_halo_px=1.0, max_pos=2000
    )
    blind_pos = true_fault & (exposure < 0.25)
    blind_bg = (~true_fault) & (exposure < 0.25)
    assert np.isfinite(p_sarpu).all() and np.isfinite(e_pred).all()
    lift_sarpu = float(p_sarpu[blind_pos].mean() - p_sarpu[blind_bg].mean())
    lift_naive = float(p_naive[blind_pos].mean() - p_naive[blind_bg].mean())
    assert lift_sarpu > lift_naive + 0.05


def test_h44_geotiff_bundle_passes_strict_submission_spec() -> None:
    for p in (H44_ZEROS, H44_NAN, H44_ZIP, H44_AUDIT):
        assert p.exists(), f"Missing H44 artifact: {p}"
    assert _sha256(H44_ZEROS) == H44_SHA256

    with rasterio.open(H44_ZEROS) as ds:
        assert ds.count == 1
        assert (ds.height, ds.width) == (3730, 3292)
        assert ds.dtypes[0] == "float32"
        assert str(ds.crs) == "EPSG:32611"
        assert ds.nodata is None
        arr = ds.read(1)

    assert np.isfinite(arr).all(), "Primary -zeros.tif must have 0 NaN/Inf across entire grid"
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int((arr > 0.5).sum()) == 37654

    with zipfile.ZipFile(H44_ZIP) as zf:
        tif_members = [m for m in zf.namelist() if m.lower().endswith(".tif")]
        assert tif_members == [H44_ZEROS.name]

    audit = json.loads(H44_AUDIT.read_text())
    assert all(audit["zeros_tif"]["checks"].values())
    assert audit["zeros_tif"]["sha256"] == H44_SHA256
    assert audit["zeros_tif"]["on_catalogue_positive_pixels"] == 0


def test_h44_run_card_and_experiments_match_fail_closed_protocol() -> None:
    rc_ev = json.loads((ROOT / "evidence" / "h44_spcp_run_card.json").read_text())
    rc_web = json.loads((ROOT / "docs" / "data" / "h44_spcp_run_card.json").read_text())
    assert rc_ev == rc_web

    required = {
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
    }
    assert required.issubset(rc_ev.keys())
    assert rc_ev["verdict"] == "negative"
    assert rc_ev["ok_to_submit"] is False
    assert rc_ev["raster_sha256"] == H44_SHA256
    assert 1 <= len(rc_ev["submission_note"]) <= 140
    assert "DO NOT SUBMIT" in rc_ev["submission_note"]
    assert rc_ev["validator_output"]["strict_cli_check_submission"]["passed"] is True
    assert rc_ev["validator_output"]["audit_geotiff_13_checks_passed"] is True
    assert rc_ev["leakage_canary"]["passed"] is True
    assert rc_ev["leakage_canary"]["max_oriented_auc"] <= 0.90

    uniq = rc_ev["correlation_and_overlap_vs_registry"]
    assert uniq["genuine_pre_placement_surface_passed"] is True
    assert uniq["genuine_final_dots_passed"] is True
    assert uniq["max_abs_surface_spearman"] <= 0.90
    assert uniq["max_genuine_3px_dot_overlap"] <= 0.70
    assert uniq["literal_all_rasters_final_passed"] is False

    # Paired spatial-block bootstrap CI on blind off-catalogue SGMC-cal must be strictly > 0
    ci = rc_ev["holdout_dti"]["paired_sgmc_calibrated_delta_vs_02778_champion"]["ci95"]
    assert ci[0] > 0.0 and ci[1] > ci[0]

    audit9 = json.loads((ROOT / "evidence" / "nine_site_live_audit_20261026.json").read_text())
    expected_sites = {f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36)}
    assert {row["repo"] for row in audit9["sites"]} == expected_sites


def test_site_and_readme_preserve_h44_history_without_promoting_upload() -> None:
    # H44 is historical. Requiring every old candidate in the first 6000 chars
    # prevents an accurate current decision from replacing a stale release banner.
    readme = (ROOT / "README.md").read_text()
    assert H44_STEM in readme
    current = json.loads((ROOT / "registry/current_status.json").read_text())
    assert current["newest_unique"]["file"] in readme[:6000]
    assert "DO NOT SUBMIT" in readme[:6000]

    for rel in ("docs/index.html", "docs/executive-summary.html"):
        html = (ROOT / rel).read_text()
        assert H44_STEM in html
        assert "DO NOT SUBMIT" in html
        assert "OK TO DOWNLOAD AND SUBMIT" not in html
