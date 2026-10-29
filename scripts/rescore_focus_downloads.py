#!/usr/bin/env python3
"""Re-score every binary GeoTIFF in docs/downloads and the restored `scored/` rasters.

Purpose (2026-10-29 review): replace owner-reported scores with numbers produced by the
repo's canonical evaluator (`scripts/evaluate_holdout.py` -> `gems32.holdout`), and record
the format, hash, binary-ness and pairwise 3-px overlap facts needed for the nine-site table.

Labels: every holdout number here is HOLDOUT-DTI (evaluator version, withheld positives,
95% spatial-block CI). Nothing in this script is a leaderboard score. Only a submission-page
receipt can be ORGANIZER-CONFIRMED, and none is present in this repository.

Usage:
    PYTHONPATH=src python scripts/rescore_focus_downloads.py --out evidence/focus_rescore_20261029.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_holdout import evaluate_path  # noqa: E402
from gems32.paths import data_dir  # noqa: E402

EXPECTED_TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
FOCUS_SITES = ["24", "25", "27", "28", "30", "31", "32", "33", "36"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def format_check(p: Path) -> dict:
    with rasterio.open(p) as ds:
        a = ds.read(1)
        out = {
            "count": ds.count,
            "dtype": ds.dtypes[0],
            "epsg": ds.crs.to_epsg() if ds.crs else None,
            "shape": [ds.height, ds.width],
            "transform_ok": tuple(ds.transform)[:6] == EXPECTED_TRANSFORM,
            "nodata": ds.nodata,
        }
    finite = np.isfinite(a)
    out["finite_fraction"] = float(finite.mean())
    out["nan_cells"] = int((~finite).sum())
    fin_vals = a[finite]
    out["min_finite"] = float(fin_vals.min()) if fin_vals.size else None
    out["max_finite"] = float(fin_vals.max()) if fin_vals.size else None
    out["values_in_01_finite"] = bool(fin_vals.size and fin_vals.min() >= 0 and fin_vals.max() <= 1)
    out["is_binary_0_1"] = bool(fin_vals.size and np.all((fin_vals == 0) | (fin_vals == 1)))
    out["nonzero_finite"] = int(np.count_nonzero(fin_vals))
    return out


def three_px_mask(mask: np.ndarray) -> np.ndarray:
    """Cells within 3 px (Chebyshev-style disc) of a positive cell."""
    dist = ndimage.distance_transform_edt(~mask)
    return dist <= 3.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", nargs="*", default=None, help="optional filename substrings to restrict")
    args = ap.parse_args()

    ddir = data_dir()
    cands: list[Path] = sorted((ROOT / "docs" / "downloads").glob("*-zeros.tif"))
    cands += sorted((ROOT / ".cache" / "gems_data" / "scored").glob("*.tif"))
    if args.only:
        cands = [p for p in cands if any(s in p.name for s in args.only)]

    rows = []
    masks = {}
    for p in cands:
        row = {"file": str(p.relative_to(ROOT)), "sha256": sha256(p), "bytes": p.stat().st_size}
        try:
            fc = format_check(p)
        except Exception as exc:  # pragma: no cover - recorded, not hidden
            row["format_error"] = repr(exc)
            rows.append(row)
            continue
        row["format"] = fc
        if fc["is_binary_0_1"]:
            try:
                ev = evaluate_path(p, ddir=ddir, name=p.stem)
                hr = ev["hide_and_recover"]
                sg = ev["sgmc_off_catalogue"]
                row["holdout"] = {
                    "evaluator_version_hide_recover": hr["evaluator_version"],
                    "hide_recover_pooled_dti": hr["pooled_dti"],
                    "hide_recover_ci95": hr["ci95_cluster_bootstrap"],
                    "hide_recover_withheld_positives": hr["n_withheld_positives"],
                    "evaluator_version_sgmc": sg["evaluator_version"],
                    "sgmc_calibrated_dti": sg["sgmc_prevalence_calibrated_dti"],
                    "sgmc_calibrated_ci95": sg["sgmc_calibrated_ci95"],
                    "sgmc_withheld_positives": sg["n_withheld_positives"],
                    "label": "HOLDOUT-DTI (repo canonical evaluator; not a leaderboard score)",
                }
                m = (rasterio.open(p).read(1) == 1)
                masks[p.name] = m
            except Exception as exc:
                row["holdout_error"] = repr(exc)
        else:
            row["holdout"] = None
            row["holdout_skip_reason"] = (
                "continuous or NaN-bearing raster: canonical binary evaluator refuses to threshold "
                "probabilities (scripts/gems32/submission.require_binary_mask)"
            )
        rows.append(row)

    # Pairwise 3-px overlap (fraction of this raster's dots within 3 px of the other's dots)
    names = list(masks)
    pairs = []
    cache3 = {n: three_px_mask(masks[n]) for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            na, nb = int(masks[a].sum()), int(masks[b].sum())
            if na == 0 or nb == 0:
                continue
            fa = float((masks[a] & cache3[b]).sum() / na)
            fb = float((masks[b] & cache3[a]).sum() / nb)
            pairs.append({"a": a, "b": b, "a_within3px_of_b": fa, "b_within3px_of_a": fb,
                          "max_overlap": max(fa, fb)})
    pairs.sort(key=lambda r: -r["max_overlap"])

    doc = {
        "schema": "gemsdoe32.focus_rescore.v1",
        "generated_by": "scripts/rescore_focus_downloads.py",
        "label": "HOLDOUT-DTI only. Not a leaderboard score; no submission-page receipt in repo.",
        "data_dir": str(ddir),
        "focus_sites": FOCUS_SITES,
        "n_candidates": len(rows),
        "n_binary_scored": len(masks),
        "rows": rows,
        "pairwise_3px_overlap_top25": pairs[:25],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(doc, indent=2) + "\n")
    print(f"wrote {args.out} candidates={len(rows)} binary_scored={len(masks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
