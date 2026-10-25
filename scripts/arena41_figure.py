#!/usr/bin/env python3
"""Arena41 summary figure -> docs/assets/fig_arena41_pfonly.png (from cached fields + shipped TIF)."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, rasterio
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gems32.paths import data_dir, work_dir
DATA=data_dir(); WORK=work_dir(); DL=ROOT/"docs/downloads"
def rm(p):
    with rasterio.open(p) as s: a=s.read(1)
    return np.isfinite(a)&(a>0)
def down(a,f=6):
    h,w=a.shape; return a[:h//f*f,:w//f*f].reshape(h//f,f,w//f,f).mean(axis=(1,3))
def main():
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    champ=rm(DL/"gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif")
    b=json.loads((ROOT/"evidence/arena41_build.json").read_text()); final=rm(DL/b["file"])
    field=np.load(WORK/"arena41_full_PF_ONLY.npy")
    e2=json.loads((ROOT/"evidence/arena41_exp2_oof.json").read_text())
    fig,ax=plt.subplots(1,3,figsize=(15,5))
    ax[0].imshow(np.where(down(foot.astype(np.float32))>0,down(field),np.nan),cmap="viridis"); ax[0].set_title("PF-ONLY field (no DEM/LiDAR)"); ax[0].axis("off")
    ov=np.zeros((*down(foot.astype(np.float32)).shape,3),dtype=np.float32)
    c=down(champ.astype(np.float32)); n=down(final.astype(np.float32))
    ov[...,0]=(c>0)*0.9; ov[...,2]=(n>0)*0.9; ov[...,1]=((c>0)&(n>0))*0.9
    ov[down(foot.astype(np.float32))==0]=1.0
    ax[1].imshow(ov); ax[1].set_title("Dots: champion=red, Arena41=blue\n(only 25.8% of Arena41 within 300m of champion)"); ax[1].axis("off")
    names=["random","PF-ONLY","CTRL-SURF"]; vals=[e2["random_37654"]["pooled"]["pooled_dti"],e2["arms"]["PF_ONLY"]["budgets"]["37654"]["pooled"]["pooled_dti"],e2["arms"]["CTRL_SURF"]["budgets"]["37654"]["pooled"]["pooled_dti"]]
    cis=[e2["random_37654"]["pooled"]["ci95_cluster_bootstrap"],e2["arms"]["PF_ONLY"]["budgets"]["37654"]["pooled"]["ci95_cluster_bootstrap"],e2["arms"]["CTRL_SURF"]["budgets"]["37654"]["pooled"]["ci95_cluster_bootstrap"]]
    err=[[v-c[0] for v,c in zip(vals,cis)],[c[1]-v for v,c in zip(vals,cis)]]
    ax[2].bar(names,vals,yerr=err,capsize=4,color=["grey","tab:blue","tab:red"]); ax[2].set_ylabel("pooled HOLDOUT-DTI (not a live score)"); ax[2].set_title("EXP2 quadrant-OOF, 37,654 dots")
    fig.tight_layout(); fig.savefig(ROOT/"docs/assets/fig_arena41_pfonly.png",dpi=130); print("ok")
if __name__=="__main__": main()
