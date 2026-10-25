#!/usr/bin/env python3
"""Generate final UNIQUE TIF submission: CV-field + alteration fusion, B2 flank, sorted Poisson."""
import sys, json, time, hashlib
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
from gems32.submission import write_submission_pair, sha256_file  # check import
from gems32.h35_new import build_h35d

def poisson_sorted(field, foot, exclusion, min_dist_px, budget, pool_quantile=0.3):
    valid = foot & ~exclusion
    vals = field[valid]
    thresh=np.quantile(vals, 1.0-pool_quantile) if pool_quantile<1 else -np.inf
    cand_mask = valid & (field >= thresh)
    yy,xx=np.nonzero(cand_mask)
    scores=field[yy,xx]
    order=np.argsort(scores)[::-1]
    yy,xx=yy[order], xx[order]
    H,W=foot.shape
    cell=max(1.0,float(min_dist_px))
    grid={}
    out=np.zeros(foot.shape,bool)
    r2=min_dist_px*min_dist_px
    kept=0
    for y,x in zip(yy,xx):
        if kept>=budget: break
        cy,cx=int(y//cell), int(x//cell)
        ok=True
        for gy in range(cy-2,cy+3):
            for gx in range(cx-2,cx+3):
                for (ky,kx) in grid.get((gy,gx),()):
                    if (y-ky)**2 + (x-kx)**2 < r2:
                        ok=False; break
                if not ok: break
            if not ok: break
        if ok:
            out[y,x]=True
            grid.setdefault((cy,cx),[]).append((int(y),int(x)))
            kept+=1
    # if not enough, expand pool
    if kept < budget*0.95 and pool_quantile<0.9:
        return poisson_sorted(field, foot, exclusion, min_dist_px, budget, pool_quantile+0.2)
    return out

def main():
    ddir=data_dir()
    wdir=work_dir()
    bands=wdir/"bands"
    foot=np.load(bands/"_footprint.npy")
    labels=np.load(bands/"_labels.npy")
    ctx=load_holdout_context(ddir)
    # Load fields
    cv_field=np.load("/tmp/gems_work/cv_field.npy")
    # Build H35-D alteration surface
    print("Building H35-D...")
    h35d=build_h35d(bands, ddir, foot)
    # Fusion: 0.75 CV + 0.25 H35D (CV dominates but alteration adds off-catalogue signal)
    fused = 0.75*cv_field + 0.25*h35d
    fused = np.clip(fused,0,1)
    # Normalize robust
    v=fused[foot]
    med=np.median(v); p95=np.percentile(v,95)
    fused_norm=np.clip((fused-med)/(p95-med+1e-9),0,1)
    fused_norm[~foot]=0
    # Exclusion: B=2 flank (200m buffer) + catalogue itself
    exclusion=binary_dilation(labels, iterations=2)
    # Budget: target 40k-44k, choose 42600 to be distinct from existing 44090/37654/46090
    budget=42600
    min_dist=2.35
    mask=poisson_sorted(fused_norm, foot, exclusion, min_dist, budget, pool_quantile=0.35)
    n=int(mask.sum())
    print(f"Generated mask {n} px (target {budget}) oncat {(mask & labels).sum()} flank_exclusion {exclusion.sum()}")
    # Evaluate holdout
    ev=evaluate_candidate_holdout(mask, ctx, "H35-CV-ALT-FUSION")
    print(json.dumps(ev, indent=2))
    # Overlap checks vs registry
    d28=read_binary(Path("docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"))
    overlap=(mask & binary_dilation(d28,iterations=3)).sum()/max(1,n)
    print(f"Overlap vs D2.8 within 3px: {overlap:.3f}")
    # Correlation of fused surface vs D2.8 field proxy? Use binary mask correlation approx
    # Compute rank correlation of fused field vs cv field? Not needed
    # Leakage canary: AUC of fused
    from sklearn.metrics import roc_auc_score
    auc=roc_auc_score(labels[foot], fused_norm[foot])
    auc2=max(auc,1-auc)
    print(f"Leakage AUC {auc:.4f} two-sided {auc2:.4f} {'LEAK' if auc2>0.90 else 'ok'}")
    # Write submission using gems32 writer (requires footprint+labels)
    from gems32.submission import write_submission_pair
    template=ddir/"sample_submission.tif"
    ts=time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    slug=f"h35-cv-altfusion-b2-{budget}"
    # candidate_meta needed by writer
    candidate_meta={
        "candidate_id": slug,
        "description": f"CV HGB field (0.68 AUC) fused 75/25 with Th/K alteration edge (H35-D), B=2 flank buffer, sorted Poisson 2.35px, {budget} dots",
        "submission_note_zeros": "H35 CV+ALT B2 {dots}dots 0onCat sorted2.35 fused CV75+ALT25 | HOLDOUT-DTI {drift_cal:.4f}±{cat_hid:.4f} SGMC {sgmc_cal:.4f}",
        "submission_note_nan": "H35 CV+ALT B2 {dots}dots | HOLDOUT-DTI {drift_cal:.4f}",
        "catalogue_hidden_mean": float(ev["catalogue_hidden_mean"]),
        "catalogue_hidden_per_quadrant": ev["catalogue_hidden_per_quadrant"],
        "sgmc_prevalence_calibrated_dti": float(ev["sgmc_prevalence_calibrated_dti"]),
        "drift_corrected_holdout_mean": float(ev["drift_corrected_holdout_mean"]),
        "drift_corrected_per_quadrant": ev["drift_corrected_per_quadrant"],
        "predicted_leaderboard_dti": float(ev["drift_corrected_holdout_mean"]),  # placeholder
        "ei_drift_corrected": 0.0,
        "slot_decision": "test-candidate",
    }
    bundle=write_submission_pair(mask, foot, labels, template, Path("docs/downloads"), slug, ts, candidate_meta)
    out_zeros=Path(bundle["zeros_tif"]["filename"])
    # Actually bundle returns dict with audit, need to construct path
    zeros_path=Path("docs/downloads")/f"gemsdoe32-{slug}-{ts}-{bundle['content_digest8']}-zeros.tif"
    nan_path=Path("docs/downloads")/f"gemsdoe32-{slug}-{ts}-{bundle['content_digest8']}-nan.tif"
    print(f"Wrote {zeros_path} and {nan_path}")
    sha=hashlib.sha256(zeros_path.read_bytes()).hexdigest()
    print(f"SHA256 {sha}")
    # Validator re-read
    with rasterio.open(template) as tpl, rasterio.open(zeros_path) as sub:
        tpl_data=tpl.read(1)
        valid_foot=np.isfinite(tpl_data)
        sub_data=sub.read(1)
        inside=sub_data[valid_foot]
        print(f"Validator: shape {sub.shape} vs tpl {tpl.shape} CRS {sub.crs} vs {tpl.crs} transform {sub.transform==tpl.transform}")
        print(f" Inside footprint: min {inside.min():.3f} max {inside.max():.3f} finite {np.isfinite(inside).all()} NaN {np.isnan(sub_data).sum()}")
        print(f" Values in [0,1] inside: {((inside>=0)&(inside<=1)).all()} all finite {np.isfinite(sub_data).all()}")
        # Capture for run card validator
        validator_ok = bool(np.isfinite(inside).all() and ((inside>=0)&(inside<=1)).all() and np.isfinite(sub_data).all() and sub.shape==tpl.shape and sub.crs==tpl.crs and sub.transform==tpl.transform)
    # Update ev_out with real paths
    ev_out_path="evidence/h35_final_run_card.json"
    # Validator output
    template_path=ddir/"sample_submission.tif"
    with rasterio.open(template_path) as tpl, rasterio.open(out_zeros) as sub:
        tpl_data=tpl.read(1)
        valid_foot=np.isfinite(tpl_data)
        sub_data=sub.read(1)
        inside=sub_data[valid_foot]
        print(f"Validator: shape {sub.shape} vs tpl {tpl.shape} CRS {sub.crs} vs {tpl.crs} transform {sub.transform==tpl.transform}")
        print(f" Inside footprint: min {inside.min():.3f} max {inside.max():.3f} finite {np.isfinite(inside).all()} NaN {np.isnan(sub_data).sum()}")
        print(f" Outside footprint: unique vals {np.unique(sub_data[~valid_foot])[:5]}")
        print(f" Values in [0,1] inside: {((inside>=0)&(inside<=1)).all()} all finite {np.isfinite(sub_data).all()}")
        print(f" SHA256 {hashlib.sha256(out_zeros.read_bytes()).hexdigest()}")
    # Compute correlation vs registry surfaces (approx via mask correlation)
    # Save evidence
    ev_out={
        "hypothesis":"H35-CV-ALT-FUSION: cross-validated 35-channel HGB field (0.68 AUC) fused 75/25 with radiometric Th/K alteration edge (H35-D), B=2 catalogue flank buffer, score-sorted Poisson disk 2.35px",
        "mechanism":"HGB detector learns subtle multi-band lineaments (curvature, ridge, edge) that correlate with held-out faults; fusion adds alteration geochemical signal over blind conduits lacking scarp; sorted Poisson maximizes credit per dot vs row-major BFS",
        "non_fault_mimic":"Fluvial terrace scarps and lithologic contacts produce identical curvature/alteration lineaments; river incision terraces in Lahontan basin mimic fault scarps in detrended elevation and Th/K (alluvial Th enrichment)",
        "holdout_dti": ev["drift_corrected_holdout_mean"],
        "holdout_ci": [ev["drift_corrected_holdout_mean"]-1.96*ev["drift_corrected_holdout_std"], ev["drift_corrected_holdout_mean"]+1.96*ev["drift_corrected_holdout_std"]],
        "catalogue_hidden_mean": ev["catalogue_hidden_mean"],
        "sgmc_prevalence_calibrated_dti": ev["sgmc_prevalence_calibrated_dti"],
        "leakage_auc2": float(auc2),
        "correlation_overlap": {"overlap_3px_vs_D2_8": float(overlap), "rank_corr_proxy": float(np.corrcoef(fused_norm[foot].ravel()[:100000], cv_field[foot].ravel()[:100000])[0,1]) if foot.sum()>100000 else 0},
        "raster_sha256": hashlib.sha256(out_zeros.read_bytes()).hexdigest(),
        "validator": {"no_nan_inside_footprint": bool(np.isfinite(inside).all()), "values_in_01": bool(((inside>=0)&(inside<=1)).all()), "crs_match": str(sub.crs==tpl.crs), "shape_match": bool(sub.shape==tpl.shape), "transform_match": bool(sub.transform==tpl.transform)},
        "submission_name": name,
        "note": f"H35 CV+ALT B2 {budget}dots 0onCat sortedPoisson2.35 fused CV75+ALT25",
        "verdict": "negative" if ev["drift_corrected_holdout_mean"] < 0.14801 else "promote",
        "evaluator_version": "GEMSDOE32-HOLDOUT-v2 (4-quadrant, 15px collar, 12px erosion, 12691 LB prevalence calibrated)",
        "withheld_positives": int(sum([c.n_truth for c in ctx.cells])),
        "footprint_px": int(foot.sum()),
    }
    Path("evidence/h35_final_run_card.json").write_text(json.dumps(ev_out, indent=2))
    print(json.dumps(ev_out, indent=2))

if __name__=="__main__": main()
