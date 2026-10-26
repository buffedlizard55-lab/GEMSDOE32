# Three-pass repository review, H46 negative result, and nine-site executive summary

**Review date:** 2026-10-26 UTC
**Branch:** `arena/7e63e67a-gemsdoe32`
**Decision:** **No new file is authorized for a DrivenData submission.** The H46 GeoTIFF is available for research/audit only. **Do not upload it.**
**Weekly slots used:** `0`.

## Executive decision — download status and score estimate

| File | Estimate / evidence | Unique? | Decision |
|---|---|---|---|
| [`gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-zeros.tif`](../downloads/gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-zeros.tif) · [single-TIFF ZIP](../downloads/gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-zeros.zip) · [saved-byte audit](../downloads/gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-audit.json) · [run card](../../evidence/h46_trhv_run_card.json) | **Exploratory `HOLDOUT-DTI = 0.109361`**, `GEMSDOE32-HIDE-RECOVER-v3.0`, `22,232` withheld positives, 95% spatial-block CI `[0.094695, 0.122341]`. This is **not a leaderboard projection**. It is below the prior same-evaluator H38 result `0.116958 [0.100533, 0.132040]`; H38 paired bootstrap draws are not archived, so no paired difference is asserted. Auxiliary **`HOLDOUT-DTI` SGMC-cal v3.0** is `0.044756 [0.039243, 0.050114]` on `62,703` proxy positives, below the Champion `0.064121`. | **Yes against the nine historical winner masks:** each directional overlap is `47.84–54.58%` within 3 px; continuous-surface maximum `|Spearman| = 0.166685`. **No under the literal full-registry rule:** `99.267%` of dots are within 3 px of the registered 5-px calibration lattice (`>70%` stop). | **DOWNLOAD: YES, research/audit only. SUBMIT: NO.** In addition to the lattice failure and lower-than-H38 holdout point, the prompt’s required method paragraph was not present and the executed settings diverged from the frozen preregistration. The observed DTI is descriptive, not admissible promotion evidence. |

**Portal name:** `GEMSDOE32-H46-TRHV-6437B275`
**Note (`80/140` characters):** `H46-1 TRHV 2-regime vent+TIGER 37654d B2 | HR=0.1094 SGMC=0.0448 | DO NOT SUBMIT`
**SHA-256:** `9f42346d3acecb8d873fb35c70d988ae0afeb99781c6104c644d8cf9f85e0dc3`
**Saved-byte validator:** PASS locally — one `float32` band, `EPSG:32611`, `3730×3292`, exact template transform `[100,0,243350,0,-100,4508550]`, `nodata=None`, all `12,279,160` cells finite in `[0,1]`, no NaN anywhere, `37,654` positive cells and zero on-catalogue cells. `check_submission.py --strict-finite` passed; `audit_geotiff` 13 checks passed. This is a local format check, not DrivenData acceptance.

## Portfolio recommendation

- **Best historical score supplied for the nine sites:** GEMSDOE32 `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`, **`0.2778 OWNER-REPORTED`**. It is already reported as submitted; do not resubmit. No submission-page receipt in this checkout binds the number to those exact bytes.
- **Best new file to submit now:** **none**. The H46 file is downloadable for audit but not cleared. No public-leaderboard score is estimated from a local holdout score.
- The prompt’s `0.3195` and `0.4413` figures are historical/undated inputs. The repository contains a timestamped public-page read of `0.4437` at `2026-10-26T04:32:28Z`; that observation is stale relative to this review and is not a score for this team. See [`evidence/live_leaderboard_snapshot_20261026.json`](../../evidence/live_leaderboard_snapshot_20261026.json) and the [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).

## Nine-site table — highest historical file supplied for each site

Historical values below are **OWNER-REPORTED**, not `ORGANIZER-CONFIRMED`; the exact file links point to pinned sibling-repository commits recorded in [`registry/focus_registry_manifest.json`](../../registry/focus_registry_manifest.json). The score is not a holdout estimate. For the pairwise test, “within 3 px” means a source prediction is within Euclidean distance `<=3` raster pixels of a positive pixel in the reference mask; the test is directional and uses the full raster grid without resampling.

| Site | Highest historical file (pinned bytes) | Historical reported score | Unique relative to the other eight historical winners? |
|---|---|---:|---|
| **GEMSDOE24** | [`gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif`](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/e6b2edbfab141d13b23a79117bf957ea2040c281/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif) · 60,069 dots | **0.2477 OWNER-REPORTED** | **No** — `100%` directed overlap with at least one other historical winner. |
| **GEMSDOE25** | [`gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif`](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/ece220432d7cec9af8d246959146245c9dceb1c1/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif) · 44,090 dots | **0.2600 OWNER-REPORTED** | **No** — pixel-identical dot mask to GEMSDOE30 (XOR `0`). |
| **GEMSDOE27** | [`gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-allfinite.tif`](https://github.com/buffedlizard55-lab/GEMSDOE27/blob/cf8b4c201f2cc2ef649b6ca7cd32f235c2f6743a/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-allfinite.tif) · 61,328 dots | **0.2449 OWNER-REPORTED** | **No** — lowest overlap in the nine-winner matrix is still `86.72%` (vs GEMSDOE32). |
| **GEMSDOE28** | [`gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif`](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/12ec4fea4c97a7887a7ca8a06f9bd94c7609ea07/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif) · 37,660 dots | **0.2710 OWNER-REPORTED** | **No** — `100%` directed overlap with at least one historical winner. |
| **GEMSDOE30** | [`gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif`](https://github.com/buffedlizard55-lab/GEMSDOE30/blob/35ce8911e2c3287eed973eacd12c252e8cb3f34c/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca-nanoutside.tif) · 44,090 dots | **0.2600 OWNER-REPORTED** | **No** — exact dot-mask duplicate of GEMSDOE25. |
| **GEMSDOE31** | [`gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif`](https://github.com/buffedlizard55-lab/GEMSDOE31/blob/8e91d82ae236c92b917302122237e45fc20ec337/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif) · 40,199 dots | **0.2708 OWNER-REPORTED** | **No** — B1 parent; the GEMSDOE32 B2 mask is its strict subset (2,545 fewer positives). |
| **GEMSDOE32** | [`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/8310370d041f6737952063b197ac9967652e9629/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) · 37,654 dots | **0.2778 OWNER-REPORTED** | **No** — `100%` directed overlap with several winner masks; its H19-5 pruning family is not independent. |
| **GEMSDOE33** | [`GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif`](https://github.com/buffedlizard55-lab/GEMSDOE33/blob/0384d793b5a23151425f45505ac745b54f84c7c9/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e-nanoutside.tif) · 41,865 dots | **0.2632 OWNER-REPORTED** | **No** — `92.62%` directed overlap with GEMSDOE32. |
| **GEMSDOE36** | [`gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif`](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/2c78770e0544259082b0b6b73ce8e4d0749c175d/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif) · 38,854 dots | **0.2750 OWNER-REPORTED** | **No** — contains all GEMSDOE32 B2 dots plus 1,200 additions (XOR `1,200`). |

Machine-readable byte-level audit: [`evidence/focus_site_winner_overlap_20261026.json`](../../evidence/focus_site_winner_overlap_20261026.json). Its 3-px directional rule is the user's requested threshold. The exact `GEMSDOE25`/`GEMSDOE30` mask identity and the GEMSDOE31→GEMSDOE32 and GEMSDOE32→GEMSDOE36 subset relations are direct raster-byte comparisons; scores remain owner claims.

## Why the historical H33 B2 file could score above thicker H19-5 descendants

The competition’s published Distance-Weighted Tversky Index uses `alpha=0.2`, `beta=0.8`, and a 300 m triangular distance kernel. In code and algebra:

`DTI = TP_w / (TP_w + 0.2*FP_w + 0.8*FN_w) = T / (0.2*(T + S - M) + 0.8*|G|)`

where `T=TP_w`, `S` is emitted prediction mass, `M` is the prediction-weighted kernel proximity to ground truth, and `|G|` is hidden truth mass. The site masks show a dense `H19-5` line-ribbon and progressively thinner descendants. The owner-reported score sequence (`0.1922 → 0.2477 → 0.2600 → 0.2708 → 0.2778`) is consistent with removing redundant or low-marginal-credit mass while preserving useful coverage. Known catalogue faults are excluded from scoring per organizer clarification, which makes catalogue-flank pruning plausible. This is a metric-consistent hypothesis, not causal proof: the hidden test truth and score-to-hash organizer receipts are not in this checkout.

## H46-1 result — what was measured and why it cannot be promoted

### Preregistered hypotheses and data

Five ranked hypotheses and physical mimics are in [`h46-trhv-preregistration-20261026.md`](h46-trhv-preregistration-20261026.md). H46-1 combined cached 35-channel features and 20-channel SPCP transforms with 8 proposed label-free channels: GDR #1391 2-m thermal observations, paleo-geothermal feature points, a TIGER/Line road-distance raster, magnetic upward-continuation persistence, and derived couplings. The code reads no catalogue distance field from the GDR CSV; the active fault catalogue enters only through fold-local visible labels, fault-tip terms, and B=2 visible-catalogue gates.

**Provenance limitation:** the extra GDR and Census-derived TIFF files were restored from a pinned owner-hosted GitHub mirror and SHA-256 checked against the modified `registry/data_manifest.json`. The links below are official sources, but the actual official-host downloads were not performed in this sandbox; the hashes demonstrate mirror-byte consistency, not official-host authenticity. `data/restore_receipt.json` now records 26 verified manifest entries.

### Three frozen arms and local results

The completed execution tested the three registered detector/allocation arms (one main hyperparameter setting each): 63-channel exposed-regime classifier (`EXP1`), 63-channel vent-coupled SAR-PU (`EXP2`), and sequential two-regime residual-coverage allocation (`EXP3`). The leakage canary tested 63 channels and passed (maximum oriented AUC `0.586868 <= 0.90`). Results from the executed, later-found-to-deviate implementation are recorded as **exploratory**:

| Arm | `HOLDOUT-DTI` (`GEMSDOE32-HIDE-RECOVER-v3.0`, 22,232 withheld positives, 95% CI) | Off-catalogue diagnostic (`GEMSDOE32-SGMC-CAL-v3.0`, 62,703 positives, calibrated 95% CI) |
|---|---|---|
| Fold-collared D2.8/B2 Champion proxy | `0.099202 [0.085951, 0.112668]` | `0.064121 [0.056730, 0.071649]` |
| `EXP1_H46_EXPOSED63` | `0.117156 [0.101181, 0.131227]` | `0.049800 [0.043400, 0.057083]` |
| `EXP2_H46_VENT_SARPU63` | `0.065944 [0.056916, 0.075357]` | `0.074530 [0.064466, 0.084000]` |
| `EXP3_H46_TRHV_TWOREGIME` (executed as 72/28, not preregistered 70/30) | **`0.109361 [0.094695, 0.122341]`** | **`0.044756 [0.039243, 0.050114]`** |
| Prior repo best H38 (same evaluator/population, prior run-card receipt) | **`0.116958 [0.100533, 0.132040]`** | — |

`EXP3` beats the fold-collared D2.8/B2 Champion proxy on paired primary holdout (`+0.010263 [0.001136, 0.019022]`), but its point estimate is below H38 (`−0.007597`), no paired H38 bootstrap is archived, and its calibrated off-catalogue diagnostic loses to the Champion (`paired delta −0.019268 [−0.025711, −0.012319]`). Neither local metric is a leaderboard-score prediction.

### Protocol / implementation irregularities — hard stop

1. **No assigned method paragraph.** The standing brief requires a single explicit lane paragraph; the active prompt context and standing README do not contain it. H46 was selected from a previous README next-step suggestion, so its lane is **not protocol-authorized**. No slot was used.
2. **Preregistration deviations.** The frozen plan specified `70/30` dot allocation (`26,358/11,296`), `F2mDAB > 1 °C`, `T2m−T1m`, and a `150 m` TIGER road scale. The completed H46 output used `72/28` (`27,111/10,543`), positive F2mDAB values above `0`, `T2m−T15m` (the mirrored schema calls T15m 1.5 m), and `180 m`. The run therefore does not test the frozen exact hypothesis.
3. **Point-boundary defect discovered after the completed run.** The first H46 point rasterizer kept a 24-px exterior margin but clipped outside-footprint station/deposit coordinates onto the raster edge before smoothing. The parsed probe mirror contains 3,800 records: 2,782 fall inside the exact footprint and 659 additional points are within the 24-px padding; the parsed paleo-feature mirror contains 709 records: 281 in-footprint and 121 additional points in the padding. The executed code clipped those outside points and then smoothed them, potentially creating artificial boundary plumes. `src/gems32/trhv.py` now filters inputs to the exact finite template footprint before rasterization, but the feature stack was not rebuilt and corrected code was not rerun. The saved raster and all H46 performance results still correspond to the pre-fix implementation.
4. **Literal registry gate fails.** Against `339` pinned focus-site raster entries (`321` unique hash/grid-comparable rasters), the pre-placement surface’s max genuine-registry `|Spearman|` is `0.166685` and max genuine final-dots overlap is `66.5587%`; both are below their thresholds. But `99.267%` of final dots are within 3 px of the spacing-5 calibration lattice, so the user’s literal no-exemption `70%` final overlap rule fails. No density exception was applied.
5. **Historical winner family is not novel.** The nine historical winner masks have a minimum pairwise directed 3-px overlap of `86.718954%`; all therefore fail the same 70% novelty rule relative to at least one other focus-site winner. This is why “different filename” or a unique hash is not enough.

### H46 validator and naming

- File name: `gemsdoe32-h46-trhv-tworegime-ventconduit-37654-20261026T173000Z-6437b275-zeros.tif`
- Submission name: `GEMSDOE32-H46-TRHV-6437B275`
- Note (80/140): `H46-1 TRHV 2-regime vent+TIGER 37654d B2 | HR=0.1094 SGMC=0.0448 | DO NOT SUBMIT`
- Raster SHA-256: `9f42346d3acecb8d873fb35c70d988ae0afeb99781c6104c644d8cf9f85e0dc3`
- Format: strict CLI and 13-check local GeoTIFF audit passed (`EPSG:32611`, `3730×3292`, exact template transform, one float32 band, all `12,279,160` values finite in `[0,1]`, no NaN, zero catalogue positives). This only means the saved bytes satisfy the local format checker; it does not mean submission is allowed or accepted.

## Three-pass review

### Pass 1 — implement/review against the request

- Read the standing README prompt, project state, source manifests, prior run cards, writer, validator, metric, holdout evaluator, and site builder.
- Restored the 26 SHA-pinned manifest files (including the three H46 external mirrors); prepared the 19-band data and reused the cached 35-channel feature stack. Refreshing the nine focus-site registry produced 339 raster entries with zero fetch failures at pinned refs.
- Generated a new label-free TRHV feature stack, executed three planned arms, wrote a unique hash-named GeoTIFF bundle, ran strict saved-byte validation, evaluated both holdout instruments, and compared the surface/final mask to the registry. No weekly slot was used.

### Pass 2 — bug and edge-case review

- The first TRHV feature-builder invocation expected `example_submission.tif`, while the restored dataset names the template `sample_submission.tif`; the shared builder now prefers the actual sample filename with a legacy fallback.
- `scripts/run_h46_trhv.py` now fails closed unless an explicit `GEMSDOE32_ASSIGNED_LANE_ID=H46-1-TRHV` authorization is present; the current prompt does not supply it, so this runner must not be rerun as-is.
- Fixed shared `src/gems32/emitter.py`: the published `rho` option-value parameter previously computed a lower `alpha*prior_dti/(1+rho)` bar but its acceptance inequality still used unadjusted alpha; `exact_greedy` also computed and ignored the bar. New tests verify both paths. Added `initial_mask` support for pre-seeded residual-coverage CELF; its disjointness and exact marginal coverage are tested. This code repair preceded the completed H46 run.
- A later audit found the H46 point-clipping defect and the frozen/actual setting mismatches above. These are explicitly disclosed; the candidate is not silently relabeled as a clean preregistered pass. The shared TRHV builder now excludes exterior points from rasterization, and the runner’s next-run defaults were aligned back to the frozen 70/30, `F2mDAB > 1 °C`, and 150 m settings. The H46 trial was not rerun after these changes because the assigned lane is missing and the three-arm experimental budget had been used.
- Compared H46 against H38’s prior same-version `HOLDOUT-DTI`: H46’s point is lower. No paired confidence interval against H38 is claimed because no matching bootstrap draws are archived.

### Pass 3 — final requirement check

- **Unique TIFF generated:** yes, new mask/hash, never copied from another submission. **OK to download for audit:** yes. **OK to submit:** no.
- **Score labeling:** historical values remain `OWNER-REPORTED`; local values are explicitly `HOLDOUT-DTI` with evaluator, withheld-positive count, and CI; there is no leaderboard projection and no `ORGANIZER-CONFIRMED` score for the new file.
- **Novelty:** passes the nine genuine historical winner comparisons, fails the literal all-registry lattice check. This is a stop, not an exemption.
- **Format:** saved bytes pass local checks; portal acceptance is not tested.
- **Research integrity:** external bytes came from the pinned owner mirror, not a fresh authenticated official-host download. The source links are included for manual review.

## Remaining work / blockers

1. Obtain an explicit single-method lane paragraph/authorization for a future session. Do not continue H46 or another lane by inference.
2. If H46-1 is explicitly re-authorized, execute only the preregistered `70/30` setting with the corrected point-footprint handling, `F2mDAB > 1 °C`, and the 150 m road scale, then rebuild the feature cache and rerun the 3-arm holdout. Do not select on SGMC alone; compare paired spatial-block bootstrap against H38 and Champion.
3. The literal lattice overlap is near-certain to stop any 37,654-dot candidate. This must be resolved by a prospective protocol revision accepted across lanes, not by silently exempting the calibration grid.
4. Verify official external asset bytes directly from GDR / Census on an allowed, authenticated machine, or keep all claims explicitly pinned to the owner mirror. The current SHA checks prove mirror integrity only.
5. An authenticated submission-page receipt and the visible weekly quota are unavailable here. Never submit or claim a score without them.
6. The repository’s cached public leaderboard snapshot is old; refresh it only through an approved official-source process. Do not treat the user-supplied `0.3195` or `0.4413` as current.

## Manual-review sources

- [DrivenData DOE GEMS overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [DOE/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE GDR #1391 INGENIOUS record](https://gdr.openei.org/submissions/1391) · [DOI](https://doi.org/10.15121/1881483)
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [DOI](https://doi.org/10.5066/P93LGLVQ)
- [US Census TIGER/Line 2024 roads directory](https://www2.census.gov/geo/tiger/TIGER2024/ROADS/)
- [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) · [EPSG:32611](https://epsg.io/32611)
- [Official scoring clarification on known-fault masking](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
