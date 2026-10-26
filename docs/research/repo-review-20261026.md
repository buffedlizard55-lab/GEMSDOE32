# GEMSDOE32 repository review — 2026-10-26

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

The prompt cites **0.4413** and later says **0.3195** is the current public high. They cannot both describe the same snapshot. The repository history provides a plausible date explanation: it records **0.3195** in an early-October 2026 snapshot and **0.4413** in a page read dated 2026-10-25. This review did not retrieve a fresh live page, so **0.4413 is the latest stored observation, not a verified current score**. Refresh and timestamp the official public page before using a leaderboard value in a decision.

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

## Passes for the present review turn (2026-10-26)

### Pass 1 — inspect current state

Read the repository standing brief, generated Pages, source registry, build code, release gate, and test suite. The current release decision remains fail-closed. No feature cache or `data/sample_submission.tif`, labels, or training feature raster is present in the tracked checkout; no experiment or TIF build was attempted.

### Pass 2 — cross-check provenance and generated claims

Found a source-of-truth contradiction in `registry/current_status.json`: the 0.2778 group score was labeled `ORGANIZER-CONFIRMED (owner-reported receipt)` even though `registry/claims.json`, the project irregularity ledger, and the review text explicitly say no submission-page receipt linking those TIFF bytes to that score is archived. Under the standing protocol, an owner report is not organizer-confirmed. Changed the status label to `OWNER-REPORT`, corrected README wording that called it verified, and regenerated the site/feed so the same distinction appears in the published summary. The local hash confirms the archived TIFF bytes, not the organizer's score attribution.

### Pass 3 — verify correction and remaining blockers

Added a regression test that checks the status metadata and owner-claim ledger remain consistent. Ran the site generator and the full suite: **105 passed, 9 skipped, 15 warnings**. Skips depend on absent competition data/cache; they do not represent a fresh end-to-end holdout. The current prompt still supplies no designated single method paragraph, so the lane stop condition remains in force. No candidate TIF was newly generated; existing downloadable rasters are audit/research artifacts and all current release records say **DO NOT SUBMIT**. No weekly submission slot was used.
