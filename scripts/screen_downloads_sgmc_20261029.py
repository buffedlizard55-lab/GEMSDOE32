#!/usr/bin/env python3
"""SCREEN (not validation): every binary GeoTIFF in docs/downloads on SGMC-CAL-v3.0 with a uniqueness gate.

Why this exists: `scripts/focus9_exec_table_20261029.py` found that, over the nine published focus-site
files, the static SGMC-CAL-v3.0 DTI rank-correlates with the owner-reported leaderboard scores
(Spearman rho = 0.95, n = 9), while the static HIDE-RECOVER-v3.0 DTI rank-correlates negatively
(rho = -0.85). This screen therefore ranks candidate bytes by SGMC-CAL only.

Rules applied (literal, from the repo's gate; see registry/current_status.json):
  * uniqueness vs each of the nine focus-site files: directional 3-px overlap <= 0.70 in BOTH
    directions, and |phi| <= 0.90 (binary correlation of footprint masks);
  * the candidate must be a binary {0,1} GeoTIFF on the template grid.

Limits (stated, not hidden):
  * Only docs/downloads is screened (75 binary rasters). The full 451-raster registry gate is NOT run here.
  * CIs are unpaired 256-block cluster bootstraps from the evaluator. A paired comparison to the champion
    needs a dedicated run and is NOT computed here.
  * Output is HOLDOUT-DTI (static diagnostic). It is never a leaderboard score.

Run: GEMS_DATA_DIR=.cache/gems_data python3 scripts/screen_downloads_sgmc_20261029.py
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

from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir  # noqa: E402

TABLE = ROOT / "evidence" / "focus9_exec_table_20261029.json"
OUT = ROOT / "evidence" / "downloads_sgmc_screen_20261029.json"
DL = ROOT / "docs" / "downloads"
OVERLAP_LIMIT = 0.70
PHI_LIMIT = 0.90
NEAR_PX = 3.0
CHAMPION_SHA = "c55bafc47005"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_dots(path: Path, foot: np.ndarray):
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        grid = (ds.crs, ds.shape, ds.transform)
    fin = np.where(np.isfinite(arr), arr, 0)
    binary_in = bool(np.isin(arr[foot], [0.0, 1.0]).all())
    return (fin > 0.5) & foot, grid, binary_in


def phi(a: np.ndarray, b: np.ndarray, foot: np.ndarray):
    x, y = a[foot].astype(float), b[foot].astype(float)
    if x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def main() -> int:
    ddir = data_dir()
    template = ddir / "sample_submission.tif"
    with rasterio.open(template) as ds:
        foot = np.isfinite(ds.read(1)) & (ds.read_masks(1) > 0)
        tgrid = (ds.crs, ds.shape, ds.transform)
    ctx = holdout.load_holdout_context(ddir)

    table = json.loads(TABLE.read_text())
    focus = [r for r in table["rows"] if r["published_score_OWNER_REPORT"] is not None]
    if len(focus) != 9:
        raise SystemExit("FAIL-CLOSED: expected nine focus rows")
    focus_masks, focus_dt, focus_names = [], [], []
    for r in focus:
        m, g, _ = load_dots(ROOT / r["file"], foot)
        if g != tgrid:
            raise SystemExit(f"FAIL-CLOSED grid mismatch {r['file']}")
        focus_masks.append(m)
        focus_dt.append(distance_transform_edt(~m))
        focus_names.append(r["site"])

    rows = []
    for p in sorted(DL.glob("*.tif")):
        mask, grid, binary_in = load_dots(p, foot)
        if grid != tgrid or not binary_in or not mask.any():
            continue
        sha = sha256_file(p)
        sg = holdout.evaluate_sgmc_with_ci(mask, ctx, name=p.stem)
        dt_self = distance_transform_edt(~mask) if mask.any() else None
        fwd, rev, phis = [], [], []
        for m, dt_f in zip(focus_masks, focus_dt):
            if m is None or not m.any():
                fwd.append(None); rev.append(None); phis.append(None)
                continue
            fwd.append(float((dt_f[mask] <= NEAR_PX).mean()))     # candidate dots near focus dots
            rev.append(float((dt_self[m] <= NEAR_PX).mean()))     # focus dots near candidate dots
            phis.append(phi(mask, m, foot))
        worst = max(max(f, r) for f, r in zip(fwd, rev))
        worst_site = focus_names[int(np.argmax([max(f, r) for f, r in zip(fwd, rev)]))]
        dup_phi = any(v is not None and abs(v) > PHI_LIMIT for v in phis)
        unique = worst <= OVERLAP_LIMIT and not dup_phi
        rows.append({
            "file": str(p.relative_to(ROOT)),
            "sha256": sha,
            "is_champion_bytes": sha.startswith(CHAMPION_SHA),
            "positive_dots": int(mask.sum()),
            "sgmc_calibrated_dti": round(float(sg["sgmc_prevalence_calibrated_dti"]), 6),
            "sgmc_calibrated_ci95_unpaired": [round(float(x), 6) for x in sg["sgmc_calibrated_ci95"]],
            "n_withheld_positives": int(sg["n_withheld_positives"]),
            "evaluator_version": sg["evaluator_version"],
            "max_directional_overlap_vs_focus9": round(worst, 6),
            "closest_focus_site": worst_site,
            "max_abs_phi_vs_focus9": round(max(abs(v) for v in phis if v is not None), 6),
            "unique_vs_focus9_literal_70pct": bool(unique),
        })
        print(f"{p.name[:70]:<70} SG={rows[-1]['sgmc_calibrated_dti']:.6f} "
              f"maxov={worst:.4f} unique={unique}", flush=True)

    rows.sort(key=lambda r: -r["sgmc_calibrated_dti"])
    out = {
        "schema": "gemsdoe32-downloads-sgmc-screen-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "label": "HOLDOUT-DTI (SGMC-CAL-v3.0, static screen, unpaired CI); NOT a leaderboard score",
        "champion_sgmc_calibrated_dti_reference": 0.064121,
        "rules": {"overlap_limit_both_directions": OVERLAP_LIMIT, "phi_limit": PHI_LIMIT, "near_px": NEAR_PX,
                  "compared_against": "nine focus-site files in focus9_exec_table_20261029.json"},
        "n_candidates": len(rows),
        "rows": rows,
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} candidates)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
