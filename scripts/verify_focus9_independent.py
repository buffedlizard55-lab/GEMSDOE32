#!/usr/bin/env python3
"""Independent re-verification of the nine focus-site files and uniqueness scan (2026-10-28).

Everything is re-derived from the raw GeoTIFF bytes (no prior audit JSON is trusted for
numbers; the audit only supplies the expected SHA-256 for each focus file, which is then
checked against the bytes actually fetched):

  * footprint = finite cells of sample_submission.tif (portal template)
  * per candidate: sha256, shape, CRS, transform, dtype, NaN inside footprint, range [0,1],
    dot count (value > 0 inside footprint), format_pass
  * uniqueness vs EVERY fetched focus-repo raster with 0 < dots <= 100,000 (protocol set),
    plus the dense registry raster r13 (206,895 dots, reported separately):
      - share of candidate dots within 3 px (Euclidean) of any registry dot  (protocol: <= 70%)
      - footprint Spearman rank correlation (protocol: <= 0.90)
  * lattice-compliance bound vs r13: how many footprint cells lie beyond 3 px of r13 dots,
    and a greedy count of how many dots could be placed there at >= 2.8 px spacing.

Not a leaderboard score. No DrivenData data is used. Writes
evidence/focus9_independent_verification_20261028.json.

Usage: .venv/bin/python scripts/verify_focus9_independent.py [--manifest /tmp/...json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
DL = ROOT / "docs" / "downloads"
DATA = ROOT / ".cache" / "gems_data"
OUT = ROOT / "evidence" / "focus9_independent_verification_20261028.json"

NEAR_PX = 3.0
MAX_RHO = 0.90
MAX_OVERLAP = 0.70
PROTOCOL_MAX_DOTS = 100_000

# site -> expected sha256 prefix (from evidence/nine_site_best_files_audit.json; re-checked below)
FOCUS_SHA = {
    "GEMSDOE24": "68d0e2e4fcc5",
    "GEMSDOE25": "91eae1ca42ec",
    "GEMSDOE27": "33003374335d",
    "GEMSDOE28": "5556aa1438fd",
    "GEMSDOE30": "8cf893ead566",
    "GEMSDOE31": "07b6db440535",
    "GEMSDOE32": "c55bafc47005",
    "GEMSDOE33": "87f857d505e2",
    "GEMSDOE36": "e15891020b9c",
}
H51 = DL / "gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif"
R13 = DATA / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_arr(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as ds:
        arr = ds.read(1).astype(np.float32)
        meta = {
            "bands": ds.count,
            "dtype": ds.dtypes[0],
            "crs": ds.crs.to_string() if ds.crs else None,
            "transform_top6": [float(x) for x in list(ds.transform)[:6]],
            "shape": [ds.height, ds.width],
            "nodata_tag": None if ds.nodata is None else str(ds.nodata),
        }
    return arr, meta


def format_row(arr: np.ndarray, meta: dict, foot: np.ndarray) -> dict:
    tr = meta["transform_top6"]
    vals = arr[foot]
    nan_in = int(np.isnan(vals).sum())
    finite_vals = vals[np.isfinite(vals)]
    rng_ok = bool(nan_in == 0 and finite_vals.size > 0 and finite_vals.min() >= 0.0 and finite_vals.max() <= 1.0)
    out_vals = arr[~foot]
    out_nonzero_finite = int(np.count_nonzero(np.isfinite(out_vals) & (out_vals != 0)))
    dots = foot & np.isfinite(arr) & (arr > 0)
    fmt = (
        meta["bands"] == 1
        and meta["crs"] == "EPSG:32611"
        and meta["shape"] == [3730, 3292]
        and meta["dtype"] == "float32"
        and rng_ok
        and abs(tr[0] - 100.0) < 1e-9 and abs(tr[4] + 100.0) < 1e-9
        and abs(tr[2] - 243350.0) < 1e-6 and abs(tr[5] - 4508550.0) < 1e-6
    )
    return {
        "bands": meta["bands"],
        "dtype": meta["dtype"],
        "crs": meta["crs"],
        "shape": meta["shape"],
        "transform_top6": tr,
        "nodata_tag": meta["nodata_tag"],
        "nan_inside_footprint": nan_in,
        "range_0_1_inside_footprint": rng_ok,
        "nonzero_finite_outside_footprint": out_nonzero_finite,
        "dots_inside_footprint": int(dots.sum()),
        "format_pass": bool(fmt),
    }


def lattice_bound(foot: np.ndarray, r13_dots: np.ndarray, min_sep: float = 2.8) -> dict:
    """Footprint cells beyond 3 px of r13 dots, and a greedy count of dots placeable there."""
    collar = binary_dilation(r13_dots, structure=_disk(3))
    outside = foot & ~collar
    n_out = int(outside.sum())
    # greedy packing with min separation (upper-bound style; scans in raster order)
    ys, xs = np.nonzero(outside)
    taken = np.zeros_like(outside)
    n_pack = 0
    r = int(np.ceil(min_sep))
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - r), min(outside.shape[0], y + r + 1)
        x0, x1 = max(0, x - r), min(outside.shape[1], x + r + 1)
        win = taken[y0:y1, x0:x1]
        yy, xx = np.mgrid[y0:y1, x0:x1]
        close = (yy - y) ** 2 + (xx - x) ** 2 < min_sep ** 2
        if not (win & close).any():
            taken[y, x] = True
            n_pack += 1
    return {
        "footprint_cells": int(foot.sum()),
        "cells_beyond_3px_of_r13_dots": n_out,
        "greedy_dots_outside_collar_min_sep_2p8": n_pack,
        "max_total_dots_if_70pct_rule_binding": int(n_pack / 0.30) if n_pack else 0,
        "note": "Greedy raster-order packing is a LOWER bound on the outside-collar dot capacity.",
    }


def _disk(r: int) -> np.ndarray:
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    return (yy * yy + xx * xx) <= r * r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / ".cache" / "registry" / "focus_manifest_for_verify.json"))
    ap.add_argument("--no-registry-scan", action="store_true")
    a = ap.parse_args()
    t0 = time.time()

    with rasterio.open(DATA / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    print(f"footprint px = {int(foot.sum())}", flush=True)

    manifest = json.loads(Path(a.manifest).read_text())
    by_sha = {r["sha256"]: r for r in manifest["rasters"] if r.get("status") == "ok"}

    candidates: dict[str, dict] = {}
    for site, pref in FOCUS_SHA.items():
        hit = [r for r in by_sha.values() if r["sha256"].startswith(pref)]
        if len(hit) != 1:
            candidates[site] = {"status": f"NOT FOUND ({len(hit)} hits)"}
            continue
        r = hit[0]
        candidates[site] = {"path": ROOT / r["local"], "repo_path": f"{r['repo']}/{r['path']}", "ref": r["ref"]}
    candidates["H51-1-EWSP (candidate)"] = {"path": H51, "repo_path": "local docs/downloads"}

    cand_rows = {}
    cand_mask = {}
    cand_rank = {}
    for name, c in candidates.items():
        if "path" not in c:
            cand_rows[name] = c
            continue
        arr, meta = load_arr(c["path"])
        row = {"status": "OK", "path": str(c["path"].relative_to(ROOT)), "repo_path": c["repo_path"],
               "ref": c.get("ref"), "sha256": sha256(c["path"]), "bytes": c["path"].stat().st_size}
        row.update(format_row(arr, meta, foot))
        cand_rows[name] = row
        dots = foot & np.isfinite(arr) & (arr > 0)
        cand_mask[name] = dots
        cand_rank[name] = rankdata(np.where(np.isfinite(arr[foot]), arr[foot], 0.0))
        del arr
    print("candidates loaded", len(cand_mask), f"{time.time()-t0:.0f}s", flush=True)

    names = list(cand_mask.keys())

    # Pairwise among candidates (dist from B's dots, check A's dots)
    pairs = []
    for b in names:
        if cand_mask[b].sum() == 0:
            continue
        db = distance_transform_edt(~cand_mask[b])
        for an in names:
            if an == b:
                continue
            ma = cand_mask[an]
            if ma.sum() == 0:
                continue
            ov = float((db[ma] <= NEAR_PX).mean())
            rho = float(np.corrcoef(cand_rank[an], cand_rank[b])[0, 1])
            pairs.append({"A": an, "B": b, "share_A_dots_within_3px_of_B": round(ov, 6),
                          "spearman_footprint": round(rho, 6),
                          "fails_70pct": ov > MAX_OVERLAP, "fails_rho_090": rho > MAX_RHO})
        del db

    # Registry scan: every fetched focus raster with 0 < dots <= 100k (protocol set)
    reg_rows = []
    skipped_shape: list[dict] = []
    n_over_100k = 0
    r13_dots = None
    r13_rank = None
    if not a.no_registry_scan:
        ok_rows = [r for r in manifest["rasters"] if r.get("status") == "ok"]
        for r in ok_rows:
            p = ROOT / r["local"]
            if not p.exists():
                continue
            arr, meta = load_arr(p)
            if list(arr.shape) != [foot.shape[0], foot.shape[1]]:
                skipped_shape.append({"repo": r["repo"], "path": r["path"], "shape": list(arr.shape)})
                del arr
                continue
            dots = foot & np.isfinite(arr) & (arr > 0)
            nd = int(dots.sum())
            if nd == 0:
                del arr
                continue
            if nd > PROTOCOL_MAX_DOTS:
                n_over_100k += 1
            rr = rankdata(np.where(np.isfinite(arr[foot]), arr[foot], 0.0))
            del arr
            row = {"registry_repo": r["repo"], "registry_path": r["path"], "registry_dots": nd,
                   "registry_sha256": r["sha256"][:16]}
            db = distance_transform_edt(~dots)  # once per registry raster
            for cn in names:
                if cand_mask[cn].sum() == 0:
                    continue
                ov = float((db[cand_mask[cn]] <= NEAR_PX).mean())
                rho = float(np.corrcoef(cand_rank[cn], rr)[0, 1])
                # identical dot set (same submission in another file variant, e.g. -nan vs -zeros)
                same = bool(nd == int(cand_mask[cn].sum()) and ov >= 0.999999 and rho >= 0.999999)
                row.setdefault("per_candidate", {})[cn] = {"share_within_3px": round(ov, 6),
                                                          "spearman": round(rho, 6),
                                                          "identical_dot_set": same}
            del db
            reg_rows.append(row)
            print(f"  scanned {r['repo']}/{r['path'][:60]} dots={nd}", flush=True)
        # r13 separately (dense; protocol set excludes it by size)
        if R13.exists():
            arr, _ = load_arr(R13)
            r13_dots = foot & np.isfinite(arr) & (arr > 0)
            r13_rank = rankdata(np.where(np.isfinite(arr[foot]), arr[foot], 0.0))
            del arr

    summary = {}
    for cn in names:
        if cand_mask[cn].sum() == 0:
            continue
        rows_c = [row for row in reg_rows if cn in row.get("per_candidate", {})
                  and not row["per_candidate"][cn]["identical_dot_set"]]
        rows_p = [row for row in rows_c if row["registry_dots"] <= PROTOCOL_MAX_DOTS]
        vals_ov = [row["per_candidate"][cn]["share_within_3px"] for row in rows_p]
        vals_rho = [row["per_candidate"][cn]["spearman"] for row in rows_p]
        worst_row = max(rows_p, key=lambda row: row["per_candidate"][cn]["share_within_3px"], default=None)
        all_ov = [row["per_candidate"][cn]["share_within_3px"] for row in rows_c]
        n_identical = sum(1 for row in reg_rows if cn in row.get("per_candidate", {}) and row["per_candidate"][cn]["identical_dot_set"])
        worst_all = max(rows_c, key=lambda row: row["per_candidate"][cn]["share_within_3px"], default=None)
        r13_share = None
        r13_rho = None
        if r13_dots is not None:
            db = distance_transform_edt(~r13_dots)
            r13_share = round(float((db[cand_mask[cn]] <= NEAR_PX).mean()), 6)
            r13_rho = round(float(np.corrcoef(cand_rank[cn], r13_rank)[0, 1]), 6)
            del db
        summary[cn] = {
            "n_registry_le100k_compared": len(vals_ov),
            "identical_dot_set_variants_excluded": n_identical,
            "max_share_within_3px_vs_registry_le100k": max(vals_ov) if vals_ov else None,
            "max_spearman_vs_registry_le100k": max(vals_rho) if vals_rho else None,
            "worst_registry_raster_le100k": (f"{worst_row['registry_repo']}/{worst_row['registry_path']}" if worst_row else None),
            "max_share_within_3px_vs_all_registry_incl_dense": max(all_ov) if all_ov else None,
            "worst_registry_raster_all": (f"{worst_all['registry_repo']}/{worst_all['registry_path']}" if worst_all else None),
            "share_within_3px_vs_r13_dense": r13_share,
            "passes_70pct_and_rho_vs_registry_le100k": bool(vals_ov) and max(vals_ov) <= MAX_OVERLAP and max(vals_rho) <= MAX_RHO,
            "passes_70pct_and_rho_vs_all_registry": bool(all_ov) and max(all_ov) <= MAX_OVERLAP and max(
                row["per_candidate"][cn]["spearman"] for row in rows_c) <= MAX_RHO,
            "spearman_vs_r13_dense": r13_rho,
            "passes_70pct_vs_r13": (r13_share is not None and r13_share <= MAX_OVERLAP),
        }

    lattice = lattice_bound(foot, r13_dots, 2.8) if r13_dots is not None else None

    doc = {
        "schema_version": 2,
        "session": "2026-10-28 independent re-verification (arena/73853a05-gemsdoe32)",
        "purpose": "Recomputed from raw rasters. NOT a leaderboard score; no DrivenData data used.",
        "footprint_px": int(foot.sum()),
        "footprint_source": "sample_submission.tif finite cells (5,167,373 expected)",
        "manifest_source": str(Path(a.manifest).name),
        "thresholds": {"near_px": NEAR_PX, "max_overlap": MAX_OVERLAP, "max_spearman": MAX_RHO,
                       "protocol_max_dots_for_registry_scan": PROTOCOL_MAX_DOTS},
        "candidates": cand_rows,
        "pairwise_among_candidates": pairs,
        "uniqueness_summary": summary,
        "r13_lattice_capacity": lattice,
        "registry_rasters_scanned": len(reg_rows),
        "registry_rows_file": "evidence/focus9_registry_scan_rows_20261028.json",
        "registry_rasters_skipped_shape_mismatch": skipped_shape,
        "registry_rasters_over_100k_dots_not_in_protocol_set": n_over_100k,
        "runtime_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(doc, indent=1))
    (ROOT / "evidence" / "focus9_registry_scan_rows_20261028.json").write_text(json.dumps(reg_rows, separators=(",", ":")))
    print(json.dumps({k: doc[k] for k in ("footprint_px", "registry_rasters_scanned", "runtime_s")}, indent=1))
    for k, v in summary.items():
        print(k, v)
    print("r13 lattice", lattice)
    return 0


if __name__ == "__main__":
    sys.exit(main())
