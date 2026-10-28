#!/usr/bin/env python3
"""Reproduce the comparator numbers quoted in the registry, from bytes, with the shared evaluator.

Checks (each printed and written to evidence/comparator_reproduction_20261028.json):
  1. "0.2778 champion proxy" HOLDOUT-DTI 0.099202 is the GEMSDOE25 d2.8 PARENT masked with a
     visible-only 2-px collar (run_h51_ewsp.py: champ_hr = evaluate_hide_and_recover(d28_parent, b=2)).
     It is NOT the H33-B2 file's own holdout.
  2. H33-B2 file (0.2778) static SGMC-cal = 0.064121 (registry match).
  3. H51 EXP1 file static SGMC-cal = 0.063032 (registry match); its static hide-and-recover is far
     lower because its full-catalogue B=2 exclusion removes dots near every catalogue fault.
Label: HOLDOUT-DTI (GEMSDOE32-HIDE-RECOVER-v3.0 / SGMC-CAL-v3.0, static diagnostic path).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir, evidence_dir  # noqa: E402

H33 = "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
H51 = "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif"
D28_PARENT = "scored/gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"


def mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0) & foot


def main() -> int:
    ddir = data_dir()
    ctx = holdout.load_holdout_context(ddir)
    res: dict = {"schema_version": 1, "generated_by": "scripts/reproduce_comparators_20261028.py", "checks": {}}

    hr_proxy = holdout.evaluate_hide_and_recover(mask(ddir / D28_PARENT, ctx.foot), ctx, b_visible_px=2.0,
                                                 name="d28_parent_visible_collar_2px")
    res["checks"]["registry_0p2778_proxy_is_d28_parent_collared"] = {
        "label": "HOLDOUT-DTI", "evaluator_version": "GEMSDOE32-HIDE-RECOVER-v3.0",
        "source_file": D28_PARENT, "b_visible_px": 2.0, "n_withheld_positives": int(hr_proxy["n_withheld_positives"]),
        "pooled_dti": float(hr_proxy["pooled_dti"]), "ci95": [float(v) for v in hr_proxy["ci95_cluster_bootstrap"]],
        "registry_value": 0.099202, "matches_registry": bool(abs(hr_proxy["pooled_dti"] - 0.099202) < 1e-5),
    }
    m33 = mask(ROOT / H33, ctx.foot)
    sg33 = holdout.evaluate_sgmc_with_ci(m33, ctx, name="h33_b2")
    res["checks"]["h33_b2_file_sgmc_cal"] = {
        "label": "HOLDOUT-DTI", "evaluator_version": "GEMSDOE32-SGMC-CAL-v3.0", "file": H33,
        "n_withheld_positives": int(sg33["n_withheld_positives"]),
        "prevalence_calibrated_dti": float(sg33["sgmc_prevalence_calibrated_dti"]),
        "ci95": [float(v) for v in sg33["sgmc_calibrated_ci95"]], "registry_value": 0.064121,
        "matches_registry": bool(abs(sg33["sgmc_prevalence_calibrated_dti"] - 0.064121) < 1e-5),
    }
    m51 = mask(ROOT / H51, ctx.foot)
    sg51 = holdout.evaluate_sgmc_with_ci(m51, ctx, name="h51_exp1")
    hr51 = holdout.evaluate_hide_and_recover(m51, ctx, b_visible_px=0.0, name="h51_exp1_static")
    res["checks"]["h51_exp1_file_static"] = {
        "file": H51,
        "sgmc_cal_dti": float(sg51["sgmc_prevalence_calibrated_dti"]),
        "sgmc_cal_ci95": [float(v) for v in sg51["sgmc_calibrated_ci95"]], "registry_sgmc_value": 0.063032,
        "static_hide_recover_dti": float(hr51["pooled_dti"]),
        "static_hide_recover_ci95": [float(v) for v in hr51["ci95_cluster_bootstrap"]],
        "note": ("Registry HR 0.115134 for this experiment comes from the per-fold re-emission in "
                 "scripts/run_h51_ewsp.py; the shipped file alone does not reproduce it under the static path."),
    }
    outp = evidence_dir() / "comparator_reproduction_20261028.json"
    outp.write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
