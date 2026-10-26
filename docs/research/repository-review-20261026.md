# Repository review — 2026-10-26

## Decision at review time

**No upload is authorized.** The single source of truth is [`registry/current_status.json`](../../registry/current_status.json), rendered by the generated landing and executive-summary pages. Its current decision is `any_file_ok_to_submit: false`. The H50 TIFF is an audit/research artifact, not an upload recommendation. The historical GEMSDOE32 H33-B2 score (`0.2778`) is recorded as owner-reported because the checkout does not contain an organizer receipt binding that score to the raster hash. See the current decision card and run-card evidence before interpreting any measurement.

## Requested nine-site comparison

The existing nine-site audit is [`evidence/nine_site_executive_audit_20261026.json`](../../evidence/nine_site_executive_audit_20261026.json), with file-level byte/hash/overlap checks in [`evidence/focus_site_winner_overlap_20261026.json`](../../evidence/focus_site_winner_overlap_20261026.json) and an executive rendering at [`docs/executive-summary.html`](../executive-summary.html). The reported historical leaders are:

| Site | Highest reported submission | Reported score | Interpretation |
|---|---|---:|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5` | 0.2477 | Owner-reported; same H19-5 thinning family |
| GEMSDOE25 | `dotted-h19-5-d2-8` | 0.2600 | Owner-reported; byte/mask alias of GEMSDOE30 winner |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5` | 0.2449 | Owner-reported; related H19-5 base |
| GEMSDOE28 | `h36-1-rung30-blind-r1` | 0.2710 | Owner-reported; second-highest among the nine |
| GEMSDOE30 | `d28-poisson300m-offcat-44090` | 0.2600 | Owner-reported; identical mask to GEMSDOE25 winner |
| GEMSDOE31 | `h27-4-solo-d28` | 0.2708 | Owner-reported; parent rung in the nested thinning/pruning family |
| GEMSDOE32 | `h33-h33-2-b2` | 0.2778 | Owner-reported; highest among the nine, already submitted |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30` | 0.2632 | Owner-reported; related B2-base variant |
| GEMSDOE36 | `anderson-geothermal-pinn` | 0.2750 | Owner-reported; close superset of GEMSDOE32 mask |

**Do not submit any of these as a new experiment.** They are historical submissions; the audit identifies the nine winners as one highly related lineage rather than nine independent detectors. New files must pass all gates and the separate selector first. The values above are not organizer-confirmed scores and no prospective leaderboard estimate is asserted here.

## Review passes

1. **Pass 1 — repository and status inspection.** Read the standing prompt, current status, nine-site audit, release/run-card evidence, site-builder code, existing open PR/issue summary, and current generated pages. Confirmed the project already has the candidate/protocol evidence and a fail-closed current decision; no remaining authorization to create or promote a submission.
2. **Pass 2 — defect review.** Found an archived H47 section still rendered before newer H50 status on the home and executive pages, despite H47 being superseded. Removed the archived banner generator and its insertion points, and removed the stale generated section from published HTML. This prevents an obsolete file and old estimate from appearing as a current call to action. Added a small regression test for generated pages and builder source.
3. **Pass 3 — checks and boundary conditions.** Rechecked all three landing/executive outputs for the stale H47 banner and current H50/DO-NOT-SUBMIT wording; ran the focused test, Python syntax compilation, repository JSON parse, and `git diff --check`. Full pytest and full site regeneration were attempted but could not run because this sandbox's Python lacks `pytest` and `numpy` (the builder imports numpy). Thus the changed generated pages were updated consistently by removing the superseded section, but a complete dependency-backed rebuild remains unverified here.

## Protocol and limitations

- The standing protocol's single-method lane paragraph is explicitly absent from the recorded prompt. The README says not to infer a lane; therefore no new geological experiment or TIFF was produced in this review. This honors the protocol rather than fabricating authorization or spending a slot.
- The budget is treated as exhausted for this review; no new holdout evaluation was started. Existing H50 evidence is negative and does not justify promotion.
- DrivenData data downloads require authenticated access, which is not available in this sandbox. No claim is made that the full training dataset was fetched or that a new model was trained.
- Public leaderboard observations and all local evaluation values are timestamped/evidence-linked elsewhere. A holdout DTI or surrogate projection is not a competition score.
- There is an already-open PR #34 from a different branch and open issue #37 about probabilistic inputs being silently binarized. This review does not modify or merge unrelated work. The PR for this branch should only contain the stale-banner fix and its regression check.

## Recommended next work

1. Resolve the lane ambiguity by supplying/recording the exact authorized method paragraph, then pre-register one bounded experiment (within protocol cap) before execution.
2. Install the repository dependencies in CI and make `pytest`, complete `scripts/build_site.py` regeneration, and generated-page consistency part of a repeatable check. The current runtime could not run them.
3. Review issue #37 against the shared evaluator/writer and preserve probability values end-to-end; avoid silently converting probabilistic surfaces to binary masks. Fix centrally and add tests only after confirming the intended API semantics.
4. Refresh the sibling-registry raster inventory before any novelty claim, because a missing registry raster makes literal uniqueness fail closed.
5. Keep the prominent `DO NOT SUBMIT` decision until both scientific improvement and literal novelty gates pass and the separate weekly-slot selector approves the candidate.

## Provenance and authoritative links

- Current machine decision: [`registry/current_status.json`](../../registry/current_status.json)
- Nine-site audit: [`evidence/nine_site_executive_audit_20261026.json`](../../evidence/nine_site_executive_audit_20261026.json)
- Byte-level overlap review: [`evidence/focus_site_winner_overlap_20261026.json`](../../evidence/focus_site_winner_overlap_20261026.json)
- Current release review: [`evidence/current_release_review.json`](../../evidence/current_release_review.json)
- Official competition page: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Official problem description: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Official reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
