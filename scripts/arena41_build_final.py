#!/usr/bin/env python3
"""Arena41 final build: unique PF-ONLY TIF + zip + automated gate validator (no human inspection).

Uses the shared submission writer (gemsdoe32.submission.write_submission_geotiff).
Final eligibility applies the live-validated B2 rule on the FULL catalogue (legitimate for a
final file; holdout numbers come from the OOF field in EXP2). Writes:
 docs/downloads/gemsdoe32-arena41-pfonly-blindbasin-37654-<ts>-<digest8>-zeros.tif (+ .zip + writer sidecar)
 docs/downloads/checks-<same>.json, evidence/arena41_build.json,
 registry/arena41_submission.json, evidence/arena41_run_card.json
Verdict is COMPUTED from the pre-registered gates (docs/research/arena41-preregistration-and-hypotheses.md).
"""
from __future__ import annotations
import hashlib, json, sys, zipfile
from datetime import datetime, timezone
from pathlib import Path
import numpy as np, rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from gems32.paths import data_dir, work_dir
from gems32.pfonly import dot_thin
from gemsdoe32.submission import write_submission_geotiff, validate_submission_geotiff
DATA=data_dir(); WORK=work_dir(); DL=ROOT/"docs/downloads"; BUDGET=37654
def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1<<20),b''): h.update(c)
    return h.hexdigest()
def read_mask(p):
    with rasterio.open(p) as s: a=s.read(1)
    return np.isfinite(a)&(a>0)
def main():
    with rasterio.open(DATA/"sample_submission.tif") as s: foot=np.isfinite(s.read(1))
    with rasterio.open(DATA/"labels.tif") as s: labels=(s.read(1)>0)&foot
    dcat=distance_transform_edt(~labels)
    field=np.load(WORK/"arena41_full_PF_ONLY.npy")
    assert field.shape==foot.shape
    # --- uniqueness BEFORE placement: sampled Spearman surface vs each distinct registry raster
    rng=np.random.default_rng(41); fidx=np.flatnonzero(foot.ravel())
    samp=rng.choice(fidx,size=250000,replace=False); fv=field.ravel()[samp].astype(np.float64)
    reg_paths=sorted(DL.glob("*.tif"))+sorted((DATA/"scored").glob("*.tif"))
    seen={}; surf_corr=[]
    for p in reg_paths:
        h=sha_file(p)
        if h in seen: continue
        seen[h]=p.name; m=read_mask(p)
        rho=float(spearmanr(fv,m.ravel()[samp].astype(np.float64)).statistic)
        surf_corr.append({"file":p.name,"sha256":h,"spearman_surface_sampled":rho,"dots":int(m.sum())})
    surf_corr.sort(key=lambda r:-abs(r["spearman_surface_sampled"]))
    print("surface spearman max",surf_corr[0],flush=True)
    # --- placement
    mask=dot_thin(field, foot&(dcat>2.0), BUDGET, min_dist=2.8)
    digest8=sha_bytes(mask.astype(np.uint8).tobytes())[:8]
    ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem=f"gemsdoe32-arena41-pfonly-blindbasin-37654-{ts}-{digest8}-zeros"
    out_tif=DL/f"{stem}.tif"
    note140="Arena41 PF-only blind-basin 37654d B2 zeros | HOLDOUT gates G2/G3 FAIL vs surf-ctrl | DO NOT SUBMIT"
    assert len(note140)<=140, len(note140)
    manifest=write_submission_geotiff(mask.astype(np.float32), DATA/"sample_submission.tif", out_tif, outside_mode="zeros", note=note140)
    zip_path=DL/f"{stem}.zip"
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z: z.write(out_tif,arcname=out_tif.name)
    # --- independent re-read validator (template-strict, whole-array finite)
    rep=validate_submission_geotiff(out_tif, DATA/"sample_submission.tif", strict_whole_array_finite=True)
    with rasterio.open(out_tif) as s:
        a=s.read(1); prof={"crs":str(s.crs),"transform":list(s.transform)[:6],"shape":[s.height,s.width],"dtype":s.dtypes[0],"count":s.count,"nodata":repr(s.nodata)}
    m2=np.isfinite(a)&(a>0)
    checks={"validator_passed":bool(rep.passed),"checks":[c.to_dict() for c in rep.checks],
      "all_cells_finite":bool(np.isfinite(a).all()),"nan_cells":int(np.isnan(a).sum()),
      "min":float(a.min()),"max":float(a.max()),"values_outside_0_1":int(((a<0)|(a>1)).sum()),
      "nodata_is_none":prof["nodata"]=="None","dots":int(m2.sum()),"mask_roundtrip_exact":bool(np.array_equal(m2,mask)),
      "dots_on_catalogue":int((m2&labels).sum()),"dots_within_200m_catalogue":int((m2&(dcat<=2.0)).sum()),
      "min_dist_to_catalogue_px":float(dcat[m2].min())}
    checks["portal_legal"]=bool(rep.passed and checks["all_cells_finite"] and checks["values_outside_0_1"]==0 and checks["nodata_is_none"])
    (DL/f"checks-{stem}.tif.json").write_text(json.dumps({"file":out_tif.name,"sha256":sha_file(out_tif),"bytes":out_tif.stat().st_size,"profile":prof,"checks":checks},indent=2)+"\n")
    # --- uniqueness of FINAL dots vs every distinct registry raster (incl. champion)
    uniq=[]
    for rec in surf_corr:
        p=next(pp for pp in reg_paths if pp.name==rec["file"] and sha_file(pp)==rec["sha256"])
        m=read_mask(p)&foot
        if np.array_equal(m,mask): frac_in=frac_out=1.0; phi=1.0
        else:
            d_other=distance_transform_edt(~m); frac_in=float((d_other[mask]<=3.0).mean())
            d_me=distance_transform_edt(~mask); frac_out=float((d_me[m]<=3.0).mean()) if m.any() else 0.0
            n=int(foot.sum()); na=int(mask.sum()); nb=int(m.sum()); nab=int((mask&m).sum())
            phi=float((nab*n-na*nb)/np.sqrt(float(na)*float(n-na)*float(nb)*float(n-nb))) if na and nb else 0.0
        uniq.append({**rec,"phi_binary_final":phi,"frac_final_within3px_of_other":frac_in,"frac_other_within3px_of_final":frac_out})
    uniq.sort(key=lambda r:-r["frac_final_within3px_of_other"])
    print("uniq worst",uniq[0],flush=True)
    # --- gates from pre-registered evidence
    e2=json.loads((ROOT/"evidence/arena41_exp2_oof.json").read_text())
    pf=e2["arms"]["PF_ONLY"]; ct=e2["arms"]["CTRL_SURF"]; rnd=e2["random_37654"]
    pf37=pf["budgets"]["37654"]; ct37=ct["budgets"]["37654"]
    g1=max(pf["auc_by_quadrant"].values())<=0.90
    g2=pf37["pooled"]["pooled_dti"]>3.0*rnd["pooled"]["pooled_dti"]
    g3=(pf37["sgmc_prevalence_calibrated_dti"]>ct37["sgmc_prevalence_calibrated_dti"]) and (pf37["pooled"]["pooled_dti"]>=0.70*ct37["pooled"]["pooled_dti"])
    g4=bool(all(abs(r["spearman_surface_sampled"])<0.90 for r in surf_corr) and all(r["frac_final_within3px_of_other"]<=0.70 for r in uniq) and sha_file(out_tif) not in seen)
    g5=bool(checks["portal_legal"] and checks["dots_on_catalogue"]==0 and checks["dots_within_200m_catalogue"]==0 and checks["dots"]==BUDGET)
    verdict="promote" if all([g1,g2,g3,g4,g5]) else "negative"
    build={"candidate_id":"ARENA41-PFONLY","file":out_tif.name,"zip":zip_path.name,"sha256":sha_file(out_tif),
      "zip_sha256":sha_file(zip_path),"bytes":out_tif.stat().st_size,"dots":int(mask.sum()),"digest8_mask":digest8,
      "note_le140":note140,"unique_submission_name":"GEMSDOE32-ARENA41-PFONLY","profile":prof,"checks":checks,
      "writer_manifest":manifest,"surface_uniqueness_top5":surf_corr[:5],"dot_uniqueness_top5":uniq[:5],
      "dot_uniqueness_vs_champion":[r for r in uniq if "e5eb6e7e-zeros" in r["file"]],
      "gates":{"G1_auc_le_0.90":g1,"G2_pooled_gt_3x_random":g2,"G3_lane_offcat_beats_ctrl_and_retains70":g3,
               "G4_uniqueness":g4,"G5_format":g5},"verdict":verdict,
      "ok_to_submit":verdict=="promote"}
    (ROOT/"evidence/arena41_build.json").write_text(json.dumps(build,indent=2)+"\n")
    (ROOT/"registry/arena41_submission.json").write_text(json.dumps({k:build[k] for k in ["candidate_id","file","zip","sha256","bytes","dots","note_le140","unique_submission_name","verdict","ok_to_submit","gates"]},indent=2)+"\n")
    run_card={
      "hypothesis":"PF-ONLY blind-basin: subsurface potential-field-only HGB recovers buried faults missed by DEM/LiDAR-trained (catalogue-selection-biased) fields",
      "mechanism":"Bands 1,2,3,5,6,9,11,13,14,15,17,18 + HGM/FFT-upward-continuation worm persistence/Hessian/basement+conductivity gradients; HGB quadrant-OOF; dot_thin 2.8px; final B2",
      "named_nonfault_mimic":"Basement lithologic contacts and intrusion/volcanic margins (persistent potential-field edges with no fault)",
      "holdout":{"label":"HOLDOUT-DTI (NOT an organizer score)","evaluator":"gems32.holdout.evaluate_candidate_holdout @012e17b pooled from per-cell TP/FP/FN; hide 20% whole components x 4 quadrants x draws20/21; alpha0.2 beta0.8 R3px",
        "PF_ONLY_37654":pf37["pooled"],"CTRL_SURF_37654":ct37["pooled"],"RANDOM_37654":rnd["pooled"],
        "sgmc_prev_cal_PF_vs_CTRL":[pf37["sgmc_prevalence_calibrated_dti"],ct37["sgmc_prevalence_calibrated_dti"]],
        "auc_by_quadrant_PF":pf["auc_by_quadrant"]},
      "correlation_overlap_vs_registry":{"max_abs_spearman_surface_sampled":max(abs(r["spearman_surface_sampled"]) for r in surf_corr),
        "max_frac_final_within3px":max(r["frac_final_within3px_of_other"] for r in uniq),"worst_registry":uniq[0]["file"],
        "vs_champion":build["dot_uniqueness_vs_champion"]},
      "raster_sha256":sha_file(out_tif),
      "validator_output":{"no_nan_inside_footprint":checks["nan_cells"]==0,"values_in_0_1":checks["values_outside_0_1"]==0,
        "crs_shape_transform_match":bool(rep.passed),"nodata":prof["nodata"],"portal_legal":checks["portal_legal"]},
      "submission_name":"GEMSDOE32-ARENA41-PFONLY","note_le140":note140,
      "organizer_confirmed_scores_cited":{"leaderboard_2026-10-25_rank1_xiaofanhu":0.4413,"champion_H33-2-B2_owner_reported_NOT_receipt_verified":0.2778},
      "verdict":verdict}
    (ROOT/"evidence/arena41_run_card.json").write_text(json.dumps(run_card,indent=2)+"\n")
    print(json.dumps({"file":out_tif.name,"sha256":build["sha256"],"gates":build["gates"],"verdict":verdict},indent=2))
if __name__=="__main__": main()
