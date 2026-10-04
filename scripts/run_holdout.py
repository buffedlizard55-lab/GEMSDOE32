#!/usr/bin/env python3
"""Preregistered spatially blocked hide-and-recover run of the emission-arm ladder."""
import argparse, json, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import grid, holdout, detector  # noqa: E402

PREREG = dict(
    id="GEMSDOE32-PREREG-1",
    date="2026-10-04",
    harness="4 quadrant blocks x 1 draw; buffer 30 px removed from training around each block",
    detector="HistGradientBoostingClassifier(max_iter=80, lr=0.1, leaves=31), 60k positives / 240k negatives sampled from the training region only",
    budget_px_per_block=8000,
    prior_dti_for_bar=0.13,
    rho_discovery=1.0,
    primary_contrast="A1/A2 greedy cover vs A0 dot_thin at MATCHED emitted count (paired per fold; pass = mean>0 and >=3/4 folds positive)",
    secondary_contrasts=["A3_greedy_bar_discovery vs A2_greedy_credit_bar", "A5_nms_ridge_matched vs A0_dot_thin_matched"],
    proxy="the visible catalogue (USGS/INGENIOUS) inside the hidden block; NOT the hidden new-fault labels",
    note="no weekly submission slot is spent on the strength of this proxy alone",
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stack", default="/tmp/gems32/work/feature_stack.npy")
    ap.add_argument("--labels", default="/tmp/gems32/data/labels.tif")
    ap.add_argument("--features", default="/tmp/gems32/data/training_features.tif")
    ap.add_argument("--out", default="evidence/holdout_run1.json")
    ap.add_argument("--budget", type=int, default=8000)
    ap.add_argument("--buffer", type=int, default=30)
    ap.add_argument("--prior-dti", type=float, default=0.13)
    ap.add_argument("--rho", type=float, default=1.0)
    ap.add_argument("--limit-folds", type=int, default=0)
    a = ap.parse_args()

    PREREG["budget_px_per_block"] = a.budget
    PREREG["prior_dti_for_bar"] = a.prior_dti
    (ROOT / "registry").mkdir(exist_ok=True)
    (ROOT / "registry" / "preregistration.json").write_text(json.dumps(PREREG, indent=1) + "\n")

    stack = np.load(a.stack, mmap_mode="r")
    labels = grid.read_labels(a.labels)
    footprint = grid.read_footprint(a.features)
    blocks = holdout.quadrant_blocks(labels.shape)
    if a.limit_folds:
        blocks = blocks[:a.limit_folds]

    results = []
    t0 = time.time()
    for k, block in enumerate(blocks):
        y0, y1, x0, x1 = block
        train_mask = holdout.block_train_mask(labels.shape, block, a.buffer)
        rng = np.random.default_rng(1000 + k)
        spec = detector.DetectorSpec(seed=k)
        X, y = detector.sample_training_rows(stack, labels, train_mask, spec, rng)
        det = detector.Detector(spec).fit(X, y)
        field = det.predict_field(stack, y0, y1)[:, x0:x1]   # block columns only
        truth = labels[y0:y1, x0:x1]
        fp = footprint[y0:y1, x0:x1]
        from sklearn.metrics import roc_auc_score
        auc = roc_auc_score(truth[fp].astype(int), field[fp]) if truth[fp].any() else float("nan")
        res = holdout.run_fold(field, truth, fp, a.budget, a.prior_dti, a.rho, rng, seed=k)
        res.update(block=[int(y0), int(y1), int(x0), int(x1)], auc=float(auc),
                   n_pos_train=int((labels & train_mask).sum()), n_pos_test=int(truth.sum()),
                   field_mean=float(field[fp].mean()), seconds=round(time.time() - t0, 1))
        results.append(res)
        print(f"fold {k} block={block} auc={auc:.4f} pos_test={int(truth.sum())} "
              + " ".join(f"{x['name'].split('_')[0]}={x['dti']:.4f}" for x in res["arms"]), flush=True)

    summary = summarize(results)
    out = dict(preregistration=PREREG, folds=results, summary=summary,
               seconds=round(time.time() - t0, 1))
    p = ROOT / a.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    print(json.dumps(summary, indent=1))


def summarize(folds):
    names = [x["name"] for x in folds[0]["arms"]]
    by = {n: [f["arms"][i]["dti"] for f in folds for i, a in enumerate(f["arms"]) if a["name"] == n] for n in names}
    mean = {n: float(np.mean(v)) for n, v in by.items()}
    out = {"arms_mean": mean, "arms_mean_n_px": {n: float(np.mean([f["arms"][i]["n_px"] for f in folds for i, a in enumerate(f["arms"]) if a["name"] == n])) for n in names}}
    for name, (a, b) in {"primary_A2_minus_A0": ("A2_greedy_credit_bar", "A0_dot_thin_2p8_topk"),
                         "secondary_A1_minus_A0": ("A1_greedy_fixed_budget", "A0_dot_thin_2p8_topk"),
                         "secondary_A3_minus_A2": ("A3_greedy_bar_discovery", "A2_greedy_credit_bar")}.items():
        d = []
        for f in folds:
            m = {x["name"]: x["dti"] for x in f["arms"]}
            if a in m and b in m:
                d.append(m[a] - m[b])
        out[name] = {"mean": float(np.mean(d)), "folds_positive": int(np.sum(np.array(d) > 0)), "n_folds": len(d), "per_fold": d}
    return out


if __name__ == "__main__":
    main()
