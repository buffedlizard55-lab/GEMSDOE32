"""Leakage probe: share of each candidate's dots within 1 px of SGMC off-catalogue truth,
relative to the base rate of footprint cells. Probes the top-25 SGMC-cal passing candidates from
evidence/candidate_sweep_20261029.json. Writes evidence/sgmc_leakage_probe_20261029.json."""
import json, sys
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import holdout
ctx = holdout.load_holdout_context(ROOT / ".cache/gems_data")
foot = np.asarray(ctx.foot, bool); H, W = foot.shape
sg = np.zeros((H, W), bool); sg[ctx.sgmc_truth_coords] = True
dsg = ndimage.distance_transform_edt(~sg)
base1 = float(((dsg <= 1) & foot).sum() / foot.sum())
d = json.load(open(ROOT / "evidence/candidate_sweep_20261029.json"))
top = sorted([r for r in d["rows"] if r["nondegenerate_gate_pass"]], key=lambda r: -(r["sgmc_cal"] or -1))[:25]
res = []
for r in top:
    with rasterio.open(r["path"]) as ds: a = ds.read(1)
    m = (a == 1.0) & foot
    s1 = float((dsg[m] <= 1).mean())
    res.append(dict(path=r["path"], dots=r["dots"], sgmc=r["sgmc_cal"], sgmc_ci=r["sgmc_cal_ci95"], maxOV=r["max_overlap_vs_pool"],
                    maxPhi=r["max_phi_vs_pool"], share_le1px_sgmc_truth=round(s1, 5), enrichment=round(s1 / base1, 2), aliases=r["aliases"]))
json.dump({"base_rate_within1px": base1, "top25": res}, open(ROOT / "evidence/sgmc_leakage_probe_20261029.json", "w"), indent=1)
print("base", round(base1, 5), "rows", len(res))
