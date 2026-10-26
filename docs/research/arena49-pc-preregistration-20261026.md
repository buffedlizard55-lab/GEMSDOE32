# ARENA49 pre-registration — five untried hypotheses, single lane H1-PCG (frozen 2026-10-26, before any ARENA49 code ran)

## 0. Irregularity flagged before implementation (IR-ARENA49-LANE-01)

The session prompt says *"Your lane is the single method paragraph below"*, but no method
paragraph follows it — the thresholds appear as unresolved placeholders (`[0.90]`, `[70%]`,
`[3] experiments`). The standing brief in this repo records the same absence
(`docs/research/standing-prompt-as-recorded-20261026.md`). **We do not silently invent a lane.**
This document adopts the top-ranked hypothesis below (Rank 1) as this session's single lane,
records that adoption explicitly, and stays inside it. Thresholds used are the repo's standing
values, not the placeholders: surface/final Spearman ≤ 0.90, final-dot ≤70% within 3 px of any
genuine registry raster, single-feature canary AUC ≤ 0.90, budget ≤3 experiments / ≤2 h,
0 weekly slots spent by this session (promotion is a separate selector step).

Data status, verified this session by hash, not assumed: core + external + scored inputs were
restored with `scripts/restore_data.py` (SHA-256 verified against
`registry/data_manifest.json`; training_features `4371c82e…`, labels `7ba308cc…`,
sample_submission `2176d08e…`). No new external download is needed for Rank 1.

## 1. Five candidate hypotheses not yet tried in this repo

Each names: layers · physical signature/transform · why it should catch a fault missing from
the USGS/INGENIOUS catalogue · how it differs from everything already in this repo ·
free/official external data status. Ranked by expected HOLDOUT-DTI gain ÷ implementation cost.

| Rank | ID | Layers | Signature / transform | Why off-catalogue | Differs from repo | External data |
|---|---|---|---|---|---|---|
| **1 (LANE)** | **ARENA49-H1-PCG** | Band 12 `det_elev`, Band 13 `iso_grav_anom` (both official `training_features.tif`) | **Kovesi log-Gabor phase congruency (PC)**: step/line features are points where Fourier components are maximally in phase; PC = \|Σₙ EOₙ\| / Σₙ\|EOₙ\| per orientation, summed over orientations. Amplitude/contrast-invariant, unlike every gradient/Hessian/theta detector here. DEM-PC catches low-throw scarps whose gradient amplitude is buried in regional slope noise; gravity-PC catches buried basement steps with no scarp. Dual-field geometric-mean concordance requires both. | Catalogue mapping is scarp-amplitude driven (photo/LiDAR interpretation): a low-throw or sediment-blanketed fault has a real step in elevation/basement but too little amplitude to have been mapped. PC normalises amplitude away, so exactly those steps rank as high as range-front scarps. | `grep` over `src/ scripts/ docs/research/ knowledge/ registry/` finds **no** phase-congruency, monogenic, Riesz or log-Gabor implementation anywhere in this repo. H50 used TDR local-wavenumber + theta-map (amplitude-weighted derivatives); Arena8a/H36 used TDR zero-crossings; features.py uses Hessian ridges/curvature — all amplitude-based. | None needed. Bands already hash-verified in-repo. Method: Kovesi (1999), *Image Features From Phase Congruency*, Videre 1(3), https://www.peterkovesi.com/papers/Kovesi_Videre_v1n3001.pdf ; geophysics use: *Monogenic Phase Congruency* lineament mapping, GeoConvention 2016, https://geoconvention.com/wp-content/uploads/abstracts/2016/147_GC2016_Monogenic_Phase_Congruency.pdf |
| 2 | ARENA49-H2-NODE | Band 12 `det_elev` skeleton × Bands 3/9 `tmi_hg/tmi_vg` skeleton (official) | **Topological lineament-intersection nodes**: crossing points of two independently-derived 1-px skeletons, dilated by the 300 m kernel. Fault intersections/step-overs are the classic geothermal upflow sites. | Intersections of a mapped DEM lineament with a buried magnetic lineament are off-catalogue by construction — neither parent lineament alone needs to be a catalogued fault. | Prior concordance (H44/H50/Arena8a) is pixel-wise AND/geometric-mean of co-located fields; no code here computes skeleton *crossings* as a topological object. | None needed. Not run (outside lane). |
| 3 | ARENA49-H3-UPCONT | Band 14 `tmi`, external `geodawn_extensions_u8.tif` Band 4 `TMI_up150` (GeoDAWN, DOI 10.5066/P93LGLVQ, already restored) | Upward-continuation persistence ratio \|∇TMI₁₅₀\|/\|∇TMI₀\| on gradient crests (deep Euler N≈0–0.5 contacts persist; surficial sources decay). | Deep-rooted buried contacts under alluvium persist at +150 m continuation where surficial float does not. | Registered as H46-2 but **never executed**; H38/H44 used a scalar `tmi − up150` difference, not a gradient-persistence ratio. | Already in repo (hash-verified external). Not run (outside lane). |
| 4 | ARENA49-H4-TERN | External `geodawn_rad_u8.tif` Bands 1–3 (K, Th, U; GeoDAWN DOI 10.5066/P93LGLVQ, already restored) | Radiometric **ternary / Efimov F-parameter** (K·eU/eTh) alteration-boundary lineaments: hydrothermal K-metasomatism fronts as edges in ternary-centroid distance. | K-enrichment along permeable upflow can occur on blind faults with no scarp and no magnetic basement offset. | H35/H38 used a single Th/K ratio edge as one fused channel inside a supervised GBM; no ternary/F-parameter field or standalone alteration-boundary skeleton exists here. | Already in repo. Not run (outside lane). |
| 5 | ARENA49-H5-OBLIQ | Bands 4/7/8 (geodetic strain), 10/16 (seismic), 2 `rtp` (official) | Strain-gradient azimuthal obliquity sin²2(θ_PF − θ_∇ε) coupled to potential-field strike (slip/dilatation tendency on buried strikes). | Actively dilating Walker Lane transfer segments can be permeable before accumulating mappable Quaternary offset. | Registered as H46-3, never executed; prior strain use was isotropic products, no azimuthal coupling. Deprioritised: this repo measured `ieq_n100a15` autocorrelation 0.9986 at 1 km (100 km smoothing), so the seismic part carries almost no fault-scale signal. | None needed. Not run (outside lane). |

**Named non-fault mimic for the lane (H1-PCG):** Pleistocene Lake Lahontan wave-cut shoreline
benches and unfaulted basin-fill density contacts. Shorelines are DEM-only steps (no gravity
step); basin-fill contacts are gravity-only steps (no DEM step). The EXP3 dual-field
geometric-mean concordance down-weights both single-domain classes. A genuine fault step that
offsets both the surface (or shallow section) and basement is the concordant class.

## 2. Frozen lane design (ARENA49-H1-PCG) — no tuning after this point

- **Fields.** PC computed on the nearest-neighbour-filled full grid (so the irregular footprint
  edge is not itself a step), output masked to the footprint; emission support additionally
  excludes a 3-px erosion of the footprint boundary.
  - EXP1 `EXP1_DEM_PCG`: PC of Band 12 `det_elev`.
  - EXP2 `EXP2_GRAV_PCG`: PC of Band 13 `iso_grav_anom`.
  - EXP3 `EXP3_DUAL_PCG` (**the shipped candidate if any**): floored geometric mean of the
    percentile-stretched EXP1/EXP2 PC fields (same floored form as `tmspi.geometric_mean_concordance`);
    support is the DEM-PC support re-ranked by the concordance field (gravity cannot inflate a blob).
- **PC parameters (fixed):** log-Gabor bank, 4 scales (min wavelength 3 px, multiplier 2.0),
  6 orientations, σ_onf = 0.55, Butterworth low-pass (order 15, cutoff 0.45 Nyquist).
  Per orientation: PC_o = W_o · max(|Σₙ EOₙ| − T_o, 0) / (Σₙ |EOₙ| + ε), T_o = 2 × median(|EO| at the
  smallest scale) — a documented simplification of Kovesi's Rayleigh noise estimate;
  W_o is Kovesi's frequency-spread weighting in the simplified amplitude-spread form
  s = (ΣₙAₙ/maxₙAₙ − 1)/(nscale−1), W = 1/(1+exp((0.5−s)·10)). (Amendment recorded before any
  real-data fit: the first synthetic step-edge unit test showed W_o=1 scores PC≈0.86 far from a
  step, where only the largest wavelength responds — exactly the failure Kovesi's spread
  weighting exists to suppress. W_o=1 was therefore replaced, not tuned on holdout data.)
  Total PC = Σ_o numerator_o / (Σ_o Σₙ |EOₙ| + ε) ∈ [0, 1].
- **Support (fixed):** PC ≥ 90th percentile of positive in-support PC, footprint eroded 3 px.
- **Emission (fixed):** shared `gems32.emitter.emit` (exact 300 m CELF lazy-greedy),
  budget 37,654 dots, `prior_dti=0.0` (budget-stopped, as H50). Catalogue pixels masked exactly.
  Final file additionally applies the full-catalogue B=2 gate (distance to `labels.tif` > 2 px);
  holdout scoring re-derives that gate **per cell from visible faults only** via the shared
  evaluator (`b_visible_px=2`), so no withheld fault influences its own gate.
- **Evaluation (fixed, shared tools only):** `gems32.holdout.evaluate_visible_gated_holdout` +
  `evaluate_hide_and_recover` + `evaluate_sgmc_with_ci` via the same context as H50
  (evaluator versions `GEMSDOE32-HOLDOUT-v3-visible-gated` / `GEMSDOE32-HIDE-RECOVER-v3.0` /
  `GEMSDOE32-SGMC-CAL-v3.0`, 22,232 withheld positives, 1,000 bootstrap reps, seed 50/20261026
  as in the shared code). Champion `h33-h33-2-b2` scored on the identical evaluators.
  Every number is labelled HOLDOUT-DTI (evaluator, n, 95% CI) or OWNER-REPORT; no live-score
  projection is printed as a score.
- **Canary (Rule 4):** every PC channel alone vs catalogue positives, two-polarity AUC ≤ 0.90.
- **Uniqueness (Rule 1):** continuous surface Spearman AND final-dot ≤3-px directional overlap
  vs every genuine `docs/downloads/*-zeros.tif` (1,000–90,000 dots), limits 0.90 / 0.70, checked
  on the surface before placement (EXP surfaces) and on final dots. The 5-px calibration lattice
  (`13gems r13-lattice-s5`) is reported separately: it is a synthetic covering grid, and this
  repo has measured random/champion dots at ≈0.999 on it (IR-42-UNIQ-01 pigeonhole) — it is
  flagged, not silently exempted.
- **Format (shared writer):** `gems32.submission.write_submission_pair` + `audit_geotiff`
  + `scripts/check_submission.py --strict-finite`. Zeros variant: single-band float32,
  EPSG:32611, 3730×3292, template transform, `nodata=None`, all 12,279,160 cells finite in [0,1].
- **Promotion rule (fail-closed):** `gems32.release_gate.promotion_decision` must return
  `promote` on all gates **and** a separate weekly-slot selector must approve. This session
  spends 0 slots regardless; a `promote` verdict here still prints "selector required".

## 3. Budget

3 experiments (above), ≤2 h wall time. Negative result is a deliverable and will be shipped
as a labelled research/audit artifact with the full run card, exactly like H50.

## 4. Official / verified sources for manual review

- Competition + metric (α=0.2, β=0.8, 300 m kernel): https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Leaderboard (public observation only): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Kovesi (1999) phase congruency: https://www.peterkovesi.com/papers/Kovesi_Videre_v1n3001.pdf
- Phase congruency for magnetic lineaments (GeoConvention 2016): https://geoconvention.com/wp-content/uploads/abstracts/2016/147_GC2016_Monogenic_Phase_Congruency.pdf
- GeoDAWN airborne magnetic/radiometric surveys (USGS): https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ; DOI 10.5066/P93LGLVQ
- EPSG:32611: https://epsg.io/32611
- Tversky index: https://en.wikipedia.org/wiki/Tversky_index
