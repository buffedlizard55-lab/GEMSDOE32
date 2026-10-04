#!/usr/bin/env python3
"""Regenerate `registry/submission_build.json` -- the file the site renders as its ONE-CLICK primary.

The primary is chosen by a fixed, pre-committed rule rather than by preference:

1. it must be **slot-eligible** under the standing gate (live-mirror 4/4 folds, positive live-mirror
   margin, live-anchored safety factor >= 2.0 for any removal arm);
2. among eligible candidates it must have the **highest live-anchored projected DTI**;
3. ties are broken toward the **pure removal arm** -- a single-mechanism change on the axis that
   already has a measured live gain carries less model risk than one that also adds mass.

The 0.2708 anchor (the group's best live-scored emission) is always kept in the pack, one click away,
so the owner can fall back to a file whose leaderboard behaviour is already known.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from gems32.feed import sha256


def _pick_primary(cands: list[dict]) -> dict | None:
    eligible = [c for c in cands if c.get("slot_eligible")]
    if not eligible:
        return None
    def key(c: dict):
        proj = c.get("live_anchor_projection") or 0.0
        pure_removal = 0 if (c.get("removal", {}).get("n_removed", 0) > 0
                             and c["emitted_pixels"] < c.get("base_dots", 10 ** 9)) else 1
        return (-proj, pure_removal, -c["lm_mean"])
    return sorted(eligible, key=key)[0]


def main() -> int:
    ev_path = ROOT / "evidence" / "h33_validation.json"
    ev = json.loads(ev_path.read_text())
    cands = ev["candidates"]
    base = ev["base"]

    primary = _pick_primary(cands)
    if primary is None:
        print("[build_submission_build] no slot-eligible candidate; leaving the registry untouched")
        return 1

    dl = ROOT / "docs" / "downloads"
    # locate the written pair by the emitted pixel count and the candidate slug
    stem = f"gemsdoe32-h33-{primary['candidate_id'].lower()}-"
    zeros = sorted(dl.glob(stem + "*-zeros.tif"))
    nans = sorted(dl.glob(stem + "*-nan.tif"))
    if not zeros or not nans:
        print(f"[build_submission_build] missing GeoTIFFs for {primary['candidate_id']}")
        return 1
    z, n = zeros[0], nans[0]
    # a .zip containing exactly one GeoTIFF is also accepted by the portal
    zp = z.with_suffix(".zip")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(z, arcname=z.name)

    name = z.stem
    # the DrivenData note field is capped at 200 characters (GEMSDOE28 measured 192/200 for its
    # own note), so the note is built to a hard budget and asserted below.
    note = (
        f"GEMSDOE32 {primary['candidate_id']} | flank B=2 prune on the 0.2708 base: "
        f"{primary['emitted_pixels']:,} dots, 0 within 200 m of the catalogue; "
        f"live-mirror +{primary.get('lm_margin_vs_base', 0):.5f} in 4/4 folds, "
        f"safety {primary.get('live_anchor_safety') or 0:.2f}, "
        f"projected {primary.get('live_anchor_projection') or 0:.4f}; UNSCORED"
    )
    assert len(note) <= 200, f"submission note is {len(note)} chars; the portal caps it at 200"
    status = (
        f"PRIMARY = {primary['candidate_id']} ({primary['description']}). "
        f"{primary['emitted_pixels']:,} dots; live-mirror (spatially blocked, off-catalogue truth, "
        f"validated on the known live orderings) +{primary.get('lm_margin_vs_base', 0):.6f} in 4/4 "
        f"quadrants over the 0.2708 base; live-anchored safety factor "
        f"{primary.get('live_anchor_safety') or 0:.2f}; projected live DTI "
        f"{primary.get('live_anchor_projection') or 0:.4f} (a MODEL, not a score). "
        "NO ORGANISER SCORE EXISTS for this or any artifact in this repository."
    )

    pack = [{
        "role": "SECONDARY (slot-eligible)",
        "path": str(n.relative_to(ROOT)),
        "sha256": sha256(n), "bytes": n.stat().st_size,
        "positive_px": primary["emitted_pixels"],
        "note": "NaN-outside twin in the competition's own format (identical values inside the footprint)",
    }]
    # every other download the site offers, so nothing is a dead button
    for p in sorted(dl.glob("*.tif")):
        rel = str(p.relative_to(ROOT))
        if rel in {str(z.relative_to(ROOT)), str(n.relative_to(ROOT))}:
            continue
        try:
            with rasterio.open(p) as ds:
                a = ds.read(1)
            pos = int(((a > 0) & np.isfinite(a)).sum())
        except Exception:
            pos = None
        pack.append({"role": "AVAILABLE DOWNLOAD", "path": rel, "sha256": sha256(p),
                     "bytes": p.stat().st_size, "positive_px": pos,
                     "note": "kept for the audit trail; see docs/research/ for its status"})

    out = {
        "name": name,
        "note": note,
        "status_line": status,
        "file": {"path": str(z.relative_to(ROOT)), "sha256": sha256(z),
                 "bytes": z.stat().st_size, "positive_px": primary["emitted_pixels"]},
        "file_zeros": {"path": str(z.relative_to(ROOT)), "sha256": sha256(z),
                       "bytes": z.stat().st_size},
        "zip": {"path": str(zp.relative_to(ROOT)), "sha256": sha256(zp), "bytes": zp.stat().st_size},
        "candidate_id": primary["candidate_id"],
        "hypothesis": primary["hypothesis"],
        "selection_rule": ("highest live-anchored projected DTI among slot-eligible candidates, "
                           "ties broken toward the pure removal arm"),
        "live_anchor": primary.get("live_anchor"),
        "lm": {"mean": primary["lm_mean"], "margin_vs_base": primary.get("lm_margin_vs_base"),
               "folds_beat_base": primary.get("lm_folds_beat_base"),
               "per_fold": primary.get("lm_per_fold")},
        "catalogue_hidden_mean": primary["catalogue_hidden_mean"],
        "anchor": {
            "role": "ANCHOR -- the group's best live-scored emission",
            "path": "docs/downloads/gems32-probe-S1-ANCHOR-identical-to-live-02600.tif",
            "note": ("bit-identical in-footprint to the owner-reported 0.2708 / 0.2600 emissions; "
                     "upload this if you want a file whose leaderboard behaviour is already known"),
        },
        "pack": pack,
        "rule": ("0.2708 base (gems28-h27-4-r1-solo-d2-8, 40,199 dots) minus every dot within 2 px "
                 "(200 m) of the published catalogue"),
        "provenance": ("built by scripts/run_h33_validation.py; every digest re-read from the "
                       "written bytes; receipt evidence/h33_validation.json and "
                       "docs/research/hypotheses-round4.md"),
    }
    (ROOT / "registry" / "submission_build.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"[build_submission_build] primary = {name} ({primary['emitted_pixels']:,} dots, "
          f"projected live {primary.get('live_anchor_projection'):.4f})")
    print(f"[build_submission_build] note ({len(note)} chars): {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
