"""Regression pins for the 2026-10-29 repo review (review-20261029).

These tests do not re-run the holdout; they check that the committed evidence agrees with the
registry, that the verdict stays fail-closed, and that the page is generated from evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _j(rel: str):
    return json.loads((ROOT / rel).read_text())


def test_rescore_has_no_errors_and_reproduces_registry_champion():
    rs = _j("evidence/focus_rescore_20261029.json")
    assert not [r for r in rs["rows"] if "holdout_error" in r or "format_error" in r]
    h33 = [r for r in rs["rows"] if r["file"].endswith("gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif")]
    assert len(h33) == 1
    # registry/current_status.json and evidence/holdout_static_recheck_20261028.json record 0.004515
    assert abs(h33[0]["holdout"]["hide_recover_pooled_dti"] - 0.004515) < 1e-5
    assert abs(h33[0]["holdout"]["sgmc_calibrated_dti"] - 0.064121) < 1e-5
    assert h33[0]["holdout"]["hide_recover_withheld_positives"] == 22232
    assert h33[0]["holdout"]["sgmc_withheld_positives"] == 62703


def test_unique_candidate_bytes_match_registry_sha():
    st = _j("registry/current_status.json")
    art = ROOT / st["newest_unique"]["file"]
    assert hashlib.sha256(art.read_bytes()).hexdigest() == st["newest_unique"]["sha256"]


def test_verdict_stays_fail_closed():
    st = _j("registry/current_status.json")
    assert st["any_file_ok_to_submit"] is False
    assert st["newest_unique"]["ok_to_submit"] is False


def test_directional_overlap_has_both_0p2778_pairs():
    ov = _j("evidence/focus_directional_overlap_20261029.json")
    h33_to_25 = [p for p in ov["pairs"] if p["your_dots"].startswith("GEMSDOE32 h33") and "GEMSDOE25 d2-8" in p["registry_or_peer"]]
    assert len(h33_to_25) == 1
    assert h33_to_25[0]["your_dots_within_3px"] > 0.99


def test_irregularities_recorded_for_review():
    ids = {x["id"] for x in _j("registry/irregularities.json")["items"]}
    for want in ["IR-20261029-LB-01", "IR-20261029-NAN-01", "IR-20261029-EVAL-01",
                 "IR-20261029-DUP-01", "IR-20261029-BYTES-01", "IR-20261029-PROB-01"]:
        assert want in ids


def test_review_page_is_generated_and_fail_closed():
    page = (ROOT / "docs" / "review-20261029.html").read_text()
    assert "NO FILE IS CLEARED FOR UPLOAD" in page
    assert "0.4544" in page
    assert "No projection is written as a score" in page
