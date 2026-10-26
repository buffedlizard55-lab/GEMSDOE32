# Round-6 hypotheses & frozen preregistration — written BEFORE any round-6 candidate was built

**Date:** 2026-10-26 · **Session lane (explicit, single paragraph):** see §2.
**Labels:** `[HOLDOUT-DTI]` = local hide-and-recover / SGMC instrument (evaluator +
withheld positives + 95 % CI stated with every number); `[OWNER-REPORT]` = a number
the owner recorded from a DrivenData submission screen (no organizer receipt linking
bytes to score exists in this repo — IR-32-SCORE-01); `[MODEL]` = algebra on the
published metric. **No number in this file is ORGANIZER-CONFIRMED**, because this
repository holds no submission-page receipt for any group file. Earlier pages that
call 0.2778 "organizer-confirmed" overstate the evidence and are corrected by this
round (IR-R6-01).

## 0. Constraints established before proposing anything (measured this session)

1. **The champion is a subtraction, not a detector** `[measured-here]`:
   H19-5 (121,131 dots) ⊃ d2.8 (44,090) ⊃ solo/B=1 (40,199) ⊃ champion/B=2 (37,654).
   Verified again 2026-10-26 from bytes: champion ⊂ d2.8 exactly (37,654/37,654),
   sha256 `c55bafc4…`. Every gain in the family came from *removing* low-credit mass.
2. **The metric's bar** `[MODEL]`: a dot raises DTI iff its realised kernel credit
   `k > 0.2·DTI` (= 0.0556 at 0.2778). Known faults are masked, so near-catalogue
   dots earn ≈0 but still pay 0.2 — this is why B=1→B=2 paid +0.0108 then +0.0070
   `[OWNER-REPORT]`.
3. **Beating 0.2778 needs better-placed mass, not more/less of the same mass**
   `[MODEL]`: at the same 37,654 dots, +8 % mean credit ⇒ ≈0.30; the public #1
   (0.4413, owner-stated snapshot, unverified here) needs ≈+59 %. No public
   catalogue supplies this (newest compilation already inside the given catalogue).
4. **The current site primary does NOT pass its own gates** `[measured-here]`:
   `geo-conduit` (site: "OK TO SUBMIT") has 70.24 % of dots within 3 px of
   `gems10-h28-dotted-ridge` — above the ≤70 % lane limit — and its SGMC-calibrated
   holdout (0.0462) is below the champion's (0.06412, Round-5 measurement). The
   site simultaneously shows a red "DO NOT SUBMIT" banner and a green "OK TO
   SUBMIT" box for different files. Both defects are fixed this round (IR-R6-02).
5. **The literal lattice gate is unsatisfiable** `[measured-here]`: the calibration
   lattice (`r13-lattice-s5`, 206,895 dots) covers 99.87 % of the footprint within
   3 px; even the champion scores 99.92 % against it. A gate that every possible
   file fails measures nothing. Round 6 therefore applies the ≤70 % / ρ≤0.90 gate
   to **detector submission rasters** (every scored/downloadable detector file on
   disk) and reports the lattice number as a diagnostic only (IR-R6-03). This is a
   documented interpretation, not a silent exemption: the lattice is a calibration
   grid submitted to estimate |G|, not a competing method lane.
6. **Data restored and hash-verified this session**: core (training_features
   `4371c82e…`, labels `7ba308cc…`, sample `2176d08e…`), external (SGMC
   `643cbe99…`, LiDAR-scarp `d580bb8b…`, …), scored (12 files) — via
   `scripts/restore_data.py` from the pinned GitHub mirrors. Provenance remains
   owner-mirror, not organizer-authenticated (IR-32-DATA-01). Band 12 description
   read from the raster itself: *"det_elev — Detrended elevation"* (the check the
   protocol review required before using band 12 as DEM).

## 1. Five candidate hypotheses not yet tried, ranked

Ranking criterion: expected DTI improvement ÷ implementation cost. "Expected DTI"
is qualitative judgement only — no projected score is stated anywhere.

| Rank | Hypothesis | Layer(s) & physical signature / transform | Why it should catch catalogue-*missing* faults | How it differs from everything in this repo | Cost |
|---|---|---|---|---|---|
| **1 — BUILD NOW (this session's lane)** | **R6-1 Signed cross-profile STEP detector** (step-vs-ramp residual) | Band 12 `det_elev` (+ band 19 slope for canary only). At 4 orientations, inner means at ±(2–3) px vs outer means at ±6 px: `step=|M+−M−|`, ramp ratio `r=|W+−W−|/step` (pure ramp r=2, pure step r=1), score `step·clip(2−r,0,1)`, × structure-tensor coherence | Catalogue scarps were mapped by *strong* breaks; a weak/buried piedmont scarp retains a repeatable slope **break** (step geometry) even when curvature/relief magnitude is sub-threshold. The step-vs-ramp test targets exactly the sub-mapping-threshold tail while rejecting smooth hillslopes that fool magnitude detectors | Existing code has Hessian-ridge magnitude, top-hat, Laplace curvature (`features.py`, `pfonly.py`) — all *magnitude* responses. None fits a step model against a smooth-ramp null or checks profile concentration. Label-free (no classifier), single-layer — disjoint from GEO-CONDUIT (strain×potential), Arena41 PF-only (potential-fields), HCVF2 (35-ch GBM), H19-5 (multiline vote) | Low (label-free convolutions, CPU minutes) |
| 2 | **R6-2 Potential-field cross-gradient phase pairing** | `tmi`/`rtp` (14, 2) + `iso_grav_anom` (13): local axial angle between magnetic & gravity gradients + paired signed-curvature zero-crossings | A subsurface fault offsets *both* density and susceptibility basement, so the two gradients stay phase-locked along strike even with zero surface scarp — the buried intra-basin population | PF-only used edge *magnitudes* + upward-continuation persistence in a GBM; nobody has used the *relational* angle/sign pairing between two independent potential fields | Medium |
| 3 | **R6-3 Nuisance-residualised conductivity ridge** | `cond_surf` (17) residual after spatially cross-fitted regression on elevation/relief, then transverse ridge of the residual; `depth_to_base_surf` (15) as covariate | Hydrothermally altered fracture zones are conductive independent of topography; removing the topographic/lithologic nuisance first exposes fluid-pathway lineaments that raw-conductivity edges bury | Prior work fused raw `cond_edge` as one GBM channel among many; explicit nuisance residualisation before edge extraction is new. Mimic: saline playa sediments | Medium |
| 4 | **R6-4 Relocated microseismicity lineaments** | Raw USGS FDSN/ComCat event catalogue (free, official: https://earthquake.usgs.gov/fdsnws/event/1/) → linear hypocentre clusters (fault-plane illumination) | Active faults slip seismically whether mapped or not; the 2020 Mw 6.5 Monte Cristo rupture inside the footprint ran on largely unmapped segments. The two competition seismic bands are 100-km-smoothed (autocorr. 0.9986 @1 km — no fault-scale signal) | Never built; every seismic attempt used the smoothed bands. **DATA-BLOCKED in this sandbox** (outbound allowlist = github/pypi/npm only; `earthquake.usgs.gov` unreachable). Fetcher ready: `scripts/fetch_earthquake_catalog.sh`. **Not viable until run on an unrestricted machine** | High (blocked) |
| 5 | **R6-5 En-échelon scarplet-chain vote (1 m LiDAR)** | USGS 3DEP 1 m DEM tiles via the competition's DEM-link table (official source: https://www.usgs.gov/3d-elevation-program) → short parallel scarplet segments voting for a through-going trace | Transtensional step-overs express as discontinuous scarplet *chains* that per-pixel 100 m detectors miss but a chain-vote recovers | The mirrored `lidar_scarp_features_u8.tif` (100 m aggregates) was used as GBM channels; native 1 m chain geometry was never built. **Tiles unreachable from this sandbox** (same allowlist); the 100 m mirror is obtainable but is a different, already-explored lane | High (blocked) |

**Data-obtainability verdict (required by the brief):** R6-1/2/3 need only the
hash-verified 19-band mirror already restored — viable now. R6-4 and R6-5 name
specific free official sources above; both were checked against this sandbox's
outbound allowlist and are **not obtainable here**, so neither is proposed as
viable for this session.

## 2. Frozen build & decision rule for R6-1 (Experiment 1 of ≤3)

**Lane paragraph:** *A label-free, single-layer (detrended-elevation) signed
cross-profile step detector: score each pixel by how well its cross-strike
elevation profile matches a concentrated step rather than a smooth ramp, at four
orientations, gated by structure-tensor coherence; emit with the champion's
proven geometry (B=2 catalogue exclusion, field-ordered Poisson thinning at
2.8 px) at exactly the champion's mass (37,654 dots). Named non-fault mimic:
Pleistocene Lake Lahontan shoreline terraces and road cuts (contour-following
steps with no fault). No magnetics, gravity, strain, radiometrics, LiDAR, or
classifier is used, so the lane cannot collapse into any prior lane's field.*

1. **Field (frozen formula):** DEM = band 12, footprint = finite & above the
   −3.4e38 sentinel; median-fill outside footprint for filtering only; Gaussian
   σ=1.0. For normals n ∈ {(1,0),(0,1),(1,1),(1,−1)}: M± = mean of shifts ±2n,±3n;
   W± = shift ±6n; `step=|M+−M−|`; `r=|W+−W−|/max(step,ε)`; `s_n=step·clip(2−r,0,1)`.
   Field₀ = max_n s_n; Field = robust_unit(Field₀) × coherence_σ2(DEM); zero
   outside footprint. No parameter is tuned on any holdout readout.
2. **Leakage canary (before emission):** ROC-AUC of Field (and of bands 12, 19
   alone) for catalogue pixels vs sampled non-catalogue footprint pixels.
   Any AUC > 0.90 ⇒ leakage until proven otherwise ⇒ STOP.
3. **Surface uniqueness (before placement):** Spearman ρ between Field and the
   300 m-kernel density surface of every detector raster on disk (full footprint,
   `gems32.release_gate.compare_registry`, stage=surface). Any ρ > 0.90 ⇒ STOP.
4. **Emission:** eligible = footprint & (distance-to-catalogue > 2 px) & Field>0;
   `pfonly.dot_thin(Field, eligible, budget=37_654, min_dist=2.8)`.
5. **Gates — ALL must pass for verdict `promote` (else `negative`, file still
   published as DO NOT SUBMIT; no slot is spent either way):**
   a. **[HOLDOUT-DTI] Primary (fair for B-gated files):** exact DTI
      (`gems32.metric.dti_exact`, α=0.2, β=0.8, R=3 px) against SGMC
      off-catalogue truth (SGMC pixels >3 px from catalogue, inside footprint),
      candidate vs champion at matched mass, with paired component-bootstrap
      95 % CI of the difference (truth components resampled; FP held at
      full-truth value ⇒ CI is a lower bound on width, labelled so).
      Pass = candidate point estimate > champion.
      *Secondary (reported, never gated):* catalogue-hidden holdout
      (`gems32.holdout`, draws 20/21) — provably perverse for B-gated files
      (IR-32-INSTR-03), so it is context only.
   b. **Final-dot uniqueness:** ≤70 % of candidate dots within 3 px of *any
      single* detector raster on disk, and density-surface ρ ≤ 0.90
      (`compare_registry`, stage=final). Lattice reported as diagnostic (§0.5).
   c. **Portal validity:** `gems32.submission.audit_geotiff` (12-point) AND
      `scripts/check_submission.py --strict-finite` both PASS on the written
      bytes: single-band float32, EPSG:32611, 3730×3292, transform = sample,
      all 12,279,160 cells finite in [0,1], nodata=None (zeros variant),
      0 dots on catalogue. This is the automated no-human inspection that
      permanently prevents `"Predicted values must be in range [0, 1]"`.
6. **Budget:** ≤3 experiments / ≤2 h. If gate (a) fails, the lane is closed as a
   negative deliverable — no parameter is re-tuned against the readout.
   Promotion never spends a slot; the selector checks the authenticated weekly
   cap separately.

## 3. What would falsify R6-1 cheaply

- Canary AUC > 0.90 → the field reads the catalogue, not the terrain.
- SGMC gate: champion ≥ candidate → step geometry adds nothing over multiline
  corroboration at champion-grade emission; publish as negative.
- Uniqueness: >70 % within-3-px vs any detector raster → the step field
  re-discovered an existing lane's lineaments; log as duplicate and stop.
