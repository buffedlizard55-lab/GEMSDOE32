"""Current release status must be fail-closed and appear before any artifact link."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
R6_FILE = "gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"


def test_current_release_review_is_negative_and_preserves_format_pass():
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    assert review["submission_authorization"]["ok_to_download_and_submit"] is False
    assert review["submission_authorization"]["verdict"] == "negative"
    assert review["artifact"]["format_byte_audit"]["verified_this_review"] is True
    assert review["artifact"]["format_byte_audit"]["min"] >= 0
    assert review["artifact"]["format_byte_audit"]["max"] <= 1
    assert len(review["submission_authorization"]["reasons"]) >= 3


def test_site_pages_show_audit_only_status_before_any_artifact_link():
    for name in ["docs/index.html", "docs/executive-summary.html", "index.html"]:
        text = (ROOT / name).read_text()
        marker = "DO NOT SUBMIT"
        assert marker in text
        assert text.index(marker) < text.index(R6_FILE)
        assert "OK TO DOWNLOAD AND SUBMIT" not in text
        assert "PROMOTE" not in text
    summary = (ROOT / "docs/executive-summary.html").read_text()
    assert "will show upload instructions only after" in summary
    assert "Unique Submission Identifier" not in summary


def test_missing_release_decision_fails_closed_in_builder():
    source = (ROOT / "scripts/build_site.py").read_text()
    assert 'read("evidence/current_release_review.json", {}) or {}' in source
    assert 'get("ok_to_download_and_submit") is not True' in source


def test_literal_calibration_lattice_overlap_is_a_release_blocker():
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    uniqueness = review["uniqueness_evidence_from_historical_round6_card"]
    assert uniqueness["final_calibration_lattice_within_3px_fraction"] > uniqueness["threshold"]
    assert uniqueness["preplacement_all_registry_surface_check_complete"] is False
    for name in ["docs/index.html", "docs/executive-summary.html"]:
        text = (ROOT / name).read_text()
        assert "97.82%" in text
        assert "calibration lattice" in text


def test_current_review_run_card_has_bounded_note_and_negative_verdict():
    card = json.loads((ROOT / "evidence/review_run_card_20261026.json").read_text())
    assert card["verdict"] == "negative"
    assert len(card["submission_note_le140"]) <= 140
    assert card["raster_sha256"] == "c7f094c1f4d00f2dd9a056dc80fecc94bf1d636363acd020c9da3659eae56547"
    assert card["validator_output"]["overall_submission_validation_pass"] is False
