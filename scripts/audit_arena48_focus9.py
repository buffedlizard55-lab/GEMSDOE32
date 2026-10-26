#!/usr/bin/env python3
"""ARENA48: byte-level audit of the nine focus-site winner rasters.

Reads the winner file for each of GEMSDOE24/25/27/28/30/31/32/33/36 from the
refreshed focus-registry cache (.cache/registry, manifest-pinned), and measures —
from bytes, this session — dot counts, exact intersections/subset relations and
directional within-3-px overlaps.  Scores are NOT measured here: every score in the
output is copied from the owner-provided ledger in the session brief and labelled
OWNER-REPORT (no organizer receipt exists in this repo, IR-32-SCORE-01).
Output: evidence/arena48_focus9_overlap.json
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]

WINNERS = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5", 0.2477, "H19-5 thinned at 1.5 px (parent)"),
    ("GEMSDOE25", "dotted-h19-5-d2-8", 0.2600, "H19-5 thinned at 2.8 px (D2.8)"),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5", 0.2449, "D1.5 + topographic gap-closure mass"),
    ("GEMSDOE28", "h36-1-rung30-blind-r1", 0.2710, "best of the GEMSDOE28 four-file ~0.27 B=1/blind cluster"),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090", 0.2600, "D2.8 Poisson off-catalogue (claimed dot-identical to GEMSDOE25)"),
    ("GEMSDOE31", "h27-4-solo-d28", 0.2708, "solo/B=1 (D2.8 minus dots <=100 m from catalogue)"),
    ("GEMSDOE32", "h33-h33-2-b2", 0.2778, "champion B=2 (solo minus dots 100-200 m from catalogue)"),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30", 0.2632, "B=1 + analog fault-tip/step-over additions"),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854", 0.2750, "claimed champion superset + 1,200 Anderson/PINN additions"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    manifest = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    with rasterio.open(ROOT / ".cache/gems_data/sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    rows, masks = [], {}
    for site, needle, score, what in WINNERS:
        hits = [r for r in manifest["rasters"] if r["repo"] == site and needle in r["path"]
                and r.get("status") == "ok"]
        if not hits:
            rows.append({"site": site, "status": "NOT FOUND in refreshed registry", "needle": needle})
            continue
        # prefer the all-finite / zeros variant when several encodings of one mask exist
        hits.sort(key=lambda r: (0 if ("zeros" in r["path"] or "allfinite" in r["path"]) else 1, r["path"]))
        r = hits[0]
        p = ROOT / r["local"]
        with rasterio.open(p) as ds:
            a = ds.read(1)
        m = np.isfinite(a) & (a > 0) & foot
        masks[site] = m
        rows.append({"site": site, "file": r["path"], "repo_ref": r["ref"], "sha256": sha256(p),
                     "manifest_sha256_matches": bool(sha256(p) == r["sha256"]),
                     "dots": int(m.sum()), "owner_reported_score": score,
                     "evidence_class": "OWNER-REPORT (no organizer receipt in this repo)",
                     "what_it_is": what, "all_variants_in_registry": [h["path"] for h in hits]})
    sites = [r["site"] for r in rows if r["site"] in masks]
    dts = {s: distance_transform_edt(~masks[s]) for s in sites}
    pair = {}
    for a in sites:
        for b in sites:
            if a == b:
                continue
            ma, mb = masks[a], masks[b]
            inter = int((ma & mb).sum())
            pair[f"{a}->{b}"] = {
                "directional_within_3px_of_other": round(float((dts[b][ma] <= 3).mean()), 6),
                "exact_shared_dots": inter,
                "share_of_source_dots_shared_exactly": round(inter / max(int(ma.sum()), 1), 6),
                "source_is_exact_subset_of_other": bool(inter == int(ma.sum())),
            }
    directional = [v["directional_within_3px_of_other"] for v in pair.values()]
    out = {"generated_by": "scripts/audit_arena48_focus9.py",
           "registry_generated_utc": manifest.get("generated_utc"),
           "registry_refs": manifest.get("refs"),
           "winners": rows, "pairwise": pair,
           "summary": {"n_winner_masks_measured": len(sites),
                       "min_directional_within_3px_among_winners": min(directional) if directional else None,
                       "max_directional_within_3px_among_winners": max(directional) if directional else None,
                       "all_pairs_exceed_70pct_stop": bool(directional and min(directional) > 0.70),
                       "gem25_equals_gem30_exactly": bool(
                           "GEMSDOE25" in masks and "GEMSDOE30" in masks
                           and np.array_equal(masks["GEMSDOE25"], masks["GEMSDOE30"])),
                       "champion32_subset_of_gem36": bool(
                           "GEMSDOE32" in masks and "GEMSDOE36" in masks
                           and int((masks["GEMSDOE32"] & masks["GEMSDOE36"]).sum()) == int(masks["GEMSDOE32"].sum())),
                       "champion32_subset_of_d28_gem25": bool(
                           "GEMSDOE32" in masks and "GEMSDOE25" in masks
                           and int((masks["GEMSDOE32"] & masks["GEMSDOE25"]).sum()) == int(masks["GEMSDOE32"].sum())),
                       "note": "Scores are OWNER-REPORT; geometry above is measured from bytes this session."}}
    (ROOT / "evidence/arena48_focus9_overlap.json").write_text(json.dumps(out, indent=2) + "\n")
    for r in rows:
        print(r.get("site"), r.get("dots"), r.get("file", r.get("status")))
    print(json.dumps(out["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
