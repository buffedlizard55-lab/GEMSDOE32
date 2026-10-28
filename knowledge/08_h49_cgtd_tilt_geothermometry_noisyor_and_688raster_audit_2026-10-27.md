# Knowledge Note 08 — `H49-1-CGTD` Gravity/Magnetic Tilt-Depth, Geothermometry Disequilibrium, Tail Noisy-OR & 688-Raster Cross-Org Lessons (`2026-10-27`)

## 1. What Worked Scientifically (`H49-1-CGTD`)

1. **Stationary Tail Noisy-OR (`1 - (1 - p_scarp)(1 - 0.90 * p_vent_tail)`) Broke the `H48-1` Multiplicative Veto:**
   - Under `H48-1`'s multiplicative fusion (`p_base * prior`), blind intra-graben hydrothermal faults (`p_scarp ≈ 0.03`) were suppressed below range-front scarps (`p_scarp ≈ 0.45`), holding `SGMC-CAL-v3.0` to `0.056798 < 0.064121` Champion.
   - Replacing multiplicative fusion with `H49-1`'s Stationary Tail Noisy-OR (`src/gems32/cgtd.py::compute_cgtd_tail_noisyor_surface`, active strictly in the top `12%` multi-physics blind-conduit tail + fold-local tip/relay continuation) raised **`SGMC-CAL-v3.0` (`n=62,703`) to `0.066434 [0.059875, 0.072082]`** (`+17.0%` over `H48-1`, `+0.007425` over Multiplicative `EXP1` with `P = 1.000`, beating the `0.2778` Champion `0.064121` AND `H47-1` `0.065888`) while **simultaneously beating the `0.2778` Champion on `HIDE-RECOVER-v3.0` (`0.105043 > 0.099202`)**.
2. **10 New Zero-Leakage Physics Channels (`max AUC = 0.5434 <= 0.90`):**
   - Miller & Singh (1994) gravity tilt-angle zero-contour wall (`theta_grav = atan2(g_vg, g_slope)`), Salem et al. (2007) tilt-depth & dual gravity-magnetic `tilt=0` concordance, UNR/DOE GDR `#1391` up-gradient chemical geothermometry disequilibrium (`Delta T = max(T_chal, T_qtz, T_nakca) - Temp_C`, `1,247` stations, `1,077` `> 50 °C`), BLM MLRS closed-claim epithermal vein proximity, and multi-azimuth range-front continuity breaks raised `EXP1` `SGMC-cal` by `+0.002145` before any Noisy-OR change.

## 2. Two Critical Pitfalls Discovered & Permanently Documented

1. **NEVER Apply a Hard-Threshold PU Negative Screen on an Input Feature Kept in `X`:**
   - Excluding `y = 0` pixels above `q94(k5)` while leaving `k5` in `X` makes `P_train(y=1 | k5 > q94) === 1.0`, saturating GBDT leaves across `6%` of the map (`EXP1 HR` collapsed to `0.07488`). Always use **bounded continuous Soft-PU sample weights (`w_neg in [0.65, 1.00]`)**.
2. **Stacking 10 Channels onto an 83-Channel Ancestor GBDT Preserves Intra-Repo `> 70%` Overlap (`73.33%` vs `H48-1`):**
   - Even though `H49-1` passed **100% (`570/570`) external cross-site uniqueness (`<= 67.85%`)** across all 8 sibling focus sites and 21 sibling-org repos, sharing `83/93` input channels with `GEMSDOE32` `H48-1-FBGR` kept `73.33%` intra-repo 3-px overlap on shared 1 m LiDAR scarps.
   - **Rule for `H50+`:** Build an **orthogonal compact `~28–36`-channel feature basis** (dropping redundant raw multi-scale `H38`/`H47` scarp duplicates or using a distinct model family such as regularized spline/GAM + Steger crest vectorization) AND check intra-repo `H48`/`H49` 3-px overlap on `Cell 0` before committing the 3-experiment budget.
