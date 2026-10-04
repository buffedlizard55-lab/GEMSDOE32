# Which local instrument actually tracks the leaderboard? — a 12-artifact calibration

**Session:** Arena `arena/01a10714-gemsdoe32` · **Date:** 2026-10-04
**Command:** `PYTHONPATH=src python3 scripts/calibrate_instrument.py`
**Receipt:** [`evidence/instrument_calibration.json`](../../evidence/instrument_calibration.json)

The standing rule in this project is *"do not spend a weekly slot on an idea that has not beaten the
current holdout best."* That rule is only as good as the holdout's rank correlation with the live
board, so this is a direct measurement of that correlation — nothing is fitted to the answer.

## Method

Twelve artifacts whose owner-reported live scores are recorded in `docs/score-ledger.csv` and whose
bytes are hash-pinned in `registry/data_manifest.json` were re-scored on the blocked holdout
(4 quadrants × draws 20/21, 20 % of catalogue components withheld, 30 px collar, 20 px domain
erosion). Three instrument readings plus two variants were compared against the live scores with
Spearman's ρ. The live scores span **0.0107 … 0.2600** (11 distinct values).

## Result

| instrument | what its truth is | Spearman ρ vs live (n=12) | Pearson r | LOO MAE |
| --- | --- | ---: | ---: | ---: |
| `catalogue_hidden_mean` | withheld catalogue components | **+0.140** | +0.150 | 0.0667 |
| `catalogue_hidden_strict` | withheld components, no free mass on mapped faults | +0.140 | +0.194 | 0.0673 |
| `catalogue_hidden_debiased` | as above + 1 px inward credit shift | +0.501 | +0.614 | — |
| `sgmc_prevalence_calibrated_dti` | state-geological-map faults **not** in the catalogue | **+0.537** | +0.355 | — |
| `drift_corrected_holdout_mean` | 0.65 × debiased-catalogue + 0.35 × SGMC | **+0.529** | +0.735 | **0.0534** |

Per-artifact values (live → drift): `2314b599` 0.0107 → 0.0117 · `lattice-s5` 0.0904 → 0.0583 ·
`h25-ctx-ridge` 0.1280 → 0.1036 · `Hedge-v2` 0.1563 → 0.1841 · `ens12` 0.1563 → 0.0588 ·
`h28-dotted-ridge` 0.1839 → 0.1423 · `H16-1` 0.1855 → 0.0981 · `H19-4` 0.1894 → 0.0982 ·
`H19-5` 0.1922 → 0.0971 · `TGC-v2-on-d1.5` 0.2449 → 0.1372 · `d1.5` 0.2477 → 0.1371 ·
`d2.8` 0.2600 → 0.1480.

## What this means for decisions

1. **The historically-headline proxy (`catalogue_hidden_mean`) does not rank live scores.** ρ = +0.14
   on twelve artifacts. Two artifacts with nearly the same live score (`H19-5` 0.1922 and
   `Hedge-v2` 0.1563) sit at opposite ends of its range (0.0697 and 0.2816). Any promotion argument
   that cites only `catalogue_hidden` is unsupported.
2. **The best available ranker is `drift_corrected_holdout_mean`** (ρ = +0.53, LOO MAE 0.053), and
   even that is **not statistically significant** at n=12 (p ≈ 0.09). It is used here as the primary
   *screen*, never as evidence of a leaderboard gain.
3. **Within the family it is monotone and useful.** For the three members of the dotted-H19-5
   emission family the instrument and the live board agree in both order and direction:
   live 0.1922 → 0.2477 → 0.2600 against drift 0.0971 → 0.1371 → 0.1480 (slope ≈ 0.74, i.e. 1 unit
   of live score ≈ 1.35 units of drift). That is the only regime in which a local number has been
   seen to translate, which is why the slot plan compares *only* within that family.
4. **A caveat that costs nothing to state:** `TGC-v2-on-d1.5` added 1 259 dots to `d1.5` and was
   locally indistinguishable from it (drift 0.13724 vs 0.13709) but scored **−0.0028 live**. Small
   "add dots" changes are therefore inside the noise band of both the instrument and the live board,
   and no candidate should be promoted on a local gain of that size.

## A discontinuity that invalidates the instrument across one specific comparison

`holdout.py` switches estimator branches when a single dot lands on a mapped fault: the debiased
catalogue term is replaced by the raw one (`0.19359 → 0.09832` for the 0.2600 file) and
`sym_factor` becomes `1/(1+(n/60000)²) ≈ 0.649`. Measured, on the incumbent emission:

| mask | on-catalogue dots | `catalogue_hidden_mean` | SGMC-calibrated | `drift_corrected_holdout_mean` |
| --- | ---: | ---: | ---: | ---: |
| D2.8 (0.2600) | 0 | 0.09832 | 0.06059 | **0.14801** |
| D2.8 **+ 1 dot** on a mapped fault | 1 | 0.09832 | 0.06059 | **0.07831** |
| D2.8 + 20 such dots | 20 | 0.09866 | 0.06059 | 0.07853 |

One dot costs **47 %** of the promotion metric and changes nothing about the emission's actual
relationship to the truth. Consequence, stated plainly: *every* cross-candidate drift comparison
that straddles this branch is meaningless, and every artifact in this repository with a "promoted"
label happens to carry exactly zero on-catalogue dots. Registered as `IR-32-INSTR-01`; the fix
(a branch-free estimator) is proposed as next work.

## Cross-repository contradiction (flagged, not resolved)

The sibling repository `GEMSDOE29` reports **ρ = +0.709** for the catalogue-hidden proxy on a set of
ten stored artifacts. This checkout measures **+0.140** on twelve. The two runs do not use the same
artifact set or the same hidden fractions, so both can be internally correct — but they cannot both
be used to justify a promotion. Recorded as `IR-32-INSTR-02`; the discrepancy is disclosed here
rather than averaged away.
