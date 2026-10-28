# Repository review — 2026-10-28

## Executive decision

**No new TIF is authorized for competition upload.** This review generated no raster and spent no weekly slot. The current branch does not contain the shared feature-stack caches or the named reusable evaluator/writer entry points `evaluate_holdout.py` and `submission_writer.py`; the locally recorded 2026-10-28 audit also states that the method lane is unspecified. Starting a new modelling experiment would therefore violate the lane/reuse protocol and would not produce compliant holdout evidence. Existing downloads are research/audit artifacts unless an explicit release record says otherwise; current release decision is negative.

## Nine-site review table

The table is a **repository-audit comparison**, not an estimate of DrivenData scores. `static hide/recover` values below are historical local diagnostics recorded in `evidence/nine_site_refreshed_audit_20261028.json`; they are not organizer-confirmed scores and are not comparable to leaderboard results. The only stated leaderboard score here is the owner-reported 0.2778 for the GEMSDOE32 H33-B2 file; the repository notes there is no submission receipt tying that score to those exact bytes. No score is inferred from these local numbers.

| Site | Audited download (relative path) | Historical local hide/recover diagnostic | Exact 3-px overlap with H33-B2 | Unique vs all registries? | Download / submit decision |
|---|---|---:|---:|---|---|
| GEMSDOE24 | `docs/downloads/gems24-tmcg-b-decoupled-basin-20261027T113937Z-6f8d042d5ee4-zeros.tif` | 0.041188 | 30.14% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE25 | `docs/downloads/gems25-obj-bin-greedy-k3p5-20261026-3646faf70507-zeros.tif` | 0.004531 | 32.03% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE27 | `docs/downloads/research/gems27-h33-bss-complement-20261027-9ba8480691ed-allfinite.tif` | 0.008514 | 0.00% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE28 | `docs/downloads/gems28-s22-ctxhgb-20261026-e23dabcec6e2-allfinite.tif` | 0.017036 | 42.05% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE30 | `docs/research/2026-10-26-fflidar/gems30-FFL1-fusion_edge-44090-20261026-eacd73e854a3.tif` | 0.001275 | 46.33% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE31 | `docs/downloads/gemsdoe31-tgtd-submod-37654-20261025-ab35d4e8-zeros.tif` | 0.000002 | 39.51% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE32 | `docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.004515 | 100.00% (itself) | No: it is the exact reference | Research/reference only; do not resubmit |
| GEMSDOE33 | `docs/downloads/gemsdoe33-a33-r5-thkcond-37654-20261027-f47ef136b543-zeros.tif` | 0.002656 | 15.20% | Not established by this focus-only comparison | Audit only / no |
| GEMSDOE36 | `docs/downloads/gemsdoe36-tcd36-exp2-20261027-9970b80c6585-zeros.tif` | 0.002931 | 56.99% | Not established by this focus-only comparison | Audit only / no |

**How to read this:** the within-3-px percentages test only overlap against H33-B2, not the parallel-run rule against every raster. The source JSON does include much broader registry comparisons for those individual audited files, but its sampled “inspected_path” is not necessarily the owner-reported highest leaderboard submission named in the supplied prompt. Consequently this table does not certify cross-registry uniqueness or identify a unique contest winner for any sibling site. The audit reports `GEMSDOE25` and `GEMSDOE30` have identical footprint predictions in another comparison; that is an irregularity requiring review, not evidence that their score claims are equivalent.

## Why H33-B2 is the highest reported focus-site result

The submitted score claim in the user-provided history is **0.2778 (OWNER-REPORT; no organizer receipt present in this repo)**. A plausible mechanism is that the B-pruning sequence reduces predictions near already-catalogued faults (excluded from scoring), while retaining selected off-catalogue targets. This is a hypothesis about score mechanics, not proof of why the hidden competition labels rewarded those pixels. The same file's historical holdout diagnostics are low under local hide/recover protocols; those metrics have evaluator/version differences and must not be portrayed as a forecast or organizer score. The latest public leaderboard snapshots in repo evidence are dated 2026-10-28 and reported a top score of 0.4544 at capture time; the live leaderboard must be fetched again before describing that as current.

## Candidate hypotheses for a later, explicitly assigned lane

These are preregistration ideas only. Novelty is **not established** by this review, because the explicit lane paragraph is absent and the codebase is too large for a reliable negative search over all prior work. Do not implement one until the task assigns a single lane and its features/evaluator can be reused. No leaderboard score projection is provided.

| Priority for investigation | Geological signal / layers | Why it might emphasize uncatalogued faults | Main confounder | Data & cost |
|---|---|---|---|---|
| 1 | Scale-space directional curvature of the existing 1 m DEM, paired with orientation persistence across scales | Persistent linear scarps or subtle flexures may mark unmapped structures while downweighting short noisy edges; test only after excluding visible catalogue segments within each fold | Lithologic boundaries, roads, terrace margins | Existing DEM-derived stack if present; medium computation; no external data presumed |
| 2 | Multi-scale edge coherence between magnetic TMI derivatives and radiometric K/Th/U boundaries from GeoDAWN layers | Independent geophysical boundaries that align over multiple scales may support concealed structure away from mapped traces | Survey seams, alteration/lithology boundaries, cultural magnetic noise | Existing GeoDAWN layers if cached; medium/high preprocessing; data availability not verified in this checkout |
| 3 | Local drainage deflection / channel-network orientation discontinuity from DEM hydrology | Fault-controlled drainage can reveal structures not mapped from field exposure, especially in arid terrain | Lithologic contrasts, fan channels, roads, ephemeral stream migration | DEM-derived hydrology; medium computation; no new source required if DEM cache exists |
| 4 | Geophysical lineament termination/intersection density from multi-band magnetic/radiometric gradients | Fault tips and stepovers can concentrate intersections and may be more diagnostic of new structures than generic lineament density | Survey artifacts, contact intersections, noise | Existing numerical GeoDAWN features; medium/high and must be tested feature-by-feature for leakage |

The requested feature-alone leakage canary (AUC >0.90 alarm), buffered whole-segment holdout, exact visible-fault masking, pooled DTI and uniqueness checks were **not run** because the lane, caches and matching reusable scripts are not present. Official external-data source checks were not needed for these four cache-dependent ideas and none is called viable until the local cache manifest confirms the layers exist.

## Three-pass review and verification

1. **Pass 1 — inspect:** read the standing request, current release review, 2026-10-28 nine-site audit, current run card, dataset manifest, and source tree. Confirmed existing site/release documentation already labels the latest H51 artifact `negative` and explicitly says it is research-only.
2. **Pass 2 — check assumptions:** found the evidence table is a focus-file audit, not a complete verified leaderboard ranking; local hide/recover values are not score estimates; historical score claims lack receipts; uniqueness against H33 alone cannot establish uniqueness against all registries. No release authorization can be inferred from GeoTIFF validity.
3. **Pass 3 — run tests:** installed declared Python requirements in the ignored `.venv` and ran `.venv/bin/python -m pytest -q`: **259 passed, 10 skipped, 62 warnings, 3 subtests passed**. Skips are data-dependent; warnings include a scikit-learn GP length-scale convergence warning and Rasterio affine deprecation warnings. No experiment or TIF build was run.

## Blockers and next work

- Assign one explicit scientific method paragraph/lane, or explicitly revise the protocol to permit candidate screening.
- Restore/cache the competition feature stack and confirm canonical shared tools (`evaluate_holdout.py`, `submission_writer.py`) exist or identify their actual shared equivalents. Competition labels/data may require DrivenData authentication; do not claim data access.
- Resolve the literal calibration-lattice uniqueness contradiction using an explicit, principled registry policy; do not silently exempt it. Existing `evidence/focus_review_20261028.json` records a severe dense-map feasibility bound.
- Re-audit each target site's claimed top submission against organizer receipts and full raster registry before presenting it as a verified winner.
- Recheck exact CRS/shape/transform against an authenticated official sample template before any future authorization. Current negative release review explicitly says the H51 file's reference template was not verified in that review.
- Keep current submission status fail-closed; a high local holdout result is not a submission score and does not override uniqueness gates or the weekly slot selector.

## Audit run card (review only; no experiment)

```json
{
  "hypothesis": "No experiment: audit the nine-site repository evidence without asserting unavailable leaderboard outcomes.",
  "mechanism": "Read-only provenance, release-state and test-suite review; no map emission or score modelling.",
  "named_non_fault_mimic": "Lithologic contacts, survey seams and drainage/landform boundaries can mimic fault signals.",
  "holdout_dti": null,
  "holdout_label": "NOT RUN — no assigned lane or available shared feature caches/evaluator.",
  "correlation_overlap_vs_registry": "No new candidate surface/dots; per-file historical audit is not a new all-registry pass.",
  "raster_sha256": null,
  "validator_output": "No new TIFF generated; therefore not applicable.",
  "submission_name": null,
  "submission_note": "No submission generated; no upload authorized.",
  "verdict": "negative"
}
```
