"""Pairwise uniqueness of candidate rasters against the nine listed GEMSDOE site files.
Directional 3 px dot overlap = fraction of candidate dots with a listed-site dot within 3 px.
Duplicate rule (CONTRIBUTING / user brief): > 0.70. Writes evidence/listed_site_uniqueness_20261029.json."""
import json, sys
from pathlib import Path
import numpy as np, rasterio
from scipy.spatial import cKDTree
ROOT = Path(__file__).resolve().parents[1]
CANDS = {
    "r3-da-hgcm (GEMSDOE33 sibling, unscored)": ROOT/".cache/registry/GEMSDOE33/docs/downloads/round3/gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif",
    "R6-1 stepprofile (repo, DO NOT SUBMIT)": ROOT/"docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif",
    "tmcg-b (repo, DO NOT SUBMIT)": ROOT/".cache/registry/GEMSDOE24/docs/downloads/gems24-tmcg-b-decoupled-basin-20261027T113937Z-6f8d042d5ee4-zeros.tif",
}
LISTED = {  # site: tag used to locate the listed file under .cache/registry
    "GEMSDOE24 (0.2477)": "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1",
    "GEMSDOE25 (0.2600)": "gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89",
    "GEMSDOE27 (0.2449)": "topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1",
    "GEMSDOE28 (0.2710)": "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f",
    "GEMSDOE31 (0.2708)": "gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc",
    "GEMSDOE32 (0.2778)": "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e",
    "GEMSDOE33 (0.2632)": "h33d-analog-tip-stepover-r30-20261004-cb490425926e",
    "GEMSDOE36 (0.2750)": "anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6",
}
def find(tag):
    hits = sorted(p for p in (ROOT/".cache/registry").rglob("*") if p.is_file() and tag in p.name and p.suffix == ".tif")
    if not hits: hits = sorted(p for p in (ROOT/"docs/downloads").rglob("*") if p.is_file() and tag in p.name and p.suffix == ".tif")
    return hits
def dots(p):
    with rasterio.open(p) as ds: a = ds.read(1)
    r, c = np.nonzero(a == 1.0)
    return np.c_[r, c].astype(float)
out = {"rule": "directional 3 px overlap > 0.70 = duplicate", "candidates": {}}
listed = {}
for site, tag in LISTED.items():
    hits = find(tag)
    if not hits: out.setdefault("missing", []).append(site); continue
    listed[site] = (hits[0], dots(hits[0]))
for cname, cpath in CANDS.items():
    cd = dots(cpath); tree_cache = {}
    rows = {}
    for site, (p, ld) in listed.items():
        t = cKDTree(ld); dd, _ = t.query(cd, k=1)
        rows[site] = {"overlap_3px": round(float((dd <= 3).mean()), 5), "file": str(p.relative_to(ROOT.parent)) if False else p.name}
    out["candidates"][cname] = {"path": str(cpath.relative_to(ROOT)) if cpath.is_relative_to(ROOT) else str(cpath), "dots": int(len(cd)), "vs_listed": rows,
                                "max_vs_listed": max(v["overlap_3px"] for v in rows.values())}
    print(cname, len(cd), {k: v["overlap_3px"] for k, v in rows.items()}, flush=True)
json.dump(out, open(ROOT/"evidence/listed_site_uniqueness_20261029.json", "w"), indent=1)
print("wrote")
