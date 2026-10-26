# Round 6 Preregistration (2026-10-26): Multi-Physics Geothermal Conduit, 1 m LiDAR Asymmetry & K-Metasomatism Discovery

## 0. Forensic Prerequisites Established Before Implementation

1. **Resolution of `IR-32-INSTR-03` (Why Static Catalogue-Hidden Evaluation Inverted `0.2600 -> 0.2708 -> 0.2778`):**
   - Previous runs (`H-CVF2`, `H-GEO-CONDUIT`) applied `d(labels.tif) <= 2` across the **entire** `labels.tif` raster *before* calling `evaluate_candidate_holdout`, deleting every predicted dot within `200 m` of the `20%` withheld test segments and inverting the live `B = 0 -> 1 -> 2` ladder (`Spearman = -1.000`).
   - Repairing `src/gems32/holdout.py::evaluate_hide_and_recover` (`GEMSDOE32-HIDE-RECOVER-v3.0`) so `B` exclusion and catalogue masking apply **strictly to `visible` faults per fold** restores the exact live leaderboard rank order and non-monotone `B=2` peak on `D28`:
     - `B = 0` (`D28`, owner-reported live `0.2600`): `HOLDOUT-DTI = 0.096743`
     - `B = 1` (`SOLO28`, owner-reported live `0.2708`): `HOLDOUT-DTI = 0.098977`
     - `B = 2` (`CHAMPION h33-2-b2`, owner-reported live `0.2778`): `HOLDOUT-DTI = 0.099202` (**peak**)
     - `B = 3` (over-pruned): `HOLDOUT-DTI = 0.097102`
   - Across `n = 27` cross-site live-scored submissions (`[0.0107, 0.2778]`), our orthogonal off-catalogue instrument `SGMC_cal` (`GEMSDOE32-SGMC-CAL-v3.0`, `n_withheld_positives = 169,243` SGMC fault pixels `>300 m` from `labels.tif`) achieves **Spearman `rho = +0.6755` (`p = 1.10e-4`)**.

2. **Audit Corrections to Round-5/PR-17 Artifacts:**
   - `H-GEO-4` in `registry/hypotheses.json` misidentified `training_features.tif` Band 6 (`tc`, GDAL metadata: `Tilt angle or total curvature - magnetic field derivative for edge detection`, `data_category: magnetic_data`) as radiometric potassium; true radiometric `K, Th, U, TC` reside in `external/geodawn_rad_u8.tif` (`DOI: 10.5066/P93LGLVQ`).
   - `scripts/run_conduit_pipeline.py` hardcoded `ci95_cluster_bootstrap = [pooled_dti - 0.032, pooled_dti + 0.032]` instead of computing a cluster bootstrap, and set `ok_to_download_and_submit = True` despite `SGMC_cal = 0.05114 < 0.06412` and discrete-detector overlap `0.7024 > 0.70` vs `gems10-h28-dotted-ridge`.

---

## 1. Ranked Untried Geological Hypotheses (Frozen Before Fitting)

### Rank 1 — `H38-G1`: Multi-Physics Hydrothermal–LiDAR–Subsurface Corroborated OOF Detector + Fold-Visible Tip/Relay Mechanics (`EXP-2` & `EXP-3`)
- **Specific Layers Involved:**
  - *1 m 3DEP LiDAR Micro-Geomorphology:* `external/lidar_scarp_features_u8.tif` (`ex_max`, `step_max`, `lapneg_max`, `downface_max`, `upface_max`, `cross_max`, `coh100`, `strike`, `valid` coverage indicator — SHA-256 verified on disk).
  - *GeoDAWN Radiometrics & Upward-Continued Magnetics:* `external/geodawn_rad_u8.tif` (`K`, `Th`, `U`, `TC`) + `external/geodawn_extensions_u8.tif` (`ThK`, `UK`, `UTh`, `TMI_up150`) (`DOI: 10.5066/P93LGLVQ` — SHA-256 verified on disk).
  - *GDR 1391 INGENIOUS Thermal Wells/Springs & Quaternary Volcanic Vents:* `external/gdr_wellspring_in_footprint.csv` (`temp_c`, `geothermquartz_c`, `geothermchalc_c`, `geothermcat_c` — **strictly excluding `dist_known_fault_px`**) + `external/gdr_volcanic_vents_in_footprint.csv` (`DOI: 10.15121/1881483` — SHA-256 verified on disk).
  - *Official 19-Band Geophysical/Geodetic Stack + 35-Channel Shared Structural Stack:* `.cache/gems_work/feature_stack.npy` (`mag_anom`, `rtp`, `tmi_hg`, `geod_2ndinv`, `iso_grav_anom_slope`, `tc`, `geod_shearrate`, `geod_dilaterate`, `tmi_vg`, `deq_n100a15`, `iso_grav_anom_vg`, `det_elev`, `iso_grav_anom`, `tmi`, `depth_to_base_surf`, `ieq_n100a15`, `cond_surf`, `iso_grav_anom_hg`, `det_elev_slope` + multi-scale Hessian/Laplacian/gradient transforms).
  - *Fold-Visible Structural Tip & Relay Prior (`EXP-3` only):* Derived **strictly from `visible` faults inside each fold** (never touching withheld `hidden` segments) to capture horse-tail splays and accommodation/step-over relays `300–2,500 m` from mapped tips (Faulds et al., 2011, 2021).
- **Physical Signature / Transform:**
  Out-of-fold (`4` spatially buffered quadrants, `1.5 km` collar) gradient-boosted + calibrated multi-physics probability field combining: (i) shoreline-deconfounded asymmetric 1 m LiDAR scarplets, (ii) GeoDAWN `K`-on-`Th` metasomatism + `tmi - TMI_up150` magnetite-destruction troughs, (iii) GDR 1391 multi-scale thermal upflow conditioning, and (iv) 2D gravity/magnetic cross-gradient concordance + transtensional dilation×shear strain; emitted via exact `300 m` triangular-kernel lazy-greedy submodular coverage (`src/gems32/emitter.py`) outside `B = 2` (`200 m`).
- **Why It Catches Missing Catalogue Faults:**
  Over `75%` of Great Basin geothermal systems are blind (no major range-front scarp or boiling spring; Faulds et al., 2021), hosted in quaternary alluvial piedmont step-overs, fault terminations, and synthetic/antithetic splays whose sub-meter throw (`<1 m`) vanishes on `100 m` DEMs (`det_elev`) yet registers in `1 m` 3DEP LiDAR, shallow magnetic oxidation lows, K-metasomatic alteration, and subsurface gravity/MT steps.
- **Named Non-Fault Mimic:**
  Pleistocene Lake Lahontan wave-cut shoreline terraces (contour-parallel 1 m step scarps) and Miocene volcanic flow margins; rejected by contour-orthogonality weighting, facing asymmetry, and multi-layer subsurface/thermal corroboration.
- **How It Differs from Existing `GEMSDOE32` Implementations:**
  First supervised OOF model in `GEMSDOE32` to fuse all four verified data pillars (`19 official bands` + `12-band 1 m LiDAR` + `8-band GeoDAWN` + `GDR 1391 thermal/vents`) and evaluate under leak-free visible-only Hide-and-Recover Pooled DTI.
- **Expected DTI Gain & Cost:** `+0.010` to `+0.025 HOLDOUT-DTI` over 19-band-only OOF baselines (`H-CVF2`, `H-GEO-CONDUIT`); **Low-Medium CPU cost** (`~3–6 min` on `2` vCPU; `100%` of inputs already SHA-256 verified on disk).

### Rank 2 — `H38-G2`: Lithology-Deconfounded Potassium-Metasomatism & Magnetite-Destruction Trough Detector (Tested in `EXP-2` Feature Ablation)
- **Specific Layers Involved:** `external/geodawn_rad_u8.tif` (`K`, `Th`, `U`), `external/geodawn_extensions_u8.tif` (`ThK`, `UK`, `TMI_up150`), Band 14 (`tmi`), Band 6 (`tc` magnetic tilt angle), Band 9 (`tmi_vg`), Band 17 (`cond_surf`), Band 15 (`depth_to_base_surf`).
- **Physical Signature / Transform:** Standardized `K - Th` excess (adularia/illite alteration relative to immobile `Th`) paired with short-wavelength shallow magnetic lows (`z(tmi) - z(TMI_up150)`, hydrothermal titanomagnetite -> pyrite/hematite oxidation), magnetic tilt-angle zero-crossing witness (`exp(-|tc| / sigma_tc) * |tmi_vg|`), and lateral MT smectite clay-cap gradients (`|grad(cond_surf)|`).
- **Why It Catches Missing Catalogue Faults:** Sealed or creeping geothermal fluid conduits alter host-rock mineralogy (`200–500 m` depth to surface) without building topographic fault scarps.
- **Named Non-Fault Mimic:** Unfaulted felsic ash-flow tuffs and evaporitic K-rich playas (suppressed via `Th` normalization, `depth_to_base_surf`, and linear tilt-zero-crossing coherence).
- **How It Differs from Existing `GEMSDOE32` Implementations:** Corrects `H-GEO-4`'s Band 6 misattribution and introduces the first `tmi - TMI_up150` magnetite-destruction + true GeoDAWN `K/Th` alteration channels in `GEMSDOE32`.
- **Expected DTI Gain & Cost:** `+0.004` to `+0.012 HOLDOUT-DTI` incremental contribution; **Low cost** (all data on disk).

### Rank 3 — `H38-G3`: Contour-Orthogonal Asymmetric 1 m LiDAR Piedmont Scarplet Filter (Tested in `EXP-2` Feature Ablation)
- **Specific Layers Involved:** `external/lidar_scarp_features_u8.tif` (`step_max`, `ex_max`, `downface_max`, `upface_max`, `coh100`, `strike`, `valid`), Band 12 (`det_elev`), Band 19 (`det_elev_slope`), Band 15 (`depth_to_base_surf`).
- **Physical Signature / Transform:** `step_max * coh100 * |downface_max - upface_max| / (downface_max + upface_max + eps) * |sin(strike_lidar - azimuth_contour)|`, isolating one-sided scarplets that cut obliquely across regional basin contours over alluvial cover (`depth_to_base_surf > 0`).
- **Why It Catches Missing Catalogue Faults:** Separates true low-slip intrabasin Quaternary fault splays from both Lake Lahontan paleoshorelines (contour-parallel) and incised alluvial washes / road embankments (two-sided symmetric banks), directly fixing why `H33-C` failed (`0.0241` vs random `0.0344`).
- **Named Non-Fault Mimic:** Incised ephemeral stream banks and Lake Lahontan wave-cut benches.
- **How It Differs from Existing `GEMSDOE32` Implementations:** First asymmetric (`|downface - upface|`) and contour-angle-deconfounded LiDAR scarp transform in the repository.
- **Expected DTI Gain & Cost:** `+0.005` to `+0.015 HOLDOUT-DTI` inside the `68.2%` 3DEP coverage zone; **Low cost** (all data on disk).

### Rank 4 — `H38-G4`: Spatial-Block Tversky-Loss 2D U-Net / SegFormer on Full 53-Channel Multi-Physics Stack + Submodular 300 m Kernel Packing (Hardware-Gated Next Step)
- **Specific Layers Involved:** All `53` sanitized channels from `H38-G1..G3`, replacing the official reference solution's (`drivendataorg/gems-prize-reference-solution`) random Monte Carlo patch split with buffered quadrant CV and removing Cell 12's `if np.any(y_patches)` test-tile filter (which skipped every fault-free catalogue `128x128` tile!).
- **Physical Signature / Transform:** Multi-scale `12.8 km x 12.8 km` convolutional spatial receptive field trained directly on smooth Distance-Weighted Tversky Loss (`alpha=0.2, beta=0.8`), followed by `B=2` dead-annulus exclusion and `300 m` lazy-greedy submodular dot packing.
- **Why It Catches Missing Catalogue Faults:** Learns long-range curvilinear fault continuity, en-echelon relay geometry, and basin-wide structural symmetry that pixel-wise GBDTs cannot represent — explaining the gap between pixel-wise GBDTs (`~0.22–0.28`) and the public leaderboard `#1` (`0.4413`).
- **Named Non-Fault Mimic:** Erosional range-front sinuosity without structural offset.
- **How It Differs from Existing `GEMSDOE32` Implementations:** Replaces pixel-wise `HistGradientBoostingClassifier` with 2D spatial encoder-decoder context while fixing the reference notebook's test-time negative-tile skip bug.
- **Expected DTI Gain & Cost:** `+0.03` to `+0.12` live DTI potential toward `0.3195–0.4413`; **High compute cost** (requires GPU + PyTorch/`segmentation-models-pytorch`; deferred outside this 2-vCPU CPU-only sandbox budget, documented with exact execution plan).

---

## 2. Frozen 3-Experiment Budget & Promotion Gates

Per the Parallel-Run Protocol (`<= 3` experiments, `<= 2` hours):
1. **`EXP-1` (`H38-BASE35`):** 4-quadrant spatially-blocked OOF `HistGradientBoostingClassifier` on the shared 35-channel stack (`.cache/gems_work/feature_stack.npy`), evaluated via `GEMSDOE32-HIDE-RECOVER-v3.0` (`b_visible_px=2.0`) and `GEMSDOE32-SGMC-CAL-v3.0` at matched `37,654`-dot lazy-greedy submodular budget.
2. **`EXP-2` (`H38-G1-NOPRIOR` = `H38-G1 + H38-G2 + H38-G3`, zero catalogue-derived features):** Same spatially-blocked OOF + submodular emission on the `53`-channel multi-physics stack (adding 18 label-free LiDAR asymmetry, GeoDAWN `K/Th` & `TMI - TMI_up150`, magnetic tilt zero-crossing, 2D cross-gradient, transtensional conduit, and GDR 1391 thermal/vent channels — all passing single-feature Canary `AUC <= 0.90`).
3. **`EXP-3` (`H38-G1-CORROB`):** Multi-physics OOF probability field combined with **strictly fold-visible** structural tip/relay mechanics (computed per cell from `visible` faults only; from full `labels.tif` only at final submission time) and multi-pillar corroboration gating (`LiDAR + Hydrothermal + Potential-Field`), emitted at matched `37,654` dots via lazy-greedy 300 m kernel coverage.

**Frozen Promotion Rule:**
A candidate receives `verdict = "promote"` (`OK TO DOWNLOAD AND SUBMIT`) **if and only if ALL four automated gates pass**:
- **Gate 1 (Leakage Canary):** Every single input feature has two-sided `AUC <= 0.90`.
- **Gate 2 (Holdout Superiority):** Beats the `0.2778` group champion (`h33-2-b2`) at matched mass on **both** `GEMSDOE32-HIDE-RECOVER-v3.0` (`0.099202` on visible-only `B=2`) and `GEMSDOE32-SGMC-CAL-v3.0` (`0.064123`).
- **Gate 3 (Strict Unexempted Registry Lane Gate — `src/gems32/release_gate.py`):** Full-footprint surface `|Spearman| <= 0.90` AND `<= 70%` of emitted dots within `3 px` of **every** registry raster (reported both across all 45 discrete fault-detector rasters AND unexempted including synthetic `13gems_20261001_r13-lattice-s5_v2_nan-outside.tif`).
- **Gate 4 (13-Point Automated Portal Audit — `src/gems32/submission.py`):** `EPSG:32611`, `3730 x 3292`, exact affine transform, `float32`, `0` NaNs anywhere, `100%` values in `[0.0, 1.0]`, `0` on-catalogue dots.
