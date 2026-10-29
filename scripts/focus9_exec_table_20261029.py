#!/usr/bin/env python3
"""Nine-site executive table (2026-10-29): bytes, format, holdout and pairwise uniqueness.

Reads the nine focus-site best files named in ``evidence/nine_site_best_files_audit.json`` plus the
newest repo-generated unique candidate (``H51-1-EWSP``), resolves each to on-disk bytes, and FAILS
CLOSED unless the SHA-256 of those bytes equals the pinned digest.  For every file it records:

* format: ``gemsdoe32.submission.validate_submission_geotiff`` (the repo's validator, reused) plus
  direct checks of CRS / shape / transform against ``sample_submission.tif``, NaN counts inside and
  outside the footprint, binary-ness inside the footprint, and the dot count;
* HOLDOUT-DTI, STATIC diagnostic: ``gems32.holdout`` HIDE-RECOVER-v3.0 and SGMC-CAL-v3.0 (the same
  functions ``scripts/evaluate_holdout.py`` calls).  Static files cannot establish fold-local
  leakage-free features, so these are diagnostics, not promotion evidence;
* pairwise directional 3-px overlap (fraction of row-file dots within 3 px of column-file dots) and
  the binary correlation (phi) between footprint masks.  Literal rule: duplicate if overlap > 0.70
  or |rho| > 0.90.

Scores are never invented here.  ``published_score_OWNER_REPORT`` is copied from the audit file and
is an owner-reported number with no organizer receipt in this repository.

Run:  GEMS_DATA_DIR=.cache/gems_data python3 scripts/focus9_exec_table_20261029.py
Needs the core/external restore (scripts/restore_data.py) and the nine-site restore
(scripts/restore_nine_site_best_20261029.py).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir  # noqa: E402
from gemsdoe32.submission import validate_submission_geotiff  # noqa: E402

AUDIT = ROOT / "evidence" / "nine_site_best_files_audit.json"
OUT = ROOT / "evidence" / "focus9_exec_table_20261029.json"
FOOTPRINT_PX = 5_167_373
OVERLAP_LIMIT = 0.70
RHO_LIMIT = 0.90
NEAR_PX = 3.0

# Where each file's bytes were found on disk (first existing path whose SHA-256 matches wins).
# Audit paths for GEMSDOE24/27 do not exist in docs/downloads; their bytes are the hash-verified
# copies restored into .cache/gems_data/scored by scripts/restore_data.py.
EXTRA_CANDIDATES = {
    "GEMSDOE24": [".cache/gems_data/scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif"],
    "GEMSDOE27": [".cache/gems_data/scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif"],
    "GEMSDOE28": [".cache/registry/GEMSDOE28/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif"],
    "GEMSDOE30": [".cache/registry/GEMSDOE30/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif"],
    "GEMSDOE31": [".cache/registry/GEMSDOE31/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"],
    "GEMSDOE33": [".cache/registry/GEMSDOE33/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif"],
    "GEMSDOE36": [".cache/registry/GEMSDOE36/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif"],
}
NEWEST_UNIQUE = {
    "site": "H51-1-EWSP (newest unique candidate, not a focus-site leaderboard file)",
    "file": "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif",
    "sha256": "f66f65e469deda8ab34c380f46ffd2af23feb95a0ac45230f9829d2950651740",
    "published_score_OWNER_REPORT": None,
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve(site: str, audit_file: str, audit_sha: str) -> Path:
    """Return the first candidate path whose bytes match the pinned digest; fail closed otherwise."""
    cands = [audit_file] + EXTRA_CANDIDATES.get(site, [])
    seen = []
    for rel in cands:
        p = ROOT / rel
        if p.is_file():
            seen.append(rel)
            if sha256_file(p) == audit_sha:
                return p
    raise SystemExit(f"FAIL-CLOSED {site}: no on-disk file matches pinned sha256 {audit_sha[:12]} (checked {cands})")


def footprint_and_template(template: Path):
    with rasterio.open(template) as ds:
        a = ds.read(1)
        foot = np.isfinite(a) & (ds.read_masks(1) > 0)
        return foot, (ds.crs, ds.shape, ds.transform)


def format_checks(path: Path, foot: np.ndarray, template_grid, template: Path) -> dict:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        grid = (ds.crs, ds.shape, ds.transform)
        dtype, count, nodata = ds.dtypes[0], ds.count, ds.nodata
    inside = arr[foot]
    outside = arr[~foot]
    binary_inside = bool(np.isin(inside, [0.0, 1.0]).all())
    finite_all = np.isfinite(arr)
    rep = validate_submission_geotiff(path, template, strict_whole_array_finite=False)
    failed = [c.name for c in rep.checks if not c.passed] if hasattr(rep.checks[0], "passed") else []
    return {
        "grid_matches_template": bool(grid[0] == template_grid[0] and grid[1] == template_grid[1] and grid[2] == template_grid[2]),
        "crs": str(grid[0]),
        "shape": list(grid[1]),
        "dtype": dtype,
        "bands": count,
        "nodata_repr": str(nodata),
        "inside_footprint_finite": int(np.isfinite(inside).sum()),
        "inside_footprint_nan": int(np.isnan(inside).sum()),
        "inside_footprint_binary_0_1": binary_inside,
        "inside_footprint_min": float(np.nanmin(inside)),
        "inside_footprint_max": float(np.nanmax(inside)),
        "outside_footprint_nan": int(np.isnan(outside).sum()),
        "outside_footprint_zero": int((outside == 0).sum()),
        "outside_footprint_other": int((~np.isnan(outside) & (outside != 0)).sum()),
        "all_finite_values_in_0_1": bool(np.all((arr[finite_all] >= 0) & (arr[finite_all] <= 1))),
        "positive_dots": int((inside > 0.5).sum()),
        "repo_validator_passed": bool(rep.passed),
        "repo_validator_failed_checks": failed,
    }


def dots_of(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
    return (np.where(np.isfinite(arr), arr, 0) > 0.5) & foot


def directional_overlap(a: np.ndarray, b: np.ndarray) -> float | None:
    """Fraction of a's dots within NEAR_PX of b's dots (repo convention, registry_audit.audit_final_dots)."""
    if not a.any() or not b.any():
        return None
    return float((distance_transform_edt(~b)[a] <= NEAR_PX).mean())


def phi(a: np.ndarray, b: np.ndarray, foot: np.ndarray) -> float | None:
    x, y = a[foot].astype(float), b[foot].astype(float)
    if x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def holdout_static(mask: np.ndarray, ctx, name: str) -> dict:
    hr = holdout.evaluate_hide_and_recover(mask, ctx, b_visible_px=0.0, name=name)
    sg = holdout.evaluate_sgmc_with_ci(mask, ctx, name=name)
    return {
        "HIDE_RECOVER_v3_0": {
            "label": "HOLDOUT-DTI (static diagnostic)",
            "evaluator_version": hr["evaluator_version"],
            "n_withheld_positives": hr["n_withheld_positives"],
            "dti": round(float(hr["pooled_dti"]), 6),
            "ci95": [round(float(x), 6) for x in hr["ci95_cluster_bootstrap"]],
        },
        "SGMC_CAL_v3_0": {
            "label": "HOLDOUT-DTI (static diagnostic)",
            "evaluator_version": sg["evaluator_version"],
            "n_withheld_positives": sg["n_withheld_positives"],
            "dti": round(float(sg["sgmc_prevalence_calibrated_dti"]), 6),
            "ci95": [round(float(x), 6) for x in sg["sgmc_calibrated_ci95"]],
        },
    }


def main() -> int:
    audit = json.loads(AUDIT.read_text())
    ddir = data_dir()
    template = ddir / "sample_submission.tif"
    foot, template_grid = footprint_and_template(template)
    if int(foot.sum()) != FOOTPRINT_PX:
        raise SystemExit(f"FAIL-CLOSED footprint {int(foot.sum())} != {FOOTPRINT_PX}")
    ctx = holdout.load_holdout_context(ddir)
    if not np.array_equal(ctx.foot, foot):
        raise SystemExit("FAIL-CLOSED holdout footprint differs from sample_submission footprint")

    entries = []
    for s in audit["sites"]:
        site = s["site"]
        path = resolve(site, s["file"], s["sha256"])
        entries.append({"site": site, "leaderboard_name": s["leaderboard_name"],
                        "published_score_OWNER_REPORT": s["published_score_OWNER_REPORT"],
                        "path": path, "sha256": s["sha256"]})
    h51 = ROOT / NEWEST_UNIQUE["file"]
    if sha256_file(h51) != NEWEST_UNIQUE["sha256"]:
        raise SystemExit("FAIL-CLOSED H51 sha256 mismatch")
    entries.append({"site": NEWEST_UNIQUE["site"], "leaderboard_name": "H51-1-EWSP-BDF25D8C",
                    "published_score_OWNER_REPORT": None, "path": h51, "sha256": NEWEST_UNIQUE["sha256"]})

    rows = []
    masks = []
    for e in entries:
        fmt = format_checks(e["path"], foot, template_grid, template)
        dots = dots_of(e["path"], foot)
        masks.append(dots)
        if not fmt["inside_footprint_binary_0_1"]:
            raise SystemExit(f"FAIL-CLOSED {e['site']}: non-binary values inside footprint (static holdout requires {{0,1}})")
        hold = holdout_static(dots, ctx, name=e["path"].stem)
        rows.append({
            "site": e["site"],
            "leaderboard_name": e["leaderboard_name"],
            "file": str(e["path"].relative_to(ROOT)),
            "bytes": e["path"].stat().st_size,
            "sha256": e["sha256"],
            "sha256_matches_pin": True,
            "published_score_OWNER_REPORT": e["published_score_OWNER_REPORT"],
            "format": fmt,
            "holdout_static": hold,
        })
        print(f"{e['site']:<8} dots={fmt['positive_dots']:>6} valid={fmt['repo_validator_passed']} "
              f"HR={hold['HIDE_RECOVER_v3_0']['dti']:.6f} SG={hold['SGMC_CAL_v3_0']['dti']:.6f}", flush=True)

    n = len(entries)
    overlap = [[None] * n for _ in range(n)]
    pairs = []
    for i in range(n):
        for j in range(n):
            if i != j:
                overlap[i][j] = directional_overlap(masks[i], masks[j])
    for i in range(n):
        for j in range(i + 1, n):
            ov = max(overlap[i][j], overlap[j][i]) if overlap[i][j] is not None else None
            r = phi(masks[i], masks[j], foot)
            dup = (ov is not None and ov > OVERLAP_LIMIT) or (r is not None and abs(r) > RHO_LIMIT)
            pairs.append({"a": entries[i]["site"], "b": entries[j]["site"],
                          "a_within_3px_of_b": overlap[i][j], "b_within_3px_of_a": overlap[j][i],
                          "max_directional_overlap": ov, "binary_correlation_phi": r, "duplicate_flag": bool(dup)})
    for i, row in enumerate(rows):
        others = [p for p in pairs if entries[i]["site"] in (p["a"], p["b"])]
        row["max_overlap_vs_any_other_in_table"] = max((p["max_directional_overlap"] or 0.0) for p in others)
        row["unique_vs_all_rows_at_70pct_rule"] = not any(p["duplicate_flag"] for p in others)

    out = {
        "schema": "gemsdoe32-focus9-exec-table-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rules": {"overlap_limit": OVERLAP_LIMIT, "rho_limit": RHO_LIMIT, "near_px": NEAR_PX,
                  "footprint_px": FOOTPRINT_PX, "alpha": 0.2, "beta": 0.8, "kernel_m": 300},
        "evidence_classes": {
            "HOLDOUT-DTI": "local holdout evaluator (gems32.holdout), static diagnostic; no organizer receipt",
            "OWNER-REPORT": "leaderboard score supplied by the owner / audit file; no organizer receipt in repo",
            "ORGANIZER-CONFIRMED": "none present in this repository",
        },
        "rows": rows,
        "pairwise": pairs,
        "ordering_note": "the rows are not ranked by holdout; holdout values are shown only to document the proxy",
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
