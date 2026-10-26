"""Release-registry consistency contract (IR-48-SYNC-01).

The ARENA47 merge (PR #33) advanced the release review and current status but left
``registry/submission_build.json`` pinned to Arena9, turning main's test suite red.  These
tests pin the *relationship* between the three release registries instead of any single
candidate, so a future session cannot advance one registry and silently abandon the others.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(p: str) -> dict:
    return json.loads((ROOT / p).read_text())


def test_release_review_and_current_status_agree_on_newest_artifact():
    release = _json("evidence/current_release_review.json")
    status = _json("registry/current_status.json")
    art_sha = release["artifact"]["sha256"]
    assert art_sha == status["newest_unique"]["sha256"]
    assert (ROOT / release["artifact"]["path"]).is_file()
    assert (
        hashlib.sha256((ROOT / release["artifact"]["path"]).read_bytes()).hexdigest() == art_sha
    )
    assert release["submission_authorization"]["ok_to_download_and_submit"] is False
    assert status["any_file_ok_to_submit"] is False


def test_submission_build_pins_the_release_review_artifact_and_stays_closed():
    build = _json("registry/submission_build.json")
    release = _json("evidence/current_release_review.json")
    status = _json("registry/current_status.json")
    assert build["ok_to_submit"] is False
    assert build["verdict"] == "negative"
    assert build["current_release_review"] == "evidence/current_release_review.json"
    assert build["file"]["sha256"] == release["artifact"]["sha256"] == status["newest_unique"]["sha256"]
    assert (ROOT / build["file"]["path"]).is_file()
    assert len(build["note"]) <= 200


def test_latest_run_card_mirrors_the_newest_candidate_card():
    status = _json("registry/current_status.json")
    newest = status["newest_unique"]
    card_path = ROOT / newest["run_card"]
    assert card_path.is_file()
    latest = _json("docs/data/latest-run-card.json")
    assert latest == json.loads(card_path.read_text())
    assert latest.get("raster_sha256") == newest["sha256"]


def test_no_missing_metric_renders_as_zero():
    """A missing holdout metric must render as an em dash, never as a measured 0.00000.

    Regression guard for the ``nan [0.00000, 0.00000]`` rendering defect (IR-48-SYNC-02).
    """
    for rel in ("index.html", "docs/index.html", "docs/executive-summary.html"):
        text = (ROOT / rel).read_text()
        assert "[0.00000, 0.00000]" not in text, rel
        assert "nan [0.00000" not in text, rel
