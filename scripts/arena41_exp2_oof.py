#!/usr/bin/env python3
"""Arena41 EXP2: PF-ONLY lane vs CTRL-SURF ablation control, quadrant-OOF, shared evaluator.

Builds a 34-channel memmap stack (24 PF + 10 surface-expression), trains quadrant-OOF HGB
detectors for both arms (catalogue info = other 3 quadrants only, 15px collar), emits dotted
masks at matched budgets from the OOF fields (eligible=footprint; the shared evaluator masks
visible faults per cell), and pre-registered final fields saved for EXP3 (full-train PF field).
Outputs evidence/arena41_exp2_oof.json + .cache fields (not committed).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gems32.paths import data_dir, work_dir
from gems32.pfonly import robust_unit, fill_median, grad_mag, upward_continue, hessian_ridge, dot_thin, pooled_dti_from_folds
from gems32.holdout import load_holdout_context, evaluate_candidate_holdout, quadrant_ids
from gems32.detector import Detector, DetectorSpec

DATA=data_dir(); BANDS=work_dir()/"bands"; WORK=work_dir()
PF_RAW=[(1,"mag_anom"),(2,"rtp"),(3,"tmi_hg"),(5,"iso_grav_anom_slope"),(6,"tc"),(9,"tmi_vg"),
        (11,"iso_grav_anom_vg"),(13,"iso_grav_anom"),(14,"tmi"),(15,"depth_to_base_surf"),(17,"cond_surf"),(18,"iso_grav_anom_hg")]
def band(i,n): return np.load(BANDS/f"{i:02d}_{n}.npy")

def build_stack(foot):
    sp=WORK/"arena41_stack.npy"; meta=WORK/"arena41_stack_channels.json"
    chans=[f"raw{i:02d}_{n}" for i,n in PF_RAW]+["rtp_hgm_s1","rtp_hgm_up300","rtp_hgm_up600","worm_persist","grav_hgm_s15","grav_hgm_up300","depth_grad","cond_grad","rtp_ridge_s12","rtp_ridge_s25","grav_ridge_s25","rtp_shallow_resid"]+["dem_raw","dem_slope_raw","dem_curv_s1","dem_curv_s25","dem_ridge_s1","dem_ridge_s2","dem_ridge_s35","dem_relief5","dem_tophat","dem_coherence"]
    if sp.exists() and meta.exists() and json.loads(meta.read_text())==chans:
        return np.lib.format.open_memmap(sp,mode="r"), chans
    H,W=foot.shape; F=len(chans)
    st=np.lib.format.open_memmap(sp,mode="w+",dtype=np.float32,shape=(H,W,F))
    keep={}
    for c,(i,n) in enumerate(PF_RAW):
        a=fill_median(band(i,n),foot); st[:,:,c]=a
        if i in (2,13,15,17): keep[i]=a
        print("raw",i,n,flush=True)
    rtp,grav,depth,cond=keep[2],keep[13],keep[15],keep[17]; c=len(PF_RAW)
    h0=grad_mag(rtp,1.0); st[:,:,c]=h0; c+=1
    up3=upward_continue(rtp,3.0); h3=grad_mag(up3,0.0); st[:,:,c]=h3; c+=1
    up6=upward_continue(rtp,6.0); h6=grad_mag(up6,0.0); st[:,:,c]=h6; c+=1
    st[:,:,c]=np.minimum(np.minimum(robust_unit(h0,foot),robust_unit(h3,foot)),robust_unit(h6,foot)); c+=1
    st[:,:,c]=grad_mag(grav,1.5); c+=1
    st[:,:,c]=grad_mag(upward_continue(grav,3.0),0.0); c+=1
    st[:,:,c]=grad_mag(depth,1.5); c+=1
    st[:,:,c]=grad_mag(cond,1.5); c+=1
    st[:,:,c]=hessian_ridge(rtp,1.2); c+=1
    st[:,:,c]=hessian_ridge(rtp,2.5); c+=1
    st[:,:,c]=hessian_ridge(grav,2.5); c+=1
    st[:,:,c]=np.abs(rtp-up6); c+=1
    del keep,h0,h3,h6,up3,up6,rtp,grav,depth,cond
    dem=fill_median(band(12,"det_elev"),foot)
    st[:,:,c]=dem; c+=1; st[:,:,c]=fill_median(band(19,"det_elev_slope"),foot); c+=1
    st[:,:,c]=ndimage.gaussian_laplace(dem,1.0,mode="nearest"); c+=1
    st[:,:,c]=ndimage.gaussian_laplace(dem,2.5,mode="nearest"); c+=1
    st[:,:,c]=hessian_ridge(dem,1.0); c+=1; st[:,:,c]=hessian_ridge(dem,2.0); c+=1; st[:,:,c]=hessian_ridge(dem,3.5); c+=1
    st[:,:,c]=ndimage.maximum_filter(dem,size=5)-ndimage.minimum_filter(dem,size=5); c+=1
    st[:,:,c]=dem-ndimage.grey_opening(dem,size=(5,5)); c+=1
    gx=ndimage.gaussian_filter(dem,2.0,order=(0,1),mode="nearest"); gy=ndimage.gaussian_filter(dem,2.0,order=(1,0),mode="nearest")
    jxx=ndimage.gaussian_filter(gx*gx,2.0,mode="nearest"); jyy=ndimage.gaussian_filter(gy*gy,2.0,mode="nearest"); jxy=ndimage.gaussian_filter(gx*gy,2.0,mode="nearest")
    st[:,:,c]=(np.sqrt(np.maximum(((jxx-jyy)*0.5)**2+jxy**2,0.0))/(jxx+jyy+1e-12)).astype(np.float32); c+=1
    assert c==F, (c,F); st.flush(); meta.write_text(json.dumps(chans))
    return np.lib.format.open_memmap(sp,mode="r"), chans

def sample(stack, cols, labels, train_mask, spec, rng):
    H,W,F=stack.shape; flat=np.asarray(stack).reshape(-1,F) if False else None
    # memmap-friendly row gather without materialising the stack
    flat_view = stack.reshape(-1,F)
    pos=np.flatnonzero((labels&train_mask).ravel())
    if pos.size>spec.sample_pos: pos=rng.choice(pos,spec.sample_pos,replace=False)
    tr=train_mask.ravel(); lab=labels.ravel(); parts=[]; got=0
    while got<spec.sample_neg:
        need=int((spec.sample_neg-got)*1.35)+4096
        idx=rng.integers(0,H*W,size=need,dtype=np.int64); idx=idx[tr[idx]&~lab[idx]]
        if idx.size: parts.append(idx); got+=idx.size
    neg=np.concatenate(parts)[:spec.sample_neg]
    idx=np.sort(np.concatenate([pos,neg])); y=lab[idx].astype(np.int8)
    X=np.asarray(flat_view[idx][:,cols],dtype=np.float32)
    return X,y

def predict_rows(det, stack, cols, y0,y1):
    blk=np.asarray(stack[y0:y1][:,:,cols],dtype=np.float32); h,w,f=blk.shape
    Xs=(blk.reshape(-1,f)-det.mu)/det.sd
    return det.model.predict_proba(Xs)[:,1].astype(np.float32).reshape(h,w)

def oof_field(stack, cols, labels, foot, quad, seed):
    H,W,_=stack.shape; field=np.zeros((H,W),np.float32); aucs={}
    spec=DetectorSpec(seed=seed)
    for q in range(4):
        t0=time.time(); fold=(quad==q)
        d_to_fold=distance_transform_edt(~fold)
        train=foot&~fold&(d_to_fold>15.0)
        rng=np.random.default_rng(1000*seed+q)
        X,y=sample(stack,cols,labels,train,spec,rng)
        det=Detector(spec).fit(X,y); del X,y
        rows=np.flatnonzero(fold.any(axis=1)); r0,r1=int(rows[0]),int(rows[-1])+1
        for yy in range(r0,r1,256):
            field[yy:min(yy+256,r1)]=predict_rows(det,stack,cols,yy,min(yy+256,r1))
        pos=np.flatnonzero((labels&fold).ravel()); negp=np.flatnonzero((foot&~labels&fold).ravel())
        neg=rng.choice(negp,size=min(120000,negp.size),replace=False)
        idx=np.concatenate([pos,neg]); yy=np.concatenate([np.ones(pos.size),np.zeros(neg.size)])
        aucs[f"Q{q}"]=float(roc_auc_score(yy,field.ravel()[idx].astype(np.float64)))
        print(f"  fold{q} AUC {aucs[f'Q{q}']:.4f} {time.time()-t0:.0f}s",flush=True)
        del det
    field=np.where(foot,field,0.0).astype(np.float32)
    return field, aucs

def main():
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    with rasterio.open(DATA/"labels.tif") as s: labels=(s.read(1)>0)&foot
    quad=quadrant_ids(foot)
    stack,chans=build_stack(foot); print("stack",stack.shape,chans,flush=True)
    pf_cols=list(range(24)); all_cols=list(range(34))
    ctx=load_holdout_context(DATA); print("ctx loaded",flush=True)
    out={"experiment":"EXP2_OOF","channels":chans,"pf_cols":[chans[i] for i in pf_cols],"arms":{}}
    for arm,cols,seed in [("PF_ONLY",pf_cols,41),("CTRL_SURF",all_cols,42)]:
        print(arm,flush=True); field,aucs=oof_field(stack,cols,labels,foot,quad,seed)
        np.save(WORK/f"arena41_oof_{arm}.npy",field)
        armres={"auc_by_quadrant":aucs,"budgets":{}}
        for B in ([25000,37654,50000] if arm=="PF_ONLY" else [37654]):
            mask=dot_thin(field,foot,B,min_dist=2.8)
            ev=evaluate_candidate_holdout(mask,ctx,name=f"{arm}_{B}")
            armres["budgets"][str(B)]={"emitted":int(mask.sum()),"pooled":pooled_dti_from_folds(ev["catalogue_hidden_folds"]),
              "catalogue_hidden_mean":ev["catalogue_hidden_mean"],"sgmc_prevalence_calibrated_dti":ev["sgmc_prevalence_calibrated_dti"],
              "drift_corrected_holdout_mean":ev["drift_corrected_holdout_mean"],"sgmc_off_catalogue_raw_dti":ev["sgmc_off_catalogue_raw_dti"]}
            print(arm,B,armres["budgets"][str(B)]["pooled"]["pooled_dti"],armres["budgets"][str(B)]["sgmc_prevalence_calibrated_dti"],flush=True)
            del mask
        out["arms"][arm]=armres; del field
    # random matched baseline
    rng=np.random.default_rng(7); rfield=rng.random(foot.shape,dtype=np.float32); rmask=dot_thin(rfield,foot,37654,min_dist=2.8)
    ev=evaluate_candidate_holdout(rmask,ctx,name="RANDOM")
    out["random_37654"]={"pooled":pooled_dti_from_folds(ev["catalogue_hidden_folds"]),"sgmc_prevalence_calibrated_dti":ev["sgmc_prevalence_calibrated_dti"]}
    # full-train PF field for EXP3 (all quadrants, no collar)
    spec=DetectorSpec(seed=43); rng=np.random.default_rng(43)
    X,y=sample(stack,pf_cols,labels,foot,spec,rng); det=Detector(spec).fit(X,y); del X,y
    full=np.zeros(foot.shape,np.float32)
    for yy in range(0,foot.shape[0],256): full[yy:yy+256]=predict_rows(det,stack,pf_cols,yy,min(yy+256,foot.shape[0]))
    full=np.where(foot,full,0.0).astype(np.float32); np.save(WORK/"arena41_full_PF_ONLY.npy",full)
    try: out["full_train_feature_importance_permutation"]="skipped (HGB has no native importances; not fabricated)"
    except Exception: pass
    out["evaluator"]="gems32.holdout.evaluate_candidate_holdout (repo HEAD 012e17b) + pooled DTI from per-cell TP/FP/FN"
    (ROOT/"evidence/arena41_exp2_oof.json").write_text(json.dumps(out,indent=2)+"\n"); print("DONE")
if __name__=="__main__": main()
