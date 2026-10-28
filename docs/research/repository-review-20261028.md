# Repository review — 2026-10-28

## Executive decision

**No submission is cleared. Do not upload any raster from this checkout.** The latest registered candidate is H49-1-CGTD, but it is a research/audit artifact: the saved run card records a negative verdict, a same-evaluator result below the repository's best holdout result, and registry-uniqueness stops. The 0.2778 H33-B2 result is an owner-reported score, not an organizer-confirmed receipt tied to the raster hash. The nine-site report appropriately labels historical scores as owner-reported and leaves a new leaderboard-score estimate unavailable.

No geological experiments or new submission rasters were generated during this review. The parallel-run protocol does not identify a clearly assigned new method paragraph/lane, and the existing H49 run already records the three-experiment budget as exhausted. Using a stale or unrelated lane would violate the protocol rather than maximize the probability of a valid result.

## Findings

### Fixed in this review: misleading audit download label

`docs/nine-site-review.html` previously displayed “Download existing H48 TIF” while the link actually pointed to the H49-CGTD raster. Its generated audit card also called the artifact H48. This is a user-facing provenance defect: someone could mistake which raster they downloaded. `scripts/build_review_audit.py` now derives the artifact label from `registry/current_status.json`, renders the matching path and label, updates the report date, and writes a dated 2026-10-28 audit card. A regression test verifies that the visible label, candidate, and link remain aligned.

### High priority: stale or contradictory timestamps

- `docs/data/feed.json` says it was generated at `2026-10-28T02:31:16Z`, while the checked-out commit is titled `feed: refresh 2026-10-28T11:27Z` and committed at `11:27:41Z`. The commit message therefore does not prove that the current feed contents were refreshed at that time.
- `registry/current_status.json` and `evidence/current_release_review.json` say `2026-10-27T23:55:00Z`; the H49 run card they reference says it was generated at `2026-10-28T01:50:43Z`. The run-card time is later than the claimed current-status/review time. The status may have been reconciled afterward without updating its timestamp, but the repository does not establish that. Keep the upload gate closed until the source-of-truth timestamps are regenerated and agree.

### High priority: training data and organizer-grid verification are absent here

There is no local `sample_submission.tif` at `.cache/gems_data/sample_submission.tif`. `scripts/check_submission.py ... --strict-finite` was attempted on H49 and stopped with that missing-template error. The generated review card independently re-read H49's bytes and confirmed a single float32 band, EPSG:32611, shape 3730×3292, transform `[100,0,243350,0,-100,4508550]`, all 12,279,160 cells finite, values in `[0,1]`, and 37,654 positive pixels. Its grid check uses historical constants, not a newly authenticated organizer template. Do not describe that as a complete submission-template validation or an organizer receipt.

The checked-in `data/` directory contains manifests and surrogate logs, not the competition's raw training inputs or cached feature stack. Full feature regeneration and a fresh hide-and-recover run were not possible in this review without restoring the permitted, hash-pinned data mirrors. No DrivenData login is available in this environment to independently confirm the competition submission page, receipts, cap, or score.

### High priority: uniqueness and scientific gates fail closed

The saved H49 card reports a candidate-to-H48 final-dot overlap of 73.33%, above the protocol's 70% maximum, and a 99.45% overlap with the literal calibration lattice. The registry-unicity gate therefore fails even though selected external peer-raster comparisons are below threshold. These reported figures are historical run-card evidence, not newly recalculated in this review. The gate must be applied to every registry raster; do not exempt the lattice or compare only to a curated subset.

H49's recorded primary result is **HOLDOUT-DTI, GEMSDOE32-HIDE-RECOVER-v3.0, 22,232 withheld positives, 95% CI: 0.105043 [0.090781, 0.119402]**. It does not beat the repo's same-evaluator best result listed in the prior run records (H47-1 EXP2: 0.121959), and its paired comparison against the H33-style proxy is not a substitute for beating that best. This is not a projected leaderboard score. The reported H33-B2 0.2778 remains **OWNER-REPORT**, with no submission-page receipt binding that number to the stored H33 raster's SHA-256.

## Focus-site table and provenance

The nine-site page lists historical files at pinned GitHub commits. It does not claim those are current site heads. The reported scores are owner-reported, and “estimated future score” is correctly unavailable: historical leaderboard values and a local holdout DTI are not a calibrated conversion to the live leaderboard. In the pinned historical winner-mask audit, all nine selected masks exceeded the 70% directed 3-pixel overlap stop against at least one other winner (minimum reported directed pairwise overlap 86.72%). This is a strong reason not to recycle them as “unique” submissions.

The current nine-site review page can be audited at [`../nine-site-review.html`](../nine-site-review.html), with the saved pairwise evidence at [`../../evidence/focus_site_winner_overlap_20261026.json`](../../evidence/focus_site_winner_overlap_20261026.json) and the refreshed source manifest at [`../../evidence/nine_site_refreshed_audit_20261027.json`](../../evidence/nine_site_refreshed_audit_20261027.json). The latter's timestamps and its measured static evaluator results are evidence from that saved run; they are not organizer scores.

## Next actions, in order

1. Regenerate the feed and release metadata from a single UTC clock and attach source observation times separately; fail CI if `generated_utc` is older than the commit refresh by the project's allowed tolerance or if a current-status timestamp predates its referenced run card.
2. Restore and verify the hash-pinned data/template inputs, then run the common evaluator and strict submission validator; preserve the evaluator version, withheld-positive count, CI, and byte hashes.
3. Resolve the calibration-lattice false-positive/registry representation question in shared audit code or protocol governance. Do not silently exclude the raster. Keep any fix shared rather than creating a private lane fork.
4. Assign one explicit geological-method lane and remaining experiment budget before doing new science. Propose preregistered hypotheses, run leakage canaries feature-by-feature, and compare to the same-evaluator repository best before considering a slot.
5. Keep “download for audit” separate from “OK to submit.” Only a complete all-gates pass and the separate weekly-slot selector can authorize upload.

Potential hypotheses already recorded for future preregistration include: (a) signed gravity/magnetic displacement parity, (b) directionally asymmetric thermal residual transport, and (c) a compaction-null residual step detector. They are planning ideas, not proven novel methods or validated score gains; first perform the required implementation/registry census and data-availability check. See [`review-and-next-hypotheses-20261027.md`](review-and-next-hypotheses-20261027.md).

## Verification performed

- `python scripts/build_review_audit.py`: passed; re-read the candidate raster and verified its SHA-256 matches the registry. The resulting audit is [`../../evidence/review_audit_20261028.json`](../../evidence/review_audit_20261028.json).
- Focused release/site/regression tests: **38 passed**.
- Complete test suite after the review changes: **221 passed, 10 skipped, 40 warnings, 3 subtests passed**.
- Python `compileall`: passed; `git diff --check`: passed.
- Submission-template validator attempt: **not completed** because the local sample template is absent. This is recorded as a limitation, not a pass.

Warnings are mostly Rasterio affine-operator deprecations plus one scikit-learn GP convergence warning. They did not fail tests, but should be tracked in routine dependency maintenance.
