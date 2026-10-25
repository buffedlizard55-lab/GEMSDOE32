#!/usr/bin/env python3
"""Build cross-validated 35-channel HGB field (out-of-fold predictions)."""
import sys, json, time, hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
import os
os.environ["GEMS_DATA_DIR"]="/tmp/gems_data"
os.environ["GEMS_WORK_DIR"]="/tmp/gems_work"
from gems32.holdout import load_holdout_context, quadrant_ids
from gems32.detector import Detector, DetectorSpec, sample_training_rows
from gems32.paths import data_dir
from gems32.grid import write_submission, check_submission

ROOT=Path(__file__).resolve().parents[1]
stack_path=Path("/tmp/gems_work/feature_stack.npy")
bands_dir=Path("/tmp/gems_work/bands")
foot=np.load(bands_dir/"_footprint.npy")
labels=np.load(bands_dir/"_labels.npy")
# Load stack memmap
stack=np.lib.format.open_memmap(stack_path, mode="r")
print(f"stack shape {stack.shape}, dtype {stack.dtype}")
# Quadrant IDs
qids=quadrant_ids(foot)
print(f"quadrant counts: {[(qids==i).sum() for i in range(4)]}")
# Prepare field
field=np.full(foot.shape, 0.0, dtype=np.float32)
# Also need to handle buffer: create collar 15px buffer between train/test as in holdout.py
from scipy.ndimage import binary_dilation

for fold in range(4):
    print(f"\n=== Fold {fold} ===")
    # test mask = quadrant == fold, with domain erosion 12px and collar 15px buffer?
    # Simplify: test = (qids==fold) & foot, train = (qids!=fold) & foot
    # Apply collar: dilate test by 15, remove from train
    test_mask = (qids==fold) & foot
    # buffer
    collar = binary_dilation(test_mask, iterations=15)
    train_mask = foot & ~collar & ~test_mask
    # also erode domain boundary? skip
    print(f" test {test_mask.sum()} train {train_mask.sum()} collar {collar.sum()}")
    spec=DetectorSpec(max_iter=80, learning_rate=0.1, max_leaf_nodes=31, sample_pos=60000, sample_neg=240000, seed=fold)
    rng=np.random.default_rng(42+fold)
    X,y=sample_training_rows(stack, labels, train_mask, spec, rng)
    print(f" sampled X {X.shape} y pos {(y==1).sum()} neg {(y==0).sum()}")
    det=Detector(spec)
    det.fit(X,y)
    # Predict test region: need to predict every pixel in test_mask + maybe also buffer? We will predict whole footprint but stitch only test
    # For efficiency, predict in chunks
    H,W=foot.shape
    F=stack.shape[2]
    # Build X_test for test_mask pixels
    flat_stack=stack.reshape(-1,F)
    test_idx=np.flatnonzero(test_mask.reshape(-1))
    # chunked prediction to avoid OOM
    chunk=200000
    probs=[]
    for i in range(0,len(test_idx),chunk):
        idx=test_idx[i:i+chunk]
        Xt=flat_stack[idx]
        Xt=(Xt - det.mu)/det.sd
        p=det.model.predict_proba(Xt)[:,1]
        probs.append(p)
    probs=np.concatenate(probs)
    # assign to field
    yy,xx=np.unravel_index(test_idx, (H,W))
    field[yy,xx]=probs
    # also evaluate AUC on this fold for logging
    from sklearn.metrics import roc_auc_score
    try:
        auc=roc_auc_score(labels[test_mask], field[test_mask])
        print(f" fold {fold} AUC {auc:.4f}")
    except: pass

# After CV, we have field covering all quadrants (foot). Fill any remaining (foot but not in any qids? shouldn't happen)
# Normalize to [0,1] robust?
# field already in [0,1] from predict_proba
# Save field as npy
out_field=Path("/tmp/gems_work/cv_field.npy")
np.save(out_field, field)
print(f"\nSaved CV field to {out_field}, min {field[foot].min():.4f} max {field[foot].max():.4f} mean {field[foot].mean():.4f}")
# Also save full-trained field for comparison (train on all)
print("\n=== Full-trained field (for emission) ===")
spec=DetectorSpec(max_iter=80, learning_rate=0.1, max_leaf_nodes=31, sample_pos=60000, sample_neg=240000, seed=0)
train_mask=foot
rng=np.random.default_rng(0)
X,y=sample_training_rows(stack, labels, train_mask, spec, rng)
det=Detector(spec)
det.fit(X,y)
# Predict whole footprint in chunks
H,W=foot.shape
F=stack.shape[2]
flat_stack=stack.reshape(-1,F)
foot_idx=np.flatnonzero(foot.reshape(-1))
probs_all=[]
for i in range(0,len(foot_idx),chunk):
    idx=foot_idx[i:i+chunk]
    Xt=flat_stack[idx]
    Xt=(Xt - det.mu)/det.sd
    p=det.model.predict_proba(Xt)[:,1]
    probs_all.append(p)
probs_all=np.concatenate(probs_all)
full_field=np.zeros(foot.shape, dtype=np.float32)
yy,xx=np.unravel_index(foot_idx, (H,W))
full_field[yy,xx]=probs_all
np.save("/tmp/gems_work/full_field.npy", full_field)
print(f"Saved full field min {full_field[foot].min():.4f} max {full_field[foot].max():.4f}")
