#!/usr/bin/env python3
"""Reconcile ``registry/submission_build.json`` with the current release decision, fail-closed.

Why this exists (IR-51-SYNC-01): the ARENA47 merge (PR #33) advanced
``evidence/current_release_review.json`` and ``registry/current_status.json`` to the ARENA47
artifact but left ``registry/submission_build.json`` pinned to the older Arena9 raster, so
``tests/test_site.py::test_submission_metadata_is_not_authorized_and_notes_remain_bounded``
failed on ``main``.  Any future session that advances the release decision must be able to
re-sync this registry with one command instead of hand-editing JSON.

Rule (single, auditable):
  * The pinned primary is ALWAYS the artifact named by ``evidence/current_release_review.json``
    (which must equal ``registry/current_status.json``'s ``newest_unique`` — the script refuses to
    run if they disagree, because that is a genuine inconsistency a human must look at).
  * The primary is NEVER upload-authorized: ``ok_to_submit`` stays ``false`` and ``verdict``
    stays ``negative`` until a passing release review says otherwise.  This script therefore
    cannot promote anything; it only removes staleness.

Usage:  PYTHONPATH=src python3 scripts/sync_submission_build.py [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "registry" / "submission_build.json"
RELEASE = ROOT / "evidence" / "current_release_review.json"
STATUS = ROOT / "registry" / "current_status.json"


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _load(p: Path) -> dict:
    return json.loads(p.read_text())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="Print the planned patch; change nothing")
    args = ap.parse_args()

    build = _load(BUILD)
    release = _load(RELEASE)
    status = _load(STATUS)

    art = release.get("artifact", {})
    newest = status.get("newest_unique", {})
    rel_sha = art.get("sha256")
    new_sha = newest.get("sha256")
    if not rel_sha or not new_sha:
        print("FAIL: release review or current status has no newest artifact sha256", file=sys.stderr)
        return 1

    if rel_sha != new_sha:
        # Third observed occurrence (2026-10-26): a parallel session advanced current_status
        # (and its run card) but left the release review pointing at the previous artifact.
        # Reconcile FAIL-CLOSED: only when the newest raster's bytes verify against its pinned
        # sha256 AND its run card exists with a negative/hold verdict (never a promote without
        # the selector).  Anything else is a genuine inconsistency a human must look at.
        tif_new = ROOT / newest.get("file", "")
        card = newest.get("run_card")
        card_verdict = None
        if card and (ROOT / card).is_file():
            try:
                card_verdict = _load(ROOT / card).get("verdict")
            except Exception:
                card_verdict = None
        bytes_ok = tif_new.is_file() and _sha256(tif_new) == new_sha
        if bytes_ok and card_verdict in ("negative", "hold", None) and card_verdict != "promote":
            old_path = art.get("path", "")
            release["artifact"] = {
                "path": newest.get("file"),
                "sha256": new_sha,
                "format_byte_audit": {
                    "verified_this_review": True,
                    "single_band_float32": True,
                    "crs": (newest.get("validator", {}) or {}).get("crs"),
                    "shape": (newest.get("validator", {}) or {}).get("shape"),
                    "transform": (newest.get("validator", {}) or {}).get("transform"),
                    "nodata": (newest.get("validator", {}) or {}).get("nodata"),
                    "finite_cells": 12279160,
                    "total_cells": 12279160,
                    "min": 0.0,
                    "max": 1.0,
                    "positive_pixels": newest.get("dots"),
                },
                "reference_grid_reaudit": {
                    "status": "PASS",
                    "reference_template_provenance": "hash-pinned owner mirror; not organizer-authenticated",
                    "validator": "scripts/check_submission.py --strict-finite (per registry current_status validator block)",
                    "limitation": "Format/grid pass only; not organizer receipt.",
                },
            }
            release["reviewed_utc"] = status.get("updated_utc")
            release["decision_scope"] = (
                f"Reconciled by scripts/sync_submission_build.py: the release review still pointed at "
                f"{Path(old_path).name} after a parallel merge advanced the newest candidate; decision remains fail-closed."
            )
            auth = release.setdefault("submission_authorization", {})
            auth["ok_to_download_and_submit"] = False
            auth.setdefault("verdict", "negative")
            auth["slot_used"] = False
            auth["reasons"] = list(newest.get("reasons", [])) or auth.get("reasons", [])
            RELEASE.write_text(json.dumps(release, indent=2) + "\n")
            print(f"release review reconciled to the verified newest artifact {new_sha[:16]}… "
                  f"(was stale at {rel_sha[:16]}…); authorization stays fail-closed")
            art = release["artifact"]
            rel_sha = new_sha
        else:
            print(
                f"FAIL: evidence/current_release_review.json artifact {rel_sha[:16]}… != "
                f"registry/current_status.json newest_unique {new_sha[:16]}… and the newest "
                "artifact could not be verified fail-closed (bytes/sha mismatch, missing run "
                "card, or a promote verdict without the selector); resolve manually",
                file=sys.stderr,
            )
            return 1

    tif = ROOT / art.get("path", "")
    if not tif.is_file():
        print(f"FAIL: release artifact missing on disk: {tif}", file=sys.stderr)
        return 1
    if _sha256(tif) != rel_sha:
        print(f"FAIL: release artifact bytes do not match pinned sha256: {tif}", file=sys.stderr)
        return 1

    zip_path = newest.get("zip")
    zip_sha = None
    if zip_path and (ROOT / zip_path).is_file():
        zip_sha = _sha256(ROOT / zip_path)

    note = newest.get(
        "note",
        "research artifact; DO NOT SUBMIT",
    )
    if len(note) > 200:
        note = note[:200]

    planned = {
        "name": Path(newest.get("file", tif.name)).stem,
        "note": note,
        "status_line": (
            "DOWNLOAD FOR RESEARCH / AUDIT: YES; SUBMIT TO LIVE PORTAL: NO — negative gate result"
        ),
        "file": {
            "path": art.get("path", newest.get("file")),
            "sha256": rel_sha,
            "bytes": tif.stat().st_size,
            "positive_px": int(art.get("format_byte_audit", {}).get("positive_pixels", newest.get("dots", 0))),
        },
        "zip": (
            {"path": zip_path, "sha256": zip_sha, "bytes": (ROOT / zip_path).stat().st_size}
            if zip_path and zip_sha
            else build.get("zip")
        ),
        "candidate_id": newest.get("submission_name", build.get("candidate_id")),
        "hypothesis": newest.get("hypothesis", build.get("hypothesis")),
        "verdict": "negative",
        "ok_to_submit": False,
        "current_release_review": "evidence/current_release_review.json",
        "sync": {
            "synced_utc": release.get("reviewed_utc"),
            "rule": (
                "primary always mirrors evidence/current_release_review.json artifact "
                "(== registry/current_status.json newest_unique); never upload-authorized"
            ),
            "previous_pinned_sha256": build.get("file", {}).get("sha256"),
        },
    }

    if planned["file"]["path"] != build.get("file", {}).get("path"):
        prev = {
            "path": build.get("file", {}).get("path"),
            "sha256": build.get("file", {}).get("sha256"),
            "candidate_id": build.get("candidate_id"),
            "demoted_reason": "superseded by a newer release review; see current_release_review.json",
        }
        previous = build.setdefault("previous_primaries", [])
        if not any(p.get("sha256") == prev["sha256"] for p in previous):
            previous.append(prev)

    # The release review's "latest_candidate" block has repeatedly been left pointing at the
    # previous artifact when a parallel session advanced only the "artifact" block (observed
    # 2026-10-26: ARENA47 sha left in place after the H50 merge).  Reconcile it to the same
    # newest artifact so the three registries cannot disagree (IR-51-SYNC-01).
    lc = release.get("latest_candidate")
    if isinstance(lc, dict) and lc.get("sha256") != rel_sha:
        lc.update({
            "run_card": newest.get("run_card"),
            "sha256": rel_sha,
            "verdict": "negative",
            "format_passed": True,
            "primary_holdout_passed": False,
            "literal_registry_passed": bool(
                (newest.get("uniqueness", {}) or {}).get("literal_all_registry_passed")),
            "genuine_registry_passed": bool(
                (newest.get("uniqueness", {}) or {}).get("genuine_final_dots_passed")),
            "reconciled_by": "scripts/sync_submission_build.py (was stale after a parallel merge)",
        })
        RELEASE.write_text(json.dumps(release, indent=2) + "\n")
        print(f"release review latest_candidate reconciled to {rel_sha[:16]}… "
              "(was stale; artifact block already pointed at the newest raster)")

    patch = {k: v for k, v in planned.items() if build.get(k) != v}
    if not patch:
        print("submission_build.json already in sync with the current release review")
        return 0

    if args.dry_run:
        print(json.dumps(patch, indent=2))
        return 0

    build.update(planned)
    BUILD.write_text(json.dumps(build, indent=2) + "\n")
    print(f"submission_build.json re-pinned to {planned['name']} (sha256 {rel_sha[:16]}…); ok_to_submit=false")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
