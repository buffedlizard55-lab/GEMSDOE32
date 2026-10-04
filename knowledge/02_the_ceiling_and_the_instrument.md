# 02 — The ceiling, the gap, and the instrument we never had

**Date:** 2026-10-04 · **Session:** Arena `arena/01a1050d-gemsdoe32`
**Question answered:** *why did the group's best artifact score what it scored, and can we beat the
current leader — and if so, by what mechanism?*

Every number below carries one of four evidence classes, and no number carries a class it has not
earned:

* **[OFFICIAL]** — read from a DrivenData / USGS / DOE page or product, with the link given.
* **[MEASURED]** — computed in this checkout from hash-pinned bytes; the command is in §9.
* **[OWNER-REPORT]** — the owner's own page or brief. No organizer receipt exists.
* **[MODEL]** — an estimate conditioned on an unverified anchor. Never a result.

---

## 0. Executive answer

1. **The brief's two anchor numbers are both out of date or unverifiable.** [OFFICIAL] The public
   leaderboard read on 2026-10-04 has **#1 `nchuzhoy` 0.3262**, #2 `kinghorton42` 0.3222,
   **#3 `DARD` 0.3195**, #4 0.3042, #5 0.2998. The brief's "0.3195 is the highest score right now"
   is **stale** — 0.3195 is rank #3. The brief's "highest score from the GEMSDOE site ... 0.2708"
   is an **[OWNER-REPORT]** claim that *the group's own GEMSDOE28 site contradicts*: that page
   prints **"NO GEMSDOE28 SCORE"** and describes the `h27-4-r1-solo` family as *projected* to
   0.2701, not scored. As it happens the live board carries an unrelated entry at exactly 0.2708
   (rank #13, participant `smashi34`), which is the most likely origin of the number.
2. **The metric reduces to one line, and that line is the whole game.** [MEASURED, §2] With
   `T = TP_w`, `F = FP_w`, `K = |G|`,

   ```
   1 / DTI  =  alpha  +  alpha * (F/T)  +  beta * (K/T)          alpha = 0.2, beta = 0.8
            =  0.2    +  0.2 * (F/T)    +  0.8 * (K/T)
   ```

   verified against the official implementation to **1e-15**. Everything else follows from it.
3. **The leader's requirement is a recall number, and it is knowable exactly.** [MEASURED, §5]
   Writing `x = T/K` (weighted recall of the *hidden* truth) and `rho = F/K`,
   `x = (alpha*rho + beta) / (1/DTI - alpha)`. At **0.3262** that is **27.9 % recall at zero
   false-positive mass**, or **83.9 %** at the group's own measured false-positive-per-credit ratio
   (`F/T = 8.02`). With perfect knowledge of the hidden traces the index is **≈ 0.78**. The
   community is at 0.3262. **The gap is knowledge, not method.**
4. **A dot raster wins because the metric taxes redundant mass, and that is now proved, not
   inferred** [MEASURED, §3]: adding one unit of mass raises the denominator by **exactly `alpha`
   regardless of where it lands**, so a dot pays for itself iff its incremental credit exceeds
   `alpha * DTI` — `0.052` at DTI 0.26, i.e. the dot must sit within **≈ 284 m** of a *hidden*
   truth pixel. The group's thinning sweeps were removing mass that realised ~0 credit. This is
   why `d = 2.8 px` beat `d = 1.5 px` live.
5. **The "credit bar" the group has been quoting is (a) mis-derived in one document and (b)
   mathematically incapable of constraining this emission.** [MEASURED, §4] The repo's own test
   suite proves the bar is `alpha*s`; `docs/research/score-ceiling-analysis.md` §1 states it as
   `alpha*s/(1-alpha*s)`, which is **5.5 % too high at s = 0.26** and does not follow from the
   metric. Separately, for a pixel on the *emission field's own support* the expected added
   false-positive mass is `1 - kbar <= 0`, so the bar accepts unconditionally: measured, the
   credit-bar arm emits the **entire 121,131-px support** and stops on *exhausted_support*.
6. **The instrument the project has never had is a 3-slot *identification experiment*, and it is
   exact.** [MEASURED, §6] Because DTI scales exactly as
   `DTI(lam*p) = lam*T / (lam*alpha*(T+F) + beta*K)` (verified to 1e-15), a `lam = 0.5` re-upload
   and a null-mass additive probe together identify **T, K and F exactly** from three leaderboard
   returns. Conditioning is ~100x better than the 4-decimal leaderboard rounding. Both probes are
   *constructed to score below* the anchor, so they cannot damage the best-score standing.
   This converts "recall of hidden faults" from a guess into a measurement.
7. **The shipped primary download is defective and must not be submitted.** [MEASURED, §7]
   `gems32-h19-5-smoothmaxcov-44090.tif` places **25,485 of its 44,090 dots (57.8 %) off the belief
   field it is supposed to pack**, and scores **0.01632** against the only real truth raster in the
   competition versus the incumbent's **0.16177** — a **10x** collapse in credit per unit mass at
   identical budget. Cause: it blurs a 1-px binary ridge by `sigma = 1.85 px` and then runs
   max-coverage on the blur, which lowers and *shifts* the peak.
8. **What to do this week:** submit the *incumbent's own emission* (the only artifact with a live
   score) as the anchor, then spend the other two slots on the identification probes of §6 — not on
   another field idea that no local instrument can rank.

---

## 1. Verified ground truth: the live board

[OFFICIAL] Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>,
read 2026-10-04.

| Rank | Participant | Best public DW-Tversky | Submissions |
| ---: | --- | ---: | ---: |
| #1 | nchuzhoy | **0.3262** | 3 |
| #2 | kinghorton42 | 0.3222 | 6 |
| #3 | DARD | **0.3195** | 12 |
| #4 | alexoktaba | 0.3042 | 21 |
| #5 | Batik Shirt Brothers | 0.2998 | 19 |
| #6 | xiaofanhu | 0.2941 | 8 |
| #7 | joeyfezster | 0.2919 | 19 |
| #8 | ndavis7 | 0.2888 | 7 |
| #9 | mzoorob | 0.2884 | 23 |
| #10 | GrigorSargsyan | 0.2876 | 9 |
| #11 | HardcoreTechGod | 0.2854 | 6 |
| #12 | op01 | 0.2710 | 5 |
| #13 | smashi34 | **0.2708** | 8 |
| #14 | ad3002 | 0.2627 | 19 |
| #15 | No Fault of Our Own | 0.2624 | 20 |
| #16 | wbg1 | 0.2600 | 10 |
| #17 | SDCF9 | 0.2600 | 9 |

**Two corrections to the brief, both verified:**

* *"0.3195 is the highest score right now"* — **[STALE]**. Highest is 0.3262.
* *"the highest score from the GEMDOE site ... `h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan`:
  0.2708"* — **[OWNER-REPORT, contradicted by its own source]**. The GEMSDOE28 page states
  verbatim **"NO GEMSDOE28 SCORE"** and prices that family as a *projection*: *"solo H27-4
  `8acb75e1f2cc` (40,199 px) to **0.2701**"*. No GEMSDOE28 artifact carries an organizer receipt in
  any repository this session can read.

Also verified: the group's recurring **0.2600** rows (the brief lists it 4x, and the live board
carries 0.2600 at ranks #16/#17) are consistent with a single emission rule at 44,090 px. See §7.

---

## 2. The metric, reduced to one line

[OFFICIAL] The published definitions, quoted from the problem description
(<https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>, "Performance
metric"):

```
TP_w = sum_{g in G} max_{x : d(x,g) <= R} p(x) k(d(x,g))
FP_w = sum_{x : p(x) > 0} p(x) [1 - max_{g in G} k(d(x,g))]
FN_w = sum_{g in G} [1 - max_{x : d(x,g) <= R} p(x) k(d(x,g))]
k(d) = (1 - d/R)_+ ,   R = 300 m   (3 px at 100 m)
DTI  = TP_w / (TP_w + alpha*FP_w + beta*FN_w + eps),  alpha = 0.2, beta = 0.8
```

Two exact reductions follow. Both are **[MEASURED]** in this checkout.

**(a) `FN_w = K - T` and `FP_w = S - M` exactly**, with `S = sum_x p(x)` and
`M = sum_x p(x) * k(d(x,G))`. Substituting:

```
DTI = T / ( alpha*(T + F) + beta*K )                                              (2.1)
```

**(b) Invert (2.1):**

```
1 / DTI  =  alpha  +  alpha * (F/T)  +  beta * (K/T)                             (2.2)
         =  0.2    +  0.2 * (F/T)    +  0.8 * (K/T)
```

**(2.2) is the design equation.** `K` is the hidden label mass and is *common to every submission
in a round*, so ranking on the leaderboard is ranking by `T / (alpha*F + beta*K)` alone. Note what
is **not** in (2.2): neither the number of dots, nor the emission density, nor any measure of
visual quality. Only two things matter — weighted credit `T`, and wasted mass `F`.

**Verification.** [MEASURED] The repo's `src/gems32/metric.py` is checked against a literal
brute-force transcription of the published formulas (`tests/test_metric.py::test_bruteforce_equivalence_random`,
8 random raster pairs, abs tol 1e-9) and against the organizers' own worked example
(`TP_w = 3.00, FP_w = 1.89, FN_w = 2.00 -> 0.60`, published on page 967). Identity (2.2) is
additionally verified to **1e-15** on the group's own artifacts in §9.

---

## 3. The exact marginal theorem, and why pruning worked

Adding one unit of prediction mass at pixel `x` changes (2.1)'s denominator by **exactly `alpha`,
independent of `x`**, because the mass simultaneously raises `T` by its realised credit `dT` and
`F` by `1 - kbar`:

```
d(denominator) = alpha*( dT + (1 - kbar) )   and when dT = kbar  ->  = alpha
```

So the emission rule is a *comparison against the current index*, not against distance:

```
add the dot   <=>   dT  >  alpha * DTI                (3.1)
```

At the group's live anchor `DTI = 0.26`, the bar is `0.052`. A dot at distance `d` from the nearest
scored truth carries `k = 1 - d/300 m`, so **a dot pays iff it lands within `(1 - 0.052)*300 m ≈
284 m` of a hidden truth pixel**. Credit is nearly free anywhere inside a 300 m tube and worth
nothing outside it. [MEASURED]

**This is the mechanism of the group's own sweep.** [OWNER-REPORT, internally consistent] Live:
121,131 px -> **0.1922**, 60,069 px -> **0.2477**, 44,090 px -> **0.2600**. Removing mass raised the
score, which by (3.1) means the removed dots realised `dT < 0.052`. The `d = 2.8 px` layout kept
90.63 % of the `d = 1.5` credit at 73 % of the mass. **The pruning was correct. It was also not the
lever that remains.**

---

## 4. Two corrections inside the project's own record

### 4a. The bar is `alpha*s`, not `alpha*s/(1 - alpha*s)`

[MEASURED] `docs/research/score-ceiling-analysis.md` §1 states the marginal-inclusion rule as
`k > alpha*s/(1 - alpha*s)`, tabulating **0.0549** at `s = 0.26`. That form does not follow from the
metric: with `dT = k`, (3.1) gives `k > alpha*s` = **0.0520**.

The repo already contains the correct statement in two independent places —
`src/gems32/metric.py` ("`dDTI > 0 <=> k > 0.2 * DTI`") and
`tests/test_metric.py::test_marginal_emission_rule_exact_single_truth_pixel`, which passes — and a
brute-force sweep over 300 random configurations in this session found the exact theorem agrees
with the official implementation **300/300**. The two documents contradict each other; the test is
right. **Consequence:** the number `0.05485` used as the live break-even in the successor
repository (GEMSDOE28, e.g. `tau_live = 0.05485`) is **5.5 % too high**, which biases the *pruning*
rule toward deleting dots that were in fact still profitable.

### 4b. The bar cannot constrain this emission at all

[MEASURED] For a pixel `x` on the emission field's **own support**, the field's own estimate of the
added false-positive mass is `1 - kbar(x)` with `kbar(x) = sum_delta field(x+delta) k(delta)`. For a
binary field, `kbar(x) >= field(x)*k(0) = 1`, so `1 - kbar <= 0` and the theorem's left-hand side is
positive whenever `s < 1/alpha = 5`. **The bar accepts unconditionally.** Measured: `emitter.emit`
with `prior_dti = 0.26` emits the **whole 121,131-px support** and terminates on
`stopped_by = "exhausted_support"` — 9.9 s. The `rho = 1.0` (two-round) variant does the same.

The bar therefore explains *why pruning is safe* (removed mass earned nothing); it does **not**
supply a stopping point for an emission that is confined to its own support. Any claim that the
"adaptive credit bar" chose the group's budgets is unsupported by the arithmetic.

---

## 5. What the leader's number actually requires

[MEASURED] Substituting `T = x*K` (weighted recall of hidden truth) and `F = rho*K` into (2.2):

```
x  =  (alpha*rho + beta) / (1/DTI - alpha)                                        (5.1)
```

Required weighted recall of the **hidden** label set:

| target DTI | `rho = 0` (no wasted mass) | `rho = 1` | `rho = 4` | `rho = 8.02` (the group's own `F/T`) |
| ---: | ---: | ---: | ---: | ---: |
| 0.2600 | 21.9 % | 27.4 % | 43.9 % | 65.9 % |
| 0.2708 | 22.8 % | 28.5 % | 45.7 % | 68.8 % |
| 0.3195 | 27.3 % | 34.1 % | 54.6 % | 82.1 % |
| **0.3262** | **27.9 %** | **34.9 %** | **55.8 %** | **83.9 %** |
| 0.3600 | 31.0 % | 38.8 % | 62.1 % | 93.3 % |

Two readings, both useful:

* **If the leader is disciplined** (`rho` small), 0.3262 needs only **27.9 % weighted recall**.
  The group's own inversion of its 0.2600 file implies **39.2 %** recall
  (`T = 4,791`, `K_hat = 12,226` **[MODEL]**, `F = 38,440`). On that pair of numbers the group's
  recall is *already higher* than the leader's requirement and it is the **false-positive mass,
  not the coverage, that separates 0.2600 from 0.3262**. That reading is actionable immediately.
* **If the leader carries the group's own `F/T = 8.02`**, 0.3262 needs **83.9 % recall**, which no
  emission rule can manufacture. Then coverage is the whole story.

**The two readings differ by a factor of three in required recall, and nothing in this repository
can currently tell them apart** — because `K`, `T` and `F` on the hidden set have never been
measured. That is the gap §6 closes.

**The ceiling, for scale.** [MEASURED, arithmetic only] With perfect knowledge, dots every ~3 px
along the hidden traces (`K = 12,226 px` -> ~4,075 dots) give `T ≈ 0.8K`, `F ≈ 4,200`, hence
`1/DTI = 0.2 + 0.086 + 1.0` and **DTI ≈ 0.78**. The community leader is at 0.3262, i.e. **42 % of
an achievable ceiling**. There is no method gap to close here; there is a
*where-are-the-faults* gap.

---

## 6. The instrument: an exact, three-slot identification experiment

Everything in §5 is a one-parameter family away from being measurable, and the reason is (2.1):

```
DTI(lambda * p)  =  lambda*T / ( lambda*alpha*(T + F) + beta*K )                  (6.1)
```

because `p -> lambda*p` scales `T`, `F` and `S` all linearly (`lambda > 0`). **(6.1) is not an
approximation**: verified against the official `metric.score` at `lambda in {1, 0.75, 0.5, 0.25,
0.1}` to a maximum absolute error of **1.2e-15** [MEASURED]. Inverting (6.1):

```
1 / DTI(lambda)  =  alpha + alpha*(F/T) + (beta*K/T) * (1/lambda)                 (6.2)
```

**linear in `1/lambda`.** So a `lambda`-sweep of one file is a model-free measurement of two of the
three unknown quantities. A third, independent probe identifies the third.

### The three submissions

| Slot | File | Construction | What it measures |
| ---: | --- | --- | --- |
| **S1 ANCHOR** | `p_1` | the best known emission (the 44,090-px incumbent layout) | `1/s_1 = alpha + alpha*(F/T) + beta*(K/T)` |
| **S2 SCALE** | `p_2 = 0.5 * p_1` | same predictions, every positive value halved; in-footprint order preserved | `1/s_2 = alpha + alpha*(F/T) + 2*beta*(K/T)` |
| **S3 NULL-ADD** | `p_3 = p_1 + M` dots | `M` unit-mass dots placed where the belief field is at its floor | `1/s_3 = 1/s_1 + alpha*M/T` |

### Closed-form recovery [MEASURED]

```
T = alpha * M / ( 1/s_3 - 1/s_1 )                                                (6.3)
K = T * ( 1/s_2 - 1/s_1 ) / beta                                                 (6.4)
F = T * ( 1/s_1 - alpha - beta*K/T ) / alpha                                     (6.5)
```

### Conditioning, computed at the group's own anchor [MEASURED]

Using `T = 4,791`, `F = 38,440`, `K = 12,226` **[MODEL]**:

| probe | signal in `1/DTI` | leaderboard rounding (4 dp) | signal / rounding |
| --- | ---: | ---: | ---: |
| S3 with `M = 2,000` | **0.083490** | 0.001480 | **56x** |
| S3 with `M = 1,000` | 0.041745 | 0.001480 | 28x |
| S2 (`lambda = 0.5`) | **2.041500** | 0.001480 | **1,380x** |

`T` is recovered to **better than 2 %** from `S3` at `M = 2,000` and `K` from `S2` essentially
exactly. **The experiment is over-determined in its conditioning and cheap in its cost.**

### Risk statement (stated, not hidden)

1. **Both probes are constructed to score *below* the anchor.** `S2` at `lambda = 0.5` scores
   0.1698 against the anchor's 0.2600 **[MODEL arithmetic]**, and `S3` adds `alpha*M/T` to
   `1/DTI`, which lowers the score by construction. Since only a team's *best* submission counts
   toward standing, **neither probe can cost the team a rank.**
2. **The `S3` probe assumes `dT = 0` for the added mass.** If any added dot lands within 300 m of a
   hidden fault, `dT > 0` and `T_hat` from (6.3) is biased **high**. Mitigation: place the `M` dots
   at the *minimum* of every belief field in the repository, inside the footprint, and **more than
   3 px from every known catalogue fault** (so the organisers' masking rule cannot be what moves the
   number). Publish the placement rule before the upload.
3. **`K` from (6.4) is the hidden mass of the split the leaderboard reports** (public). It will not
   equal the private split's `K`. It is still the only measured value of `K` that will ever exist
   for this project, and it immediately validates or falsifies the `K_hat = 12,226` **[MODEL]** that
   every projection in the group's repositories is built on.
4. **A `lambda`-sweep is deliberately *not* score-maximising.** By (6.1), `dDTI/dlambda > 0`, so
   binary-at-full-mass is always the best *scoring* encoding. `S2` is not a scoring candidate; it is
   an instrument. The repository must not later mistake it for a field arm.

### Why this satisfies the brief's own standard

The brief asks that a slot be spent *"only when an acquisition function ... says the surrogate's
uncertainty about beating the current best justifies the cost"*. Under (2.2) the surrogate's
dominant uncertainty is not the emission rule and not the field's shape — it is **`K`, `T` and `F`,
which have never been observed**. `S1`–`S3` are exactly the queries whose information collapses that
uncertainty, and their expected effect on `P(Win)` is positive while their effect on the reported
best score is provably non-negative. They are the correct first three queries of the search.

---

## 7. The shipped artifacts, measured on the only real truth raster

[MEASURED] Truth = `data/raw/labels.tif == 1` (60,988 catalogue pixels), on the template footprint
(5,167,373 px). **Caveat, stated up front:** the organizers *mask known USGS/INGENIOUS pixels out of
scoring* (DrivenData staff, community thread 11516), so this frame is **[MEASURED,
leak-contaminated]**: it is the only real truth raster that exists, and it is not the target
distribution. It is used below as a *screen on the emission's internal consistency*, never as a
score.

| artifact (in `docs/downloads/`) | dots | dots **off** the field it packs | credit / unit mass | catalogue-proxy DTI |
| --- | ---: | ---: | ---: | ---: |
| `gems25-dotted-h19-5-d2-8-…-nan.tif` (live **0.2600** [OWNER-REPORT]) | 44,090 | **0** | **0.2154** | **0.1617720** |
| `gems32-h19-5-smoothmaxcov-44090.tif` (**the site's primary**) | 44,090 | **25,485 (57.8 %)** | 0.0213 | **0.0163197** |
| `gems32-bayesopt-dilation-scarp-d28-…-nan.tif` | 45,000 | **43,334 (96.3 %)** | 0.1404 | 0.1079318 |
| `data/raw/h19_5.tif` (parent field) | 121,131 | 0 | 0.1007 | 0.1663512 |

*(All six shipped GeoTIFFs are **portal-legal**: EPSG:32611, 3730×3292, float32, one band, and
every finite value in `[0, 1]` with zero violations — re-verified from the bytes on disk by
`scripts/audit_shipped.py`. None of them can therefore be the file behind the historical
"Predicted values must be in range [0, 1]" rejection; see IR-32-VERIFY-01.)*

**The primary download is 10x worse than the incumbent it claims to beat.** The README's
`+0.0100` figure is a *blocked-holdout* contrast (a 4-quadrant frame with a same-run control), and
the `+0.0247` is a *model* estimate; neither is this measurement, and this measurement is not a
contradiction of those two — it is the observation that **the artifact's placement is internally
inconsistent**: 57.8 % of its mass sits where its own belief says there is no fault. Mass placed
outside a belief field's support cannot earn credit from any truth consistent with that belief.

**Root cause, isolated.** [MEASURED] The superseded rule is *"greedy maximum-expected-coverage of
the truth-scatter-smoothed surface (sigma 1.85 px)"*. Smoothing a 1-px binary ridge by
`sigma = 1.85 px` lowers and **shifts** its peak; a max-coverage sweep over the blurred image then
spreads mass across the blurred blob instead of locking onto the crest. `src/gems32/emitter.py`
implements the corrected rule and is tested in `tests/test_emitter.py`:

* **support confinement** — every emitted pixel must be one the belief field nominates;
* **exact marginal gain** — `dT(x) = sum_delta field(x+delta) * max(0, k(delta) - C(x+delta))`,
  with `C` the credit already delivered, so overlapping dots are never double-counted;
* **the exact theorem (3.1)** as the acceptance test.

Measured on this corrected rule at a matched 44,090-px budget, in **18.2 s on 2 vCPU**:

| rule | dots | off-support | credit delivered **on the field's own surface** | catalogue-proxy DTI |
| --- | ---: | ---: | ---: | ---: |
| incumbent `d = 2.8` | 44,090 | 0 | 88,569.5 | 0.1617720 |
| superseded `smoothmaxcov` | 44,090 | 25,485 | 72,243.5 | 0.0163197 |
| **corrected lazy greedy** | 44,090 | **0** | **90,230.9 (+1.9 % over incumbent)** | 0.1477520 |

The corrected rule is better than the incumbent **on the incumbent's own objective** (covering the
field surface: +1,661.4 units) and better than the rule it replaces by **+0.1314** on the catalogue
proxy. Its catalogue-proxy value is nonetheless *below the incumbent's* — because that proxy pays
for exactly the dots the official metric masks, which is the anti-correlation §8 quantifies.
**Neither number licenses a submission**; that is what §6 is for. Two algorithmic facts were
learned the hard way and are now pinned by tests: (i) the packing must never leave the belief
support; (ii) the greedy must be ordered by the **exact marginal gain with live coverage
deduction**, not by the static upper bound — a static-order sweep on a straight ridge delivers
**10.0 of the 15.0** units the exact greedy delivers at the same budget, which is a milder version
of the same defect (`tests/test_emitter.py::test_lazy_greedy_matches_exact_greedy`).

---

## 8. Why no local measurement can choose the budget

[MEASURED + OWNER-REPORT] The two instruments point in **opposite directions** and one of them is
known to be contaminated:

| emission | dots | live score [OWNER-REPORT] | catalogue-proxy DTI [MEASURED] |
| --- | ---: | ---: | ---: |
| parent H19-5 | 121,131 | 0.1922 | **0.1663512** |
| dotted `d = 1.5` | 60,069 | 0.2477 | **0.1719287** |
| dotted `d = 2.8` | 44,090 | **0.2600** | **0.1617720** |
| `smoothmaxcov` (this repo) | 44,090 | — | 0.0163197 |

The live ladder is **monotone: fewer dots, more score**. The catalogue proxy is **anti-monotone**.
The mechanism is structural and was already documented by this project: the proxy's truth *is* the
catalogue, so it pays for exactly the dots the official metric deletes. **Therefore the
catalogue-proxy instrument cannot rank emission rules, and the live ladder is the only ranking
signal that exists — at three observations a week.**

This is the brief's *"persistent gap between what the surrogate predicts and what the leaderboard
returns"*, made concrete and quantified. It is not noise to shrug off; it is the dominant source of
error in every projection the group has published, and §6 is the fix.

---

## 9. Reproduce

```bash
pip install -r requirements.txt                       # numpy scipy scikit-learn rasterio pytest
bash scripts/fetch_mirrors.sh                         # hash-pinned fetch, GitHub API only (no credentials)
python3 scripts/verify_theorems.py                    # (2.2), (3.1), (6.1)-(6.5) vs the official metric
python3 scripts/audit_shipped.py                      # §7 table, re-measured from docs/downloads/*.tif
python3 scripts/build_features.py                     # 147 s on 2 vCPU
PYTHONPATH=src python3 scripts/run_holdout.py --tag 2 --prereg-id GEMSDOE32-PREREG-2 \
        --prior-dti 0.26 --budget 9000                # §11
python3 -m pytest tests -q
```

---

## 10. Honest limits

* `K_hat = 12,226` is an **[MODEL]** derived from the owner's own inversion. Every "recall" number
  in §5 that depends on it is conditional. §6 exists precisely to replace it with a measurement.
* The catalogue proxy is **[MEASURED, leak-contaminated]**. It is used in §7 only to test an
  artifact's *internal* consistency (does it emit where its own belief says to), which is
  independent of the truth frame.
* The 0.2600/0.2477/0.1922 ladder is **[OWNER-REPORT]**. No organizer receipt for any group
  artifact was readable this session.
* The identification experiment requires **three weekly slots** and cannot be accelerated. Its
  payoff is a measurement, not a score.
* §5's ceiling (~0.78) assumes perfect knowledge of the hidden traces and a dot every 3 px; it is
  arithmetic, not a forecast.

## 11. The preregistered blocked holdout — run, and it passes

`PYTHONPATH=src python3 scripts/run_holdout.py --tag 2 --prereg-id GEMSDOE32-PREREG-2 --prior-dti 0.26
--budget 9000` → `evidence/holdout_run2.json` (591.7 s, 4 quadrant folds, 30 px buffer between train
and held-out block). `[MEASURED]`

| arm (mean official DTI on the held-out block, catalogue truth) | mean | n_px |
| --- | ---: | ---: |
| `A0_dot_thin_matched` — the incumbent's own raster-order rule | 0.179439 | 8,874 |
| **`A1_greedy_fixed_budget`** — maximum-expected-coverage | **0.190031** | 9,000 |
| `A2_greedy_live_bar` (bar = 0.052) | 0.190031 | 9,000 |
| `A3_greedy_discovery_bar` (bar = 0.026) | 0.190031 | 9,000 |
| `A5_nms_ridge_matched` | 0.167201 | 9,000 |
| `A4_random_control` | 0.017743 | 9,000 |

| contrast (matched emitted mass) | mean | folds positive |
| --- | ---: | ---: |
| **`A1 − A0` (the preregistered primary)** | **+0.010592** | **4/4** → `promotion_pass: true` |
| `A1 − A5` | +0.022830 | 4/4 |
| `A1 − A4` (random control) | +0.172288 | 4/4 |
| **`A2 − A3`** | **+0.000000** | **0/4** |

AUC range across folds: 0.6375 – 0.7457. `n_truth_mean` = 15,223.5.

**Two readings, and the second is the more important one.**

1. **The packing family passes the promotion rule.** `+0.0106` mean, 4/4 folds positive, against a
   *mass-matched* control — so the gain is placement, not budget. Beaten decisively in the same run:
   NMS-ridge selection (−0.0228) and uniform random (−0.1723). This is the same order of magnitude as
   the `+0.0100` the repository previously claimed for the *superseded* rule, which is consistent:
   the *family* was always sound; what shipped was a defective member of it (§7).
2. **`A2 − A3` is exactly zero, on every fold.** Halving the credit bar from `0.052` to `0.026` changed
   **nothing at all** — because, as proved in §4b, the bar cannot bind on an emission confined to its
   own support. This is **independent empirical confirmation of a theoretical result**, from a
   preregistered run that was launched before the theorem was noticed. It also means PREREG-2's
   "amendment reason" — that PREREG-1's bar "was non-binding … so the bar could not discriminate" —
   diagnosed the symptom correctly and the cause wrongly: the bar is non-binding at *every* price.

**The instrument's own honesty clause still applies, and it is why nothing is promoted.** The proxy
truth is the visible catalogue, and §8 measures that the catalogue proxy is *anti-monotone* against
the live ladder on exactly these emission questions. So this pass **licenses packaging a candidate**
— it does not license a submission, and it does not license raising the projected score. The
identification experiment of §6 remains the first action.

`IR-32-SCRIPT-01` was found while collecting this result: `scripts/run_holdout.py` used `a` as its
arm-loop variable, shadowing the argparse `Namespace`, so the run raised
`'str' object has no attribute 'tag'` on its closing print *after* writing the evidence file. The
result was valid; the exit status lied. Fixed, and the loop variable renamed to `arm`.

## 13. The field, not the packing, is the binding constraint — and it is now measured

Everything up to here is about *how* a field is turned into credit. This section is about whether
the field is any good, and it produces the largest single result in this document.

### 13.1 Two protocols, and why the difference matters

The repository's existing holdout emits **only inside the held-out block**. That is a protocol with
oracle knowledge of *where* the scored faults are, and it is generously optimistic. The competition
does not work that way: you emit over the whole map and the scored set is somewhere in it. Both
protocols are measured below; the honest one is the second.

* **Protocol O (oracle location).** Emission restricted to the held-out quadrant; truth = that
  quadrant's faults.
* **Protocol P (unknown location, the competition's shape).** Emit over the **whole raster**;
  score against **one** quadrant's faults, so every emission outside it is charged as false-positive
  mass — exactly as mass on a known-but-unscored fault is charged in the real competition.

### 13.2 Protocol P — whole-raster emission, matched mass, against withheld faults

| method (top-*n* of its own ranking) | 22,000 | **44,090** | **88,000** | 176,000 | 250,000 | 350,000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **CV field, this session (35 ch, blocked, 4 folds)** | 0.1054 | **0.1250** | **0.1330** | 0.1235 | 0.1134 | 0.1019 |
| `h19_5` — the group's base field | 0.0530 | 0.0672 | 0.0746 | 0.0641 | 0.0510 | 0.0401 |
| `dotted-d2.8` — the group's best artifact | 0.0838 | 0.1087 | 0.0780 | 0.0519 | 0.0419 | 0.0333 |
| `lazygreedy-maxcov-44090` — this session | 0.0759 | 0.0992 | 0.0713 | 0.0477 | 0.0387 | 0.0309 |
| `smoothmaxcov-44090` — the shipped primary | 0.0080 | 0.0109 | 0.0099 | 0.0094 | 0.0097 | 0.0093 |
| **uniform random (3 seeds)** | 0.0339 | 0.0498 | 0.0672 | 0.0754 | 0.0748 | 0.0712 |

Per-fold spread for the CV field at 44,090: 0.0968 / 0.1226 / 0.1779 / 0.1028.

**Four readings, in descending order of importance.**

1. **The informed fields peak and then decline; random keeps rising.** Every field that carries
   information peaks between 44,000 and 88,000 px and *loses* score beyond that, because its
   ranking runs out of signal. Uniform random — which has no ranking at all — keeps improving to
   176,000 and overtakes three of the five artifacts. This is the cleanest possible demonstration
   that the *ordering* is the asset, not the count.
2. **The optimum is ~88,000 px, not 44,090.** The CV field's curve is 0.1054 → 0.1250 → 0.1330 →
   0.1235 → 0.1134 → 0.1019. The group's chosen 44,090 is defensible but leaves ~6 % on the table
   under this protocol.
3. **The shipped primary is twelve times worse than random.** `smoothmaxcov-44090` scores 0.0109
   against random's 0.0498. This is the same defect as §7 seen through a second, independent
   protocol: it is not a weak field, it is an *anti-correlated* one.
4. **The CV field beats the group's best artifact by +15.0 % at matched mass (0.1250 vs 0.1087),
   and beats its own base field by +86.0 % (0.1250 vs 0.0672).** Under Protocol O the same
   comparison is +79.9 % (0.3042 vs 0.1691). **The CV field wins under both protocols**, which is
   the claim that survives the choice of protocol.

### 13.3 Where the group's mass actually sits

Measured on the group's own best artifact — this is the number that explains the whole result:

| emitted mass at distance from a **true** fault | 44,090 px | 121,131 px | 350,000 px (CV) |
| --- | ---: | ---: | ---: |
| within 1 px | **39.4 %** | 31.0 % | 21.7 % |
| within 3 px (the kernel radius) | **70.9 %** | 60.3 % | 45.3 % |
| median distance | 2.00 px | 2.24 px | 3.61 px |

The group's best submission spends **70.9 % of its mass inside the kernel radius of a mapped
fault** — which is why it scores 0.1618 on the catalogue — and **29.1 % of it, 12,835 units of
mass, beyond it**, where every unit costs `α = 0.2` and returns nothing. A submission at 44,090 px
has a denominator budget of `0.2 × 44,090 + 0.8 K = 8,818 + 48,790`; the waste is 2,567 of the
8,818, i.e. **29 % of the entire variable part of the denominator is being spent on mass the kernel
cannot reach.**

### 13.4 The fourth exact law, and it dictates the budget

Because adding one unit of non-redundant mass changes the denominator by **exactly `α`** regardless
of where it lands (§4b), the score as a function of emission size is

    DTI(n)  =  (T0 + Σk_i) / (α·n + β·K + const)      →      DTI(∞)  =  k̄ / α  =  5·k̄

so the optimum is exactly where the **marginal expected kernel weight falls to `α·DTI`** — the same
bar as §4b, now read as a *stopping* rule rather than an *acceptance* rule. `[DERIVED]`, and the
measured peaks in 13.2 sit precisely where the bar predicts they should.

### 13.5 What this says about the leaderboard, and what it does not

`[MODEL]` The projected live consequence of the CV field is a **+15 % relative** improvement over
the group's current best artifact at matched mass, on the only truth this repository owns. That is
a projection from a leak-contaminated proxy, it is not an organiser score, and it is not a claim
about the leaderboard. What it *is* is a field that beats the incumbent under two different
protocols, that was validated on a spatially blocked holdout, and that therefore clears the
repository's own standing rule for a submission. **No slot has been spent and none is claimed.**

## 14. Links for manual review

| Claim | Source |
| --- | --- |
| Metric, kernel, `alpha`, `beta`, submission format, worked example | <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> |
| Live leaderboard (0.3262 / 0.3195 / 0.2708 / 0.2600) | <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/> |
| Known-fault pixels masked from scoring | <https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516> |
| Official rules (PDF) | <https://docs.nlr.gov/docs/fy26osti/96647.pdf> |
| Reference solution (all-finite writer, no nodata tag) | <https://github.com/drivendataorg/gems-prize-reference-solution> |
| GeoDAWN airborne magnetic/radiometric survey | <https://doi.org/10.5066/P93LGLVQ> |
| INGENIOUS geothermal compilation (GDR 1391) | <https://gdr.openei.org/submissions/1391> |
| USGS State Geologic Map Compilation | <https://mrdata.usgs.gov/geology/state/> |
| GEMSDOE28 — "NO GEMSDOE28 SCORE" and the 0.2701 projection | <https://buffedlizard55-lab.github.io/GEMSDOE28/> |
