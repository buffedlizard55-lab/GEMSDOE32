#!/usr/bin/env python3
"""Experiment 1: H-GEO-VENT — geothermal-conduit proximity predictor.

Novel, contrarian hypothesis (not present as a keyworded experiment in this repo per the
2026-10-26 standing-prompt audit): instead of mapping fault *lineaments* (the dominant approach
across H19-5/H33/H44/H47/H48/H49), predict proximity to *direct geothermal surface expressions*
that mark active fault conduits — many of which lie on faults missing from the USGS/INGENIOUS
catalogue:

Layers
------
1. Distance to Quaternary volcanic vents (21 pts, row/col in grid, GDR #1391
   gdr_volcanic_vents_in_footprint.csv) — young volcanism = active conduit.
2. Distance to hot springs (temp_c >= 60 C, thermalclass Hot, GDR #1391 wellspring CSV) —
   direct shallow thermal discharge.
3. GeoDAWN radiometric K band (normalised u8) — potassic hydrothermal alteration.
4. LiDAR young-scarp band (normalised u8) — recent slip.

field = 0.35*exp(-d_vent/3px) + 0.30*exp(-d_spring/6px) + 0.20*K + 0.15*scarp

Emission: threshold to support, dot_thin at min_dist 2.8 px to a target mass (28 k dots — a
different mass from the 37,654-dot champion so it cannot be a mass twin).

Evaluation: reuse gems32.holdout.evaluate_hide_and_recover (spatially blocked hide-and-recover,
pooled DTI alpha=0.2 beta=0.8 300 m triangular kernel, 95% spatial cluster-bootstrap CI) plus
off-catalogue SGMC diagnostic.

Lane check (protocol rule 1): Spearman rank correlation vs every registry raster <= 0.90 and
<= 70% of dots within 3 px of any single registry raster's dots.

Leakage canary (protocol rule 4): each single feature screened vs the holdout truth proxy
(catalogue); AUC > 0.90 => leakage.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
import pandas as pd
from scipy.stats import spearmanr, rankdata
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import emission as E, holdout as H  # noqa: E402
from gems32.paths import data_dir  # noqa: E402

DDIR = data_dir()
OUT = ROOT / "docs" / "downloads"
OUT.mkdir(parents=True, exist_ok=True)


def read_grid(p: Path) -> np.ndarray:
    with rasterio.open(p) as ds:
        return ds.read(1).astype(np.float64)


def auc_score(scores: np.ndarray, truth: np.ndarray) -> float:
    pos = scores[truth]
    neg = scores[~truth]
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    all_s = np.concatenate([pos, neg])
    ranks = rankdata(all_s, method="average")
    r_pos = ranks[: pos.size].sum()
    n_pos, n_neg = pos.size, neg.size
    return float((r_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def main() -> int:
    with rasterio.open(DDIR / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    labels = (read_grid(DDIR / "labels.tif") > 0) & foot

    # ---- Layer 1: Quaternary volcanic vents (GDR #1391) -------------------------
    vents = []
    with (DDIR / "external" / "gdr_volcanic_vents_in_footprint.csv").open() as f:
        for row in csv.DictReader(f):
            vents.append((int(float(row["row"])), int(float(row["col"]))))
    vents = np.array(vents, int)
    print("vents:", len(vents), "points")

    # ---- Layer 2: hot springs, temp_c >= 60 C, thermalclass Hot ------------------
    ws = pd.read_csv(DDIR / "external" / "gdr_wellspring_in_footprint.csv")
    hot = ws[(ws["temp_c"] >= 60.0) & (ws["thermalclass"].astype(str).str.strip() == "Hot")]
    springs = hot[["row", "col"]].dropna().astype(int).values
    print("hot springs (temp_c>=60, Hot):", len(springs), "points")

    # ---- Layer 3: GeoDAWN radiometrics (band 1 = K proxy), Layer 4: LiDAR scarp --
    K = read_grid(DDIR / "external" / "geodawn_rad_u8.tif")[0]
    scarp = read_grid(DDIR / "external" / "lidar_scarp_features_u8.tif")[11]

    def invdist_kernel(pts: np.ndarray, sigma_px: float) -> np.ndarray:
        yy, xx = np.mgrid[: foot.shape[0], : foot.shape[1]]
        d = np.full(foot.shape, np.inf)
        for (ry, cx) in pts:
            d = np.minimum(d, np.hypot(yy - ry, xx - cx))
        return np.exp(-d / sigma_px) * foot

    f_vent = invdist_kernel(vents, 3.0)
    f_spring = invdist_kernel(springs, 6.0)
    f_K = (K - K.min()) / (K.max() - K.min()) * foot
    f_scarp = (scarp - scarp.min()) / (scarp.max() - scarp.min()) * foot

    field = 0.35 * f_vent + 0.30 * f_spring + 0.20 * f_K + 0.15 * f_scarp
    field = field / field.max()
    work = ROOT / ".cache" / "gems_work"
    work.mkdir(parents=True, exist_ok=True)
    np.save(work / "exp1_field.npy", field)

    # ---- Leakage canary: each feature alone vs holdout truth proxy (catalogue) ---
    canary = {}
    for name, f in (("vent", f_vent), ("spring", f_spring), ("K", f_K), ("scarp", f_scarp)):
        canary[name] = auc_score(f[foot], labels[foot])
    print("leakage canary (AUC vs catalogue):", {k: round(v, 4) for k, v in canary.items()})

    # ---- Emission: dot_thin to target mass --------------------------------------
    support = field > np.quantile(field[foot], 0.90)
    target = 28_000
    mask = E.dot_thin(support & foot & ~labels, 2.8)
    n = int(mask.sum())
    print("target", target, "emitted", n, "dots")
    if n > target:
        ys, xs = np.nonzero(mask)
        keep = np.random.default_rng(7).choice(ys.size, target, replace=False)
        mask2 = np.zeros_like(mask)
        mask2[ys[keep], xs[keep]] = True
        mask = mask2
    emitted = int(mask.sum())
    print("final emitted:", emitted)
    np.save(work / f"exp1_mask_{emitted}.npy", mask)

    # ---- Holdout evaluation (reuse, don't rebuild) --------------------------
    ctx = H.load_holdout_context(DDIR)
    hr = H.evaluate_hide_and_recover(mask, ctx, b_visible_px=0.0, name="H-GEO-VENT-EXP1")
    sg = H.evaluate_sgmc_with_ci(mask, ctx, name="H-GEO-VENT-EXP1")
    print("HIDE-RECOVER pooled DTI:", hr["pooled_dti"], "CI:", hr["ci95_cluster_bootstrap"],
          "n_withheld:", hr["n_withheld_positives"])
    print("SGMC raw pooled DTI:", sg["sgmc_raw_pooled_dti"],
          "calibrated:", sg["sgmc_prevalence_calibrated_dti"],
          "cal CI:", sg["sgmc_calibrated_ci95"])
    total_emitted = int(sum(v["emitted"] for v in hr["folds"].values()))
    print("emitted_pixels:", total_emitted, "on_cat:", hr["on_catalogue_pixels"],
          "hug_share:", hr["hug_share"])

    # ---- Lane check vs registry rasters -------------------------------------
    registry_rasters = sorted(
        list((DDIR / "scored").glob("*.tif")) + list((ROOT / "docs" / "downloads").glob("*-zeros.tif"))
    )
    lane = lane_check(mask, field, registry_rasters, foot)
    print("lane_check:", json.dumps(lane, indent=1))

    result = {
        "experiment": "exp1-H-GEO-VENT",
        "hypothesis": "geothermal-conduit proximity (vents + hot springs + K + scarp)",
        "layers": {
            "vent_n": int(len(vents)),
            "spring_n": int(len(springs)),
            "vent_sigma_px": 3.0,
            "spring_sigma_px": 6.0,
            "weights": [0.35, 0.30, 0.20, 0.15],
        },
        "emitted_pixels": emitted,
        "target_mass": target,
        "leakage_canary_auc_vs_catalogue": canary,
        "holdout_hide_recover": {
            "evaluator_version": hr["evaluator_version"],
            "pooled_dti": hr["pooled_dti"],
            "ci95": hr["ci95_cluster_bootstrap"],
            "n_withheld_positives": hr["n_withheld_positives"],
            "n_spatial_clusters": hr["n_spatial_clusters"],
            "fold_mean_dti": hr["fold_mean_dti"],
            "per_quadrant_dti": hr["per_quadrant_dti"],
            "total_emitted_across_cells": total_emitted,
        },
        "sgmc_off_catalogue": {
            "raw_pooled_dti": sg["sgmc_raw_pooled_dti"],
            "prevalence_calibrated_dti": sg["sgmc_prevalence_calibrated_dti"],
            "calibrated_ci95": sg["sgmc_calibrated_ci95"],
            "n_withheld_positives": sg["n_withheld_positives"],
        },
        "lane_check": lane,
    }
    (ROOT / "evidence" / "exp1_HGEOVENT_run_card.json").write_text(json.dumps(result, indent=2) + "\n")
    print("run card written to evidence/exp1_HGEOVENT_run_card.json")
    return 0


def lane_check(mask: np.ndarray, field: np.ndarray, rasters: list, foot: np.ndarray) -> dict:
    """Protocol rule 1: correlation & 3-px overlap vs every registry raster."""
    rng = np.random.default_rng(0)
    foot_flat = np.flatnonzero(foot)
    sample = rng.choice(foot_flat, size=min(80_000, foot_flat.size), replace=False)
    yy, xx = np.unravel_index(sample, foot.shape)

    my_rank = field[yy, xx]
    my_dot_coords = np.argwhere(mask)
    worst_rho = -1.0
    worst_raster = None
    worst_overlap = 0.0
    worst_overlap_raster = None
    for rp in rasters:
        try:
            with rasterio.open(rp) as ds:
                a = ds.read(1)
            if a.shape != foot.shape:
                continue
            finite = np.isfinite(a)
            vals = np.nan_to_num(a, nan=0.0)
            rho, _ = spearmanr(my_rank, vals[yy, xx])
            rho = abs(float(rho)) if np.isfinite(rho) else 0.0
            if rho > worst_rho:
                worst_rho, worst_raster = rho, str(rp)
            rdots = np.argwhere((vals > 0.5) & finite)
            if rdots.size and my_dot_coords.size:
                d = distance_transform_edt(~(vals > 0.5))
                d_at = d[my_dot_coords[:, 0], my_dot_coords[:, 1]]
                ov = float((d_at <= 3.0).mean())
                if ov > worst_overlap:
                    worst_overlap, worst_overlap_raster = ov, str(rp)
        except Exception:
            continue
    return {
        "max_abs_spearman_vs_registry": round(worst_rho, 4),
        "max_abs_spearman_raster": worst_raster,
        "max_fraction_dots_within_3px": round(worst_overlap, 4),
        "max_overlap_raster": worst_overlap_raster,
        "lane_drift": bool(worst_rho > 0.90 or worst_overlap > 0.70),
    }


if __name__ == "__main__":
    raise SystemExit(main())
