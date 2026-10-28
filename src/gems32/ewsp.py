"""H51-1-EWSP: Elastostatic Williams-Pollard Mixed-Mode Crack-Tip Stress, Screened-Poisson
Hydrothermal Conduit Diffusion, Baranov Pseudo-Gravity Demagnetization & Orthogonal Dual-Family Cover.

Pre-registered in ``docs/research/h51-ewsp-preregistration-20261028.md`` prior to execution.

Key scientific & engineering properties:
  1. Compact, non-collinear 45-channel physical basis (33 LiDAR-free core geophysical/structural
     channels from ``.cache/gems_work/feature_stack.npy`` + 10 strictly label-free ``EWSP`` physical
     operators + 2 fold-local visible-only Williams-Pollard elastostatic fracture-mechanics channels),
     eliminating the 83-channel GBDT ancestor duplication that caused ``H49-1``'s 73.33% intra-repo
     overlap with ``H48-1`` (``IR-49-INTRAREPO-73``).
  2. Twelve brand-new physical operators never previously implemented in ``src/gems32/``:
     - Anisotropic Screened-Poisson (Helmholtz PDE) hydrothermal conduit potential & fault-strike crest;
     - Baranov (1957) 2-D Fourier vertical-integral pseudo-gravity vs isostatic gravity hydrothermal
       magnetite-destruction fault step;
     - Gallardo & Meju (2003) gravity x residualized-MT structural cross-gradient alignment;
     - Darcy-Boussinesq mountain-to-basin hydraulic head x B15 sediment-aquifer pinch-out breach;
     - Parameter-free Gabriel-graph (Gabriel & Sokal 1969) geothermal upflow conduit corridors;
     - Seam-free contractor-block interior 214Bi radon x geodetic transtensional dilation crest;
     - Multi-altitude (0 -> 600 m -> 2.4 km) Fourier upward-continuation hanging-wall dip migration;
     - 100 m LiDAR-free steerable odd-quadrature piedmont step (TIGER road & Lahontan de-confounded);
     - Single clean de-confounded 1 m 3DEP tectonic scarp step (strictly inside ``lidar_valid``,
       excluded from ``M_Sub``);
     - Fold-local Williams (1957) / Pollard & Segall (1987) Mode-I coplanar crack-tip propagation
       stress and Crider & Pollard (1998) two-tip mutual en-echelon relay-bridge stress
       ``sqrt(M1 * M2)``, derived strictly from visible faults only (``c.visible_full`` in holdout,
       ``labels.tif`` at live emission; Protocol Rule 2) and trained via leak-free nested
       complementary 50/50 segment jackknifing.
  3. Orthogonal Three-Family Dual-Cover Out-of-Fold Ensemble:
     ``ExtraTreesClassifier`` (randomized cut thresholds) + ``SplineTransformer`` L2
     ``LogisticRegression`` (smooth additive log-odds) + compact depth-regularized
     ``HistGradientBoostingClassifier`` under continuous Soft-PU reliability weights
     (``w_neg in [0.68, 1.00]``), evaluated in 400k-pixel batches (< 750 MB peak RSS on 3.8 GiB
     zero-swap hosts).
"""

from __future__ import annotations

import gc
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from numpy.lib.format import open_memmap
from scipy.fft import fftfreq, irfft2, rfft2, rfftfreq
from scipy.ndimage import (
    binary_dilation,
    binary_erosion,
    convolve,
    distance_transform_edt,
    find_objects,
    gaussian_filter,
    label,
    maximum_filter,
    minimum_filter,
    sobel,
)
from scipy.spatial import Delaunay
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import QuantileTransformer, SplineTransformer

from . import emitter, fbgr, paths, spcp, trhv

TARGET_BUDGET: int = 37_654
B_COLLAR_PX: float = 2.0
AXIAL_MIN_SEP_PX: float = 2.8

# Core 33 channels from .cache/gems_work/feature_stack.npy (indices 0..33 excluding raw un-reduced
# Band 14 `tmi` at index 13, because Band 02 `rtp` is the inclination-corrected pole reduction
# and `footprint` at index 34 is constant 1 inside valid pixels). All 33 are strictly 1m-LiDAR-free.
BASE_CORE_INDICES: tuple[int, ...] = tuple(i for i in range(34) if i != 13)
assert len(BASE_CORE_INDICES) == 33

EWSP_LABELFREE_CHANNELS: tuple[str, ...] = (
    "ewsp_helmholtz_conduit_pot",     # 0: Anisotropic Screened-Poisson (Helmholtz PDE) hydrothermal potential
    "ewsp_helmholtz_conduit_crest",   # 1: Cross-strike axial crest of Helmholtz potential x PF permeability
    "ewsp_baranov_pseudograv_demag",  # 2: Baranov Fourier pseudo-gravity vs B13 magnetite-destruction step
    "ewsp_gallardo_meju_crossgrad",   # 3: Gallardo-Meju B13 gravity x residualized B17 MT cross-gradient
    "ewsp_darcy_boussinesq_breach",   # 4: Darcy-Boussinesq topographic head x B15 aquifer pinch-out breach
    "ewsp_gabriel_conduit_network",   # 5: Parameter-free Gabriel-graph strike-aligned geothermal corridors
    "ewsp_radon_dilation_conduit",    # 6: Seam-eroded GeoDAWN 214Bi radon x GPS transtensional dilation crest
    "ewsp_upcont_dip_migration",      # 7: Fourier UC (0 -> 600 m -> 2.4 km) hanging-wall dip migration
    "ewsp_steerable_piedmont_step",   # 8: 100 m LiDAR-free steerable quadrature piedmont step (de-confounded)
    "ewsp_lidar_deconf_step",         # 9: Clean 1 m 3DEP tectonic scarp step (lidar_valid only; excluded in M_Sub)
)

EWSP_FOLDLOCAL_WP_CHANNELS: tuple[str, ...] = (
    "ewsp_williams_tip_coplanar",     # 10 (global 43): Fold-local Williams Mode-I coplanar tip propagation stress
    "ewsp_pollard_en_echelon_relay",  # 11 (global 44): Fold-local Crider-Pollard two-tip en-echelon relay stress
)

LIDAR_COL_IN_EWSP: int = 9
GLOBAL_LIDAR_COL_43: int = len(BASE_CORE_INDICES) + LIDAR_COL_IN_EWSP  # index 42 in 43-ch EXP1
GLOBAL_LIDAR_COL_45: int = len(BASE_CORE_INDICES) + LIDAR_COL_IN_EWSP  # index 42 in 45-ch EXP2/EXP3

MSUB_COLS_43: tuple[int, ...] = tuple(i for i in range(43) if i != GLOBAL_LIDAR_COL_43)
MSUB_COLS_45: tuple[int, ...] = tuple(i for i in range(45) if i != GLOBAL_LIDAR_COL_45)
assert len(MSUB_COLS_43) == 42 and len(MSUB_COLS_45) == 44


def _grad_yx(a: np.ndarray, sigma: float = 1.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = gaussian_filter(a.astype(np.float32, copy=False), sigma, mode="nearest") if sigma > 0 else a
    gy = sobel(s, axis=0).astype(np.float32) * np.float32(0.125)
    gx = sobel(s, axis=1).astype(np.float32) * np.float32(0.125)
    return gy, gx, np.hypot(gx, gy).astype(np.float32)


def compute_pf_strike_unit_vec(
    grav_iso: np.ndarray, rtp: np.ndarray, foot: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Compute local potential-field fault-strike unit vector (uy, ux) from B13 gravity + B02 RTP."""
    gy_g, gx_g, mg_g = _grad_yx(grav_iso, sigma=2.2)
    gy_m, gx_m, mg_m = _grad_yx(rtp, sigma=2.2)
    # Normal to step is gradient; fault strike is 90 deg rotated: (-gx, gy)
    wg = spcp.robust_unit_f32(mg_g, foot, pct=99.2)
    wm = spcp.robust_unit_f32(mg_m, foot, pct=99.2)
    del mg_g, mg_m
    # Orientation tensor T = w * (s s^T) to average axial strike modulo pi without sign flips
    s_gy, s_gx = -gx_g, gy_g
    s_my, s_mx = -gx_m, gy_m
    del gy_g, gx_g, gy_m, gx_m
    gn = np.hypot(s_gy, s_gx) + np.float32(1e-6)
    mn = np.hypot(s_my, s_mx) + np.float32(1e-6)
    s_gy /= gn; s_gx /= gn
    s_my /= mn; s_mx /= mn
    del gn, mn

    tyy = gaussian_filter(wg * s_gy * s_gy + np.float32(0.65) * wm * s_my * s_my, sigma=3.0, mode="nearest")
    txx = gaussian_filter(wg * s_gx * s_gx + np.float32(0.65) * wm * s_mx * s_mx, sigma=3.0, mode="nearest")
    tyx = gaussian_filter(wg * s_gy * s_gx + np.float32(0.65) * wm * s_my * s_mx, sigma=3.0, mode="nearest")
    del wg, wm, s_gy, s_gx, s_my, s_mx

    theta = np.float32(0.5) * np.arctan2(np.float32(2.0) * tyx, tyy - txx + np.float32(1e-12))
    del tyy, txx, tyx
    # Note: atan2(2*tyx, tyy - txx)/2 gives angle measured from y-axis toward x-axis: uy=cos, ux=sin
    return np.cos(theta).astype(np.float32), np.sin(theta).astype(np.float32)


def solve_anisotropic_screened_poisson_f32(
    source: np.ndarray,
    strike_uy: np.ndarray,
    strike_ux: np.ndarray,
    perm_weight: np.ndarray,
    foot: np.ndarray,
    l_par_px: float = 16.0,
    l_perp_px: float = 4.0,
    n_iter: int = 28,
) -> np.ndarray:
    """Solve anisotropic Screened-Poisson (Helmholtz) PDE `(I - div(D grad)) Phi = Q` in float32.

    Uses spatially varying anisotropic diffusivity tensor
        `D(x) = (0.35 + 0.65 * perm_weight(x)) * (l_par^2 * s s^T + l_perp^2 * n n^T)`
    discretized at 300 m macro-step (`stride = 3 px`) for rapid multi-kilometer elliptic convergence
    and bilinearly interpolated back to 100 m, followed by 6 fine-grid 100 m anisotropic relaxation
    sweeps so local fault-strike ridges remain crisp at 100 m resolution.
    """
    h, w = source.shape
    q_full = np.where(foot & np.isfinite(source), np.maximum(source, np.float32(0.0)), np.float32(0.0)).astype(np.float32)
    pw_full = np.where(foot & np.isfinite(perm_weight), np.clip(perm_weight, 0.0, 1.0), np.float32(0.0)).astype(np.float32)

    # Coarse 3x grid (h_c ~ 1244, w_c ~ 1098) -> 9x faster per sweep and 3x larger physical stencil reach
    q_c = gaussian_filter(q_full, sigma=1.2, mode="constant")[::3, ::3].copy()
    uy_c = strike_uy[::3, ::3].astype(np.float32, copy=False)
    ux_c = strike_ux[::3, ::3].astype(np.float32, copy=False)
    pw_c = (np.float32(0.35) + np.float32(0.65) * pw_full[::3, ::3]).astype(np.float32)
    foot_c = foot[::3, ::3]

    lp2 = np.float32((l_par_px / 3.0) ** 2)
    ln2 = np.float32((l_perp_px / 3.0) ** 2)
    dyy = pw_c * (lp2 * uy_c * uy_c + ln2 * ux_c * ux_c)
    dxx = pw_c * (lp2 * ux_c * ux_c + ln2 * uy_c * uy_c)
    dyx = pw_c * ((lp2 - ln2) * uy_c * ux_c)
    del pw_c

    u = q_c.copy()
    denom = np.float32(1.0) + np.float32(2.0) * (dyy + dxx)
    for _ in range(n_iter):
        u_p = np.pad(u, 1, mode="edge")
        sum_yy = u_p[2:, 1:-1] + u_p[:-2, 1:-1]
        sum_xx = u_p[1:-1, 2:] + u_p[1:-1, :-2]
        cross_yx = np.float32(0.5) * (
            u_p[2:, 2:] - u_p[2:, :-2] - u_p[:-2, 2:] + u_p[:-2, :-2]
        )
        u_new = (q_c + dyy * sum_yy + dxx * sum_xx + dyx * cross_yx) / denom
        u = np.where(foot_c, np.maximum(u_new, np.float32(0.0)), np.float32(0.0))
    del dyy, dxx, dyx, denom, q_c, foot_c

    # Upsample coarse solution back to (h, w) via nearest + Gaussian anti-alias, then 6 fine-grid sweeps
    phi = np.repeat(np.repeat(u, 3, axis=0), 3, axis=1)[:h, :w].astype(np.float32)
    del u
    phi = gaussian_filter(phi, sigma=1.5, mode="nearest")

    f_scale = np.float32(0.40) + np.float32(0.60) * pw_full
    f_lp2 = np.float32(9.0) * f_scale
    f_ln2 = np.float32(1.2) * f_scale
    f_dyy = f_lp2 * strike_uy * strike_uy + f_ln2 * strike_ux * strike_ux
    f_dxx = f_lp2 * strike_ux * strike_ux + f_ln2 * strike_uy * strike_uy
    f_dyx = (f_lp2 - f_ln2) * strike_uy * strike_ux
    f_den = np.float32(1.0) + np.float32(2.0) * (f_dyy + f_dxx)
    del f_scale, f_lp2, f_ln2, pw_full

    for _ in range(6):
        p_pad = np.pad(phi, 1, mode="edge")
        s_yy = p_pad[2:, 1:-1] + p_pad[:-2, 1:-1]
        s_xx = p_pad[1:-1, 2:] + p_pad[1:-1, :-2]
        c_yx = np.float32(0.5) * (
            p_pad[2:, 2:] - p_pad[2:, :-2] - p_pad[:-2, 2:] + p_pad[:-2, :-2]
        )
        phi = np.where(
            foot,
            np.maximum((q_full + f_dyy * s_yy + f_dxx * s_xx + f_dyx * c_yx) / f_den, np.float32(0.0)),
            np.float32(0.0),
        )
    del f_dyy, f_dxx, f_dyx, f_den, q_full
    return phi


def baranov_pseudogravity_demag_step_f32(
    rtp: np.ndarray,
    grav_iso: np.ndarray,
    foot: np.ndarray,
    dx_m: float = 100.0,
    k0_inv_m: float = 1.0 / 25_000.0,
    pad_px: int = 64,
) -> np.ndarray:
    """Baranov (1957) 2-D Fourier vertical-integral pseudo-gravity minus isostatic gravity step.

    Converts reduced-to-pole magnetic intensity ``rtp`` to synthetic pseudo-gravity via Poisson's
    relation ``g_pseudo_hat(k) = rtp_hat(k) / (2*pi*|k| + k0)``, robust-standardizes both fields on
    ``foot``, and extracts horizontal-gradient crests where ``iso_grav_anom`` shows a strong basement
    density fault step while ``pseudo-gravity`` is locally depleted/flat due to hydrothermal fluid
    alteration of magnetite to non-magnetic pyrite/chlorite/clays.
    """
    h, w = rtp.shape
    med_r = np.float32(np.median(rtp[foot][::4])) if foot.any() else np.float32(0.0)
    work = np.where(foot & np.isfinite(rtp), rtp - med_r, np.float32(0.0)).astype(np.float32)
    padded = np.pad(work, ((pad_px, pad_px), (pad_px, pad_px)), mode="reflect")
    del work

    ph, pw = padded.shape
    spec = rfft2(padded, workers=2)
    del padded

    ky = fftfreq(ph, d=dx_m).astype(np.float32)[:, None]
    kx = rfftfreq(pw, d=dx_m).astype(np.float32)[None, :]
    k_rad = np.hypot(ky, kx).astype(np.float32)
    del ky, kx

    filt = np.float32(1.0) / (np.float32(2.0 * np.pi) * k_rad + np.float32(k0_inv_m))
    filt[0, 0] = np.float32(0.0)
    del k_rad

    pgrav = irfft2(spec * filt, s=(ph, pw), workers=2)[pad_px : pad_px + h, pad_px : pad_px + w].astype(np.float32)
    del spec, filt

    # Standardize pseudo-gravity & isostatic gravity via median/MAD, then isolate density step + mag depletion
    def _z(arr: np.ndarray) -> np.ndarray:
        sub = arr[foot][::4]
        med = np.float32(np.median(sub))
        mad = np.float32(max(float(np.median(np.abs(sub - med))) * 1.4826, 1e-4))
        return np.where(foot, np.clip((arr - med) / mad, -6.0, 6.0), np.float32(0.0)).astype(np.float32)

    z_pg = _z(pgrav); del pgrav
    z_gi = _z(grav_iso)

    _, _, grad_gi = _grad_yx(z_gi, sigma=1.6)
    _, _, grad_pg = _grad_yx(z_pg, sigma=1.6)
    # Local magnetic-susceptibility deficit relative to 1.2 km background (hydrothermal alteration trough)
    pg_trough = np.maximum(gaussian_filter(z_pg, sigma=12.0, mode="nearest") - gaussian_filter(z_pg, sigma=1.8, mode="nearest"), np.float32(0.0))
    # Excess basement density gradient unexplained by unaltered magnetic basement + demagnetization trough
    demag_step = grad_gi * (
        np.float32(0.45) * np.maximum(grad_gi - np.float32(0.65) * grad_pg, np.float32(0.0))
        + np.float32(0.55) * pg_trough
    )
    del z_pg, z_gi, grad_gi, grad_pg, pg_trough
    return spcp.robust_unit_f32(demag_step, foot, pct=99.5)


def build_gabriel_conduit_corridor_f32(
    node_rows: np.ndarray,
    node_cols: np.ndarray,
    node_weights: np.ndarray,
    strike_uy: np.ndarray,
    strike_ux: np.ndarray,
    foot: np.ndarray,
    min_dist_px: float = 5.0,
    max_dist_px: float = 140.0,
    max_angle_deg: float = 32.0,
) -> np.ndarray:
    """Build parameter-free Gabriel proximity graph corridors across geothermal upflow nodes.

    An edge (i, j) of the Delaunay triangulation belongs to the Gabriel graph iff no other node k
    lies strictly inside the open disk with diameter (p_i, p_j) (Gabriel & Sokal 1969). Edges with
    length in [0.5 km, 14 km] whose azimuth agrees within ``max_angle_deg`` of the midpoint
    potential-field basement strike are rasterized as narrow 220 m fault-conduit corridors.
    """
    h, w = foot.shape
    out = np.zeros((h, w), dtype=np.float32)
    if node_rows.size < 4:
        return out

    # Spatially decluster duplicate stations within 300 m (keep max weight per 3x3 cell)
    cell_key = (node_rows // 3) * (w // 3 + 2) + (node_cols // 3)
    order = np.argsort(-node_weights)
    seen: set[int] = set()
    keep_idx: list[int] = []
    for idx in order:
        ck = int(cell_key[idx])
        if ck not in seen:
            seen.add(ck)
            keep_idx.append(int(idx))
        if len(keep_idx) >= 650:
            break
    if len(keep_idx) < 4:
        return out

    pts_y = node_rows[keep_idx].astype(np.float64)
    pts_x = node_cols[keep_idx].astype(np.float64)
    pts_w = node_weights[keep_idx].astype(np.float32)
    pts = np.column_stack([pts_y, pts_x])

    try:
        tri = Delaunay(pts)
    except Exception:
        return out

    edge_set: set[tuple[int, int]] = set()
    for simp in tri.simplices:
        a, b, c = int(simp[0]), int(simp[1]), int(simp[2])
        edge_set.add((min(a, b), max(a, b)))
        edge_set.add((min(b, c), max(b, c)))
        edge_set.add((min(a, c), max(a, c)))

    cos_thr = math.cos(math.radians(max_angle_deg))
    for i, j in edge_set:
        dy = pts_y[j] - pts_y[i]
        dx = pts_x[j] - pts_x[i]
        dist2 = dy * dy + dx * dx
        dist = math.sqrt(dist2)
        if dist < min_dist_px or dist > max_dist_px:
            continue
        # Exact Gabriel condition: midpoint M = 0.5*(p_i + p_j), radius^2 = dist2 / 4
        my = 0.5 * (pts_y[i] + pts_y[j])
        mx = 0.5 * (pts_x[i] + pts_x[j])
        d2_all = (pts_y - my) ** 2 + (pts_x - mx) ** 2
        d2_all[i] = dist2
        d2_all[j] = dist2
        if float(d2_all.min()) < 0.25 * dist2 - 1e-6:
            continue
        mr = int(np.clip(round(my), 0, h - 1))
        mc = int(np.clip(round(mx), 0, w - 1))
        if not foot[mr, mc]:
            continue
        ey, ex = dy / dist, dx / dist
        # Check axial alignment against potential-field strike at midpoint and quartiles
        q1r = int(np.clip(round(0.75 * pts_y[i] + 0.25 * pts_y[j]), 0, h - 1))
        q1c = int(np.clip(round(0.75 * pts_x[i] + 0.25 * pts_x[j]), 0, w - 1))
        q3r = int(np.clip(round(0.25 * pts_y[i] + 0.75 * pts_y[j]), 0, h - 1))
        q3c = int(np.clip(round(0.25 * pts_x[i] + 0.75 * pts_x[j]), 0, w - 1))
        align = (
            abs(ey * float(strike_uy[mr, mc]) + ex * float(strike_ux[mr, mc]))
            + abs(ey * float(strike_uy[q1r, q1c]) + ex * float(strike_ux[q1r, q1c]))
            + abs(ey * float(strike_uy[q3r, q3c]) + ex * float(strike_ux[q3r, q3c]))
        ) / 3.0
        if align < cos_thr:
            continue
        ew = float(math.sqrt(float(pts_w[i] * pts_w[j])) * math.exp(-dist / 75.0) * (align ** 2))
        n_steps = max(int(math.ceil(dist * 1.5)), 2)
        ts = np.linspace(0.0, 1.0, n_steps, dtype=np.float32)
        rr = np.clip(np.rint(pts_y[i] + ts * dy).astype(np.int32), 0, h - 1)
        cc = np.clip(np.rint(pts_x[i] + ts * dx).astype(np.int32), 0, w - 1)
        np.maximum.at(out, (rr, cc), np.float32(ew))

    sm = gaussian_filter(out, sigma=2.2, mode="constant")
    del out
    return spcp.robust_unit_f32(sm, foot, pct=99.5)


def build_ewsp_labelfree_stack(
    ddir: Path,
    base_stack_path: Path,
    out_path: Path | None = None,
    verbose: bool = True,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Build all 10 strictly label-free EWSP channels onto a disk-backed float32 memmap.

    Strictly forbids reading ``labels.tif``, ``existing_faults.tif``, ``derived_sgmc_faults_100m_u8.tif``,
    ``gdr_qfaults_traces.csv``, or ``dist_known_fault_px``.
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg, flush=True)

    with rasterio.open(ddir / "sample_submission.tif") as ds:
        ref = ds.read(1)
        transform = ds.transform
    foot = np.isfinite(ref)
    h, w = foot.shape
    del ref

    base = np.load(base_stack_path, mmap_mode="r")
    assert base.shape == (h, w, 35), f"Unexpected base stack shape: {base.shape}"

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        ewsp = open_memmap(out_path, mode="w+", dtype=np.float32, shape=(h, w, len(EWSP_LABELFREE_CHANNELS)))
    else:
        ewsp = np.zeros((h, w, len(EWSP_LABELFREE_CHANNELS)), dtype=np.float32)

    # 1. Potential-field strike field (B13 iso_grav_anom + B02 rtp)
    grav_iso = np.array(base[:, :, 12], dtype=np.float32)
    rtp = np.array(base[:, :, 1], dtype=np.float32)
    strike_uy, strike_ux = compute_pf_strike_unit_vec(grav_iso, rtp, foot)

    # 2. Hydrothermal fluid upflow source Q_hydro + discrete node list for Gabriel graph (strictly label-free)
    ext = ddir / "external"
    q_hydro = np.zeros((h, w), dtype=np.float32)
    node_r_list: list[np.ndarray] = []
    node_c_list: list[np.ndarray] = []
    node_w_list: list[np.ndarray] = []

    # (a) GDR #1391 2-m temperature probe survey (F2mDAB depth/albedo-corrected anomaly)
    probe_zip = ext / "2m_temperature_probe_INGENIOUS_regional_data.zip"
    p_lons, p_lats, p_attrs = trhv.read_point_shapefile_zip(probe_zip)
    p_rr, p_cc, p_keep = trhv._project_points_to_grid(p_lons, p_lats, transform, (h, w))
    p_idx = np.flatnonzero(p_keep)
    dab_vals = np.array([trhv._safe_float(p_attrs[i].get("F2mDAB", "")) for i in p_idx], dtype=np.float32)
    t2m_vals = np.array([trhv._safe_float(p_attrs[i].get("temp2m", "")) for i in p_idx], dtype=np.float32)
    val_dab = np.where(np.isfinite(dab_vals) & (np.abs(dab_vals) < 60.0), dab_vals, np.float32(0.0))
    pos_dab = np.maximum(val_dab, np.float32(0.0))
    if pos_dab.size > 0 and float(pos_dab.max()) > 0:
        plume_2m = trhv._nadaraya_watson_plume((h, w), p_rr, p_cc, pos_dab, sigmas=(3.5, 9.0), weights=(0.65, 0.35))
        q_hydro += np.float32(0.38) * spcp.robust_unit_f32(plume_2m, foot, pct=99.3)
        del plume_2m
        thr_p = float(np.percentile(pos_dab[pos_dab > 0], 70.0)) if (pos_dab > 0).sum() > 10 else 0.5
        hot_p = pos_dab >= max(thr_p, 0.75)
        if hot_p.any():
            node_r_list.append(p_rr[hot_p])
            node_c_list.append(p_cc[hot_p])
            node_w_list.append(np.clip(pos_dab[hot_p] / 6.0, 0.25, 1.50).astype(np.float32))
    del p_lons, p_lats, p_attrs, p_rr, p_cc, p_keep, p_idx, dab_vals, t2m_vals, val_dab, pos_dab

    # (b) GDR #1391 Paleo-geothermal sinter / travertine / silicified vents (tufa down-weighted)
    sinter_zip = ext / "paleo_geothermal_regional.zip"
    s_lons, s_lats, s_attrs = trhv.read_point_shapefile_zip(sinter_zip)
    s_rr, s_cc, s_keep = trhv._project_points_to_grid(s_lons, s_lats, transform, (h, w))
    s_idx = np.flatnonzero(s_keep)
    s_wt = np.array(
        [
            trhv._deposit_hydrothermal_weight(
                str(s_attrs[i].get("DepType", s_attrs[i].get("TYPE", s_attrs[i].get("Deposit", ""))))
            )
            for i in s_idx
        ],
        dtype=np.float32,
    )
    if s_rr.size > 0:
        s_grid = np.zeros((h, w), dtype=np.float32)
        np.maximum.at(s_grid, (s_rr, s_cc), s_wt)
        q_hydro += np.float32(0.32) * spcp.robust_unit_f32(
            gaussian_filter(s_grid, sigma=3.0, mode="constant"), foot, pct=99.4
        )
        del s_grid
        keep_s = s_wt >= 0.60
        if keep_s.any():
            node_r_list.append(s_rr[keep_s])
            node_c_list.append(s_cc[keep_s])
            node_w_list.append(s_wt[keep_s])
    del s_lons, s_lats, s_attrs, s_rr, s_cc, s_keep, s_idx, s_wt

    # (c) GDR #1391 Well/Spring Geothermometry Disequilibrium (strictly excluding dist_known_fault_px)
    ws_df = pd.read_csv(ext / "gdr_wellspring_in_footprint.csv")
    if "dist_known_fault_px" in ws_df.columns:
        ws_df = ws_df.drop(columns=["dist_known_fault_px"])
    assert "dist_known_fault_px" not in ws_df.columns
    wr = np.clip(ws_df["row"].to_numpy(dtype=np.int32), 0, h - 1)
    wc = np.clip(ws_df["col"].to_numpy(dtype=np.int32), 0, w - 1)
    t_meas = pd.to_numeric(ws_df["temp_c"], errors="coerce").fillna(15.0).to_numpy(dtype=np.float32)
    t_qtz = pd.to_numeric(ws_df["geothermquartz_c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
    t_cat = pd.to_numeric(ws_df["geothermcat_c"], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
    t_res = np.maximum(np.clip(t_qtz, 0.0, 320.0), np.clip(t_cat, 0.0, 320.0))
    diseq = np.maximum(t_res - np.maximum(t_meas, 15.0), 0.0) + np.maximum(t_meas - 22.0, 0.0) * 1.4
    ws_sig = np.clip(diseq / 120.0, 0.0, 1.5).astype(np.float32)
    ws_grid = np.zeros((h, w), dtype=np.float32)
    np.maximum.at(ws_grid, (wr, wc), ws_sig)
    q_hydro += np.float32(0.30) * spcp.robust_unit_f32(
        gaussian_filter(ws_grid, sigma=3.8, mode="constant"), foot, pct=99.4
    )
    hot_w = ws_sig >= 0.45
    if hot_w.any():
        node_r_list.append(wr[hot_w])
        node_c_list.append(wc[hot_w])
        node_w_list.append(ws_sig[hot_w])
    del ws_df, wr, wc, t_meas, t_qtz, t_cat, t_res, diseq, ws_sig, ws_grid

    # Subsurface structural permeability weight for Screened-Poisson diffusion
    grav_slope = np.array(base[:, :, 4], dtype=np.float32)   # B05
    tmi_hg = np.array(base[:, :, 2], dtype=np.float32)       # B03
    dil_rate = np.array(base[:, :, 7], dtype=np.float32)     # B08
    cond_edge = np.array(base[:, :, 29], dtype=np.float32)   # cond_edge
    perm_w = spcp.robust_unit_f32(
        np.float32(0.40) * spcp.robust_unit_f32(grav_slope, foot, pct=99.2)
        + np.float32(0.25) * spcp.robust_unit_f32(tmi_hg, foot, pct=99.2)
        + np.float32(0.20) * spcp.robust_unit_f32(cond_edge, foot, pct=99.2)
        + np.float32(0.15) * spcp.robust_unit_f32(np.maximum(dil_rate, 0.0), foot, pct=99.2),
        foot,
        pct=99.3,
    )
    del tmi_hg, cond_edge

    # Channel 0 & 1: Anisotropic Screened-Poisson (Helmholtz) Conduit Potential & Axial Fault Crest
    phi_helm = solve_anisotropic_screened_poisson_f32(
        q_hydro, strike_uy, strike_ux, perm_w, foot, l_par_px=18.0, l_perp_px=4.2, n_iter=28
    )
    del q_hydro
    helm_pot = spcp.robust_unit_f32(phi_helm, foot, pct=99.4)
    ewsp[:, :, 0] = helm_pot

    # Cross-strike second-derivative crest of Helmholtz potential coupled with permeability ridge
    gy_h, gx_h, _ = _grad_yx(helm_pot, sigma=1.4)
    ny, nx = -strike_ux, strike_uy  # unit normal to PF strike
    gn_h = gy_h * ny + gx_h * nx
    gy_gn, gx_gn, _ = _grad_yx(gn_h, sigma=1.4)
    d2n_neg = np.maximum(-(gy_gn * ny + gx_gn * nx), np.float32(0.0))
    del gy_h, gx_h, gn_h, gy_gn, gx_gn, ny, nx
    ewsp[:, :, 1] = spcp.robust_unit_f32(
        (np.float32(0.45) * helm_pot + np.float32(0.55) * spcp.robust_unit_f32(d2n_neg, foot, pct=99.3))
        * (np.float32(0.30) + np.float32(0.70) * perm_w),
        foot,
        pct=99.5,
    )
    del phi_helm, helm_pot, d2n_neg, perm_w
    gc.collect()
    log("  [EWSP] ch 0..1 (Anisotropic Screened-Poisson conduit potential & crest) built")

    # Channel 2: Baranov (1957) Fourier Pseudo-Gravity vs B13 Hydrothermal Demagnetization Step
    ewsp[:, :, 2] = baranov_pseudogravity_demag_step_f32(rtp, grav_iso, foot)
    gc.collect()
    log("  [EWSP] ch 2 (Baranov pseudo-gravity magnetite-destruction step) built")

    # Channel 3: Gallardo & Meju (2003) Gravity x Residualized-MT Cross-Gradient Alignment
    det_elev = np.array(base[:, :, 11], dtype=np.float32)    # B12
    depth_base = np.array(base[:, :, 14], dtype=np.float32)  # B15
    cond_surf = np.array(base[:, :, 16], dtype=np.float32)   # B17
    elev_slope = np.array(base[:, :, 18], dtype=np.float32)  # B19
    # Remove flat closed-playa evaporite conductance trend via stride-8 OLS on elevation & basin depth
    fy8, fx8 = np.nonzero(foot)
    fy8, fx8 = fy8[::8], fx8[::8]
    l_dep = np.log1p(np.maximum(depth_base, np.float32(0.0)))
    X_mt = np.column_stack(
        [
            np.ones(fy8.size, dtype=np.float64),
            det_elev[fy8, fx8].astype(np.float64),
            l_dep[fy8, fx8].astype(np.float64),
            elev_slope[fy8, fx8].astype(np.float64),
        ]
    )
    beta_mt, *_ = np.linalg.lstsq(X_mt, cond_surf[fy8, fx8].astype(np.float64), rcond=None)
    del X_mt, fy8, fx8
    cond_res = np.where(
        foot,
        cond_surf
        - (
            np.float32(beta_mt[0])
            + np.float32(beta_mt[1]) * det_elev
            + np.float32(beta_mt[2]) * l_dep
            + np.float32(beta_mt[3]) * elev_slope
        ),
        np.float32(0.0),
    )
    del cond_surf
    gy_gi, gx_gi, mg_gi = _grad_yx(grav_iso, sigma=1.8)
    gy_mt, gx_mt, mg_mt = _grad_yx(cond_res, sigma=1.8)
    del cond_res
    cross_sq = (gy_gi * gx_mt - gx_gi * gy_mt) ** 2
    denom_gm = (mg_gi * mg_gi) * (mg_mt * mg_mt) + np.float32(1e-7)
    colinear = np.clip(np.float32(1.0) - cross_sq / denom_gm, np.float32(0.0), np.float32(1.0))
    gm_joint = np.sqrt(
        spcp.robust_unit_f32(mg_gi, foot, pct=99.3) * spcp.robust_unit_f32(mg_mt, foot, pct=99.3)
    ) * colinear
    del gy_gi, gx_gi, mg_gi, gy_mt, gx_mt, mg_mt, cross_sq, denom_gm, colinear
    ewsp[:, :, 3] = spcp.robust_unit_f32(gm_joint, foot, pct=99.5)
    del gm_joint
    gc.collect()
    log("  [EWSP] ch 3 (Gallardo-Meju gravity x MT cross-gradient) built")

    # Channel 4: Darcy-Boussinesq Topographic-Head x Basement-Aquifer Pinch-Out Breach
    # Down-slope regional hydraulic head vector g_h = -grad(G_24(det_elev))
    hy, hx, h_mag = _grad_yx(det_elev, sigma=24.0)
    flow_y = -hy / (h_mag + np.float32(1e-4))
    flow_x = -hx / (h_mag + np.float32(1e-4))
    del hy, hx
    # Aquifer transmissivity proxy log(depth_to_base + 25m): upward forcing where thickness drops along flow
    gy_d, gx_d, d_mag = _grad_yx(np.log(np.maximum(depth_base, np.float32(0.0)) + np.float32(25.0)), sigma=2.5)
    # Both sudden fault-scarp thickening (range-front normal step) and horst pinch-out create |grad H_sed . flow|
    pinch_align = np.abs(gy_d * flow_y + gx_d * flow_x) / (d_mag + np.float32(1e-5))
    del gy_d, gx_d, flow_y, flow_x

    # De-confound Lake Lahontan (~1,180-1,360 m, approx det_elev in [-280, -90] m) flat contour terraces
    ey_loc, ex_loc, _ = _grad_yx(det_elev, sigma=2.0)
    contour_uy = -ex_loc / (np.hypot(ey_loc, ex_loc) + np.float32(1e-5))
    contour_ux = ey_loc / (np.hypot(ey_loc, ex_loc) + np.float32(1e-5))
    del ey_loc, ex_loc
    # Orthogonality between PF strike and elevation contour, or strong PF slope corroboration
    lahontan_band = np.exp(-(((det_elev + np.float32(185.0)) / np.float32(95.0)) ** 2)).astype(np.float32)
    contour_par = np.abs(strike_uy * contour_uy + strike_ux * contour_ux)
    lahontan_clean = np.float32(1.0) - np.float32(0.45) * lahontan_band * (contour_par ** 2)
    del contour_uy, contour_ux, lahontan_band, contour_par

    darcy_breach = (
        spcp.robust_unit_f32(h_mag, foot, pct=99.0)
        * spcp.robust_unit_f32(d_mag, foot, pct=99.3)
        * (np.float32(0.35) + np.float32(0.65) * pinch_align)
        * (np.float32(0.30) + np.float32(0.70) * spcp.robust_unit_f32(grav_slope, foot, pct=99.2))
        * lahontan_clean
    )
    del h_mag, d_mag, pinch_align, grav_slope
    ewsp[:, :, 4] = spcp.robust_unit_f32(darcy_breach, foot, pct=99.5)
    del darcy_breach
    gc.collect()
    log("  [EWSP] ch 4 (Darcy-Boussinesq aquifer pinch-out breach) built")

    # Channel 5: Parameter-free Gabriel-Graph Geothermal Conduit Corridors
    if node_r_list:
        all_nr = np.concatenate(node_r_list)
        all_nc = np.concatenate(node_c_list)
        all_nw = np.concatenate(node_w_list)
    else:
        all_nr = np.zeros(0, dtype=np.int32)
        all_nc = np.zeros(0, dtype=np.int32)
        all_nw = np.zeros(0, dtype=np.float32)
    del node_r_list, node_c_list, node_w_list
    ewsp[:, :, 5] = build_gabriel_conduit_corridor_f32(all_nr, all_nc, all_nw, strike_uy, strike_ux, foot)
    del all_nr, all_nc, all_nw
    gc.collect()
    log("  [EWSP] ch 5 (Gabriel-graph geothermal conduit corridors) built")

    # Channel 6: Seam-Free Contractor-Block Interior 214Bi Radon x Transtensional Dilation Crest
    with rasterio.open(ext / "acquisition_block_id_100m.tif") as ds_b:
        blk = ds_b.read(1)
    with rasterio.open(ext / "geodawn_rad_u8.tif") as ds_r:
        rad_th = ds_r.read(2).astype(np.float32)
        rad_u = ds_r.read(3).astype(np.float32)
    rad_val = foot & (blk >= 1) & (blk <= 4) & (rad_u > 0) & (rad_th > 0)
    # Erode each contractor block by 4 px (400 m) to guarantee zero flight-block seam step artifacts
    seam_free = np.zeros((h, w), dtype=bool)
    z_bi = np.zeros((h, w), dtype=np.float32)
    disk4 = distance_transform_edt(np.ones((9, 9), dtype=bool))
    st4 = (np.hypot(*(np.mgrid[-4:5, -4:5])) <= 4.0)
    del disk4
    for bid in (1, 2, 3, 4):
        mb = rad_val & (blk == bid)
        if not mb.any():
            continue
        mb_in = binary_erosion(mb, structure=st4)
        seam_free |= mb_in
        u_sub = rad_u[mb_in][::4]
        th_sub = rad_th[mb_in][::4]
        if u_sub.size > 32:
            slope_ut = float(np.cov(th_sub, u_sub)[0, 1] / (np.var(th_sub) + 1e-4))
            res_u = rad_u[mb_in] - (np.float32(np.median(u_sub)) + np.float32(slope_ut) * (rad_th[mb_in] - np.float32(np.median(th_sub))))
            mad_u = np.float32(max(float(np.median(np.abs(res_u - np.median(res_u)))) * 1.4826, 1e-3))
            z_bi[mb_in] = np.clip(res_u / mad_u, -4.0, 6.0)
    del blk, rad_th, rad_u, rad_val, st4
    # Cross-strike local radon excess (150 m minus 1.2 km background) gated against flat closed playas
    bi_loc = np.where(
        seam_free,
        np.maximum(gaussian_filter(z_bi, sigma=1.5, mode="nearest") - gaussian_filter(z_bi, sigma=12.0, mode="nearest"), np.float32(0.0)),
        np.float32(0.0),
    )
    del z_bi, seam_free
    playa_veto = spcp._sigmoid_f32((elev_slope - np.float32(0.55)) / np.float32(0.35))
    shear_rate = np.array(base[:, :, 6], dtype=np.float32)  # B07
    deq = np.log1p(np.maximum(np.array(base[:, :, 9], dtype=np.float32), np.float32(0.0)))  # B10
    strain_seis = (
        np.float32(0.45) * spcp.robust_unit_f32(np.maximum(dil_rate, np.float32(-1.0)) + np.float32(1.0), foot, pct=99.0)
        + np.float32(0.35) * spcp.robust_unit_f32(shear_rate, foot, pct=99.0)
        + np.float32(0.20) * spcp.robust_unit_f32(deq, foot, pct=99.2)
    )
    del dil_rate, shear_rate, deq
    ewsp[:, :, 6] = spcp.robust_unit_f32(
        spcp.robust_unit_f32(bi_loc, foot, pct=99.3) * playa_veto * (np.float32(0.30) + np.float32(0.70) * strain_seis),
        foot,
        pct=99.5,
    )
    del bi_loc, playa_veto, strain_seis
    gc.collect()
    log("  [EWSP] ch 6 (Seam-free 214Bi radon x transtensional dilation crest) built")

    # Channel 7: Multi-Altitude (0 -> 600 m -> 2.4 km) Fourier Upward-Continuation Dip Migration
    g_uc600, g_uc2400 = fbgr.harmonic_upward_continue_pair_f32(grav_iso, foot, heights_m=(600.0, 2400.0))
    r_uc600, r_uc2400 = fbgr.harmonic_upward_continue_pair_f32(rtp, foot, heights_m=(600.0, 2400.0))
    _, _, g0 = _grad_yx(grav_iso, sigma=1.2)
    _, _, g6 = _grad_yx(g_uc600, sigma=1.4); del g_uc600
    _, _, g24 = _grad_yx(g_uc2400, sigma=2.0); del g_uc2400
    _, _, r6 = _grad_yx(r_uc600, sigma=1.4); del r_uc600
    _, _, r24 = _grad_yx(r_uc2400, sigma=2.0); del r_uc2400
    del grav_iso, rtp

    # Dipping normal fault planes show persistent upward-continued gradient + offset toward deeper B15 hanging wall
    gy_l, gx_l, _ = _grad_yx(l_dep, sigma=3.5)
    gy_g0, gx_g0, _ = _grad_yx(g0, sigma=2.5)
    dip_coupled = np.maximum(-(gy_g0 * gy_l + gx_g0 * gx_l), np.float32(0.0))
    del gy_l, gx_l, gy_g0, gx_g0, l_dep, depth_base
    uc_persist = (
        np.cbrt(
            spcp.robust_unit_f32(g0, foot, pct=99.3)
            * spcp.robust_unit_f32(g6, foot, pct=99.3)
            * spcp.robust_unit_f32(g24, foot, pct=99.3)
        )
        * np.float32(0.60)
        + np.sqrt(spcp.robust_unit_f32(r6, foot, pct=99.3) * spcp.robust_unit_f32(r24, foot, pct=99.3)) * np.float32(0.25)
        + spcp.robust_unit_f32(dip_coupled, foot, pct=99.4) * np.float32(0.15)
    )
    del g0, g6, g24, r6, r24, dip_coupled
    ewsp[:, :, 7] = spcp.robust_unit_f32(uc_persist, foot, pct=99.5)
    del uc_persist
    gc.collect()
    log("  [EWSP] ch 7 (Fourier upward-continuation dip migration) built")

    # Channel 8 & 9: TIGER-road + Lahontan de-confounded 100 m Steerable Piedmont Step & 1 m LiDAR Step
    with rasterio.open(ext / "tiger_road_distance_m.tif") as ds_t:
        d_road = ds_t.read(1).astype(np.float32)
    road_clean = np.where(
        foot & np.isfinite(d_road),
        np.float32(1.0) - np.exp(-((np.maximum(d_road, np.float32(0.0)) / np.float32(180.0)) ** 2)),
        np.float32(1.0),
    ).astype(np.float32)
    del d_road

    with rasterio.open(ext / "blm_closed_claim_distance_m.tif") as ds_blm:
        d_blm = ds_blm.read(1).astype(np.float32)
    blm_prox = np.where(
        foot & np.isfinite(d_blm),
        np.exp(-((np.maximum(d_blm, np.float32(0.0)) / np.float32(2200.0)) ** 2)),
        np.float32(0.0),
    ).astype(np.float32)
    del d_blm

    with rasterio.open(ext / "geodawn_extensions_u8.tif") as ds_ge:
        tmi_up150 = ds_ge.read(4).astype(np.float32)
    up_v = foot & (tmi_up150 > 0)
    tmi_up150 = np.where(up_v, tmi_up150, np.float32(np.median(tmi_up150[up_v][::4])) if up_v.any() else np.float32(0.0))
    del up_v

    # Freeman & Adelson (1991) multi-orientation odd-quadrature step energy on 100 m det_elev + TMI_up150
    gy1, gx1, m1 = _grad_yx(det_elev, sigma=1.1)
    gy3, gx3, m3 = _grad_yx(det_elev, sigma=2.8)
    # Phase-coherent step occurs where fine (110 m) and coarse (280 m) odd gradients align in sign & direction
    dot_13 = np.maximum(gy1 * gy3 + gx1 * gx3, np.float32(0.0))
    steer_dem = np.sqrt(dot_13) / (np.float32(0.35) * gaussian_filter(m3, sigma=8.0, mode="nearest") + np.float32(0.8))
    del gy1, gx1, m1, gy3, gx3, m3, dot_13, det_elev, elev_slope
    _, _, m_up = _grad_yx(tmi_up150, sigma=1.5)
    del tmi_up150
    ewsp[:, :, 8] = spcp.robust_unit_f32(
        (np.float32(0.68) * spcp.robust_unit_f32(steer_dem, foot, pct=99.4)
         + np.float32(0.22) * spcp.robust_unit_f32(m_up, foot, pct=99.3)
         + np.float32(0.10) * blm_prox)
        * road_clean
        * lahontan_clean,
        foot,
        pct=99.5,
    )
    del steer_dem, m_up, blm_prox
    gc.collect()

    # Channel 9: Single clean de-confounded 1 m 3DEP LiDAR tectonic scarp step (strictly 0 outside lidar_valid)
    with rasterio.open(ext / "lidar_scarp_features_u8.tif") as ds_li:
        li_ex = ds_li.read(1).astype(np.float32)
        li_step = ds_li.read(3).astype(np.float32)
        li_down = ds_li.read(6).astype(np.float32)
        li_up = ds_li.read(7).astype(np.float32)
        li_coh = ds_li.read(10).astype(np.float32) / np.float32(255.0)
        li_valid = (ds_li.read(12) > 0) & foot
    asym = np.abs(li_down - li_up) / (li_down + li_up + np.float32(6.0))
    li_score = (
        np.sqrt(np.maximum(li_ex * li_step, np.float32(0.0)))
        * (np.float32(0.35) + np.float32(0.65) * asym)
        * (np.float32(0.25) + np.float32(0.75) * li_coh)
        * road_clean
        * lahontan_clean
    )
    del li_ex, li_step, li_down, li_up, asym, li_coh, road_clean, lahontan_clean
    li_clean = np.zeros((h, w), dtype=np.float32)
    li_clean[li_valid] = spcp.robust_unit_f32(li_score, li_valid, pct=99.4)[li_valid]
    del li_score
    ewsp[:, :, 9] = li_clean
    if hasattr(ewsp, "flush"):
        ewsp.flush()
    del li_clean, strike_uy, strike_ux
    gc.collect()
    log("  [EWSP] ch 8..9 (Steerable 100m piedmont step & clean 1m LiDAR scarp step) built")

    receipt = {
        "n_channels": len(EWSP_LABELFREE_CHANNELS),
        "channels": list(EWSP_LABELFREE_CHANNELS),
        "lidar_valid_fraction": round(float(li_valid.sum() / foot.sum()), 6),
        "catalogue_files_read": [],
    }
    return ewsp, receipt


def extract_visible_fault_tips(
    visible_mask: np.ndarray,
    min_comp_px: int = 5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Extract segment endpoints and outward unit tangents strictly from ``visible_mask``.

    Returns ``(tip_y, tip_x, tan_y, tan_x, comp_id, comp_len)`` for all connected fault segments
    with ``>= min_comp_px`` pixels. Purely geometric on ``visible_mask`` (Protocol Rule 2).
    """
    comp, n_comp = label(visible_mask, structure=np.ones((3, 3), dtype=np.int8))
    if n_comp == 0:
        z_i = np.zeros(0, dtype=np.int32)
        z_f = np.zeros(0, dtype=np.float32)
        return z_i, z_i, z_f, z_f, z_i, z_f

    sizes = np.bincount(comp.ravel())
    keep_seg = sizes >= min_comp_px
    keep_seg[0] = False
    clean = keep_seg[comp]

    k8 = np.ones((3, 3), dtype=np.int8)
    k8[1, 1] = 0
    deg = convolve(clean.astype(np.int8), k8, mode="constant", cval=0)
    slices = find_objects(comp)

    ty_list: list[int] = []
    tx_list: list[int] = []
    uy_list: list[float] = []
    ux_list: list[float] = []
    cid_list: list[int] = []
    clen_list: list[float] = []

    for cid, sl in enumerate(slices, start=1):
        if sl is None or not keep_seg[cid]:
            continue
        sub_c = comp[sl] == cid
        ry_loc, rx_loc = np.nonzero(sub_c)
        n_px = int(ry_loc.size)
        if n_px < min_comp_px:
            continue
        y0, x0 = sl[0].start, sl[1].start
        ry = ry_loc + y0
        rx = rx_loc + x0

        deg_sub = deg[sl][ry_loc, rx_loc]
        end_idx = np.flatnonzero(deg_sub <= 1)
        if end_idx.size < 2:
            # Fallback to the two principal-axis extremes for 2-px thick rasterized ends
            cy_m, cx_m = float(ry.mean()), float(rx.mean())
            dy_c, dx_c = ry - cy_m, rx - cx_m
            cov_yy = float(np.dot(dy_c, dy_c))
            cov_xx = float(np.dot(dx_c, dx_c))
            cov_yx = float(np.dot(dy_c, dx_c))
            ang = 0.5 * math.atan2(2.0 * cov_yx, cov_yy - cov_xx + 1e-12)
            proj = dy_c * math.cos(ang) + dx_c * math.sin(ang)
            end_idx = np.unique(np.concatenate([end_idx, [int(np.argmin(proj)), int(np.argmax(proj))]]))
        elif end_idx.size > 6:
            # On branched fault networks keep up to 6 most distal degree-1 tips
            cy_m, cx_m = float(ry.mean()), float(rx.mean())
            d2_c = (ry[end_idx] - cy_m) ** 2 + (rx[end_idx] - cx_m) ** 2
            end_idx = end_idx[np.argsort(-d2_c)[:6]]

        for ei in end_idx:
            ey, ex = int(ry[ei]), int(rx[ei])
            dy_all = ry - ey
            dx_all = rx - ex
            d2 = dy_all * dy_all + dx_all * dx_all
            # Outward tangent from interior segment pixels 2..11 px behind tip -> toward tip
            ring = (d2 >= 4) & (d2 <= 121)
            if not ring.any():
                ring = d2 > 0
            if not ring.any():
                continue
            vy = -float(dy_all[ring].mean())
            vx = -float(dx_all[ring].mean())
            vn = math.hypot(vy, vx)
            if vn < 1e-5:
                continue
            ty_list.append(ey)
            tx_list.append(ex)
            uy_list.append(vy / vn)
            ux_list.append(vx / vn)
            cid_list.append(cid)
            clen_list.append(float(n_px))

    return (
        np.asarray(ty_list, dtype=np.int32),
        np.asarray(tx_list, dtype=np.int32),
        np.asarray(uy_list, dtype=np.float32),
        np.asarray(ux_list, dtype=np.float32),
        np.asarray(cid_list, dtype=np.int32),
        np.asarray(clen_list, dtype=np.float32),
    )


def compute_williams_pollard_elastostatic(
    visible_mask: np.ndarray,
    foot: np.ndarray,
    max_reach_px: int = 38,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute fold-local Williams (1957) Mode-I tip propagation & Crider-Pollard (1998) two-tip
    en-echelon relay stress fields strictly from ``visible_mask``.

    Returns:
      - ``w_coplanar``: Mode-I coplanar crack-tip propagation stress ``r^(-1/2) exp(-r/L1) cos^6(theta/2)``
      - ``w_relay``: Mixed-Mode II/III wing-crack + mutual two-segment relay stress ``sqrt(M1 * M2)``
        where ``M1`` and ``M2`` originate from DISTINCT visible fault segments ``comp_1 != comp_2``.
    """
    h, w = foot.shape
    w_cop = np.zeros((h, w), dtype=np.float32)
    m1 = np.zeros((h, w), dtype=np.float32)
    m1_cid = np.zeros((h, w), dtype=np.int32)
    m2 = np.zeros((h, w), dtype=np.float32)

    tip_y, tip_x, tan_y, tan_x, comp_id, comp_len = extract_visible_fault_tips(visible_mask)
    if tip_y.size == 0:
        return w_cop, m2

    R = int(max_reach_px)
    yy_rel, xx_rel = np.mgrid[-R : R + 1, -R : R + 1].astype(np.float32)
    r_grid = np.hypot(yy_rel, xx_rel)
    in_disk = (r_grid > np.float32(0.5)) & (r_grid <= np.float32(R))

    r0 = np.float32(2.5)
    inv_sqrt_r = np.sqrt(r0 / (r_grid + r0))
    dec_cop = inv_sqrt_r * np.exp(-r_grid / np.float32(25.0))
    dec_rel = inv_sqrt_r * np.exp(-r_grid / np.float32(33.0))
    width_cop = np.float32(1.55) + np.float32(0.13) * r_grid

    for k in range(tip_y.size):
        ey = int(tip_y[k])
        ex = int(tip_x[k])
        uy = float(tan_y[k])
        ux = float(tan_x[k])
        cid = int(comp_id[k])
        k_scale = float(min(max((float(comp_len[k]) / 18.0) ** 0.35, 0.55), 1.35))

        y_lo = max(0, ey - R)
        y_hi = min(h, ey + R + 1)
        x_lo = max(0, ex - R)
        x_hi = min(w, ex + R + 1)

        py_lo = y_lo - (ey - R)
        py_hi = py_lo + (y_hi - y_lo)
        px_lo = x_lo - (ex - R)
        px_hi = px_lo + (x_hi - x_lo)

        dy = yy_rel[py_lo:py_hi, px_lo:px_hi]
        dx = xx_rel[py_lo:py_hi, px_lo:px_hi]
        rr = r_grid[py_lo:py_hi, px_lo:px_hi]
        msk = in_disk[py_lo:py_hi, px_lo:px_hi]

        s_par = dy * uy + dx * ux
        s_perp = -dy * ux + dx * uy
        fwd = msk & (s_par > np.float32(-1.5))
        if not fwd.any():
            continue

        cos_th = np.clip(s_par / (rr + np.float32(1e-6)), np.float32(-1.0), np.float32(1.0))
        cos_half2 = np.maximum(np.float32(0.5) * (np.float32(1.0) + cos_th), np.float32(0.0))  # cos^2(theta/2)
        sin_th2 = np.maximum(np.float32(1.0) - cos_th * cos_th, np.float32(0.0))

        # 1. Coplanar Mode-I propagation beam
        wc = width_cop[py_lo:py_hi, px_lo:px_hi]
        beam_cop = (
            np.float32(k_scale)
            * dec_cop[py_lo:py_hi, px_lo:px_hi]
            * (cos_half2 ** 3)
            * np.exp(-(s_perp * s_perp) / (np.float32(2.0) * wc * wc))
        )
        beam_cop = np.where(fwd, beam_cop, np.float32(0.0))
        sub_cop = w_cop[y_lo:y_hi, x_lo:x_hi]
        np.maximum(sub_cop, beam_cop, out=sub_cop)

        # 2. Mixed-Mode II/III wing-crack & step-over relay lobe (tracks top-2 distinct segments)
        lobe_rel = (
            np.float32(k_scale)
            * dec_rel[py_lo:py_hi, px_lo:px_hi]
            * (cos_half2 ** 2)
            * (np.float32(0.50) + np.float32(0.85) * sin_th2)
            * np.exp(-(s_perp * s_perp) / (np.float32(2.0) * ((np.float32(3.5) + np.float32(0.32) * rr) ** 2)))
        )
        lobe_rel = np.where(fwd, lobe_rel, np.float32(0.0))

        sub_m1 = m1[y_lo:y_hi, x_lo:x_hi]
        sub_c1 = m1_cid[y_lo:y_hi, x_lo:x_hi]
        sub_m2 = m2[y_lo:y_hi, x_lo:x_hi]

        same_c = sub_c1 == cid
        # Case A: same component already holds m1 -> update m1 only
        upd_same = same_c & (lobe_rel > sub_m1)
        if upd_same.any():
            sub_m1[upd_same] = lobe_rel[upd_same]
        # Case B: different component beats m1 -> demote old m1 to m2, set new m1 & cid
        beat_m1 = (~same_c) & (lobe_rel > sub_m1)
        if beat_m1.any():
            sub_m2[beat_m1] = sub_m1[beat_m1]
            sub_m1[beat_m1] = lobe_rel[beat_m1]
            sub_c1[beat_m1] = cid
        # Case C: different component sits between m2 and m1 -> update m2
        beat_m2 = (~same_c) & (~beat_m1) & (lobe_rel > sub_m2)
        if beat_m2.any():
            sub_m2[beat_m2] = lobe_rel[beat_m2]

    # Mutual two-segment relay bridge sqrt(m1 * m2) + single-tip wing shear lobe
    mutual_bridge = np.sqrt(np.maximum(m1 * m2, np.float32(0.0)))
    w_rel = np.where(foot, np.float32(0.72) * mutual_bridge + np.float32(0.28) * m1, np.float32(0.0)).astype(np.float32)
    w_cop = np.where(foot, w_cop, np.float32(0.0)).astype(np.float32)
    del m1, m1_cid, m2, mutual_bridge
    return np.clip(w_cop, 0.0, 1.5).astype(np.float32), np.clip(w_rel, 0.0, 1.5).astype(np.float32)


def audit_single_feature_canaries(
    base_stack_path: Path,
    ewsp_stack_path: Path,
    ctx: Any,
    foot: np.ndarray,
    labels: np.ndarray,
    seed: int = 20261028,
) -> list[dict[str, Any]]:
    """Protocol Rule 4: Test EVERY feature channel alone on holdout / public labels (AUC <= 0.90)."""
    rng = np.random.default_rng(seed)
    pos_y, pos_x = np.nonzero(labels & foot)
    neg_y, neg_x = np.nonzero((~labels) & foot)
    sp = rng.choice(pos_y.size, size=min(25_000, pos_y.size), replace=False)
    sn = rng.choice(neg_y.size, size=min(50_000, neg_y.size), replace=False)
    ry = np.concatenate([pos_y[sp], neg_y[sn]])
    rx = np.concatenate([pos_x[sp], neg_x[sn]])
    y_bin = np.concatenate([np.ones(sp.size, dtype=np.int8), np.zeros(sn.size, dtype=np.int8)])

    base_mm = np.load(base_stack_path, mmap_mode="r")
    ewsp_mm = np.load(ewsp_stack_path, mmap_mode="r")
    results: list[dict[str, Any]] = []

    for j, b_idx in enumerate(BASE_CORE_INDICES):
        vals = np.nan_to_num(np.asarray(base_mm[ry, rx, b_idx], dtype=np.float32), nan=0.0)
        auc = float(roc_auc_score(y_bin, vals))
        sym = max(auc, 1.0 - auc)
        results.append(
            {
                "index": j,
                "name": f"base_{b_idx:02d}",
                "source": "base_core_33",
                "raw_auc": round(auc, 5),
                "symmetric_auc": round(sym, 5),
                "passed": bool(sym <= 0.90),
            }
        )

    for k, cname in enumerate(EWSP_LABELFREE_CHANNELS):
        vals = np.nan_to_num(np.asarray(ewsp_mm[ry, rx, k], dtype=np.float32), nan=0.0)
        auc = float(roc_auc_score(y_bin, vals))
        sym = max(auc, 1.0 - auc)
        results.append(
            {
                "index": len(BASE_CORE_INDICES) + k,
                "name": cname,
                "source": "ewsp_labelfree_10",
                "raw_auc": round(auc, 5),
                "symmetric_auc": round(sym, 5),
                "passed": bool(sym <= 0.90),
            }
        )

    # Also test the 2 fold-local Williams-Pollard channels strictly on held-out active_sub vs withheld truth!
    wp0_vals: list[np.ndarray] = []
    wp1_vals: list[np.ndarray] = []
    wp_y: list[np.ndarray] = []
    for c in ctx.cells[:4]:  # all 4 quadrants on draw 20
        w_cop, w_rel = compute_williams_pollard_elastostatic(c.visible_full, foot)
        sy, sx = c.bbox
        act = c.active_sub & (c.d_vis_sub > B_COLLAR_PX)
        truth_sub = np.zeros(act.shape, dtype=bool)
        truth_sub[c.truth_coords] = True
        pos_m = act & truth_sub
        neg_m = act & (~truth_sub)
        py_c, px_c = np.nonzero(pos_m)
        ny_c, nx_c = np.nonzero(neg_m)
        take_n = rng.choice(ny_c.size, size=min(15_000, ny_c.size), replace=False)
        wp0_vals.append(np.concatenate([w_cop[sy, sx][py_c, px_c], w_cop[sy, sx][ny_c[take_n], nx_c[take_n]]]))
        wp1_vals.append(np.concatenate([w_rel[sy, sx][py_c, px_c], w_rel[sy, sx][ny_c[take_n], nx_c[take_n]]]))
        wp_y.append(np.concatenate([np.ones(py_c.size, dtype=np.int8), np.zeros(take_n.size, dtype=np.int8)]))
        del w_cop, w_rel

    yv_wp = np.concatenate(wp_y)
    for k, (cname, arr_list) in enumerate(zip(EWSP_FOLDLOCAL_WP_CHANNELS, (wp0_vals, wp1_vals))):
        vals = np.concatenate(arr_list)
        auc = float(roc_auc_score(yv_wp, vals))
        sym = max(auc, 1.0 - auc)
        results.append(
            {
                "index": 43 + k,
                "name": cname,
                "source": "ewsp_foldlocal_wp_2 (held-out active_sub)",
                "raw_auc": round(auc, 5),
                "symmetric_auc": round(sym, 5),
                "passed": bool(sym <= 0.90),
            }
        )

    leaked = [r for r in results if not r["passed"]]
    if leaked:
        raise RuntimeError(f"Protocol Rule 4 Canary FAILED (>0.90 AUC): {leaked}")
    return results


def _gather_pixel_matrix(
    ry: np.ndarray,
    rx: np.ndarray,
    base_mm: np.ndarray,
    ewsp_mm: np.ndarray,
    wp_pair: tuple[np.ndarray, np.ndarray] | None,
    col_indices: tuple[int, ...] | None = None,
) -> np.ndarray:
    """Gather a compact float32 matrix `(N, C)` from disk-backed memmaps without copying full rasters."""
    n = ry.size
    n_tot = 45 if wp_pair is not None else 43
    X = np.empty((n, n_tot), dtype=np.float32)
    for j, b_idx in enumerate(BASE_CORE_INDICES):
        X[:, j] = base_mm[ry, rx, b_idx]
    off = len(BASE_CORE_INDICES)
    for k in range(10):
        X[:, off + k] = ewsp_mm[ry, rx, k]
    if wp_pair is not None:
        X[:, 43] = wp_pair[0][ry, rx]
        X[:, 44] = wp_pair[1][ry, rx]
    np.nan_to_num(X, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    if col_indices is not None:
        return np.ascontiguousarray(X[:, col_indices], dtype=np.float32)
    return X


def _soft_pu_neg_weights(ewsp_mm: np.ndarray, ry: np.ndarray, rx: np.ndarray) -> np.ndarray:
    """Continuous bounded Soft-PU negative reliability weights in `[0.68, 1.00]` (fixes Hard-PU collapse)."""
    # Unmapped blind conduit indicator: mean of Helmholtz crest (1), Baranov demag (2), Gallardo-Meju (3), Darcy (4)
    c_blind = (
        np.float32(0.30) * ewsp_mm[ry, rx, 1]
        + np.float32(0.25) * ewsp_mm[ry, rx, 2]
        + np.float32(0.25) * ewsp_mm[ry, rx, 3]
        + np.float32(0.20) * ewsp_mm[ry, rx, 4]
    )
    return np.clip(np.float32(1.0) - np.float32(0.32) * c_blind, np.float32(0.68), np.float32(1.0)).astype(np.float32)


def _fit_three_family_ensemble(
    X: np.ndarray,
    y: np.ndarray,
    sample_weight: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    """Fit orthogonal 3-family ensemble: ExtraTrees + Spline-Logistic GAM + Compact Regularized GBDT."""
    et = ExtraTreesClassifier(
        n_estimators=96,
        max_depth=16,
        min_samples_leaf=24,
        max_features="sqrt",
        bootstrap=False,
        n_jobs=2,
        random_state=seed,
    )
    et.fit(X, y, sample_weight=sample_weight)

    gam = Pipeline(
        [
            ("qt", QuantileTransformer(n_quantiles=256, output_distribution="uniform", random_state=seed)),
            ("sp", SplineTransformer(n_knots=5, degree=2, include_bias=False)),
            ("lr", LogisticRegression(C=0.25, max_iter=300, solver="lbfgs")),
        ]
    )
    gam.fit(X, y, lr__sample_weight=sample_weight)

    gbdt = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.055,
        max_leaf_nodes=23,
        max_depth=5,
        min_samples_leaf=90,
        l2_regularization=4.0,
        random_state=seed,
    )
    gbdt.fit(X, y, sample_weight=sample_weight)

    return {"et": et, "gam": gam, "gbdt": gbdt}


def _predict_three_family_batched(
    ens: dict[str, Any],
    ry: np.ndarray,
    rx: np.ndarray,
    base_mm: np.ndarray,
    ewsp_mm: np.ndarray,
    wp_pair: tuple[np.ndarray, np.ndarray] | None,
    col_indices: tuple[int, ...] | None = None,
    batch_size: int = 380_000,
) -> np.ndarray:
    """Predict blended probability over `(ry, rx)` in 380k-pixel batches (< 120 MB batch RAM)."""
    n = ry.size
    out = np.empty(n, dtype=np.float32)
    et = ens["et"]
    gam = ens["gam"]
    gbdt = ens["gbdt"]
    for s in range(0, n, batch_size):
        e = min(s + batch_size, n)
        Xb = _gather_pixel_matrix(ry[s:e], rx[s:e], base_mm, ewsp_mm, wp_pair, col_indices=col_indices)
        p_et = et.predict_proba(Xb)[:, 1].astype(np.float32)
        p_gam = gam.predict_proba(Xb)[:, 1].astype(np.float32)
        p_gb = gbdt.predict_proba(Xb)[:, 1].astype(np.float32)
        out[s:e] = np.float32(0.38) * p_et + np.float32(0.24) * p_gam + np.float32(0.38) * p_gb
        del Xb, p_et, p_gam, p_gb
    return out


def _build_training_dataset(
    train_domain: np.ndarray,
    visible_train: np.ndarray,
    foot: np.ndarray,
    lidar_valid: np.ndarray,
    base_mm: np.ndarray,
    ewsp_mm: np.ndarray,
    include_wp: bool,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Construct leak-free Soft-PU training matrices for `M_Full` (inside LiDAR) and `M_Sub` (LiDAR-free).

    Strictly uses ``visible_train = cell.visible_full & train_domain`` (never full ``labels``) so
    ``hidden_train`` segments in ``HoldoutContext`` are never observed. When ``include_wp=True``,
    uses complementary 50/50 connected-segment jackknifing of ``visible_train`` so every positive
    training pixel sits on a withheld half-subset at ``> 2 px`` from the visible half-subset
    generating the Williams-Pollard field — eliminating self-tip target leakage.
    """
    rng = np.random.default_rng(seed)
    vis_in_tr = visible_train & train_domain

    if not include_wp:
        d_tr = distance_transform_edt(~vis_in_tr)
        pos_m = vis_in_tr
        neg_m = train_domain & (~vis_in_tr) & (d_tr > 5.0)
        del d_tr

        # M_Full (trained inside lidar_valid)
        py_f, px_f = np.nonzero(pos_m & lidar_valid)
        ny_f, nx_f = np.nonzero(neg_m & lidar_valid)
        sp_f = rng.choice(py_f.size, size=min(18_000, py_f.size), replace=False)
        sn_f = rng.choice(ny_f.size, size=min(36_000, ny_f.size), replace=False)
        ry_f = np.concatenate([py_f[sp_f], ny_f[sn_f]])
        rx_f = np.concatenate([px_f[sp_f], nx_f[sn_f]])
        X_full = _gather_pixel_matrix(ry_f, rx_f, base_mm, ewsp_mm, wp_pair=None, col_indices=None)
        y_full = np.concatenate([np.ones(sp_f.size, dtype=np.int8), np.zeros(sn_f.size, dtype=np.int8)])
        w_full = np.concatenate(
            [np.ones(sp_f.size, dtype=np.float32), _soft_pu_neg_weights(ewsp_mm, ny_f[sn_f], nx_f[sn_f])]
        )

        # M_Sub (trained across all train_domain using strictly LiDAR-free columns)
        py_s, px_s = np.nonzero(pos_m)
        ny_s, nx_s = np.nonzero(neg_m)
        sp_s = rng.choice(py_s.size, size=min(20_000, py_s.size), replace=False)
        sn_s = rng.choice(ny_s.size, size=min(40_000, ny_s.size), replace=False)
        ry_s = np.concatenate([py_s[sp_s], ny_s[sn_s]])
        rx_s = np.concatenate([px_s[sp_s], nx_s[sn_s]])
        X_sub = _gather_pixel_matrix(ry_s, rx_s, base_mm, ewsp_mm, wp_pair=None, col_indices=MSUB_COLS_43)
        y_sub = np.concatenate([np.ones(sp_s.size, dtype=np.int8), np.zeros(sn_s.size, dtype=np.int8)])
        w_sub = np.concatenate(
            [np.ones(sp_s.size, dtype=np.float32), _soft_pu_neg_weights(ewsp_mm, ny_s[sn_s], nx_s[sn_s])]
        )
        return X_full, y_full, w_full, X_sub, y_sub, w_sub

    # Complementary 2-world segment jackknifing of visible_train for leak-free Williams-Pollard training
    comp_tr, n_seg = label(vis_in_tr, structure=np.ones((3, 3), dtype=np.int8))
    seg_coin = rng.integers(0, 2, size=n_seg + 1)
    seg_coin[0] = -1

    Xf_parts, yf_parts, wf_parts = [], [], []
    Xs_parts, ys_parts, ws_parts = [], [], []

    for world in (0, 1):
        vis_w = (comp_tr > 0) & (seg_coin[comp_tr] == world)
        hid_w = (comp_tr > 0) & (seg_coin[comp_tr] == (1 - world))
        d_vis_w = distance_transform_edt(~vis_w)
        d_hid_w = distance_transform_edt(~hid_w)
        wp_w = compute_williams_pollard_elastostatic(vis_w, foot)

        pos_w = train_domain & hid_w & (d_vis_w > B_COLLAR_PX)
        neg_w = train_domain & (~vis_in_tr) & (d_vis_w > B_COLLAR_PX) & (d_hid_w > 5.0)
        del vis_w, hid_w, d_vis_w, d_hid_w

        # M_Full half
        py_f, px_f = np.nonzero(pos_w & lidar_valid)
        ny_f, nx_f = np.nonzero(neg_w & lidar_valid)
        sp_f = rng.choice(py_f.size, size=min(10_000, py_f.size), replace=False)
        sn_f = rng.choice(ny_f.size, size=min(20_000, ny_f.size), replace=False)
        ry_f = np.concatenate([py_f[sp_f], ny_f[sn_f]])
        rx_f = np.concatenate([px_f[sp_f], nx_f[sn_f]])
        Xf_parts.append(_gather_pixel_matrix(ry_f, rx_f, base_mm, ewsp_mm, wp_pair=wp_w, col_indices=None))
        yf_parts.append(np.concatenate([np.ones(sp_f.size, dtype=np.int8), np.zeros(sn_f.size, dtype=np.int8)]))
        wf_parts.append(
            np.concatenate([np.ones(sp_f.size, dtype=np.float32), _soft_pu_neg_weights(ewsp_mm, ny_f[sn_f], nx_f[sn_f])])
        )

        # M_Sub half (strictly LiDAR-free 44 columns)
        py_s, px_s = np.nonzero(pos_w)
        ny_s, nx_s = np.nonzero(neg_w)
        sp_s = rng.choice(py_s.size, size=min(11_000, py_s.size), replace=False)
        sn_s = rng.choice(ny_s.size, size=min(22_000, ny_s.size), replace=False)
        ry_s = np.concatenate([py_s[sp_s], ny_s[sn_s]])
        rx_s = np.concatenate([px_s[sp_s], nx_s[sn_s]])
        Xs_parts.append(_gather_pixel_matrix(ry_s, rx_s, base_mm, ewsp_mm, wp_pair=wp_w, col_indices=MSUB_COLS_45))
        ys_parts.append(np.concatenate([np.ones(sp_s.size, dtype=np.int8), np.zeros(sn_s.size, dtype=np.int8)]))
        ws_parts.append(
            np.concatenate([np.ones(sp_s.size, dtype=np.float32), _soft_pu_neg_weights(ewsp_mm, ny_s[sn_s], nx_s[sn_s])])
        )
        del wp_w, pos_w, neg_w

    del comp_tr
    return (
        np.concatenate(Xf_parts, axis=0),
        np.concatenate(yf_parts, axis=0),
        np.concatenate(wf_parts, axis=0),
        np.concatenate(Xs_parts, axis=0),
        np.concatenate(ys_parts, axis=0),
        np.concatenate(ws_parts, axis=0),
    )


def _calibrate_msub_to_mfull(
    p_full_ref: np.ndarray,
    p_sub_ref: np.ndarray,
    p_sub_target: np.ndarray,
) -> np.ndarray:
    """Monotonic empirical-quantile calibration of `M_Sub` onto `M_Full`'s distribution."""
    if p_full_ref.size < 200 or p_sub_ref.size < 200 or p_sub_target.size == 0:
        return p_sub_target
    q_grid = np.linspace(0.0, 1.0, 513, dtype=np.float64)
    src_q = np.quantile(p_sub_ref[:: max(1, p_sub_ref.size // 80_000)], q_grid)
    dst_q = np.quantile(p_full_ref[:: max(1, p_full_ref.size // 80_000)], q_grid)
    src_u, u_idx = np.unique(src_q, return_index=True)
    dst_u = dst_q[u_idx]
    if src_u.size < 4:
        return p_sub_target
    return np.interp(p_sub_target, src_u, dst_u).astype(np.float32)


def compose_stationary_ewsp_belief(
    dual_prob: np.ndarray,
    base_mm: np.ndarray,
    ewsp_mm: np.ndarray,
    wp_pair: tuple[np.ndarray, np.ndarray] | None,
    foot: np.ndarray,
    w_helm: float,
    w_wp: float,
    bbox: tuple[slice, slice] | None = None,
) -> np.ndarray:
    """100% stationary EWSP belief fusion (identical formula & weights in holdout and full-scene live).

    Supports optional ``bbox`` slice `(sy, sx)` so per-cell holdout evaluation operates strictly
    inside the cell bounding box (< 15 MB RAM) with identical local operators.
    """
    sl = bbox if bbox is not None else (slice(None), slice(None))
    f_sub = foot[sl]
    p_in = dual_prob[sl] if dual_prob.shape == foot.shape else dual_prob
    p = np.where(f_sub & np.isfinite(p_in), np.clip(p_in, 0.0, 1.0), np.float32(0.0)).astype(np.float32)

    helm_crest = np.asarray(ewsp_mm[sl[0], sl[1], 1], dtype=np.float32)
    baranov = np.asarray(ewsp_mm[sl[0], sl[1], 2], dtype=np.float32)
    gm_cross = np.asarray(ewsp_mm[sl[0], sl[1], 3], dtype=np.float32)
    darcy = np.asarray(ewsp_mm[sl[0], sl[1], 4], dtype=np.float32)
    gabriel = np.asarray(ewsp_mm[sl[0], sl[1], 5], dtype=np.float32)
    steer_step = np.asarray(ewsp_mm[sl[0], sl[1], 8], dtype=np.float32)

    subsurf_conduit = (
        np.float32(0.34) * helm_crest
        + np.float32(0.24) * baranov
        + np.float32(0.20) * gm_cross
        + np.float32(0.12) * darcy
        + np.float32(0.10) * gabriel
    )

    surf = (
        np.float32(1.0 - w_helm) * p
        + np.float32(w_helm) * np.sqrt(np.maximum(p * subsurf_conduit, np.float32(0.0)))
    ).astype(np.float32)

    if wp_pair is not None and w_wp > 0.0:
        wp0 = wp_pair[0][sl] if wp_pair[0].shape == foot.shape else wp_pair[0]
        wp1 = wp_pair[1][sl] if wp_pair[1].shape == foot.shape else wp_pair[1]
        wp_field = np.clip(np.float32(0.52) * wp0 + np.float32(0.48) * wp1, np.float32(0.0), np.float32(1.2))
        phys_corrob = np.clip(
            np.float32(0.45) * p + np.float32(0.30) * steer_step + np.float32(0.25) * subsurf_conduit,
            np.float32(0.0),
            np.float32(1.0),
        )
        surf = surf * (np.float32(1.0) + np.float32(w_wp) * wp_field * (np.float32(0.25) + np.float32(0.75) * phys_corrob))
        del wp_field, phys_corrob

    elev_slope = np.asarray(base_mm[sl[0], sl[1], 18], dtype=np.float32)
    depth_base = np.asarray(base_mm[sl[0], sl[1], 14], dtype=np.float32)
    flat_playa = (
        spcp._sigmoid_f32((np.float32(0.75) - elev_slope) / np.float32(0.25))
        * spcp._sigmoid_f32((depth_base - np.float32(450.0)) / np.float32(180.0))
        * np.clip(np.float32(1.0) - np.float32(1.6) * subsurf_conduit, np.float32(0.0), np.float32(1.0))
    )
    surf = surf * (np.float32(1.0) - np.float32(0.55) * flat_playa)
    del subsurf_conduit, flat_playa, elev_slope, depth_base

    sharpened = fbgr.sharpen_probability_crest(surf, f_sub, crest_boost=0.45)
    del surf
    s_max = float(sharpened[f_sub].max()) if f_sub.any() else 1.0
    if s_max > 1e-8:
        sharpened = (sharpened / np.float32(s_max)).astype(np.float32)
    sharpened[~f_sub] = np.float32(0.0)
    return np.clip(sharpened, np.float32(0.0), np.float32(1.0))


def emit_ewsp_dots(
    belief_surface: np.ndarray,
    eligible_mask: np.ndarray,
    budget: int = TARGET_BUDGET,
    min_sep_px: float = AXIAL_MIN_SEP_PX,
    support_mult: int = 9,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Pack ``budget`` discrete 1-px fault detections via ``gems32.emitter.emit(min_sep_px=2.8)``."""
    if budget <= 0 or not eligible_mask.any():
        return np.zeros(belief_surface.shape, dtype=bool), {"n_emitted": 0, "stopped_by": "zero_budget"}

    f = np.where(eligible_mask & np.isfinite(belief_surface), belief_surface, np.float32(0.0)).astype(np.float32)
    pos_vals = f[f > 0]
    max_support_px = max(int(budget) * int(support_mult), 45_000)
    if pos_vals.size > max_support_px:
        thr = float(np.partition(pos_vals, pos_vals.size - max_support_px)[pos_vals.size - max_support_px])
        f = np.where(f >= np.float32(thr), f, np.float32(0.0))
    del pos_vals

    field64 = np.where(f > 0, np.power(np.maximum(f, 0.0), 1.35), 0.0).astype(np.float64)
    del f
    dots, log_rec = emitter.emit(
        field64,
        budget=int(budget),
        prior_dti=0.0,
        gain_floor=0.0,
        min_sep_px=float(min_sep_px),
    )
    del field64
    return (dots & eligible_mask), log_rec.as_dict()


def run_ewsp_holdout_and_full_oof(
    base_stack_path: Path,
    ewsp_stack_path: Path,
    ctx: Any,
    lidar_valid: np.ndarray,
    include_wp: bool,
    collar_px: int = 15,
    seed_base: int = 5100,
    cache_prefix: Path | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Fit Dual-Cover 3-family OOF models strictly per cell (`cell.visible_full & train_dom`) across all
    8 holdout cells (`draw20/21 x fold0..3`), while averaging full-scene OOF predictions (`0.5 * draw20
    + 0.5 * draw21`) onto each held-out quadrant `ctx.quad == cell.fold`.
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg, flush=True)

    foot = ctx.foot
    labels = ctx.labels
    wp_full_live = compute_williams_pollard_elastostatic(labels, foot) if include_wp else None

    if cache_prefix is not None and Path(f"{cache_prefix}_full.npy").exists():
        cell_dual_probs = {
            cell.key: np.load(f"{cache_prefix}_{cell.key}.npy") for cell in ctx.cells
        }
        full_oof_dual = np.load(f"{cache_prefix}_full.npy")
        log(f"  [EWSP OOF] restored cached OOF predictions from {cache_prefix}_*.npy")
        return {
            "cell_dual_probs": cell_dual_probs,
            "full_oof_dual": full_oof_dual,
            "wp_full_live": wp_full_live,
        }

    base_mm = np.load(base_stack_path, mmap_mode="r")
    ewsp_mm = np.load(ewsp_stack_path, mmap_mode="r")
    h, w = foot.shape
    fold_train: dict[int, np.ndarray] = {}
    for f in (0, 1, 2, 3):
        collar = binary_dilation(ctx.quad == f, structure=np.ones((3, 3), dtype=bool), iterations=collar_px) & foot
        fold_train[f] = foot & (~collar)
    msub_cols = MSUB_COLS_45 if include_wp else MSUB_COLS_43

    cell_dual_probs: dict[str, np.ndarray] = {}
    full_oof_dual = np.zeros((h, w), dtype=np.float32)

    for cell in ctx.cells:
        q = cell.fold
        train_dom = fold_train[q]
        vis_tr = cell.visible_full & train_dom
        c_seed = seed_base + cell.seed * 31 + q * 7

        X_full, y_full, w_full, X_sub, y_sub, w_sub = _build_training_dataset(
            train_dom,
            vis_tr,
            foot,
            lidar_valid,
            base_mm,
            ewsp_mm,
            include_wp=include_wp,
            seed=c_seed,
        )
        ens_full = _fit_three_family_ensemble(X_full, y_full, w_full, seed=c_seed + 1)
        del X_full, y_full, w_full
        gc.collect()
        ens_sub = _fit_three_family_ensemble(X_sub, y_sub, w_sub, seed=c_seed + 2)
        del X_sub, y_sub, w_sub
        gc.collect()

        wp_cell = compute_williams_pollard_elastostatic(cell.visible_full, foot) if include_wp else None

        # Reference calibration sample inside train_dom & lidar_valid & ~vis_tr
        cal_y, cal_x = np.nonzero(train_dom & lidar_valid & (~vis_tr))
        cal_step = max(1, cal_y.size // 40_000)
        cal_y, cal_x = cal_y[::cal_step], cal_x[::cal_step]
        p_ref_full = _predict_three_family_batched(ens_full, cal_y, cal_x, base_mm, ewsp_mm, wp_cell, col_indices=None)
        p_ref_sub = _predict_three_family_batched(ens_sub, cal_y, cal_x, base_mm, ewsp_mm, wp_cell, col_indices=msub_cols)
        del cal_y, cal_x

        # 1. Predict holdout cell bbox
        sy, sx = cell.bbox
        elig_sub = cell.active_sub & (cell.d_vis_sub > B_COLLAR_PX)
        ey_loc, ex_loc = np.nonzero(elig_sub)
        ey = ey_loc + sy.start
        ex = ex_loc + sx.start

        li_e = lidar_valid[ey, ex]
        prob_sub = np.zeros(elig_sub.shape, dtype=np.float32)
        if li_e.any():
            pf = _predict_three_family_batched(
                ens_full, ey[li_e], ex[li_e], base_mm, ewsp_mm, wp_cell, col_indices=None
            )
            prob_sub[ey_loc[li_e], ex_loc[li_e]] = pf
        if (~li_e).any():
            ps_raw = _predict_three_family_batched(
                ens_sub, ey[~li_e], ex[~li_e], base_mm, ewsp_mm, wp_cell, col_indices=msub_cols
            )
            prob_sub[ey_loc[~li_e], ex_loc[~li_e]] = _calibrate_msub_to_mfull(p_ref_full, p_ref_sub, ps_raw)
        cell_dual_probs[cell.key] = prob_sub
        del wp_cell

        # 2. Accumulate 0.5 weight onto held-out quadrant q for full-scene live OOF
        q_mask = foot & (ctx.quad == q)
        qy, qx = np.nonzero(q_mask)
        li_q = lidar_valid[qy, qx]
        q_pred = np.empty(qy.size, dtype=np.float32)
        if li_q.any():
            q_pred[li_q] = _predict_three_family_batched(
                ens_full, qy[li_q], qx[li_q], base_mm, ewsp_mm, wp_full_live, col_indices=None
            )
        if (~li_q).any():
            ps_q = _predict_three_family_batched(
                ens_sub, qy[~li_q], qx[~li_q], base_mm, ewsp_mm, wp_full_live, col_indices=msub_cols
            )
            q_pred[~li_q] = _calibrate_msub_to_mfull(p_ref_full, p_ref_sub, ps_q)
        full_oof_dual[qy, qx] += np.float32(0.5) * q_pred

        del ens_full, ens_sub, p_ref_full, p_ref_sub, q_pred
        gc.collect()
        log(f"  [EWSP OOF] cell {cell.key} fitted & evaluated (include_wp={include_wp})")

    if cache_prefix is not None:
        Path(cache_prefix).parent.mkdir(parents=True, exist_ok=True)
        for ck, c_arr in cell_dual_probs.items():
            np.save(f"{cache_prefix}_{ck}.npy", c_arr)
        np.save(f"{cache_prefix}_full.npy", full_oof_dual)

    return {
        "cell_dual_probs": cell_dual_probs,
        "full_oof_dual": full_oof_dual,
        "wp_full_live": wp_full_live,
    }
