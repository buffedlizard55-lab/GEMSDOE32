"""Comprehensive end-to-end verification tests for GEMSDOE32 (Passes 1, 2, and 3)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import rasterio

from gems32.metric import dti_binary, dti_bruteforce, dti_exact
from gems32.paths import ROOT, data_dir, docs_dir, downloads_dir, evidence_dir
from gems32.submission import audit_geotiff, sha256_file


def test_dti_exact_matches_bruteforce():
    rng = np.random.default_rng(32)
    foot = np.ones((48, 48), dtype=bool)
    foot[:4, :] = False
    pred = (rng.random((48, 48)) < 0.04) & foot
    gt = (rng.random((48, 48)) < 0.03) & foot

    fast = dti_binary(pred, gt, foot)
    exact = dti_exact(np.where(foot, pred.astype(np.float32), np.nan), gt.astype(np.float32), foot)
    brute = dti_bruteforce(pred.astype(np.float32), gt.astype(np.float32))

    assert abs(fast["dti"] - brute["dti"]) < 1e-9
    assert abs(exact["dti"] - brute["dti"]) < 1e-9
    assert abs(fast["tp"] - brute["tp"]) < 1e-9
    assert abs(fast["fp"] - brute["fp"]) < 1e-9


def test_data_restore_and_sentinel_sanitization_manifests():
    restore = json.loads((ROOT / "data" / "restore_receipt.json").read_text())
    assert restore["verified_files_count"] == 22
    assert all(f["status"] == "present" for f in restore["files"])

    prep = json.loads((ROOT / "data" / "prepared_manifest.json").read_text())
    assert prep["grid"]["epsg"] == 32611
    assert prep["grid"]["height"] == 3730
    assert prep["grid"]["width"] == 3292
    assert prep["counts"]["footprint_valid_pixels"] == 5_167_373
    assert prep["counts"]["positive_catalogue_label_pixels"] == 60_988
    assert prep["counts"]["total_sentinel_band_pixels_inside_footprint"] == 58_171
    assert len(prep["bands"]) == 19


def test_d28_forensic_autopsy_verified():
    autopsy = json.loads((evidence_dir() / "d28_forensic_autopsy.json").read_text())
    assert len(autopsy["verified_reproductions_pixel_identical"]) == 3
    for rep in autopsy["verified_reproductions_pixel_identical"]:
        assert rep["leaderboard_dti"] == 0.2600
        assert rep["emitted_pixels"] == 44_090
        assert rep["max_abs_diff_vs_ref"] == 0.0

    chain = autopsy["ablation_chain_h19_5_to_d15_to_d28"]
    assert chain["H19-5-Dense-Backbone"]["emitted_pixels"] == 121_131
    assert chain["D1.5-Thinned-H19-5"]["emitted_pixels"] == 60_069
    assert chain["D2.8-Poisson300m-Ref"]["emitted_pixels"] == 44_090
    assert chain["D1.5-Thinned-H19-5"]["strict_subset_of_h19_5"] is True
    assert chain["D2.8-Poisson300m-Ref"]["strict_subset_of_h19_5"] is True


def test_bo_surrogate_and_holdout_improvements():
    log_json = json.loads((ROOT / "data" / "holdout_surrogate_log.json").read_text())
    records = log_json["evaluations"]
    diag = log_json["diagnostics"]

    assert len(records) == 19
    assert diag["correlations_9_non_leaking_scored"]["drift_corrected_pearson"] > 0.92
    assert diag["correlations_9_non_leaking_scored"]["drift_corrected_spearman"] > 0.80

    by_id = {r["candidate_id"]: r for r in records}
    d28 = by_id["D2.8-Poisson300m-Ref"]

    for cid in ("H32-A", "H32-B", "H32-C", "H32-D-Eq44090", "H32-D"):
        r = by_id[cid]
        assert r["on_catalogue_emitted_px"] == 0
        assert r["catalogue_hidden_mean"] > d28["catalogue_hidden_mean"]
        assert r["sgmc_prevalence_calibrated_dti"] > d28["sgmc_prevalence_calibrated_dti"]
        assert r["drift_corrected_holdout_mean"] > d28["drift_corrected_holdout_mean"]
        assert r["ei_drift_corrected"] > 0.0
        assert r["beats_incumbent_all_holdouts"] is True

    # Verify H32-D wins 4/4 quadrants on both catalogue_hidden and drift_corrected_holdout
    h32d = by_id["H32-D"]
    for q in ("NW", "NE", "SW", "SE"):
        assert h32d["catalogue_hidden_per_quadrant"][q] > d28["catalogue_hidden_per_quadrant"][q]
        assert h32d["drift_corrected_per_quadrant"][q] > d28["drift_corrected_per_quadrant"][q]

    # Verify wholesale ablations are logged and rejected by the holdout gate
    for wid in ("H32-A-Wholesale", "H32-B-Wholesale", "H32-C-Wholesale"):
        assert by_id[wid]["slot_decision"] == "REJECTED_BY_HOLDOUT_GATE"


def test_all_12_submission_geotiffs_pass_range_01_audit():
    ddir = data_dir()
    with rasterio.open(ddir / "sample_submission.tif") as src:
        foot = np.isfinite(src.read(1))
    with rasterio.open(ddir / "labels.tif") as src:
        labels = np.isfinite(src.read(1)) & (src.read(1) > 0) & foot

    manifest_path = downloads_dir() / "submissions_manifest.json"
    if not manifest_path.exists():
        import pytest
        pytest.skip("docs/downloads/submissions_manifest.json is absent: the parallel session's 12 "
                    "submission GeoTIFFs are gitignored and are not shipped in this checkout, so "
                    "this audit cannot run here. It is not a silent pass -- see IR-32-CI-01.")
    manifest = json.loads(manifest_path.read_text())
    assert manifest["validator_range_fix_verified"] is True
    assert len(manifest["submissions"]) == 6

    seen_filenames = set()
    for sub in manifest["submissions"]:
        for key, mode in (("zeros_tif", "zeros"), ("nan_tif", "nan")):
            info = sub[key]
            fname = info["filename"]
            assert fname not in seen_filenames
            seen_filenames.add(fname)
            tif_path = downloads_dir() / fname
            assert tif_path.exists()
            assert sha256_file(tif_path) == info["sha256"]
            audit = audit_geotiff(tif_path, foot, labels, mode=mode)
            assert audit["all_checks_passed"] is True


def test_docs_and_readme_integrity():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index_html = (docs_dir() / "index.html").read_text(encoding="utf-8")
    exec_html = (docs_dir() / "executive-summary.html").read_text(encoding="utf-8")

    for text in (readme, index_html):
        assert "Maximize P(Win)" in text
        assert "Own the Outcome" in text
        assert "Predicted values must be in range [0, 1]" in text
        assert "dotted-h19-5-d2-8-20261002-e56ea318af89-nan" in text

    # Check every local href/src in docs/index.html and docs/executive-summary.html resolves
    for page_name, content in (("index.html", index_html), ("executive-summary.html", exec_html)):
        refs = re.findall(r'(?:href|src)="([^"#]+)"', content)
        for ref in refs:
            if ref.startswith(("http://", "https://", "mailto:", "javascript:")):
                continue
            target = (docs_dir() / ref).resolve()
            assert target.exists(), f"Broken local reference {ref} in docs/{page_name} -> {target}"
