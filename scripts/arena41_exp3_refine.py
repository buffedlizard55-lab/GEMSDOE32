#!/usr/bin/env python3
"""Arena41 EXP3 (final experiment): worm-ridge support-confinement refinement on OOF fields.

Fault = a *line* along a potential-field edge; EXP2 dotted smooth probability blobs.
Refinement: eligible dots must sit on a local maximum (3x3) of the worm_persist channel.
Both arms get the same support fix (fair), same OOF fields, same shared evaluators:
gems32.holdout (mandated) + gems32.live_mirror (off-catalogue, prevalence-calibrated).
Also evaluates CHAMPION and RANDOM under LM for anchoring. No retraining.
Outputs evidence/arena41_exp3_refine.json.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np, rasterio
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gems32.paths import data_dir, work_dir
from gems32.pfonly import dot_thin, pooled_dti_from_folds
from gems32.holdout import load_holdout_context, evaluate_candidate_holdout
from gems32.live_mirror import load_live_mirror_context, evaluate_live_mirror
DATA=data_dir(); WORK=work_dir(); B=37654
def ev_all(mask,ctx,lm,name):
    e=evaluate_candidate_holdout(mask,ctx,name=name)
    l=evaluate_live_mirror(mask,lm,name=name,calibrate_prevalence=True)
    return {"emitted":int(mask.sum()),"pooled":pooled_dti_from_folds(e["catalogue_hidden_folds"]),
      "sgmc_prevalence_calibrated_dti":e["sgmc_prevalence_calibrated_dti"],
      "catalogue_hidden_mean":e["catalogue_hidden_mean"],
      "lm_mean":l.get("lm_mean"),"lm_calibrated_mean":l.get("lm_calibrated_mean"),
      "lm_keys":sorted(l.keys())}
def main():
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    with rasterio.open(DATA/"labels.tif") as s: labels=(s.read(1)>0)&foot
    stack=np.lib.format.open_memmap(WORK/"arena41_stack.npy",mode="r")
    worm=np.asarray(stack[:,:,15],dtype=np.float32)  # worm_persist per channels list
    support=(worm>=ndimage.maximum_filter(worm,size=3,mode="nearest"))&(worm>0)&foot
    print("support px",int(support.sum()),flush=True)
    ctx=load_holdout_context(DATA); lm=load_live_mirror_context(DATA,foot,labels)
    out={"experiment":"EXP3_refine_support","support_px":int(support.sum()),"arms":{}}
    for arm in ["PF_ONLY","CTRL_SURF"]:
        field=np.load(WORK/f"arena41_oof_{arm}.npy")
        for tag,elig in [("plain",foot),("wormsupport",support)]:
            mask=dot_thin(field,elig,B,min_dist=2.8)
            out["arms"][f"{arm}_{tag}"]=ev_all(mask,ctx,lm,f"{arm}_{tag}")
            print(arm,tag,out["arms"][f"{arm}_{tag}"]["pooled"]["pooled_dti"],out["arms"][f"{arm}_{tag}"]["sgmc_prevalence_calibrated_dti"],out["arms"][f"{arm}_{tag}"]["lm_calibrated_mean"],flush=True)
            del mask
        del field
    with rasterio.open(ROOT/"docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif") as s: champ=(s.read(1)>0)&foot
    out["arms"]["CHAMPION_prebuilt"]=ev_all(champ,ctx,lm,"CHAMPION")
    print("CHAMPION",out["arms"]["CHAMPION_prebuilt"],flush=True)
    (ROOT/"evidence/arena41_exp3_refine.json").write_text(json.dumps(out,indent=2)+"\n"); print("DONE")
if __name__=="__main__": main()
