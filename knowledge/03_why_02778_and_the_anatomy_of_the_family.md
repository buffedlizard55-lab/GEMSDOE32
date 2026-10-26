# GEMSDOE32 reported score 0.2778 and family-lineage notes

**Corrected:** 2026-10-26. This replaces the former “anatomy of the family” analysis, which treated owner-reported live scores as organizer-confirmed and used unsupported hidden-truth inversions to infer per-dot credit and score reachability. Those estimates are withdrawn.

## Evidence status

The portfolio records identify a nested H19-5 family: H19-5 (121,131 dots; reported 0.1922), d2.8 (44,090; reported 0.2600), solo/B=1 (40,199; reported 0.2708), and champion/B=2 (37,654; reported 0.2778). These values are **OWNER-REPORT**; no submission-page receipt linking the exact TIFF bytes to the reported values is stored in this checkout. The archived overlap records report the files as nested, with the B=2 variant excluding 2,545 dots within two pixels of the training catalogue. Treat the byte/lineage analysis as a recorded claim unless the source rasters are restored and rerun.

The sequence is consistent with this possible mechanism: if some pruned predictions have little marginal credit against hidden faults but still contribute false-positive mass, pruning them could improve DTI. The hidden truth and per-submission organizer receipts are not available, so the repository cannot show that B=2 caused the reported score difference, infer per-dot hidden credit, or establish that the same rule improves a new method.

## Metric and marginal condition

With `TP` the kernel-weighted true-positive credit, `FP` prediction mass not credited as TP, `FN=|G|-TP`, and `alpha=0.2`, `beta=0.8`:

```text
DTI = TP / (TP + 0.2*FP + 0.8*FN)
    = TP / (0.2*(TP + FP) + 0.8*|G|)
```

For actual changes `ΔTP`, `ΔFP`, and `ΔFN`, an addition improves DTI exactly when:

```text
ΔTP * D > TP * (ΔTP + 0.2*ΔFP + 0.8*ΔFN)
```

The scalar `k > 0.2*DTI` applies only to one binary pixel whose full kernel credit goes to previously uncovered truth. It is not a universal filter for arbitrary additions to partially-covered fields. See [`knowledge/02_the_ceiling_and_the_instrument.md`](02_the_ceiling_and_the_instrument.md) and [`src/gems32/metric.py`](../src/gems32/metric.py).

## What is not established

- No unique hidden-truth mass, weighted TP/FP/FN, recall, ceiling, or exact score requirement can be recovered from this reported score ladder alone.
- The former equations assigning mean credit to removed annulus dots, the “dead annulus” claim, estimated effect of a B=3 prune, the `+59%` credit-density requirement, and per-dot Anderson inferences are withdrawn. Do not use them as evidence or projections.
- A holdout result is distinct from a live leaderboard score. Label research measurements `HOLDOUT-DTI` with evaluator version, withheld-positive count, and 95% CI. Label a team live score `ORGANIZER-CONFIRMED` only when a submission-page receipt is stored and tied to the exact bytes. Otherwise use `OWNER-REPORT`.
- The official public leaderboard snapshot read at `2026-10-26T04:32:28Z` showed `xiaofanhu` at #1 with 0.4437. This is a time-stamped public observation for another participant, not a private/final score and not evidence about our team.

## Release decision

**DO NOT SUBMIT** any archived or new file on the basis of this analysis. This review ran no new experiment or compliant holdout because the competition rasters and cached feature stack are absent from this checkout. A new experiment must use the shared visible-only holdout and writer, pass leakage and registry-uniqueness rules, carry a complete JSON run card, and beat the compliant holdout incumbent before a separate selector considers spending a weekly slot. See [`docs/research/repo-review-20261026.md`](../docs/research/repo-review-20261026.md) and [`evidence/current_release_review.json`](../evidence/current_release_review.json).
