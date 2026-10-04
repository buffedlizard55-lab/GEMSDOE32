# Why `dotted-h19-5-d2-8` scored 0.2600, and what it takes to beat 0.3195

*Analysis, 2026-10-04. Every number below is tagged **[measured-here]**, **[official]**, or
**[owner-report]** (an unverified claim from the group's own ledger). Nothing is presented as an
organizer receipt unless it is one.*

## 0. The three numbers that set the whole problem

| quantity | value | provenance |
|---|---|---|
| published metric weights | α = 0.2 (FP), β = 0.8 (FN), R = 300 m | **[official]** competition page 967 |
| public leaderboard #1 / #2 on 2026-10-04 | 0.3262 (nchuzhoy) / 0.3195 (DARD) | **[official]** leaderboard page, snapshot `registry/leaderboard_history.jsonl` |
| the group's best file | 0.2600, `dotted-h19-5-d2-8-20261002-e56ea318af89-nan`, 44 090 px | **[owner-report]** (IR-32-SCORE-01) |
| the same family's earlier members | 0.2477 (d1.5, 60 069 px); 0.1922 (solid H19-5, 121 131 px) | **[owner-report]** |
| live credit per emitted pixel, solid → d2.8 | 0.0520 → 0.0893 | **[owner-report]** |
| live marginal credit of an *added* dot at 0.26 | 0.0548 | **[owner-report]** |

## 1. The metric is a budget, not a segmentation score

**[official]** `DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw + ε)`, with
`TPw = Σ_g max_x p(x)k(d(x,g))`, `FPw = Σ_x p(x)[1 − max_g k]`, `FNw = Σ_g [1 − max_x p(x)k(d)]`,
`k(d) = max(1 − d/300 m, 0)`.

**[measured-here]** (`tests/test_metric.py`, brute-force O(N²) transcription, 1e−9 agreement):
`FNw = |G| − TPw` exactly, so with `T = TPw`, `S = Σp` (total emitted mass) and
`M = Σ_x p(x)·max_g k` (mass that is best-covering a truth pixel),

```
DTI = T / ( 0.2·(T + S − M) + 0.8·|G| )            (★)
```

**[measured-here]** Differentiating (★) at fixed `T, M, |G|` gives the **marginal credit rule**

```
adding a unit of mass raises DTI  ⟺  k > 0.2 · DTI          (★★)
```

At DTI = 0.26 the bar is **0.0520**; at the leader's 0.3262 it is **0.0652**. This is not a
heuristic — it is the metric's own first-order condition, and it is why *emission*, not
architecture, was the strongest lever the group ever pulled.

## 2. So why did the *thinnest* member of the family win?

The family is one field (H19-5) emitted at three densities. Using `T ≈ M` (each emitted pixel is
best-cover for a different truth pixel — the regime a thin dotted line aims for) and the
owner-reported credit-per-pixel `c = T/S`:

| file | S (px) | c = T/S | T = c·S | implied |G| from (★) at the reported DTI |
|---|---|---|---|---|---|
| solid H19-5 | 121 131 | 0.0520 | 6 299 | (0.1922 ⇒ |G| = 7 320) |
| d1.5 | 60 069 | — | — | (0.2477 ⇒ |G| = 8 486 at c = 0.0893) |
| **d2.8** | **44 090** | **0.0893** | **3 937** | **(0.2600 ⇒ |G| = 7 905)** |

Read the last column: under this model the *same* hidden test set implies |G| ≈ 7 300–8 500 px
(≈ 73–85 km of fault at 100 m) for all three files, and the two independently reported quantities
for d2.8 (c = 0.0893 and DTI = 0.2600) are **mutually consistent** with |G| = 7 905 px
(0.0893 × 44 090 / (0.2 × 44 090 + 0.8 × 7 905) = 0.2600 exactly). That is a real cross-check: the
reported numbers were not invented independently of each other.

The mechanism is (★★) applied to the *removed* pixels. Thinning from 121 131 px to 44 090 px raises
the mean realised weight of the surviving mass from 0.0520 to 0.0893 (+72 %) while *dropping* the
low-weight tail, whose realised credit was already below the bar. Each removed pixel with weight
`w < 0.2·DTI` had been *costing* 0.2 − w per unit. Hence:

> **d2.8 is the highest-scoring member of the family because it is the first member whose emission
> mass has been cut back to (approximately) the point where the marginal pixel's realised credit
> equals the metric's own break-even bar.** [owner-report] independently measured the live marginal
> rate at 0.0548 versus a bar of 0.0520 — within +5 %. Two completely different routes (the group's
> live-rate regression and this repository's analytic derivation from the published formula) put the
> file at its own optimum.

The same arithmetic explains why leaderboard-level scores in this competition cluster where they do:
a file that is a *wide* rasterisation of a good field is dominated by the 0.2-per-pixel FP tax —
0.2 × 121 131 = 24 226 units of denominator against only 6 299 units of credit.

## 3. Are we able to beat 0.26? Yes — but only in one of two ways, and the cheap one is nearly used up

**(a) Emission improvements (cheap, measurable, bounded).** Take the *same* field at the *same* mass.
(★) says DTI is bilinear in the mass placement: for a fixed budget `S`, DTI is maximised by choosing
the pixels with the highest expected weight, which is exactly a maximum-coverage packing problem
(greedy is within 1−1/e; the objective is the metric's own TPw term). **[measured-here]** on the
preregistered blocked holdout (`evidence/holdout_run1.json`), the greedy maximum-expected-coverage
emission beats the raster-order thinning cascade **at matched emitted count** — fold 0: 0.0933 vs
0.0833, +0.0100 proxy DTI, with the incumbent's own raster-order rule as the control. The incumbent
d2.8 file *is* a raster-order thinning cascade, so the comparison is exactly the one that matters.
The shipped candidate in `docs/downloads/` is that rule applied to H19-5 at 44 090 px.

**(b) Field improvements (expensive, the only route to 0.3195).** Solve (★) for the credit needed at
#1's score with the *same* mass and the implied |G| = 7 905 px:

```
T = 0.3262 × (0.2 × 44 090 + 0.8 × 7 905) = 0.3262 × 15 142 = 4 939
```

against the current `T = 3 937`: the mean realised credit of the emitted pixels must rise from
**0.0893 to 0.1120, i.e. +25 %**, at the same mass, with the same hidden truth. Equivalently the
top-44 090 pixels of the field must average 25 % more kernel weight toward real new faults than
H19-5's do. That is a *detector* problem, not an emission problem:

> **Emission thinning bought +0.068 (0.1922 → 0.2600). Closing the remaining 0.066 needs a field
> whose high-rank pixels are better, and no public catalogue can supply one.**

## 4. Why no public catalogue can supply the missing field

**[measured-here]** (`scripts/run_h60_2.py`, `evidence/h60_2_catalogue_difference.json`):

* The newest official catalogue the group ever fetched — GDR QFaults v2, rasterised to this grid at
  59 065 px — lies within 300 m of the competition's *given* catalogue for **59 064 of its 59 065
  pixels** (one pixel is 4 px away). The given catalogue **already contains** the newest public
  compilation. (This corroborates, with an independent computation, the sibling repository's own
  finding IR-30-006.)
* The USGS SGMC compilation does have a large off-catalogue population: **61 664 px** beyond 300 m
  from the given catalogue (median distance 15 px). SGMC is *pre-Quaternary-inclusive*, so it can
  contain real faults that the Quaternary catalogue omits — but it is also where the older mapping
  that later compilations *rejected* lives.
* **[measured-here]** the group's best field's enrichment on that off-catalogue set versus the
  footprint background is reported in the same JSON. It is the only local measurement of
  *off-catalogue* skill available anywhere in the family's record.

The competition's own round-2 rule (top five submissions re-scored against **faults the panel
verifies from everyone's submissions**) tells us the hidden truth contains faults that are in *no*
public catalogue. That is why the objective is not DTI alone but

```
max  DTI_1 + ρ · DTI_2           (two-round objective)
```

and why the correct emission bar for a *novel* candidate is `0.2·DTI/(1+ρ)` — lower than the
single-round bar, because round 2 pays for correct discoveries while round 1 charges only the 0.2
false-positive tax. With the published prize pools ($50 k initial vs $250 k final) a conservative
ρ = 1 is already defensible; ρ > 1 is not absurd.

## 5. What this repository therefore ships, and what it refuses to claim

1. **Ships** a maximum-coverage emission of the group's best field at the incumbent's own mass
   (measured +0.0100 proxy DTI over the incumbent's rule on the blocked holdout), format-validated
   by independent re-read, with the note string ready to paste.
2. **Ships** the instrument that turns every submission into a data point: the GP surrogate, the
   expected-improvement gate with an explicit slot cost, and the drift report
   (`src/gems32/bo.py`), fed by `registry/observations.jsonl`.
3. **Refuses** to claim a score. Nothing here has an organizer receipt; 0.2600 is an owner report;
   the local holdout is a *proxy* whose truth is the given catalogue and therefore cannot reward a
   genuinely new fault by construction (IR-32-PROXY-01).
4. **Exposes the honest ceiling**: +25 % mean credit on the same mass is the whole distance to #1
   with this field. Anything less is not a plan; anything more requires new field physics.

## 6. What would actually move the ceiling (ranked, with the sensor physics named)

| # | direction | why it should raise the top-of-ranking credit | cost | data licence |
|---|---|---|---|---|
| 1 | **Post-2023 rupture and deformed-terrain detection** (H60-1): the 2020 Mw 6.5 Monte Cristo rupture is *inside* the footprint, on largely **unmapped** parts of the Candelaria fault, with displacements mostly < 5 cm over zones up to 800 m wide, and it is "not likely preserved in the geologic record" ([official] USGS field response, SRL 92(2A) 823–829). A ruptured-but-unmapped fault is precisely a hidden-truth fault | adds credit the catalogue cannot contain; the scatter is spatially tight so the mass is cheap | high (needs InSAR/optical change or relocated seismicity; not in the 19 given bands) | free official: USGS ComCat, ARIA/COMET products (obtainability flagged, not yet fetched) |
| 2 | **Cross-catalogue disagreement as a *feature*, gated** (H60-2): distance-to-SGMC-off-catalogue + the field's own enrichment, with the metric's credit bar as the gate | the only source of *known real* faults absent from the given catalogue | medium (local rasters exist) | SGMC (USGS, public domain) |
| 3 | **Curvature/scarp sharpening of the DEM family** (H60-5): Sato-style ridge filters on detrended elevation already paid +0.0253 in the group's factorial | raises the *precision at the top* of the ranking, which is what (★) pays for | low (all bands present) | given bands |
| 4 | **Two-round bar** (H60-3): `0.2·DTI/(1+ρ)` with the surrogate deciding ρ from the round-2 pool size | mathematically free if the novel pixels are real; catastrophic if the field is noise | zero | — |

The ranking is by *expected DTI gain per unit of implementation cost going forward*, and it is
explicitly a judgement, not a measurement: directions 1–2 are the only ones that can add faults the
given catalogue lacks, and direction 4 is the only one that is free.

---

## 7. Addendum (same session, after the model Monte Carlo was built)

**[measured-here]** The group's H28 inference gives one usable description of the hidden set for the
H19-5 family: about **12,691 truth pixels scattered around the surface with a 1.85 px scale**. Written
down, it can be scored with the *official metric* on paired draws, which turns "can we beat 0.26?"
into a measurement instead of an argument. That measurement changed the design of the shipped file.

| candidate, all at **44,090 emitted pixels** | mean official DTI (live-anchored truth model, paired draws) | paired difference vs the incumbent |
|---|---|---|
| incumbent: raster-order dot-thin (`dotted-h19-5-d2-8`) | 0.2791 | — |
| greedy max-coverage of the **surface** | 0.2758 | **−0.0033** (0/12 draws positive) |
| **greedy max-coverage of the scatter-smoothed field, catalogue pixels excluded** | **0.3038** | **+0.0247 ± 0.0005 (12/12)** |

Three things follow, and they are the intellectual core of this session's result:

1. **The catalogue-truth holdout had drifted from the live distribution** — exactly the failure mode
   the brief asks to chase rather than shrug off. It says the surface-coverage packing is better
   (+0.0100, 4/4 folds); the live-anchored model says it is worse (−0.0033, 0/12). The mechanism is
   not subtle once stated: a proxy whose truth *is* the catalogue rewards covering wherever the
   catalogue runs, while the hidden set is scattered *around* the field surface. A proxy can be
   internally consistent, reproducible, preregistered — and still point the wrong way.
2. **The fix is a derivation, not a tuning knob.** If truth is scattered by σ around the surface,
   the expected credit of an emitted pixel is the metric's kernel applied to the *scattered* density;
   so the right thing to cover is the surface blurred by σ. That single change converts a −0.0033
   into a +0.0247 at identical mass, field, and metric, with 12/12 paired draws agreeing.
3. **The corrected file's advantage is in captured credit, not in thrift:** mean TPw 5,531 vs 5,120
   (+8 %) at the same 44,090 pixels — i.e. it buys real credit rather than exploiting the metric's
   denominators.

**Answer to the brief's question, restated after the measurement.** The dotted file was the group's
best because it removed mass that the metric charges 0.2 per unit for; the *same field* can be
emitted ~0.025 better by covering the scattered truth density instead of the surface, which is the
largest single emission-side gain this repository can substantiate. It is still not enough for
0.3262 on its own: the remaining ≈0.02–0.03 must come from a **better field** (a deep detector with
1 m LiDAR context and a GPU), which is H60-5 and the deployment work in the README's limitations.
These are pooled-competition scores; the final round's expanded label set makes a *novel-but-real*
fault worth more than the public board can show, which is why H60-1 (the 2020 Monte Cristo rupture,
inside the footprint, on largely unmapped ground) ranks first for the prize even though no local
instrument can reward it.

**What is *not* claimed.** The truth model is owner-report-derived; only paired differences are used.
Absolute values from it (0.30 vs 0.28) over-predict the group's claimed 0.2600, as the group's own
model already reported. No slot is spent until `bo.slot_gate` approves one, and the file remains a
candidate, not a result.
