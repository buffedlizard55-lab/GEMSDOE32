# Pre-registration — H42 slate and the H42-1 hanging-wall experiment (2026-10-25)

*Frozen before any H42 holdout number was computed. Session branch `arena/7a2fb844-gemsdoe32`.
Changing any gate below after seeing results would invalidate the experiment; deviations, if any,
are logged in the run card under `deviations`.*

## 0. Facts this slate rests on (all re-verified this session from primary sources)

| fact | source (read 2026-10-25) |
|---|---|
| Metric: DTI = TP_w / (TP_w + 0.2 FP_w + 0.8 FN_w + ε), triangular kernel, R = 300 m (3 px) | [problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) |
| Submission: one float32 band, EPSG:32611, 100 m, template bounds, values in [0, 1] | same page, "Submission format" |
| Known USGS/INGENIOUS fault **pixels** are masked from evaluation | DrivenData staff, [forum 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) |
| "New fault" = any fault pixel not already captured by USGS/INGENIOUS, *including newly mapped geometry of an existing fault system* | DrivenData staff, [forum 11536](https://community.drivendata.org/raw/11536) |
| Public score = one pooled Tversky index over all public-subset pixels; private computed the same way; final re-evaluation over the whole GeoDAWN area | DrivenData staff, [forum 11550](https://community.drivendata.org/raw/11550) |
| Same metric for public, private and Phase-2; no extra fault weighting; Phase-2 labels can be added/removed/changed; the exclusion mask is unchanged | DrivenData staff, [forum 11556](https://community.drivendata.org/raw/11556) |
| Test-fault data sources / fault types / coverage are deliberately not disclosed | DrivenData staff, [forum 11527](https://community.drivendata.org/raw/11527) |
| Weekly cap = whatever the DrivenData submission page displays | DrivenData staff, [forum 11553](https://community.drivendata.org/raw/11553) |
| Champion `h33-h33-2-b2…-zeros` (0.2778, owner-reported) = d2.8 ∩ {> 1 px} ∩ {> 2 px from catalogue}; d2.8 ⊂ H19-5 | re-measured from bytes this session (`evidence/h42_run.json → champion_construction`) |
| H19-5 = OOF-stacked fusion of 4 lines incl. 1 m / 10 m lidar openness/LRM and catalogue tip/step-over geometry | [19GEMSDOE README](https://github.com/buffedlizard55-lab/19GEMSDOE) |

Live evidence used to motivate (not to tune): the B-ladder 0.2600 → 0.2708 → 0.2778 (owner-reported)
says dots 0–200 m from mapped traces earn far below the marginal bar ⇒ new faults are rarely within
200 m of a mapped trace.

## 1. Candidate hypotheses (untried in this repo family; ranked)

| rank | id | layers | physical signature | why it should find *unmapped* faults | how it differs from existing work | expected Δ DTI · cost |
|---|---|---|---|---|---|---|
| **1** | **H42-1 HWCI** — hanging-wall conditional intensity | visible catalogue (geometry only), band 12 `det_elev`, band 19 slope, lidar scarp bands 1–10 & 12, bands 15/17/13/5/2/3/4, cached curvature/ridge/top-hat/coherence channels | learned P(new fault \| distance to nearest *visible* trace, **topographically signed side** (Δz = z̄(p) − z̄(nearest trace)), strike alignment with the nearest trace, local scarp evidence) | synthetic/antithetic splays and basinward-stepping piedmont scarps form on the **down-thrown (hanging-wall) side** of normal faults, in young alluvium, at 0.3–3 km — short, low-offset strands that 1:250k Quaternary compilations omit; the B-ladder says the 0–200 m annulus is dead, so the signal must live further out | 57GEMSDOE's `side` is left/right of an arbitrarily oriented strike vector (+ strike-slip handedness) — it cannot encode down-thrown vs up-thrown; H19 L1 / GEMSDOE33 = along-strike tip/step-over lobes; H37-1 DOC (GEMSDOE25) shifted the *same* dots down-dip; habitat models (GEMSDOE23/29/30) are unconditioned on the network. None learns side-asymmetry from fault-system hide-and-recover | +0.000…+0.015 (wide; the side effect may be absent) · medium (CPU GBM, ~15 min) |
| 2 | H42-2 Lahontan isobath suppression | absolute DEM (USGS 3DEP 1 arc-second, public domain) | delete lineaments whose along-strike elevation range < ~3 m below the pluvial highstand (shorelines are level; scarps cross contours) | removes the main named mimic of every scarp detector in the Lahontan basins | no repo implements a contour-parallelism discriminator (Lahontan appears only as a named mimic in run cards) | precision-only, unknown magnitude · high: absolute DEM is **not** in the restored data; `prd-tnm.s3.amazonaws.com` is unreachable from this sandbox (reachable from GitHub-hosted runners, as 19GEMSDOE did) |
| 3 | H42-3 Playa-floor dead zone | band 19 slope, lidar relief, band 17 conductivity | flat, conductive lacustrine floors where scarps are not preserved | precision: experts cannot map what the surface does not preserve | not used as an explicit mask before (1 passing mention) | small · low (subsumed by H42-1's learned model, which sees the same inputs) |
| 4 | H42-4 Anthropogenic-corridor suppression | TIGER/Line road distance (GEMSDOE24 audit source) | road/rail cuts and fills mimic scarps | precision | GEMSDOE24 already used roads as a nuisance audit (C2ST) — partially tried | small · low |
| 5 | H42-5 Relocated-seismicity lineaments | USGS ComCat FDSN | microseismic planes | sub-surface faults with no scarp | proposed before as H33-E/H-F4; data-blocked from this sandbox | low at 300 m tolerance · high |

**Only H42-1 is run this session** (budget: ≤ 3 experiments, ≤ 2 h; experiment count is recorded).

## 2. H42-1 experiment specification (frozen)

**Instrument (shared template, no private fork):** `vendor/gems57` pinned from
[57GEMSDOE@822a0ce](https://github.com/buffedlizard55-lab/57GEMSDOE/tree/822a0ce5546c7b6749cdd82eb145b6b3e616603d)
(via GEMSDOE31's vendored copy; hashes in `vendor/PROVENANCE.json`).
`holdout.buffered_component_draw(grid, seed ∈ {20, 21}, hide_frac = 0.20, buffer_px = 3)`:
whole 8-connected catalogue components withheld (20 % of catalogue pixels per label-blind eroded
quadrant), feature context = catalogue minus a 3 px collar around withheld truth, every other
catalogue pixel masked from scoring pixel-exactly. Scoring: `evaluate_holdout.evaluate` per fold
(20 km blocks) and `pooled_summary` (pool TP/FP/FN first; paired percentile bootstrap, 1000 draws,
seed 520810). Every number is labelled `HOLDOUT-DTI (gems57-pooled-hide-v2, n withheld, 95 % CI)`.

**Arms (identical emission law and identical per-fold dot budget):**

* `HWCI` — all features (relational incl. side + evidence).
* `SYM` — `HWCI` minus the three side features (ablation for the hanging-wall claim).
* `EVID` — evidence features only (no catalogue-relational features).
* `CHAMP_RECIPE` — the champion's d2.8 dot set with the B = 2 gate re-derived from the *visible*
  catalogue of each draw. Caveat fixed in advance: H19-5 was trained with the full catalogue, so this
  comparator is leak-advantaged; it cannot be reconstructed honestly (GEMSDOE24 reached the same
  conclusion).

**Model:** leave-one-quadrant-out `HistGradientBoostingClassifier(max_iter=200, learning_rate=0.06,
max_leaf_nodes=31, min_samples_leaf=200, l2_regularization=1.0, random_state=20261025)`; positives =
withheld truth in the three training regions; negatives = 300 000 random eligible non-catalogue
pixels in the training regions. No hyper-parameter search.

**Emission:** `emit.emit_decimated` on the predicted probability (one dot per 3 × 3 tile, ranked by
E[k]), allowed = fold region ∩ not catalogue ∩ distance-to-visible > 2 px (B = 2 re-derived from the
visible catalogue); per-fold budget = the `CHAMP_RECIPE` dot count in that fold.

**Final raster:** model refit on both draws' withheld truth (all four regions); predicted with the
*full* catalogue as context; B = 2 from the full catalogue; budget = 37 654 dots (the champion's mass).

## 3. Gates (all must pass for "OK TO SUBMIT"; otherwise the file is published as DO NOT SUBMIT)

* **G1 leakage canary** — every single feature's AUC (max(AUC, 1 − AUC), withheld truth vs eligible
  non-catalogue pixels of the test regions) ≤ 0.90; otherwise stop and report.
* **G2 hypothesis** — paired Δ(`HWCI` − `SYM`) > 0 with 95 % CI lower bound > 0.
* **G3 promotion** — paired Δ(`HWCI` − `CHAMP_RECIPE`) > 0 with 95 % CI lower bound > 0.
* **G4 lane uniqueness** — on the surface before placement and on the final dots: Spearman ≤ 0.90 and
  ≤ 70 % of my dots within 3 px of any one registry raster (all 222 focus-repo rasters, manifest
  `registry/focus_registry_manifest.json`).
* **G5 format** — template fail-closed writer + `scripts/check_submission.py --strict-finite` pass.

A negative result is a deliverable: the run card is written whatever the outcome.
