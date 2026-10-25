#!/usr/bin/env python3
"""Arena41 Pass-2 audit: (1) recompute G4 with the covering-set defect corrected,
(2) repair the champion .zip (measured empty 216 B self-entry) without touching tif bytes,
(3) relabel run-card score evidence classes. Verdict logic unchanged: G2/G3 already fail,
so the amended G4 cannot change the verdict (no goalpost benefit).
Outputs evidence/arena41_pass2_audit.json.
"""
from __future__ import annotations
import hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import distance_transform_edt
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gems32.paths import data_dir
DATA=data_dir(); DL=ROOT/"docs/downloads"
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def rm(p):
    with rasterio.open(p) as s: a=s.read(1)
    return np.isfinite(a)&(a>0)
def main():
    b=json.loads((ROOT/"evidence/arena41_build.json").read_text())
    final=DL/b["file"]; mask=rm(final)
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    mask&=foot; rows=[]; seen=set()
    for p in sorted(DL.glob("*.tif"))+sorted((DATA/"scored").glob("*.tif")):
        h=sha(p)
        if h in seen or p.name==final.name: continue
        seen.add(h); m=rm(p)&foot
        d1=distance_transform_edt(~m); f_in=float((d1[mask]<=3).mean())
        d2=distance_transform_edt(~mask); f_out=float((d2[m]<=3).mean()) if m.any() else 0.0
        rows.append({"file":p.name,"dots":int(m.sum()),"frac_final_within3":f_in,"frac_other_within3":f_out,
                     "sym_overlap_min":min(f_in,f_out),"covering_set_gt100k_dots":bool(m.sum()>100000)})
    sparse=[r for r in rows if r["dots"]<=2*37654]
    amended_g4=bool(all(r["frac_final_within3"]<=0.70 for r in sparse) and all(r["sym_overlap_min"]<=0.70 for r in rows))
    # champion zip repair
    cz=DL/"gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.zip"; ct=DL/"gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    before={"bytes":cz.stat().st_size,"sha256":sha(cz),"entries":zipfile.ZipFile(cz).namelist()}
    with zipfile.ZipFile(cz,"w",zipfile.ZIP_DEFLATED) as z: z.write(ct,arcname=ct.name)
    after={"bytes":cz.stat().st_size,"sha256":sha(cz),"entries":zipfile.ZipFile(cz).namelist(),
           "entry_uncompressed_bytes":zipfile.ZipFile(cz).getinfo(ct.name).file_size,"champion_tif_sha256_unchanged":sha(ct)}
    audit={"G4_literal_preregistered":b["gates"]["G4_uniqueness"],
      "G4_defect":"One-directional within-3px fraction is vacuously failed by dense covering rasters in the registry (lattice-s5 206,895 dots: 98.7% of ANY footprint dot set lies within 3px; phi vs final = 0.00012). It measures the other raster's coverage, not duplication.",
      "G4_amended_rule":"spearman<0.90 (build) AND frac_final_within3<=0.70 vs every registry raster with <=2x final dots AND symmetric min(within3 both directions)<=0.70 vs all",
      "G4_amended_pass":amended_g4,
      "max_frac_final_within3_sparse":max((r["frac_final_within3"] for r in sparse),default=None),
      "worst_sparse":max(sparse,key=lambda r:r["frac_final_within3"]) if sparse else None,
      "vs_champion":[r for r in rows if "e5eb6e7e-zeros" in r["file"]],
      "champion_zip_repair":{"before":before,"after":after},
      "verdict_unchanged":b["verdict"],"reason":"G2 and G3 fail independently of G4"}
    (ROOT/"evidence/arena41_pass2_audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    # relabel run-card score classes (no numbers changed)
    rc=json.loads((ROOT/"evidence/arena41_run_card.json").read_text())
    if "organizer_confirmed_scores_cited" in rc:
        rc["scores_cited_by_evidence_class"]={"ORGANIZER-CONFIRMED (leaderboard page read 2026-10-25)":{"rank1_xiaofanhu":0.4413},
          "OWNER-REPORTED (standing brief 2026-10-25; no receipt in checkout)":{"H33-2-B2_champion":0.2778,"H27-4-R1-SOLO":0.2708,"D2.8":0.2600}}
        del rc["organizer_confirmed_scores_cited"]
        rc["pass2_G4_amended_pass"]=amended_g4; rc["pass2_G4_literal"]=False
        (ROOT/"evidence/arena41_run_card.json").write_text(json.dumps(rc,indent=2)+"\n")
    print(json.dumps(audit,indent=2))
if __name__=="__main__": main()
