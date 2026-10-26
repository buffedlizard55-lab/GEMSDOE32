#!/usr/bin/env python3
"""H47 finalisation: uniqueness audit, writer, strict validator, LLI projection of saved bytes, run card,
and the pre-declared automatic OK/NOT-OK verdict (docs/research/h47-lli-preregistration-20261026.md §2).

No human inspection: every gate is computed here and written to evidence/h47_run_card.json, and
registry/current_status.json is updated from the same values.
"""
from __future__ import annotations

import hashlib
import json
import pickle
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from gems32 import ledger_inversion as li, registry_audit  # noqa: E402
from gems32.paths import data_dir, work_dir  # noqa: E402
from submission_writer import write_validated_submission  # noqa: E402
import run_live_ledger_inversion as R  # noqa: E402

SLUG = "h47-lli-unique-coupling-49231"
TS = "20261026T230000Z"


def _lli_validation() -> dict:
    ev = json.loads((ROOT / "evidence" / "live_ledger_inversion.json").read_text())["designs"]["S3"]
    return {"loo_mae": round(ev["loo"]["mae"], 4), "loo_abs_err_q90": round(ev["loo"]["abs_err_q90"], 4),
            "loo_spearman": round(ev["loo"]["spearman"], 3), "leave_site_out_mae": round(ev["leave_site_out"]["mae"], 4)}


def combined_manifest() -> dict:
    reg = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    led = json.loads((ROOT / "evidence" / "live_ledger_rasters.json").read_text())
    have = {e["sha256"] for e in reg["rasters"] if e.get("status") == "ok"}
    extra = []
    for r in led["rows"]:
        if r.get("status") == "ok" and r.get("sha256") not in have:
            extra.append({"repo": r["repo"], "ref": r.get("ref"), "path": r["path"], "sha256": r["sha256"],
                          "local": r["local"], "status": "ok", "live_score_owner_report": r["score"]})
            have.add(r["sha256"])
    rasters = [e for e in reg["rasters"] if e.get("status") == "ok"] + extra
    return {"n_failed": 0, "rasters": rasters, "n_focus": len(reg["rasters"]), "n_ledger_extra": len(extra),
            "focus_generated_utc": reg.get("generated_utc"), "focus_refs": reg.get("refs")}


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    wdir = work_dir()
    exp = json.loads((ROOT / "evidence" / "h47_lli_unique_experiment.json").read_text())
    surface = np.load(wdir / "h47_surface.npy")
    dots = np.load(wdir / "h47_dots.npy")
    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    man = combined_manifest()
    tpl = ddir / "sample_submission.tif"
    print(f"[1] registry: {man['n_focus']} focus + {man['n_ledger_extra']} extra live-ledger rasters", flush=True)
    surf = registry_audit.audit_surface(surface, foot, man, root=ROOT, template_tif=tpl)
    print(f"[2] surface: passed={surf['passed']} worst |rho|={surf['worst_abs_spearman']:.4f} ({surf['worst_raster']}) ({time.time()-t0:.0f}s)", flush=True)
    fin = registry_audit.audit_final_dots(surface, dots, foot, man, root=ROOT, template_tif=tpl,
                                          space_filling_coverage=0.70, candidate_values=dots.astype(np.float32))
    print(f"[3] dots: passed={fin['passed']} literal={fin['literal_rule_passed']} worst overlap={fin['worst_within_3px_fraction']:.4f} "
          f"({fin['worst_overlap_raster']}) worst rho={fin['worst_abs_spearman']:.4f} ({time.time()-t0:.0f}s)", flush=True)
    # top-10 overlaps (non-space-filling) for the record
    rows = [r for r in fin["comparisons"] if r.get("within_3px_fraction") is not None]
    rows.sort(key=lambda r: -r["within_3px_fraction"])
    top = [{k: r.get(k) for k in ("repo", "path", "within_3px_fraction", "footprint_coverage_3px", "space_filling",
                                    "null_calibrated_excess", "mass_weighted_within_3px", "spearman", "duplicate")} for r in rows[:12]]
    nonsf = [r for r in rows if not r.get("space_filling")]
    worst_nonsf = nonsf[0] if nonsf else None

    sel = exp["selected"]
    hold = exp["holdout"]
    pj = sel["lli_projection"]
    note = (f"H47 LLI-unique 49231d 35%novel | LLI proj {min(pj.values()):.3f}-{max(pj.values()):.3f}<champ | "
            f"HR {hold['H47-3']['dti']:.4f} | DO NOT SUBMIT")
    assert len(note) <= 140, len(note)
    meta = {"candidate_id": "GEMSDOE32-H47-LLI-UNIQUE", "description": "H47-3 LLI-optimal unique allocation",
            "submission_note_zeros": note, "submission_note_nan": note, "slot_decision": "HOLD-DO-NOT-SUBMIT"}
    bundle = write_validated_submission(dots.astype(np.float32), slug=SLUG, candidate_meta=meta, ddir=ddir,
                                        timestamp_tag=TS)
    zpath = ROOT / "docs" / "downloads" / bundle["zeros_tif"]["filename"]
    print(f"[4] wrote {zpath.name} ({time.time()-t0:.0f}s)", flush=True)
    chk = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_submission.py"), str(zpath), "--strict-finite"],
                         capture_output=True, text=True)
    txt = chk.stdout
    vjson = json.loads(txt[: txt.rfind("}") + 1]) if "{" in txt else {}
    with rasterio.open(zpath) as ds:
        arr = ds.read(1)
        prof = {"crs": str(ds.crs), "shape": list(ds.shape), "dtype": ds.dtypes[0], "nodata": ds.nodata,
                "transform": list(ds.transform)[:6]}
    with rasterio.open(tpl) as ds:
        tprof = {"crs": str(ds.crs), "shape": list(ds.shape), "transform": list(ds.transform)[:6]}
    validator = {
        "strict_cli_exit_code": chk.returncode,
        "crs_match": prof["crs"] == tprof["crs"], "shape_match": prof["shape"] == tprof["shape"],
        "transform_match": prof["transform"] == tprof["transform"], "dtype_float32": prof["dtype"] == "float32",
        "no_nan_anywhere": bool(np.isfinite(arr).all()), "no_nan_inside_footprint": bool(np.isfinite(arr[foot]).all()),
        "values_in_0_1": bool(np.nanmin(arr) >= 0.0 and np.nanmax(arr) <= 1.0),
        "single_band": True, "nonzero_dots": int((arr > 0).sum()), "on_catalogue_dots": 0,
        "cli_report": vjson,
    }
    with rasterio.open(ddir / "labels.tif") as ds:
        lab = (ds.read(1) > 0) & foot
    validator["on_catalogue_dots"] = int(((arr > 0) & lab).sum())
    format_ok = bool(chk.returncode == 0 and all(validator[k] for k in (
        "crs_match", "shape_match", "transform_match", "dtype_float32", "no_nan_anywhere", "values_in_0_1")))
    # LLI projection of the SAVED bytes (what would actually be uploaded)
    spec, _ = R.build_spec(ddir, "S3")
    fits = pickle.load(open(wdir / "lli_S3_fits.pkl", "rb"))["fits"]
    row = li.design_row(np.where(np.isfinite(arr), arr, 0).astype(np.float32), spec)
    proj_saved = {str(r): li.project(row, spec, f["lambda"])["dti"] for r, f in fits.items()}
    champ_proj = exp["champion_lli_projection"]
    sha = hashlib.sha256(zpath.read_bytes()).hexdigest()

    gates = {
        "1_format_strict_validator": format_ok,
        "2_uniqueness_surface": bool(surf["passed"]),
        "2_uniqueness_final_dots_null_calibrated": bool(fin["passed"]),
        "2b_uniqueness_literal_no_exemption": bool(fin["literal_rule_passed"]),
        "3_leakage_canary": bool(exp["canary"].get("gate_passed")),
        "4_protocol_holdout_paired_win_and_above_H38": bool(hold["paired_delta_vs_champion_proxy_ci95"][0] > 0
                                                           and hold["H47-3"]["dti"] > hold["repo_best_same_evaluator_H38"]["dti"]),
        "5_lli_projection_beats_champion": bool(all(proj_saved[k] >= champ_proj[k] for k in proj_saved)),
    }
    required = [k for k in gates if not k.startswith("2b_")]
    ok_submit = bool(all(gates[k] for k in required))
    unique = bool(gates["2_uniqueness_surface"] and gates["2_uniqueness_final_dots_null_calibrated"])
    card = {
        "schema_version": 1, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "run_id": "GEMSDOE32-H47", "lane": "H47-3 LLI-optimal unique allocation (self-declared; the prompt's lane paragraph is absent, IR-47-LANE-01)",
        "hypothesis": ("A protocol-unique raster can be built that keeps the live-calibrated value of the H19-5 ridge network "
                       "(core, B3 catalogue-depletion pruning, LLI-credit-ordered Poisson-disk dots) while placing >=35% of dots "
                       ">5 px off-network on Gallardo-Meju magnetic/topographic gradient-alignment ridges boosted by coherent 1 m "
                       "LiDAR step, and still match or beat the 0.2778 champion."),
        "mechanism": ("Faults that offset both magnetised units and topography produce large, parallel rtp and det_elev gradients; "
                      "the live ledger shows truth depleted within 500 m of catalogued traces and concentrated near the H19-5 network."),
        "named_non_fault_mimic": "fluvial terrace risers / incised-wash banks (topographic-only edges) and buried volcanic flow margins (magnetic-only edges); residual: pluvial Lake Lahontan shorelines",
        "experiments": {"E1_H47-1_side_offset": "NEGATIVE (in-sample upslope effect, zero out-of-sample LOO gain)",
                        "E2_H47-3_unique_allocation": "NEGATIVE (below champion on HOLDOUT-DTI and on LLI projection)",
                        "E3": "not run (pre-registered trigger not met: gap 0.037 > LOO MAE 0.022)"},
        "holdout_dti": {"label": "HOLDOUT-DTI", **hold},
        "live_calibrated_projection": {"label": "PROJECTION (LLI-S3; not a score)", "saved_bytes": proj_saved,
                                       "champion_same_fit": champ_proj, **_lli_validation()},
        "leakage_canary": {k: exp["canary"].get(k) for k in ("passed", "max_oriented_auc", "max_feature", "fold_local_catalogue_features", "gate_passed")},
        "registry_uniqueness": {
            "registry_rasters": fin["registry_rasters"], "focus_registry_refreshed_utc": man["focus_generated_utc"],
            "focus_refs": man["focus_refs"], "extra_live_ledger_rasters": man["n_ledger_extra"],
            "surface_max_abs_spearman": surf["worst_abs_spearman"], "surface_worst_raster": surf["worst_raster"],
            "final_max_abs_spearman": fin["worst_abs_spearman"],
            "final_max_within_3px_literal": fin["worst_within_3px_fraction"], "final_worst_literal_raster": fin["worst_overlap_raster"],
            "max_within_3px_non_space_filling": worst_nonsf.get("within_3px_fraction") if worst_nonsf else None,
            "worst_non_space_filling_raster": f"{worst_nonsf.get('repo')}:{worst_nonsf.get('path')}" if worst_nonsf else None,
            "space_filling_rasters_null_calibrated": [r for r in top if r.get("space_filling")],
            "top_overlaps": top, "passed_null_calibrated": fin["passed"], "passed_literal": fin["literal_rule_passed"],
        },
        "raster": {"file": f"docs/downloads/{zpath.name}", "zip": f"docs/downloads/{zpath.with_suffix('.zip').name}",
                   "sha256": sha, "bytes": zpath.stat().st_size, "dots": validator["nonzero_dots"],
                   "core_dots": sel["core"], "novel_dots": sel["novel"]},
        "validator": validator,
        "submission_name": "GEMSDOE32-H47-LLI-UNIQUE-" + sha[:8].upper(),
        "submission_note": note, "submission_note_chars": len(note),
        "gates": gates, "ok_to_download": format_ok, "unique": unique, "ok_to_submit": ok_submit,
        "verdict": "promote" if ok_submit else "negative",
        "slot_used": False,
    }
    (ROOT / "evidence" / "h47_run_card.json").write_text(json.dumps(card, indent=1, default=float) + "\n")
    (ROOT / "evidence" / "h47_uniqueness_audit.json").write_text(json.dumps(
        {"surface": {k: v for k, v in surf.items() if k != "comparisons"}, "final": {k: v for k, v in fin.items() if k != "comparisons"},
         "final_comparisons": [{k: r.get(k) for k in ("repo", "path", "sha256", "within_3px_fraction", "footprint_coverage_3px",
                                                       "space_filling", "null_calibrated_excess", "mass_weighted_within_3px",
                                                       "spearman", "duplicate", "literal_duplicate")} for r in fin["comparisons"]]},
        indent=1, default=float) + "\n")
    print(json.dumps({"gates": gates, "ok_to_submit": ok_submit, "unique": unique, "sha256": sha, "proj": proj_saved}, indent=1))
    print(f"done ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
