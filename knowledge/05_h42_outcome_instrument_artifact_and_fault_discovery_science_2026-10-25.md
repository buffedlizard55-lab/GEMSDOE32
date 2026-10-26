# H42 outcome, the "gap-filling" instrument artefact, and what fault-discovery science says (2026-10-25)

*Reusable knowledge. Every number is labelled: **HOLDOUT-DTI** (evaluator, withheld positives, 95 % CI),
**INSTRUMENT** (an independent local proxy, labelled with its truth set), **ORGANIZER-CONFIRMED (owner-reported)**,
or **user-report**. Nothing here is a leaderboard projection. Machine-readable receipts:
`evidence/h42_run.json`, `evidence/h42_run_card.json`, `evidence/h42_sgmc_offcatalogue_check.json`.*

## 0. Bottom line

1. **No new file is cleared for a weekly slot.** The group's best remains
   `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` = **0.2778** (ORGANIZER-CONFIRMED, owner-reported; already
   submitted — do not resubmit).
2. **H42-1 (hanging-wall conditional intensity) is negative.** It beat the champion recipe on the
   catalogue-hidden holdout by a wide margin, but (a) it failed the parallel-run lane gate and (b) on an
   independent off-catalogue instrument it is **worse than random dots**. Its unique file is published as
   **DO NOT SUBMIT**.
3. **The previous README banner "✅ OK TO DOWNLOAD AND SUBMIT" (`h32-winning-46090-prune400`) is withdrawn.**
   It shares 37,298 exact dots with the champion (Jaccard 0.803; 84.0 % of its dots within 3 px of the
   champion's), its claimed holdout margin (0.14840 vs 0.14801) sat inside its own CI [0.115, 0.182], and on
   the independent instrument it is indistinguishable from the champion (Δ +0.0001 [−0.0010, +0.0013]).
4. **The most important finding is about the instrument, not the hypothesis**: catalogue-hidden
   hide-and-recover rewards *gap-filling between fragments of the catalogue's own traces*. A model can gain
   +45 % HOLDOUT-DTI over the champion recipe and still lose to random dots off-catalogue (§3).

## 1. Why `h33-2-b2` scored 0.2778 (re-verified from bytes and primary sources this session)

* **Construction (measured):** H19-5 (121,131 px) ⊃ d2.8 (44,090; raster-order thinning at 2.8 px) ⊃ solo
  (40,199 = d2.8 minus dots ≤ 1 px from the catalogue) ⊃ champion (37,654 = solo minus dots ≤ 2 px). Checked
  pixel-exactly in `evidence/h42_run.json → champion_construction` and the session log.
* **H19-5 itself** is an out-of-fold stacked fusion of four evidence lines — catalogue tip/step-over geometry,
  thermal/geochemical conduits (GDR 1391), 1 m / 10 m lidar openness + local-relief scarps, geopotential
  "worms" — with 1-px ridge NMS at a 2.45 % budget ([19GEMSDOE README](https://github.com/buffedlizard55-lab/19GEMSDOE)).
* **Metric algebra** ([official page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)):
  with binary dots, `DTI = T / (0.2·(T + F) + 0.8·|G|)`; adding one dot of realised kernel credit `k` raises
  DTI iff `k > 0.2·DTI` (0.0556 at 0.2778).
* **Why removing near-catalogue dots helped:** DrivenData staff confirmed that *pixels* of known faults are
  masked ([forum 11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)) —
  only the pixels, not a buffer. A dot 100–200 m from a mapped trace is therefore scored, and it pays full FP
  unless a *new* fault lies within 300 m of it. The live ladder 0.2600 → 0.2708 → 0.2778 (owner-reported)
  says such dots earned far below the bar: new faults are rarely within 200 m of mapped traces.
* **What it takes to go further:** at fixed mass and |G|, `T + F ≈ S` for thin dots, so DTI ∝ T. Reaching
  the 2026-10-25 public #1 (0.4413, [leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/))
  from 0.2778 needs ≈ +59 % credit per dot at the same mass — a better *detector*, not more subtraction.
  Further B-gating (B = 3) is a champion-family subset (lane duplicate) with an expected effect of a few
  thousandths either way (knowledge/03).

## 2. The H42-1 experiment (pre-registered: `knowledge/04_…md`, commit `86de6eb`)

**Hypothesis.** New faults (synthetic/antithetic splays, basinward-stepping piedmont scarps) concentrate on the
*down-thrown* side of mapped normal faults at 0.3–3 km. Side is signed topographically:
Δz = z̄(p) − z̄(nearest visible trace), z̄ = band-12 `det_elev` smoothed σ = 2 px. Model = leave-one-quadrant-out
HistGradientBoosting on evidence (19 cached channels + 11 lidar scarp bands) + relational features
(distance, cross/along-strike offsets, strike alignment, local density) computed from the *visible* catalogue
only, plus the three side features. Emission: one dot per 3 × 3 tile by E[k]
(`gems57.emit.emit_decimated`), B = 2 re-derived from the visible catalogue, per-fold budget = the champion
recipe's dot count.

**Instrument.** Shared template `vendor/gems57` (pinned [57GEMSDOE@822a0ce](https://github.com/buffedlizard55-lab/57GEMSDOE/tree/822a0ce5546c7b6749cdd82eb145b6b3e616603d)):
`holdout.buffered_component_draw` (whole 8-connected components, 20 % per label-blind quadrant, 3-px context
collar, all other catalogue pixels masked pixel-exactly), `evaluate_holdout.evaluate` + `pooled_summary`
(pooled TP/FP/FN, paired percentile bootstrap over 20 km blocks, 1000 draws).

**Leakage canary (G1):** worst single-feature AUC = `d_perp` 0.827 (limit 0.90) — passed.

**Per fold (HOLDOUT-DTI, gems57-pooled-hide-v2):**

| draw | fold | withheld px | dots/arm | HWCI | SYM | EVID | CHAMP_RECIPE |
|---|---|---|---|---|---|---|---|
| 20 | NE | 2,367 | 9,943 | 0.1645 | 0.1580 | 0.0450 | 0.1112 |
| 20 | NW | 1,923 | 8,681 | 0.1737 | 0.1593 | 0.0654 | 0.0883 |
| 20 | SE | 3,250 | 7,374 | 0.1211 | 0.1253 | 0.0507 | 0.1044 |
| 20 | SW | 3,781 | 10,495 | 0.1481 | 0.1474 | 0.0538 | 0.0829 |
| 21 | NE | 2,361 | 9,975 | 0.1564 | 0.1483 | 0.0690 | 0.1269 |
| 21 | NW | 1,918 | 8,699 | 0.1686 | 0.1704 | 0.0791 | 0.0934 |
| 21 | SE | 3,480 | 7,509 | 0.1646 | 0.1567 | 0.0966 | 0.1576 |
| 21 | SW | 3,813 | 10,504 | 0.1386 | 0.1294 | 0.0562 | 0.0841 |

**Pooled (HOLDOUT-DTI, gems57-pooled-hide-v2, 22,893 withheld positives, 95 % CI):**
HWCI **0.1529** [0.1400, 0.1674] · SYM 0.1479 [0.1349, 0.1612] · EVID 0.0638 [0.0540, 0.0743] ·
CHAMP_RECIPE 0.1056 [0.0936, 0.1166] (leak-advantaged: H19-5 was trained on the full catalogue).
Paired: HWCI − SYM **+0.0050 [+0.0006, +0.0099]** (G2 pass, narrow) · HWCI − CHAMP_RECIPE
**+0.0473 [+0.0338, +0.0610]** (G3 pass) · HWCI − EVID +0.0891 [+0.0772, +0.1019].

**Final raster** (refit on both draws; full catalogue as context): 37,654 dots, 0 on the catalogue, 0 within
2 px, median 5.83 px from the catalogue, 47.9 % on the topographically lower side, 42.1 % within 3 px of the
champion's dots. Template writer + `scripts/check_submission.py --strict-finite`: PASS (G5).
SHA-256 `c8e8d10dc55c3164c3f777a0f74764f408bb132e8b0a3e4ac5b5fa8fe914e515`.

**Lane gate (G4) — FAILED on the final dots.** Max Spearman vs 205 unique registry rasters = 0.127 (fine),
but 22 rasters have > 70 % of H42's dots within 3 px:

* 1 is the space-filling calibration lattice `13gems_20261001_r13-lattice-s5` (206,895 px, 4.0 % support,
  3-px footprint coverage 0.9987): random dots overlap it 0.9988 and the champion 0.9992 — it blocks *every*
  possible raster under the literal rule (irregularity IR-42-UNIQ-01 below);
* **21 are genuine**: e.g. GEMSDOE25 `gems25-h38-greedy-credit-k3p5` (54,472 dots): H42 overlap 0.819 vs a
  *band-matched* random null 0.573, an unconstrained random null 0.186 and the champion 0.386 — H42's
  near-network placement co-locates with GEMSDOE25's lane beyond what the distance band explains.

**Verdict: negative — DO NOT SUBMIT.**

## 3. The instrument artefact (why the holdout win is not evidence of live skill)

**Measurement (INSTRUMENT: SGMC off-catalogue = SGMC fault pixels > 3 px from the catalogue, 62,122 px;
catalogue masked; same template evaluator; neither model trained on SGMC):**

| raster | dots | INSTRUMENT DTI | live (owner-reported) |
|---|---|---|---|
| Anderson PINN (GEMSDOE36) | 38,854 | 0.0968 | 0.2750 |
| previous "OK" h32-winning-46090 | 46,090 | 0.0955 | unscored |
| **champion h33-2-b2** | 37,654 | **0.0954** [0.0841, 0.1066] | **0.2778** |
| solo h27-4 | 40,199 | 0.0953 | 0.2708 |
| d2.8 | 44,090 | 0.0942 | 0.2600 |
| random dots (same mass) | 37,654 | 0.0709 [0.0678, 0.0742] | — |
| **H42 final** | 37,654 | **0.0545** [0.0463, 0.0636] | — |

Paired: H42 − champion = −0.0409 [−0.0497, −0.0319]; H42 − random = −0.0164 [−0.0261, −0.0065].
The instrument orders the B-ladder correctly (d2.8 < solo < champion) but cannot resolve ±0.003 (it puts
Anderson above the champion, the reverse of the live order).

**Mechanism.** USGS/INGENIOUS traces rasterise into many small 8-connected fragments; withholding 20 % of
components mostly withholds *pieces of systems whose other pieces stay visible 3–10 px away*. A model given
"distance / offset to the nearest visible trace" learns to fill those gaps — and the instrument pays for it.
Genuinely new faults are, by construction, not pieces of mapped traces, and the live B-ladder says they are
rarely within 200 m of one. The skill does not transfer: H42's dots hug the network (median 580 m) and miss
off-catalogue faults more often than random dots do.

**Rule for every lane that uses catalogue-relational features** (proposed for the shared template, not
patched privately): pass an off-catalogue instrument as well as the catalogue-hidden one, and/or withhold
*detached* components only (the template's `holdout.build_holdout(mode="detached")` already implements a
≥ 4 px detachment rule) so that gap-filling earns nothing.

## 4. Fault-discovery science that matters for this metric (sources checked this session)

* **Where faults cluster in the Great Basin.** Faulds & Hinz catalogued ~250 geothermal fields: step-overs /
  relay ramps host ~32 %, normal-fault terminations ~25 %, fault intersections ~22 %, accommodation zones a
  smaller share ([WGC 2015 paper](https://pangea.stanford.edu/ERE/db/WGC/papers/WGC/2015/11100.pdf);
  [GDR 355 dataset](https://gdr.openei.org/submissions/355)); nearly 90 % of known systems sit in four
  settings ([Faulds et al. 2016, SGW](https://pangea.stanford.edu/ERE/pdf/IGAstandard/SGW/2016/Faulds1.pdf)).
  These are exactly the settings with many *short* strands — where unmapped faults are most likely — but the
  group has tested tip/step-over lobes repeatedly (H19 L1, GEMSDOE28/33) and they are already inside H19-5.
* **What counts as a new fault.** "Any fault pixel not already captured by USGS/INGENIOUS", including newly
  mapped geometry of an existing system ([forum 11536](https://community.drivendata.org/raw/11536)). The data
  sources and fault types behind the test set are deliberately undisclosed
  ([forum 11527](https://community.drivendata.org/raw/11527)).
* **The dominant non-fault mimic in this footprint.** Pluvial Lake Lahontan reached a highstand of ~1330 m
  ([USGS](https://www.usgs.gov/publications/lake-level-variation-lahontan-basin-past-50000-years)); the
  highstand shoreline is 1338.5 m in the Jessup embayment
  ([Adams & Wesnousky 1998, GSA Bull.](https://pubs.geoscienceworld.org/gsa/gsabulletin/article/110/10/1318/183306/shoreline-processes-and-the-age-of-the-lake))
  and varies from ~1340 m near the basin centre to ~1318 m at its northern edge from isostatic rebound and tilting
  ([Adams et al., summarised in this 2008 paper](https://www.researchgate.net/publication/247987548_Late_Pleistocene_and_Early_Holocene_lake-level_fluctuations_in_the_Lahontan_Basin_Nevada_Implications_for_the_distribution_of_archaeological_sites)). Wave-cut shorelines are level, scarp-like
  steps that any lidar scarp detector fires on. A contour-parallelism (isobath) filter needs *absolute*
  elevation, which is not in the provided bands (band 12 is detrended); 62GEMSDOE's Lahontan *datum-offset*
  lane ([PR #9](https://github.com/buffedlizard55-lab/62GEMSDOE/pull/9)) is related prior work (owner-reported
  0.0000; single transcription, not cross-checked).
* **Scoring rules that shape strategy** (DrivenData staff): public score is one pooled index over the public
  subset ([11550](https://community.drivendata.org/raw/11550)); same metric, no extra fault weighting, for
  public, private and Phase 2, whose labels can be added/removed/changed
  ([11556](https://community.drivendata.org/raw/11556)); the weekly cap is whatever the submission page
  shows ([11553](https://community.drivendata.org/raw/11553)).

## 5. Contrarian conclusions (grounded in the measurements above)

1. **More holdout-optimised network priors will look excellent locally and fail live.** The catalogue-hidden
   instrument is biased toward gap-filling; trust a relational lane only after an off-catalogue check.
2. **The near-network band (3–8 px from mapped traces) is saturated** by registry rasters (GEMSDOE25's
   greedy/sapd family): band-matched random dots already overlap them 57 %. New lanes must earn credit
   elsewhere to be unique.
3. **The leaders' 0.39–0.44 is unlikely to come from network priors.** The only lever with that much headroom
   is better *local* evidence — full-resolution (1 m) lidar scarp detection — which this sandbox cannot run
   (no GPU; USGS hosts unreachable), but which GitHub-hosted runners can reach (19GEMSDOE pulled 3DEP tiles
   that way).
4. **The hanging-wall side carries a small real signal on catalogue-hidden truth** (+0.0050 [+0.0006,
   +0.0099]); whether it holds for new faults is untested. Do not build on it without an off-catalogue gain.

## 6. Irregularities logged this session

| id | finding | action |
|---|---|---|
| IR-42-README-01 | README showed "✅ OK TO DOWNLOAD AND SUBMIT" for `h32-winning-46090-prune400` directly beneath a note saying no TIF was certified; the file is a champion-family variant (Jaccard 0.803) whose margin was inside its CI | banner withdrawn; status centralised in one top block |
| IR-42-UNIQ-01 | shared template's lane gate: the calibration lattice `13gems…r13-lattice-s5` (3-px coverage 0.9987) makes the literal 70 % rule fire for *every* raster (random 0.9988); `representation_class` classifies by support (> 20 %), not coverage | reported, template not patched privately; proposed fix: treat rasters with 3-px coverage > 0.70 as uninformative for the overlap test (keep them in the rank test) |
| IR-42-INSTR-01 | catalogue-hidden hide-and-recover rewards gap-filling; H42 +0.047 HOLDOUT-DTI vs −0.041 on SGMC off-catalogue and −0.016 vs random | relational lanes need an off-catalogue gate or detached-only hiding |
| IR-42-RUN-01 | `run_h42.py` applied the dot-overlap statistic to the continuous surface (every pixel a "dot") | declared deviation; corrected statistic reported as D3; verdict unaffected (decided on final dots) |
| IR-42-WRITER-01 | `src/gems32/submission.py::audit_geotiff` read but never compared the GeoTransform/CRS with the template | fixed (template comparison added when a template path is supplied) |

## 7. Next steps (highest expected value first)

1. **Off-catalogue-first detector with full-resolution lidar** — run on a GitHub-hosted runner (unrestricted
   network, 4 vCPU) to pull USGS 3DEP 1 m tiles, compute scarp likelihood at native resolution, aggregate to
   100 m, and validate on *both* the catalogue-hidden and the SGMC off-catalogue instruments.
2. **Detached-only hide-and-recover** as the default instrument for any relational feature.
3. **Absolute DEM (USGS 3DEP 1 arc-second, public domain) via the same runner** → H42-2 Lahontan isobath
   suppression as a precision filter on an off-catalogue-validated field.
4. Propose the IR-42-UNIQ-01 coverage rule to the 57GEMSDOE template owner.

## 8. Reproduce (clean checkout, CPU only, ~25 min)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/restore_data.py --group all --target-dir .cache/gems_data      # 23 files, SHA-256 verified
.venv/bin/python scripts/build_features.py --features .cache/gems_data/training_features.tif \
    --out .cache/gems_work/feature_stack.npy --receipt registry/feature_receipt.json      # ~3 min
.venv/bin/python scripts/fetch_focus_registry.py                                          # 222 registry rasters
.venv/bin/python scripts/run_h42.py        # folds, canary, LOQO arms, pooled bootstrap, final raster, gates, writer
.venv/bin/python scripts/h42_finalize.py   # diagnostics D1-D4 and the run card
```

The writer refuses to overwrite, and the file name carries a UTC stamp, so a re-run writes a new file rather than
replacing the published one. Library versions used are recorded in `evidence/h42_run.json → environment`.
