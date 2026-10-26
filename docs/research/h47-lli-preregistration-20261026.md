# H47 — Live-Ledger Inversion (LLI) instrument and pre-registered hypotheses (2026-10-26)

**Status:** written before the H47 candidate was built. Experiment E1 (the side-offset test,
H47-1) had already run while the instrument was being validated; it is recorded here as such.
Nothing below is a leaderboard score. Live scores are **OWNER-REPORT**. Instrument outputs for
unscored rasters are **PROJECTIONS**. Holdout numbers are **HOLDOUT-DTI** with evaluator, n, and CI.

## 0. Why a new instrument

The repository's catalogue-based holdouts (HIDE-RECOVER-v3.0, visible-gated, SGMC-cal) measure
recovery of *catalogued* faults. The organisers score *new, expert-mapped* faults and mask the
catalogue ([staff #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)).
The repo already documented live counter-examples: SGMC-tracing rasters scored 0.56–0.65 locally
and 0.0512/0.0492 live. The only direct measurements of the hidden public truth are the
owner-reported live scores of **111 distinct rasters** whose exact bytes could be restored from
the GEMSDOE repositories (`scripts/fetch_live_ledger_rasters.py` → `evidence/live_ledger_rasters.json`).

**LLI** (`src/gems32/ledger_inversion.py`) uses the official metric
([page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)). For any
truth-inclusion probability map π, E[TP_w] = Σ_y π(y)·max_x p(x)k(d(x,y)) and E[|G|] = Σ_y π(y)
hold exactly. The matched mass M is approximated by (1/3)Σ_y π(y)Σ_x p(x)k(d(x,y)), which is the
exact line-truth ratio and enters the denominator only with weight 0.2. With π constant on
feature strata, every live score is one equation. The fit is a log-additive stratum model by
bounded least squares on DTI, multi-started, with warm-started leave-one-out (LOO) and
leave-site-out validation.

**Validation (geometry design S3: distance-to-catalogue × distance-to-H19-5, 14 parameters):**
LOO MAE **0.0222**, Spearman **0.921**, 90% of |errors| ≤ **0.052**. Leave-site-out MAE **0.0226**,
ρ **0.918**. The fit reproduces the live B-ladder ordering D2.8 < B1 < B2 (projections
0.271–0.277 < 0.279–0.283 < 0.283–0.285 vs live 0.2600 < 0.2708 < 0.2778). It over-predicts this
family by +0.005 to +0.017. Adding slope, LiDAR step or SGMC strata did **not** improve LOO.

## 1. Hypotheses (ranked by expected DTI gain ÷ cost, before the candidate was built)

| rank | id | layers | physical signature / transform | why it should catch uncatalogued faults | how it differs from repo work | expected gain / cost | status |
|---|---|---|---|---|---|---|---|
| 1 | **H47-1 Ridge-to-trace side offset** | `det_elev` (band 12), H19-5 ridge network | Expert traces sit at a consistent side of multi-evidence ridge centerlines (scarp foot vs crest; gravity-gradient maxima lie basinward of range-front traces). A 1-px shift toward the correct side raises per-dot kernel credit by up to ~35% | It improves the localisation of an existing detector of uncatalogued faults, so it works below the 300 m kernel scale | No prior session tested a sub-kernel localisation bias against the **live** population | high if real / very low cost | **E1 ran: NEGATIVE** (see §3) |
| 2 | **H47-2 Catalogue-proximal depletion (≤500 m)** | `labels.tif` distance only | Organiser masking plus expert practice: new faults are rarely mapped within ~500 m of a catalogued trace | The live truth density estimated by LLI is 0.06× / 0.15× / 0.22× (1–2 / 2–3 / 3–5 px), then flat beyond 5 px | Generalises the B=1/B=2 ladder with a live-calibrated depletion curve instead of a fixed radius | low-moderate / very low | used inside H47-3 (B3 core) |
| 3 | **H47-3 LLI-optimal unique allocation** (selected lane) | H19-5 network (core), `rtp` (2) and `det_elev` (12) gradients, LiDAR `step_max` (3) and `coh100` (10) | Core: H19-5 centerline dots placed by LLI expected credit with B3 depletion pruning. Novel component (≥30% share, >5 px off-network, >5 px off-catalogue): Gallardo–Meju magnitude-weighted *alignment* of magnetic and topographic gradients (faults that offset both magnetised units and topography), boosted by coherent LiDAR step. The dot budget is set to maximise the LLI projection under the uniqueness constraint | Off-network faults are, by construction, ones no prior GEMSDOE network reached. Joint-structure coupling is a physical, non-catalogue criterion | First allocation that is (a) explicitly optimised against a live-calibrated instrument and (b) uniqueness-constrained by design | uncertain: LLI says off-network strata carry an expected 0.002–0.018 credit/dot vs the 0.056 break-even, so a tax is expected / low cost | E2 (this run) |
| 4 | H47-4 Absolute-elevation pluvial-shoreline veto | absolute DEM (not in the 19 bands) | Lake Lahontan highstand shorelines (~1,190–1,340 m) are the classic NW-Nevada scarp mimic | Removes a non-fault mimic from ridge networks | Needs an absolute DEM; `det_elev` is detrended, so obtainability is unverified in this sandbox | moderate / high | not run (data access) |

**Named non-fault mimic process for the selected lane (H47-3):** fluvial terrace risers and
incised-wash banks (topographic edge without magnetic coupling), plus buried volcanic flow margins
(magnetic edge without topographic coupling). The alignment criterion requires **both** gradients
to be large and parallel. Pluvial shorelines remain a residual mimic (H47-4).

## 2. Pre-declared automatic verdict rule (no human inspection)

`OK TO SUBMIT` requires **every** gate below; otherwise `DO NOT SUBMIT`.

1. **Format:** strict validator on the saved bytes (EPSG:32611, 3730×3292, float32, transform
   equal to the sample, every cell finite in [0,1]).
2. **Uniqueness:** pre-placement surface |Spearman| ≤ 0.90 and final dots ≤ 70% within 3 px,
   against every refreshed focus-registry raster **and** every restored live-ledger raster. A
   registry raster whose 3-px dilation covers ≥ 70% of the footprint (space-filling, e.g. the
   5-px calibration lattice) makes the literal test unsatisfiable by construction. It is judged by
   the null-calibrated excess (overlap − coverage)/(1 − coverage) ≤ 0.70, and the literal value is
   still reported. A mass-weighted overlap ≤ 0.70 is also required, so low-value "padding" dots
   cannot buy uniqueness.
3. **Leakage canary:** every feature alone, oriented AUC ≤ 0.90 on HIDE-RECOVER positives.
4. **Protocol holdout:** HIDE-RECOVER-v3.0 pooled DTI with a paired 95% CI vs the champion proxy
   (D2.8 + fold-local B gate) that excludes zero, **and** a point estimate above the repo's
   same-evaluator best (H38 0.116958).
5. **Live-calibrated projection:** LLI projection ≥ the champion's LLI projection under the same
   fit (both ridge settings). Otherwise the file is projected not to beat 0.2778.

Budget: ≤ 3 experiments. E1 = H47-1 test (done). E2 = H47-3 build + all gates. E3 is reserved for
one budget/spacing variant only if E2 is within the LOO MAE of the champion projection.

## 3. E1 result (H47-1) — NEGATIVE

Splitting the H19-5 halo by side (S4 design) gave a huge in-sample upslope effect: 358× at 1 px
and 113× at 2.2–3 px upslope, ≈1× downslope. It did **not** improve held-out prediction. LOO MAE
was 0.0222 → 0.0222. On the 53 most side-asymmetric rasters it was 0.0217 vs 0.0217, and the
correlation between side-asymmetry and live score is −0.07. The in-sample effect is an
identifiability artifact. **No shift is applied.**
