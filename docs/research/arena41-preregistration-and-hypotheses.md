# Arena41 — pre-registration, 5 candidate hypotheses, and promotion gates

**Date:** 2026-10-25 · **Branch:** `arena/41c41811-gemsdoe32` · **Experiment budget:** 3
(EXP1 screen · EXP2 OOF model comparison · EXP3 final build). Written *before* EXP2 is run.
Every live score below is **OWNER-REPORTED** from the standing brief unless marked
**ORGANIZER-CONFIRMED** (read from the DrivenData leaderboard page on 2026-10-25:
#1 xiaofanhu **0.4413**, #2 cfld__ 0.3916 — <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>).
The brief's "0.3195 leader" is a stale 2026-10-03 snapshot in `docs/score-ledger.csv`.

## Why the champion scored 0.2778 (measured, `evidence/arena41_forensic.json`)

`h33-h33-2-b2-…-e5eb6e7e-zeros` (37,654 dots) is **pixel-exactly** D2.8 (44,090, 0.2600)
minus every dot within 2 px of the catalogue — verified from bytes, 0 discrepancies.
It is a *mass-removal*, not a better geological field. Inverting the two controlled live
steps (0.2600 → 0.2708 → 0.2778) under the stated c=m sensitivity family, the removed
200 m shell earned **0.004–0.029 weighted credit/dot** against a break-even of
α·s = 0.2×0.2778 = **0.0556**. The catalogue proxy claims that same shell earns **0.678/dot**
and the 100 m shell **1.72/dot** — a 40–400× overstatement, because catalogue-holdout truth
*is* the catalogue while the live scorer masks catalogue pixels and scores *new* faults
(<https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>). Shell credit
(SGMC off-catalogue proxy) rises monotonically with distance from the catalogue and crosses
break-even in the 2–3 px shell (0.064/dot), which is why B=2 is the optimum and B=3 was
correctly rejected in Round 4. **Beating 0.2778 requires new *coverage* of hidden faults,
not more removal:** at the champion's operating point (T≈5,064, D≈18,230, family-midpoint),
0.3195 needs ≈ +760 weighted credit (+15%) at equal mass; 0.4413 needs ≈ +59%.

## Five candidates, ranked by expected DTI gain ÷ cost

| # | Hypothesis | Layers | Signature | Why it catches a catalogue-missing fault | Differs from this repo | Mimic (named non-fault process) |
|---|---|---|---|---|---|---|
| 1 | **PF-ONLY blind-basin detector** (THE LANE) | bands 1,2,3,5,6,9,11,13,14,15,17,18 only | HGB over HGM, FFT upward-continuation worm persistence (0/300/600 m), Hessian ridges, basement & conductivity gradients; **no DEM/LiDAR/radiometrics** | Catalogue inclusion is *caused* by surface scarp expression; DEM-trained fields learn P(catalogued), not P(fault). Buried piedmont/intra-basin faults have no scarp but offset magnetic/gravity basement | Every field here (35-ch CV GBM, H19-5, H33-A…D) is DEM/LiDAR-led; no subsurface-only ablation exists | Basement lithologic contacts, intrusion & volcanic margins — identical potential-field edges, no fault |
| 2 | Piedmont concealment-belt curvature | 12 `det_elev`, 19 `det_elev_slope`, 15 `depth_to_base_surf` | `curv_s2` crest gated to the range-front→basin slope-transition belt at intermediate basement depth | Range-front faults get *harder* to map exactly where fans prograde over them; the belt is where mapping completeness collapses | H62-4 used curvature ungated; no concealment-belt gate exists | Lahontan paleo-shorelines & alluvial-fan channel levees |
| 3 | Worm-persistence solo (label-free) | 2 `rtp` (FFT continuation), 13 `iso_grav_anom` | min of unit-HGM at 0/300/600 m continuation heights, dotted | Deep basement faults persist on upward continuation; shallow volcanic/intra-sediment edges attenuate | H33 used ridge responses at fixed scale; no continuation-persistence operator | Dykes and intrusion margins persist identically |
| 4 | Radiometric alteration × demagnetisation | GeoDAWN rad (K,Th,U,TC) + extensions (Th/K…), 2 `rtp` | unit(1/ThK) × unit(−smoothed RTP) ridge | Hydrothermal K-metasomatism + magnetite destruction tracks permeable (fault) upflow, incl. blind systems | Rad used only as one of six physics inside H33-A; never a conjunction solo | Felsic volcanics (K-rich, magnetite-poor lithology) |
| 5 | Catalogue-tip strike propagation | `labels.tif` geometry (visible only) | extend segment strikes past terminations/step-overs | Faults continue past mapped tips under cover | REJECTED for this lane: catalogue-derived (holdout leakage-prone), duplicates champion near tips (uniqueness fail); group solo tip arms scored 0.0159–0.2632 owner-reported | Continuation of a *mapped* fault the scorer already masks |

EXP1 (done, `evidence/arena41_exp1_screen_foot.json`): all solo-surface canary AUCs
0.48–0.57 (no leakage); dotted solo pooled HOLDOUT-DTI (8 cells, 22,232 withheld px):
worm-scale-persistence proxy **0.0409** > PF-edge-mean 0.0329 > rad-alt 0.0294 >
basement-step 0.0240 > curvature 0.0160. A flawed B2-eligibility variant was run first and
is retained as `arena41_exp1_screen_b2_flawed.json` (its DTI screen measured only 2–3 px
shell geometry; its AUC canaries are unaffected).

## Pre-registered promotion gates for EXP2/EXP3 (all must pass → 🟢 OK TO SUBMIT)

Evaluator: shared `gems32.holdout.evaluate_candidate_holdout` (hide 20% whole catalogue
components/quadrant, draws 20/21, 15 px collar; pooled DTI from per-cell TP/FP/FN,
α=0.2 β=0.8 R=3 px). OOF field: model for quadrant q trained only on the other three
quadrants outside a 15 px collar — every catalogue-derived quantity uses visible faults only.
Control: CTRL-SURF = identical stack **plus** DEM surface-expression channels (the ablation
control), same sampler, same emission. Champion prebuilt is *not* a fair comparator on this
instrument (it was built with the full catalogue incl. withheld segments); it is reported for
context only.

- **G1 leakage canary:** OOF field AUC ≤ 0.90 in every quadrant.
- **G2 fault reality (sanity):** PF pooled HOLDOUT-DTI > 3× the matched random-dot baseline.
- **G3 lane evidence (off-catalogue):** PF SGMC-prevalence-calibrated DTI > CTRL-SURF's at
  37,654 dots (the lane predicts DEM channels *hurt* off-catalogue transfer). Catalogue-hidden
  DTI is reported but is a *biased-against-the-lane* instrument (withheld catalogue faults are
  the surface-expressed population); PF must retain ≥70% of CTRL-SURF's catalogue-hidden pooled DTI.
- **G4 uniqueness (parallel protocol):** vs *every* distinct registry raster: sampled Spearman
  surface↔raster < 0.90, final-dot fraction within 3 px ≤ 70%, and sha256 unequal to any prior file.
- **G5 format (no human inspection):** automated re-read: single band float32, EPSG:32611,
  3730×3292, transform == template, all 12,279,160 cells finite, min≥0, max≤1, nodata=None,
  0 dots on catalogue, 0 within 200 m (B2, the live-validated safety rule) in the FINAL file.
- **Verdict rule:** all G1–G5 pass → **promote** (site shows 🟢). Any fail → **negative**
  (site shows 🔴 DO NOT SUBMIT); the TIF is still published as a measured negative deliverable.
