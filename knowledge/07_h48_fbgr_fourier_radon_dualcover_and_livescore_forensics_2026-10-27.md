# 07 — Session H48-1-FBGR: Live-Score Forensics, Fourier-Continued Basement-Graben + GeoDAWN Radon Dual-Cover, and Bug Fixes (`2026-10-27`)

## 1. Forensics of the `2026-10-26` Live-Score Returns (`OWNER-REPORT`)

All 13 prompt-referenced rasters were verified byte-for-byte in `evidence/livescore_forensics_20261027.json`:

1. **Why `GEMSDOE27 H31-1` (`cf8e1bbef244-allfinite.tif`) scored `0.2250` (`OWNER-REPORT`):**
   - `42,000` dots (`0` on-catalogue), `52.4%` placed `> 1.5 km` from `GEMSDOE76` (`35.3%` vs `H19-5` Champion), `25.7%` inside the `24.63%` 1 m LiDAR gap, only `4.3%` in flat deep basins, and **`Clump>=3 = 0.19%`** (`cov300 = 5.86%`).
   - Proves a genuinely off-catalogue model (`< 40%` overlap with Champion) can clear `> 0.22` live when it maintains axial dot spacing (`d >= 2.8 px`) and avoids both catalogue hugging and flat-playa false positives.
2. **Why `GEMSDOE36 KPL-36` (`05c6acbb51b2-zeros.tif`) scored `0.1647` (`OWNER-REPORT`):**
   - `99.17%` 3-px duplicate of `GEMSDOE32 H38` (`23fbbb51`). Because `d = 0` greedy CELF was run on smooth 2D probability ribbons without axial crest thinning or `min_sep_px`, **`42.57%` of its `37,654` dots clumped (`Clump>=3`)**, collapsing `cov300` from `6.31%` to **`4.17%`** (`-34%` spatial footprint).
3. **Why `GEMSDOE24 GVC1` (`0.0859`), `GEMSDOE25 H66-BGHF` (`0.0742`), and `GEMSDOE28 S21` (`0.0206`) collapsed (`OWNER-REPORT`):**
   - Placed `86.0%`, `90.9%`, and `96.5%` of their dots within `<= 1.5 km` of `GEMSDOE76` (`> 15 px` off-catalogue share was only `14.0%`, `9.1%`, `3.5%` vs `54.8%` for `0.2778` and `52.4%` for `0.2250`), while spilling `10.4%–15.5%` of dots into flat deep basins (`elev < 1300 m, slope < 1.5 deg`).

## 2. Irregularities Found & Fixed in Shared `GEMSDOE32` Code

- **`IR-48-BAND14-01` (`src/gems32/ldgi.py` & `src/gems32/fbgr.py`):** Band 14 (`5km_grav`) in `test_X.tif` is shallow residual gravity, not upward-continued gravity (`r = -0.351` with `iso_grav_anom`). Fixed in `ldgi.py` and replaced in `fbgr.py` with exact 2-D Fourier harmonic upward continuation ($\hat{U}(\mathbf{k}; z) = \hat{U}(\mathbf{k}; 0)e^{-2\pi z|\mathbf{k}|}$) at $z \in \{500\text{ m}, 2,000\text{ m}\}$.
- **`IR-A48-JX-01` (`src/gems32/fbgr.py`):** Raw GeoDAWN radiometric flights have inter-block calibration steps across Blocks 1–4. Fixed by z-standardizing `K`, `eTh`, `eU`, `TC`, `U/Th`, `U/K` within each contractor polygon (`acquisition_block_id_100m.tif`, DOI `10.5066/P93LGLVQ`) before computing playa-vetoed $^{214}\text{Bi}$ (`eU - beta*eTh`) radon crests and concentric silica/potassic DoG zones.
- **`IR-48-CCAA-01` (`src/gems32/ldgi.py` & `src/gems32/fbgr.py`):** Eliminated non-stationary `eta=1.0 -> 0.55` holdout-vs-live switching; `H48-1-FBGR` uses a 100% stationary Dual-Cover OOF architecture (`83`-ch `M_Full` inside `lidar_valid` + quantile-matched `71`-ch strictly LiDAR-free `M_Sub` inside the `24.63%` 1 m LiDAR gap).
- **`IR-48-RELEASE-01`, `IR-48-EXTRA-FETCH-01`, `IR-48-TESTPIN-01`, `IR-48-WBG-SURFACE-01`:** Reconciled release manifests in `scripts/sync_submission_build.py`, added `codeload.github.com` tarball streaming fallback to `scripts/restore_data.py` & `scripts/fetch_extra_scored.py`, decoupled `tests/test_h47_ldgi.py` from live pointer drift, and classified `WBGGEMSDOE1/2` continuous `5.1M`-pixel research surfaces separately from discrete dot candidates.

## 3. `H48-1-FBGR` Controlled 3-Experiment Ablation (`evidence/h48_fbgr_run_card.json`)

- **Artifact:** `docs/downloads/gemsdoe32-h48-fbgr-dualcover-axial28-37654-20261027T180500Z-4d38a240-zeros.tif` (`SHA-256 = 4177f236b7c6a26fdf39d85f0896d1a83da745c9a36b04be7fe201a0076bf29f`, `37,654` dots, `B=2`, `min_sep_px=2.8`).
- **`HIDE-RECOVER-v3.0` (`n=22,232`):** `EXP3 = 0.115341 [0.100168, 0.130524]` vs `0.2778` Champion `0.099202` (**`+0.016217 [+0.008599, +0.024287]`, `p=1.000`**) and vs `EXP2` (`d=0` greedy `0.103264`, **`+0.012020`, `p=1.000`**).
- **Detached `>= 600 m` blind segments (`n=15,504`):** **`0.101168 [0.085002, 0.117569]`** — highest stationary score in repo history (vs Champion `0.094324`, `p=0.957`, and `H47-1 = 0.091842`).
- **`SGMC-CAL-v3.0` (`n=62,703`):** `EXP3 = 0.056798` vs `EXP2 = 0.040721` (**`+39.4%`**, `p=1.000`, reducing `Clump>=3` from `53.24% -> 0.98%` and raising `cov300` from `4.00% -> 5.89%`), trailing Champion `0.064121` by `-0.007243`.
- **Uniqueness:** `|Spearman| <= 0.6315` (`PASS`); focus-site 3-px `<= 65.94%` (`PASS`); all-org discrete `<=100k` 3-px `<= 68.82%` across `439` rasters (`PASS`); literal all-raster gate `False` (`99.78%` on `r13-lattice-s5` union). Held **`DO NOT SUBMIT`** (`verdict: "negative"`).

## 4. Next Steps to Clear `0.3195 -> 0.4437`

1. Train Regime-A exposed-bedrock OOF directly against joint `{withheld GEMSDOE76} U {off-catalogue SGMC fault contacts}` using 30 m Copernicus GLO-30 bedrock curvature (`H48-5`) so `SGMC-CAL-v3.0` exceeds `0.078` while keeping `HIDE-RECOVER-v3.0 >= 0.115` and `Detached >= 600 m >= 0.101`.
2. Add continuous sub-pixel center-of-mass ridge snapping outside `r13-lattice-s5`'s 3-px mask on uncertain blind segments if strict literal union clearance (`<= 70%` against `>100k`-dot probes) is maintained as a hard release gate.
