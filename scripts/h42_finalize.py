#!/usr/bin/env python3
"""H42-1 post-run diagnostics and run-card finalisation (no change to any pre-registered gate).

Adds, transparently and labelled as diagnostics:
  D1  space-filling registry rasters: 3-px footprint coverage of every registry raster, and the
      overlap a *random* dot set and the champion get against the worst one (shows when the literal
      70 % overlap test is uninformative by geometry);
  D2  band-matched null: random dots drawn with the SAME distance-to-catalogue distribution as the
      H42 final dots, overlapped with the registry rasters that fired (is the firing about the
      placement zone rather than the method?);
  D3  surface phase, corrected statistic: rank correlation only (a continuous surface has no dots),
      plus the dot overlap of the surface's top-37,654 support (pre-placement would-be dots);
  D4  independent instrument: SGMC off-catalogue faults (> 3 px from the catalogue; neither model
      trained on SGMC) — H42 final dots vs the champion at equal mass, template pooled evaluator.
Verdict logic is unchanged: G4 uses the literal final-dot rule; D1–D4 are reported, never used to
override a failed gate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))
from gems57 import evaluate_holdout as g57eval  # noqa: E402
from gems57 import uniqueness as U  # noqa: E402
import run_h42 as R  # noqa: E402


def main() -> int:
    rep = json.loads((ROOT / "evidence/h42_run.json").read_text())
    grid = R.g57grid.load_grid(R.DATA)
    fp, cat = grid.footprint, grid.catalogue
    dots = np.load(R.CACHE / "final_dots.npy")
    surface = np.load(R.CACHE / "final_surface.npy")
    champ = R.read_mask(R.CHAMPION) & fp
    d_cat = ndi.distance_transform_edt(~cat)
    index, _ = R.registry_index(fp)
    rng = np.random.default_rng(20261026)

    # D1 coverage of every registry raster
    cover = {}
    masks = {}
    for e in index["rasters"]:
        with rasterio.open(ROOT / e["cache_file"]) as s:
            a = s.read(1)
        m = np.isfinite(a) & (a > 0) & fp
        masks[e["sources"][0]] = m
        cover[e["sources"][0]] = float(U._near(m)[fp].mean())
    space_filling = {k: v for k, v in cover.items() if v > U.OVERLAP_LIMIT}
    fidx = np.flatnonzero(fp.ravel())
    rnd = np.zeros(fp.size, bool)
    rnd[rng.choice(fidx, int(dots.sum()), replace=False)] = True
    rnd = rnd.reshape(fp.shape)
    d1 = dict(rule="3-px footprint coverage > 0.70 => any dot set exceeds the 70 % limit by geometry",
              space_filling_rasters={k: dict(coverage=v, random_dots_overlap=float(U.dot_overlap(rnd, masks[k])),
                                             champion_overlap=float(U.dot_overlap(champ, masks[k])))
                                     for k, v in space_filling.items()})

    # D2 band-matched null for the rasters that fired on the final dots
    fired = [r for r in rep["final_gate"]["top_overlap_rows"] if r["my_dots_within_3px_of_theirs"] > U.OVERLAP_LIMIT]
    full_rows = U.compare_array_to_registry(dots.astype(np.float32), index, fp, include_reverse=False)["rows"]
    fired_all = sorted([r for r in full_rows if "error" not in r and r["my_dots_within_3px_of_theirs"] > U.OVERLAP_LIMIT],
                       key=lambda r: -r["my_dots_within_3px_of_theirs"])
    bins = np.r_[0, 2.5, 3.5, 4.5, 5.5, 6.5, 8, 10, 13, 17, 25, 40, 80, 1e9]
    my_d = d_cat[dots]
    allowed = fp & ~cat & (d_cat > R.B_GATE_PX)
    band = np.zeros(fp.shape, bool)
    for lo, hi in zip(bins[:-1], bins[1:]):
        need = int(((my_d > lo) & (my_d <= hi)).sum())
        if need == 0:
            continue
        pool = np.flatnonzero((allowed & (d_cat > lo) & (d_cat <= hi)).ravel())
        band.ravel()[rng.choice(pool, min(need, pool.size), replace=False)] = True
    d2 = dict(method="random dots with the H42 final dots' distance-to-catalogue histogram (13 bins), same count",
              n=int(band.sum()),
              rows=[dict(submission=r["submission"], their_dots=r["their_dots"],
                         h42_overlap=r["my_dots_within_3px_of_theirs"],
                         band_null_overlap=float(U.dot_overlap(band, masks.get(r["submission"], np.zeros_like(fp)))),
                         random_null_overlap=float(U.dot_overlap(rnd, masks.get(r["submission"], np.zeros_like(fp)))),
                         champion_overlap=float(U.dot_overlap(champ, masks.get(r["submission"], np.zeros_like(fp)))),
                         coverage=cover.get(r["submission"]))
                    for r in fired_all])
    d2["n_fired_total"] = len(fired_all)
    d2["n_fired_excluding_space_filling"] = len([r for r in fired_all if r["submission"] not in space_filling])

    # D3 surface phase with the corrected statistic
    k = int(dots.sum())
    vals = surface[fp]
    thr = np.partition(vals, -k)[-k]
    top = (surface >= thr) & fp
    top_rows = U.compare_array_to_registry(top.astype(np.float32), index, fp, include_reverse=False)
    informative = [r for r in top_rows["rows"] if "error" not in r and r["submission"] not in space_filling]
    worst_top = max(informative, key=lambda r: r["my_dots_within_3px_of_theirs"])
    d3 = dict(statistic="surface: Spearman (unchanged, all rasters) + top-k support overlap (pre-placement dots)",
              worst_spearman=rep["surface_gate"]["worst_spearman"], worst_spearman_submission=rep["surface_gate"]["worst_spearman_submission"],
              top_k=k, worst_topk_overlap_informative=worst_top["my_dots_within_3px_of_theirs"],
              worst_topk_overlap_submission=worst_top["submission"],
              surface_duplicate_corrected=bool(rep["surface_gate"]["worst_spearman"] > U.RHO_LIMIT
                                               or worst_top["my_dots_within_3px_of_theirs"] > U.OVERLAP_LIMIT))

    # D4 SGMC off-catalogue instrument (truth independent of the catalogue labels and of both models)
    with rasterio.open(R.DATA / "external" / "derived_sgmc_faults_100m_u8.tif") as s:
        sg = s.read(1) > 0
    truth = sg & fp & ~cat & (d_cat > 3)
    fold = dict(region=fp, truth=truth, masked_known=cat, visible=cat)
    terms = {}
    for name, m in (("H42_HWCI_final", dots), ("CHAMPION_0.2778", champ), ("RANDOM_37654", rnd & ~cat)):
        res, t = g57eval.evaluate(m.astype(np.float32), fold, fp, block_side=200, origin=(0, 0), global_shape=fp.shape)
        terms[name] = t
    d4 = g57eval.pooled_summary(terms, draws=1000, seed=520810, candidate="H42_HWCI_final")
    d4["truth_definition"] = "SGMC fault pixels (derived_sgmc_faults_100m_u8) > 3 px from the catalogue; catalogue masked"
    d4["truth_pixels"] = int(truth.sum())

    rep["diagnostics_post_run"] = dict(D1_space_filling=d1, D2_band_matched_null=d2, D3_surface_corrected=d3,
                                       D4_sgmc_off_catalogue=d4)
    rep["deviations"] = rep.get("deviations", []) + [
        "Surface phase: run_h42.py passed the continuous surface to the dot-overlap test, so every footprint pixel "
        "counted as a 'dot'; that statistic is geometrically guaranteed to fire against any <=4-px lattice raster. "
        "Reported as D3 with the corrected statistic. G4 is decided by the FINAL-DOT literal rule, which is unaffected.",
        "Registry scope: 205 unique on-grid rasters from 9 focus repositories at pinned refs (1 off-grid format test "
        "excluded); not every GEMSDOE repository."]
    g4_final_dup = rep["final_gate"]["duplicate"]
    rep["gates"]["G4_lane_unique"] = not g4_final_dup and not d3["surface_duplicate_corrected"]
    rep["verdict"] = "promote" if all(rep["gates"].values()) else "negative"
    rep["ok_to_submit"] = rep["verdict"] == "promote"
    rep["verdict_reasons"] = ([] if rep["ok_to_submit"] else
                              [f"G4 lane gate FAILED on the final dots: {d2['n_fired_excluding_space_filling']} registry "
                               f"rasters beyond the space-filling lattice have > 70 % of H42 dots within 3 px "
                               f"(worst {fired_all[1]['submission'] if len(fired_all) > 1 else fired_all[0]['submission']})"
                               ", i.e. H42's near-network placement zone is already occupied by GEMSDOE25's lane."])
    (ROOT / "evidence/h42_run.json").write_text(json.dumps(rep, indent=1, allow_nan=False, default=float) + "\n")
    receipt = json.loads((ROOT / (rep["file"][:-4] + ".json")).read_text())
    R.write_card(rep, receipt, rep["submission"]["name"], rep["submission"]["note"])
    print(json.dumps(dict(gates=rep["gates"], verdict=rep["verdict"], reasons=rep["verdict_reasons"],
                          D1=list(d1["space_filling_rasters"].items())[:2],
                          D2_head=d2["rows"][:4], D2_counts=(d2["n_fired_total"], d2["n_fired_excluding_space_filling"]),
                          D3={k: v for k, v in d3.items() if k != "statistic"},
                          D4={k: (v["dti"], v["ci95"]) for k, v in d4["scores"].items()},
                          D4_paired={k: (v["delta"], v["ci95"]) for k, v in d4["paired_differences"].items()}),
                     indent=1, default=float))
    return 0


if __name__ == "__main__":
    sys.exit(main())
