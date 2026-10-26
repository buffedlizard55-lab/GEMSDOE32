# Protocol review — 2026-10-25

## Decision first: DO NOT SUBMIT

No new candidate was generated or promoted in this session. No weekly submission slot was used.
The prompt refers to a **single method paragraph**, but supplies none. Choosing a lane ourselves
would violate the parallel-run instruction. Additionally, the literal duplicate gate fails for
both the current registry primary and the prior PF-only result. These are **negative deliverables**,
not permission to recycle an old submission.

[Reproducible byte-level audit](../data/protocol-audit.json):

| Artifact | Format against pinned sample | Fraction within 3 px of registry lattice | Literal decision |
|---|---|---|---|
| H32-WIN registry primary | pass | 0.9967021045779996 | duplicate; STOP |
| Arena41 PF-only | pass | 0.9866415254687417 | duplicate; STOP |

These fractions are geometry diagnostics, not scores. The lattice is dense; this explains why the
rule is difficult to satisfy, but does **not** authorize silently weakening it. The earlier
`evidence/arena41_pass2_audit.json` density exemption is not compliant with this prompt.
Pre-placement surfaces are not present in this checkout; no surface correlation was invented.
The audit only needs one failing registry comparison to stop; it does not claim a complete
all-registry uniqueness pass. Files remain available for audit, not submission approval.

## What explains the reported winner?

The values in the request are **user-reported, unverified**, not ORGANIZER-CONFIRMED receipts.
Neither the reported champion value nor any stated leaderboard maximum was authenticated this
session. The request itself contains conflicting leaderboard snapshots. Do not treat any as current.

Prior byte-level forensic evidence (`evidence/registry_overlap.json`) describes a nested thinning
family, not independent discoveries: H19-5 → dotted d2.8 → solo → H33-2-B2. The prior construction
check identifies the champion as solo with near-catalogue dots removed. This supports a metric
mechanism: removal of low-credit predicted mass can improve the Tversky denominator without
finding additional faults. It does **not** prove which unobserved faults the organizer accepted,
or causally explain every difference between reported submission results.

For an additive perturbation of TP and FP, with FN changing oppositely to TP,
`D = TP / (TP + alpha*FP + beta*FN)`. At alpha+beta=1, adding a dot with expected
truth credit k increases D only if k > alpha*D under the simplifying one-dot, no-interaction
model. Nearest-distance triangular kernels couple neighbouring predictions; the criterion is
not a substitute for rescoring the complete raster. No projection is a competition score.

Higher performance is possible in principle; there is no measured evidence here that a new
method beats the reported champion, let alone the leaderboard. A valid GeoTIFF alone is not
scientific validation. This challenge predicts **fault traces**, not a directly labelled vent map.
A geothermal interpretation remains a downstream hypothesis.

## Ranked hypotheses BEFORE implementation

Ranking is qualitative scientific judgment (not projected DTI). Novelty is relative to the checked-in
feature/model code, **not** a claim that no external team or sibling repo has ever tried it.
All are untested proposals, not approved lanes. Only the top proposal should be tried after a lane
is explicitly assigned. Stop after the user's experiment/time budget, even on negative results.

| Priority / expected benefit / cost | Layers and transform | Missing-fault mechanism | Named non-fault mimic | Difference from this checkout |
|---|---|---|---|---|
| First / plausible / medium | Cached DEM `band12` (confirm band description before use), curvature and ridge channels; signed cross-profile step fit minus smooth hillslope fit, with opposite-direction profile consistency | Buried/weak scarp can retain a repeatable slope break not strong enough for catalogue mapping; no catalogue-distance channel | Lahontan shoreline terrace and road cut | Explicit step-vs-smooth residual and profile sign consistency rather than Hessian ridge magnitude/top-hat alone |
| Second / uncertain / medium | Cached `grav_edge`, `tmi_edge`, `rtp_edge` and their source bands; local axial cross-gradient angle plus paired signed curvature zero crossings | Coincident density/susceptibility offsets might trace a subsurface contact even where no exposed scarp exists | Intrusive contact | Relational phase/sign pairing, not PF-only HGB on edge magnitudes or upward-continuation persistence |
| Third / uncertain / medium-high | Cached conductivity source band (resolve metadata first), `cond_edge`, `depth_grad`, DEM relief; spatially cross-fitted conductivity residual conditional on elevation/relief, then transverse residual ridge | Fluid-altered fracture permeability may have conductive expression independent of topographic mapping bias | Saline playa sediments | Explicit nuisance residualization before edge extraction, not raw conductivity edge fusion |
| Fourth / low-confidence / medium | Cached DEM and `strike_cos`, `strike_sin`, `coherence_s2`; repeatability of signed step orientation across independent terrain strips, suppressing concave drainage junctions | Along-strike repeated weak scarps could persist across disconnected erosional gaps | Bedding-controlled cuestas | Strip-to-strip consistency and drainage null, not tip continuation or ridge thinning |

`src/gems32/features.py`, `pfonly.py`, `h33.py`, `h35_new.py`, and the prior research reports
were the comparison baseline. Band12 is used as DEM in prior local code; the proposal must
verify this against the restored raster descriptions before executing. No proposal here requires
new external data. Physical mechanisms are explicitly hypotheses, not verified detection claims.
The feature cache recorded by `registry/feature_receipt.json` is **not physically present** in
this snapshot; do not call it ready merely because a historical receipt exists.

## Required next experiment (not run)

1. Resolve lane and register hypothesis, fixed budget, incumbent, evaluator commit and paired split seeds.
2. Restore hash-pinned data and the actual shared feature cache. Owner mirror integrity is not proof
   of organizer provenance. Feature receipt footprint and sample footprint differ; resolve which is
   the submission domain before training, rather than silently switching masks.
3. Use the shared holdout: hide whole fault components with spatial buffer; derive every
   catalogue feature from visible faults **within that split**, mask visible pixels exactly.
   A fixed field learned from all labels is not hide-and-recover validation.
4. Run every feature alone on these splits; AUC above the user threshold is a leakage stop.
5. Compare exact full-footprint rank correlation against every registry surface **before placement**.
   Missing surfaces are missing evidence, not zeros. Stop and log on duplicate.
6. Use shared writer and score pooled TP/FP/FN with alpha=0.2, beta=0.8 and 300 m triangular
   support; bootstrap whole spatial blocks, compare incumbent on identical splits. Report
   HOLDOUT-DTI, evaluator version, withheld positives and 95% CI. Repeat final-dot duplicate gate.
7. Require improvement over the current comparable holdout best. Promotion is a selector
   recommendation only; check the authenticated current weekly cap separately. Never submit automatically.

## Verified sources and limits

* [Official organizer reference repository](https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b)
  retrieved with GitHub API this session. Its README explicitly supports CPU training; GPU is
  faster, **not a universal training prerequisite**. Its notebook demonstrates U-Net, Monte Carlo
  patch splits and Tversky loss with alpha=0.2, beta=0.8. This is not evidence that its random
  patch split meets our buffered segment holdout protocol, nor a verification of organizer DTI code.
* [Official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
  and [submission data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/):
  manual-review links only this session; these hosts are outside this sandbox's outbound allowlist.
* [USGS GeoDAWN source](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and),
  [GDR INGENIOUS source](https://gdr.openei.org/submissions/1391), and
  [official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf): provided references,
  not fetched or certified obtainable in this session. No new external-data candidate is marked viable.

No DrivenData authentication, live submission-page cap, organizer receipt, or unrestricted internet
is available. We did restore and hash-check the pinned sample, catalogue, and lattice needed for
this audit via GitHub. Historical `data/restore_receipt.json` records a previous environment;
it is not a statement about every file currently on disk.

## Three passes

* Pass 1: shared geometry validator now checks exact CRS, shape and affine transform; writer
  supplies its template. Strict reusable duplicate and promotion gates added. Reproduced literal
  failures on the primary and previous negative result.
* Pass 2: regression tests cover shifted origin, wrong CRS, dense registry, identical surface,
  undefined correlation, empty registry, missing lane, leakage canary and incompatible evaluation.
  Fractional positive values on known faults now fail the catalogue-zero check too.
* Pass 3: regenerate site with authoritative DO NOT SUBMIT notice above all archived claims,
  rerun tests, inspect diff and audit reproducibility. No fabricated holdout or score.

### Next-session priorities

Supply a real lane paragraph through the session setup, recover the shared cache with provenance,
fix any split-feature visibility issues in the shared evaluator, and run only the assigned experiment.
An explicit protocol revision is needed if the dense-lattice duplicate rule is to change. Do not
apply an unapproved density exemption. Extend CI with full cached-data, registry-surface and
receipt-bound integration tests; keep raw data outside Git.

## Requested nine-site source inventory

All nine owner-authored HTML sources were retrieved through GitHub at immutable commits in this
session. This checks what the sites say, **not** the organizer's scores, served Pages deployment,
or each linked raster. The prior byte-level family audit remains separate evidence. Full commit
and SHA256 inventory: [`sibling_source_review_20261025.json`](../../evidence/sibling_source_review_20261025.json).

| Site | Pinned owner source | Evidence status |
|---|---|---|
| GEMSDOE24 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE24/blob/fc2bc6f350bf5c6ce8da5d7a2ab03578ea1259d1/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE25 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/e40b9b5e3871cb34d138f586bde97f5099658d01/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE27 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE27/blob/cd6bdab32e82c4fd3bcf4ba15294cb11903e84eb/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE28 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE28/blob/e6321461066f89080e3b1bb670d3951ab20d3638/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE30 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE30/blob/3edad3641bcc3d72bd3cd05b77b719297617841c/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE31 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE31/blob/1ffc7ad5467a9860f7eb1554c5888d0bfd15db1e/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE32 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/5786b21a1674b26ee525e8e9bf048e2e0f50fc0e/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE33 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE33/blob/f618cc54773bd9b4d6c2b3ebf78103a05cc10cb6/docs/index.html) | Retrieved; not an organizer receipt |
| GEMSDOE36 | [HTML source](https://github.com/buffedlizard55-lab/GEMSDOE36/blob/c5a8ae7da3bd2fcff5aa5855afd44c7a3346c16f/docs/index.html) | Retrieved; not an organizer receipt |

The current sibling sites themselves contain warnings about the dense-lattice gate and missing
organizer receipts. GEMSDOE28's page explicitly describes the nine-site family and GEMSDOE25
labels the removal explanation as inference. These are corroborating owner narratives, not
independent confirmation of the hidden evaluation truth. New sibling work may have appeared since
this checkout; no claim of worldwide or cross-repository hypothesis novelty is justified.

## Final local verification

`python -m pytest -q` in the project virtual environment: **86 passed, 8 skipped**.
Skipped tests require data/caches not restored for this audit; this is not a full training integration
pass. Warnings are scikit-learn optimizer convergence and rasterio affine deprecation warnings.
`python scripts/audit_release_protocol.py` reproduced both fractions and format receipts on a
second run. `git diff --check` passed. New tests also exercise pre-placement surface-only checking
without dots and rejection of NaN, infinity, out-of-range values and fractional catalogue mass.

The shared validator retains historical-grid fallback for legacy callers and identifies that
fallback explicitly in its receipt; the shared pair writer and this audit pass the real sample
path. Its exact-grid check no longer silently accepts a shifted geotransform. The new gate
functions are available to future training runners; old training scripts have not all been
retrofitted to invoke them. The site's current prohibition applies regardless of old script output.
