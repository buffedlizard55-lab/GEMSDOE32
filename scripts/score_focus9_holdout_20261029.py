#!/usr/bin/env python3
"""Score the nine focus-site best files on the repo's shared HOLDOUT-DTI evaluators (2026-10-29).

Uses ONLY the shared template evaluators, unchanged:
  * gems32.holdout.evaluate_hide_and_recover  -> GEMSDOE32-HIDE-RECOVER-v3.0 (HOLDOUT-DTI)
  * gems32.holdout.evaluate_sgmc_with_ci      -> GEMSDOE32-SGMC-CAL-v3.0     (HOLDOUT-DTI)
and the shared strict binary-emission validator gems32.submission.require_binary_mask.

Input files are the nine audited files in docs/downloads/ (hash-checked against
evidence/nine_site_best_files_audit.json before scoring). Output: evidence/focus9_holdout_20261029.json.

These are HOLDOUT-DTI numbers (local holdout, not organizer scores). A score on the
leaderboard is only ORGANIZER-CONFIRMED from a submission-page receipt.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import holdout  # noqa: E402
from gems32.submission import require_binary_mask  # noqa: E402

DDIR = ROOT / ".cache" / "gems_data"
AUDIT = ROOT / "evidence" / "nine_site_best_files_audit.json"
OUT = ROOT / "evidence" / "focus9_holdout_20261029.json"
N_BOOT = 1000


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    t0 = time.time()
    audit = json.loads(AUDIT.read_text())
    ctx = holdout.load_holdout_context(DDIR)
    template = DDIR / "sample_submission.tif"
    with rasterio.open(template) as tpl:
        tpl_grid = (tpl.crs, tpl.shape, tpl.transform)

    # Repo-unique candidates scored on the same instrument (not focus-site winners; no score claimed).
    extra = [
        {"site": "UNIQUE-H51-1-EWSP", "leaderboard_name": "(none: not submitted)", "published_score_OWNER_REPORT": None,
         "file": "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif"},
        {"site": "UNIQUE-H49-1-CGTD", "leaderboard_name": "(none: not submitted)", "published_score_OWNER_REPORT": None,
         "file": "docs/downloads/gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.tif"},
    ]
    rows = []
    for s in audit["sites"] + extra:
        path = ROOT / s["file"]
        digest = sha256(path)
        if "sha256" in s and digest != s["sha256"]:
            raise SystemExit(f"{s['site']}: sha256 mismatch {digest} != {s['sha256']}")
        with rasterio.open(path) as ds:
            if ds.count != 1 or (ds.crs, ds.shape, ds.transform) != tpl_grid:
                raise SystemExit(f"{s['site']}: grid mismatch vs template")
            arr = ds.read(1)
        mask = require_binary_mask(arr, ctx.foot)  # raises on any non-{0,1} value inside footprint
        row = {
            "site": s["site"],
            "leaderboard_name": s["leaderboard_name"],
            "published_score_OWNER_REPORT": s["published_score_OWNER_REPORT"],
            "file": s["file"],
            "sha256": digest,
            "dots": int(mask.sum()),
            "nodata_outside_footprint": "NaN" if np.isnan(arr[~ctx.foot]).any() else "zero",
        }
        for b in (0.0, 2.0):
            hr = holdout.evaluate_hide_and_recover(mask, ctx, b_visible_px=b, n_boot=N_BOOT, name=s["site"])
            row[f"HOLDOUT_DTI_HIDE_RECOVER_b{int(b)}"] = {
                "label": "HOLDOUT-DTI",
                "evaluator_version": "GEMSDOE32-HIDE-RECOVER-v3.0",
                "b_visible_px": b,
                "n_withheld_positives": int(hr.get("n_withheld_positives", -1)),
                "pooled_dti": round(float(hr["pooled_dti"]), 6),
                "ci95": [round(float(x), 6) for x in hr["ci95_cluster_bootstrap"]],
            }
        sg = holdout.evaluate_sgmc_with_ci(mask, ctx, n_boot=N_BOOT, name=s["site"])
        row["HOLDOUT_DTI_SGMC_CAL"] = {
            "label": "HOLDOUT-DTI",
            "evaluator_version": "GEMSDOE32-SGMC-CAL-v3.0",
            "raw_pooled_dti": round(float(sg["sgmc_raw_pooled_dti"]), 6),
            "prevalence_calibrated_dti": round(float(sg["sgmc_prevalence_calibrated_dti"]), 6),
            "calibrated_ci95": [round(float(x), 6) for x in sg["sgmc_calibrated_ci95"]],
        }
        rows.append(row)
        print(
            f"{s['site']:9s} dots={row['dots']:6d} "
            f"HR_b0={row['HOLDOUT_DTI_HIDE_RECOVER_b0']['pooled_dti']:.6f} "
            f"HR_b2={row['HOLDOUT_DTI_HIDE_RECOVER_b2']['pooled_dti']:.6f} "
            f"SGMC={row['HOLDOUT_DTI_SGMC_CAL']['prevalence_calibrated_dti']:.6f}",
            flush=True,
        )

    doc = {
        "schema_version": 1,
        "nine_site_rows": len(audit["sites"]),
        "session": "2026-10-29",
        "purpose": "HOLDOUT-DTI of the nine focus-site best files on the shared evaluators. Not a leaderboard score.",
        "n_boot": N_BOOT,
        "footprint_px": int(ctx.foot.sum()),
        "rows": rows,
        "runtime_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} in {doc['runtime_s']} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
