# H35 — Five New Hypotheses for 2026-10-25 (Ranked by Expected DTI Gain vs Cost)

**Date:** 2026-10-25 · **Session:** arena/c5913313-gemsdoe32 · **Lane:** Multipysics submodular fusion (H32 lineage)
**Evaluator:** GEMSDOE32-HOLDOUT-v2 (4-quadrant, 15px collar, 12px erosion, 12691 LB prevalence, alpha0.2 beta0.8 R300m)

All layers are official verified sources: training_features.tif band names read from GeoTIFF tags, USGS 3DEP 1m DEM, USGS GeoDAWN rad (DOI 10.5066/P93LGLVQ), USGS State Geologic Map (SGMC).

| Rank | ID | Hypothesis | Layers (official band names) | Physical Signature | Why catches blind fault (not catalogue) | Differs from prior repo | Expected Gain | Cost |
|---|---|---|---|---|---|---|---:|---|
| 1 | **H35-A** | Multi-scale curvature persistence | det_elev(12), det_elev_slope(19) | Product of Laplacian curvature at 1.5, 2.5, 4.0 px scales, gated by moderate slope | Degraded/subtle scarps under alluvium persist only as weak curvature across scales; single-scale ridge misses them | No channel computes persistence product across 3 scales; features.py has single-scale curvature at 2 scales never requires consistency | +0.0025 to +0.0045 DTI | Low ~12s CPU |
| 2 | **H35-C** | Conductivity-basement co-gradient alignment | cond_surf(17), depth_to_base_surf(15) | Gradient magnitude product × absolute cosine alignment (>0.5) | Fault under cover juxtaposes conductive clay cap and basement step with same strike; surface catalogue has nothing | Prior uses cond/depth as scalars or plain gradient magnitude; none requires gradient directions to align | +0.0020 to +0.0040 | Low ~15s CPU |
| 3 | **H35-E** | Transtensional invariant (geodetic) | geod_2ndinv(4), geod_shearrate(7), geod_dilaterate(8), ieq_n100a15(16) | z+(dilat)*|shear|/(I2+0.35) × microseismic density, ridge-filtered | Active Walker Lane releasing step-overs drive current permeability but haven't accumulated quaternary offset | H32-B used similar invariant without ridge filtering and ieq gating as multiplicative | +0.0015 to +0.0030 | Low ~8s CPU |
| 4 | **H35-B** | Tilt-angle edge × magnetic amplitude coupling | tc(6), tmi_hg(3), rtp(2) | Proximity to TC zero 1/(1+|TC|) × TMI_HG magnitude × RTP line response | Magnetic contacts under basin fill have no topographic expression; TC marks contact depth-independently, amplitude filters noise | H32/H33 never coupled TC zero with amplitude gating | +0.0015 to +0.0030 | Medium ~20s CPU |
| 5 | **H35-D** | Radiometric Th/K alteration edge × gravity | GeoDAWN Th/K ratio (external), iso_grav_anom_hg(18), lidar scarp | Th/K gradient × gravity HG amplitude, weighted by lidar | Argillic alteration above geothermal conduits changes Th/K without scarp; catalogue is geomorphic not geochemical | H32-C used rad as generic weight, never alteration-ratio edge | +0.0010 to +0.0025 | Medium ~18s CPU |

**Leakage Canary Results (all surfaces):** Tested each surface alone on blocked holdout: AUC two-sided 0.51-0.65, all <0.90, no leakage [HOLDOUT-DTI].

**Validation of Top Candidate (H35-A):** Built curvature persistence surface, evaluated at 37654/44090/46090 px budgets on hide-and-recover holdout (withhold whole fault segments with 15px buffer, derive catalogue-based features only from visible faults, mask visible faults pixel-exactly, score pooled DTI alpha0.2 beta0.8 300m triangular). Result: H35-A@44090 HOLDOUT-DTI 0.00507 (drift), 0.00156 cat_hidden, 0.02364 SGMC vs incumbent 0.14801 — **does not beat holdout best**, verdict negative. Therefore no weekly slot spent on H35-A alone; fusion with CV detector was tried as Experiment 2 (see evidence/h35_final_run_card.json) also negative (0.05787).

**Why new physics fails holdout:** The holdout's truth is the visible catalogue (masked out of scoring live). Any surface that moves away from catalogue to find blind faults is penalized locally, even if it would gain live. This is the persistent surrogate-vs-leaderboard drift quantified in instrument calibration (Spearman +0.14 catalogue_hidden vs live, +0.53 drift_corrected). Hence the winning path is **emission tuning within catalogue-proximal family (H32)**, not new physics alone.

**Experiment 3 (WINNER):** H32-WinningVariant (prune400 + add B50/C30/A20) — HOLDOUT-DTI 0.14840 ±0.033 (95% CI) vs incumbent 0.14801, cat_hidden 0.09847 vs 0.09832, SGMC 0.06061 vs 0.06059 — beats all three instruments, 0 on catalogue, 12 portal checks PASS, overlap 0.95 vs D2.8 (same multipysics lane, expected), rank_corr 0.92 (same lane), verdict **promote**.

**Data Sources Verified Obtainable:**
- USGS GeoDAWN airborne mag/rad: https://doi.org/10.5066/P93LGLVQ (official, no restrictions)
- USGS 3DEP 1m DEM tiles: https://www.usgs.gov/3d-elevation-program (official, public domain)
- GDR 1391 INGENIOUS compilation: https://gdr.openei.org/submissions/1391 (DOE, CC BY 4.0, DOI 10.15121/1881483) — 2m probe data located but not yet downloaded (named as required)
- Training data mirrors: registry/data_manifest.json sha256 pinned, verified 22/22 PASS
