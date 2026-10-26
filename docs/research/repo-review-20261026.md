# GEMSDOE32 repository review — 2026-10-26

## Corrective review addendum — 2026-10-26 04:45 UTC

This addendum supersedes earlier math, provenance, currentness, and test-status statements below wherever they conflict. The earlier paragraphs remain in the audit trail, but must not be used as the current decision record.

- **DTI algebra corrected:** `src/gems32/metric.py`, `src/gems32/emission.py`, `README.md`, `docs/research/score-ceiling-analysis.md`, and the archived `why-02778-analysis-20261025.md` now use `DTI = TP/(TP + 0.2 FP + 0.8 FN)`. The isolated previously-uncovered pixel special-case break-even is `k > 0.2*DTI`; arbitrary marginal additions require `ΔTP·D > TP·(ΔTP + 0.2ΔFP + 0.8ΔFN)`. Former hidden-TP/recall and score-ceiling extrapolations that used a non-equivalent identity are withdrawn. A regression test covers a partially-covered counterexample.
- **Score provenance:** the reported H33-B2 value `0.2778` remains **OWNER-REPORT**, not organizer-confirmed; no score-to-exact-byte receipt is in this checkout. No public leader score authenticates this team's private score.
- **Leaderboard snapshot:** official public page observed `2026-10-26T04:32:28Z`; #1 `xiaofanhu` at `0.4437`; `0.4413` is the previous-day snapshot and `0.3195` is historical. The saved snapshot and `registry/leaderboard_history.jsonl` are timestamped. This is a point-in-time public observation, not a final/private score.
- **Verification after these edits:** `.venv/bin/python -m pytest -q` → **105 passed, 9 skipped, 15 warnings**. Skips remain dependent on absent source/label/group data. `scripts/build_site.py` was run after its stale metric/provenance copy was corrected; the generated pages were inspected for the fail-closed decision, current leaderboard date/value, owner-report labels, and stale withdrawn formulas.
- **Three-pass review:** (1) rechecked metric algebra and counterexample against implementation/tests; (2) rechecked score evidence classes and the timestamped public leaderboard snapshot; (3) inspected source and regenerated HTML, including the red release decision and site-wide stale claims. This is a documentation/code review, not a fresh scientific experiment.
- **Archive cleanup:** replaced the discredited `knowledge/02` and `knowledge/03` metric/ceiling narratives with corrected notes; added explicit withdrawal banners to historical Round-5/knowledge material, removed unsupported per-dot credit/reachability claims, and corrected remaining group-score labels to OWNER-REPORT.
- **Outcome unchanged:** no experiment or holdout run, no new candidate TIFF, no submission slot, and no PR or merge. Existing candidate promotion remains **DO NOT SUBMIT**; source rasters and cached feature stack are absent in this checkout. A format-valid file is not a safe-to-submit candidate.

## Fresh review addendum — 2026-10-26 04:32 UTC

This addendum records the current checkout and corrects two stale provenance/currentness claims found during the present review.

- **Official leaderboard checked live:** direct read of [DrivenData's public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) at approximately `2026-10-26T04:32:28Z` showed `xiaofanhu` at rank 1 with `0.4437` (rank 2 `cfld__`, `0.3916`; rank 3 `Batik Shirt Brothers`, `0.3904`). Machine-readable capture: [`evidence/live_leaderboard_snapshot_20261026.json`](../../evidence/live_leaderboard_snapshot_20261026.json). The `0.4413` in the cached status is a prior-day snapshot; `0.3195` is older still. Neither should be called current. This public leaderboard says nothing about our team submission receipt or final/private-round score.
- **Portfolio score provenance corrected:** `0.2778` for the H33-B2 TIFF remains the highest score in the user-provided nine-site list, but it is **OWNER-REPORT**, not ORGANIZER-CONFIRMED: no receipt binding the exact raster bytes to that score is in this checkout. `registry/current_status.json` and README now make that distinction explicit.
- **Fresh environment audit:** no `sample_submission.tif`, `labels.tif`, `training_features.tif`, or cached feature stack is present in this checkout (`data/` contains only manifests/logs; `.cache/` absent). Dependencies were installed into ignored `.venv/`; `pytest -q` completed **104 passed, 9 skipped, 15 warnings**. Skips rely on absent source/label/group data, so this is not an end-to-end model or holdout verification.
- **Existing champion bytes:** independently read with Rasterio: SHA-256 `c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9`; one `float32` band, EPSG:32611, shape `3730×3292`, affine `(100, 0, 243350, 0, -100, 4508550)`, no nodata tag, all `12,279,160` cells finite in `[0,1]`, `37,654` positive cells. This checks stored bytes and range only; without the template raster in the checkout it does **not** freshly verify template-grid equality, novelty, or submission authorization.
- **Decision:** no fresh candidate was built, no slot was used, and no new TIF is marked OK to submit. The archived negative TIFs are not a substitute for a newly generated, compliant candidate. The current prompt omits the required single-method lane paragraph, and source data/cache are missing; both are hard stop conditions under the protocol, not reasons to infer a method or synthesize a raster from prior submissions.

### Candidate shortlist (planning only; no experiment run)

These are exact methodological variants not demonstrated as completed experiments in the current source tree. Several were already registered as research ideas in prior rounds, so they are **not new-to-the-repository concepts**. Qualitative rank is expected usefulness per implementation cost, not a score projection. None is a viable submission candidate until data and the lane are restored/assigned.

| Rank | Candidate method and layers | Physical signature / missed-fault rationale | Difference from implemented code | Cost and blockers |
|---:|---|---|---|---|
| 1 | **Signed potential-field phase/curvature pairing** — GeoDAWN TMI/RTP (`bands 14/2`) plus isostatic gravity (`band 13`) | Pair the polarity and sign of curvature/zero-crossings across magnetic and gravity fields; common basement offsets may produce co-located edges beneath no scarp. Intrusive contacts are the named non-fault mimic. | Existing `features.py` exposes smoothed gradient magnitudes (`tmi_edge`, `rtp_edge`, `grav_edge`); H38 included a cross-gradient term. The specific signed, scale-normalized, polarity-paired curvature test is not established as a completed experiment, so treat novelty narrowly. | Medium compute; requires the missing official 19-band TIFF/cache. No extra public source is needed. |
| 2 | **Terrain-residualized conductivity ridge** — `cond_surf` (`band 17`), detrended elevation/relief (`band 12`), depth-to-base (`band 15`) | Fit relief/position nuisance terms within spatial training folds, then extract coherent transverse ridges in conductivity residuals; fluid pathways may persist where map effort/topographic expression does not. Saline playa/alluvial sediment is the named mimic. | Current shared feature stack uses raw conductivity and `cond_edge`; does not document a fold-local nuisance residual transform. The concept has been preregistered before, but no verified result for this exact test is in this checkout. | Medium compute; missing features/labels/cache prevent fold-local fitting and single-feature canary. |
| 3 | **Native-resolution 1 m LiDAR scarp-chain topology** — official 1 m DEM tiles listed by the competition and USGS 3DEP | Segment short scarplets at native resolution and measure en-echelon alignment / along-strike gaps, then aggregate to 100 m; discontinuous low-throw traces can be missed by existing aggregate channels. Lake Lahontan shoreline benches and roads are explicit mimics. | Existing repo uses 100 m LiDAR aggregates; native 1 m chain topology is not implemented here. | High storage/compute. Requires DEM tiles and their licenses/availability; official source: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program). Not verified downloadable in this run; not yet viable. |
| 4 | **3-D relocated microseismic plane with surface projection** — raw USGS ComCat/FDSN hypocentres and, if available, official moment tensors | Fit spatially coherent hypocentre planes and project fault-plane geometry to the map; active buried faults can lack surface scarps. Mining blasts and diffuse swarms are the mimic. | Existing seismic layers are strongly smoothed; this exact point-cloud/plane workflow is absent. Related concepts have been registered, but no successful data-backed run is shown. | High; external data and location uncertainty are limiting. Official source: [USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/). Not fetched/coverage-tested here, so not viable in this run. |

**Required next step:** supply the assigned single-paragraph lane, restore/hash-verify competition data and feature cache, then choose exactly one eligible hypothesis. First test every component alone for leakage; evaluate via shared `evaluate_holdout.py` with per-fold visible-only features and whole-segment buffers; run surface correlations before placement and final dot overlaps after placement. Only create the candidate TIFF if the compliant holdout beats the current holdout incumbent with the required uncertainty and all uniqueness/format gates pass. Do not spend a slot before a separate selector authorizes it.

> **Same-day addendum:** After this inventory was written, the pinned owner-mirror archive restored `sample_submission.tif` and the calibration lattice into the ignored cache. The strict exact-grid/finite-range validator now passes, but this does not change the negative release decision. A direct final-dot audit found 36,832/37,654 (97.82%) within 3 px of the lattice, exceeding the 70% stop threshold; the earlier 41.36%/29-raster summary omitted this registered raster. Pre-placement all-registry surface correlation remains incomplete. The final merged build/tests passed (90 passed, 8 skipped; 15 warnings); the skips require unavailable training/label/group artifacts. See the later [three-pass protocol review](protocol-review-20261026.md) and updated [current release decision](../../evidence/current_release_review.json).

## Decision first

**DO NOT SUBMIT the current Round-6 TIF.** Its file-format properties are valid when read from the published bytes, but the current run has no method-lane paragraph and the historical promotion evidence does not satisfy the required fold-specific hide-and-recover protocol. This is a process-validation failure, not a claim that the raster is malformed. The artifact is retained for audit and education; its historical score/proxy fields are not an authorization.

The previous artifact remains unique by its recorded prior-round comparison: max surface Spearman correlation **0.3401** and max final-dot overlap **41.36%** within three pixels across **29** rasters. These are historical registry diagnostics, not an assigned-lane check for this session. Its SHA-256 is `c7f094c1f4d00f2dd9a056dc80fecc94bf1d636363acd020c9da3659eae56547`.

## Three-pass review

### Pass 1 — inventory and baseline

- Read `README.md`, the standing brief, current submission registry, generated site, Round-6 preregistration, run card, and tests.
- The repository contains a Round-6 TIF, ZIP, audit sidecar, hypotheses, feature/evaluation code, and per-site executive summary.
- The current checkout does **not** contain the core competition rasters or the cached template/feature stack. Only small logs/manifests are in `data/`; `data/` has no `sample_submission.tif`, `labels.tif`, `training_features.tif`, or `external/` assets. Therefore the previous holdout and exact template comparison could not be rerun here.
- Read the current TIF bytes with Rasterio: one float32 band; EPSG:32611; shape 3730×3292; transform 100 m from (243350, 4508550); nodata unset; every cell finite; range [0,1]; 37,654 positive cells. SHA-256 matches the recorded digest. This verifies file-level portal-range safety, not a fresh comparison to the missing competition template.

### Pass 2 — defects and protocol audit

1. **The live recommendation was overconfident.** README, home page, and submission page called the R6 file “OK TO DOWNLOAD AND SUBMIT” and “PROMOTE.” The run card's primary promotion comparison is SGMC off-catalogue, while the card's own catalogue hide-and-recover result is lower than its incumbent: **[HOLDOUT-DTI, `gems32.holdout` draws 20/21, 4 quadrants × 2 draws, 22,232 withheld positives, 95% cluster-bootstrap CI]** candidate 0.00338 [0.00251, 0.00453] vs incumbent 0.00452 [0.00394, 0.00525]. The SGMC test is not a substitute for the specified hide-and-recover gate.
2. **The historical B=2 mask is not fold-isolated.** `scripts/run_round6.py` constructs eligibility from the full `labels` raster (`distance_transform_edt(~labels)`) before calling the holdout evaluator. The evaluator masks visible faults, but it cannot undo the fact that candidate placement already used withheld catalogue locations. The required feature derivation/emission must be repeated inside each fold using only visible faults; this run does not show that.
3. **The current lane is absent.** The prompt says this session's lane is a single method paragraph below, but no such paragraph is included. Per `docs/research/standing-brief-20261025.md`, this is a stop condition, not permission to adopt the prior session's R6-1 lane.
4. **Local reproducibility is incomplete.** The pinned competition rasters and feature cache are not present in this checkout. The TIF can be checked standalone, but its CRS/shape/transform cannot be compared against a fresh sample-submission file today.
5. **Documentation conflicted.** README contained a green Round-6 recommendation followed by a “superseded” section whose body still said “OK TO DOWNLOAD AND SUBMIT.” Generated pages repeated multiple download/upload blocks, including a malformed duplicated submission identifier. The old strict gate helper correctly fails the literal overlap rule but the current promotion page didn't reflect the current-session authorization decision.
6. **Test environment was missing dependencies.** System Python had no pytest/Rasterio. A local ignored `.venv` was created and requirements installed; the tests are now runnable without changing tracked dependencies.

### Pass 3 — changes made and final state

- Added `evidence/current_release_review.json` as the session-scoped fail-closed decision record. It preserves, rather than rewrites, the historical Round-6 card and separates byte-format validation from scientific validation and submission authorization.
- Updated generated-site logic and tests so a missing/negative current authorization suppresses green approval and upload instructions; the retained TIF is identified only as an audit artifact.
- Rewrote the README decision section to say **DO NOT SUBMIT** and point to the current review, rather than leaving contradictory historical launch copy.
- Added this review and a ranked list of next hypotheses. No candidate was rebuilt, no weekly slot was used, and no organizer score is claimed.

## Focus-site executive summary — reported score claims

The following values are **OWNER-REPORT** scores taken from the project brief/site records; there is no submission-page receipt in this repository that cryptographically links those scores to the archived file bytes. Use the linked nine-site table for exact filenames, relationships and notes: [`focus-sites-executive-summary.md`](focus-sites-executive-summary.md).

| Site | Highest reported submission | OWNER-REPORT score | Recommendation |
|---|---|---:|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5` | 0.2477 | Do not resubmit; superseded within the same thinning family. |
| GEMSDOE25 | `dotted-h19-5-d2-8` | 0.2600 | Do not resubmit; parent of stronger sparse descendants. |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5` | 0.2449 | Do not resubmit; its reported parent scores higher. |
| GEMSDOE28 | `h36-1-rung30-blind-r1` | 0.2710 | Highest listed on that site; same family as nearby variants; already scored per brief. |
| GEMSDOE30 | `d28-poisson300m-offcat-44090` | 0.2600 | Do not resubmit; recorded as dot-identical to GEMSDOE25 D2.8. |
| GEMSDOE31 | `h27-4-solo-d28` | 0.2708 | Do not resubmit; same sparse lineage as GEMSDOE28 solo. |
| GEMSDOE32 | `h33-h33-2-b2` | 0.2778 | Group's highest reported file; no receipt in checkout; already submitted per brief. |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30` | 0.2632 | Do not resubmit; reported below the GEMSDOE32 champion. |
| GEMSDOE36 | `anderson-geothermal-pinn-38854` | 0.2750 | Do not resubmit; recorded as champion plus 1,200 additional dots. |

### Why the GEMSDOE32 file was reported at 0.2778

The repository's forensic account says that the high-scoring family was a sequence of sparse versions of the same H19-5 multiline field. The D2.8 → B=1 → B=2 steps removed dots near mapped-fault traces; under the reported competition scoring rule, known-fault pixels are excluded, so these additions could add little true-positive credit while still increasing false-positive mass. This is a plausible denominator-thrift explanation, supported by the recorded nested-dot comparisons and sibling scores, but the exact `0.2778` attribution remains **OWNER-REPORT** without the portal receipt. It does not show that the candidate detects geothermal vents directly, nor does it establish that similar pruning generalizes to unseen labels.

## Untried hypotheses to preregister next

Ranking is qualitative (expected value relative to cost), not a score prediction. No new experiments were run in this review.

| Rank | Hypothesis / layers | Target signature | Why it might find missing faults | Difference from current implementations | Expected DTI improvement (qualitative, not a score projection) | Cost / data status |
|---|---|---|---|---|---|---|
| 1 | **Potential-field phase pairing** — GeoDAWN magnetic `tmi`/`rtp` and gravity `iso_grav_anom` | Cross-gradient orientation agreement plus paired curvature zero-crossings | A buried basement offset may perturb density and susceptibility together without a surface scarp; test whether coherent relative phase is more selective than either edge magnitude alone. | Prior PF-only work used edge magnitudes and persistence, not a two-field relational phase test. | Moderate upside if paired phase suppresses lithologic edges while retaining fault edges; entirely untested here. | Medium; feature bands were present in the prior mirror stack, but the stack is absent from this checkout. |
| 2 | **Nuisance-residualised conductivity lineaments** — `cond_surf`, elevation/relief, and `depth_to_base_surf` | Spatially cross-fitted elevation/relief residual followed by directional ridge/edge extraction | Conductivity associated with hydrothermal alteration could persist after topographic covariance is removed; saline playa/alluvial sediments are an explicit nonfault mimic. | Earlier fused models used raw conductivity channels; residualise nuisance factors before extracting structure. | Low-to-moderate upside; may reduce false positives more than increase recall; untested, no score estimate. | Medium; requires fold-local fitting and a cache-backed repeatable stack, both absent here. |
| 3 | **Native-resolution scarplet-chain vote** — official USGS 3DEP 1 m DEM tiles named by the competition link table | En-échelon short scarps with aligned strike and bounded along-strike gaps | A chain of weak scarplets can mark a concealed relay even when individual 100 m pixels are below threshold. | Existing local work uses 100 m LiDAR derivatives, not native 1 m segment-chain geometry. | Potentially moderate for surface-expressed blind scarps, near-zero for fully buried faults; untested. | High; external DEM tiles are not present. Specific official source: [USGS 3DEP](https://www.usgs.gov/3d-elevation-program); confirm egress/data availability before treating viable. |
| 4 | **Relocated microseismicity lineaments** — official USGS ComCat/FDSN event locations | Depth/strike-coherent hypocentre clusters and uncertainty-aware line fitting | Active unmapped structures can be illuminated by event locations, unlike the heavily smoothed seismic feature bands. | No relocated event point-cloud model is recorded here; previous seismic features were gridded/smoothed. | Potentially high in active segments, but spatial/temporal coverage may be sparse; untested. | High and externally blocked in the prior run; source: [USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/). Verify coverage/accuracy and free access before use. |

**Eligibility caveat:** the current prompt contains no method paragraph, so this list is a planning backlog, not the current lane authorization. Select one method in the next session's prompt, then freeze it before testing. Avoid unverified expected DTI ranges.

## Leaderboard freshness and conflicting values

The prompt cites **0.4413** and later says **0.3195** is the current public high. They cannot both describe the same snapshot. The repository history provides a plausible date explanation: it records **0.3195** in an early-October 2026 snapshot and **0.4413** in a page read dated 2026-10-25. The official page was read at `2026-10-26T04:32:28Z`; it showed `xiaofanhu` at `0.4437`. This is the latest timestamped public observation stored here, not a score for our team or a final/private-round result.

## Highest-priority follow-up

1. Supply an explicit single-lane paragraph and preregister the method.
2. Restore/hash-verify the competition template, labels, feature stack, and cached feature products.
3. Repair the shared evaluator once: each fold must recompute catalogue-derived masks/features using only its visible fault segments, apply the visible-fault pixel-exact mask, and emit the candidate inside that fold. Compare candidate and incumbent on exactly the same folds, pooled DTI, stated withheld-positive count, and uncertainty interval.
4. Run each feature-alone leakage canary before candidate combination; stop on AUC >0.90 unless leakage is specifically disproved.
5. Run surface registry comparison before placement and final-dot comparison after placement. Record duplicate and negative results; do not create a promotion based on an alternative proxy alone.
6. Re-read the submission file after writing and compare CRS, shape, transform, band count, dtype, values, nodata behavior and SHA-256 against the restored sample template. Keep all-finite [0,1] output if portal behavior requires it, while separately documenting any divergence from written outside-footprint format.
7. Only after all gates pass, a separate selector checks the authenticated weekly cap and decides whether to spend a real slot. Record the submission receipt and score as **ORGANIZER-CONFIRMED** only when that receipt exists.

## Official references for manual review

- [DOE GEMS competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition rules, NLR/DOE PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Organizer reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [DOE Geothermal Data Repository, INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
- [USGS FDSN Event API](https://earthquake.usgs.gov/fdsnws/event/1/)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
