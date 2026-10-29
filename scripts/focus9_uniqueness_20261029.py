#!/usr/bin/env python3
"""Directional 3-px dot-overlap matrix for the nine focus-site best files plus the two repo-unique candidates.

Lane rule (organizer-independent, from the repo's PARALLEL-RUN PROTOCOL rule 1): a raster is a duplicate if
MORE THAN 70% of ITS dots fall within 3 px of ONE other raster's dots. The matrix is directional:
cell[row, col] = fraction of row's dots within 3 px of col's dots. Reuses `mask_of` / `near3` from
scripts/focus_directional_overlap.py (no private fork). Output: evidence/focus9_uniqueness_20261029.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from focus_directional_overlap import mask_of, near3  # noqa: E402

OUT = ROOT / "evidence" / "focus9_uniqueness_20261029.json"
RULE_PCT = 70.0


def main() -> int:
    audit = json.loads((ROOT / "evidence" / "nine_site_best_files_audit.json").read_text())
    items = [(s["site"], s["file"]) for s in audit["sites"]]
    items += [
        ("UNIQUE-H51-1-EWSP", "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif"),
        ("UNIQUE-H49-1-CGTD", "docs/downloads/gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.tif"),
    ]
    masks = {}
    hashes = {}
    for name, rel in items:
        p = ROOT / rel
        masks[name] = mask_of(p)
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    names = [n for n, _ in items]
    near = {n: near3(masks[n]) for n in names}

    cell = {}
    for r in names:
        for c in names:
            if r == c:
                continue
            tot = int(masks[r].sum())
            cell[f"{r} -> {c}"] = round(float((masks[r] & near[c]).sum() / max(tot, 1)) * 100.0, 4)

    identical = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            if int(masks[a].sum()) == int(masks[b].sum()) and cell[f"{a} -> {b}"] == 100.0 and cell[f"{b} -> {a}"] == 100.0:
                identical.append([a, b])

    verdict = {}
    for r in names:
        worst = max((cell[f"{r} -> {c}"], c) for c in names if c != r)
        verdict[r] = {
            "dots": int(masks[r].sum()),
            "sha256": hashes[r],
            "max_directional_overlap_pct_vs_other_listed": worst[0],
            "max_overlap_vs": worst[1],
            "passes_70pct_rule_vs_all_listed": worst[0] <= RULE_PCT,
        }

    doc = {
        "schema_version": 1,
        "session": "2026-10-29",
        "rule": "duplicate if > 70% of a raster's dots lie within 3 px of one other raster's dots (directional)",
        "rule_pct": RULE_PCT,
        "rows_are_source": True,
        "matrix_pct": cell,
        "identical_dot_sets": identical,
        "per_file": verdict,
        "scope_note": "Only the 9 focus files + 2 repo-unique candidates. Not a full 30-repo registry scan; that scan is evidence/focus9_independent_verification_20261028.json and the H51 registry audit.",
    }
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    for n in names:
        v = verdict[n]
        print(f"{n:22s} dots={v['dots']:6d} max={v['max_directional_overlap_pct_vs_other_listed']:6.2f}% vs {v['max_overlap_vs']:22s} pass={v['passes_70pct_rule_vs_all_listed']}")
    print("identical dot sets:", identical)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
