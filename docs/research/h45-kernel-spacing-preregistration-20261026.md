# H45-1 Pre-registration — Kernel-Spacing Emission (frozen before any H45 code ran)

**Date:** 2026-10-26 · **Lane (single method):** Fold-local supervised surface +
300 m-kernel-aware **hard minimum-separation packing**. This session stays inside
this lane. If the final raster's rank-correlation with any genuine registry raster
exceeds 0.90, or >70% of its dots fall within 3 px of one genuine registry raster's
dots, it is logged as a duplicate and stopped (calibration-lattice/control rasters
are reported separately — see IR-32-LATTICE-01: a spacing-5 lattice covering
99.87% of the footprint is within 3 px of *any* dense dot set by construction, so
it cannot be a genuine submission comparator; it is flagged, never silently exempted).

## Hypothesis H45-1 (KS)
The DTI kernel radius is 3 px (300 m). Two binary dots closer than ~3 px cover
largely the *same* hidden-truth pixels: the second dot's marginal TP credit is
small while its FP mass is ~full. Prior emissions (37,654–44,090 dots, thinning
≈2.8 px) therefore waste mass on self-redundant pairs. **Enforcing a hard minimum
separation of 4 px and cutting the budget should raise credit-per-dot enough to
raise pooled HOLDOUT-DTI at equal or lower dot count.**

- **Layers:** the template's cached 35-channel feature stack (`scripts/build_features.py`,
  from the 19 official bands of `training_features.tif`) only. No catalogue-distance
  feature (leakage canary, per-channel AUC ≤ 0.90 required).
- **Physical signature:** HistGradientBoosting probability of a *visible* fault,
  trained fold-locally (hide-and-recover: whole segments withheld, 15 px collar,
  catalogue features derived only from visible faults, visible faults masked
  pixel-exactly + B=2 px exclusion at emission).
- **Why off-catalogue:** emission is forbidden within 2 px of any visible/catalogue
  fault; scoring (official) masks catalogue pixels anyway, so mass there earns nothing.
- **Non-fault mimic that could fake it:** broad smooth probability blobs (e.g. over
  pluton margins) — spacing would then just spread false positives thinner. The
  holdout decides: if KS does not beat the unspaced control on withheld segments, verdict = negative.
- **Differs from repo history:** champion family = H19-5 surface + 2.8 px thinning +
  B=2 (OWNER-REPORT 0.2778); H36/H38/H44 = new physics channels at 37,654 dots with
  submodular packing but **no hard ≥4 px separation and no budget cut**. KS changes
  only the packing geometry/budget on a standard fold-local surface.

## Ranked candidate hypotheses considered (only #1 is in-lane this session)
| Rank | Idea | Layers / signature | Off-catalogue rationale | Cost |
|---|---|---|---|---|
| 1 | **H45-1 kernel-spacing packing (≥4 px, 12–20k dots)** | 35-ch stack, greedy 300 m coverage with hard separation | removes self-redundant FP mass near unmapped traces | Low (this run) |
| 2 | H36-2 anisotropic Phillips–Hansen strike-coherent curvature tensor | B02/B05 Hessian eigenvectors | blind basement steps under cover | Medium, untried standalone |
| 3 | H36-4 half-graben polarity-reversal saddle detector | B18/B12 + depth_to_base | accommodation zones host blind geothermal systems (Faulds & Hinz 2015) | Medium |
| 4 | H61-4 GNSS 2-D strain-tensor matched filter | external GNSS velocities (free: UNAVCO/EarthScope) | actively extending, unmapped faults | Data obtainable but new pipeline; out of budget |
| 5 | H44-5 GPU Tversky U-Net | 55-ch stack | 2-D relay geometry | Blocked: no GPU in sandbox |

## Experiments (budget: exactly 3, all on `GEMSDOE32-HIDE-RECOVER-v3.0`, 22,232 withheld positives)
- EXP1 `KS0-37654`: min-sep 0, budget 37,654 (unspaced control, same surface)
- EXP2 `KS4-20000`: min-sep 4.0 px, budget 20,000
- EXP3 `KS4-12000`: min-sep 4.0 px, budget 12,000

Promotion gate: winner must beat EXP1 control **and** the repository holdout best
(H38, 0.11696) on the same evaluator, pass canary + genuine-registry uniqueness +
`check_submission.py --strict-finite`. Otherwise verdict = negative, no slot spent.
Every number is labelled HOLDOUT-DTI (evaluator, n, 95% CI) or OWNER-REPORT /
ORGANIZER-CONFIRMED; projections are never written as scores.
