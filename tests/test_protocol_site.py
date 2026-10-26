"""Current release status must fail closed and precede every current-artifact link."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
H46_FILE = "gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-zeros.tif"


def test_current_release_review_is_negative_and_scopes_the_saved_byte_audit():
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    assert review["submission_authorization"]["ok_to_download_and_submit"] is False
    assert review["submission_authorization"]["verdict"] == "negative"
    audit = review["artifact"]["format_byte_audit"]
    assert audit["verified_this_review"] is True
    assert audit["min"] >= 0
    assert audit["max"] <= 1
    assert audit["total_cells"] == audit["finite_cells"] == 12_279_160
    template = review["artifact"]["reference_grid_reaudit"]
    assert template["template_present_this_review"] is False
    assert template["status"].startswith("NOT RUN")
    assert len(review["submission_authorization"]["reasons"]) >= 3


def test_site_pages_show_current_audit_only_status_before_current_artifact_link():
    for name in ["docs/index.html", "docs/executive-summary.html", "index.html"]:
        text = (ROOT / name).read_text()
        marker = "DO NOT SUBMIT"
        assert marker in text
        assert text.index(marker) < text.index(H46_FILE)
        assert "OK TO DOWNLOAD AND SUBMIT" not in text
        assert "PROMOTE" not in text
        assert "NOT FOR LIVE SUBMISSION" in text or "SUBMIT TO DRIVENDATA: NO" in text
    summary = (ROOT / "docs/executive-summary.html").read_text()
    assert "will show upload instructions only after" in summary
    assert "Unique Submission Identifier" not in summary


def test_missing_release_decision_fails_closed_in_builder():
    source = (ROOT / "scripts/build_site.py").read_text()
    assert 'read("evidence/current_release_review.json", {}) or {}' in source
    assert 'get("ok_to_download_and_submit") is not True' in source


def test_literal_calibration_lattice_overlap_is_a_release_blocker():
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    uniqueness = review["uniqueness_evidence_from_h46_run_card"]
    assert uniqueness["literal_calibration_lattice_within_3px_fraction"] > uniqueness["threshold"]
    assert uniqueness["freshly_recomputed_this_review"] is False
    assert uniqueness["literal_all_registry_passed"] is False
    for name in ["docs/index.html", "docs/executive-summary.html"]:
        text = (ROOT / name).read_text()
        assert "99.267%" in text
        assert "calibration lattice" in text


def test_group_champion_score_is_not_mislabeled_as_organizer_confirmed():
    status = json.loads((ROOT / "registry/current_status.json").read_text())
    champion = status["best_scored"]
    assert champion["score"] == 0.2778
    assert champion["evidence_class"].startswith("OWNER-REPORT")
    assert "no submission-page receipt" in champion["evidence_class"]
    claims = json.loads((ROOT / "registry/claims.json").read_text())
    claim = next(row for row in claims["claims"] if row["id"] == "claim-h33-b2-02778")
    assert claim["kind"] == "owner_report"
    assert "no submission-page receipt" in claim["reported_by"]
    for page in ["docs/index.html", "docs/executive-summary.html"]:
        rendered = (ROOT / page).read_text()
        assert "0.2778</b> OWNER-REPORT" in rendered
        assert "ORGANIZER-CONFIRMED (owner-reported receipt)" not in rendered


def test_current_review_run_card_has_bounded_note_and_negative_verdict():
    card = json.loads((ROOT / "evidence/review_run_card_20261026.json").read_text())
    assert card["verdict"] == "negative"
    assert len(card["submission_note_le140"]) <= 140
    assert card["raster_sha256"] == "c7f094c1f4d00f2dd9a056dc80fecc94bf1d636363acd020c9da3659eae56547"
    assert card["validator_output"]["overall_submission_validation_pass"] is False


def test_all_current_release_sources_point_to_h46_and_remain_negative():
    status = json.loads((ROOT / "registry/current_status.json").read_text())
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    build = json.loads((ROOT / "registry/submission_build.json").read_text())
    candidate = status["newest_unique"]
    assert candidate["file"].endswith(H46_FILE)
    assert candidate["sha256"] == review["artifact"]["sha256"] == build["file"]["sha256"]
    assert status["any_file_ok_to_submit"] is False
    assert candidate["ok_to_submit"] is False
    assert build["ok_to_submit"] is False
    assert build["verdict"] == "negative"
    assert review["submission_authorization"]["ok_to_download_and_submit"] is False
    assert "template comparison was not reproduced" in status["headline"]
