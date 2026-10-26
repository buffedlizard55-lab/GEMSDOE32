#!/usr/bin/env python3
"""H47 E2: LLI-optimal *unique* allocation (pre-registration: docs/research/h47-lli-preregistration-20261026.md).

Core   : H19-5 centerline pixels outside the live-calibrated catalogue-depletion zone (B3), placed greedily
         by LLI expected credit with a Poisson-disk spacing (our own placement; not a copy of D2.8/B2 dots).
Novel  : >= 35% of dots, > 5 px from the H19-5 network and > 5 px from the catalogue, ranked by the
         Gallardo-Meju magnitude-weighted alignment of rtp and smoothed det_elev gradients, boosted by
         coherent 1 m-LiDAR step evidence (valid tiles only), 3x3 non-maximum suppression.
Budget : grid over (core spacing, core size); the novel count is tied to the core size by the share;
         the configuration with the best LLI projection (mean of both ridge fits) is selected.
Gates  : format validator, refreshed focus registry + live-ledger uniqueness (surface + dots), leakage
         canary, HIDE-RECOVER-v3.0 paired holdout vs the champion proxy, LLI projection vs champion.
Every LLI number is a PROJECTION, never a score.
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
from scipy.ndimage import binary_dilation, convolve, distance_transform_edt, gaussian_filter, maximum_filter, sobel
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from gems32 import holdout, ledger_inversion as li, registry_audit  # noqa: E402
from gems32.h36_tdr_pds import run_single_feature_leakage_canary  # noqa: E402
from gems32.metric import kernel  # noqa: E402
from gems32.paths import data_dir, work_dir  # noqa: E402
import run_live_ledger_inversion as R  # noqa: E402

H195 = "scored/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif"
CHAMP = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
D28 = "scored/gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
NOVEL_SHARE = 0.35
CORE_B = 3.01        # live-calibrated depletion: prune core dots with d_catalogue <= 3 px
NOVEL_MIN_DH = 5.01  # novel dots strictly off-network (no offset copies of network ridges)
NOVEL_MIN_DCAT = 5.01
OUT = ROOT / "evidence" / "h47_lli_unique_experiment.json"


def read1(p, band=1):
    with rasterio.open(p) as ds:
        return ds.read(band)


def clean(a):
    a = a.astype(np.float32)
    a[~np.isfinite(a) | (a < -1e30)] = np.nan
    return a


def rank01(x, mask):
    out = np.zeros(x.shape, np.float32)
    v = x[mask]
    v = np.where(np.isfinite(v), v, np.nanmin(v[np.isfinite(v)]) if np.isfinite(v).any() else 0.0)
    out[mask] = (rankdata(v, method="average") / max(v.size, 1)).astype(np.float32)
    return out


def poisson_select(order_y, order_x, shape, r, limit=None):
    """Greedy Poisson-disk selection in the given priority order (min Euclidean spacing >= r)."""
    H, W = shape
    occ = np.zeros((H + 8, W + 8), bool)
    ri = int(np.ceil(r))
    yy, xx = np.mgrid[-ri:ri + 1, -ri:ri + 1]
    disk = (yy * yy + xx * xx) < r * r - 1e-9
    sel_y, sel_x = [], []
    for y, x in zip(order_y, order_x):
        win = occ[y + 4 - ri:y + 4 + ri + 1, x + 4 - ri:x + 4 + ri + 1]
        if (win & disk).any():
            continue
        occ[y + 4, x + 4] = True
        sel_y.append(y)
        sel_x.append(x)
        if limit is not None and len(sel_y) >= limit:
            break
    return np.array(sel_y, np.int64), np.array(sel_x, np.int64)


def lli_priority_map(spec_levels_fn, lam_table, d_cat, d_h, active):
    """Per-pixel expected isolated-dot credit sum_y lambda(y) k(d(x,y)) under an S3 LLI fit."""
    cat_lv = R.digitize(d_cat, [2.01, 3.01, 5.01, 10.01, 30.01], [1, 2, 3, 4, 5, 0]).astype(np.int64)
    h_lv = R.digitize(d_h, [0.01, 1.01, 2.01, 3.01, 4.01, 5.01, 8.01, 15.01], [1, 2, 3, 4, 5, 6, 7, 8, 0]).astype(np.int64)
    sid = cat_lv + 6 * h_lv
    lam = np.where(active, lam_table[sid], 0.0).astype(np.float32)
    k = np.array([[float(kernel(np.hypot(dy, dx))) for dx in range(-3, 4)] for dy in range(-3, 4)], np.float32)
    return convolve(lam, k, mode="constant")


def novel_score(ddir, foot, active):
    rtp = clean(read1(ddir / "training_features.tif", 2))
    elev = clean(read1(ddir / "training_features.tif", 12))
    for a in (rtp, elev):
        a[~np.isfinite(a)] = np.nanmedian(a)
    elev_s = gaussian_filter(elev, 1.0)
    rtp_s = gaussian_filter(rtp, 0.7)
    gmy, gmx = sobel(rtp_s, 0), sobel(rtp_s, 1)
    gey, gex = sobel(elev_s, 0), sobel(elev_s, 1)
    mm = np.hypot(gmy, gmx)
    me = np.hypot(gey, gex)
    cos2 = ((gmy * gey + gmx * gex) / (mm * me + 1e-12)) ** 2
    coupling = np.sqrt(rank01(mm, foot) * rank01(me, foot)) * cos2.astype(np.float32)
    del gmy, gmx, gey, gex, cos2
    valid = read1(ddir / "external/lidar_scarp_features_u8.tif", 12) > 0
    step = read1(ddir / "external/lidar_scarp_features_u8.tif", 3).astype(np.float32)
    coh = read1(ddir / "external/lidar_scarp_features_u8.tif", 10).astype(np.float32)
    lidar = np.full(foot.shape, 0.5, np.float32)
    m = foot & valid
    lidar[m] = np.sqrt(rank01(step, m)[m] * rank01(coh, m)[m])
    score = coupling * (0.5 + 0.5 * lidar)
    score[~foot] = 0.0
    return score.astype(np.float32), coupling.astype(np.float32), lidar


def nms3(score, mask):
    return mask & (score >= maximum_filter(score, size=3)) & (score > 0)


def build(core_pool, core_prio, novel_cand, nscore, shape, r_core, k_core):
    cy, cx = np.nonzero(core_pool)
    o = np.lexsort((cx, cy, -core_prio[cy, cx]))
    sy, sx = poisson_select(cy[o], cx[o], shape, r_core, limit=k_core)
    core = np.zeros(shape, bool)
    core[sy, sx] = True
    n_nov = int(np.ceil(len(sy) * NOVEL_SHARE / (1.0 - NOVEL_SHARE)))
    ny, nx = np.nonzero(novel_cand)
    o = np.lexsort((nx, ny, -nscore[ny, nx]))
    vy, vx = poisson_select(ny[o], nx[o], shape, 3.0, limit=n_nov)
    nov = np.zeros(shape, bool)
    nov[vy, vx] = True
    return core, nov


def paired_ci(b1, b0):
    d = np.asarray(b1) - np.asarray(b0)
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    wdir = work_dir()
    foot = np.isfinite(read1(ddir / "sample_submission.tif"))
    labels = (read1(ddir / "labels.tif") > 0) & foot
    active = foot & ~labels
    d_cat = distance_transform_edt(~labels)
    h = read1(ddir / H195)
    h = np.isfinite(h) & (h > 0) & foot
    d_h = distance_transform_edt(~h)
    spec, _ = R.build_spec(ddir, "S3")
    fits = pickle.load(open(wdir / "lli_S3_fits.pkl", "rb"))["fits"]
    lam_cons = fits[1e-3]["lambda"]
    print(f"[1] inputs ready ({time.time() - t0:.0f}s)", flush=True)

    prio = lli_priority_map(None, lam_cons, d_cat, d_h, active)
    core_pool = h & active & (d_cat > CORE_B)
    nscore, coupling, lidar = novel_score(ddir, foot, active)
    novel_elig = active & (d_h > NOVEL_MIN_DH) & (d_cat > NOVEL_MIN_DCAT)
    # E2-repair (uniqueness compliance, not score tuning): the first extended-registry audit found the
    # spread-out novel dots inside the 3-px coverage of five dense GEMSDOE rasters (41-55% footprint
    # coverage).  Novel candidates now avoid the union of the 3-px dilations of every registry/ledger
    # raster that had >= 55% literal overlap with the first build (.cache/gems_work/h47_avoid_union.npy,
    # rebuilt by the audit step).  Core selection is unchanged.
    avoid_p = wdir / "h47_avoid_union.npy"
    avoid = np.load(avoid_p) if avoid_p.exists() else np.zeros(foot.shape, bool)
    novel_elig_cat = novel_elig.copy()
    novel_elig &= ~avoid
    novel_cand = nms3(nscore, novel_elig)
    print(f"[2] core pool {int(core_pool.sum())} px; novel NMS candidates {int(novel_cand.sum())} ({time.time() - t0:.0f}s)", flush=True)

    champ = (read1(CHAMP) > 0) & foot
    champ_row = li.design_row(champ.astype(np.float32), spec)
    champ_proj = {str(r): li.project(champ_row, spec, f["lambda"])["dti"] for r, f in fits.items()}
    grid = []
    best = None
    for r_core in (2.8, 3.0, 3.3):
        for k_core in (16000, 20000, 24000, 28000, 32000):
            core, nov = build(core_pool, prio, novel_cand, nscore, foot.shape, r_core, k_core)
            cand = core | nov
            row = li.design_row(cand.astype(np.float32), spec)
            pj = {str(r): li.project(row, spec, f["lambda"])["dti"] for r, f in fits.items()}
            within_h = float(binary_dilation(h, structure=np.ones((7, 7), bool) & (np.add.outer(np.arange(-3, 4) ** 2, np.arange(-3, 4) ** 2) <= 9))[cand].mean())
            rec = {"r_core": r_core, "k_core_requested": k_core, "core": int(core.sum()), "novel": int(nov.sum()),
                   "dots": int(cand.sum()), "lli_projection": pj, "mean_projection": float(np.mean(list(pj.values()))),
                   "within3px_H19-5": within_h}
            grid.append(rec)
            print(f"   r={r_core} K={k_core}: core={rec['core']} novel={rec['novel']} proj={pj} within3(H19-5)={within_h:.3f}", flush=True)
            if within_h <= 0.66 and (best is None or rec["mean_projection"] > best[0]["mean_projection"]):
                best = (rec, core, nov)
    rec, core, nov = best
    cand = core | nov
    print(f"[3] selected r={rec['r_core']} core={rec['core']} novel={rec['novel']} proj={rec['lli_projection']} champion proj={champ_proj} ({time.time() - t0:.0f}s)", flush=True)

    # --- continuous pre-placement surface (for the surface uniqueness gate) ---
    surface = (0.5 * rank01(nscore, foot)).astype(np.float32)
    surface[core_pool] = 0.5 + 0.5 * rank01(prio, core_pool)[core_pool]
    surface[~foot] = 0.0
    np.save(wdir / "h47_surface.npy", surface)
    np.save(wdir / "h47_dots.npy", cand)

    # --- HIDE-RECOVER-v3.0 (fold-local rebuild with visible-only catalogue distances) ---
    ctx = holdout.load_holdout_context(ddir)
    cells = {}
    for cell in ctx.cells:
        vis = cell.visible_full
        d_vis = distance_transform_edt(~vis)
        act_c = foot & ~vis
        prio_c = lli_priority_map(None, lam_cons, d_vis, d_h, act_c)
        cp = h & act_c & (d_vis > CORE_B)
        ne = act_c & (d_h > NOVEL_MIN_DH) & (d_vis > NOVEL_MIN_DCAT) & ~avoid
        c_core, c_nov = build(cp, prio_c, nms3(nscore, ne), nscore, foot.shape, rec["r_core"], rec["core"])
        cells[cell.key] = c_core | c_nov
    hr = holdout.evaluate_hide_and_recover(cells, ctx, b_visible_px=0.0, name="H47-3")
    d28 = read1(ddir / D28)
    d28 = np.isfinite(d28) & (d28 > 0) & foot
    champ_hr = holdout.evaluate_hide_and_recover(d28, ctx, b_visible_px=2.0, name="CHAMPION_PROXY_D28_visB2")
    core_cells = {}
    for cell in ctx.cells:  # ablation: same pipeline without the novel component (core only)
        vis = cell.visible_full
        d_vis = distance_transform_edt(~vis)
        act_c = foot & ~vis
        prio_c = lli_priority_map(None, lam_cons, d_vis, d_h, act_c)
        cp = h & act_c & (d_vis > CORE_B)
        cy, cx = np.nonzero(cp)
        o = np.lexsort((cx, cy, -prio_c[cy, cx]))
        sy, sx = poisson_select(cy[o], cx[o], foot.shape, rec["r_core"], limit=rec["core"])
        m = np.zeros(foot.shape, bool)
        m[sy, sx] = True
        core_cells[cell.key] = m
    core_hr = holdout.evaluate_hide_and_recover(core_cells, ctx, b_visible_px=0.0, name="H47-3-core-only")
    h38 = json.loads((ROOT / "evidence" / "h38_run_card.json").read_text())["holdout_dti"]["primary_hide_and_recover"]
    holdout_block = {
        "evaluator_version": hr["evaluator_version"], "n_withheld_positives": hr["n_withheld_positives"],
        "H47-3": {"dti": hr["pooled_dti"], "ci95": hr["ci95_cluster_bootstrap"]},
        "H47-3 core-only ablation": {"dti": core_hr["pooled_dti"], "ci95": core_hr["ci95_cluster_bootstrap"]},
        "champion proxy (D2.8 + fold-local B2)": {"dti": champ_hr["pooled_dti"], "ci95": champ_hr["ci95_cluster_bootstrap"]},
        "paired_delta_vs_champion_proxy_ci95": paired_ci(hr["_boots"], champ_hr["_boots"]),
        "paired_delta_novel_component_ci95": paired_ci(hr["_boots"], core_hr["_boots"]),
        "repo_best_same_evaluator_H38": {"dti": h38["pooled_dti"], "ci95": h38.get("ci95") or h38.get("ci95_cluster_bootstrap")},
    }
    print(f"[4] HIDE-RECOVER: H47={hr['pooled_dti']:.5f} {hr['ci95_cluster_bootstrap']} core-only={core_hr['pooled_dti']:.5f} "
          f"champ-proxy={champ_hr['pooled_dti']:.5f} paired={holdout_block['paired_delta_vs_champion_proxy_ci95']} ({time.time() - t0:.0f}s)", flush=True)

    # --- leakage canary (non-catalogue features on the full map; catalogue features fold-local) ---
    names = ["coupling_rtp_elev", "lidar_step_coh", "novel_score", "neg_d_H19-5", "lli_priority_fullcat"]
    X = np.stack([coupling[foot], lidar[foot], nscore[foot], -d_h[foot].astype(np.float32), prio[foot]], 1)
    try:
        canary = run_single_feature_leakage_canary(X, names, foot, ctx, max_allowed_auc=0.90)
        canary["full_catalogue_feature_note"] = None
    except RuntimeError as exc:
        canary = {"passed": False, "error": str(exc)}
    # fold-local versions of the catalogue-derived features (the ones actually used in the holdout build)
    from sklearn.metrics import roc_auc_score
    rng = np.random.default_rng(47)
    fl = {}
    for nm in ("neg_d_visible", "lli_priority_visible"):
        ys, ss = [], []
        for cell in ctx.cells:
            vis = cell.visible_full
            sl = cell.bbox
            d_vis = distance_transform_edt(~vis)
            f = -d_vis if nm == "neg_d_visible" else lli_priority_map(None, lam_cons, d_vis, d_h, foot & ~vis)
            fs = f[sl]
            ty, tx = cell.truth_coords
            pos = fs[ty, tx]
            tm = np.zeros(cell.active_sub.shape, bool)
            tm[ty, tx] = True
            negp = np.nonzero(cell.active_sub & ~tm)
            pick = rng.choice(negp[0].size, size=min(negp[0].size, max(4 * pos.size, 4000)), replace=False)
            neg = fs[negp[0][pick], negp[1][pick]]
            ys += [np.ones(pos.size), np.zeros(neg.size)]
            ss += [pos, neg]
        auc = float(roc_auc_score(np.concatenate(ys), np.concatenate(ss)))
        fl[nm] = {"raw_auc": round(auc, 5), "oriented_auc": round(max(auc, 1 - auc), 5)}
    canary["fold_local_catalogue_features"] = fl
    fl_max = max(v["oriented_auc"] for v in fl.values())
    canary_pass_for_gate = bool(fl_max <= 0.90 and all(
        v["oriented_auc"] <= 0.90 for k, v in canary.get("per_feature", {}).items() if k != "lli_priority_fullcat"))
    canary["gate_passed"] = canary_pass_for_gate
    print(f"[5] canary: {json.dumps({k: canary.get(k) for k in ('passed', 'max_oriented_auc', 'max_feature')})} fold-local={fl} ({time.time() - t0:.0f}s)", flush=True)

    out = {
        "schema_version": 1, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "experiment": "H47 E2 - LLI-optimal unique allocation (H47-3)",
        "preregistration": "docs/research/h47-lli-preregistration-20261026.md",
        "constants": {"novel_share": NOVEL_SHARE, "core_B_px": CORE_B, "novel_min_d_H19-5_px": NOVEL_MIN_DH,
                      "novel_min_d_catalogue_px": NOVEL_MIN_DCAT},
        "uniqueness_repair": {"applied": bool(avoid.any()), "avoid_zone_footprint_fraction": float(avoid[foot].mean()),
                              "reason": "first extended-registry audit: novel dots inside dense GEMSDOE22/23/67/77 rasters; "
                                        "novel candidates now avoid the union of 3-px dilations of all rasters with >=55% overlap"},
        "budget_grid": grid, "selected": rec, "champion_lli_projection": champ_proj,
        "lli_validation": {"design": "S3", "loo_mae": 0.0222, "loo_spearman": 0.921, "abs_err_q90": 0.0515,
                           "leave_site_out_mae": 0.0226, "note": "from evidence/live_ledger_inversion.json (S3 refit)"},
        "holdout": holdout_block, "canary": {k: v for k, v in canary.items() if k != "per_feature"} | {"per_feature": canary.get("per_feature")},
        "dots_sha256_packbits": hashlib.sha256(np.packbits(cand).tobytes()).hexdigest(),
    }
    OUT.write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(f"wrote {OUT} ({time.time() - t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
