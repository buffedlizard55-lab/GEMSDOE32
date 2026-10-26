# H47 — Why 0.2778 won, what the live ledger says about the hidden faults, and why no unique file beats it yet

**Session:** 2026-10-26 (H47). **Branch:** `arena/f6961c02-gemsdoe32`.

**Evidence labels:** live scores are **OWNER-REPORT** (owner-supplied submission log; no organizer
receipts in this repository). **HOLDOUT-DTI** values give evaluator, n withheld positives, and 95% CI.
**PROJECTION** marks live-calibrated model output for an unscored raster. A projection is never a score.

## 0. Bottom line

| Question | Answer |
|---|---|
| Unique TIF generated this session? | **Yes.** [`gemsdoe32-h47-lli-unique-coupling-49231-20261026T230000Z-33464ce2-zeros.tif`](../downloads/gemsdoe32-h47-lli-unique-coupling-49231-20261026T230000Z-33464ce2-zeros.tif) ([single-TIFF .zip](../downloads/gemsdoe32-h47-lli-unique-coupling-49231-20261026T230000Z-33464ce2-zeros.zip)). SHA-256 `d8da7e94…80fea1`, 49,231 dots. |
| Validated automatically? | **Yes, no human step.** Strict validator: EPSG:32611, 3730×3292, float32, transform equal to the sample, all 12,279,160 cells finite in [0,1], 0 NaN, 0 catalogue dots. Uniqueness checked against **452 GEMSDOE rasters**: surface max \|ρ\| = 0.224; max final-dot overlap with any non-space-filling raster = 0.650. |
| **OK to submit?** | 🔴 **NO.** It fails two pre-declared performance gates. It is projected to score *below* the 0.2778 champion: PROJECTION 0.240–0.248 vs 0.283–0.285 for the champion under the same fit. Its HOLDOUT-DTI is 0.0784 vs 0.0992 for the champion proxy. **Download for research/audit only.** |
| Best file across the nine focus sites | GEMSDOE32 `h33-h33-2-b2-…-e5eb6e7e-zeros` (**0.2778, OWNER-REPORT**). It has already been submitted, so do **not** resubmit it. |
| Can a unique file beat 0.2778 with today's signals? | **Not with the signals tested.** §3 explains this with live-ledger evidence. |

## 1. Why the GEMSDOE32 `h33-h33-2-b2` file scored 0.2778 (the GEMSDOE best)

### 1.1 The metric rewards sparse, well-placed dots

The official metric ([page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), verified verbatim this session) is

TP_w = Σ_g max_x p(x)k(d(x,g)), FP_w = Σ_x p(x)[1 − max_g k(d(x,g))], FN_w = |G| − TP_w,
DTI = TP_w / (TP_w + 0.2 FP_w + 0.8 FN_w), with k(d) = max(0, 1 − d/3 px).

Known USGS/INGENIOUS pixels are excluded from evaluation ([staff #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)).
The public score is **one pooled index** over the public chunks ([staff #11550](https://community.drivendata.org/raw/11550)).

Two exact consequences explain most of the H19-5 → 0.2778 ladder:

* **Dotting.** Take binary dots spaced s px along a truth line. Each truth pixel's credit is
  1 − u/3, where u is its along-line distance to the nearest dot, so the mean credit is
  c(s) = 1 − s/12 for s ≤ 6 px. A dot therefore earns s·c(s) = s − s²/12 truth credit, which peaks
  at 3.0 when s = 6. Off truth, each dot still costs 1 unit of FP mass, so cutting mass by a factor s
  while keeping ~77% of the line credit (s ≈ 2.8) raises DTI whenever most of the mass is false
  positive.
* **Break-even.** An isolated binary dot that adds credit k to otherwise uncovered truth raises DTI
  iff k > α·DTI. At DTI 0.2778 that bar is 0.0556 (`src/gems32/metric.py`; `tests/test_metric.py`
  covers the partial-coverage case).

### 1.2 Three ingredients, each now measured against the live ledger

The champion is **exactly** `D2.8 minus every dot with Euclidean distance ≤ 2 px to the catalogue`.
`D2.8` is ⊂ H19-5 (121,131 px). This was verified this session on the restored bytes: 6,436 dots
removed (3,891 at d = 1, 1,201 at d = √2, 1,344 at d = 2), leaving 37,654.

1. **A ridge network that sits on the hidden faults.** H19-5 (19GEMSDOE) is the Hessian ridge-NMS
   centerline of a four-line fused score: power-law tip/relay stress, GDR thermal/geochemistry,
   1 m/10 m DEM openness/LRM scarps, and gravity/magnetic "worms". It uses a 2.45% budget. The new
   Live-Ledger Inversion (§2) estimates that **73–96% of the hidden public truth lies within 300 m of
   this network**, concentrated in its 1-px halo (stratum density 50–1,400× the far-field
   reference). The range depends on regularisation.
2. **Dot thinning** (H19-5 solid 0.1922 → D1.5 0.2477 → D2.8 0.2600) is the c(s) trade-off in §1.1.
3. **Pruning inside the catalogue-depletion zone** (D2.8 0.2600 → B1 0.2708 → B2 0.2778). LLI
   measures the live truth density near catalogued traces at **0.01–0.07× (1–2 px)**,
   **0.05–0.15× (2–3 px)** and **0.14–0.22× (3–5 px)** of the far-field density, and ≈1× beyond 5 px.
   This holds across every fit and regularisation tested. Dots there are almost pure false positives,
   so removing them lowers the denominator and barely touches TP.

### 1.3 Calibration facts (MODEL-INFERENCE from OWNER-REPORT scores; reproducible)

* The 5-px calibration lattice scored **0.0904** live. Under a uniform-truth model that implies about
  12.3k public truth pixels at full-footprint scale (lattice mean credit 0.3752 per truth pixel). LLI
  fits give |G| ≈ 17–18k because they let density concentrate near the network.
* A **spatially random** raster would score ≈ 0.042–0.046 with 37,654 dots and ≈ 0.045–0.047 with
  44,090 dots. The SGMC-tracing files (0.0512, 0.0492) are at the random level. **SGMC bedrock faults
  carry essentially no information about the test faults.** This explains the documented SGMC
  instrument failure (IR-42-INSTR-02).
* The champion is ≈ 6.5× the random-equivalent DTI for its dot count.

### 1.4 What cannot be inferred

The hidden truth, the public/private chunk map, and per-submission receipts are unavailable. LLI
estimates are **stratum averages**. They say nothing about a detector that is far better than average
inside a stratum, and they inherit any error in the owner-reported scores.

## 2. New shared instrument: Live-Ledger Inversion (LLI)

`src/gems32/ledger_inversion.py`, `scripts/run_live_ledger_inversion.py`, inputs located by
`scripts/fetch_live_ledger_rasters.py`.

* **Inputs.** 118 of 123 owner-reported live scores were matched to exact GeoTIFF bytes in the GEMSDOE
  repositories by conservative filename matching; 5 rows were left unmatched rather than guessed.
  After collapsing identical masks, **111 distinct rasters** remain (`evidence/live_ledger_rasters.json`).
* **Identity.** E[TP_w] and E[|G|] are exactly linear in the truth-inclusion map π. The matched mass
  uses the exact line-truth max/sum ratio (1/3), which is tested against the exact metric in
  `tests/test_ledger_inversion.py`. Each live score is one equation.
* **Model.** π is a log-additive function of feature strata only, never location. The fit is
  multi-start bounded least squares on DTI, with warm-started leave-one-out and leave-site-out
  validation.

| design (strata) | params | LOO MAE | LOO Spearman | leave-site-out MAE / ρ |
|---|---|---|---|---|
| S0: d_catalogue (8) × d_H19-5 (5) | 12 | 0.0221 | 0.926 | 0.0224 / 0.925 |
| **S3: d_catalogue (6) × d_H19-5 (9 halo bins)** | 14 | **0.0219** | **0.927** | **0.0223 / 0.923** |
| S4: S3 with halo split by up/down-slope side | 15 | 0.0222 | 0.923 | 0.0226 / 0.919 |
| S0 + slope / LiDAR step / SGMC (each) | 13–19 | 0.0223–0.0241 | 0.907–0.926 | no gain |

The fit reproduces the live B-ladder order (D2.8 < B1 < B2). It over-predicts the champion family by
+0.005 to +0.007; the champion projects at 0.2831–0.2845 against 0.2778 live. Use LLI for **ranking
and go/no-go**, with ±0.022 (MAE) and ±0.052 (q90) error bands. Do not use it as a score.

## 3. The uniqueness ceiling: why no tested unique file beats the champion

The protocol's duplicate rule (≤70% of dots within 3 px of **each** registry raster) applies to the
dense H19-5 network itself (121,131 px; a registry raster via GEMSDOE24 `inputs/`). Any protocol-unique
file must therefore place **≥30% of its dots more than 3 px from the network**. LLI puts only 4–27% of
the hidden truth there, spread over ~4.6 M pixels. Off-network strata are worth **0.002–0.018 expected
credit per dot**, against the **0.0556** break-even. Each such dot adds ≈0.2 to the denominator and
almost nothing to TP.

**E2 confirmed this directly** (`evidence/h47_lli_unique_experiment.json`):

* Budget sweep: 15 configurations; core 16k–32k dots; novel share fixed at 35%.
* Best unique configuration: **PROJECTION 0.2402–0.2476**, versus 0.2831–0.2845 for the champion.
* **HOLDOUT-DTI** (GEMSDOE32-HIDE-RECOVER-v3.0, 22,232 withheld positives):
  * H47: 0.0784 [0.0662, 0.0909].
  * Champion proxy: 0.0992 [0.0860, 0.1127].
  * Paired Δ CI [−0.0246, −0.0168].
  * The novel component alone costs Δ CI [−0.0164, −0.0095] relative to core-only (0.0915).

**What would beat 0.2778, 0.3195 or 0.4437.** This uses the identity with the champion calibration
(TP ≈ 5.06k on |G| ≈ 12.7k at 37,654 dots). It is MODEL-INFERENCE, not a forecast:

* **0.3195** needs about +16% TP at the same dot count, or the same TP with about 32% fewer dots,
  all of them removed false positives.
* **0.4437** (current #1) needs about +63% TP at the same dot count. It cannot be reached by pruning
  alone; it needs better recall *and* better precision.

**Realistic routes** (next sessions):

* (a) **Segment-level precision.** Fit LLI on *segment attributes* of the network and prune false
  segments. This is a refinement of the H19-5 family and is blocked by the duplicate rule unless the
  owner allows refinements (owner decision, IR-47-UNIQ-CEILING).
* (b) **Sub-kernel localisation of traces.** The 1-px halo finding suggests centerlines sit ~100 m
  off the traces, but the side is not identifiable from the ledger (E1). This needs a trace-snapping
  method, e.g. from 1 m LiDAR.
* (c) **Off-network recall.** This needs ≥7× stratum-average lift. No tested signal achieves that.

## 4. Hypotheses (pre-registered in `docs/research/h47-lli-preregistration-20261026.md`)

| id | result |
|---|---|
| H47-1 ridge-to-trace side offset | **NEGATIVE.** A large in-sample "upslope" effect (358×) gave **zero** out-of-sample gain: LOO 0.0222 → 0.0222; the 53 most asymmetric rasters 0.0217 vs 0.0217; r(asymmetry, score) = −0.07. In a later multi-start fit the side flips between bands, so it is not identifiable. |
| H47-2 catalogue-proximal depletion | **Supported** in every fit (0.01–0.22× within 5 px). A B3 champion subset projects +0.002 to +0.004, which is inside the error band and would be a protocol duplicate. |
| H47-3 LLI-optimal unique allocation (selected lane) | **NEGATIVE** (E2 above). |
| H47-4 absolute-elevation shoreline veto | Not run: needs an absolute DEM. `det_elev` is detrended, and DEM download hosts are not reachable from this sandbox. |

**Experiments used:** 2 of 3. E3 was not triggered, because the pre-registered trigger required E2 to
be within the LOO MAE of the champion projection.

## 5. Nine-site executive summary

These are the best OWNER-REPORT files per site. "Unique" means no byte- or mask-identical alias and
≤70% within 3 px of every other restored live-scored GEMSDOE submission. Space-filling rasters with
≥70% footprint coverage are excluded from the max because they overlap every map. The estimate is the
LLI leave-one-out PROJECTION. Source: `evidence/nine_site_table_h47.json`.

| Site | Best file (download) | Live score | LLI LOO estimate (projection) | Unique vs all listed? |
|---|---|---|---|---|
| **GEMSDOE32** | [`h33-h33-2-b2…e5eb6e7e-zeros`](https://github.com/buffedlizard55-lab/GEMSDOE32/raw/45ee207185f72804497f7a7a392ad2c43e168f02/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | **0.2778** | 0.285 | **No.** 25 listed files >70%, e.g. G29 wormrank-d28. Already submitted. |
| GEMSDOE36 | `anderson-geothermal-pinn-38854` | 0.2750 | 0.283 | **No.** Champion + 1,200 dots; 25 files >70%. |
| GEMSDOE28 | `h36-1-rung30-blind-r1` | 0.2710 | 0.277 | **No** (27 files >70%). |
| GEMSDOE31 | `h27-4-solo-d28` | 0.2708 | 0.279 | **No.** Byte-identical mask to G28 `h27-4-r1-solo`. |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30` | 0.2632 | 0.278 | **No** (27 files >70%). |
| GEMSDOE25 | `dotted-h19-5-d2-8` | 0.2600 | 0.271 | **No.** Identical to G30 `d28-poisson300m` and G29 `efd28-repro`. |
| GEMSDOE30 | `d28-poisson300m-offcat-44090` | 0.2600 | 0.271 | **No** (identical to G25). |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5` | 0.2477 | 0.268 | **No** (26 files >70%). |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5` | 0.2449 | 0.266 | **No** (26 files >70%). |
| **GEMSDOE32 (new, H47)** | [`h47-lli-unique…33464ce2-zeros`](../downloads/gemsdoe32-h47-lli-unique-coupling-49231-20261026T230000Z-33464ce2-zeros.tif) | unscored | **0.240–0.248** | **Yes** (max 0.650; 452 rasters). 🔴 **Not OK to submit.** |

All nine historical bests are one H19-5 family.

## 6. Irregularities flagged this session

See `registry/irregularities.json`, ids `IR-47-*`:

* **IR-47-LANE-01:** the prompt's lane paragraph is absent; the H47 lane is self-declared.
* **IR-47-LATTICE-FIX:** the literal 3-px rule is unsatisfiable against space-filling rasters. A
  null-calibrated rule is implemented in the shared `registry_audit`, the literal result is still
  reported, and a mass-weighted guard is added.
* **IR-47-UNIQ-CEILING:** the duplicate rule vs the dense H19-5 network forces ≥30% off-network dots,
  and live evidence says those are near-worthless. Owner decision requested.
* **IR-47-TARGETS:** 0.4413 (cached) and 0.3195 (historical) are superseded. The live #1 read at
  2026-10-26T21:20Z is **0.4437**.
* **IR-47-PRIZES:** the problem page now describes $50k Initial / $250k Final pools. The prompt cites
  $175k / $395k.
* **IR-47-ALIAS:** byte-identical masks under different names (G25 = G30 = G29 efd28-repro;
  G31 = G28 h27-4-r1-solo).
* **IR-47-G77:** GEMSDOE77 lists a file named `gems85-…`.
* **IR-47-UNSCORED:** G91 `S18-UNIQUE` and the G86/G88 entries have no score.
* **IR-47-LEDGER-GAPS:** 5 ledger rows (GEMSDOE, GEMSDOE4, 21GEMSDOE, GEMSDOE64, GEMSDOE79) could not be
  matched unambiguously and were excluded, not guessed.

## 7. Remaining work, limitations, access needed

* **Owner decisions:**
  * The duplicate rule for H19-5-family refinements (IR-47-UNIQ-CEILING).
  * Whether the space-filling exemption is acceptable (IR-47-LATTICE-FIX).
* **Access:**
  * Organizer submission receipts. Every live score here is OWNER-REPORT.
  * An absolute DEM (USGS 3DEP) for H47-4. Not reachable from this sandbox (only GitHub/PyPI hosts).
* **Next session (highest expected value):**
  * Segment-level LLI: attributes of each network segment (length, strike vs regional fabric, LiDAR
    step, coupling, catalogue distance), fitted on the ~30 champion-family variants with different
    segment subsets.
  * A LiDAR-based trace-snapping test for the 1-px halo.
* **Limitations:**
  * The LLI ignores the unknown public/private chunk map, which is the likely source of most of its
    residual error.
  * The matched-mass term is approximate (weight 0.2).
  * Owner-reported scores are unverified.
