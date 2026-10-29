"""Directional 3 px overlap matrix among the nine listed GEMSDOE site files (row file -> column file).
Writes evidence/listed_vs_listed_20261029.json. Duplicate rule: > 0.70."""
import json
from pathlib import Path
import numpy as np, rasterio
from scipy.spatial import cKDTree
import importlib.util
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ll", ROOT / "scripts/listed_site_uniqueness_20261029.py")
src = (ROOT / "scripts/listed_site_uniqueness_20261029.py").read_text()
LISTED = eval(src[src.index("LISTED = {") + len("LISTED = "): src.index("}\ndef find") + 1])
def find(tag):
    hits = sorted(p for p in (ROOT/".cache/registry").rglob("*") if p.is_file() and tag in p.name and p.suffix == ".tif")
    if not hits: hits = sorted(p for p in (ROOT/"docs/downloads").rglob("*") if p.is_file() and tag in p.name and p.suffix == ".tif")
    return hits
def dots(p):
    with rasterio.open(p) as ds: a = ds.read(1)
    r, c = np.nonzero(a == 1.0); return np.c_[r, c].astype(float)
D = {}; P = {}
for s, tag in LISTED.items():
    h = find(tag)
    if h: P[s] = str(h[0].relative_to(ROOT)) if h[0].is_relative_to(ROOT) else h[0].name; D[s] = dots(h[0])
sites = list(D)
M = {a: {} for a in sites}
for a in sites:
    for b in sites:
        if a == b: continue
        dd, _ = cKDTree(D[b]).query(D[a], k=1)
        M[a][b] = round(float((dd <= 3).mean()), 4)
flags = [(a, b, M[a][b]) for a in sites for b in sites if a != b and M[a][b] > 0.70]
out = {"rule": "row site's dots within 3 px of column site's dots; > 0.70 = duplicate", "n_dots": {s: int(len(D[s])) for s in sites},
       "files": P, "matrix": M, "duplicate_pairs_gt_0.70": flags}
json.dump(out, open(ROOT/"evidence/listed_vs_listed_20261029.json", "w"), indent=1)
for a, b, v in flags: print(a, "->", b, v)
print("sites", len(sites), "missing", [s for s in LISTED if s not in D])
