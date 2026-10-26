"""Regression tests for the single authoritative, fail-closed site decision."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
R6_FILE = "gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"


def test_current_stop_notice_is_above_all_download_links():
    for name in ["docs/index.html", "docs/executive-summary.html", "index.html"]:
        text = (ROOT / name).read_text()
        assert "DO NOT SUBMIT" in text
        assert "OK TO DOWNLOAD AND SUBMIT" not in text
        assert text.index("DO NOT SUBMIT") < text.index('href="downloads/' if name.startswith("docs/") else 'href="docs/downloads/')
        assert R6_FILE in text


def test_run_card_fails_closed_on_holdout_leak_and_literal_registry_overlap():
    card = json.loads((ROOT / "evidence/round6_run_card.json").read_text())
    review = card["protocol_review"]
    assert card["verdict"] == "negative"
    assert card["ok_to_download_and_submit"] is False
    assert review["release_authorized"] is False
    gates = {g["gate"]: g for g in review["failed_gates"]}
    overlap = gates["literal registry-dot overlap <= 70% within 3 px"]["candidate_within3px_fraction"]
    assert overlap > 0.70
    leakage = gates["required spatial hide-and-recover holdout"]["finding"]
    assert "full catalogue" in leakage


def test_generated_site_has_no_superseded_green_promotion_copy():
    for name in ["docs/index.html", "docs/executive-summary.html", "index.html"]:
        text = (ROOT / name).read_text()
        assert "R6-1 STEP file is an audit artifact only" in text
        assert "PROMOTE" not in text
        assert "OK TO SUBMIT" not in text
