"""Archived Arena9 negative result remains intact; current release is H46 and fails closed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CARD = ROOT / "evidence" / "arena9_run_card.json"
TIFF = ROOT / "docs" / "downloads" / "gemsdoe32-arena9-pgrn-pu37654-20261026T053246Z-4f7aba9b-zeros.tif"
EXPECTED_SHA256 = "8eee6e1a85708c9188c7b9d7f436deab621657aab22c3d9d48da9dd64c84e609"
H46_FILE = "docs/downloads/gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-zeros.tif"
H46_SHA256 = "9f42346d3acecb8d873fb35c70d988ae0afeb99781c6104c644d8cf9f85e0dc3"


def _json(path: Path):
    return json.loads(path.read_text())


def test_archived_arena9_run_card_is_complete_and_negative():
    card = _json(CARD)
    assert not (ROOT / "registry" / "arena9_submission.json").exists()
    assert card["lane_id"] == "A9-H1-MDRC-PGRN-PU"
    assert card["hypothesis"] and card["mechanism"] and card["named_non_fault_mimic"]
    assert card["experiments_used"] == 3 <= card["experiments_budget"]
    assert card["weekly_slots_used"] == 0
    assert card["holdout_dti"]["label"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "GEMSDOE32-HIDE-RECOVER-v3.0"
    assert card["holdout_dti"]["n_withheld_positives"] == 22_232
    assert len(card["holdout_dti"]["selected_ci95"]) == 2
    assert card["correlation_overlap_vs_registry"]["final_dots"]["worst_within_3px_fraction"] > 0.70
    assert card["raster_sha256"] == EXPECTED_SHA256
    assert card["validator_output"]["independent_validator_passed"] is True
    assert card["submission_name"] == "GEMSDOE32-A9-PGRN-PU-4F7ABA9B"
    assert len(card["submission_note"]) == card["submission_note_length"] <= 140
    assert card["verdict"] == "negative"
    assert card["ok_to_submit_to_live_portal"] is False


def test_current_release_is_h46_but_arena9_artifact_remains_archived():
    card = _json(CARD)
    assert TIFF.is_file()
    assert hashlib.sha256(TIFF.read_bytes()).hexdigest() == EXPECTED_SHA256

    status = _json(ROOT / "registry" / "current_status.json")
    release = _json(ROOT / "evidence" / "current_release_review.json")
    latest = _json(ROOT / "docs" / "data" / "latest-run-card.json")
    archive = _json(ROOT / "evidence" / "release_review_arena9_20261026.json")
    candidate = status["arena9_candidate"]

    assert candidate["sha256"] == card["raster_sha256"]
    assert candidate["verdict"] == "DO NOT SUBMIT"
    assert candidate["ok_to_download"] is True
    assert candidate["ok_to_submit"] is False
    assert status["newest_unique"]["file"] == H46_FILE
    assert status["newest_unique"]["sha256"] == H46_SHA256
    assert status["any_file_ok_to_submit"] is False
    assert release["artifact"]["path"] == H46_FILE
    assert release["artifact"]["sha256"] == H46_SHA256
    assert release["prior_release_review_archive"] == "evidence/release_review_arena9_20261026.json"
    assert archive["latest_candidate"]["sha256"] == card["raster_sha256"]
    assert archive["submission_authorization"]["ok_to_download_and_submit"] is False
    assert release["submission_authorization"]["ok_to_download_and_submit"] is False
    # The published latest-run-card follows current_status, while Arena9 remains an archived artifact.
    assert latest["raster_sha256"] == status["newest_unique"]["sha256"]
    assert latest["candidate_id"] == "H46-1-TRHV"
    assert latest["verdict"] == "negative"


def test_arena9_fail_closed_gates_and_registry_irregularity_are_explicit():
    card = _json(CARD)
    gates = card["automated_gates"]
    assert gates == {
        "G1_leakage_canary": True,
        "G2_holdout_beats_champion_and_repo_best": False,
        "G3_sgmc_beats_champion": True,
        "G4_surface_registry_unique": True,
        "G4_final_registry_unique": False,
        "G5_format_and_range": True,
    }
    assert card["leakage_canary"]["worst_auc"] <= card["leakage_canary"]["threshold"] == 0.90

    audit = card["correlation_overlap_vs_registry"]
    assert audit["surface_before_placement"]["registry_rasters"] == 304
    assert audit["surface_before_placement"]["malformed_or_missing"] == 1
    malformed = [
        row
        for row in audit["surface_before_placement"]["comparisons"]
        if row.get("status") == "grid_mismatch"
    ]
    assert len(malformed) == 1
    assert malformed[0]["path"].endswith("GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif")


def test_pages_separate_current_h46_audit_download_from_arena9_history():
    for rel in ("docs/index.html", "docs/executive-summary.html", "index.html"):
        text = (ROOT / rel).read_text()
        assert "DO NOT SUBMIT" in text
        assert "NOT FOR LIVE SUBMISSION" in text or "SUBMIT TO DRIVENDATA: NO" in text
        assert Path(H46_FILE).name in text
        assert TIFF.name in text
        assert "H46" in text
