"""ARENA-EULER lane: windowed 3-D Euler deconvolution contact channels.

Solves Reid et al. (1990) Euler homogeneity equation in 9x9 windows

    Tx*x0 + Ty*y0 + Tz*z0 + N*B = Tx*x + Ty*y + N*T      (observation plane z=0)

for source position (x0, y0, z0) and regional B, with structural index N=0.25
(fault-contact).  Vertical derivative Tz is the exact spectral derivative
|k|*T_hat (Blakely 1995).  Normal equations are accumulated with box filters
and solved in row chunks (bounded memory).  All channels are label-free:
no catalogue raster is read here.

Channels (float32, 0 outside footprint):
  0 euler_rtp_z        clipped source depth z0(RTP)/3500
  1 euler_rtp_good     low-residual, in-depth-window solution density (smoothed)
  2 euler_grav_z       clipped source depth z0(gravity)/3500
  3 euler_grav_good    same for gravity
  4 euler_z_concord    exp(-|z_rtp - z_grav|/1000 m) gated by both-good
  5 euler_joint        sqrt(good_rtp * good_grav) (joint contact density)
  6 euler_base_concord exp(-|z_joint - depth_to_base_surf|/800 m) gated by joint
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.fft import irfft2, rfft2

N_STRUCT = 0.25
WIN = 9
Z_MIN_M, Z_MAX_M = 300.0, 3500.0
CHANNELS = ("euler_rtp_z", "euler_rtp_good", "euler_grav_z", "euler_grav_good",
            "euler_z_concord", "euler_joint", "euler_base_concord")
DX_M = 100.0


def _fill(field: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = field.astype(np.float32, copy=True)
    if (~valid).any():
        _, idx = ndimage.distance_transform_edt(~valid, return_distances=True, return_indices=True)
        out[~valid] = out[idx[0][~valid], idx[1][~valid]]
    return out


def _derivatives(field: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(Tx, Ty, Tz): horizontal central differences + spectral vertical derivative."""
    f = field.astype(np.float64)
    ty, tx = np.gradient(f)  # per-pixel (100 m) units; scale cancels in Euler ratio except z0
    spec = rfft2(f)
    ky = np.fft.fftfreq(f.shape[0])[:, None]
    kx = np.fft.rfftfreq(f.shape[1])[None, :]
    k = 2.0 * np.pi * np.hypot(ky, kx)  # cycles/pixel -> rad/pixel; Tz in per-pixel units
    tz = irfft2(spec * k, s=f.shape)
    return tx.astype(np.float32), ty.astype(np.float32), tz.astype(np.float32)


def _box_sum(a: np.ndarray) -> np.ndarray:
    return ndimage.uniform_filter(a, size=WIN, mode="nearest") * float(WIN * WIN)


def euler_solve(field: np.ndarray, foot: np.ndarray) -> dict[str, np.ndarray]:
    """Return z0_m, resid (relative RMS), offset_px for one potential field.

    Memory-bounded: derivatives are float32 full grids; the 9x9 normal-equation
    sums and the 4x4 solve run in 256-row strips so peak RSS stays <1 GB on
    the 3730x3292 grid (the naive float64 full-grid version OOMs, IR-EULER-01).
    """
    tx, ty, tz = _derivatives(field)
    t = field.astype(np.float32)
    h, w = t.shape
    z0 = np.zeros((h, w), np.float32); resid = np.ones((h, w), np.float32)
    off = np.full((h, w), 99.0, np.float32)
    halo = WIN
    for y0 in range(0, h, 256):
        y1 = min(h, y0 + 256)
        a0, a1 = max(0, y0 - halo), min(h, y1 + halo)
        gy, gx = np.mgrid[a0:a1, 0:w]
        gx = gx.astype(np.float64); gy = gy.astype(np.float64)
        A = [tx[a0:a1].astype(np.float64), ty[a0:a1].astype(np.float64),
             tz[a0:a1].astype(np.float64),
             np.full((a1 - a0, w), N_STRUCT, dtype=np.float64)]
        b = gx * A[0] + gy * A[1] + N_STRUCT * t[a0:a1].astype(np.float64)
        sums, atb = {}, []
        for i in range(4):
            atb.append(_box_sum((A[i] * b).astype(np.float32)).astype(np.float64))
            for j in range(i, 4):
                sums[(i, j)] = _box_sum((A[i] * A[j]).astype(np.float32)).astype(np.float64)
        bb = _box_sum((b * b).astype(np.float32)).astype(np.float64)
        del A, b
        s0, s1 = y0 - a0, (y0 - a0) + (y1 - y0)
        M = np.zeros((y1 - y0, w, 4, 4)); v = np.zeros((y1 - y0, w, 4))
        for i in range(4):
            v[:, :, i] = atb[i][s0:s1]
            for j in range(4):
                M[:, :, i, j] = sums[(min(i, j), max(i, j))][s0:s1]
        trace = np.trace(M, axis1=2, axis2=3)
        M += np.eye(4)[None, None] * (1e-9 * np.maximum(trace, 1e-30))[:, :, None, None]
        u = np.linalg.solve(M, v[:, :, :, None])[:, :, :, 0]
        z0[y0:y1] = (u[:, :, 2] * DX_M).astype(np.float32)
        pred = np.einsum("...i,...i->...", v, u)
        bbs = bb[s0:s1]
        resid[y0:y1] = np.clip(np.sqrt(np.maximum(bbs - pred, 0.0) / (bbs + 1e-30)), 0, 1).astype(np.float32)
        off[y0:y1] = np.hypot(u[:, :, 0] - gx[s0:s1], u[:, :, 1] - gy[s0:s1]).astype(np.float32)
        del gy, gx, sums, atb, bb, M, v, u
    return {"z0_m": np.where(foot, z0, 0).astype(np.float32),
            "resid": np.where(foot, resid, 1).astype(np.float32),
            "offset_px": np.where(foot, off, 99).astype(np.float32)}


def build_stack(features_path: str | Path, out_path: str | Path, log=print) -> dict:
    features_path, out_path = Path(features_path), Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(features_path.parent / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(features_path) as ds:
        rtp_raw, grav_raw, base_raw = ds.read(2), ds.read(13), ds.read(15)
    valid = foot & np.isfinite(rtp_raw) & (rtp_raw > -1e30)
    rtp, grav = _fill(rtp_raw, valid), _fill(grav_raw, valid)
    base = _fill(base_raw, valid).astype(np.float64)
    log("  Euler solve: RTP")
    er = euler_solve(rtp, foot)
    log("  Euler solve: gravity")
    eg = euler_solve(grav, foot)

    def good(e):
        in_z = (e["z0_m"] >= Z_MIN_M) & (e["z0_m"] <= Z_MAX_M)
        g = np.exp(-e["resid"] * 4.0) * np.exp(-e["offset_px"] / 5.0) * in_z
        return ndimage.gaussian_filter(np.where(foot, g, 0).astype(np.float32), 1.5)

    gr, gg = good(er), good(eg)
    joint = np.sqrt(np.maximum(gr, 0) * np.maximum(gg, 0)).astype(np.float32)
    z_joint = 0.5 * (er["z0_m"] + eg["z0_m"])
    concord = (np.exp(-np.abs(er["z0_m"] - eg["z0_m"]) / 1000.0) * (joint > 0)).astype(np.float32)
    base_con = (np.exp(-np.abs(z_joint - base) / 800.0) * (joint > 0)).astype(np.float32)

    def norm01(a):
        a = np.where(foot, a, 0).astype(np.float32)
        hi = float(np.percentile(a[foot], 99.5)) if foot.any() else 1.0
        return np.clip(a / max(hi, 1e-12), 0, 1).astype(np.float32)

    stack = np.lib.format.open_memmap(out_path, mode="w+", dtype=np.float32,
                                      shape=(*foot.shape, len(CHANNELS)))
    stack[:, :, 0] = np.where(foot, np.clip(er["z0_m"] / Z_MAX_M, 0, 1), 0)
    stack[:, :, 1] = norm01(gr); stack[:, :, 2] = np.where(foot, np.clip(eg["z0_m"] / Z_MAX_M, 0, 1), 0)
    stack[:, :, 3] = norm01(gg); stack[:, :, 4] = np.where(foot, concord, 0)
    stack[:, :, 5] = norm01(joint); stack[:, :, 6] = np.where(foot, base_con, 0)
    stack.flush()
    return {"channels": list(CHANNELS), "n_channels": len(CHANNELS),
            "shape": list(foot.shape), "footprint_px": int(foot.sum()), "path": str(out_path)}
