# Round-5 hypotheses — written 2026-10-25 BEFORE any round-5 candidate was built

**Session lane (parallel-run protocol).** This session's single method is **H-CVF2** below. Every
other hypothesis is documented, ranked, and explicitly *not* built here, either because it belongs
to another lane, because it is data-blocked, or because it cannot be validated locally. Numbers are
labelled **[ORGANIZER-CONFIRMED]** (owner-reported from the DrivenData submission page),
**[HOLDOUT-DTI]** (local proxy, evaluator `src/gems32/holdout.py`), or **[MODEL]** (algebra).

## 0. What the forensic measurements established first (2026-10-25, this session)

All measured from the bytes on disk (`evidence/registry_overlap.json`, reproduced by
`scripts/analyze_registry_overlap.py`):

1. **The group's whole top cluster is one nested family.** Dot sets satisfy
   `champion (37,654) ⊂ solo (40,199) ⊂ d2.8 (44,090) ⊂ H19-5 (121,131)` exactly, and
   `champion == solo & (dist_to_catalogue > 2 px)` **exactly** (2,545 dots removed, all within
   200 m of the catalogue). Every live improvement in the family came from *removing* dots from
   one belief field: 0.1922 → 0.2600 → 0.2708 → **0.2778 [ORGANIZER-CONFIRMED]**.
2. **The GEMSDOE36 "Anderson PINN" (0.2750) is not an independent method at the dot level**: its
   38,854 dots *contain all 37,654 champion dots* (Jaccard 0.969). Its +1,200 extra dots scored
   **−0.0028** — a direct live measurement that marginal dots near the champion's own lineaments
   are below the metric's break-even credit `k > α·DTI = 0.0556` at DTI 0.2778.
3. **GEMSDOE30's `d28-poisson300m` and GEMSDOE25's `dotted-h19-5-d2-8` are the identical dot set**
   (44,090; symmetric difference 0) — and both are reported 0.2600, consistent with a
   deterministic scorer on dot sets.
4. Every pair of top-cluster rasters has **≥ 92.6 %** of dots within 3 px of each other. Under the
   parallel-run lane rule (≤ 70 % within 3 px of any one registry raster), *no re-sampling of the
   same lineament network is a legal new lane* — a new lane must place ≥ 30 % of its mass on
   different structures. That is the protocol working as intended.

**Why the champion won (mechanism, [MODEL] on [ORGANIZER-CONFIRMED] points).** The scorer masks
known faults; mass within 200 m of the catalogue almost never earns (the 2,545 removed dots
implied ≈ 0.006–0.016 credit/dot under the `(★)` inversion at |G| ∈ [7,905, 12,691], vs the
0.0556 break-even bar) but always pays α = 0.2 in the denominator. B = 2 was the first emission
with **zero** dots inside 200 m. The gain (+0.0070 over B = 1) is denominator thrift, not new
geology — which is also why it is nearly exhausted: the next annulus (200–300 m) can still earn
partial kernel credit, so B = 3 is a coin-flip worth ≤ +0.009 (see H-F3).

## 1. The five candidates, ranked by expected DTI gain ÷ implementation cost

| rank | id | layers / inputs | physical signature targeted | why it should catch faults the catalogue lacks | how it differs from everything in this repo | cost |
|---|---|---|---|---|---|---|
| 1 | **H-CVF2 — spatially-CV 35-channel GBM field, emitted under the champion's proven emission law** | the 19 official bands via `src/gems32/features.py` (bands 12 `det_elev`, 14 `tmi`, 2 `rtp`, 13 `iso_grav_anom`, 17 `cond_surf`, 15 `depth_to_base_surf` drive the derived channels) | line-shaped discontinuities *jointly* in topography and potential fields: Hessian ridge response of detrended elevation at σ = 1/2/3.5 px, Gaussian-Laplace curvature, white top-hat scarp step, gradient magnitudes of magnetic/gravity/conductivity/depth-to-basement, structure-tensor coherence — ranked by a per-pixel gradient-boosted classifier trained with 4-quadrant spatial CV | supervision comes from catalogue pixels, but the *ranking* generalises by appearance: a buried or unmapped fault with the same joint topo+potential-field line signature scores high even where no fault is mapped; the B = 2 gate then forbids spending mass where the field is merely re-describing the catalogue | the field family exists in the repo ("Candidate A") but its only artifact was **quarantined** (14.8 % of dots on-catalogue) and never submitted, and its emission was a plain top-n threshold. H-CVF2 is the first emission of this field with (i) zero dots within 200 m of the catalogue, (ii) exact lazy-greedy 300 m-kernel maximum-coverage spacing (`src/gems32/emitter.py`), (iii) the champion's exact 37,654-dot budget. The champion's own field is a hand-built multiline-corroboration surface emitted by raster-order thinning — different ranking, different placement rule | low–medium (all code exists; ~1 h CPU) |
| 2 | **H-SUP-SGMC — same stack, SGMC-augmented supervision** | 19 bands + USGS SGMC fault raster (local, hash-pinned) | same transforms; classifier positives = catalogue ∪ SGMC-off-catalogue pixels | SGMC is pre-Quaternary-inclusive: it contains real faults the Quaternary catalogue omits (61,664 px beyond 300 m of the catalogue, measured `evidence/h60_2_catalogue_difference.json`). Learning their *appearance* (not tracing their coarse pixels) targets a population no group field has aimed at | no artifact in the group has used SGMC as *supervision*; the two live SGMC attempts traced SGMC pixels directly and failed (0.0512, 0.0492 [ORGANIZER-CONFIRMED]) — a positional-accuracy failure, not evidence about appearance learning. **Designated fallback if H-CVF2 fails the lane-uniqueness gate** | medium |
| 3 | **H-F3 — B = 3 flank prune of the champion** | champion raster + catalogue | none (emission geometry only) | removes the 2,171 champion dots at 200–300 m from the catalogue; helps iff their mean credit < 0.0556 ([MODEL] breakeven; the 100–200 m annulus measured ≈ 0.006–0.016, but credit should rise with distance) | **REJECTED for this session**: a strict subset of the champion → 100 % of dots within 3 px of a registry raster → lane violation by construction. It is the incumbent lane's cheapest next experiment and is handed to the selector quantified: expected live Δ ∈ [−0.002, +0.009] | trivial |
| 4 | **H-F4 — relocated-seismicity lineaments (ex-H33-E)** | raw USGS FDSN event catalogue (ComCat), free & official: <https://earthquake.usgs.gov/fdsnws/event/1/> | linear clusters of microseismicity (fault-plane illumination) not present in the smoothed `ieq_n100a15`/`deq_n100a15` bands (measured autocorrelation 0.9986 @ 1 km — no fault-scale information) | active faults creep/seismically slip whether or not they are mapped; the 2020 Mw 6.5 Monte Cristo rupture inside the footprint ran on largely unmapped segments | never built: every seismic attempt used the two smoothed bands. **DATA-BLOCKED in this sandbox**: `earthquake.usgs.gov` returns HTTP 000 (re-verified 2026-10-25); the ready fetcher is `scripts/fetch_earthquake_catalog.sh`. Not claimed viable until fetched | high |
| 5 | **H-F5 — soft-valued kernel-matched emission** | any belief field | emit values ∝ expected kernel credit instead of binary dots | if the scorer integrates `p(x)·k` (as the published formula states), fractional mass on uncertain pixels dominates binary all-or-nothing placement | **NOT VALIDATABLE this session**: the identification probe S2 (λ = 0.5 scaling) that would reveal the scorer's value semantics has no reported score. Shipping soft values blind risks a thresholded scorer reading them as ~0 or as full mass. Documented, not built | low (but unvalidatable) |

## 2. Frozen build & decision rule for H-CVF2 (experiment 1 of ≤ 3)

1. **Stack**: `gems32.features.build` on the hash-verified 19-band mirror
   (sha256 `4371c82e…`, 418,912,844 B) → 35 channels, memmapped.
2. **Leakage canary (before any training)**: each channel alone → ROC-AUC of catalogue pixels vs
   240k sampled non-catalogue pixels, reported per quadrant and pooled. Any channel with
   AUC > 0.90 is leakage until proven otherwise and stops the build. (The stack deliberately has
   no distance-to-catalogue channel.)
3. **Field**: 4 quadrant folds (`holdout.quadrant_ids`, 15-px collar excluded from training);
   `DetectorSpec` defaults exactly as in `src/gems32/detector.py`
   (HistGB, 80 iters, lr 0.1, 31 leaves, ≤ 60k pos / 240k neg from the other three quadrants).
   Out-of-fold predictions assemble the full-footprint belief field. No hyperparameter is tuned
   on any holdout readout.
4. **Emission law (the champion's, verbatim where it was proven live)**: field zeroed outside the
   footprint and within 2 px of the catalogue (B = 2); support capped at the top 500,000 field
   pixels; `emitter.emit(budget = 37_654, prior_dti = 0)` — exact lazy-greedy maximum
   expected coverage under the official 300 m triangular kernel, exactly the champion's mass.
5. **Validation gates (all must pass for verdict `promote`)**:
   a. **[HOLDOUT-DTI]** beats the champion at matched mass on *both* `catalogue_hidden_mean` and
      `sgmc_prevalence_calibrated_dti` (evaluator `src/gems32/holdout.py`, draws 20/21);
      pooled DTI + 95 % CI (8-cell bootstrap) and the number of withheld positives are reported.
   b. **Lane uniqueness**: Spearman ρ ≤ 0.90 vs every registry raster (300 m-kernel density
      surfaces, footprint pixels) **and** ≤ 70 % of dots within 3 px of any single registry
      raster's dots. Checked on the field's density surface *and* on the final dots.
   c. **Portal validity**: the repo's 12-point audit (`gems32.submission.audit_geotiff`) **and**
      the independent second validator (`scripts/check_submission.py --strict-finite`) both PASS:
      single-band float32, EPSG:32611, 3730 × 3292, transform match, all values finite and in
      [0, 1], 0 on-catalogue dots.
   Any gate failure → verdict `negative`, the file is still published with its evidence, and the
   site labels it **DO NOT SUBMIT**. No weekly slot is spent by this session either way;
   promotion is the selector's step.
6. **Mimic (named non-fault process)**: the classifier can rank *drainage lines, roads, and
   GeoDAWN flight-line artefacts* — all produce line-shaped joint topo/magnetic responses.
   Mitigations: training positives are mapped fault pixels only; the SGMC off-catalogue
   instrument (faults the classifier never trained on) is gate (a); a shifted-null agreement
   test is reported for the dot set.

## 2b. Experiment-1 result and the instrument flaw it exposed (measured 2026-10-25)

H-CVF2 was built exactly as frozen above (`evidence/hcvf2_run.json`). Canary: **passed**
(worst channel AUC 0.6217 — `coherence_s2`, max-quadrant; no channel near 0.90). Uniqueness:
**passed decisively** (49.7 % of dots within 3 px of the champion vs ≥ 92.6 % for every
family member; density Spearman +0.31). Portal audit: **passed** (12-point audit and the
independent `scripts/check_submission.py --strict-finite`). Holdout gate (a): **failed** —
SGMC prevalence-calibrated DTI 0.05876 vs champion 0.06412 (SGMC coverage 8.19 % vs 8.94 % at
identical mass). **Verdict under the frozen gates: negative.** That verdict stands; nothing
below re-opens it.

One by-product outranks the candidate: with the new [ORGANIZER-CONFIRMED] points, the
`catalogue_hidden` instrument is now *provably perverse for B-gated emissions*. It scores the
live order **backwards**: live champion (B = 2) 0.2778 > solo (B = 1) 0.2708 > d2.8 (B = 0)
0.2600, but catalogue-hidden gives 0.00460 < 0.03104 < 0.09832. Mechanism: the instrument
hides catalogue components and rewards recovering them, while a B-gated candidate used the
*full* catalogue (hidden components included) to forbid dots within 200 m of them — it is
punished for exactly the behaviour the live scorer rewards. The brief's own holdout spec
("derive every catalogue-based feature only from the visible faults") is violated *by the
candidate's gate*, and `evaluate_candidate_holdout` does not correct for it (the 1-px
"debiased" shift does not reach B = 2). Registered as an irregularity; the instrument remains
valid only for candidates whose construction never saw the hidden segments. The SGMC
off-catalogue instrument has no such flaw (its truth is ≥ 300 m from the catalogue by
construction) and is the only fair local gate for B-gated candidates.

## 2c. Experiment 2 — H-SUP-SGMC, frozen addendum (written before the build, 2026-10-25)

Rank-2 hypothesis from §1, run as experiment 2 of ≤ 3. Identical to H-CVF2 except supervision:
positives = catalogue ∪ SGMC-off-catalogue pixels **from the north quadrants (NW, NE) only**.
The south quadrants' SGMC pixels are never shown to any fold, so a south-only SGMC readout is
an uncontaminated validation of exactly the population the hypothesis targets.

Frozen gates for experiment 2 (adapted only where §2b proved the original instrument invalid
for this candidate class; the adaptation is documented here *before* the run):

- **(a′) Primary**: exact pooled DTI against SGMC-off-catalogue truth restricted to the south
  quadrants (SW, SE), candidate vs champion at their native masses (37,654 = 37,654, matched).
  Paired component-bootstrap 95 % CI of the difference (truth components resampled; FP held at
  its full-truth value — the CI is therefore a lower bound on width, and is labelled so).
  Pass = candidate point estimate > champion.
- **(b′)** Lane uniqueness, unchanged thresholds (ρ ≤ 0.90; ≤ 70 % within 3 px), all rasters.
- **(c′)** Portal validity, unchanged (12-point audit fail-closed + second validator after).
- Full-map SGMC (train-contaminated for this candidate) and catalogue-hidden (perverse for
  B-gated candidates, §2b) are reported for the record and used as gates for **nothing**.

Honest prior: SGMC traces are positionally coarse, so SGMC positives are noisy supervision;
the two live SGMC-tracing failures (0.0512, 0.0492) warn the SGMC population may only partly
overlap the hidden test population. If (a′) fails, the learned-field lane is closed for this
project with two independent measurements, and the selector's best next step reverts to H-F3
(B = 3, incumbent lane).

## 3. What would falsify H-CVF2 cheaply

- Canary AUC > 0.90 on any channel → the field is reading the catalogue, not the geology.
- Holdout: champion ≥ H-CVF2 on either gate-(a) instrument → the hand-built field's ordering is
  better than the learner's; publish as a negative result (it would be the group's first clean
  field-vs-field measurement at champion-grade emission).
- Uniqueness: > 70 % within-3-px vs the champion → the learner re-discovered the same
  lineaments; log as duplicate lane and stop (fallback H-SUP-SGMC becomes experiment 2).
