#!/usr/bin/env python3
"""H45-1 Kernel-Spacing emission: 3 pre-registered experiments on HIDE-RECOVER-v3.0.

EXP1 KS0-37654 (min-sep 0 control) / EXP2 KS4-20000 / EXP3 KS4-12000, all from the
same fold-local 35ch HistGB OOF surfaces. Then builds the final full-data raster
with the winning config, checks genuine-registry uniqueness, writes + validates it.
"""
from __future__ import annotations
import gc, hashlib, json, sys, time, zipfile
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import features, holdout, spcp  # noqa: E402
from gems32.emission import greedy_cover_fast  # noqa: E402
from gems32.paths import data_dir, downloads_dir, evidence_dir, work_dir  # noqa: E402

CONFIGS = [("EXP1_KS0_37654", 0.0, 37654), ("EXP2_KS4_20000", 4.0, 20000), ("EXP3_KS4_12000", 4.0, 12000)]
B_PX = 2.0

def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def emit(field, elig, budget, min_dist):
    f = np.where(elig, field, 0.0).astype(np.float32)
    dots, _ = greedy_cover_fast(f, elig, max_n=int(budget), min_dist=float(min_dist))
    return dots & elig

def main():
    t0 = time.time()
    ddir, wdir = data_dir(), work_dir()
    stack = np.load(wdir / "feature_stack.npy", mmap_mode="r")
    assert stack.shape[2] == len(features.CHANNELS), stack.shape
    ctx = holdout.load_holdout_context(ddir)
    foot, labels = ctx.foot, ctx.labels
    disk2 = spcp._disk_mask(B_PX)

    # --- Leakage canary: per-channel sampled AUC vs labels (protocol rule 4) ---
    rng = np.random.default_rng(45)
    yy, xx = np.nonzero(foot)
    pick = rng.choice(yy.size, size=min(250_000, yy.size), replace=False)
    ys, xs = yy[pick], xx[pick]
    ytrue = labels[ys, xs].astype(int)
    canary = []
    for i, name in enumerate(features.CHANNELS):
        v = np.asarray(stack[:, :, i], dtype=np.float32)[ys, xs]
        ok = np.isfinite(v)
        auc = roc_auc_score(ytrue[ok], v[ok]) if ok.sum() > 100 else 0.5
        canary.append({"channel": name, "auc": round(float(max(auc, 1 - auc)), 5)})
    worst = max(canary, key=lambda r: r["auc"])
    print(f"canary worst {worst} n={len(canary)}", flush=True)
    if worst["auc"] > 0.90:
        raise SystemExit("LEAKAGE CANARY FAIL")

    fold_train, fold_domain = {}, {}
    for f in holdout.FOLDS:
        q = ctx.quad == f
        collar = binary_dilation(q, structure=np.ones((3, 3), bool), iterations=holdout.COLLAR_PX) & foot
        fold_train[f] = foot & ~collar
        fold_domain[f] = binary_erosion(q, iterations=holdout.DOMAIN_ERODE) & foot

    elig_full = foot & ~binary_dilation(labels, structure=disk2)
    n_elig_full = int(elig_full.sum())

    # --- Fold-local OOF surfaces per cell (computed once, shared by 3 experiments) ---
    cell_prob, cell_elig = {}, {}
    for cell in ctx.cells:
        elig_cell = fold_domain[cell.fold] & ~binary_dilation(cell.visible_full, structure=disk2)
        cell_elig[cell.key] = elig_cell
        prob = spcp.fit_predict_naive_binary(stack, None, fold_train[cell.fold],
                                             cell.visible_full & fold_train[cell.fold],
                                             fold_domain[cell.fold], seed=1000 + cell.seed * 10 + cell.fold)
        cell_prob[cell.key] = prob
        print(f"surface {cell.key} done {time.time()-t0:.0f}s", flush=True)

    results = {}
    cell_masks_by_cfg = {}
    for name, min_dist, budget in CONFIGS:
        cell_masks, full_approx = {}, None
        for cell in ctx.cells:
            b_cell = int(round(budget * (cell_elig[cell.key].sum() / n_elig_full)))
            cell_masks[cell.key] = emit(cell_prob[cell.key], cell_elig[cell.key], b_cell, min_dist)
        hr = holdout.evaluate_hide_and_recover(cell_masks, ctx, b_visible_px=B_PX, name=name)
        hr.pop("_block_totals", None); hr.pop("_boots", None)
        sg = holdout.evaluate_sgmc_with_ci(_union(cell_masks), ctx, name=name)
        sg = {k: v for k, v in sg.items() if not k.startswith("_")}
        results[name] = {"min_dist": min_dist, "budget": budget, "holdout": hr, "sgmc": sg}
        cell_masks_by_cfg[name] = cell_masks
        (wdir / "h45_partial_results.json").write_text(json.dumps(results, indent=1, default=float))
        print(f"{name}: HOLDOUT-DTI={hr['pooled_dti']:.5f} CI={hr.get('ci95_cluster_bootstrap')} SGMC={ {k: sg[k] for k in list(sg)[:12]} }", flush=True)
        gc.collect()

    winner = max(results, key=lambda k: results[k]["holdout"]["pooled_dti"])
    w_min, w_bud = results[winner]["min_dist"], results[winner]["budget"]
    print(f"WINNER {winner}", flush=True)

    # --- Final full-data model + emission with winning config ---
    prob_full = spcp.fit_predict_naive_binary(stack, None, foot, labels, foot, seed=4500)
    np.save(wdir / "h45_oof_prob_full.npy", prob_full)
    dots = emit(prob_full, elig_full, w_bud, w_min)
    print(f"final dots={int(dots.sum())}", flush=True)

    # --- Uniqueness vs focus registry (324 rasters) ---
    uniq = check_uniqueness(prob_full, dots, foot, ddir)
    print(json.dumps(uniq["summary"], indent=1), flush=True)

    # --- Write submission (zeros outside footprint, values {0,1}) ---
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    h8 = hashlib.sha256(dots.tobytes()).hexdigest()[:8]
    base = f"gemsdoe32-h45-kernelspacing-{int(dots.sum())}dots-{stamp}-{h8}"
    out = downloads_dir() / f"{base}-zeros.tif"
    arr = np.where(foot, dots.astype(np.float32), 0.0).astype(np.float32)
    with rasterio.open(ddir / "sample_submission.tif") as ds:
        prof = ds.profile.copy()
    prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(out, "w", **prof) as ds:
        ds.write(arr, 1)
    with zipfile.ZipFile(downloads_dir() / f"{base}-zeros.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out, arcname=out.name)

    card = {
        "schema_version": "gems-parallel-runcard-v3", "candidate_id": "H45-1-KS",
        "hypothesis": "Dots closer than the 300m DTI kernel radius redundantly cover the same hidden-truth pixels; hard >=4px separation + reduced budget raises credit/dot.",
        "mechanism": f"35ch fold-local HistGB OOF surface -> greedy 300m coverage packing min_dist={w_min}px budget={w_bud} -> B=2 catalogue exclusion -> binary {{0,1}} GeoTIFF",
        "named_non_fault_mimic": "Broad smooth probability blobs over pluton margins/caldera rings: spacing would merely spread false positives thinner (holdout decides).",
        "experiments": results, "winner": winner, "canary": {"n": len(canary), "worst": worst, "passed": True},
        "uniqueness": uniq, "final": {"file": out.name, "dots": int(dots.sum()), "sha256": sha256(out),
                                      "on_catalogue": int((dots & labels).sum())},
        "runtime_seconds": round(time.time() - t0, 1),
    }
    (evidence_dir() / "h45_kernel_spacing_run_card.json").write_text(json.dumps(card, indent=1, default=float))
    (downloads_dir() / f"{base}-audit.json").write_text(json.dumps(card, indent=1, default=float))
    print(json.dumps({"winner": winner, "file": out.name, "sha256": card["final"]["sha256"], "dots": int(dots.sum())}, indent=1))
    return 0

def _union(cell_masks):
    out = None
    for m in cell_masks.values():
        out = m.copy() if out is None else (out | m)
    return out

def check_uniqueness(surface, dots, foot, ddir):
    man = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    rng = np.random.default_rng(7)
    yy, xx = np.nonzero(foot)
    pick = rng.choice(yy.size, size=200_000, replace=False)
    ys, xs = yy[pick], xx[pick]
    surf_s = np.asarray(surface, dtype=np.float64)[ys, xs]
    rows, non_genuine = [], []
    dy, dx = np.nonzero(dots)
    for r in man["rasters"]:
        p = ROOT / r["local"]
        if not p.exists():
            continue
        try:
            with rasterio.open(p) as ds:
                a = ds.read(1)
        except Exception:
            continue
        if a.shape != foot.shape:
            continue
        other = np.isfinite(a) & (a > 0)
        n_other = int(other.sum())
        name = Path(r["path"]).name
        is_control = any(t in name.lower() for t in ("lattice", "probe", "placeholder", "null", "anchor-identical"))
        if n_other == 0:
            continue
        rho = float(spearmanr(surf_s, np.asarray(a, dtype=np.float64)[ys, xs]).statistic) if not is_control else 0.0
        if len(dy):
            dist = distance_transform_edt(~other)
            within3 = float((dist[dy, dx] <= 3.0).mean())
        else:
            within3 = 0.0
        row = {"repo": r["repo"], "name": name, "dots": n_other, "surface_spearman_sampled": round(rho, 4),
               "frac_my_dots_within3px": round(within3, 4)}
        (non_genuine if is_control else rows).append(row)
    if rows:
        w_rho = max(rows, key=lambda r: abs(r["surface_spearman_sampled"]))
        w_ov = max(rows, key=lambda r: r["frac_my_dots_within3px"])
        summary = {"n_genuine_compared": len(rows), "max_abs_spearman": w_rho, "max_within3px": w_ov,
                   "passed": bool(abs(w_rho["surface_spearman_sampled"]) <= 0.90 and w_ov["frac_my_dots_within3px"] <= 0.70)}
    else:
        summary = {"n_genuine_compared": 0, "passed": False}
    return {"summary": summary, "top_overlap": sorted(rows, key=lambda r: -r["frac_my_dots_within3px"])[:8],
            "top_spearman": sorted(rows, key=lambda r: -abs(r["surface_spearman_sampled"]))[:8],
            "control_or_lattice_flagged_not_genuine": non_genuine}

if __name__ == "__main__":
    raise SystemExit(main())
