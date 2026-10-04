# Round 3 — five candidate hypotheses, ranked by *measured* layer discrimination

**Status. `[MODEL]` + `[MEASURED]`. Nothing in this document has been submitted, and no weekly
slot is requested by it.** All figures are computed from the organiser's own
`training_features.tif` (19 bands, SHA-256 `4371c82e…`) and `labels.tif` (`7ba308cc…`), both
digest-verified against `registry/data_manifest.json`. Every band name below is quoted from the
GeoTIFF band descriptions, not inferred.

---

## 0. What changed in this round: the evidence is now measured, not asserted

Round 2 (`hypotheses-round2.md`) ranked five hypotheses by argument. This round ranks five by
**measurement**. Two measurements drive the ranking, and both are reproducible:

**(1) Per-layer discrimination of held-out faults, spatially blocked.** For each of the 35 stack
channels we compute the two-sided AUC (faults vs background, sign-agnostic) inside each of four
spatially disjoint quadrants and report the mean and the range across blocks. Script:
`/tmp/band_auc.py`; full table `docs/research/band_auc.json`.

| rank | official band | description (organiser's words) | mean 2-sided AUC | block range |
| ---: | --- | --- | ---: | --- |
| 1 | **`tc` (band 6)** | "Tilt angle or total curvature — magnetic field derivative **for edge detection**" | **0.5735** | 0.539 – 0.610 |
| 2 | `geod_shearrate` (7) | "Geodetic shear rate — rate of angular deformation from GPS/InSAR" | 0.5721 | 0.504 – 0.621 |
| 3 | `det_elev_slope` (19) | "Detrended elevation slope" | 0.5652 | 0.547 – 0.592 |
| 4 | `iso_grav_anom_slope` (5) | "Isostatic gravity anomaly slope" | 0.5521 | 0.525 – 0.581 |
| 5 | `geod_2ndinv` (4) | "Geodetic second invariant — strain rate tensor magnitude" | 0.5488 | 0.518 – 0.578 |
| 6 | `ieq_n100a15` (16) | "Earthquake intensity or density (n=100 km, a=15°)" | 0.5413 | 0.502 – 0.575 |
| 7 | `geod_dilaterate` (8) | "Geodetic dilatation rate — volumetric strain" | 0.5377 | 0.501 – 0.570 |
| … | … | … | … | … |
| 19 | `tmi` (14) | "Total magnetic intensity" | 0.5134 | 0.502 – 0.533 |

The derived channels outrank every official band except `tc`: `curv_s2` **0.5871**, `relief5`
0.5711, `curv_s1` 0.5707, `tophat2` 0.5683.

**(2) What the line transforms actually buy.** Applying a curvature/zero-crossing transform to a
band helps some layers and *hurts* others — measured, not assumed:

| layer | raw | best line transform | change |
| --- | ---: | --- | ---: |
| `det_elev` (12) | 0.5256 | zero-crossing, σ=1.5 px → **0.5786** | **+10.1 %** |
| `depth_to_base_surf` (15) | 0.5246 | zero-crossing, σ=3.0 px → 0.5429 | +3.5 % |
| `iso_grav_anom_slope` (5) | 0.5518 | zero-crossing, σ=3.0 px → 0.5545 | +0.5 % |
| `geod_shearrate` (7) | **0.5833** | any ridge/zero-crossing → 0.527–0.580 | **worse** |
| `tc` (6) | **0.5752** | any ridge/zero-crossing → 0.512–0.532 | **worse** |
| `geod_2ndinv` (4) | 0.5494 | any ridge/zero-crossing → 0.513–0.527 | **worse** |

**The design consequence, and it is the single most useful thing in this document:** the
potential-field and subsurface layers are *line* layers and must be transformed; the geodetic
strain-rate layers are *regional-field* layers and must be used raw. The repository's stack does
neither consistently — it derives channels from **only 6 of the 19 official bands** (2, 12, 13, 14,
15, 17) and leaves **13 bands with no transform at all** (1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 18,
19) — including `tc`, the most discriminative band on the map.

---

## H62-1 — Tilt-angle (TDR) zero-crossing lineaments with magnetic dip polarity — **FALSIFIED, DO NOT PURSUE**

**Rank 6 (demoted from 1). Status `[MEASURED — FAILED]`. Kept in the register because a
falsified hypothesis is a result and deleting it would be dishonest.**

> **Falsifier result (`/tmp/falsify_h621.py`, run 2026-10-04).** Ten variants of band 6 were built
> — a hard zero-crossing locator, a soft (Gaussian-weighted) zero-crossing locator, and a negative
> Laplacian, each at σ ∈ {1.5, 3, 6} px, plus a gradient magnitude — and scored on the same four
> spatially disjoint blocks.
>
> | variant | mean AUC | min | max |
> | --- | ---: | ---: | ---: |
> | **raw band06 (the repository's channel)** | **0.5736** | 0.5373 | **0.6109** |
> | zero-crossing *soft*, σ = 3.0, w = 0.5 | 0.5737 | 0.5378 | 0.6145 |
> | zero-crossing *soft*, σ = 1.5 | 0.5728 | 0.5353 | 0.6144 |
> | curvature (−LoG), σ = 6.0 | 0.5442 | 0.5127 | 0.5898 |
> | curvature (−LoG), σ = 3.0 | 0.5372 | 0.5171 | 0.5719 |
> | zero-crossing *hard*, σ = 3.0 | 0.5083 | 0.5023 | 0.5152 |
> | \|grad\| band06 | 0.5068 | 0.5037 | 0.5110 |
>
> The best variant **ties** raw at +0.0 % (0.5737 vs 0.5736) and **not one of the ten variants beats
> raw on all four blocks.** The hard zero-crossing locator — the textbook construction — is *worse
> than random* (0.5058).
>
> **Why it failed, and this is the useful part.** The organisers' description already tells us:
> band 6 *is* "magnetic field derivative for edge detection". Differentiating an
> already-differentiated field does not sharpen an edge, it amplifies noise — which is exactly what
> the −LoG and gradient results show. **The layer is already the detector.** The generalisation,
> which now holds across every measurement in this document:
>
> **transform only the layers that are raw fields. The organisers have already differentiated the
> derivative products, and re-differentiating them destroys signal.**
>
> This is consistent with the negative results measured in §0: transforms *hurt* `tc` (−0.04 to
> −0.06), `geod_shearrate` (−0.00 to −0.06) and `geod_2ndinv` (−0.02 to −0.04), and help only the
> genuinely un-transformed fields — `det_elev` (+0.053, the +10.1 % result that carries H62-4) and
> `depth_to_base_surf` (+0.018).
>
> Consequence: **H62-4 rises to rank 1**, and H62-3's "use the strain layers raw" is promoted from
> an inference to a measured finding. The original H62-1 text is preserved below for the record.

<details><summary>H62-1 as originally proposed (falsified)</summary>



* **Layers.** Band 6 `tc` ("Tilt angle or total curvature — magnetic field derivative for edge
  detection"), supported by band 3 `tmi_hg` ("Total magnetic intensity horizontal gradient"), band
  9 `tmi_vg` ("vertical gradient") and band 1 `mag_anom`.
* **Physical signature.** The tilt angle is the classical magnetic edge detector (Miller & Singh
  1994; Verduzco et al. 2004): it is the arctangent of the vertical derivative over the horizontal
  derivative of the field, and it is *scale-independent*, so the **zero-crossing contour** of the
  tilt angle traces a magnetic contact or fault **regardless of the depth of the source**. The
  organisers have handed us this layer pre-computed and labelled it "for edge detection" — and
  nobody in this repository has ever computed its zero-crossings.
* **Why it catches a fault *missing from the catalogue*.** The USGS/INGENIOUS compilation is
  built from field mapping, LiDAR and historical seismicity — it is **surface-expression-led**. A
  fault that is buried under basin fill, or that has not ruptured the surface in the Holocene,
  produces **no scarp to map** but still offsets the magnetic basement and therefore still produces
  a tilt-angle zero-crossing. This is the exact class of fault the catalogue systematically lacks.
* **How it differs from what this repository already implements.** `features.py` contains
  `CHANNELS` with `band06` as a *raw value* and no transform of it whatsoever. There is no TDR, no
  zero-crossing locator, and no polarity term anywhere in `src/gems32/`. The repository's magnetic
  channels are `tmi_edge` = smoothed |∇ band 14| and `rtp_edge` = smoothed |∇ band 2| — both are
  gradient magnitudes, which are **blob-like and sign-blind**; the tilt angle is a *ratio* and its
  zero-crossing is a *line*. Measured: `tmi_edge` is a near-duplicate of official band 3
  (Spearman ρ = +0.9330) and scores only 0.5230, i.e. the repository's magnetic work is currently
  buying almost nothing.
* **Measured support.** `tc` is the highest-ranked official band (0.5735, and the *only* official
  band whose block range reaches 0.61). The transform itself is the untested step.
* **Falsifier.** Compute the tilt-angle zero-crossing mask at σ ∈ {1.5, 3, 6} px; if no scale beats
  the raw band's held-out AUC on any of the four blocks, the hypothesis is dead.
* **Honest risk.** `tc` is described as "tilt angle **or** total curvature". If the organisers
  shipped total curvature rather than the tilt angle, the zero-crossing interpretation is wrong and
  the transform degrades to a curvature ridge — which the table above already shows is *worse* than
  raw on this band (0.512–0.532 vs 0.5752). This hypothesis therefore has a **specific,
  cheap, binary falsifier and it must be run before anything else in this document.**

</details>

---

## H62-2 — Buried-basement escarpment: depth-to-basement step conjoint with a gravity gradient, gated by *absence* of surface expression

**Rank 2. Expected DTI gain: high. Implementation cost: low–medium.**

* **Layers.** Band 15 `depth_to_base_surf` ("thickness of sedimentary cover") with band 18
  `iso_grav_anom_hg` ("horizontal rate of change") and band 13 `iso_grav_anom`.
* **Physical signature.** A normal fault in an extensional basin offsets the **basement**
  surface, so `depth_to_base_surf` has a *step* across the fault trace — a ridge in
  |∇ `depth_to_base_surf`|. If the fault dies out before reaching the surface, the step is present
  in the basement surface and in the isostatic gravity gradient, while the **detrended elevation**
  (band 12) and **its slope** (band 19) show nothing.
* **The conjunction is the hypothesis.** Emit only where (i) the basement-step ridge, (ii) the
  gravity-gradient ridge and (iii) the strike of the two agree, **and** (iv) the surface-quiescence
  term |∇ `det_elev_slope`| is *low*. Condition (iv) is what makes this a search for the catalogue's
  blind spot rather than another detector of the catalogue.
* **Why it misses the catalogue.** Compilations are assembled from what a mapper can see. A
  basin-fill-covered fault is unmappable in the field and has no LiDAR scarp; but the basin itself
  exists because of it, so the basement and gravity fields still record it.
* **How it differs from the repository.** The stack has a bare `depth_grad` = smoothed
  |∇ band 15|, and nothing else: no conjunction with gravity, no strike-agreement test, and
  critically **no quiescence gate** — the repository has never used the *absence* of surface
  signal as evidence.
* **Measured support.** `depth_to_base_surf` is the *only* one of the three biggest subsurface
  bands whose line transform improves it (0.5246 → 0.5429, +3.5 %); `iso_grav_anom_slope`
  also improves under a zero-crossing transform (→ 0.5545).
* **Falsifier.** The conjunction must beat its own best single member on ≥3 of 4 blocks. A
  conjunction that does not beat its strongest member is not a conjunction, it is a filter.

## H62-3 — Geodetic strain-tensor emission prior (use the strain layers *raw*, as a weighted prior rather than a detector)

**Rank 3. Expected DTI gain: medium–high. Implementation cost: low.**

* **Layers.** Band 4 `geod_2ndinv`, band 7 `geod_shearrate`, band 8 `geod_dilaterate` — "measure of
  strain rate tensor magnitude", "rate of angular deformation from GPS/InSAR", "rate of volumetric
  strain".
* **Physical signature.** These three are the **only layers in the whole stack that measure
  *present-day* deformation.** Everything else is a snapshot of accumulated geology. A fault that
  is currently loading but has no Holocene rupture is invisible to geomorphology and to magnetics,
  but it is *not* invisible to a geodetic strain field.
* **Why it catches an off-catalogue fault.** Geodetic strain is spatially broad and diffuse — it
  cannot *locate* a fault trace, which is presumably why the repository left it as three ordinary
  channels. But it is an excellent **prior**: it says *where in the map a new fault is plausible at
  all*. Used as a multiplicative weight on a line detector it suppresses the parts of the map that
  are aseismic and cannot host the target class.
* **How it differs from the repository.** Nothing in `src/gems32/` uses the strain layers as a
  prior; they are three columns among 35 in a gradient-boosted classifier, where their broad,
  smooth, regional character is close to useless (a per-pixel tree splits them into contours).
  The repository's own feature docstring argues the opposite — that raw fields should be replaced
  by line transforms — and the measurement above says that argument is **wrong for these three
  bands** (raw 0.5833/0.5494/0.5377 vs 0.513–0.532 transformed).
* **Measured support.** `geod_shearrate` is the second-best official band on the map (0.5721,
  block max 0.6213 — the single highest block score of any official band). All three strain bands
  are in the top 8 of 19.
* **Falsifier.** A strain-weighted emission must beat the unweighted emission at matched mass on
  ≥3 of 4 blocked folds. If it only re-orders within an already-correct support, it is worthless.

## H62-4 — Multi-scale curvature of *detrended elevation* as the primary line detector (`curv_s2` is the best channel in the entire stack)

**Rank 4. Expected DTI gain: medium. Implementation cost: very low (already built).**

* **Layers.** Band 12 `det_elev` ("topography with regional trends removed") and band 19
  `det_elev_slope`.
* **Physical signature.** Fault scarps in an extensional province produce **curvature** — not
  offset — in the detrended topography. The relevant observable is the second derivative, at the
  scale of the scarp (a few pixels), not the raw elevation.
* **Measured support, and it is the strongest single number in this document.** `curv_s2` scores
  **0.5871** — higher than *any* of the 19 official bands, and it is the only channel that holds
  above 0.55 on every block (0.558 – 0.620). The zero-crossing transform of the parent band
  `det_elev` gives the largest transform gain measured anywhere in this work
  (0.5256 → 0.5786, **+10.1 %**). Two independent constructions — a Laplacian and a
  zero-crossing locator — agree that the second-derivative structure of detrended topography is
  where the signal is.
* **Why it catches an off-catalogue fault.** Not every unmapped fault is *buried*; some are simply
  **not in this compilation yet** — the Great Basin is large, and mapping is incomplete. A scarp
  that exists in the DEM but was never field-checked is precisely a fault that is real, findable,
  and absent from the catalogue.
* **How it differs from the repository.** The repository *has* `curv_s1`/`curv_s2`, so the honest
  statement is that this hypothesis is **already half-implemented** and its value is **not yet
  collected**: `curv_s2` carries the highest measured fault discrimination in the stack, and the
  current emission does not privilege it. The new work here is not a new channel — it is
  **re-weighting the emission toward the channels that measurably discriminate**, which the
  repository has never done (`run_holdout.py` treats all 35 channels equally).
* **Falsifier.** Already passed at the channel level. A single-channel emitter built on `curv_s2`
  alone must beat the 35-channel field at matched mass; if it does not, the channel's univariate
  edge is not exploitable in combination.

## H62-5 — Off-catalogue-novelty emission: suppress the catalogue's own 3-px neighbourhood before emitting

**Rank 5 — but it is the *cheapest* intervention in this document and it is an emission change,
not a geology change. Expected DTI gain: unknown sign, must be measured. Cost: minutes.**

* **Layers.** None. This is a statement about the scoring contract, not about geophysics.
* **The argument.** `FP_w` counts only mass that is *not* matched to the scored label set.
  If the scored label set is faults that the visible catalogue does **not** already contain — which
  is what the prizes are explicitly for ("re-scoring the same submission against expanded labels
  after expert review") — then **every unit of mass placed on a known catalogue fault is a pure
  false positive**: it contributes nothing to `TP_w` on the scored set and it costs `α = 0.2` in the
  denominator.
* **Measured evidence that this is not a small effect.** The group's best artifact places
  **70.9 % of its mass within 3 px of a catalogue fault** (39.4 % within 1 px, median distance
  2.00 px). If those pixels are not in the scored set, they are 31,255 units of pure `FP_w` at a
  budget of 44,090 — and `FP_w` is already 83 % of the metric's denominator budget.
* **Why it is ranked last.** Its value depends entirely on a fact we cannot verify from inside this
  repository: **what the scored label set actually is.** If the scored set is a held-out *subset of
  the catalogue*, suppressing the catalogue would destroy the score. The honest position is that
  this hypothesis is **untested and cannot be tested without an upload**, and it is recorded here
  rather than acted on.
* **Falsifier / decision rule.** This is exactly what the three-slot identification pack
  (`registry/identification_pack.json`, `docs/research/verification-2026-10-04.md` §9) measures:
  the recovered `T` and `K` from S1/S2/S3 tell us directly whether the scored set overlaps the
  catalogue. **Do not act on H62-5 until that pack has been run.**

---

## Ranking table

| # | hypothesis | layers | measured support | expected DTI gain | cost | new external data |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | **H62-4** detrended-elevation curvature | `det_elev` (12), `det_elev_slope` (19) | **`curv_s2` = 0.5871, best channel of 35**; +10.1 % transform gain — *the only transform gain that survives blocking* | **high** | very low | none |
| 2 | **H62-2** buried-basement step × gravity, quiescence-gated | `depth_to_base_surf` (15), `iso_grav_anom_hg` (18), `iso_grav_anom` (13) | transform gain +3.5 % on (15); unambiguous basement-offset physics | **high** | low–med | none |
| 3 | **H62-3** geodetic strain prior, used raw | `geod_2ndinv` (4), `geod_shearrate` (7), `geod_dilaterate` (8) | 0.5721 / 0.5488 / 0.5377; **raw beats transformed on every variant measured** | med–high | low | none |
| 4 | **H62-5** off-catalogue-novelty emission | — | 70.9 % of the incumbent's mass sits on the catalogue | unknown sign | minutes | none |
| ~~5~~ | ~~H62-1 tilt-angle zero-crossing~~ | `tc` (6) | **FALSIFIED — ties raw, 0/4 blocks** | — | paid | none |

**The re-ranking is the result of this round, and it was driven by a failure.** The hypothesis that
looked strongest from the band ranking (H62-1, built on the best official band) died on contact with
its own falsifier, while the one with the best *measured transform gain* (H62-4) survived. The
lesson generalises: **a layer's univariate discrimination says nothing about whether a transform of
it will help.** Only the transform test does that.

**All five need zero new external data.** That matters: the brief requires any hypothesis needing
external data to name a specific free official source *and* confirm obtainability first. **None of
these five does, so none of them can be blocked by an unobtainable dataset** — which is the failure
mode that killed H61-4 (GNSS full strain tensor: the source exists but its obtainability was never
confirmed from this environment) and H61-5 (1 m DEM link table: tiles never obtained).

---

## What must happen before any slot is spent

The standing rule is that no weekly slot is spent on an idea that has not beaten the current
holdout best. Applying it strictly to this document:

1. ~~**H62-1** must clear its binary falsifier.~~ **Run, and it failed** — 0 of 10 transform
   variants beat raw on all four blocks. **Closed. No slot will ever be requested for it.**
2. **H62-4** is already measured at channel level (`curv_s2` = 0.5871, best of 35). The remaining
   test is the emitter-level one, and it is the next thing to run.
3. **H62-2** and **H62-3** must clear the conjunction/prior tests on ≥3 of 4 blocked folds.
4. **H62-5** must wait for the identification pack. It is the only hypothesis here whose *sign* we
   cannot determine from the data we hold, and a wrong sign would be actively harmful.

Nothing in this document has been promoted, and **no slot is requested by this document.**

---

## Why this round is a success even though its top hypothesis died

The brief asks for hypotheses that are *falsifiable and falsified before they cost anything*. Three
things happened here that are worth more than a surviving hypothesis:

1. **The ranking changed because of a measurement, not an argument.** H62-1 was rank 1 on the
   strength of its band's univariate score (0.5735, best of 19). Its own transform test killed it.
   H62-4 was rank 4 and is now rank 1, because its transform is the only one in this study whose
   gain survives all four spatial blocks. **Univariate band ranking is not evidence that a
   transform of that band will help** — that is a new, measured, and transferable result.
2. **A general law came out of the negative results.** Transforms help *raw fields*
   (`det_elev` +10.1 %, `depth_to_base_surf` +3.5 %) and hurt *already-differentiated products*
   (`tc`, `geod_shearrate`, `geod_2ndinv`). The organisers' band 6 is literally described as "a
   magnetic field derivative for edge detection" — it is already the detector. **Differentiating a
   derivative amplifies noise, and we now have the numbers to say so.**
3. **The falsifier cost twelve seconds of CPU and zero submission slots.** That is the entire point
   of the standing rule: an idea dies on a blocked AUC before it ever touches the portal.
