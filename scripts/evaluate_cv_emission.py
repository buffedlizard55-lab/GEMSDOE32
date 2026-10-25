#!/usr/bin/env python3
import sys, json, time
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import binary_dilation

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
import os
os.environ["GEMS_DATA_DIR"]="/tmp/gems_data"
os.environ["GEMS_WORK_DIR"]="/tmp/gems_work"
from gems32.holdout import load_holdout_context, evaluate_candidate_holdout, read_binary
from gems32.paths import data_dir, work_dir

def poisson_sorted(field, foot, exclusion, min_dist_px, budget, candidate_pool_quantile=0.2):
    """Sorted Poisson disk: candidates = top quantile of field inside foot & not excluded, sorted descending."""
    # candidate pool: top 20% of field to limit compute
    valid = foot & ~exclusion
    vals = field[valid]
    if vals.size==0:
        return np.zeros(foot.shape, bool)
    # threshold for pool
    thresh=np.quantile(vals, 1.0-candidate_pool_quantile) if candidate_pool_quantile<1.0 else -np.inf
    cand_mask = valid & (field >= thresh)
    yy,xx=np.nonzero(cand_mask)
    scores=field[yy,xx]
    order=np.argsort(scores)[::-1]  # descending
    yy=yy[order]; xx=xx[order]
    # grid for fast neighbor check
    H,W=foot.shape
    cell=max(1.0,float(min_dist_px))
    grid={}
    out=np.zeros(foot.shape,bool)
    r2=min_dist_px*min_dist_px
    kept=0
    for y,x in zip(yy,xx):
        if kept>=budget:
            break
        cy,cx=int(y//cell), int(x//cell)
        ok=True
        for gy in range(cy-2,cy+3):
            for gx in range(cx-2,cx+3):
                for (ky,kx) in grid.get((gy,gx),()):
                    dy,dx=y-ky, x-kx
                    if dy*dy+dx*dx < r2:
                        ok=False; break
                if not ok: break
            if not ok: break
        if ok:
            out[y,x]=True
            grid.setdefault((cy,cx),[]).append((int(y),int(x)))
            kept+=1
    return out

def main():
    ddir=data_dir()
    wdir=work_dir()
    foot=np.load(wdir/"bands"/"_footprint.npy")
    labels=np.load(wdir/"bands"/"_labels.npy")
    ctx=load_holdout_context(ddir)
    cv_field=np.load("/tmp/gems_work/cv_field.npy")
    full_field=np.load("/tmp/gems_work/full_field.npy")
    # Load incumbent D2.8 mask for overlap checks
    d28=read_binary(Path("docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"))
    for name,field in [("CV-field",cv_field),("Full-field",full_field)]:
        print(f"\n=== {name} ===")
        for budget in [37654,44090,46090,88000]:
            for min_dist in [2.4,2.35,2.0]:
                for flank in [0,2]:  # 0=no buffer, 2=200m buffer
                    exclusion=labels.copy()
                    if flank==2:
                        exclusion=binary_dilation(labels, iterations=2)
                    mask=poisson_sorted(field, foot, exclusion, min_dist, budget, candidate_pool_quantile=0.25)
                    # also need to ensure mask has exactly budget? It may be less if pool insufficient
                    # If less, relax pool quantile
                    if mask.sum()<budget*0.9:
                        mask=poisson_sorted(field, foot, exclusion, min_dist, budget, candidate_pool_quantile=0.5)
                    n=int(mask.sum())
                    on_cat=int((mask & labels).sum())
                    # overlap within 3px of D28
                    overlap=(mask & binary_dilation(d28,iterations=3)).sum()/max(1,n) if n else 0
                    ev=evaluate_candidate_holdout(mask, ctx, f"{name}-b{budget}-d{min_dist}-flank{flank}")
                    print(f" {name} b{budget} d{min_dist} flank{flank}: n={n} oncat={on_cat} overlap={overlap:.3f} cat_hidden {ev['catalogue_hidden_mean']:.5f} drift {ev['drift_corrected_holdout_mean']:.5f} sgmc {ev['sgmc_prevalence_calibrated_dti']:.5f}")
                    # Also test raw top-k without Poisson (just top pixels)
    # Also test raw top-k for comparison
    for name,field in [("CV-field",cv_field)]:
        print(f"\n=== {name} raw top-k (no Poisson) ===")
        for budget in [44090]:
            flat=np.where(foot,field,-np.inf).ravel()
            idx=np.argpartition(flat,-budget)[-budget:]
            mask=np.zeros(flat.size,bool); mask[idx]=True; mask=mask.reshape(foot.shape)
            # mask catalogue
            mask=mask & ~labels
            # need to adjust to budget after masking? Keep as is
            n=int(mask.sum())
            ev=evaluate_candidate_holdout(mask, ctx, f"{name}-rawtopk")
            print(f" raw top-k {budget}: n={n} cat_hidden {ev['catalogue_hidden_mean']:.5f} drift {ev['drift_corrected_holdout_mean']:.5f}")

if __name__=="__main__": main()
