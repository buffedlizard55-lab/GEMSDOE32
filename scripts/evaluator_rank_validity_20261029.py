#!/usr/bin/env python3
"""Evaluator-validity experiment (negative-results deliverable): does each static evaluator rank the
nine published focus-site files the way their owner-reported leaderboard scores rank them?

Input : evidence/focus9_exec_table_20261029.json (HOLDOUT-DTI static values + OWNER-REPORT scores)
Output: evidence/evaluator_rank_validity_20261029.json

Caveats written into the output: n = 9; scores are OWNER-REPORT (no organizer receipt); GEMSDOE25 and
GEMSDOE30 are dot-identical (ties); SGMC-CAL is circular for any file whose generator reads the SGMC raster
as a model input (see IR-20261029-S01), so a high SGMC rank correlation is NOT evidence of skill by itself.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from scipy.stats import kendalltau, spearmanr

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "evidence" / "focus9_exec_table_20261029.json"
OUT = ROOT / "evidence" / "evaluator_rank_validity_20261029.json"


def main() -> int:
    rows = [r for r in json.loads(SRC.read_text())["rows"] if r["published_score_OWNER_REPORT"] is not None]
    pub = [r["published_score_OWNER_REPORT"] for r in rows]
    res = {}
    for key, label in [("HIDE_RECOVER_v3_0", "HIDE-RECOVER-v3.0"), ("SGMC_CAL_v3_0", "SGMC-CAL-v3.0")]:
        x = [r["holdout_static"][key]["dti"] for r in rows]
        rho, p = spearmanr(pub, x)
        tau, pt = kendalltau(pub, x)
        res[label] = {"n": len(x), "spearman_rho": round(float(rho), 4), "spearman_p": float(p),
                      "kendall_tau": round(float(tau), 4), "kendall_p": float(pt),
                      "label": "HOLDOUT-DTI (static diagnostic) vs OWNER-REPORT leaderboard scores"}
    out = {
        "schema": "gemsdoe32-evaluator-rank-validity-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "question": "Does each static evaluator order the nine published files like the owner-reported scores?",
        "result": res,
        "verdict": ("HIDE-RECOVER ranks them in the OPPOSITE order (rho < 0). SGMC-CAL ranks them in the same order, "
                    "but that agreement is not yet trustworthy: it is circular for files that use the SGMC raster as an input, "
                    "and n = 9 with two dot-identical sites. Neither evaluator is cleared as the canonical proxy (IR-45-EVAL-02)."),
        "caveats": [
            "n = 9 published scores, OWNER-REPORT only",
            "GEMSDOE25 and GEMSDOE30 are dot-identical, so they contribute tied values",
            "SGMC-CAL truth = off-catalogue SGMC traces; any generator that reads that raster as a feature is in-sample (IR-20261029-S01)",
        ],
        "rows": [{"site": r["site"], "published_OWNER_REPORT": r["published_score_OWNER_REPORT"],
                  "HIDE_RECOVER": r["holdout_static"]["HIDE_RECOVER_v3_0"]["dti"],
                  "SGMC_CAL": r["holdout_static"]["SGMC_CAL_v3_0"]["dti"]} for r in rows],
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    for k, v in res.items():
        print(k, v["spearman_rho"], v["spearman_p"], v["kendall_tau"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
