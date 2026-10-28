# Repository review and next hypotheses — 2026-10-27

## Decision and scope

**DO NOT SUBMIT.** This session is an audit, not a geological experiment. No new TIF was generated, no new holdout-DTI measured, and no weekly slot used. A protocol-compliant new unique submission has **not** been achieved. The latest existing H48 audit file remains downloadable; do not mistake it for a newly generated file.

Read the [nine-site executive table](../nine-site-review.html). Its pinned winners and overlap findings come from saved evidence, not a freshly fetched nine-repository census. Their owner-reported results lack submission-page receipts; none is ORGANIZER-CONFIRMED. No defensible leaderboard estimate is available.

### Why not continue the previous session's next experiment immediately?

1. The prompt refers to a “single method paragraph below” but supplies no clearly assigned method paragraph. H48 was the *previous session's* lane, not authorization to reuse or extend it in this parallel session.
2. The previous H48 run exhausted its three-experiment budget. Its literal-registry overlap failed against a dense calibration lattice. The user's rule says stop on duplication; a discrete-only subset is not an authorized exemption.
3. `.cache` feature stacks, catalogue arrays, and registry rasters do not persist in this checkout. Historical restore receipts describe earlier machines, not current file availability. GitHub mirror restoration is possible through `scripts/restore_data.py`; it proves hash consistency, not organizer authentication. We did not restore gigabytes of training inputs for an unassigned lane.
4. A better public score cannot be inferred from the H48 holdout advantage over H33. The current rule requires comparison with the **best same-evaluator** result, not merely the older leaderboard champion. Repeated tuning on a reused holdout also requires a sealed, untouched confirmation partition.

## Three candidate hypotheses (planning only, before any new implementation)

Expected improvement ranking is **qualitative judgment, not a score projection**. These combinations are not certified globally novel: a lane assignment and a full implementation/registry census are still needed. No external-data idea is called viable without obtainable bytes.

| Rank / cost | Hypothesis and layers | Physical transform and unmapped target | Difference from reviewed implementation; non-fault mimic |
|---|---|---|---|
| 1 / medium | Signed cross-field displacement parity: RTP magnetics, isostatic gravity anomaly, basement depth, DEM slope | Test whether parallel gravity/magnetic edges maintain a signed cross-strike offset consistent with basement relief across multiple scales. Could identify buried basin-margin faults absent from surface catalogues. | FBGR uses continued edges, persistence and asymmetry; proposed test adds explicit **sign-consistent displacement parity between independent fields**, not an added mixture floor. Must first check for equivalent code. Mimic: dipping stratigraphic/lithologic contacts. |
| 2 / medium-high | Residual thermal transport asymmetry: existing F2mDAB observations, DEM, conductivity | After cross-fitted elevation/regional-temperature removal, compare uphill versus downhill thermal residual coherence along geophysical ridges; test advection rather than absolute warmth. Could detect concealed conduits where scarps are buried. | Existing TRHV/SPCP use thermal corroboration. Proposed test requires **directional transport asymmetry**, with fold-local interpolation and exclusion buffers around thermal observations. Mimic: shallow groundwater discharge or irrigation. Sparse observations may make this unidentifiable. |
| 3 / medium | Sediment-compaction counterfactual: basement depth, DEM curvature, gravity horizontal gradient | Model smooth depth-dependent compaction curvature on training blocks; retain narrow residual step edges with independent gravity support. Targets fault displacement beneath fan sediment rather than catalogue proximity. | Distinct intended target is **failure of a compaction null model**, not raw scarp curvature or habitat emission. Mimic: alluvial-fan lobes, incision, paleoshorelines. |

The listed layers have recorded mirror manifests, but their cached feature arrays are absent locally. Thus these are restoration-dependent hypotheses, not ready-to-run submissions. No new official-data obtainability claim is made. Official data source: [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (not fetched here). External acquisition is unnecessary in principle; input identity and interpolation support must be audited after restoration.

### Evaluation plan once a lane is established

Use shared `scripts/evaluate_holdout.py`, `scripts/submission_writer.py`, and `gems32.holdout`, not a private fork. Freeze at most three experiments. Hide whole fault components with buffer, derive catalogue features only from visible faults, and mask visible faults exactly. Run each feature alone; AUC above 0.90 stops the run pending leakage investigation. Run surface-registry comparison before placement and final-dot comparison afterward; exceedance stops the lane. Use pooled distance-tolerant Tversky, alpha 0.2/beta 0.8, 300 m triangular kernel. Record withheld positives, evaluator version and paired spatial 95% CI. Only then inspect saved bytes against a restored template and footprint. Do not promote using a flat-mask or different evaluator's baseline.

## Verified defect and fix

`scripts/sync_submission_build.py` previously fabricated format fields during stale-release reconciliation: finite count, min/max, dimensions and a template PASS were copied or hard-coded without opening the raster. A matching SHA proves byte identity, not valid predictions. Missing/invalid run cards could also pass via `None` verdict. `--dry-run` could write release JSON. These are fixed with actual raster inspection, explicit historical-grid-only provenance, a required negative/hold card, read-only dry-run, matching paths, measured positive counts and a 140-character note bound.

The new byte audit is intentionally limited: all-cell finite/range, band/dtype and documented historical grid. It does **not** claim to rerun catalogue exclusion, footprint provenance, organizer-template identity, surface novelty, final-dot overlap, or model performance. Existing primary H48 bytes pass this limited check; that does not authorize upload.

## Three passes

1. **Implementation:** examined README, manifests, prior results and release code; implemented actual byte inspection and an executive review generated from pinned evidence.
2. **Bug review:** regression tests exercise wrong grids, nonfinite/range failures, missing run cards, stale reconciliation and read-only dry-run; removed intermediate release writes before validation completes.
3. **Requirements review:** explicitly retained negative decision, withheld score estimates, separated historical results from new measurements, documented lane/data/registry blockers and linked the review from the site builder so regeneration does not erase access.

## Official evidence and limitations

Fetched the official [reference-solution README at commit aebe92f](https://github.com/drivendataorg/gems-prize-reference-solution/blob/aebe92f7c8a990f0e3443451b7a825d9afd6336b/README.md) through GitHub. [Saved copy](../../evidence/official/reference-solution-readme-20261027.md). It explicitly supports CPU training; “GPU needed for training” in the prompt is not a hard requirement. Faster training may benefit from GPU.

DrivenData, USGS, GDR, Dropbox and the NLR PDF hosts are outside this environment's direct outbound allowlist. They were **not** fetched or freshly verified; links are review pointers, not proof. No competition login/session is available. Never infer the weekly cap or current leaderboard from conflicting old prompt numbers. New data can be restored autonomously from pinned permitted GitHub mirrors where available. A high-scoring, unique, fully cleared upload cannot honestly be promised from the current evidence.

The existing standing prompt is preserved with an explicit completeness warning; the conversation remains authoritative. This document records the current request's operative constraints, not a claimed verbatim transcript. Core values: maximize probability of winning by protecting scarce slots; own the outcome by publishing negative results and fixing validation defects rather than relabeling research artifacts as submissions.
