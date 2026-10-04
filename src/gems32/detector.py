"""CPU-feasible detectors trained on the visible catalogue.

The sandbox has 2 vCPU / 3 GB RAM, so a U-Net (the official reference solution) is out of reach
here; these are honest baselines for *harness* work, not the proposed final model.  The detector
matters only through the field it produces; the emission rule is validated on that field.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np


@dataclass
class DetectorSpec:
    kind: str = "hgb"          # 'hgb' | 'logistic'
    max_iter: int = 80
    learning_rate: float = 0.1
    max_leaf_nodes: int = 31
    sample_pos: int = 60_000
    sample_neg: int = 240_000
    seed: int = 0

    def as_dict(self):
        return asdict(self)


def sample_training_rows(stack: np.ndarray, labels: np.ndarray, train_mask: np.ndarray,
                         spec: DetectorSpec, rng: np.random.Generator):
    """Sample (X, y) from a *training region only* (blocks are removed by ``train_mask``)."""
    h, w, f = stack.shape
    lab = labels & train_mask
    pos = np.flatnonzero(lab.ravel())
    if pos.size > spec.sample_pos:
        pos = rng.choice(pos, spec.sample_pos, replace=False)
    cand = np.flatnonzero(train_mask.ravel())
    neg_pool = np.setdiff1d(cand, np.flatnonzero(labels.ravel()), assume_unique=False)
    neg = rng.choice(neg_pool, min(spec.sample_neg, neg_pool.size), replace=False)
    idx = np.concatenate([pos, neg])
    y = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
    flat = stack.reshape(-1, f)                      # memmap-friendly: no full materialisation
    X = np.asarray(flat[idx], dtype=np.float32)      # bounded: <= ~40 MB for the default caps
    return X, y


class Detector:
    def __init__(self, spec: DetectorSpec | None = None):
        self.spec = spec or DetectorSpec()
        self.model = None
        self.mu = None
        self.sd = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.mu = X.mean(0)
        self.sd = X.std(0) + 1e-6
        Xs = (X - self.mu) / self.sd
        if self.spec.kind == "hgb":
            from sklearn.ensemble import HistGradientBoostingClassifier
            self.model = HistGradientBoostingClassifier(
                max_iter=self.spec.max_iter, learning_rate=self.spec.learning_rate,
                max_leaf_nodes=self.spec.max_leaf_nodes, early_stopping=False,
                random_state=self.spec.seed)
            self.model.fit(Xs, y)
        else:
            from sklearn.linear_model import LogisticRegression
            self.model = LogisticRegression(max_iter=400, class_weight="balanced")
            self.model.fit(Xs, y)
        return self

    def predict_field(self, stack: np.ndarray, y0: int, y1: int) -> np.ndarray:
        """Probability field for rows [y0, y1) of the stack."""
        block = stack[y0:y1]
        h, w, f = block.shape
        Xs = (np.asarray(block, dtype=np.float32).reshape(-1, f) - self.mu) / self.sd
        p = self.model.predict_proba(Xs)[:, 1].astype(np.float32)
        return p.reshape(h, w)
