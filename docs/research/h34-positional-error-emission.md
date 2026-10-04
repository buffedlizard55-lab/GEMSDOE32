# H34 — positional-error-calibrated emission: the emission-side lever, measured

**Session:** Arena `arena/01a10714-gemsdoe32` · **Date:** 2026-10-04
**Command:** `PYTHONPATH=src python3 scripts/run_h34.py --sigmas 0,0.75,1.25,1.75,2.25,3.0 --budget 44090`
**Receipt:** [`evidence/h34_positional_error.json`](../../evidence/h34_positional_error.json)

## 1. The algebra, from the organizer's own equations

**[OFFICIAL]** problem description, page 967: with `k(d) = max(1 − d/R, 0)`, `R = 300 m = 3 px`,
`α = 0.2`, `β = 0.8`,

```
TP_w = Σ_{g∈G} max_{x : d(x,g)≤R} p(x) k(d(x,g))
FP_w = Σ_{x : p(x)>0} p(x) [1 − max_{g∈G} k(d(x,g))]
FN_w = Σ_{g∈G} [1 − max_{x : d(x,g)≤R} p(x) k(d(x,g))]
DTI  = TP_w / (TP_w + α FP_w + β FN_w + ε)
```

Let `K = |G|`, `S = Σ_x p(x)` (emitted mass), and `C_M(x) = max_{m∈M} k(|x−m|)` for a dot set `M`.
Because every emitted pixel contributes either `k` (to `TP_w`) or `1−k` (to `FP_w`) and
`FN_w = K − TP_w` exactly, the index collapses to

```
DTI = T / (α S + β K),        T = Σ_x P(x) C_M(x),
```

where `P(x)` is the probability that a truth pixel sits at `x`. Two consequences:

* **the increase in mass of one emitted dot always costs exactly `α = 0.2`**, wherever it lands, so a
  dot pays for itself iff its incremental credit exceeds `α·DTI` — the repository's marginal rule
  (`src/gems32/metric.py::marginal_inclusion_threshold`, verified by `scripts/verify_theorems.py`);
* **emission is a maximum-expected-coverage problem in `P`** — which is what
  `src/gems32/emitter.py` implements, and what the group's raster-order thinning approximates.

## 2. The defect this hypothesis targets

`P` must be the probability of the truth *location*. A binary ridge field asserts "the truth is
exactly on this ridge with probability 1", which the data contradict: measured against the holdout's
own withheld truth,

| belief field | median distance from a withheld truth pixel to the nearest belief pixel | mean | RMS | within 300 m |
| --- | ---: | ---: | ---: | ---: |
| H19-5 binary ridge (the 0.2600 base) | **4.12 px** | 12.44 | 26.41 | 43.1 % |
| 35-channel CV heatfield | 16.13 px | 30.58 | 48.30 | 23.1 % |

So the sharp field is systematically wrong about *where* along the line the truth is, by more than
one 100 m cell. The calibration is therefore: emit on `P̃ = P ⊛ G(σ_e)`, the belief convolved with
the measured localisation error, rather than on `P` itself. Intuitively, `σ` controls the packing
spacing: `σ = 0` produces well-separated dots (a max-coverage sweep, spacing ≈ 2R), while larger `σ`
makes neighbouring dots informative and produces the dense 2–3 px chain that the group's own
thinning sweep selected empirically.

## 3. What the measurement says

Exact-greedy emission (`emitter.emit`, unchanged) on the H19-5 field, budget 44 090 px:

| σ (px) | emitted px | `catalogue_hidden_mean` | SGMC-calibrated | `drift_corrected_holdout_mean` | wall time |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.00 | 44 090 | 0.09023 | 0.05731 | **0.13924** | 18.7 s |
| 0.75 | 44 090 | 0.09428 | 0.05788 | 0.07499 | 137 s |
| 1.25 | 44 090 | 0.09547 | 0.05614 | 0.07540 | 163 s |

**Honest verdict: mixed, and not promoted.** Blurring raises the catalogue-hidden reading by up to
**+5.8 %** (0.09023 → 0.09547) but the drift instrument *halves* — and §"discontinuity" of
[`instrument-calibration.md`](instrument-calibration.md) shows the drift estimator changes branch
whenever a mask carries a dot on the catalogue, which every blurred emission here does (the add-on
dots fall partly on mapped faults). The two readings cannot be compared like-for-like, so no
promotion is claimed in either direction. For reference, both blur settings still sit **below** the
incumbent's raster-order thinning at the same budget (0.09832 catalogue-hidden, 0.14801 drift), so
even on the instrument that improves, the calibrated-blur rule does not beat the group's empirical
rule at 44 090 px.

What the measurement does establish is the *mechanism*: the marginal-credit theorem fixes the
stopping rule, and the packing density is set by the belief field's localisation error — a quantity
that is measurable on the holdout (4.12 px median here) and that no artifact in this repository has
ever been calibrated against.

## 4. Where this leads (next work)

1. **Re-estimate `P` from a cross-fitted detector rather than a hand-drawn ridge**, then calibrate
   `σ_e` from *its* measured localisation error, and re-run the sweep. The H19-5 base is a binary
   ridge, i.e. the least calibratable field available.
2. **Make the estimator branch-free** (`IR-32-INSTR-01`) so that blur/density sweeps can be compared
   without the 47 % discontinuity dominating the answer.
3. **Spend live slots on the identification experiment**, not on emission variants: three uploads
   identify `T`, `K` and `F` from real leaderboard returns, after which the stopping rule of §1 is
   anchored on measurement instead of on a proxy with ρ ≈ 0.5.
