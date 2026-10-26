> **SUPERSEDED (2026-10-26):** this review was written when data and dependencies were absent. The data has since been restored, the H42 experiment run and its run card written — see [knowledge/05](../../knowledge/05_h42_outcome_instrument_artifact_and_fault_discovery_science_2026-10-25.md) and the status block at the top of the README.

# GEMSDOE32 repository review — 2026-10-25

## Executive finding

This checkout contains substantial prior implementation and evidence, but it does **not** contain the competition source rasters or the cached feature stack needed to execute a fresh holdout and emission build in this environment. As a result, no new raster is generated here: producing one by copying, thinning, rescaling, or otherwise re-encoding a checked-in submission would violate the explicit uniqueness requirement and would not constitute scientifically validated discovery. The existing GeoTIFFs remain prior artifacts, not a new submission recommendation.

The local evidence does not establish an organizer-confirmed score for any checked-in file. In particular, `0.2778` and the stated `0.3195` leaderboard high are user-provided values in this task, not verified here against a submission receipt or a current official leaderboard response. They must not be described as holdout results or as a promise that a new artifact can exceed them.

## What was inspected

- Repository status and current branch (`arena/fb6cbb57-gemsdoe32`); working tree was clean at review start.
- `README.md`, `scripts/run_holdout.py`, `scripts/build_submission.py`, `scripts/check_submission.py`, `src/gems32/features.py`, the holdout/validation/slot-plan evidence and available GeoTIFFs.
- The tracked `data/` directory has only manifests/logs, not source TIFs. `data/restore_receipt.json` records files at the ignored path `/home/user/GEMSDOE32/.cache/gems_data`, but that cache is not present in this checkout. `/tmp/gems32/data` and `/tmp/gems32/work/feature_stack.npy`, the paths hard-coded by the legacy scripts, are also absent.
- Python 3.11 exists, but NumPy, Rasterio, SciPy, scikit-learn and pytest are not installed. Thus neither raster-level checks nor the test suite can run in this environment without dependencies and data.
- The first repository-wide `compileall` pass found a pre-existing syntax error in `scripts/build_site_parallel_01a104ba.py`: a second module docstring preceded its `from __future__` import. That syntax defect was corrected by consolidating the module docstring. The subsequent full compile check passes.

## Reading the high score claims conservatively

The supplied inter-site table reports `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` at 0.2778 as GEMSDOE32's then-highest submission. The supplied history also reports 0.2708 for the B=1 baseline, and a 0.2747 estimate for B=2. The most plausible explanation consistent with the repository's own records is that the B=2 variant removes predicted pixels within two grid cells (200 m at the stated 100 m grid) of mapped faults from the B=1 emission. This is an identifiable change and has a plausible score-mechanism rationale if mapped faults are excluded from the hidden target: it reallocates prediction mass away from already-known traces. The local `evidence/h33_validation.json` reports four spatial folds and a `lm_mean` of 0.2679205 for H33-2-B2 versus 0.2630510 for the base, and records a separate live-anchor projection of 0.2746732. Those are **local proxy/model quantities**, not a hidden-label holdout DTI and not an organizer receipt. The repository's recorded owner-reported score of 0.2708 and the 0.2778 user-listed score do not establish causality: the score may reflect the whole emission recipe and competition split, and the available records do not provide hidden truth or uncertainty intervals.

The metric intuition is not enough to claim that B=2 truly improved the expected score. Removing predictions can reduce false positives but can also discard true undiscovered structures lying near mapped faults; a boundary distance does not identify geological novelty. Spatial dependence and label/catalogue bias can make a four-quadrant catalogue holdout over-optimistic. To answer whether it beats 0.2778 requires an organizer-scored receipt for the exact artifact; to justify promotion before that requires an independently valid hide-and-recover protocol and its uncertainty interval. The information available here supports neither a guaranteed improvement nor a projected score label.

## Comparability and duplication audit

A proper protocol check requires the registered rasters from `registry/` and the final candidate surface, in the same grid, with a declared correlation statistic and overlap distance rule. The needed source rasters are not available in this environment, so surface correlation, dot-to-dot overlap, and final candidate correlation cannot be recomputed. Do not infer uniqueness from a different filename, a new hash, or a different TIFF encoding. No new raster was built, therefore there is no candidate duplicate result to report.

## Hypothesis slate for a future data-enabled session (not tested, not viable/passed yet)

The repo already implements curvature, DEM Hessian ridges, relief, top-hat, scalar potential-field gradients and structure-tensor orientation in `src/gems32/features.py`; the registered H33/H62 work also covers multiple lineament, curvature and field-combination concepts. The following are deliberately framed as *new tests*, not established advantages. They all use supplied layers, so they require no new external source, but do require source data, leakage checks and blocked holdout evaluation. Rank is tentative prioritization, not measured DTI.

| Rank | Candidate hypothesis | Layers and signature | Why potentially targets unmapped faults | Difference from existing implementation | Cost / risk |
|---:|---|---|---|---|---|
| 1 | Cross-band edge-pair polarity and separation | RTP and TMI (bands 2, 14): find spatially paired, approximately parallel gradient ridges with opposite polarity and stable separation across scale | A paired magnetic contact response may indicate a buried structural boundary even without a mapped surface trace | Existing code uses scalar gradient magnitudes (`rtp_edge`, `tmi_edge`); this tests joint signed edge-pair geometry, not edge magnitude | Medium; magnetic lithologic contacts are a major confounder |
| 2 | Drainage-network deflection conditioned on local relief | detrended elevation and slope (bands 12, 19), deriving channel-like valleys and measuring directional change across neighboring reaches | Fault control can deflect drainage where no continuous scarp is preserved | Existing DEM transforms are local derivatives/ridges; this tests a network-scale deflection statistic, distinct from simply counting aligned valley pixels | Medium-high; requires careful channel extraction and hydrologic/erosional controls |
| 3 | Conductivity–basement boundary concordance with gravity residual | conductivity (17), depth to basement (15), gravity anomaly/high-gradient (13, 18): co-located, orientation-consistent boundary evidence | A concealed structural boundary may be expressed in independent subsurface contrasts where surface mapping is absent | Existing code computes gradients and field consensus, but a pre-registered joint boundary geometry/offset test is distinct from weighted pixel fusion | Medium; strong non-fault lithologic/contact confounding |
| 4 | Fault-strike anisotropy relative to geodetic strain tensor | geodetic scalar bands 4, 7, 8 plus external orientation only if recoverable from official source | Mechanical orientation may prioritize blind structures; scalar invariants alone cannot determine strike | Repository currently has no demonstrated full 2-D strain orientation reconstruction; the supplied scalar invariants may be insufficient, so do not implement absent a validated official vector/tensor source | High/data-blocked; not currently viable without verified official orientation data |

## Required next actions before any unique TIF can be responsibly produced

1. Restore the exact competition `training_features.tif`, `labels.tif`, `sample_submission.tif`, and catalogue inputs from their authorized source/cache; verify hashes against `data/prepared_manifest.json` and repair hard-coded paths so the shared evaluator/writer operate reproducibly from repository configuration.
2. Install the pinned project dependencies; run tests and a small end-to-end format check.
3. Freeze a single candidate hypothesis and run the leakage canary feature-by-feature (any AUC > 0.90 is quarantined pending a provenance investigation).
4. Run the required hide-and-recover evaluator: withheld whole fault segments with a buffer; catalogue-derived features fitted only on visible faults; exact visible-fault masking; pooled DTI using alpha 0.2, beta 0.8 and the required 300 m triangular kernel. Report evaluator version, number of withheld positives and a 95% CI. The currently inspected legacy evaluator is not demonstrated to meet all of these exact requirements; review/fix the shared evaluator before trusting a result.
5. Before any new placement, compare surface rank-correlation and dot overlap against each registry raster. Stop and record a duplicate if correlation exceeds 0.90 or more than 70% of dots are within 3 px of any one registry raster. Re-run on final emitted dots.
6. Only if the candidate beats the current valid holdout best under a pre-registered rule and passes format/duplicate checks, write a unique TIFF plus an independent validation receipt. Do not select or upload a weekly slot here; slot selection is separate and subject to the live weekly cap.
7. Obtain a receipt for organizer-scored claims. Name and note are metadata, not evidence of uniqueness or performance.

## Submission usability and known inconsistencies

The repository already has one-click TIFs and detailed claims in `README.md`, but there is no trustworthy newly validated download to feature from this run. The README also contains multiple historical one-click sections and stale session/branch dates; treat it as an evidence archive, not a real-time official score feed. In particular, numerous recorded values are labelled owner-reported, proxy, model, or projected and must remain distinct from organizer-confirmed values. No evidence in this review verifies a current live leaderboard feed.

## Current-turn follow-up: ranking and next experiment

The project records already cover the obvious DEM curvature, multi-physics fusion, conductivity/basement gradients, magnetic/tilt coupling, and geodetic-invariant ideas (`docs/research/h35-hypotheses-20261025.md`, H33/H32 evidence). Re-running those would not be a genuinely new hypothesis. The following shortlist is deliberately narrower and explicitly **untested**; ranking is prospective, not a score estimate. All use the competition-provided bands and therefore need no external data source. Exact band availability/names are enumerated in `data/prepared_manifest.json`; these are not independent geological evidence.

| Rank | Untested hypothesis | Layers and targeted signature | Rationale for off-catalogue targets | Difference from recorded work | Cost / principal mimic |
|---:|---|---|---|---|---|
| 1 | Paired magnetic edge geometry | RTP (2), TMI (14), tilt derivative (6): detect two nearby, parallel, opposite-polarity edge ridges with stable separation across scales | A buried fault-zone boundary may produce a paired magnetic response while lacking a mapped scarp; geometry can suppress isolated contacts | Tests signed, paired edge topology; existing feature inventory predominantly uses single-band edge/ridge magnitudes and weighted fusion | Medium; lithologic contacts and dikes can mimic it |
| 2 | Cross-drainage channel-deflection statistic | detrended elevation (12), slope (19): channel-network skeleton with change in bearing across adjacent reaches, conditioned on local relief | A concealed structure may perturb drainage without a continuous scarp, so the signal is a network-scale discontinuity rather than a lineament ridge | Existing DEM work includes local curvature/relief and aligned-valley proposals; this requires explicit channel extraction and reach-to-reach bearing change | High; lithologic control, incision, and stream capture mimic it |
| 3 | Scale-persistent geophysical contact discontinuity | conductivity (17), basement depth (15), gravity high-gradient (18): independently detect edge position and strike agreement at multiple smoothing scales | Buried structural boundaries could persist in subsurface properties under cover and be absent from surface-fault catalogues | Differs from simple co-gradient fusion by requiring edge persistence and spatially consistent offset topology across scale | Medium; basement lithology and intrusive margins mimic it |

**Validation decision:** do not implement/run these yet. The files needed for the shared hide-and-recover evaluator (`training_features.tif`, `labels.tif`, `sample_submission.tif`, catalogue inputs, and cached features) are absent. The top-ranked candidate therefore **cannot be validated in this checkout**; reporting a HOLDOUT-DTI or projected leaderboard value would be fabricated. No TIF has been produced this turn, and no weekly slot is recommended. Candidate 1 needs no new external data, so there is no external-source download to claim as a blocker.

## Run card (this review; no experiment was run)

```json
{
  "hypothesis": "No candidate tested; ranked future hypothesis slate is in this review",
  "mechanism": "No new raster generation; avoid manufacturing an unvalidated duplicate",
  "named_non_fault_mimic": "Lithologic contacts and drainage/erosion can mimic lineaments",
  "holdout_dti_and_ci": "NOT RUN; no evaluator version, withheld-positive count, or 95% CI available",
  "correlation_overlap_vs_registry": "NOT COMPUTABLE; no new surface and source/cache data unavailable",
  "raster_sha256": null,
  "validator_output": "NOT RUN; no generated TIF. Existing artifacts are not re-certified in this environment",
  "submission_name": null,
  "note": "No new file: missing source rasters, feature stack, and runtime dependencies",
  "verdict": "negative"
}
```

Negative means the requested experiment could not be validly executed in this checkout; it is not a claim that the geological hypothesis is false.

## Official references for manual review

- Competition overview and requirements: https://www.drivendata.org/competitions/306/competition-doe-gems/
- Problem description: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Competition rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Official reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- Official DOE GEMS GDR resource landing page (source inventory/license should be checked there): https://gdr.openei.org/submissions/1391
- Official USGS GeoDawn data record: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
- EPSG:32611 registry: https://epsg.io/32611
- Current leaderboard (requires live access and should be checked at time of decision): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
