"""Run the spatially blocked HIDE-RECOVER DTI holdout on every candidate that passes the
pre-declared 2026-10-29 eligibility rule (see evidence/candidate_sweep_20261029.json and
evidence/sgmc_leakage_probe_20261029.json). Writes evidence/holdout_eligible_pool_20261029.json.
Labels: HOLDOUT-DTI (never a leaderboard score)."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sweep = json.load(open(ROOT / "evidence/candidate_sweep_20261029.json"))
probe = json.load(open(ROOT / "evidence/sgmc_leakage_probe_20261029.json"))
enr = {r["path"]: r["enrichment"] for r in probe["top25"]}
flag = re.compile(r"sgmc|offcat|off-cat|RESEARCH", re.I)
elig = [r for r in sweep["rows"] if r["nondegenerate_gate_pass"] and r["sgmc_cal"] is not None
        and r["path"] in enr and enr[r["path"]] <= 2.5 and not flag.search(r["path"])]
out = []
for r in sorted(elig, key=lambda r: -r["sgmc_cal"]):
    p = r["path"]
    res = subprocess.run([sys.executable, str(ROOT / "scripts/evaluate_holdout.py"), p],
                         capture_output=True, text=True, cwd=ROOT, timeout=600)
    j = json.loads(res.stdout)
    hr = j["hide_and_recover"]
    out.append({"path": p, "sgmc_cal": r["sgmc_cal"], "sgmc_cal_ci95": r["sgmc_cal_ci95"],
                "maxOV_vs_pool": r["max_overlap_vs_pool"], "literal_lattice_overlap": r["literal_lattice_overlap"],
                "HOLDOUT_DTI_pooled": hr["pooled_dti"], "HOLDOUT_DTI_ci95": hr["ci95_cluster_bootstrap"],
                "label": "HOLDOUT-DTI"})
    print(p[-60:], round(hr["pooled_dti"], 6), flush=True)
json.dump({"champion_reference": {"path": "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
           "HOLDOUT_DTI_pooled": 0.004515, "ci95": [0.003816, 0.005262]}, "rows": out},
          open(ROOT / "evidence/holdout_eligible_pool_20261029.json", "w"), indent=1)
print("DONE", len(out))
