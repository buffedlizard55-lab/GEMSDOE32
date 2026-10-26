#!/usr/bin/env python3
"""ARENA48 Pass-2 independent verification (does not trust the runner's numbers).

Re-reads the saved TIF bytes and checks, from scratch:
  * sha256, ZIP single-member identity, NaN-twin mask identity;
  * strict portal validation (shared ``validate_submission_geotiff``, the tool behind
    ``scripts/check_submission.py --strict-finite``) + raw array range/NaN counts;
  * off-catalogue SGMC HOLDOUT-DTI on the flat final mask (must reproduce the run card);
  * registry uniqueness again for BOTH placement surfaces (gated EXP2 field and the
    ``jx_quiescent`` stage-2 field) and the final dots, listing malformed entries;
  * the champion B-ladder annulus claim: distances-to-catalogue of the dots removed
    D2.8->solo (B=1) and solo->champion (B=2), from the focus-9 byte audit masks.
Output: evidence/arena48_pass2_verification.json
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir, work_dir  # noqa: E402
from gems32.registry_audit import audit_final_dots, audit_surface, load_manifest  # noqa: E402
from gemsdoe32.submission import validate_submission_geotiff  # noqa: E402


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def dots(path: Path, foot):
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.isfinite(a) & (a > 0) & foot, a


def main() -> int:
    card = json.loads((ROOT / "evidence/arena48_jxstep_run_card.json").read_text())
    ddir = data_dir()
    zpath = ROOT / card["artifacts"]["primary_zeros_tif"]
    npath = ROOT / card["artifacts"]["nan_companion_tif"]
    zippath = Path(card["artifacts"]["zip_archive"])
    if not zippath.is_absolute():
        zippath = ROOT / zippath
    template = ddir / "sample_submission.tif"
    with rasterio.open(template) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ddir / "labels.tif") as ds:
        labels = (ds.read(1) > 0) & foot

    zmask, zarr = dots(zpath, foot)
    nmask, _ = dots(npath, foot)
    with zipfile.ZipFile(zippath) as zf:
        members = zf.namelist()
        zip_sha = hashlib.sha256(zf.read(members[0])).hexdigest() if len(members) == 1 else None
    portal = validate_submission_geotiff(zpath, template, strict_whole_array_finite=True).to_dict()

    ctx = holdout.load_holdout_context(ddir)
    sg = holdout.evaluate_sgmc_with_ci(zmask, ctx, name="A48_PASS2")
    card_sg = card["holdout_dti"]["secondary_off_catalogue_sgmc"]["sgmc_prevalence_calibrated_dti"]

    manifest = load_manifest(ROOT / "registry/focus_registry_manifest.json")
    surface_path = work_dir() / "a48_best_surface.npy"
    audits = {}
    if surface_path.exists():
        surf = np.load(surface_path)
        audits["exp2_gated_surface"] = audit_surface(surf, foot, manifest, root=ROOT, template_tif=template)
        final = audit_final_dots(surf, zmask, foot, manifest, root=ROOT, template_tif=template)
    else:
        surf = np.where(foot, zmask.astype(np.float32), 0.0)
        audits["exp2_gated_surface"] = {"status": "cached surface missing; dot-mask proxy used for final audit only"}
        final = audit_final_dots(surf, zmask, foot, manifest, root=ROOT, template_tif=template)
    jx_path = work_dir() / "jxstep7.npy"
    if jx_path.exists():
        jx = np.lib.format.open_memmap(jx_path, mode="r")
        quiescent = np.asarray(jx[:, :, 6], np.float32).copy()
        quiescent[~foot] = 0.0
        audits["jx_quiescent_surface"] = audit_surface(quiescent, foot, manifest, root=ROOT, template_tif=template)

    def brief(a):
        if "comparisons" not in a:
            return a
        comps = a["comparisons"]
        malformed = [{k: c.get(k) for k in ("repo", "path", "status")} for c in comps if not c.get("measurable")]
        gen = [c for c in comps if "lattice-s5" not in str(c.get("path"))]
        top = sorted([c for c in gen if c.get("within_3px_fraction") is not None],
                     key=lambda c: -c["within_3px_fraction"])[:5]
        return {"registry_rasters": a["registry_rasters"], "malformed_or_missing": a["malformed_or_missing"],
                "malformed_nonmeasurable": malformed[:10],
                "worst_abs_spearman": a.get("worst_abs_spearman"), "worst_raster": a.get("worst_raster"),
                "worst_within_3px": a.get("worst_within_3px_fraction"),
                "worst_overlap_raster": a.get("worst_overlap_raster"),
                "top5_genuine_by_overlap": [{k: c.get(k) for k in ("repo", "path", "within_3px_fraction", "spearman")}
                                            for c in top],
                "passed": a["passed"]}

    # Champion ladder annulus verification from the focus-9 audit masks.
    f9 = json.loads((ROOT / "evidence/arena48_focus9_overlap.json").read_text())
    masks = {}
    for row in f9["winners"]:
        if "file" not in row:
            continue
        cand = [r for r in manifest["rasters"] if r["repo"] == row["site"] and r["path"] == row["file"]]
        if cand:
            m, _ = dots(ROOT / cand[0]["local"], foot)
            masks[row["site"]] = m
    d_lab = distance_transform_edt(~labels)
    def annulus(removed):
        d = d_lab[removed]
        return {"n_removed": int(removed.sum()), "d_min_px": float(d.min()) if d.size else None,
                "d_max_px": float(d.max()) if d.size else None,
                "share_with_d_le_1px": round(float((d <= 1.0).mean()), 6) if d.size else None,
                "share_with_1lt_d_le_2px": round(float(((d > 1.0) & (d <= 2.0)).mean()), 6) if d.size else None,
                "share_with_d_gt_2px": round(float((d > 2.0).mean()), 6) if d.size else None}
    ladder = {}
    if {"GEMSDOE25", "GEMSDOE31", "GEMSDOE32"} <= masks.keys():
        ladder["d28_to_solo_B1_removed"] = annulus(masks["GEMSDOE25"] & ~masks["GEMSDOE31"])
        ladder["solo_to_champion_B2_removed"] = annulus(masks["GEMSDOE31"] & ~masks["GEMSDOE32"])
        ladder["champion_dots_with_d_le_2px"] = int((d_lab[masks["GEMSDOE32"]] <= 2.0).sum())

    out = {
        "file": card["artifacts"]["primary_zeros_tif"],
        "sha256_recomputed": sha256(zpath), "sha256_run_card": card["raster_sha256"],
        "sha_match": bool(sha256(zpath) == card["raster_sha256"]),
        "zip_members": members, "zip_member_sha_equals_tif_sha": bool(zip_sha == card["raster_sha256"]),
        "nan_twin_mask_identical": bool(np.array_equal(zmask, nmask)),
        "dots": int(zmask.sum()), "on_catalogue_dots": int((zmask & labels).sum()),
        "whole_array_finite": int(np.isfinite(zarr).sum()), "whole_array_cells": int(zarr.size),
        "nan_inside_footprint": int(np.isnan(zarr[foot]).sum()),
        "values_outside_0_1_whole_array": int(((zarr < 0) | (zarr > 1) | ~np.isfinite(zarr)).sum()),
        "portal_strict_finite_passed": bool(portal["passed"]), "portal_report": portal,
        "sgmc_flat_recheck": {"label": "HOLDOUT-DTI", "evaluator_version": "GEMSDOE32-SGMC-CAL-v3.0",
                              "n_withheld_positives": sg["n_withheld_positives"],
                              "sgmc_prevalence_calibrated_dti": sg["sgmc_prevalence_calibrated_dti"],
                              "ci95": sg["sgmc_calibrated_ci95"], "run_card_value": card_sg,
                              "abs_diff_vs_run_card": abs(float(sg["sgmc_prevalence_calibrated_dti"]) - float(card_sg))},
        "uniqueness_recheck": {k: brief(v) for k, v in audits.items()},
        "final_dots_recheck": brief(final),
        "champion_ladder_annulus_from_bytes": ladder,
    }
    (ROOT / "evidence/arena48_pass2_verification.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("sha_match", "zip_member_sha_equals_tif_sha", "nan_twin_mask_identical",
                                           "dots", "on_catalogue_dots", "nan_inside_footprint",
                                           "values_outside_0_1_whole_array", "portal_strict_finite_passed")}, indent=2))
    print(json.dumps(out["sgmc_flat_recheck"], indent=2))
    print(json.dumps(out["champion_ladder_annulus_from_bytes"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
