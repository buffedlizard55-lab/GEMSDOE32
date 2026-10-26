#!/usr/bin/env python3
"""Byte-level audit of each focus site's SUBMITTED-VARIANT file (the one named on the leaderboard).

For every site it locates the pinned raster in `registry/focus_registry_manifest.json`, verifies the
SHA-256 against the manifest, and records grid, dot count and pairwise uniqueness against the other
eight site files on the footprint:
  - full-footprint Spearman of the value surface (duplicate gate: > 0.90);
  - directional share of this file's dots within 3 px of the other file's dots (duplicate gate: > 70%).

It writes evidence/nine_site_best_files_audit.json. Nothing here is a leaderboard score.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32.paths import data_dir  # noqa: E402

# (site, leaderboard file stem, manifest repo path suffix, leaderboard score as published)
SITES = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan", "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477),
    ("GEMSDOE25", "dotted-h19-5-d2-8-20261002-e56ea318af89-nan", "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan", "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449),
    ("GEMSDOE28", "h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan", "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca", "gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600),
    ("GEMSDOE31", "h27-4-solo-d28-20261004-8acb75e1-nan", "gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708),
    ("GEMSDOE32", "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros", "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", 0.2778),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30-20261004-cb490425926e", "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros", "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750),
]


def _local_path(man_rows: list[dict], site: str, suffix: str) -> dict:
    hits = [r for r in man_rows if r["repo"] == site and r["path"].endswith(suffix)]
    if len(hits) != 1:
        raise SystemExit(f"{site}: expected exactly one manifest entry for {suffix}, found {len(hits)}")
    return hits[0]


def _ranks(a: np.ndarray) -> np.ndarray:
    r = rankdata(a).astype(np.float64)
    r -= r.mean()
    n = np.linalg.norm(r)
    return r / n if n > 0 else r


def main() -> int:
    man = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())["rasters"]
    with rasterio.open(data_dir() / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    records = []
    arrays = {}
    for site, stem, suffix, pub in SITES:
        row = _local_path(man, site, suffix)
        path = ROOT / row["local"]
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        if sha != row["sha256"]:
            raise SystemExit(f"{site}: SHA-256 mismatch for {path}")
        with rasterio.open(path) as ds:
            arr = ds.read(1).astype(np.float64)
            facts = {
                "shape": [int(ds.height), int(ds.width)],
                "crs": ds.crs.to_string() if ds.crs else None,
                "dtype": ds.dtypes[0],
                "nodata": ds.nodata,
                "bands": int(ds.count),
            }
        fin = np.isfinite(arr)
        in_foot = arr[foot]
        dots = np.isfinite(arr) & (arr > 0) & foot
        arrays[site] = (arr, dots)
        records.append(
            {
                "site": site,
                "leaderboard_name": stem,
                "published_score_OWNER_REPORT": pub,
                "file": str(row["path"]),
                "github_ref": row["ref"],
                "bytes": len(data),
                "sha256": sha,
                "sha256_matches_manifest": True,
                **facts,
                "finite_in_footprint": int(np.isfinite(in_foot).sum()),
                "nan_in_footprint": int(np.isnan(in_foot).sum()),
                "footprint_px": int(foot.sum()),
                "min_in_footprint": float(np.nanmin(in_foot)) if np.isfinite(in_foot).any() else None,
                "max_in_footprint": float(np.nanmax(in_foot)) if np.isfinite(in_foot).any() else None,
                "unique_values_in_footprint": int(np.unique(in_foot[np.isfinite(in_foot)]).size),
                "positive_dots": int(dots.sum()),
                "all_finite_zero_outside_or_nan": bool(np.all((arr[~foot] == 0) | ~np.isfinite(arr[~foot]))),
            }
        )
        print(f"{site}: {path.name} dots={int(dots.sum())} finite={int(np.isfinite(in_foot).sum())}", flush=True)

    # pairwise uniqueness on the footprint
    pairs = []
    ranks = {s: _ranks(np.nan_to_num(arrays[s][0][foot], nan=0.0)) for s in arrays}
    dist_inv = {s: distance_transform_edt(~arrays[s][1]) for s in arrays}
    names = [s[0] for s in SITES]
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            rho = float(np.dot(ranks[a], ranks[b]))
            da = arrays[a][1]
            db = arrays[b][1]
            ov_ab = float((dist_inv[b][da] <= 3.0).mean()) if da.any() else None
            ov_ba = float((dist_inv[a][db] <= 3.0).mean()) if db.any() else None
            pairs.append(
                {
                    "a": a,
                    "b": b,
                    "spearman_footprint": round(rho, 6),
                    "a_dots_within_3px_of_b": round(ov_ab, 6) if ov_ab is not None else None,
                    "b_dots_within_3px_of_a": round(ov_ba, 6) if ov_ba is not None else None,
                    "duplicate_flag_rho_gt_0_90": bool(abs(rho) > 0.90),
                    "duplicate_flag_overlap_gt_70pct": bool((ov_ab or 0) > 0.70 or (ov_ba or 0) > 0.70),
                }
            )
    out = {
        "schema_version": 1,
        "purpose": "Byte-level audit of the 9 focus sites' submitted-variant files. Not a leaderboard score.",
        "footprint_px": int(foot.sum()),
        "sites": records,
        "pairwise": pairs,
        "sources": [
            "registry/focus_registry_manifest.json (pinned refs; SHA-256 verified)",
            "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
        ],
    }
    (ROOT / "evidence" / "nine_site_best_files_audit.json").write_text(json.dumps(out, indent=2) + "\n")
    print("wrote evidence/nine_site_best_files_audit.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
