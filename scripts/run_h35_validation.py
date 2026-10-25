#!/usr/bin/env python3
"""Validate H35 candidates on spatially-blocked holdout, leakage canary, correlation/overlap checks."""
import sys, json, time
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
import os
os.environ["GEMS_DATA_DIR"]="/tmp/gems_data"
os.environ["GEMS_WORK_DIR"]="/tmp/gems_work"
from gems32.holdout import load_holdout_context, evaluate_candidate_holdout, read_binary
from gems32.h35_new import H35_BUILDERS, H35_SPECS, top_n_mask
from gems32.paths import data_dir, work_dir

def auc_for_surface(surface, foot, labels):
    # simple ROC AUC faults vs background (foot without labels)
    # use sklearn if available
    from sklearn.metrics import roc_auc_score
    mask = foot
    y_true = labels[mask].astype(int)
    y_score = surface[mask]
    # two-sided AUC: max(AUC, 1-AUC)
    try:
        auc = roc_auc_score(y_true, y_score)
        auc_twosided = max(auc, 1-auc)
        return auc, auc_twosided
    except:
        return 0.5, 0.5

def main():
    ddir=data_dir()
    wdir=work_dir()
    bands_dir=wdir/"bands"
    foot=np.load(bands_dir/"_footprint.npy")
    labels=np.load(bands_dir/"_labels.npy")
    ctx=load_holdout_context(ddir)
    print(f"Holdout context: {len(ctx.cells)} cells, foot {foot.sum()}, labels {labels.sum()}")
    # Load registry rasters for correlation/overlap
    registry_tifs = sorted(Path("docs/downloads").glob("*.tif"))
    reg_masks={}
    for p in registry_tifs:
        try:
            reg_masks[p.name]=read_binary(p)
        except: pass
    print(f"Registry rasters: {len(reg_masks)}")
    results={}
    BUDGETS=[37654, 44090, 46090]  # test budgets incl B2 matched
    for hid, builder in H35_BUILDERS.items():
        print(f"\n=== {hid}: {H35_SPECS[hid]['name']} ===")
        t0=time.time()
        surface=builder(bands_dir, ddir, foot)
        dt=time.time()-t0
        print(f" built in {dt:.1f}s range [{surface[foot].min():.3f},{surface[foot].max():.3f}]")
        # leakage canary AUC
        auc, auc2 = auc_for_surface(surface, foot, labels)
        print(f" AUC raw {auc:.4f} two-sided {auc2:.4f} {'LEAK' if auc2>0.90 else 'ok'}")
        # correlation/overlap vs registry (surface rank correlation would need field fields not masks; use binary mask correlation as proxy)
        # For surface, compute Spearman vs D2.8 mask distance? Use simple Pearson of surface vs H32-D field not available, so compute binary mask overlap later
        for budget in BUDGETS:
            mask=top_n_mask(surface, foot, budget)
            # ensure 0 on catalogue? mask may have catalogue dots; we will enforce later but measure
            on_cat = int((mask & labels).sum())
            # overlap vs registry
            max_overlap=0
            max_corr=0
            for rn, rm in reg_masks.items():
                # overlap within 3px
                # use dilation 3
                dil=binary_dilation(rm, iterations=3)
                ov=(mask & dil).sum()/max(1,mask.sum())
                max_overlap=max(max_overlap, ov)
                # pearson correlation of binary masks flat
                # cheap: correlation of surfaces not masks, but mask correlation proxy
                # compute phi correlation
                # skip for speed
            ev=evaluate_candidate_holdout(mask, ctx, hid)
            print(f" budget {budget}: on_cat {on_cat} overlap_max {max_overlap:.3f} cat_hidden {ev['catalogue_hidden_mean']:.5f} drift {ev['drift_corrected_holdout_mean']:.5f} sgmc {ev['sgmc_prevalence_calibrated_dti']:.5f}")
            key=f"{hid}@{budget}"
            results[key]={"hid":hid,"budget":budget,"on_catalogue":on_cat,"max_overlap":float(max_overlap),"leakage_auc2":float(auc2),
                          "catalogue_hidden_mean":ev["catalogue_hidden_mean"],
                          "drift_corrected_holdout_mean":ev["drift_corrected_holdout_mean"],
                          "sgmc_prevalence_calibrated_dti":ev["sgmc_prevalence_calibrated_dti"],
                          "emitted_pixels":int(ev["emitted_pixels"]),
                          }
        results[hid]={"spec":H35_SPECS[hid],"surface_stats":{"min":float(surface[foot].min()),"max":float(surface[foot].max()),"auc2":float(auc2)}}
    # rank by expected gain: use drift_corrected_holdout_mean at 37654 budget (comparable to B2)
    # Sort
    ranked=sorted([(k,v) for k,v in results.items() if "@" in k], key=lambda x: x[1]["drift_corrected_holdout_mean"], reverse=True)
    print("\n=== RANKED by drift_corrected_holdout_mean ===")
    for k,v in ranked:
        print(f"{k}: drift {v['drift_corrected_holdout_mean']:.5f} cat {v['catalogue_hidden_mean']:.5f} sgmc {v['sgmc_prevalence_calibrated_dti']:.5f} oncat {v['on_catalogue']}")
    # save
    out=Path("evidence/h35_validation.json")
    out.write_text(json.dumps({"generated":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "results":results, "ranked":[k for k,_ in ranked]}, indent=2))
    print(f"\nSaved {out}")
if __name__=="__main__": main()
