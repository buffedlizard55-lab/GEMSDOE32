#!/usr/bin/env python3
"""PROJECTION ONLY (never a score): linear map from SGMC-cal DTI to owner-reported live score.

Training points: the 11 restored files in evidence/instrument_vs_live_20261028.json plus the
H33-B2 champion (SGMC-cal 0.064121 -> owner-reported live 0.2778). Output includes a 95% prediction
interval.  Caveats: n=12, owner-reported live scores, SGMC contamination excluded for training rows,
and a selection-biased SGMC criterion for later candidates.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32.paths import evidence_dir  # noqa: E402

CANDIDATES = {
    "H47-1 LDGI (0eb8a25c)": 0.0659,
    "H51-1 EXP1 (bdf25d8c)": 0.063032,
    "H49-1 CGTD (f3e24fb5)": 0.0664,
    "ARENA49-PCG (54e97629)": 0.0715,
    "ARENA9 PGRN-PU (4f7aba9b)": 0.0878,
    "ARENA-EULER-E1 (71f0a187)": 0.0663,
    "H33-B2 champion (e5eb6e7e)": 0.064121,
}


def main() -> int:
    ev = json.loads((evidence_dir() / "instrument_vs_live_20261028.json").read_text())
    x = [r["sgmc_cal_dti"] for r in ev["rows"] if r["label"] != "13GEMSDOE r13-lattice-s5 (dense reference)"]
    y = [r["live_score_owner_report"] for r in ev["rows"] if r["label"] != "13GEMSDOE r13-lattice-s5 (dense reference)"]
    x.append(0.064121)
    y.append(0.2778)
    x = np.array(x)
    y = np.array(y)
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    s2 = float(resid @ resid) / (n - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    tcrit = stats.t.ppf(0.975, n - 2)
    out = {"n_training_points": n, "intercept": float(beta[0]), "slope": float(beta[1]),
           "residual_sd": float(np.sqrt(s2)), "r_squared": float(1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))),
           "label": "PROJECTION - NOT A SCORE", "candidates": {}}
    for name, xv in CANDIDATES.items():
        v = np.array([1.0, xv])
        mu = float(v @ beta)
        se_pred = float(np.sqrt(s2 * (1 + v @ np.linalg.inv(X.T @ X) @ v)))
        out["candidates"][name] = {"sgmc_cal": xv, "projected_live_mean": round(mu, 4),
                                   "projected_95pi": [round(mu - tcrit * se_pred, 4), round(mu + tcrit * se_pred, 4)],
                                   "beats_0p2778_projection": bool(mu > 0.2778)}
    p = evidence_dir() / "live_projection_from_sgmc_20261028.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
