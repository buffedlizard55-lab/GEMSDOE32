#!/usr/bin/env python3
"""Arena41 forensic autopsy: why did H33-2-B2 (owner-reported 0.2778) beat its parent?

Re-reads hash-pinned bytes only. Every live number is OWNER-REPORTED (standing brief,
2026-10-25); no organizer receipt is in this checkout. Outputs evidence/arena41_forensic.json
and prints a human table. Memory-lean: one EDT at a time.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32.paths import data_dir  # noqa
from gems32 import metric as M  # noqa

DATA = data_dir()
DL = ROOT / "docs" / "downloads"

def sha(p): 
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def read_mask(p):
    with rasterio.open(p) as s: a=s.read(1)
    return np.isfinite(a) & (a>0)
def phi_corr(a,b,foot):
    # Pearson (=phi = Spearman on binary with ties handled by rank equivalence up to tie correction;
    # report phi and label it phi, not Spearman)
    A=a&foot; B=b&foot
    n=int(foot.sum()); na=int(A.sum()); nb=int(B.sum()); nab=int((A&B).sum())
    num = nab*n - na*nb
    den = float(np.sqrt(float(na)*float(n-na)*float(nb)*float(n-nb))) if na and nb and na<n and nb<n else 0.0
    return float(num/den) if den else 0.0, nab
def frac_within3(src, other):
    if not src.any() or not other.any(): return 0.0
    d = distance_transform_edt(~other)
    return float((d[src]<=3.0).mean())

def main():
    champ_p = DL/"gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    d28_p = DATA/"scored/gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    with rasterio.open(DATA/"labels.tif") as s: labels=(s.read(1)>0)&foot
    champ = read_mask(champ_p)&foot
    d28 = read_mask(d28_p)&foot
    dcat = distance_transform_edt(~labels)
    b1 = d28 & (dcat>1.0)
    b2synth = d28 & (dcat>2.0)
    shells={}
    for nm,(lo,hi) in {"d_eq_0_oncat":(-0.1,0.0),"0<d<=1":(0.0,1.0),"1<d<=2":(1.0,2.0),"2<d<=3":(2.0,3.0),"3<d<=5":(3.0,5.0),">5":(5.0,1e9)}.items():
        shells[nm]=int((d28 & (dcat>lo)&(dcat<=hi)).sum())
    out={
      "evidence_class":"MEASURED bytes + OWNER-REPORTED live scores (no organizer receipt in checkout)",
      "champion":{"file":champ_p.name,"sha256":sha(champ_p),"dots":int(champ.sum()),
                  "audit_sha_matches": sha(champ_p)=="c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"},
      "d28":{"file":d28_p.name,"sha256":sha(d28_p),"dots":int(d28.sum())},
      "labels_px":int(labels.sum()),"footprint_px":int(foot.sum()),
      "shell_counts_in_d28":shells,
      "champ_subset_of_d28": bool((champ & ~d28).sum()==0),
      "champ_equals_d28_minus_dle2_pixel_exact": bool(np.array_equal(champ,b2synth)),
      "b1_synth_dots":int(b1.sum()),"b2_synth_dots":int(b2synth.sum()),
      "champ_minus_b2synth":int((champ&~b2synth).sum()),"b2synth_minus_champ":int((b2synth&~champ).sum()),
      "champ_dcat_min":float(dcat[champ].min()),"champ_shell_2_3":int((champ&(dcat>2)&(dcat<=3)).sum()),
      "champ_shell_gt3":int((champ&(dcat>3)).sum()),
    }
    # live-pair inversion, assumption c==m (dot-side credit == truth-side unique coverage lost),
    # one-parameter family in c1 (credit earned by shell 0<d<=1). Scores OWNER-REPORTED.
    s0,s1,s2=0.2600,0.2708,0.2778
    dn1=int(d28.sum()-b1.sum()); dn2=int(b1.sum()-champ.sum())
    fam=[]
    for c1 in [0,7.8,25,50,100]:
        # T0=s0*D0 ; T0-c1=s1*(D0-0.2dn1)  => D0=(c1-0.2*dn1*s1)/(s0-s1)
        D0=(c1-0.2*dn1*s1)/(s0-s1); T0=s0*D0
        D2=D0-0.2*(dn1+dn2); T2=s2*D2; c2=(T0-c1)-T2
        fam.append({"c1_assumed":c1,"D_d28":float(D0),"T_d28":float(T0),"c2_implied":float(c2),
                    "c2_per_dot":float(c2/dn2),"c1_per_dot":float(c1/dn1),
                    "pred_s2_if_c2_eq_0":float((T0-c1)/D2)})
    out["live_inversion"]={"scores_owner_reported":{"D2.8":s0,"B1_solo":s1,"B2_champion":s2},
        "dn_shell_le1":dn1,"dn_shell_1_2":dn2,"assumption":"c==m for removed shells (denominator falls exactly 0.2*dn); family indexed by c1",
        "family":fam,
        "breakeven_credit_per_removed_dot_at_s2":0.2*s2,
        "note":"c2_per_dot << breakeven 0.0556 across the admissible c1 sensitivity family shown (c1=7.8 is the SGMC-proxy anchor): shell 1<d<=2 earned near-zero live credit. c1>=~150 is inadmissible under c==m (implies D_d28<6000, T<1500, inconsistent with a 44k-dot emission at these scores)."}
    # proxy credits of each shell against SGMC off-catalogue and against full catalogue
    with rasterio.open(DATA/"external/derived_sgmc_faults_100m_u8.tif") as s: sgmc=(s.read(1)>0)&foot
    sg_off = sgmc & (dcat>3.0)
    out["sgmc_offcat_px_dgt3"]=int(sg_off.sum())
    def tp_of(mask, truth):
        if not mask.any() or not truth.any(): return 0.0
        d=distance_transform_edt(~mask); return float(M.kernel(d[truth]).sum())
    shell_masks={"shell_le1":d28&(dcat<=1),"shell_1_2":d28&(dcat>1)&(dcat<=2),"shell_2_3":champ&(dcat>2)&(dcat<=3)}
    proxy={}
    base_sg=tp_of(d28,sg_off); base_cat=tp_of(d28,labels)
    for nm,sm in shell_masks.items():
        rest=d28&~sm if nm!="shell_2_3" else champ&~sm
        b_sg = base_sg if nm!="shell_2_3" else tp_of(champ,sg_off)
        b_cat = base_cat if nm!="shell_2_3" else tp_of(champ,labels)
        proxy[nm]={"dots":int(sm.sum()),
                   "unique_credit_sgmc_offcat":float(b_sg-tp_of(rest,sg_off)),
                   "unique_credit_catalogue":float(b_cat-tp_of(rest,labels))}
        proxy[nm]["per_dot_sgmc"]=proxy[nm]["unique_credit_sgmc_offcat"]/max(1,int(sm.sum()))
        proxy[nm]["per_dot_catalogue"]=proxy[nm]["unique_credit_catalogue"]/max(1,int(sm.sum()))
    out["shell_unique_credit_proxies"]=proxy
    # registry overlap of champion vs every distinct shipped/scored raster (phi + within-3px)
    regs=[]
    seen={}
    for p in sorted(DL.glob("*.tif"))+sorted((DATA/"scored").glob("*.tif")):
        h=sha(p)
        if h in seen: continue
        seen[h]=p.name
        m=read_mask(p)&foot
        phi,nab=phi_corr(champ,m,foot)
        regs.append({"file":p.name,"sha256":h,"dots":int(m.sum()),"phi_binary_vs_champion":phi,
                     "exact_overlap_dots":nab,"frac_champ_within3px":frac_within3(champ,m),
                     "frac_other_within3px_of_champ":frac_within3(m,champ)})
    out["registry_vs_champion"]=sorted(regs,key=lambda r:-r["phi_binary_vs_champion"])
    (ROOT/"evidence/arena41_forensic.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({k:v for k,v in out.items() if k!="registry_vs_champion"},indent=2))
    print("\nTop registry phi vs champion:")
    for r in out["registry_vs_champion"][:10]:
        print(f"  {r['phi_binary_vs_champion']:.3f} within3={r['frac_champ_within3px']:.3f} dots={r['dots']:6d} {r['file'][:80]}")

if __name__=="__main__": main()
