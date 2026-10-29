"""Regression checks for the 2026-10-29 verified nine-site summary (no competition data needed)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = json.loads((ROOT / "evidence" / "nine_site_verification_20261029.json").read_text())
CARD = json.loads((ROOT / "evidence" / "run_card_20261029_verification.json").read_text())
STATUS = json.loads((ROOT / "registry" / "current_status.json").read_text())
PAGE = (ROOT / "docs" / "nine-site-verified-summary.html").read_text()


def test_pinned_digests_match_for_all_nine_focus_files():
    checks = EVID["pinned_digest_check"]
    assert set(checks) == {"GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                           "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"}
    assert all(v["match"] for v in checks.values())


def test_identical_dot_sets_are_recorded():
    assert "GEMSDOE25==GEMSDOE30" in EVID["identical_dot_sets"]


def test_h51_card_digest_matches_registry_and_note_fits_limit():
    assert CARD["raster_sha256"] == STATUS["newest_unique"]["sha256"]
    assert len(CARD["submission_note"]) <= 140
    assert CARD["validator_output"]["nan_in_footprint"] == 0
    assert CARD["validator_output"]["unique_values_in_footprint"] == [0.0, 1.0]
    assert CARD["verdict"].startswith("negative")


def test_r13_rule_bound_is_consistent():
    r13 = EVID["r13_coverage"]
    assert 0.0 < r13["footprint_within_3px_of_r13"] <= 1.0
    assert r13["max_dots_satisfying_literal_70pct_rule_bound"] == int(r13["footprint_beyond_3px_of_r13_px"] / 0.30)


def test_association_signs_are_recorded_not_claimed_causal():
    a = EVID["association_n9"]
    assert a["rho_live_vs_dots"] < 0
    assert a["rho_static_HIDE_RECOVER_vs_live"] < 0
    assert "no causal claim" in a["note"]


def test_every_projection_is_labelled_projection_and_not_a_score():
    mv = EVID["mass_vs_owner_live"]
    assert mv["label"].startswith("PROJECTION")
    assert CARD["projection_not_a_score"]["label"].startswith("PROJECTION")
    assert "ORGANIZER-CONFIRMED: none" in PAGE


def test_page_decision_is_do_not_submit_and_links_the_unique_file():
    assert "DO NOT SUBMIT" in PAGE
    assert "gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif" in PAGE
    assert (ROOT / "docs" / "downloads" / "gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif").is_file()
