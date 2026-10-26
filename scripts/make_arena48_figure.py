#!/usr/bin/env python3
"""ARENA48 4-panel diagnostic figure (downsampled for the site; evidence is the TIF/JSON)."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import rasterio  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32.paths import data_dir, work_dir  # noqa: E402

F = 4  # block factor


def block(a, how="mean"):
    h, w = a.shape
    hh, ww = h // F, w // F
    b = a[:hh * F, :ww * F].reshape(hh, F, ww, F)
    return b.max(axis=(1, 3)) if how == "max" else b.mean(axis=(1, 3))


def main() -> int:
    ddir, wdir = data_dir(), work_dir()
    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ddir / "labels.tif") as ds:
        labels = (ds.read(1) > 0) & foot
    jx = np.lib.format.open_memmap(wdir / "jxstep7.npy", mode="r")
    conc = np.asarray(jx[:, :, 5], np.float32)
    exp2 = np.load(wdir / "a48_exp2_field.npy")
    final = np.load(wdir / "a48_best_mask.npy")
    with rasterio.open(ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif") as ds:
        champ = (ds.read(1) > 0) & foot

    foot_b = block(foot.astype(np.float32), "max") > 0
    def prep(a, how="mean", p=99.5):
        b = block(np.asarray(a, np.float32), how)
        hi = np.percentile(b[foot_b], p) if foot_b.any() else 1.0
        out = np.clip(b / max(float(hi), 1e-9), 0, 1)
        out[~foot_b] = np.nan
        return out

    both = block((final & champ).astype(np.float32), "max")
    only_new = block((final & ~champ).astype(np.float32), "max")
    only_ch = block((champ & ~final).astype(np.float32), "max")
    rgb = np.dstack([only_ch, only_new, both]).astype(np.float32)
    rgb[~foot_b] = 1.0

    fig, axes = plt.subplots(2, 2, figsize=(11, 12))
    panels = [
        (prep(conc), "A  jx_concordant (label-free juxtaposition step)", "viridis"),
        (prep(exp2), "B  EXP2 OOF field (35ch + JX7 HistGB)", "viridis"),
        (prep(final.astype(np.float32), "max", 100), "C  ARENA48 final dots (37,654, EXP3)", "gray_r"),
        (None, "D  vs champion: green=new-only, red=champion-only, blue=both (4px blocks)", None),
    ]
    for ax, (img, title, cmap) in zip(axes.ravel(), panels):
        if img is None:
            ax.imshow(rgb, interpolation="nearest")
        else:
            ax.imshow(img, cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
        ax.set_title(title, fontsize=10)
        ax.set_xticks([]); ax.set_yticks([])
    fig.suptitle("ARENA48 A48-H1-JXSTEP — verdict negative (DO NOT SUBMIT): "
                 "HOLDOUT-DTI 0.1063 < H38 0.1170; SGMC 0.0614 < champion 0.0641", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = ROOT / "docs/assets/fig_arena48_jxstep.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    print(out, out.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
