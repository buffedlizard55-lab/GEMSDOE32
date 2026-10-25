#!/usr/bin/env python3
"""Arena41 EXP1 (leakage canary + solo-surface screen). 1 of max 3 experiments.

Each candidate surface is LABEL-FREE. For each: (a) quadrant holdout AUC alone
(leakage canary: AUC>0.90 => leakage until proven otherwise), (b) dotted emission at
37,654 dots (global catalogue + B2 masked; pessimistic screen, identical for all incl.
champion comparator), scored with the shared gems32.holdout evaluator (no fork).
Outputs evidence/arena41_exp1_screen.json.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT/"src"))
from gems32.paths import data_dir, work_dir
from gems32.pfonly import robust_unit, fill_median, grad_mag, dot_thin, pooled_dti_from_folds
from gems32.holdout import load_holdout_context, evaluate_candidate_holdout, quadrant_ids

DATA=data_dir(); BANDS=work_dir()/"bands"; BUDGET=37654
def band(i,name): return np.load(BANDS/f"{i:02d}_{name}.npy")
def main():
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    with rasterio.open(DATA/"labels.tif") as s: labels=(s.read(1)>0)&foot
    dcat=distance_transform_edt(~labels); quad=quadrant_ids(foot)
    import os
    ELIG=os.environ.get("ARENA41_ELIG","foot")
    eligible = foot & (dcat>2.0) if ELIG=="b2" else foot.copy()
    ctx = load_holdout_context(DATA)
    print("ctx loaded", flush=True)
    surfaces={}
    rtp=fill_median(band(2,"rtp"),foot); grav=fill_median(band(13,"iso_grav_anom"),foot)
    depth=fill_median(band(15,"depth_to_base_surf"),foot); cond=fill_median(band(17,"cond_surf"),foot)
    dem=fill_median(band(12,"det_elev"),foot)
    hgm_rtp1=grad_mag(rtp,1.0); hgm_rtp4=grad_mag(rtp,4.0)
    surfaces["C2_worm_scale_persist_proxy"]=np.minimum(robust_unit(hgm_rtp1,foot),robust_unit(hgm_rtp4,foot))
    surfaces["C3_curv_abs_s2p5"]=robust_unit(np.abs(ndimage.gaussian_laplace(dem,2.5,mode="nearest")),foot)
    surfaces["C_basement_step"]=robust_unit(grad_mag(depth,1.5),foot)
    surfaces["C1_pf_edge_mean"]=((robust_unit(hgm_rtp1,foot)+robust_unit(grad_mag(grav,1.5),foot)
                                  +robust_unit(grad_mag(depth,1.5),foot)+robust_unit(grad_mag(cond,1.5),foot))/4.0).astype(np.float32)
    # C4 radiometric alteration x demagnetisation (external u8: extensions band1 Th/K; low Th/K => K-rich)
    with rasterio.open(DATA/"external/geodawn_extensions_u8.tif") as s: thk=s.read(1).astype(np.float32)
    k_rich=robust_unit(255.0-thk,foot); rtp_lo=robust_unit(-ndimage.gaussian_filter(rtp,3.0,mode="nearest"),foot)
    surfaces["C4_radalt_x_demag"]=(k_rich*rtp_lo).astype(np.float32)
    del rtp,grav,depth,cond,dem,hgm_rtp1,hgm_rtp4,thk,k_rich,rtp_lo

    rng=np.random.default_rng(41); results={}
    # champion comparator (prebuilt; leak-contaminated on this instrument in champion's favour/penalty noted in report)
    with rasterio.open(ROOT/"docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif") as s:
        champ=(s.read(1)>0)&foot
    for name,mask in [("CHAMPION_B2_prebuilt",champ)]:
        ev=evaluate_candidate_holdout(mask,ctx,name=name)
        results[name]={"emitted":int(mask.sum()),"pooled":pooled_dti_from_folds(ev["catalogue_hidden_folds"]),
            "catalogue_hidden_mean":ev["catalogue_hidden_mean"],"sgmc_prevalence_calibrated_dti":ev["sgmc_prevalence_calibrated_dti"],
            "drift_corrected_holdout_mean":ev["drift_corrected_holdout_mean"]}
        print(name,results[name]["pooled"],flush=True)
    for name,surf in surfaces.items():
        aucs=[]
        for q in range(4):
            pos=np.flatnonzero((labels&(quad==q)).ravel())
            neg_pool=np.flatnonzero((foot&~labels&(quad==q)).ravel())
            neg=rng.choice(neg_pool,size=min(120000,neg_pool.size),replace=False)
            idx=np.concatenate([pos,neg]); y=np.concatenate([np.ones(pos.size),np.zeros(neg.size)])
            v=surf.ravel()[idx].astype(np.float64); ok=np.isfinite(v)
            aucs.append(float(roc_auc_score(y[ok],v[ok])))
        mask=dot_thin(surf,eligible,BUDGET,min_dist=2.8)
        ev=evaluate_candidate_holdout(mask,ctx,name=name)
        results[name]={"emitted":int(mask.sum()),"auc_by_quadrant":aucs,"auc_mean":float(np.mean(aucs)),
            "pooled":pooled_dti_from_folds(ev["catalogue_hidden_folds"]),
            "catalogue_hidden_mean":ev["catalogue_hidden_mean"],"sgmc_prevalence_calibrated_dti":ev["sgmc_prevalence_calibrated_dti"],
            "drift_corrected_holdout_mean":ev["drift_corrected_holdout_mean"]}
        print(name,"AUC",np.round(aucs,4),"pooled",results[name]["pooled"]["pooled_dti"],flush=True)
        del surf,mask
    out={"experiment":"EXP1_screen","evaluator":"gems32.holdout.evaluate_candidate_holdout v(repo HEAD 012e17b): hide 20% whole catalogue components per quadrant, draws 20/21, 15px collar, visible masked in scoring domain; pooled DTI alpha0.2 beta0.8 R=3px computed from per-cell TP/FP/FN",
         "budget":BUDGET,"screen_mask":ELIG,
         "leakage_canary":"AUC>0.90 => leakage until proven otherwise","results":results}
    (ROOT/f"evidence/arena41_exp1_screen_{ELIG}.json").write_text(json.dumps(out,indent=2)+"\n")
    print("DONE")
if __name__=="__main__": main()
