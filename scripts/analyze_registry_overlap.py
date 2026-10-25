#!/usr/bin/env python3
"""Forensic overlap anatomy of every scored raster this project can lay hands on.

Written 2026-10-25 (round 5) after the owner reported the first organizer score for a
GEMSDOE32 artifact: ``h33-h33-2-b2-…-zeros`` = **0.2778**.  This script measures, from the
bytes on disk only:

* each raster's dot count and distance-to-catalogue profile;
* the champion's construction claim (``solo & (dist>2px)``) pixel-exactly;
* pairwise "% of row dots within 3 px of column dots" (the parallel-run lane statistic);
* nested-family subset relations;
* a shifted-null agreement test for the champion vs the GEMSDOE36 Anderson raster.

Inputs are staged under ``$GEMS_DATA_DIR`` (default ``.cache/gems_data``) by
``scripts/fetch_mirrors.sh``-equivalent hash-verified fetches; sibling champions are listed in
``SIBLINGS`` with their source repo paths.  Output: ``evidence/registry_overlap.json``.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
G = Path(os.environ.get("GEMS_DATA_DIR", ROOT / ".cache" / "gems_data"))

RASTERS = {
    "CHAMPION_h33-2-b2_0.2778": ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "ANDERSON36_0.2750": G / "scored/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
    "SOLO28_h27-4_0.2708": G / "scored/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif",
    "RUNG30_h36-1_0.2710": G / "scored/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif",
    "EULER28_h38-1_0.2707": G / "scored/gems28-h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-allfinite.tif",
    "H33D33_0.2632": G / "scored/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "POISSON30_d28_0.2600": G / "scored/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "D28_d2-8_0.2600": G / "scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
    "D15_0.2477": G / "scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "TGC27_0.2449": G / "scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "H19-5_0.1922": G / "scored/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
}


def load_mask(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0)


def main() -> int:
    labels = load_mask(G / "labels.tif")
    with rasterio.open(G / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    d_cat = distance_transform_edt(~labels)

    masks, meta = {}, {}
    for name, path in RASTERS.items():
        m = load_mask(path)
        masks[name] = m
        d = d_cat[m]
        meta[name] = {
            "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "dots": int(m.sum()),
            "on_catalogue": int((m & labels).sum()),
            "within_1px_of_catalogue": int((d <= 1).sum()),
            "within_2px_of_catalogue": int((d <= 2).sum()),
            "within_3px_of_catalogue": int((d <= 3).sum()),
            "beyond_3px_of_catalogue": int((d > 3).sum()),
            "median_dist_to_catalogue_px": float(np.median(d)),
        }

    champ = masks["CHAMPION_h33-2-b2_0.2778"]
    solo = masks["SOLO28_h27-4_0.2708"]
    construction = {
        "champion_subset_of_solo": bool((champ & ~solo).sum() == 0),
        "champion_equals_solo_and_dist_gt_2px": bool(((solo & (d_cat > 2)) == champ).all()),
        "dots_removed_by_b2": int((solo & ~champ).sum()),
        "removed_dots_all_within_2px": bool((d_cat[solo & ~champ] <= 2).all()),
        "solo_equals_d28_and_dist_gt_1px": bool(((masks["D28_d2-8_0.2600"] & (d_cat > 1)) == solo).all()),
        "champion_subset_of_anderson": bool((champ & ~masks["ANDERSON36_0.2750"]).sum() == 0),
        "anderson_extra_dots_vs_champion": int((masks["ANDERSON36_0.2750"] & ~champ).sum()),
        "poisson30_equals_d28_dot_for_dot": bool((masks["POISSON30_d28_0.2600"] == masks["D28_d2-8_0.2600"]).all()),
        "champion_subset_of_h19_5": bool((champ & ~masks["H19-5_0.1922"]).sum() == 0),
        "d28_subset_of_h19_5": bool((masks["D28_d2-8_0.2600"] & ~masks["H19-5_0.1922"]).sum() == 0),
    }

    dts = {k: distance_transform_edt(~m) for k, m in masks.items()}
    names = list(masks)
    within3 = {r: {c: float((dts[c][masks[r]] <= 3).mean()) for c in names} for r in names}
    jaccard_vs_champion = {
        k: float((champ & masks[k]).sum() / max((champ | masks[k]).sum(), 1)) for k in names
    }

    and_m = masks["ANDERSON36_0.2750"]
    real = float((dts["ANDERSON36_0.2750"][champ] <= 3).mean())
    nulls = []
    for dy, dx in [(137, 251), (-311, 173), (419, -281), (-97, -389), (523, 61)]:
        rolled = np.roll(np.roll(and_m, dy, axis=0), dx, axis=1) & foot
        nulls.append(float((distance_transform_edt(~rolled)[champ] <= 3).mean()))

    out = {
        "generated_by": "scripts/analyze_registry_overlap.py",
        "grid": {"shape": list(labels.shape), "footprint_px": int(foot.sum()),
                 "catalogue_px": int(labels.sum())},
        "rasters": meta,
        "construction_checks": construction,
        "frac_row_dots_within_3px_of_col_dots": within3,
        "exact_dot_jaccard_vs_champion": jaccard_vs_champion,
        "champion_vs_anderson_shifted_null": {
            "real_frac_within_3px": real,
            "null_fracs": nulls,
            "null_mean": float(np.mean(nulls)),
            "ratio": float(real / np.mean(nulls)),
        },
    }
    dest = ROOT / "evidence" / "registry_overlap.json"
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps({"construction_checks": construction,
                      "null_ratio": out["champion_vs_anderson_shifted_null"]["ratio"]}, indent=1))
    print(f"wrote {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
