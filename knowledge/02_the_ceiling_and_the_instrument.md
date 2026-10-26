# Metric identity and evidence limits

**Corrected:** 2026-10-26. This file replaces the historical ceiling/instrument note whose score inversions and slot recommendations depended on unsupported hidden-truth assumptions. Those estimates and recommendations are withdrawn. Current release decision: **DO NOT SUBMIT**; see [`evidence/current_release_review.json`](../evidence/current_release_review.json) and [`docs/research/repo-review-20261026.md`](../docs/research/repo-review-20261026.md).

## Exact metric

Let `TP` be kernel-weighted credit, `FP` prediction mass not credited as TP, and `FN=|G|-TP`, with `alpha=0.2` and `beta=0.8`:

```text
DTI = TP / (TP + alpha*FP + beta*FN)
    = TP / (alpha*(TP + FP) + beta*|G|)
```

For any actual marginal addition, with denominator `D = TP + alpha*FP + beta*FN`, its effect is positive exactly when

```text
ΔTP * D > TP * (ΔTP + alpha*ΔFP + beta*ΔFN).
```

A narrower special case applies to one binary prediction whose full kernel credit `k` is assigned to a truth pixel that had no previous credit: `ΔTP=k`, `ΔFP=1-k`, `ΔFN=-k`, so the isolated-pixel break-even is `k > alpha*DTI`. For `DTI=0.2778`, this is `k > 0.05556`. It is **not** a universal per-pixel criterion in a partially covered field. Use the marginal condition above. The regression test [`tests/test_metric.py`](../tests/test_metric.py) covers a case where a pixel clears the isolated scalar bar but still lowers DTI after its actual marginal changes are evaluated.

The exact denominator can also be written `0.2*TP + 0.2*FP + 0.8*|G|`. Because the `0.2*TP` term is present, comparisons cannot be simplified to `TP/(0.2*FP + 0.8*|G|)`.

## What the available evidence cannot identify

The hidden truth raster is unavailable in this checkout. Historical owner-reported scores and prediction counts alone do not identify hidden-truth mass, weighted TP, FP, FN, recall, a score ceiling, or exact coverage needed to reach another score. They also do not prove that a particular pruning edit caused a live-score change. The reported GEMSDOE32 value `0.2778` is **OWNER-REPORT**; no receipt linking the exact raster bytes to that score is stored here.

Local experiment scores must be labelled `HOLDOUT-DTI` and include evaluator version, withheld-positive count, and 95% CI. Only a submission-page receipt linked to exact bytes can establish `ORGANIZER-CONFIRMED` for a group submission. A public leaderboard observation for another team is not evidence about this team's score.

The official public leaderboard was read at `2026-10-26T04:32:28Z`; it showed `xiaofanhu` at #1 with `0.4437`. This is a timestamped public observation, not a private/final-round result. The capture is [`evidence/live_leaderboard_snapshot_20261026.json`](../evidence/live_leaderboard_snapshot_20261026.json).

## Current operational status

No fresh scientific experiment or compliant holdout was run in this review: the competition rasters and cached feature stack are absent in this checkout. No new GeoTIFF was created, no weekly slot was used, and no candidate is authorized for upload. Restore and hash-check the inputs, use the shared visible-only holdout and submission writer, and satisfy the method-lane, leakage, uniqueness, run-card, and separate slot-selector gates before considering a new artifact.

## References

- [Official competition description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [`src/gems32/metric.py`](../src/gems32/metric.py)
- [`docs/research/score-ceiling-analysis.md`](../docs/research/score-ceiling-analysis.md)
