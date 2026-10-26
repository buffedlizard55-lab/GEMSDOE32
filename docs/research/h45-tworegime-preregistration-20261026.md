# H45-1 Two-Regime Split-Budget Allocation — pre-registration (2026-10-26)

Frozen **before** any H45 code is executed. Reproduction: `scripts/run_h45_tworegime.py`.
Run card (written only by the runner): `evidence/h45_tworegime_run_card.json`.

## 0. Lane assignment (read first)

The Parallel-Run Protocol refers to "the single method paragraph below" as the lane definition.
**That paragraph is absent from the supplied prompt** (the prompt ends the protocol at
"Your lane is the single method paragraph below. Stay inside it."). The lane is therefore
**provisional**: this run executes README §8.4 "Next suggestion #1 — Two-Regime Split-Budget
Allocation", the explicit untried follow-up left by the H44-1 session. Flagged as an
irregularity for the owner to confirm or replace.

## 1. Hypothesis

Splitting the 37,654-dot budget by a fold-local **observability propensity** `e(z)` (the SAR-PU
propensity estimated from visible-fault observability, `src/gems32/spcp.py::fit_predict_sarpu_spcp`)
gives a single map that wins on **both** failure modes measured so far:

- **Regime A, `e(z) >= 0.5`** (exposed / observable range fronts): dots from the naive 55-channel
  binary HistGB surface (`EXP2_H44_NAIVE_BIN55`, the best measured HIDE-RECOVER arm at `0.1077`).
- **Regime B, `e(z) < 0.5`** (blind / concealed basins): dots from the SAR-PU curvature-conduit
  surface (`EXP3_H44_SARPU_SPCP`, the arm that cures the off-catalogue PU suppression,
  `SGMC-cal 0.0777` vs champion `0.0641`).

## 2. Mechanism

`IR-A8A-PU-BIAS-01`: a naive `y=0` classifier learns that blind basins are negatives, so it
suppresses real but unmapped faults there. `IR-32-SARPU-PARETO-01`: SAR-PU debiasing fixes that
suppression but loses the exposed-range-front signal that the naive model captures. Routing each
regime to the surface that is strong there removes the trade-off by construction, rather than by
tuning a blend weight.

## 3. Named non-fault process that could mimic it

- **Near-trace gap-filling on exposed fronts.** A high naive HIDE-RECOVER score can come from
  dots hugging the withheld trace (the `d_hidden <= 2 px` censorship artifact, `IR-42-INSTR-01`).
  Test: the detached `>= 600 m` diagnostic and the censorship-matched `d_hidden > 2 px` score.
- **Alluvial-fan / playa margins and pluton ring margins** in the blind regime, which carry
  curvature crests with no fault. Test: the off-catalogue USGS SGMC diagnostic (`n=62,703`).

## 4. Fixed design (no tuning after this point)

- Evaluator: shared `gems32.holdout` hide-and-recover (`GEMSDOE32-HIDE-RECOVER-v3.0`, draws 20/21,
  4 quadrants, 1.5 km collar, `B=2 px` visible-mask), alpha `0.2`, beta `0.8`, 300 m triangular
  kernel. Off-catalogue diagnostic: `evaluate_sgmc_with_ci`.
- Regime threshold `e >= 0.5` (the value already used inside `spcp.emit_crest_submodular` callers
  and in README §8.4). No other thresholds are tried.
- Budget split per cell and on the full map: `b_A = round(b * |elig & A| / |elig|)`,
  `b_B = b - b_A`, with `A`/`B` the regime masks inside the eligible domain. Emission uses the
  shared `emit_crest_submodular` (1-px crest sharpening, `support_mult=5`, `emitter.emit`) for both
  regimes. No new emitter.
- Seeds, HistGB hyper-parameters, the 20-channel SPCP stack and the 55-channel canary are the H44
  ones (imported, not re-implemented).
- Final full-map surface: stitched OOF, as in H44 (`EXP2` uses the seed-20 quadrant predictions,
  `EXP3` averages the two seeds per quadrant). `e` is averaged the same way.

## 5. Pre-registered criteria (ALL must pass to promote)

| ID | Criterion | Evidence class |
|---|---|---|
| C1 | Leakage canary: every one of the 55 single channels has oriented AUC `<= 0.90` | leakage canary |
| C2 | Pooled HIDE-RECOVER DTI of H45 `>` EXP2 replica, **paired spatial-block bootstrap CI lower bound `> 0`** | HOLDOUT-DTI |
| C3 | Off-catalogue SGMC prevalence-calibrated DTI of H45 `>` champion `0.06412`, paired CI lower bound `> 0` | HOLDOUT-DTI (off-catalogue diagnostic, not a leaderboard score) |
| C4 | Detached `>= 600 m` DTI of H45 `>=` EXP2 replica (point estimate; guards gap-filling) | diagnostic |
| C5 | Pre-placement surface: max `|Spearman|` vs every genuine registry raster `<= 0.90` | uniqueness |
| C6 | Final dots: `<= 70%` within 3 px of every genuine registry raster's dots | uniqueness |
| C7 | Literal calibration-lattice rule (`13gems r13-lattice-s5`, `<= 70%`). **Reported, not exempted.** Expected to FAIL (`IR-R6-03`: champion itself is 99.92%) | uniqueness (literal) |
| C8 | Format: one float32 band, EPSG:32611, `3730x3292`, exact transform, `nodata` unset, all cells finite, values in `[0,1]`; `scripts/check_submission.py --strict-finite` PASS | format |

**Decision rule (fail-closed):** `promote` only if C1–C8 all pass **and** the separate weekly-slot
selector approves. Under the current literal rule C7 is expected to fail, so the expected verdict
is **negative / DO NOT SUBMIT**. No criterion will be relaxed after seeing results.

## 6. Budget and what would make this wrong

- Experiments: **1** of the `<= 3` budget. Wall-clock cap `2 h`. No DrivenData weekly slot is used.
- Would be wrong if: `EXP2` replica does not reproduce the H44 EXP2 number (`0.1077`) to within
  bootstrap noise (then the baseline is not trustworthy and the result is void); or if the
  regime-A emission is simply the naive map restricted to a subset (then the split adds nothing).
  The runner reports both checks.

## 7. Limitations declared up front

- All numbers are **HOLDOUT-DTI** (local instrument) or **OWNER-REPORT** (live scores). No organizer
  receipt exists for any group file (`IR-32-SCORE-01`).
- The repo has two holdout evaluators that rank the champion differently (`HIDE-RECOVER-v3.0`:
  champion `0.0045`; `HOLDOUT-v3-visible-gated`: champion `0.0992`). This run uses the
  `HIDE-RECOVER-v3.0` evaluator because it is the one in which the H44 arms were already measured.
  The evaluator conflict is an open irregularity, not resolved here.
