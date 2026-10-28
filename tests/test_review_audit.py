"""Regression checks for the generated nine-site audit's live artifact reference."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_nine_site_audit_download_label_matches_current_registered_artifact():
    status = json.loads((ROOT / "registry/current_status.json").read_text())
    candidate = status["newest_unique"]
    label = candidate.get("submission_name") or Path(candidate["file"]).stem
    page = (ROOT / "docs/nine-site-review.html").read_text()
    href = candidate["file"].removeprefix("docs/")

    assert f'href="{href}"' in page
    assert f"Download {label} GeoTIFF — RESEARCH / AUDIT ONLY" in page
    assert f"The latest registered candidate is <b>{label}</b>" in page
    assert "{html.escape(artifact_label)}" not in page
    assert "Download existing H48 TIF" not in page
    assert "DO NOT SUBMIT" in page


def test_review_audit_card_labels_historical_evidence_and_preserves_protocol_numbers():
    card = json.loads((ROOT / "evidence/review_audit_20261028.json").read_text())
    assert card["verdict"] == "negative"
    assert card["holdout"]["status"] == "HISTORICAL_RESULT_NOT_RERUN_THIS_REVIEW"
    assert card["holdout"]["label"] == "HOLDOUT-DTI"
    assert card["holdout"]["evaluator_version"] == "GEMSDOE32-HIDE-RECOVER-v3.0"
    assert card["holdout"]["n_withheld_positives"] == 22232
    assert card["holdout"]["ci95"] == [0.090781, 0.119402]
    assert card["correlation_overlap_vs_registry"]["literal_registry_passed"] is False
    assert card["correlation_overlap_vs_registry"]["literal_calibration_lattice_3px_overlap"] > 0.70


def test_review_audit_generator_uses_current_candidate_instead_of_hardcoded_h48():
    source = (ROOT / "scripts/build_review_audit.py").read_text()
    assert "artifact_label = newest.get('submission_name')" in source
    assert "Download {html.escape(artifact_label)} GeoTIFF" in source
    assert "Existing H48 artifact" not in source
