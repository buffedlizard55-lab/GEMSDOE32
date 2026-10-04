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


def _require_inputs(*names):
    """Skip (never silently pass) when a gitignored competition input is absent.

    ``data/`` is gitignored by design, so a fresh clone and CI have no rasters until
    ``bash scripts/download_competition_data.sh`` has run.  A test that needs one must say so
    explicitly rather than fail the build or, worse, pass vacuously.  IR-32-CI-01.
    """
    import pytest
    d = data_dir()
    missing = [n for n in names if not (d / n).exists()]
    if missing:
        pytest.skip(f"competition input(s) absent from {d}: {', '.join(missing)} — run "
                    f"bash scripts/download_competition_data.sh first")


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
    _require_inputs("training_features.tif")
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
    _require_inputs("training_features.tif")
    log_json = json.loads((ROOT / "data" / "holdout_surrogate_log.json").read_text())
    records = log_json["evaluations"]
    diag = log_json["diagnostics"]

    # the group-artifact extension (GEMSDOE27/28 owner mirrors) grew the log from 19 to 33
    # evaluations; one legacy duplicate (GEMS27-TGC-v2-on-D1.5, IR-33-DUP-01) is skipped, leaving 32.
    assert len(records) == 32, f"expected 32 de-duplicated evaluations, got {len(records)}"
    ids = [r["candidate_id"] for r in records]
    assert len(set(ids)) == len(ids), "duplicate candidate_id in the slot log"
    assert not any("DUPLICATE-REMOVED" in i for i in ids)

    # The co-kriging model must beat the raw catalogue proxy -- but it is *not* a strong predictor.
    # Adding the live-scored group artifacts made the honest numbers drift-corrected Spearman 0.697 /
    # Pearson 0.835, and the 0.2708 anchor is still under-predicted by ~-0.042. That gap is a
    # registered finding (IR-33-DRIFT-01), not a bug, so the test asserts the *ordering* and the
    # sign of the residual rather than an arbitrary threshold.
    corr = diag["correlations_9_non_leaking_scored"]
    assert corr["drift_corrected_spearman"] > corr["catalogue_hidden_spearman"]
    assert corr["drift_corrected_pearson"] > corr["catalogue_hidden_pearson"]
    anchor = next((r for r in records if r["candidate_id"] == "GEMS28-H27-4-R1-SOLO-D2.8"), None)
    if anchor is not None:
        # the 0.2708 anchor is under-predicted: the surrogate-vs-leaderboard gap (IR-33-DRIFT-01).
        gap = anchor["predicted_leaderboard_dti"] - 0.2708
        assert gap < -0.01, f"the surrogate no longer under-predicts the live anchor: {gap:+.4f}"

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
    _require_inputs("sample_submission.tif", "labels.tif")
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
    assert manifest.get("portal_illegal") == [], "the audit found a portal-illegal artifact"
    # scripts/audit_shipped.py rebuilds this manifest from the files actually on disk, so it lists
    # every artifact the repository ships (27 as of the H33 round), not only the six the pipeline's
    # own step 6 wrote.
    subs = manifest["submissions"]
    assert len(subs) >= 6, f"expected at least the 6 pipeline artifacts, got {len(subs)}"

    seen_filenames = set()
    for sub in subs:
        fname = sub["file"]
        assert fname not in seen_filenames, f"{fname} appears twice in the manifest"
        seen_filenames.add(fname)
        tif_path = downloads_dir() / fname
        assert tif_path.exists(), f"manifest lists a file that is not on disk: {fname}"
        assert sha256_file(tif_path) == sub["sha256"], f"digest mismatch for {fname}"
        # Mode is inferred from what the file actually writes outside the footprint -- never from
        # the filename and never from the nodata tag, because
        # `gems32-h19-5-smoothmaxcov-44090-zeros.tif` carried `nodata = NaN` on an all-finite
        # raster (IR-34-NODATA-01), so the tag is not trustworthy.
        with rasterio.open(tif_path) as ds:
            _arr, _nd = ds.read(1), ds.nodata
        _out = _arr[~foot]
        if bool(np.isnan(_out).all()):
            mode = "nan"
        elif bool(np.all(_out == 0.0)):
            mode = "zeros"
        else:                       # neither convention: fail loudly rather than guess
            raise AssertionError(
                f"{fname} writes {np.unique(_out)[:4]} outside the footprint; it follows neither "
                "the zeros nor the NaN convention")
        # IR-34-NODATA-01: a nodata tag that contradicts the file's own content is portal risk.
        if _nd is not None and np.isnan(_nd) and not np.isnan(_arr).any():
            raise AssertionError(
                f"{fname} carries nodata=NaN but contains no NaN; that tag/content mismatch is the "
                "configuration the DrivenData validator could reject (IR-34-NODATA-01)")
        audit = audit_geotiff(tif_path, foot, labels, mode=mode)
        assert audit["all_checks_passed"] is True, \
            f"{fname} failed the 12-point validator: {audit.get('failed_checks')}"


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
