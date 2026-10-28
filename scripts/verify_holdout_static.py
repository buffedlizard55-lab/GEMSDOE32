#!/usr/bin/env python3
"""Static (byte-level) holdout re-check for named submission files (2026-10-28).

Runs the repo's shared evaluators, unchanged, on the exact emitted bytes of each file:
  * gems32.holdout.evaluate_hide_and_recover   (GEMSDOE32-HIDE-RECOVER-v3.0, HOLDOUT-DTI)
  * gems32.holdout.evaluate_sgmc_with_ci       (GEMSDOE32-SGMC-CAL-v3.0,      HOLDOUT-DTI)
for b_visible_px in {0, 2}. A static file has no per-fold re-emission, so these numbers are
what the downloadable file itself scores on the holdout; they are NOT leaderboard scores.
Writes evidence/holdout_static_recheck_20261028.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import holdout  # noqa: E402

DDIR = ROOT / ".cache" / "gems_data"
# Files are resolved from the independent verification JSON (SHA-verified), not hard-coded paths.
_VER = ROOT / "evidence" / "focus9_independent_verification_20261028.json"
FILES = {}
if _VER.exists():
    for _name, _row in json.loads(_VER.read_text())["candidates"].items():
        if isinstance(_row, dict) and _row.get("status") == "OK":
            FILES[_name] = ROOT / _row["path"]
else:
    FILES = {
        "GEMSDOE32 champion 0.2778 (h33-h33-2-b2)": ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "H51-1-EWSP emitted (bdf25d8c)": ROOT / "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif",
    }
OUT = ROOT / "evidence" / "holdout_static_recheck_20261028.json"


def main() -> int:
    t0 = time.time()
    ctx = holdout.load_holdout_context(DDIR)
    res = {}
    for name, path in FILES.items():
        with rasterio.open(path) as ds:
            m = (ds.read(1) > 0) & ctx.foot
        entry = {"path": str(path.relative_to(ROOT)), "dots": int(m.sum())}
        for b in (0.0, 2.0):
            hr = holdout.evaluate_hide_and_recover(m, ctx, b_visible_px=b, n_boot=300, name=name)
            entry[f"hide_recover_b{int(b)}"] = {
                "label": "HOLDOUT-DTI", "evaluator_version": "GEMSDOE32-HIDE-RECOVER-v3.0",
                "b_visible_px": b, "n_withheld_positives": int(hr.get("n_withheld_positives", -1)),
                "pooled_dti": round(float(hr["pooled_dti"]), 6),
                "ci95": [round(float(x), 6) for x in hr["ci95_cluster_bootstrap"]],
            }
        sg = holdout.evaluate_sgmc_with_ci(m, ctx, n_boot=300, name=name)
        entry["sgmc_cal"] = {
            "label": "HOLDOUT-DTI", "evaluator_version": "GEMSDOE32-SGMC-CAL-v3.0",
            "raw_pooled_dti": round(float(sg["sgmc_raw_pooled_dti"]), 6),
            "prevalence_calibrated_dti": round(float(sg["sgmc_prevalence_calibrated_dti"]), 6),
            "calibrated_ci95": [round(float(x), 6) for x in sg["sgmc_calibrated_ci95"]],
        }
        res[name] = entry
        print(name, json.dumps(entry)[:300], flush=True)
    doc = {"schema_version": 1, "purpose": "Static byte-level holdout re-check; not a leaderboard score.",
           "results": res, "runtime_s": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(doc, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
