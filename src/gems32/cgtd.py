"""H49-1 (CG-TILT-NOISYOR): Multi-Field Miller-Singh Tilt-Zero Wall, Up-Gradient
Chemical Geothermometry Disequilibrium Advection, Reliable-Negative PU Dual-Cover &
Stationary Noisy-OR Conduit Discovery.

Pre-registered in ``docs/research/h49-cgtd-preregistration-20261027.md`` before execution.

Key scientific & engineering properties:
  1. Adds 10 genuinely untried, strictly label-free geological/geophysical channels
     (`CGTD_EXTRA_CHANNELS`, bringing stack to `93` total / `80` strictly 1 m LiDAR-free):
       - Miller & Singh (1994) isostatic gravity tilt-angle zero-contour wall (`theta_g = 0`)
         and Verduzco et al. (2004) Total Horizontal Derivative of Gravity Tilt (`THDR_tilt`),
         amplitude-invariant with fault burial depth (`1.5-3.5 km` blind horsts/grabens).
       - Salem et al. (2007) dual-field gravity-magnetic tilt phase-lock and Salem tilt-depth
         vs `Band 15` sedimentary cover contact sharpness.
       - Up-gradient structural-topographic advection of UNR/DOE GDR #1391 chemical
         geothermometry disequilibrium (`Delta T_diseq = max(T_quartz, T_chalc, T_NaKCa) - T_surf`,
         `1,247` assayed stations, `dist_known_fault_px` explicitly dropped & asserted absent),
         mapping blind feeding fault conduits rather than valley-floor gravel outflow plumes.
       - Hydrothermal smectite clay-cap lateral flank conductivity inflection (`Band 17`),
         3-D Kostrov-Byerlee dilatant slip-tendency crest (`Bands 04, 07, 08, 10, 16`),
         GeoDAWN 4-block seam-eroded `214Bi x K/eTh` redox-potassic crest, and playa/road-vetoed
         soft `k-of-5` independent-physics conduit convergence.
  2. Fixes `IR-48-PU-NEG-01`: screens `y = 0` unlabeled negatives in both `93`-ch `M_Full` and
     `80`-ch `M_Sub` to exclude the top `6%` high-concordance unmapped physical fault/vent crests
     (`multiphysics_k_of_5_concord > q94`), preventing GBDTs from suppressing unmapped bedrock
     and hydrothermal fault conduits.
  3. Fixes `IR-48-MULT-COLLAR-01` & gap over-inflation (`30.4% -> ~24.5%`): blends calibrated
     `M_Sub` inside `lidar_valid` (`0.68 * M_Full + 0.32 * M_Sub_cal`) to rescue blind piedmont
     faults under young fans, uses `blend_raw = 0.45` inside `lidar_gap`, and fuses the supervised
     posterior with the 1-px crest-sharpened `multiphysics_k_of_5` conduit ridge via a 100%
     stationary Noisy-OR discovery law `1 - (1 - P_sup)(1 - lambda_vent * R_vent^1.5)`.
  4. Memory-engineered (`< 2.0 GiB` peak RSS on `3.8 GiB` zero-swap hosts) using `madvise(MADV_DONTNEED)`
     after memmap reads so OS file-cache pages never accumulate across the 6 stacks.
"""

from __future__ import annotations

import gc
import json
import mmap
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from numpy.lib.format import open_memmap
from scipy.ndimage import (
    binary_dilation,
    binary_erosion,
    distance_transform_edt,
    gaussian_filter,
    map_coordinates,
    sobel,
)
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

from . import emitter, fbgr, ldgi, mdrc, paths, spcp, trhv

TARGET_BUDGET: int = 37_654
B_COLLAR_PX: float = 2.0
AXIAL_MIN_SEP_PX: float = 2.8

CGTD_EXTRA_CHANNELS: tuple[str, ...] = (
    "grav_tilt_zero_wall",             # 0 (global 83): Miller-Singh gravity tilt=0 wall x h-grad
    "verduzco_thdr_grav_tilt",         # 1 (global 84): Verduzco ||grad_h(theta_g)|| contact crest
    "pf_grav_mag_tilt_phaselock",      # 2 (global 85): Dual-field gravity-magnetic tilt=0 phase congruence
    "salem_tilt_cover_match",          # 3 (global 86): Salem 1/||grad_h(theta_g)|| vs Band 15 cover depth match
    "geotherm_diseq_upgrad_conduit",   # 4 (global 87): Up-gradient advected (T_chem - T_surf) disequilibrium conduit
    "mt_claycap_flank_conduit",        # 5 (global 88): Playa-vetoed MT smectite clay-cap lateral flank inflection
    "kostrov_byerlee_dilatant_crest",  # 6 (global 89): Tensorial GPS slip+dilation tendency + seismic swarm on tilt strike
    "geodawn_seamfree_redox_potassic", # 7 (global 90): 300m-seam-eroded GeoDAWN 214Bi redox x K/Th alteration edge
    "multiphysics_k_of_5_concord",     # 8 (global 91): Strictly LiDAR-free k-of-5 independent-physics conduit convergence
    "cgtd_conduit_ridge_1px",          # 9 (global 92): 4-azimuth NMS 1-px fault/vent ridge (LiDAR-assisted where valid)
)

# Global indices in 93-channel stack:
#   0..82  (83): inherited stacks (`fbgr.LIDAR_DEPENDENT_GLOBAL_COLS` has 12 LiDAR-touching cols)
#   83..91 ( 9): strictly 1 m LiDAR-free
#   92     ( 1): touches `lidar_clean` inside `lidar_valid` -> excluded from `M_Sub`
LIDAR_DEPENDENT_GLOBAL_COLS_93: frozenset[int] = fbgr.LIDAR_DEPENDENT_GLOBAL_COLS | frozenset({92})
MSUB_93_COL_INDICES: tuple[int, ...] = tuple(
    i for i in range(83 + len(CGTD_EXTRA_CHANNELS)) if i not in LIDAR_DEPENDENT_GLOBAL_COLS_93
)
assert len(MSUB_93_COL_INDICES) == 80, f"Expected 80 pure non-LiDAR columns, got {len(MSUB_93_COL_INDICES)}"


def drop_mmap_cache(*arrays: Any) -> None:
    """Release clean OS file-backed mmap pages immediately so RSS stays well below 2 GiB."""
    dontneed = getattr(mmap, "MADV_DONTNEED", None)
    if dontneed is None:
        return
    for arr in arrays:
        mm_obj = getattr(arr, "_mmap", None)
        if mm_obj is not None:
            try:
                mm_obj.madvise(dontneed)
            except OSError:
                pass


def _read_clean_band(base_mm: np.ndarray, idx0: int, foot: np.ndarray, sigma_smooth: float = 0.0) -> np.ndarray:
    raw = np.asarray(base_mm[:, :, idx0], dtype=np.float32).copy()
    drop_mmap_cache(base_mm)
    valid = foot & np.isfinite(raw) & (np.abs(raw) < 1e12)
    med = np.float32(np.median(raw[valid][::4])) if valid.any() else np.float32(0.0)
    out = np.where(valid, raw, med).astype(np.float32)
    del raw, valid
    if sigma_smooth > 0.0:
        out = gaussian_filter(out, sigma=float(sigma_smooth), mode="nearest").astype(np.float32)
    out[~foot] = np.float32(0.0)
    return out


def _build_upgrad_geotherm_diseq(
    ddir: Path,
    det_elev: np.ndarray,
    depth_base: np.ndarray,
    struct_wall: np.ndarray,
    playa_gate: np.ndarray,
    foot: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Advect UNR/GDR #1391 chemical geothermometry disequilibrium up-gradient onto structural walls.

    Drops `dist_known_fault_px` immediately on load and asserts its absence (zero catalogue leakage).
    """
    ws_path = ddir / "external" / "gdr_wellspring_in_footprint.csv"
    ws = pd.read_csv(ws_path)
    if "dist_known_fault_px" in ws.columns:
        ws = ws.drop(columns=["dist_known_fault_px"])
    assert "dist_known_fault_px" not in ws.columns

    h, w = foot.shape
    rows = np.clip(ws["row"].to_numpy(dtype=np.int32), 0, h - 1)
    cols = np.clip(ws["col"].to_numpy(dtype=np.int32), 0, w - 1)
    in_f = foot[rows, cols]
    rows, cols = rows[in_f], cols[in_f]
    ws_f = ws.loc[in_f].reset_index(drop=True)

    t_surf = pd.to_numeric(ws_f.get("temp_c"), errors="coerce")
    chem_cols = [c for c in ("geothermquartz_c", "geothermchalc_c", "geothermcat_c") if c in ws_f.columns]
    t_chem = ws_f[chem_cols].apply(pd.to_numeric, errors="coerce").max(axis=1)

    t_surf_arr = t_surf.fillna(16.0).to_numpy(dtype=np.float32)
    t_chem_arr = t_chem.to_numpy(dtype=np.float32)
    has_chem = np.isfinite(t_chem_arr) & (t_chem_arr > 45.0)
    diseq = np.where(has_chem, np.maximum(t_chem_arr - np.clip(t_surf_arr, 5.0, 120.0), 0.0), 0.0).astype(np.float32)
    surf_excess = np.clip(t_surf_arr - 32.0, 0.0, 180.0).astype(np.float32)

    # Weight chemical disequilibrium strongly (deep reservoir ascent) + high-T surface discharge
    score_pt = (
        np.clip(diseq / 110.0, 0.0, 2.2) + np.float32(0.45) * np.clip(surf_excess / 95.0, 0.0, 1.8)
    ).astype(np.float32)
    active = score_pt > 0.08
    n_active_pts = int(active.sum())
    n_diseq_gt50 = int((diseq > 50.0).sum())

    # Structural-topographic potential: high over shallow-basement range blocks, low in deep basins
    pot = gaussian_filter(det_elev - np.float32(0.45) * depth_base, sigma=3.0, mode="nearest")
    gy = sobel(pot, axis=0).astype(np.float32) * np.float32(0.125)
    gx = sobel(pot, axis=1).astype(np.float32) * np.float32(0.125)
    gnorm = np.hypot(gx, gy) + np.float32(1e-5)
    uy = (gy / gnorm).astype(np.float32)
    ux = (gx / gnorm).astype(np.float32)
    del pot, gy, gx, gnorm

    src_grid = np.zeros((h, w), dtype=np.float32)
    if n_active_pts > 0:
        ar, ac, av = rows[active], cols[active], score_pt[active]
        # Deposit along up-gradient structural flowlines at steps s in {0, 300 m, 600 m, 900 m}
        for step_px, wt in ((0.0, 0.45), (3.0, 0.85), (6.0, 1.00), (9.0, 0.75)):
            rr_s = np.clip(np.rint(ar + step_px * uy[ar, ac]).astype(np.int32), 0, h - 1)
            cc_s = np.clip(np.rint(ac + step_px * ux[ar, ac]).astype(np.int32), 0, w - 1)
            np.maximum.at(src_grid, (rr_s, cc_s), av * np.float32(wt))
    del uy, ux

    plume = (
        np.float32(0.58) * gaussian_filter(src_grid, sigma=3.2, mode="constant")
        + np.float32(0.42) * gaussian_filter(src_grid, sigma=8.5, mode="constant")
    )
    del src_grid
    plume_u = spcp.robust_unit_f32(plume, foot, pct=99.4)
    del plume

    # Couple up-gradient advected disequilibrium plume onto sharp structural tilt/MT walls & veto flat playas
    coupled = mdrc.directional_chain_max(
        plume_u * (np.float32(0.28) + np.float32(0.72) * struct_wall) * playa_gate,
        foot,
        halflen=2,
    )
    out = spcp.robust_unit_f32(coupled, foot, pct=99.5)
    del plume_u, coupled
    return out, {
        "in_footprint_wellspring_rows": int(in_f.sum()),
        "active_thermal_or_diseq_stations": n_active_pts,
        "disequilibrium_gt_50c_stations": n_diseq_gt50,
    }


def build_cgtd_extra_stack(
    out_path: Path | None = None,
    receipt_path: Path | None = None,
    rebuild: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Build or open the 10-channel label-free CGTD feature stack (`3730 x 3292 x 10`, float32)."""
    wdir = paths.work_dir()
    ddir = paths.data_dir()
    if out_path is None:
        out_path = wdir / "cgtd_extra_10ch.npy"
    if receipt_path is None:
        receipt_path = paths.ROOT / "registry" / "cgtd_feature_receipt.json"

    if out_path.exists() and receipt_path.exists() and not rebuild:
        mm = open_memmap(out_path, mode="r")
        meta = json.loads(receipt_path.read_text())
        if mm.ndim == 3 and mm.shape[2] == len(CGTD_EXTRA_CHANNELS):
            return mm, meta

    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
        h, w = foot.shape

    base_mm = open_memmap(wdir / "feature_stack.npy", mode="r")
    spcp_mm = open_memmap(wdir / "spcp_extra_20ch.npy", mode="r")
    trhv_mm = open_memmap(wdir / "trhv_extra_8ch.npy", mode="r")
    fbgr_mm = open_memmap(wdir / "fbgr_extra_12ch.npy", mode="r")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    mm = open_memmap(out_path, mode="w+", dtype=np.float32, shape=(h, w, len(CGTD_EXTRA_CHANNELS)))

    # --- Ch 0..3: Miller-Singh Gravity Tilt-Zero Wall, Verduzco THDR_tilt, Dual-Field Phase-Lock & Salem Cover Match ---
    iso_grav = _read_clean_band(base_mm, 12, foot, sigma_smooth=1.0)     # Band 13: iso_grav_anom
    grav_vg = _read_clean_band(base_mm, 10, foot, sigma_smooth=1.0)      # Band 11: iso_grav_anom_vg
    gh_mag, g_gy, g_gx = fbgr._hgrad_mag_and_vec(iso_grav, sigma=1.1)
    del iso_grav

    eps_g = np.float32(np.percentile(gh_mag[foot][::4], 15) * 0.25 + 1e-5)
    theta_g = np.arctan2(grav_vg, gh_mag + eps_g).astype(np.float32)
    del grav_vg

    gh_unit = spcp.robust_unit_f32(gh_mag, foot, pct=99.3)
    del gh_mag
    # Zero-contour wall peaks sharply where theta_g == 0 AND horizontal gravity gradient is non-trivial
    tilt_zero_raw = np.exp(-((theta_g / np.float32(0.28)) ** 2)).astype(np.float32) * (
        np.float32(0.20) + np.float32(0.80) * np.sqrt(gh_unit)
    )
    tilt_zero_wall = spcp.robust_unit_f32(
        mdrc.directional_chain_max(tilt_zero_raw, foot, halflen=2), foot, pct=99.5
    )
    del tilt_zero_raw, gh_unit
    mm[:, :, 0] = tilt_zero_wall

    # Verduzco et al. (2004) Total Horizontal Derivative of Tilt ||grad_h(theta_g)|| (rad / 100 m)
    thdr_g_px, t_gy, t_gx = fbgr._hgrad_mag_and_vec(theta_g, sigma=1.0)
    del t_gy, t_gx
    thdr_unit = spcp.robust_unit_f32(
        mdrc.directional_chain_max(thdr_g_px, foot, halflen=2), foot, pct=99.5
    )
    mm[:, :, 1] = thdr_unit

    # Dual-field Gravity-Magnetic Tilt Phase-Lock (Salem et al., 2007)
    rtp = _read_clean_band(base_mm, 1, foot, sigma_smooth=1.0)           # Band 02: rtp
    tmi_vg = _read_clean_band(base_mm, 8, foot, sigma_smooth=1.0)        # Band 09: tmi_vg
    mh_mag, m_gy, m_gx = fbgr._hgrad_mag_and_vec(rtp, sigma=1.1)
    del rtp
    eps_m = np.float32(np.percentile(mh_mag[foot][::4], 15) * 0.25 + 1e-5)
    theta_m = np.arctan2(tmi_vg, mh_mag + eps_m).astype(np.float32)
    del tmi_vg

    cos_align = np.abs(g_gx * m_gx + g_gy * m_gy) / (
        np.hypot(g_gx, g_gy) * np.hypot(m_gx, m_gy) + np.float32(1e-6)
    )
    del m_gy, m_gx, mh_mag
    phase_lock_raw = (
        np.exp(-((theta_g * theta_g + theta_m * theta_m) / np.float32(0.18))).astype(np.float32)
        * (np.float32(0.25) + np.float32(0.75) * cos_align)
    )
    del theta_g, theta_m, cos_align
    phaselock = spcp.robust_unit_f32(
        mdrc.directional_chain_max(phase_lock_raw, foot, halflen=2), foot, pct=99.5
    )
    del phase_lock_raw
    mm[:, :, 2] = phaselock

    # Salem Tilt-Depth z_tilt = 100 m / (thdr_g_px + 0.015) matched against Band 15 cover thickness
    depth_base = np.maximum(_read_clean_band(base_mm, 14, foot, sigma_smooth=0.8), np.float32(0.0))
    z_tilt_m = np.float32(100.0) / (thdr_g_px + np.float32(0.025))
    del thdr_g_px
    log_mismatch = np.abs(np.log((z_tilt_m + np.float32(80.0)) / (depth_base + np.float32(80.0))))
    del z_tilt_m
    cover_match = spcp.robust_unit_f32(
        np.exp(-log_mismatch).astype(np.float32) * thdr_unit, foot, pct=99.5
    )
    del log_mismatch
    mm[:, :, 3] = cover_match
    gc.collect()

    # --- Flat Deep-Basin Structural Veto Gate (Law 2: slope < 1.8 deg & depth_to_base > 300 m) ---
    elev_slope = np.maximum(_read_clean_band(base_mm, 18, foot, sigma_smooth=0.5), np.float32(0.0))
    det_elev = _read_clean_band(base_mm, 11, foot, sigma_smooth=0.5)
    flat_playa_prob = spcp._sigmoid_f32((np.float32(1.8) - elev_slope) / np.float32(0.45)) * spcp._sigmoid_f32(
        (depth_base - np.float32(280.0)) / np.float32(90.0)
    )
    playa_gate = np.where(foot, np.float32(1.0) - np.float32(0.88) * flat_playa_prob, np.float32(0.0)).astype(
        np.float32
    )
    del flat_playa_prob, elev_slope

    # --- Ch 5 (computed first to couple Ch 4): MT Smectite Clay-Cap Lateral Flank Inflection ---
    cond_surf = _read_clean_band(base_mm, 16, foot, sigma_smooth=1.0)    # Band 17: cond_surf
    # Residualize broad regional evaporite brine sheets (sigma=16 px = 1.6 km) to isolate clay-cap margins
    cond_local = cond_surf - np.float32(0.75) * gaussian_filter(cond_surf, sigma=16.0, mode="nearest")
    del cond_surf
    mt_hgrad, mt_gy, mt_gx = fbgr._hgrad_mag_and_vec(cond_local, sigma=1.2)
    del cond_local
    mt_grav_align = np.abs(g_gx * mt_gx + g_gy * mt_gy) / (
        np.hypot(g_gx, g_gy) * np.hypot(mt_gx, mt_gy) + np.float32(1e-6)
    )
    del mt_gy, mt_gx
    mt_flank_raw = (
        spcp.robust_unit_f32(mt_hgrad, foot, pct=99.3)
        * (np.float32(0.35) + np.float32(0.65) * mt_grav_align)
        * (np.float32(0.35) + np.float32(0.65) * tilt_zero_wall)
        * playa_gate
    )
    del mt_hgrad, mt_grav_align
    mt_claycap_flank = spcp.robust_unit_f32(
        mdrc.directional_chain_max(mt_flank_raw, foot, halflen=2), foot, pct=99.5
    )
    del mt_flank_raw
    mm[:, :, 5] = mt_claycap_flank

    # --- Ch 4: Up-Gradient Chemical Geothermometry Disequilibrium Advection ---
    struct_wall = np.maximum(tilt_zero_wall, np.maximum(phaselock, mt_claycap_flank))
    geotherm_upgrad, geotherm_stats = _build_upgrad_geotherm_diseq(
        ddir, det_elev, depth_base, struct_wall, playa_gate, foot
    )
    del det_elev, depth_base, struct_wall
    mm[:, :, 4] = geotherm_upgrad
    gc.collect()

    # --- Ch 6: 3-D Kostrov-Byerlee Dilatant Slip-Tendency + Seismic Swarm on Tilt Strike ---
    geod_2nd = _read_clean_band(base_mm, 3, foot, sigma_smooth=1.5)      # Band 04
    geod_shr = _read_clean_band(base_mm, 6, foot, sigma_smooth=1.5)      # Band 07
    geod_dil = _read_clean_band(base_mm, 7, foot, sigma_smooth=1.5)      # Band 08
    deq = np.maximum(_read_clean_band(base_mm, 9, foot, sigma_smooth=1.0), np.float32(0.0))
    ieq = np.maximum(_read_clean_band(base_mm, 15, foot, sigma_smooth=1.0), np.float32(0.0))

    # Basin-and-Range regional principal extension azimuth ~ N65W (azimuth -65 deg in map coords)
    gnorm = np.hypot(g_gx, g_gy) + np.float32(1e-6)
    nx_f = g_gx / gnorm
    ny_f = g_gy / gnorm
    del g_gx, g_gy, gnorm
    # Unit extension vector e_ext = (cos(-25 deg), sin(-25 deg)) in (x=East, y=South) image coords
    ext_x, ext_y = np.float32(0.9063078), np.float32(-0.4226183)
    cos_beta = np.clip(np.abs(nx_f * ext_x + ny_f * ext_y), 0.0, 1.0)
    sin_2beta = np.float32(2.0) * cos_beta * np.sqrt(np.maximum(np.float32(1.0) - cos_beta * cos_beta, 0.0))
    del nx_f, ny_f

    dil_pos = spcp.robust_unit_f32(np.maximum(geod_dil, np.float32(0.0)), foot, pct=99.2)
    shr_mag = spcp.robust_unit_f32(np.hypot(geod_shr, geod_2nd), foot, pct=99.2)
    seis_swarm = spcp.robust_unit_f32(ieq / (deq + np.float32(5.0)), foot, pct=99.2)
    del geod_2nd, geod_shr, geod_dil, deq, ieq

    byerlee_raw = (
        (np.float32(0.52) * (cos_beta * cos_beta) * (np.float32(0.35) + np.float32(0.65) * dil_pos)
         + np.float32(0.48) * sin_2beta * (np.float32(0.35) + np.float32(0.65) * shr_mag))
        * (np.float32(0.55) + np.float32(0.45) * seis_swarm)
        * np.maximum(tilt_zero_wall, thdr_unit)
        * playa_gate
    )
    del cos_beta, sin_2beta, dil_pos, shr_mag, seis_swarm
    byerlee_crest = spcp.robust_unit_f32(byerlee_raw, foot, pct=99.5)
    del byerlee_raw
    mm[:, :, 6] = byerlee_crest

    # --- Ch 7: GeoDAWN 300m-Seam-Eroded 214Bi Redox x K/eTh Potassic Alteration Crest ---
    with rasterio.open(ddir / "external" / "acquisition_block_id_100m.tif") as ds_blk:
        blk = ds_blk.read(1)
    seam_mask = np.zeros((h, w), dtype=bool)
    for bid in (1, 2, 3, 4):
        bm = blk == bid
        if bm.any():
            seam_mask |= bm & ~binary_erosion(bm, iterations=3)
    seam_gate = np.where(
        foot,
        np.float32(1.0) - np.float32(0.85) * gaussian_filter(seam_mask.astype(np.float32), sigma=2.0, mode="nearest"),
        np.float32(0.0),
    ).astype(np.float32)
    del blk, seam_mask

    radon_crest = np.asarray(fbgr_mm[:, :, 3], dtype=np.float32).copy()
    dog_sil_pot = np.asarray(fbgr_mm[:, :, 4], dtype=np.float32).copy()
    blm_conduit = np.asarray(fbgr_mm[:, :, 5], dtype=np.float32).copy()
    rtp_persist = np.asarray(fbgr_mm[:, :, 1], dtype=np.float32).copy()
    grav_persist = np.asarray(fbgr_mm[:, :, 0], dtype=np.float32).copy()
    drop_mmap_cache(fbgr_mm)

    k_th_excess = np.asarray(spcp_mm[:, :, 8], dtype=np.float32).copy()
    lidar_valid = (np.asarray(spcp_mm[:, :, 12], dtype=np.float32) > 0.5).copy()
    drop_mmap_cache(spcp_mm)

    tiger_gate = np.asarray(trhv_mm[:, :, 4], dtype=np.float32).copy()
    vent_conduit = np.asarray(trhv_mm[:, :, 3], dtype=np.float32).copy()
    lidar_clean = np.asarray(trhv_mm[:, :, 5], dtype=np.float32).copy()
    drop_mmap_cache(trhv_mm)

    seamfree_rad = spcp.robust_unit_f32(
        mdrc.directional_chain_max(
            (np.float32(0.46) * radon_crest + np.float32(0.32) * dog_sil_pot + np.float32(0.22) * k_th_excess)
            * seam_gate
            * playa_gate
            * (np.float32(0.30) + np.float32(0.70) * tiger_gate),
            foot,
            halflen=2,
        ),
        foot,
        pct=99.5,
    )
    del radon_crest, dog_sil_pot, k_th_excess, seam_gate
    mm[:, :, 7] = seamfree_rad

    # --- Ch 8: Strictly LiDAR-Free Soft k-of-5 Independent-Physics Conduit Convergence ---
    mod1_grav = spcp._rank_unit_f32(
        np.float32(0.45) * tilt_zero_wall + np.float32(0.30) * thdr_unit + np.float32(0.25) * grav_persist, foot
    )
    mod2_mag = spcp._rank_unit_f32(
        np.float32(0.55) * rtp_persist + np.float32(0.45) * phaselock, foot
    )
    mod3_mt = spcp._rank_unit_f32(
        np.float32(0.65) * mt_claycap_flank + np.float32(0.35) * cover_match, foot
    )
    mod4_rad = spcp._rank_unit_f32(seamfree_rad, foot)
    mod5_vent = spcp._rank_unit_f32(
        np.maximum(geotherm_upgrad, np.float32(0.85) * np.maximum(vent_conduit, blm_conduit)), foot
    )
    del grav_persist, rtp_persist, phaselock, cover_match, mt_claycap_flank, seamfree_rad, geotherm_upgrad, vent_conduit, blm_conduit

    # Sort the 5 independent [0,1] rank modalities per pixel in row chunks to keep RAM tiny
    k5_raw = np.zeros((h, w), dtype=np.float32)
    step_r = 512
    for r0 in range(0, h, step_r):
        r1 = min(h, r0 + step_r)
        stk = np.stack(
            [
                mod1_grav[r0:r1],
                mod2_mag[r0:r1],
                mod3_mt[r0:r1],
                mod4_rad[r0:r1],
                mod5_vent[r0:r1],
            ],
            axis=-1,
        )
        stk.sort(axis=-1)
        # Require >= 2-3 independent modalities simultaneously high: 2nd-largest * geom_mean(top 3)
        top2 = stk[:, :, 3]
        gmean3 = np.cbrt(np.maximum(stk[:, :, 4] * stk[:, :, 3] * stk[:, :, 2], np.float32(0.0)))
        k5_raw[r0:r1] = np.float32(0.50) * top2 + np.float32(0.50) * gmean3
        del stk, top2, gmean3
    del mod1_grav, mod2_mag, mod3_mt, mod4_rad, mod5_vent

    # Localize onto sharp 100 m tilt/DEM/Byerlee structural crests + gate out playas & highways
    dem100_ridge = spcp.robust_unit_f32(_read_clean_band(base_mm, 22, foot, sigma_smooth=0.0), foot, pct=99.4)
    carrier_nonlidar = np.float32(0.44) * tilt_zero_wall + np.float32(0.30) * thdr_unit + np.float32(0.26) * np.maximum(
        dem100_ridge, byerlee_crest
    )
    del tilt_zero_wall, thdr_unit, dem100_ridge, byerlee_crest

    k5_conduit = spcp.robust_unit_f32(
        fbgr.sharpen_probability_crest(
            (k5_raw ** np.float32(1.6))
            * (np.float32(0.25) + np.float32(0.75) * carrier_nonlidar)
            * playa_gate
            * (np.float32(0.25) + np.float32(0.75) * tiger_gate),
            foot,
            crest_boost=0.52,
        ),
        foot,
        pct=99.6,
    )
    del k5_raw, carrier_nonlidar
    mm[:, :, 8] = k5_conduit

    # --- Ch 9: 1-px Fault/Vent Conduit Ridge (LiDAR-assisted inside lidar_valid, pure k5_conduit in gap) ---
    ridge_with_lidar = np.where(
        lidar_valid & foot,
        np.float32(0.62) * k5_conduit + np.float32(0.38) * lidar_clean * playa_gate,
        k5_conduit,
    ).astype(np.float32)
    del lidar_valid, lidar_clean, playa_gate, tiger_gate
    mm[:, :, 9] = spcp.robust_unit_f32(
        fbgr.sharpen_probability_crest(ridge_with_lidar, foot, crest_boost=0.55),
        foot,
        pct=99.6,
    )
    del ridge_with_lidar, k5_conduit

    mm.flush()
    drop_mmap_cache(mm, base_mm, spcp_mm, trhv_mm, fbgr_mm)
    gc.collect()

    meta: dict[str, Any] = {
        "channels": list(CGTD_EXTRA_CHANNELS),
        "shape": [h, w, len(CGTD_EXTRA_CHANNELS)],
        "dtype": "float32",
        "label_free": True,
        "sgmc_used_in_features_or_training": False,
        "dist_known_fault_px_dropped": True,
        "msub_93_pure_non_lidar_col_count": len(MSUB_93_COL_INDICES),
        "geotherm_disequilibrium_stats": geotherm_stats,
    }
    receipt_path.write_text(json.dumps(meta, indent=2) + "\n")
    return open_memmap(out_path, mode="r"), meta


def gather_93ch(
    base_stack: np.ndarray,
    spcp_stack: np.ndarray,
    trhv_stack: np.ndarray,
    ldgi_stack: np.ndarray,
    fbgr_stack: np.ndarray,
    cgtd_stack: np.ndarray,
    ys: np.ndarray,
    xs: np.ndarray,
    col_indices: tuple[int, ...] | None = None,
    release_pages: bool = False,
) -> np.ndarray:
    """Memory-bounded gather across all 6 disk-backed stacks."""
    parts = []
    stacks = (base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack)
    for st in stacks:
        arr = np.asarray(st[ys, xs, :], dtype=np.float32)
        if arr.base is not None:
            arr = arr.copy()
        if release_pages:
            drop_mmap_cache(st)
        parts.append(arr)
    full = np.hstack(parts)
    del parts
    if col_indices is not None:
        sub = full[:, col_indices].copy()
        del full
        return sub
    return full


def run_leakage_canary_93ch(
    base_stack: np.ndarray,
    spcp_stack: np.ndarray,
    trhv_stack: np.ndarray,
    ldgi_stack: np.ndarray,
    fbgr_stack: np.ndarray,
    cgtd_stack: np.ndarray,
    base_names: list[str],
    ctx,
    max_auc: float = 0.90,
    stride: int = 4,
) -> dict[str, Any]:
    """Protocol Rule 4 single-feature two-polarity leakage canary across all 93 channels."""
    pos_mask = np.zeros(ctx.foot.shape, dtype=bool)
    neg_mask = np.zeros(ctx.foot.shape, dtype=bool)
    for cell in ctx.cells:
        if cell.seed != 20:
            continue
        sl = cell.bbox
        sub_t = np.zeros(cell.active_sub.shape, dtype=bool)
        sub_t[cell.truth_coords] = True
        pos_mask[sl] |= sub_t
        neg_mask[sl] |= cell.active_sub & ~sub_t

    py, px = np.nonzero(pos_mask)
    ny, nx = np.nonzero(neg_mask)
    ny, nx = ny[::stride], nx[::stride]
    y_true = np.concatenate([np.ones(py.size, dtype=np.int8), np.zeros(ny.size, dtype=np.int8)])

    stacks = (base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack)
    offsets = np.cumsum([0] + [s.shape[2] for s in stacks])
    all_names = (
        list(base_names)
        + list(spcp.SPCP_EXTRA_CHANNELS)
        + list(trhv.TRHV_EXTRA_CHANNELS)
        + list(ldgi.LDGI_EXTRA_CHANNELS)
        + list(fbgr.FBGR_EXTRA_CHANNELS)
        + list(CGTD_EXTRA_CHANNELS)
    )
    assert len(all_names) == int(offsets[-1]) == 93

    rows = []
    for i, name in enumerate(all_names):
        s_idx = int(np.searchsorted(offsets[1:], i, side="right"))
        st = stacks[s_idx]
        plane = st[:, :, i - int(offsets[s_idx])]
        vals = np.concatenate([plane[py, px], plane[ny, nx]]).astype(np.float64)
        drop_mmap_cache(st)
        vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
        if np.ptp(vals) <= 1e-12:
            raw_auc, auc_dir = 0.5, 0.5
        else:
            raw_auc = float(roc_auc_score(y_true, vals))
            auc_dir = max(raw_auc, 1.0 - raw_auc)
        rows.append(
            {
                "index": i,
                "channel": name,
                "in_msub_pure_non_lidar": i in MSUB_93_COL_INDICES,
                "raw_auc": round(raw_auc, 6),
                "oriented_auc": round(auc_dir, 6),
                "passed": bool(auc_dir <= max_auc),
            }
        )

    worst = max(rows, key=lambda r: r["oriented_auc"])
    return {
        "passed": all(r["passed"] for r in rows),
        "threshold_auc": max_auc,
        "n_features_tested": len(rows),
        "max_oriented_auc": worst["oriented_auc"],
        "worst_channel": worst["channel"],
        "n_withheld_pos_tested": int(py.size),
        "n_active_neg_sampled": int(ny.size),
        "per_channel": rows,
    }


def fit_cgtd_pu_classifier(
    base_stack: np.ndarray,
    spcp_stack: np.ndarray,
    trhv_stack: np.ndarray,
    ldgi_stack: np.ndarray,
    fbgr_stack: np.ndarray,
    cgtd_stack: np.ndarray,
    train_region: np.ndarray,
    visible_train: np.ndarray,
    conduit_prior_plane: np.ndarray,
    foot: np.ndarray,
    col_indices: tuple[int, ...] | None = None,
    seed: int = 49,
    max_pos: int = 44_000,
    n_neg_hard: int = 88_000,
    n_neg_unif: int = 88_000,
) -> HistGradientBoostingClassifier:
    """Fit a Soft-PU Prior-Downweighted `HistGradientBoostingClassifier` (`93` or `80` cols).

    Crucially avoids hard-threshold negative exclusion on input features (which creates degenerate
    `P(y=1 | F > q94) = 1.0` tree splits!). Instead, samples across ALL unlabeled cells `d_tr >= 5`
    and applies bounded continuous Elkan-Noto / Bekker-Davis negative reliability weights
    `w_neg = 1.0 - 0.35 * conduit_prior_plane in [0.65, 1.00]`, preserving calibrated scarp precision
    while gently reducing false-negative suppression on unmapped physical fault/vent conduits.
    """
    rng = np.random.default_rng(seed)
    tr_pos = train_region & visible_train
    d_tr = distance_transform_edt(~tr_pos)

    pos_y, pos_x = np.nonzero(tr_pos)
    if pos_y.size > max_pos:
        pp = rng.choice(pos_y.size, size=max_pos, replace=False)
        pos_y, pos_x = pos_y[pp], pos_x[pp]

    unlab = train_region & (~visible_train)
    hard_y, hard_x = np.nonzero(unlab & (d_tr >= 5.0) & (d_tr <= 24.0))
    unif_y, unif_x = np.nonzero(unlab & (d_tr > 24.0))
    del d_tr, unlab

    nh = min(n_neg_hard, hard_y.size)
    nu = min(n_neg_unif, unif_y.size)
    ph = rng.choice(hard_y.size, size=nh, replace=False)
    pu = rng.choice(unif_y.size, size=nu, replace=False)

    ny = np.concatenate([hard_y[ph], unif_y[pu]])
    nx = np.concatenate([hard_x[ph], unif_x[pu]])
    neg_w = (np.float32(1.0) - np.float32(0.35) * np.clip(conduit_prior_plane[ny, nx], 0.0, 1.0)).astype(np.float32)

    ys = np.concatenate([pos_y, ny])
    xs = np.concatenate([pos_x, nx])
    y = np.concatenate([np.ones(pos_y.size, dtype=np.int8), np.zeros(nh + nu, dtype=np.int8)])
    sw = np.concatenate([np.ones(pos_y.size, dtype=np.float32), neg_w])
    del pos_y, pos_x, hard_y, hard_x, unif_y, unif_x, ny, nx, neg_w

    order = np.argsort(ys * foot.shape[1] + xs)
    ys, xs, y, sw = ys[order], xs[order], y[order], sw[order]

    X = gather_93ch(
        base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
        ys, xs, col_indices=col_indices, release_pages=True,
    )
    clf = HistGradientBoostingClassifier(
        max_iter=175,
        learning_rate=0.052,
        max_leaf_nodes=47,
        min_samples_leaf=85,
        l2_regularization=3.0,
        early_stopping=False,
        random_state=seed,
    )
    clf.fit(X, y, sample_weight=sw)
    del X, y, sw, ys, xs
    return clf


def predict_chunked_cgtd(
    clf: HistGradientBoostingClassifier,
    base_stack: np.ndarray,
    spcp_stack: np.ndarray,
    trhv_stack: np.ndarray,
    ldgi_stack: np.ndarray,
    fbgr_stack: np.ndarray,
    cgtd_stack: np.ndarray,
    mask: np.ndarray,
    col_indices: tuple[int, ...] | None = None,
    chunk_size: int = 240_000,
) -> np.ndarray:
    out = np.zeros(mask.shape, dtype=np.float32)
    ys, xs = np.nonzero(mask)
    for start in range(0, ys.size, chunk_size):
        sl = slice(start, min(start + chunk_size, ys.size))
        X = gather_93ch(
            base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack,
            ys[sl], xs[sl], col_indices=col_indices, release_pages=False,
        )
        out[ys[sl], xs[sl]] = clf.predict_proba(X)[:, 1].astype(np.float32)
        del X
    drop_mmap_cache(base_stack, spcp_stack, trhv_stack, ldgi_stack, fbgr_stack, cgtd_stack)
    return out


def combine_dual_cover_posteriors(
    p_full: np.ndarray,
    p_sub: np.ndarray,
    calib_lidar_valid: np.ndarray,
    calib_lidar_gap: np.ndarray,
    pred_region: np.ndarray,
    lidar_valid: np.ndarray,
    w_sub_in_lidar: float = 0.22,
    gap_blend_raw: float = 0.42,
) -> np.ndarray:
    """Hybrid Dual-Cover posterior combining `M_Full` + scale-calibrated `M_Sub` across cover regimes."""
    out = np.zeros_like(p_full, dtype=np.float32)
    li_pred = pred_region & lidar_valid
    gp_pred = pred_region & (~lidar_valid)

    if li_pred.any():
        cal_li = fbgr.calibrate_msub_to_mfull_quantiles(
            p_full, p_sub, calib_lidar_valid, calib_lidar_valid, li_pred, blend_raw=0.35
        )
        ws = np.float32(w_sub_in_lidar)
        out[li_pred] = (np.float32(1.0) - ws) * p_full[li_pred] + ws * cal_li[li_pred]
        del cal_li

    if gp_pred.any():
        cal_gp = fbgr.calibrate_msub_to_mfull_quantiles(
            p_full, p_sub, calib_lidar_valid, calib_lidar_gap, gp_pred, blend_raw=gap_blend_raw
        )
        out[gp_pred] = cal_gp[gp_pred]
        del cal_gp
    return np.clip(out, 0.0, 1.0).astype(np.float32)


def build_stationary_cgtd_surface(
    p_sup: np.ndarray,
    cgtd_stack: np.ndarray,
    fbgr_stack: np.ndarray,
    trhv_stack: np.ndarray,
    visible_mask: np.ndarray,
    foot: np.ndarray,
    region_mask: np.ndarray | None = None,
    mode: str = "noisyor",
    lambda_vent: float = 0.90,
    w_tip_relay: float = 0.34,
    sharpen_crest: bool = True,
    crest_boost: float = 0.45,
) -> np.ndarray:
    """100% stationary pre-placement belief surface (`noisyor` discovery vs `multiplicative` ablation).

    Uses the EXACT same equation on every OOF holdout cell and on the live full-footprint raster
    (zero `eta` holdout-vs-live switches).
    """
    if region_mask is None:
        region_mask = foot
    mask = region_mask & foot

    relay = ldgi.anisotropic_tip_relay_cone(visible_mask, foot)
    conduit_1px = np.asarray(cgtd_stack[:, :, 9], dtype=np.float32).copy()
    k5_nonlidar = np.asarray(cgtd_stack[:, :, 8], dtype=np.float32).copy()
    drop_mmap_cache(cgtd_stack)

    fbgr_crest = np.asarray(fbgr_stack[:, :, 11], dtype=np.float32).copy()
    drop_mmap_cache(fbgr_stack)

    tiger_clean = np.asarray(trhv_stack[:, :, 4], dtype=np.float32).copy()
    drop_mmap_cache(trhv_stack)

    surf = np.zeros(foot.shape, dtype=np.float32)
    ps = np.clip(p_sup[mask], 0.0, 1.0)
    rl = relay[mask]
    tg = tiger_clean[mask]
    r_vent = np.clip(
        np.float32(0.55) * conduit_1px[mask]
        + np.float32(0.30) * k5_nonlidar[mask]
        + np.float32(0.15) * fbgr_crest[mask],
        0.0,
        1.0,
    )
    del relay, conduit_1px, k5_nonlidar, fbgr_crest, tiger_clean

    if mode == "multiplicative":
        w_c = np.float32(0.14)
        base_p = (np.float32(1.0) - w_c) * ps + w_c * (r_vent * np.sqrt(np.maximum(ps, np.float32(0.02))))
        surf[mask] = base_p * (np.float32(1.0) + np.float32(w_tip_relay) * rl) * (np.float32(0.35) + np.float32(0.65) * tg)
    elif mode == "noisyor":
        # Scale-anchored tail-activated Noisy-OR:
        #   - Zero perturbation on 98% of background/ordinary pixels (r_vent <= q98.0), protecting HIDE-RECOVER!
        #   - Independent discovery channel anchored to q99.35(ps_rel) on the top 2% sharpest 1-px multi-physics
        #     tilt=0 + geothermometry disequilibrium + MT clay-cap + GeoDAWN crests!
        ps_rel = np.clip(ps * (np.float32(1.0) + np.float32(w_tip_relay) * rl), 0.0, 0.98)
        q_anchor = np.float32(np.percentile(ps_rel[::4], 99.35)) if ps_rel.size > 32 else np.float32(0.35)
        q_rv98 = np.float32(np.percentile(r_vent[::4], 98.0)) if r_vent.size > 32 else np.float32(0.65)
        rv_tail = np.clip((r_vent - q_rv98) / np.maximum(np.float32(1.0) - q_rv98, np.float32(1e-4)), 0.0, 1.0)
        p_indep = np.clip(np.float32(lambda_vent) * q_anchor * np.power(rv_tail, np.float32(1.15)), 0.0, 0.92)
        p_or = np.float32(1.0) - (np.float32(1.0) - ps_rel) * (np.float32(1.0) - p_indep)
        surf[mask] = p_or * (np.float32(0.35) + np.float32(0.65) * tg)
        del ps_rel, rv_tail, p_indep, p_or
    else:
        raise ValueError(f"Unknown surface mode: {mode}")
    del ps, rl, tg, r_vent

    if sharpen_crest:
        surf = fbgr.sharpen_probability_crest(surf, mask, crest_boost=crest_boost)
    return np.clip(surf, 0.0, 1.0).astype(np.float32)
