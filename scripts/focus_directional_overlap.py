#!/usr/bin/env python3
"""Directional 3-px overlap between binary focus-site rasters (2026-10-29 review).

The protocol's lane rule is directional: "more than 70% of YOUR dots fall within 3 px of one
registry raster's dots". `rescore_focus_downloads.py` reports the max of both directions, which
flags subsets as 1.0. This script reports both directions explicitly so the rule can be read
off directly. Output: evidence/focus_directional_overlap_20261029.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FILES = {
    "GEMSDOE32 h33-2-b2 (0.2778 owner-reported)": "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "GEMSDOE25 d2-8 (0.2600 owner-reported; zeros variant)": "docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif",
    "GEMSDOE24/25 d2-8 -nan bytes (sha 91eae1ca)": ".cache/gems_data/scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
    "GEMSDOE24 d1-5 (0.2477 owner-reported)": ".cache/gems_data/scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE27 topo-gap-closure (0.2449 owner-reported)": ".cache/gems_data/scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28 h27-4-r1 solo (0.2708 owner-reported)": ".cache/gems_data/scored/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif",
    "GEMSDOE32 H51-1-EWSP (this review's unique candidate)": "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif",
    "GEMSDOE32 H49-1-CGTD": "docs/downloads/gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.tif",
    "GEMSDOE32 H-GEO-VENT 28000": "docs/downloads/gemsdoe32-H-GEO-VENT-28000-20261027T174146Z-3c5837e9-zeros.tif",
    "GEMSDOE32 H19-5 powerlaw (registry, 121131 dots, nan)": ".cache/gems_data/scored/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
    "GEMSDOE37-class 80k registry raster (13gems r13-lattice)": ".cache/gems_data/scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
}


def mask_of(p: Path) -> np.ndarray:
    with rasterio.open(p) as ds:
        a = ds.read(1)
    return a == 1


def near3(m: np.ndarray) -> np.ndarray:
    return ndimage.distance_transform_edt(~m) <= 3.0


def main() -> int:
    masks, near = {}, {}
    for label, rel in FILES.items():
        p = ROOT / rel
        if not p.exists():
            print("MISSING", rel)
            continue
        masks[label] = mask_of(p)
        near[label] = near3(masks[label])
    labels = list(masks)
    pairs = []
    for a in labels:
        for b in labels:
            if a == b:
                continue
            na = int(masks[a].sum())
            frac = float((masks[a] & near[b]).sum() / na)
            pairs.append({"your_dots": a, "registry_or_peer": b, "your_dots_within_3px": round(frac, 6),
                          "lane_rule_70pct_violated": frac > 0.70})
    out = {
        "schema": "gemsdoe32.focus_directional_overlap.v1",
        "generated_by": "scripts/focus_directional_overlap.py",
        "rule": "your dots within 3 px of peer dots; > 0.70 = duplicate (protocol lane rule)",
        "dots": {k: int(v.sum()) for k, v in masks.items()},
        "pairs": pairs,
    }
    dest = ROOT / "evidence" / "focus_directional_overlap_20261029.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", dest, "pairs", len(pairs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
