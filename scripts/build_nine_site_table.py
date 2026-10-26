#!/usr/bin/env python3
"""Nine-focus-site table: best OWNER-REPORT file per site, pinned download link, LLI leave-one-out estimate,
and uniqueness of each file against EVERY other restored live-scored GEMSDOE submission (byte/mask aliases of
itself excluded).  Output: evidence/nine_site_table_h47.json (rendered by scripts/build_site.py)."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32.paths import data_dir  # noqa: E402

BEST = {  # site -> substring of the best OWNER-REPORT submission (standing prompt 2026-10-26)
    "GEMSDOE24": "h25-1-dotted-h19-5-d1-5", "GEMSDOE25": "dotted-h19-5-d2-8-20261002-e56ea318af89",
    "GEMSDOE27": "topo-gap-closure-t-v2-on-d1-5", "GEMSDOE28": "h36-1-rung30-blind-r1",
    "GEMSDOE30": "d28-poisson300m-offcat-44090", "GEMSDOE31": "h27-4-solo-d28",
    "GEMSDOE32": "h33-h33-2-b2", "GEMSDOE33": "h33d-analog-tip-stepover-r30",
    "GEMSDOE36": "anderson-geothermal-pinn-38854",
}


def main() -> int:
    ddir = data_dir()
    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ddir / "labels.tif") as ds:
        lab = (ds.read(1) > 0) & foot
    act = foot & ~lab
    led = json.loads((ROOT / "evidence" / "live_ledger_rasters.json").read_text())
    rows = [r for r in led["rows"] if r.get("status") == "ok"]
    masks, digests = [], []
    for r in rows:
        with rasterio.open(ROOT / r["local"]) as ds:
            a = ds.read(1)
        m = np.isfinite(a) & (a > 0) & act
        masks.append(m)
        digests.append(hashlib.sha256(np.packbits(m).tobytes()).hexdigest()[:16])
    yy, xx = np.ogrid[-3:4, -3:4]
    disk = (yy * yy + xx * xx) <= 9
    best_idx = {}
    for site, key in BEST.items():
        cand = [i for i, r in enumerate(rows) if r["site"] == site and key in r["submission"]]
        if cand:
            best_idx[site] = cand[0]
    over = {s: [] for s in best_idx}
    space_filling = set()
    for j, r in enumerate(rows):
        dil = binary_dilation(masks[j], structure=disk)
        if float(dil[foot].mean()) >= 0.70:
            space_filling.add(j)   # e.g. the 5-px lattice: every map overlaps it; reported, not decisive
        for s, i in best_idx.items():
            if digests[j] == digests[i]:
                continue  # the file itself or a byte/mask-identical alias
            over[s].append((float(dil[masks[i]].mean()), j))
    lli = {}
    p = ROOT / "evidence" / "live_ledger_inversion.json"
    if p.exists():
        d = json.loads(p.read_text())
        des = d["designs"].get("S3") or next(iter(d["designs"].values()))
        for pr in des["per_raster"]:
            lli[pr["submission"]] = pr
    out = []
    for site, i in best_idx.items():
        r = rows[i]
        ov = sorted([o for o in over[site] if o[1] not in space_filling], reverse=True)
        top = ov[0]
        aliases = sorted({f"{rows[j]['site']}:{rows[j]['submission']}" for j in range(len(rows))
                          if digests[j] == digests[i] and j != i})
        dup_of = [f"{rows[j]['site']}:{rows[j]['submission']}" for v, j in ov if v > 0.70]
        L = lli.get(r["submission"], {})
        if not L:  # this file's mask was collapsed into a byte-identical alias in the LLI fit
            for j in range(len(rows)):
                if digests[j] == digests[i] and rows[j]["submission"] in lli:
                    L = lli[rows[j]["submission"]]
                    break
        out.append({
            "site": site, "submission": r["submission"], "live_score": r["score"], "score_label": "OWNER-REPORT",
            "download_url": f"https://github.com/buffedlizard55-lab/{r['repo']}/raw/{r['ref']}/{r['path']}",
            "sha256": r["sha256"], "dots": int(masks[i].sum()),
            "lli_loo_estimate": L.get("loo"), "lli_fit": L.get("fit"), "estimate_label": "PROJECTION (LLI-S3 leave-one-out; not a score)",
            "byte_or_mask_identical_aliases": aliases,
            "max_within_3px_vs_other_listed": top[0], "max_overlap_with": f"{rows[top[1]]['site']}:{rows[top[1]]['submission']}",
            "n_other_listed_over_70pct": len(dup_of), "unique_vs_all_listed": bool(top[0] <= 0.70 and not aliases),
            "duplicate_examples": dup_of[:4],
        })
    out.sort(key=lambda x: -x["live_score"])
    doc = {"schema_version": 1, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "rule": "unique iff no byte/mask-identical alias and <=70% of its dots within 3 px of every other restored live-scored GEMSDOE submission (space-filling rasters with >=70% footprint coverage excluded from the max; they overlap every map)",
           "n_listed_rasters_compared": len(rows), "rows": out}
    (ROOT / "evidence" / "nine_site_table_h47.json").write_text(json.dumps(doc, indent=1) + "\n")
    for o in out:
        print(f"{o['site']} {o['live_score']:.4f} uniq={o['unique_vs_all_listed']} max={o['max_within_3px_vs_other_listed']:.3f} "
              f"vs {o['max_overlap_with'][:60]} aliases={len(o['byte_or_mask_identical_aliases'])} loo={o['lli_loo_estimate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
