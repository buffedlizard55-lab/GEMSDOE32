"""GitHub Pages output must render the current release authorization, not historical status."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"
AUDIT_NAME = "gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"


def _require_inputs(*names: str):
    missing = [n for n in names if not (SITE / n).exists()]
    if missing:
        pytest.skip(f"site not built in this checkout: {missing}")


def _local_targets(page: Path):
    html = page.read_text()
    for rel in re.findall(r'(?:href|src)="([^"#]+?)"', html):
        if rel.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
            continue
        target = (page.parent / rel).resolve()
        assert target.is_file(), f"{page.relative_to(ROOT)} links at missing file: {rel}"


def test_root_pages_have_valid_links_and_do_not_imply_submission_authorization():
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    assert review["submission_authorization"]["ok_to_download_and_submit"] is False
    root_pages = sorted(ROOT.glob("*.html"))
    assert root_pages
    for page in root_pages:
        _local_targets(page)
        html = page.read_text()
        if AUDIT_NAME in html:
            assert "DO NOT SUBMIT" in html
            assert "audit artifact only" in html.lower()
            assert "OK TO DOWNLOAD AND SUBMIT" not in html
            assert "PROMOTE" not in html
    index = (ROOT / "index.html").read_text()
    assert AUDIT_NAME in index
    assert "DO NOT SUBMIT" in index


def test_docs_pages_link_only_to_auditing_artifact_when_release_is_negative():
    _require_inputs("index.html", "executive-summary.html")
    review = json.loads((ROOT / "evidence/current_release_review.json").read_text())
    assert review["submission_authorization"]["ok_to_download_and_submit"] is False
    for page in sorted(SITE.glob("*.html")):
        _local_targets(page)
        html = page.read_text()
        if AUDIT_NAME in html:
            assert "DO NOT SUBMIT" in html
            assert "audit" in html.lower()
            assert "OK TO DOWNLOAD AND SUBMIT" not in html
            assert "PROMOTE" not in html
    summary = (SITE / "executive-summary.html").read_text()
    assert "no upload authorized" in summary.lower()
    assert "Unique Submission Identifier" not in summary
    assert "Click <i>Submit</i>" not in summary


def test_submission_metadata_is_not_authorized_and_notes_remain_bounded():
    sub = json.loads((ROOT / "registry/submission_build.json").read_text())
    assert sub["ok_to_submit"] is False
    assert sub["verdict"] == "negative"
    assert sub["current_release_review"] == "evidence/current_release_review.json"
    assert len(sub["note"]) <= 200
    assert sub["file"]["sha256"] == json.loads(
        (ROOT / "evidence/current_release_review.json").read_text()
    )["artifact"]["sha256"]


def test_registry_and_site_agree_on_the_hypothesis_count():
    _require_inputs("hypotheses.html")
    hyp = json.loads((ROOT / "registry/hypotheses.json").read_text())
    ids = [h["id"] for h in hyp["hypotheses"]]
    assert len(ids) == len(set(ids)), "duplicate hypothesis id in the registry"
    html = (SITE / "hypotheses.html").read_text()
    for h in hyp["hypotheses"]:
        assert h["id"] in html, f"{h['id']} is registered but not rendered on the hypotheses page"
