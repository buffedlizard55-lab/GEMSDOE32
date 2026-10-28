#!/usr/bin/env python3
"""Instrument-vs-live validation (2026-10-28).

Question: does either shared static holdout instrument rank restored submissions
in the same order as their public live leaderboard scores?  If not, neither can
be used as a score *estimate* for a new file.

Inputs
  * restored competition/scored rasters in .cache/gems_data (hash-pinned mirrors,
    see registry/data_manifest.json; NOT organizer-authenticated)
  * live scores copied from docs/score-ledger.csv or the owner brief (OWNER-REPORT,
    not organizer-verified; each row names its source)

Outputs
  evidence/instrument_vs_live_20261028.json

Instruments (shared tools, unmodified): gems32.holdout.evaluate_sgmc_with_ci
(GEMSDOE32-SGMC-CAL-v3.0) and gems32.holdout.evaluate_hide_and_recover with
b_visible_px=0 (GEMSDOE32-HIDE-RECOVER-v3.0 static diagnostic).  The static HR
instrument is known to penalise files whose exclusion mask used the full catalogue;
it is reported anyway so the gap is visible.
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

# (label, path relative to data_dir(), live score, live-score source)
ITEMS = [
    ("GEMSDOE24 h25-1 d1.5", "scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE25 d2.8", "scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE27 topo-gap-closure", "scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE19 h19-5 powerlaw", "scored/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif",
     0.1922, "owner brief (ledger row present)"),
    ("GEMSDOE19 h19-4 multiline", "scored/gems19-h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan.tif",
     0.1894, "owner brief (ledger row present)"),
    ("GEMSDOE16 h16-1 baseline ridges", "scored/gems16-h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan.tif",
     0.1855, "owner brief (ledger row present)"),
    ("GEMSDOE10 h28 dotted ridge", "scored/gems10-h28-dotted-ridge-20260928T020256236880Z-6452ae1d00.tif", 0.1839,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE-ens12 7f00890a", "scored/gemsdoe-ens12-adopted-7f00890a.tif", 0.1563,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE8 Hedge-v2", "scored/8GEMSDOE_Hedge-v2_submission.tif", 0.1563,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE10 H25 ctx ridge", "scored/gems10-h25-ctx-ridge-20260927T232947704150Z-6452ae1d00.tif", 0.1280,
     "docs/score-ledger.csv (owner brief)"),
    ("GEMSDOE9 2314b599 (name says PLACEHOLDER)", "scored/gemsdoe9-PLACEHOLDER-2314b599.tif", 0.0107,
     "docs/score-ledger.csv (owner brief)"),
]
# 13GEMSDOE lattice: score taken from the owner brief only (not in ledger); included as the dense-reference control.
LATTICE = ("13GEMSDOE r13-lattice-s5 (dense reference)", "scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif", 0.0904,
           "owner brief text")


def _spearman(x: list[float], y: list[float]) -> float:
    from scipy.stats import spearmanr

    return float(spearmanr(x, y).statistic)


def main() -> int:
    ddir = data_dir()
    ctx = holdout.load_holdout_context(ddir)
    rows = []
    for label, rel, live, src in ITEMS + [LATTICE]:
        p = ddir / rel
        with rasterio.open(p) as ds:
            a = ds.read(1)
        mask = np.isfinite(a) & (a > 0) & ctx.foot
        n_dots = int(mask.sum())
        sg = holdout.evaluate_sgmc_with_ci(mask, ctx, name=label)
        hr = holdout.evaluate_hide_and_recover(mask, ctx, b_visible_px=0.0, name=label)
        rows.append({
            "label": label,
            "file": rel,
            "sha256_prefix": None,
            "dots_in_footprint": n_dots,
            "live_score_owner_report": live,
            "live_source": src,
            "sgmc_cal_dti": float(sg["sgmc_prevalence_calibrated_dti"]),
            "sgmc_cal_ci95": [float(v) for v in sg["sgmc_calibrated_ci95"]],
            "static_hide_recover_dti": float(hr["pooled_dti"]),
            "static_hide_recover_ci95": [float(v) for v in hr["ci95_cluster_bootstrap"]],
            "n_withheld_positives": int(hr["n_withheld_positives"]),
        })
        print(f"{label:45s} live={live:.4f} sgmc_cal={rows[-1]['sgmc_cal_dti']:.4f} "
              f"static_hr={rows[-1]['static_hide_recover_dti']:.4f} dots={n_dots}", flush=True)

    main_rows = rows[:-1]  # exclude dense lattice control from the correlation
    live = [r["live_score_owner_report"] for r in main_rows]
    summary = {
        "n_files_correlated": len(main_rows),
        "spearman_live_vs_sgmc_cal": _spearman(live, [r["sgmc_cal_dti"] for r in main_rows]),
        "spearman_live_vs_static_hide_recover": _spearman(live, [r["static_hide_recover_dti"] for r in main_rows]),
        "note": ("Live scores are OWNER-REPORT (no organizer receipt in repo). With n<=10 the Spearman has wide "
                 "uncertainty; a rank-correlation near 0 means the instrument does not predict live rank."),
    }
    out = {
        "schema_version": 1,
        "generated_by": "scripts/validate_instrument_vs_live.py",
        "evaluator_versions": ["GEMSDOE32-SGMC-CAL-v3.0", "GEMSDOE32-HIDE-RECOVER-v3.0 (static, b_visible_px=0)"],
        "rows": rows,
        "summary": summary,
    }
    outp = evidence_dir() / "instrument_vs_live_20261028.json"
    outp.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"wrote {outp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
