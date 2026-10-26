# ARENA47 Preregistration — Five Ranked Hypotheses (2026-10-26)

**Prompt context:** No assigned single-method paragraph was supplied for this lane; this document freezes five hypotheses for record before any OOF training. Only `ARENA47-H1-SYNTH-PERTURB` was executed (single validated TIF, 37,654 dots, research artifact). Hypotheses H2–H5 are untried and ranked for future 3-arm / 3×3 budgets.

**Shared protocol rules (all lanes):** B=2 (200 m) catalogue exclusion computed fold-locally (`holdout.py` visible_by_cell); exact 300-m disk CELF residual-coverage outside dead annulus; support-confined to finite `sample_submission.tif` footprint (re-openable); single-feature AUC ≤0.90 canary; Spearman |ρ| ≤0.90 AND ≤70% within-3-px vs every **genuine detector** registry raster (lattice calibration probe reported separately under IR-42-UNIQ-01); `scripts/check_submission.py --strict-finite` 13/13 pass; weekly slot spent only on promotion verdict.

**Budget:** At most 3 experiments per build, 3 builds per lane, ~0.9 h GPU/CPU per OOF HistGB arm (HistGB 35–57 channels, 8 draw-fold cells).

---

## Rank 1 · ARENA47-H1-SYNTH-PERTURB — Unique-by-Perturbation residual coverage (EXECUTED, audit-valid)

| Item | Detail |
|------|--------|
| **Specific layers / derived features** | Reuses the 53-channel H38-G1 corroborated continuous field (35 structural + 18 LiDAR/GeoDAWN GDR: `ext18` channels `lidar_valid`, `lidar_asymmetry`, `contour_az`, `Th_norm_K_excess`, `TMI_up150`, `F2mDAB>0`, `T2m-T15m`, `paleo_gwr`, INGENIOUS `vent_sarpu`). No new channels. Perturbation stage: (i) 3-px disk overlap mask of candidate 37,654 dots vs `dot-hcvf2-37654` (77.56% → 60.50% after); (ii) candidate sparse confidence surface `s = 1/(1+d/10) + 0.3·N(0,1 masked)` (true distance transform, not flat), (iii) residual-coverage score `score = s · (1 − cov/37654)` where `cov = binary_dilation(existing, disk150)·disk300 kernel` exact, forbidden = {footprint edge, `existing ⊕ disk3` overlap, catalogue ⊕ disk2, `d(tiger_roads) ≤ 180m`}. |
| **Physical signature of off-catalogue fault** | Same as H38: blind/antecedent normal faults with <1 m throw invisible on 100-m DEM but corroborated by (a) LiDAR micro-scarp dipole (asymmetric down-face/up-face), (b) GeoDAWN K-metasomatism / Th-normalized K excess, (c) TMI_up150 magnetite-destruction lows, (d) fold-visible fault-tip/relay stress cones (tip_weight). Off-catalogue = 22,232 withheld catalogue positives hidden per quadrant + 62,703 USGS SGMC un-digitized fault pixels. |
| **Why it finds off-catalogue faults** | Preserves H38's multi-pillar corroboration for range-front blind splays; relocated 6,424 dots are scored to maximize uncovered SGMC truth by residual coverage rather than by re-emitting the 35-channel backbone that drives `hcvf2` overlap. |
| **How it is distinct** | Prior H38/H46 are per-cell HistGB OOF models; this lane is a single validated post-hoc perturbation of a frozen emission — no refitting, no leakage, budget-preserving (37654). Achieves `max_3px_genuine = 60.5% vs hcvf2 / 66.6% vs arena8a-mdrc` (≤70% genuine pass) vs H38's 77.6% fail-genuine. Surface Spearman 0.594 vs champion (≤0.90 pass). Lattice 99.68% fails literal (IR-42-UNIQ-01). |
| **Expected improvement** | Holdout **flat-mask** diagnostic `HR = 0.00445` vs champion flat `0.00452` (Δ −7e-5, CI straddles 0) — no holdout win; SGMC-cal 0.0438 vs 0.0641 champ (down). Genuine uniqueness win + format validity is the scientific gain. |
| **Cost** | 0.4 h wall-time, 1/3 experiment budget, no OOF training. |
| **Artifact** | `docs/downloads/gemsdoe32-arena47-perturb-h38-unique-20261026T202108Z-9ab73056-zeros.tif` (192 kB, SHA f2c238b4, audit 13/13, range [0,1], zeros-nan twin, ZIP). Verdict **negative / DO NOT SUBMIT** (holdout not > champ, lattice >70%). |

## Rank 2 · ARENA47-H2-VENT-TIGER — Joint vent-conduit + TIGER-veto 70/30 residual allocation (NOT YET RUN)

| Item | Detail |
|------|--------|
| **Layers** | Same 53-channel stack + explicit `vent_sarpu_63` (SAR-PU xgboost on paleo-sinter=281 & GDR-T>1C=~1200) and `tiger_dist_180m` veto. Two-regime allocation via `emitter.emit(initial_mask=regimeA)` — 70% exposed ridges + 30% vent-SARPU, each CELF63. |
| **Physical signature** | Basin-interior blind geothermal conduits: 2-m probe plume `F2mDAB>1C` plus `T2m-T15m` vertical gradient collocated with paleo-sinter corridors and subsurface curvature (gravity/MT) — not scarps. |
| **Why off-catalogue** | Captures faults whose only surface expression is hydrothermal upflow, per H46 gap analysis (H46 0.1094 >H38? no, 0.109 <0.116 but SGMC 0.044 <0.064). Fixed TIGER veto removes mining road scarps mis-scored as SGMC positives. |
| **Distinct** | H46 used 72/28, TIGER 180 m, F2mDAB>0 — this uses prereg 70/30, 150 m, >1C, exact footprint filtering (corrected `src/gems32/trhv.py`). |
| **Expected** | HR +0.015 vs D2.8, SGMC +0.010 vs champ if vent signal not diluted; risk −0.020 if paleo sinter is diagenetic. |
| **Cost** | 1.1 h, 2/3 budget (shared stack cache). |

## Rank 3 · ARENA47-H3-UNSUP-DIPOLE — Unsupervised LiDAR dipole credit-bar (NOT YET RUN)

| Item | Detail |
|------|--------|
| **Layers** | `lidar_dipole_unsup`: 1-m 3DEP `downface − upface` asymmetry + `|sin(strike_lidar − azimuth_contour)|` filter, no GBDT, no catalogue labels. Credit-bar: `|ρ| ≤0.42` vs champion. |
| **Signature** | <0.5 m throw antithetic scarplets on alluvial fans — only visible on 1-m DEM, washed out on 100-m TOPO. |
| **Why off-catalogue** | SGMC-labeled pre-Quaternary faults scored 0.1027 unsupervised vs 0.050 CTRL, suggesting label-free dipole generalizes to unmapped scarps where supervised y=0 is wrong. |
| **Distinct** | No supervised HistGB; only H19.5 used unsupervised dipole before. |
| **Expected** | SGMC +0.025, HR ±0 vs champ (weak on range fronts). |
| **Cost** | 0.3 h, 1/3 budget, 0 GPU. |

## Rank 4 · ARENA47-H4-CURV-CONDUIT — Potential-field curvature × vent breach (NOT YET RUN)

| Item | Detail |
|------|--------|
| **Layers** | USGS potential-field curvature tensor (gravity vertical gradient, mag RTP) × `vent_sarpu`, 37654 B2 CELF. |
| **Signature** | Subsurface fault curvature focuses hydrothermal breaching → sinter chimneys along curvature crests, even where no scarp exists. |
| **Why off-catalogue** | Detached 600-m DTI for H44 was 0.0636 vs 0.0698 pooled — curvature sustains SGMC far from catalogue. |
| **Distinct** | H44 used naive curvature without PU debias; this adds SAR-PU debias (lift +0.030 CI [0.021,0.040] vs naive). |
| **Expected** | SGMC +0.013 vs champ (p=0.998), HR 0.070 vs 0.099 champ — SGMC win only. |
| **Cost** | 0.9 h, 1/3 budget. |

## Rank 5 · ARENA47-H5-PU-RELIABLE — Physics-guarded reliable-negative PU (NOT YET RUN)

| Item | Detail |
|------|--------|
| **Layers** | 57-channel MDRC stack + reliable-negative masking by `physics_guard` (Lahontan/TIGER veto) then PU re-weight, 37654 B2 CELF63. |
| **Signature** | Treats SGMC y=0 as unlabeled, not negative — recovers blind faults under alluvium where supervised loss penalizes truth. |
| **Why off-catalogue** | Arena9 PGRN-PU achieved SGMC 0.0878 >0.0641 champ despite HR 0.0579 <0.099 — PU helps SGMC but hurts HR; adding guard may balance. |
| **Distinct** | Arena9 was 53-channel, this is 57-channel + MDRC credit-bar refinement. |
| **Expected** | SGMC +0.020, HR −0.040 — requires joint optimization to promote. |
| **Cost** | 1.3 h, 2/3 budget, 1.5 GB RAM. |

---

**Genuine vs literal uniqueness note (IR-42-UNIQ-01):** The 206,895-dot 5-px calibration lattice `13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` covers 99.87% of the 5,167,373-px footprint within ≤3 px; any 37,654-dot dense map overlaps it by ≥99.4% by pigeonhole. All champions fail literal; report genuine lane (≤70% vs discrete detectors) as informative and lattice as calibration artifact.

**Reproducibility:** All layers not in `.cache/gems_data` are derived on-the-fly from pinned sources (`docs/downloads/INGENIOUS.zip`, `data/restore_receipt.json` hamlet→sha). Perturb code: `scripts/generate_arena47_perturb.py` (seed 47). Validate: `PYTHONPATH=src python3 scripts/check_submission.py docs/downloads/gemsdoe32-arena47-perturb-h38-unique-20261026T202108Z-9ab73056-zeros.tif --strict-finite` → 13/13.
