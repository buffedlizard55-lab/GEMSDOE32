"""Regression coverage for the 2026-10-26 fail-closed repository review."""
from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _digest(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_retired_conduit_runner_exits_without_mutating_release_records():
    protected = [
        "registry/current_status.json",
        "registry/submission_build.json",
        "registry/submission_build_geo_conduit_superseded.json",
        "evidence/geo_conduit_run_card.json",
        "evidence/current_release_review.json",
    ]
    before = {rel: _digest(rel) for rel in protected}
    proc = subprocess.run(
        [sys.executable, "scripts/run_conduit_pipeline.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 2
    assert "retired" in proc.stdout.lower()
    assert "no experiment" in proc.stdout.lower()
    assert {rel: _digest(rel) for rel in protected} == before


def test_archived_arena9_updater_refuses_to_overwrite_h46():
    protected = [
        "registry/current_status.json",
        "registry/submission_build.json",
        "evidence/current_release_review.json",
    ]
    before = {rel: _digest(rel) for rel in protected}
    proc = subprocess.run(
        [sys.executable, "scripts/update_arena9_release.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode != 0
    assert "Refusing to restore the historical Arena9 review" in proc.stderr
    assert {rel: _digest(rel) for rel in protected} == before


def test_legacy_conduit_promotion_and_interval_are_withdrawn_but_preserved_as_history():
    card = json.loads((ROOT / "evidence/geo_conduit_run_card.json").read_text())
    build = json.loads((ROOT / "registry/submission_build_geo_conduit_superseded.json").read_text())
    hypothesis = json.loads((ROOT / "registry/hypotheses.json").read_text())
    hgeo3 = next(h for h in hypothesis["hypotheses"] if h["id"] == "H-GEO-3")

    assert card["verdict"] == "negative"
    assert card["ok_to_download_and_submit"] is False
    assert card["historical_decision"]["verdict"] == "promote"
    assert card["historical_decision"]["ok_to_download_and_submit"] is True
    assert card["holdout"]["ci95_cluster_bootstrap"] is None
    assert "Withdrawn" in card["holdout"]["ci95_status"]
    assert card["reassessment"]["replacement_runner"].startswith("Disabled")
    assert build["verdict"] == "negative"
    assert build["ok_to_submit"] is False
    assert build["historical_decision"]["verdict"] == "promote"
    assert "Unquantified" in hgeo3["expected_dti"]
    assert "withdrawn" in hgeo3["expected_dti"].lower()
    assert "absent from this checkout" in hgeo3["data_status"]

    status = json.loads((ROOT / "registry/current_status.json").read_text())
    current_build = json.loads((ROOT / "registry/submission_build.json").read_text())
    assert status["round6_candidate"]["ok_to_submit"] is False
    assert current_build["round6_session_verdict"] == "negative"
    assert current_build["round6_session_verdict_legacy"].startswith("promote (unqualified legacy value")


def test_site_page_render_is_deterministic_for_the_same_status_snapshot():
    module = runpy.run_path(str(ROOT / "scripts/build_site.py"), run_name="site_determinism_probe")
    render = module["page"]
    first = render("Determinism", "<p>same body</p>", "index.html", "")
    second = render("Determinism", "<p>same body</p>", "index.html", "")
    assert first == second
    status = json.loads((ROOT / "registry/current_status.json").read_text())
    stamp = status["updated_utc"][:16].replace("T", " ") + " UTC"
    assert f"Status snapshot updated {stamp}" in first


def test_release_page_renders_one_status_card_and_audit_only_catalogue_role():
    for rel in ("docs/index.html", "docs/executive-summary.html"):
        html = (ROOT / rel).read_text()
        assert html.count('id=status') + html.count('id="status"') == 1
        assert html.count('aria-label="Current submission decision"') == 1
        assert "A file is cleared." not in html
        assert "Upload authorized &mdash; see the status card" not in html
    assert "CURRENT RESEARCH/AUDIT ONLY" in (ROOT / "docs/executive-summary.html").read_text()
    builder = (ROOT / "scripts/build_site.py").read_text()
    assert "protocol_notice/arena41_block" not in builder
    assert "repo-review-20261026.md" not in builder
    assert "repository-review-20261026-arena-followup.md" in builder


def test_current_followup_review_exists_and_discloses_blockers_and_ranked_tests():
    path = ROOT / "docs/research/repository-review-20261026-arena-followup.md"
    text = path.read_text()
    for required in (
        "## Three review passes",
        "## Ranked, not-yet-executed geological tests",
        "Threshold-persistent 1 m LiDAR scarp-network topology",
        "Signed paired magnetic-edge geometry",
        "Drainage-reach deflection",
        "GeoDAWN acquisition-block-normalized radiometric alteration zoning",
        "Paired InSAR deformation-gradient and 3-D MT phase-tensor segmentation",
        "DOWNLOAD FOR RESEARCH/AUDIT: YES. SUBMIT: NO.",
        "No new GeoTIFF",
        "not an organizer score",
        "2026-10-26",
    ):
        assert required in text
