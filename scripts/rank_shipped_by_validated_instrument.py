#!/usr/bin/env python3
"""Rank every shipped binary GeoTIFF by the instrument that tracked live rank, and gate uniqueness.

Context (see evidence/instrument_vs_live_20261028.json): SGMC-prevalence-calibrated DTI
(GEMSDOE32-SGMC-CAL-v3.0) has Spearman ~0.90 with owner-reported live scores (n=11), while the
static hide-and-recover diagnostic has ~0.05.  So this script ranks shipped files by SGMC-cal.

For each unique-sha `*-zeros.tif` in docs/downloads (plus restored scored rasters) it records:
  * strict format/range validation via gems32.submission.validate_submission_geotiff
  * dots = finite & >0 & in footprint
  * SGMC-cal DTI + 95% CI (shared evaluator, unmodified)
  * max directional overlap: fraction of THIS file's dots within 3.0 px (Euclidean) of ANY dot in
    another file, against (a) the 13GEMSDOE lattice, (b) every other shipped/restored file.
    Literal registry rule: > 70 % => duplicate.
Coverage is stated in the output: only files present on disk, NOT the full 610-raster registry.

Output: evidence/shipped_ranked_validated_20261028.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir  # noqa: E402
from gemsdoe32.submission import validate_submission_geotiff  # noqa: E402

LATTICE_NAME = "scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
# SGMC-independence flags (the SGMC-cal instrument is NOT independent evidence for these files).
#  * hsupsgmc: run_hsupsgmc.py sets sgmc_off_north_px as TRAINING positives (receipt key
#    "sgmc_off_north_px_used_as_positives"), so SGMC-cal evaluates on data used for fitting.
#  * bayesopt: src/gems32/bo_surrogate.py selects designs on sgmc_prevalence_calibrated_dti
#    (incumbent-beat criterion), so SGMC-cal is a selection criterion for these files.
SGMC_FLAGS = {}
DIST_PX = 3.0


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dot_coords(p: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(p) as ds:
        a = ds.read(1)
    m = np.isfinite(a) & (a > 0) & foot
    return np.column_stack(np.nonzero(m)).astype(np.float64)


def overlap_within(a_xy: np.ndarray, tree_b: cKDTree) -> float:
    if len(a_xy) == 0:
        return 0.0
    d, _ = tree_b.query(a_xy, k=1, distance_upper_bound=DIST_PX)
    return float(np.isfinite(d).mean())


def main() -> int:
    ddir = data_dir()
    template = ddir / "sample_submission.tif"
    with rasterio.open(template) as ds:
        foot = np.isfinite(ds.read(1)) & (ds.read_masks(1) > 0)
    ctx = holdout.load_holdout_context(ddir)

    # Candidate pool: unique-sha binary zeros tifs in docs/downloads + restored scored rasters.
    pool: dict[str, Path] = {}
    for p in sorted(downloads_dir().glob("*-zeros.tif")):
        pool.setdefault(sha256(p), p)
    for p in sorted((ddir / "scored").glob("*.tif")):
        pool.setdefault(sha256(p), p)
    # Dedupe by sha; keep the first-seen path per sha, record duplicate names.
    items = list(pool.items())
    print(f"unique-sha rasters: {len(items)}", flush=True)

    coords = {}
    for sh, p in items:
        coords[sh] = dot_coords(p, foot)
    trees = {sh: cKDTree(c) for sh, c in coords.items() if len(c)}

    lattice_sha = sha256(ddir / LATTICE_NAME)
    rows = []
    for sh, p in items:
        rel = str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)
        val = validate_submission_geotiff(p, template, strict_whole_array_finite=True)
        sg = holdout.evaluate_sgmc_with_ci(_mask(p, foot), ctx, name=p.name)
        xy = coords[sh]
        # Overlap with every other unique raster (directional: share of this file's dots near other's dots)
        worst = (0.0, None)
        worst_nolat = (0.0, None)
        for osh, otree in trees.items():
            if osh == sh:
                continue
            f = overlap_within(xy, otree)
            if f > worst[0]:
                worst = (f, pool[osh].name)
            if osh != lattice_sha and f > worst_nolat[0]:
                worst_nolat = (f, pool[osh].name)
        lat = overlap_within(xy, trees[lattice_sha]) if lattice_sha in trees else None
        rows.append({
            "file": rel,
            "sha256": sh,
            "dots": int(len(xy)),
            "format_passed": bool(val.passed),
            "sgmc_cal_dti": float(sg["sgmc_prevalence_calibrated_dti"]),
            "sgmc_cal_ci95": [float(v) for v in sg["sgmc_calibrated_ci95"]],
            "max_within3px_vs_any_other": round(worst[0], 4),
            "max_within3px_vs_other_file": worst[1],
            "max_within3px_vs_any_non_lattice_file": round(worst_nolat[0], 4),
            "max_within3px_vs_non_lattice_file_name": worst_nolat[1],
            "literal_70pct_gate_vs_non_lattice": worst_nolat[0] <= 0.70,
            "sgmc_independence_flag": SGMC_FLAGS.get(p.name),
            "within3px_vs_13gems_lattice": round(lat, 4) if lat is not None else None,
            "literal_70pct_gate_vs_any": worst[0] <= 0.70,
            "literal_70pct_gate_vs_lattice": (lat is not None and lat <= 0.70),
        })
        print(f"{p.name[:70]:70s} dots={len(xy):6d} sgmc={rows[-1]['sgmc_cal_dti']:.4f} "
              f"maxov={worst[0]:.3f} lat={rows[-1]['within3px_vs_13gems_lattice']}", flush=True)

    for r in rows:
        nm = Path(r["file"]).name
        if "hsupsgmc" in nm:
            r["sgmc_independence_flag"] = "CONTAMINATED: SGMC north px used as training positives (run_hsupsgmc.py)"
        elif "bayesopt" in nm:
            r["sgmc_independence_flag"] = "SELECTION-BIASED: BO objective includes SGMC-cal (bo_surrogate.py)"
    rows.sort(key=lambda r: r["sgmc_cal_dti"], reverse=True)
    out = {
        "schema_version": 1,
        "generated_by": "scripts/rank_shipped_by_validated_instrument.py",
        "coverage": ("Only rasters on disk: docs/downloads/*-zeros.tif (unique sha) + restored scored rasters. "
                     "NOT the full 610-raster registry; the 70% overlap test is therefore a lower bound on true overlap."),
        "instrument": "GEMSDOE32-SGMC-CAL-v3.0 (HOLDOUT-DTI, prevalence-calibrated, 62,703 withheld off-catalogue positives)",
        "overlap_rule": f"fraction of this file's dots within {DIST_PX} px (Euclidean) of another file's dots; literal >70% = duplicate",
        "n_rasters": len(rows),
        "rows": rows,
    }
    outp = evidence_dir() / "shipped_ranked_validated_20261028.json"
    outp.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {outp}")
    return 0


def _mask(p: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(p) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0) & foot


if __name__ == "__main__":
    raise SystemExit(main())
