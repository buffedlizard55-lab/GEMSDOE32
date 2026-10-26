# Arena51 — Live-score covariate audit and nine-site executive decision (2026-10-26)

**Session:** Arena `arena/b4675e19-gemsdoe32` · **Date:** 2026-10-26 (evening UTC)
**Kind:** retrospective portfolio audit. **No new experiment lane was assigned in this session's
prompt, no holdout experiments were run, no candidate GeoTIFF was generated, and no weekly
submission slot was used.** The deliverables are (i) the repair of two shared-template defects
that had left `main`'s test suite red (IR-49-SYNC-01/02, fixed and regression-tested; the same script then reconciled the stale ARENA47 latest_candidate left in the release review by the H50 merge), (ii) a new
auditable instrument that quantifies what co-varies with the owner-reported leaderboard scores
across the whole locally pinned portfolio, and (iii) this executive decision summary.

**Evidence classes used below** (unchanged rules):
- **OWNER-REPORT** — a score the owner transcribed from a DrivenData submission screen. No
  organizer receipt in this repository binds any of these numbers to the exact raster bytes
  (IR-32-SCORE-01). There is still no ORGANIZER-CONFIRMED score for any of our files.
- **HOLDOUT-DTI** — a local evaluator result with evaluator version, withheld-positive count and
  95% CI. Never a leaderboard prediction.
- **PUBLIC-LEADERBOARD** — rows read directly from the official DrivenData leaderboard page.
  Re-read during this session (2026-10-26): `xiaofanhu` 0.4437 #1, `cfld__` 0.3916 #2,
  `Batik Shirt Brothers` 0.3904 #3 — the same top-3 order and scores as the 2026-10-26T04:32:28Z
  read preserved in `evidence/live_leaderboard_snapshot_20261026.json`.

Machine receipt for every number in this document:
[`evidence/livescore_covariates_20261026.json`](../../evidence/livescore_covariates_20261026.json)
· instrument code: [`src/gems32/livescore.py`](../../src/gems32/livescore.py) +
[`scripts/run_livescore_analysis.py`](../../scripts/run_livescore_analysis.py) ·
extra scored rasters pinned at [`registry/extra_scored_manifest.json`](../../registry/extra_scored_manifest.json).

---

## 1. Executive decision (the answer first)

**Is any file in this repository OK to download and submit to the competition right now? NO.**

1. **Nothing new is authorized.** `registry/current_status.json` keeps
   `any_file_ok_to_submit = false`. The newest research artifact is now **ARENA49-PCG** (a
   phase-congruency skeleton, merged to `main` by a parallel session while this one was in
   flight): it is the first genuine-unique candidate to beat the champion on **both** recorded
   instruments — visible-gated HOLDOUT-DTI `0.02826` vs the champion's same-evaluator
   `0.00452` (paired Δ `+0.0236 [+0.0178, +0.0294]`) and SGMC-cal `0.07033` vs `0.06412` —
   and its run card records gate-level `promote` **with `selector_required: true` and an
   overall `negative` verdict**, i.e. held for the weekly-slot selector, not authorized. Two
   cautions apply before treating it as the answer: (a) its run-card registry-comparison block
   is **empty**, and at 37,654 dots the literal lattice rule is mathematically impassable
   (§2.3), so its `final=true` gate necessarily excluded the lattice — precisely the exemption
   IR-51-LATTICE-01 reserves for an explicit owner decision; (b) every previous non-family
   "instrument winner" in this portfolio scored ≤ `0.2478` live (OWNER-REPORT), so a live gain
   over `0.2778` is possible but not supported by precedent. The prior artifacts (H50 TM-SPI:
   SGMC-cal 0.0164 < 0.0641; H47's LLI projection for its own unique candidate 0.240–0.248 vs
   the champion's 0.283–0.285) all carry recorded negative verdicts, as do ARENA47, H46, H44,
   Arena9, Arena8a, H38 …. This audit is complementary to H47's LLI: LLI models hidden-truth
   density strata from 111 rasters and produces PROJECTIONS; Arena51 fits intrinsic raster
   covariates and quantifies the family ceiling, the champion's above-trend residual, and the
   exact lattice bound below.
2. **The best historical file is already scored.** `h33-h33-2-b2` (0.2778 OWNER-REPORT) was
   already submitted. Resubmitting it spends one of the 3-per-week slots and adds no information.
3. **All nine focus-site "winners" are one family, byte-verified.** The nine best historical
   masks have a minimum pairwise directed 3-px overlap of 86.7% (existing audit
   `evidence/focus_site_winner_overlap_20261026.json`), and this session's mask-digest audit
   proves several are *literally the same raster*: GEMSDOE25 `dotted-h19-5-d2-8` ≡ GEMSDOE30
   `d28-poisson300m-offcat` ≡ GEMSDOE29 `efd28-repro` (one 44,090-dot mask, digest
   `426073b6…`); GEMSDOE28 `h27-4-r1-solo-d2-8` ≡ GEMSDOE31 `h27-4-solo-d28` (one 40,199-dot
   mask, digest `dbb80910…`); GEMSDOE ≡ 5GEMSDOE ≡ 8GEMSDOE `Hedge-v2/ens12` (one 172,974-dot
   mask). None of the nine is "unique" against the others.
4. **A blocking owner decision is quantified exactly.** The literal novelty rule ("stop if >70%
   of your dots fall within 3 px of any registry raster's dots", applied without exemption to
   the 5-px calibration lattice `r13-lattice-s5`) is **mathematically impassable for any
   submission with more than 22,163 dots** (exact computation below). Every champion-family file
   (37,654–61,328 dots) fails by construction, as does the champion itself (99.92%). Until the
   owner decides between (a) exempting documented calibration probes or (b) keeping the literal
   rule (in which case no dense map can ever pass), **no new dense candidate can be cleared,
   regardless of its science.** This is IR-49-LATTICE-01; it sharpens IR-42-UNIQ-01/IR-45-LATTICE-02
   from an observation to an exact bound.

**Why no new TIFF was generated this session:** the parallel-run protocol requires an assigned
single-method lane (absent from this session's prompt, as in the H46 session), and even a
perfect-science raster would be auto-blocked by item 4 above. Generating another near-duplicate
research artifact would spend budget without creating any path to submission. The highest-value
work — and what this session delivered — is the repaired fail-closed pipeline, the exact
lattice bound the owner needs for the protocol decision, and the quantified portfolio analysis
that says where a real gain could come from.

---

## 2. What the new instrument measured (H48-A, pre-registered before running)

**Hypothesis H48-A (fixed before execution):** owner-reported live DTI across the portfolio is
explained principally by (i) membership of the H19-5 thinning family, (ii) emitted-dot count
within that family, and (iii) catalogue-proximity/packing covariates — not by any local
holdout instrument (the 12-artifact calibration already showed the best local instrument reaches
only ρ = +0.53, p ≈ 0.09).

**Method (deterministic, auditable):** every row of `docs/score-ledger.csv` with a parseable
score was joined to locally pinned raster bytes (focus registry 354 rasters, data-manifest scored
mirrors, this repo's `docs/downloads`, and 38 newly fetched and SHA-pinned rasters from 24 other
owner repositories) under strict matching rules (exact normalized name → containment with a
12-character minimum → strong hash tokens; calendar-date tokens excluded). Identical dot masks
were collapsed by mask digest. All 54 joins were then audited row by row; two join hazards found
during the audit (generic `submission.tif` stems; a version token `6452ae1d00` shared by two
different GEMSDOE10 submissions) were fixed in the matcher **before** any statistic was trusted,
and regression tests now cover both. No organizer source was contacted; no external
(non-owner) data entered the analysis.

**Join outcome (final run, on the merged `main` state):** 145 ledger rows → 22 excluded (18
other-team leaderboard rows, 4 non-parseable/UNSCORED) → **59 joined → 53 unique scored masks**
(0 conflicting scores for one mask, 0 read errors). 59 rows had no local raster (mostly scores
< 0.10; the fetch threshold was 0.10). Five rows joined mid-session because the owner's
2026-10-26 ledger additions (GEMSDOE24 0.0859, GEMSDOE25 0.0742, GEMSDOE27 **0.2190**, GEMSDOE28
0.0217, GEMSDOE30 0.1462 — all OWNER-REPORT) reached already-pinned bytes; each of those five
joins is an exact same-site normalized match and was audited like the rest. Fitted set spans
0.0107–0.2778. The first run of this session (before the merge) had 54 joins / 48 masks; every
statistic below is from the final 53-mask run, and the headline conclusions are unchanged.

### 2.1 Results

| statistic (OWNER-REPORT-fitted; n = 53 unique masks) | value |
|---|---|
| Spearman ρ, score vs `frac_within3_h195` (family membership) | **+0.844** (p = 2.2e-15) |
| Spearman ρ, score vs `frac_within3_champion` | **+0.865** (p = 6.9e-17) |
| Spearman ρ, score vs `log10_dots` (all) | −0.278 (p = 4.4e-02) |
| Spearman ρ, score vs `frac_on_catalogue` | −0.245 (p = 7.7e-02) |
| Spearman ρ, score vs `median_dist_catalogue_px` | +0.311 (p = 2.3e-02) |
| LOO linear regression, 5 covariates, all 53 masks | **R² = 0.720, ρ = 0.861, MAE = 0.0256** |
| LOO linear regression, dot count only, family subset (n = 17) | **R² = 0.881, ρ = 0.765, MAE = 0.0072** |
| Family (≥80% of dots within 3 px of H19-5) | n = 17, median 0.2560, **max 0.2778** |
| Non-family detectors | n = 36 (33 site repositories), median 0.1444, **max 0.2478** (`gems70-p5-dual-submod300-oof38k`) |
| Champion leave-one-out on the family's own dot-count trend | actual 0.2778 vs predicted 0.2677 → **residual +0.0101** |
| Full-fit standardized β (dominant covariate) | `frac_within3_h195` **+0.94**; `mean_self_kernel` −0.43 |

Reading (with the caveats in §2.2): the portfolio's owner-reported scores are dominated by
family membership. Within the family, dot count alone reproduces the score ladder to
MAE ≈ 0.007 — the thinning story is real and quantified. The champion sits ~+0.010 *above* the
family's own dot-count trend, i.e. the B=2 catalogue-apron pruning bought roughly one point of
DTI beyond thinning alone. **Outside the family, nothing has beaten 0.2478 OWNER-REPORT in 31
attempts across 24 detector families** — a 0.030 gap to the champion and a 0.196 gap to the
public #1 (0.4437).

### 2.2 What these numbers cannot say (stated plainly)

- Every fitted score is OWNER-REPORT; a single mis-transcribed score moves the fits. The
  instrument is a portfolio diagnostic, not a score predictor, and **must not be used to
  estimate a live score for an unscored file** (the repo's standing rule; also the 12-artifact
  calibration's conclusion).
- Observational, not causal: family membership and champion overlap are lineage variables, so
  their βs are partly mechanical (family members are nested thinnings of one mask).
- The ≥0.10 fetch threshold under-samples very low scores; the 59 unmatched rows are listed in
  the receipt.
- n = 53 with 5 covariates: the LOO diagnostics are honest (held-out only) but wide; the
  standardized βs are collinear (e.g. `frac_on_catalogue` flips sign between marginal and
  conditional views) and are reported for direction, not effect size.

### 2.3 The exact lattice bound (IR-49-LATTICE-01)

Computed from the pinned `r13-lattice-s5_v2` raster on the 5,167,373-pixel footprint:
the 5-px lattice leaves **6,649 hole pixels** farther than 3 px from every lattice dot, i.e.
99.87% of the footprint is within 3 px of the lattice. A dot set satisfies "≤70% of dots within
3 px of the lattice" only if ≥30% of its dots sit in holes, so **any submission with more than
⌊6,649 / 0.3⌋ = 22,163 dots fails the literal rule no matter where the dots are placed.**
Every champion-family file (37,654–61,328 dots), every research artifact in this repository,
and every one of the 48 scored masks except the 10,347-dot `r7-nms3` and 17,297-dot `ens12`
exceeds that bound. The rule as written therefore cannot be satisfied by any competitive map;
it needs the owner's prospective decision (calibration-probe exemption vs literal rule), not a
silent exemption by one session.

---

## 3. Nine-site executive table (which file, what estimate, unique or not, submit or not)

Scores are OWNER-REPORT actuals (the only defensible "estimate" for an already-scored file).
The "Arena51 LOO" column is the instrument's held-out prediction from the *other 47* masks —
a cross-check of the instrument, **not** a score estimate for a future submission. "Unique?" is
against the other eight site-best files and the genuine registry per the 70%/3-px rule.

| Site | Best file to download (audit) | Dots | Score (OWNER-REPORT) | Arena51 LOO | Unique? | Submit? |
|---|---|---:|---:|---:|---|---|
| GEMSDOE32 | [`gemsdoe32-h33-h33-2-b2-…-e5eb6e7e-zeros.tif`](../downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | 37,654 | **0.2778** | 0.2782 | NO — family (86.7%+ vs all eight) | **NO — already submitted; do not resubmit** |
| GEMSDOE36 | `anderson-geothermal-pinn-38854` | 38,854 | 0.2750 | 0.2730 | NO — champion + 1,200 dots | NO |
| GEMSDOE28 | `h36-1-rung30-blind-r1` | 37,660 | 0.2710 | 0.2736 | NO — family | NO |
| GEMSDOE31 | `h27-4-solo-d28` | 40,199 | 0.2708 | 0.2687 | NO — **byte-identical to GEMSDOE28's h27-4-r1-solo** (digest `dbb80910…`) | NO |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30` | 41,865 | 0.2632 | 0.2695 | NO — champion + 4,211 dots | NO |
| GEMSDOE25 | `dotted-h19-5-d2-8` | 44,090 | 0.2600 | 0.2646 | NO — **byte-identical to GEMSDOE30 + GEMSDOE29 files** (digest `426073b6…`) | NO |
| GEMSDOE30 | `d28-poisson300m-offcat-44090` | 44,090 | 0.2600 | 0.2646 | NO — same raster as GEMSDOE25's | NO |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5` | 60,069 | 0.2477 | 0.2431 | NO — family | NO |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5` | 61,328 | 0.2449 | 0.2392 | NO — family (98% overlap with H19-5) | NO |

**Best to submit today: none.** The only file with a claim to "best" is the GEMSDOE32 champion,
and it is already on the board. The unscored research artifacts in `docs/downloads/` (ARENA47,
H46, H44, Arena9, Arena8a, H38 …) all carry recorded negative verdicts and DO NOT SUBMIT labels;
their HOLDOUT-DTI values are listed in `registry/current_status.json` and are not scores.

---

## 4. Why 0.2778 happened, and what would actually beat it (PhD-level reading of the data)

1. **The thinning mechanism is real, quantified, and nearly exhausted.** Within the family,
   dot count alone reproduces the score ladder (LOO R² = 0.881, MAE = 0.0072), consistent with
   the metric algebra `DTI = T / (0.2·(T + S − M) + 0.8·|G|)`: mass whose realized kernel
   credit is below the break-even bar lowers the score, so removing it gains. But the champion
   already sits +0.010 above the trend, and no family member below 37,654 dots has ever been
   scored — extrapolating the trend further is a projection, and the recorded holdout attempts
   at further pruning (H32-winning-prune400, ARENA47 perturb) were flat-to-negative on
   HIDE-RECOVER-v3.0. The thinning lane is not where the next 0.02–0.17 lives.
2. **Detector novelty has a measured ceiling of 0.2478 so far.** Thirty-six non-family
   submissions across 33 site repositories — LiDAR scarp topology, radiometric fusion, tilt worms,
   submodular PU ensembles, geothermal belief covers, Euler deconvolution, SGMC tracing — top
   out at 0.2478 OWNER-REPORT. Every one of them discovered *some* off-catalogue structure and
   none of it converted into champion-level live score (the newest addition, GEMSDOE27's
   hydrothermal-piedmont CELF at 0.2190 OWNER-REPORT, is the fifth-best non-family result).
   This is the measured counterweight to the ARENA49-PCG instrument result above: the local
   instruments have never yet been validated by a non-family live score above 0.2478, so if the
   selector ever spends a slot on PCG, its live score is the decisive experiment — and the
   portfolio audit says the prior is that it lands in the 0.19–0.25 band, not above 0.2778. The gap to the champion (0.030) is the
   measured price of trading family coverage for novelty under this metric.
3. **The real target is 0.4437, and it is not a thinning target.** The public #1's margin over
   our best (+0.166) is 16× the champion's own above-trend residual. Whoever leads has found
   substantial hidden-fault coverage that neither the champion family nor any of our 31
   non-family detectors has. Under β = 0.8, the arithmetic says unseen-truth coverage is worth
   4× the false-positive price, so the winning lane is high-recall discovery of real,
   off-catalogue, geothermal-indicative faults (stepovers, terminations, relay ramps — the
   structural-discontinuity settings USGS identifies as hosting the most hydrothermal systems),
   not further optimization of the H19-5 mask.
4. **The concrete blockers before any new submission can be cleared:** (a) the owner's
   lattice-rule decision (§2.3) — without it, no dense map can pass Gate C7 literally;
   (b) an explicitly assigned single-method lane with a 3-experiment budget for a
   discovery-oriented hypothesis (the ranked, unexecuted slates in
   `docs/research/repository-review-20261026-arena-followup.md` and
   `docs/research/hypotheses-round6-20261026.md` remain the menu);
   (c) a candidate that beats the H38 per-cell OOF HOLDOUT-DTI 0.116958 on
   GEMSDOE32-HIDE-RECOVER-v3.0 with a paired CI excluding zero — the standing rule, unchanged.

---

## 5. Irregularities flagged this session

| ID | Severity | Statement | Mitigation |
|---|---|---|---|
| IR-49-SYNC-01 | high (main was red) | The ARENA47 merge advanced the release review/current status but left `registry/submission_build.json` pinned to Arena9; 5 tests failed on `main`. | `scripts/sync_submission_build.py` (fail-closed re-pin) + `tests/test_release_consistency.py` relationship contract; suite green (158 passed). |
| IR-49-SYNC-02 | medium | `build_site.py` rendered a missing H46 holdout field as `nan [0.00000, 0.00000]` — missing data displayed as a measured zero. | Generic candidate card renders `—` for missing metrics; regression test `test_no_missing_metric_renders_as_zero`. |
| IR-49-LATTICE-01 | high (decision required) | The literal ≤70%/3-px novelty rule is impassable for any map with >22,163 dots (exact bound, §2.3); every champion-family file and all but two scored masks exceed it. | Requires the owner's prospective protocol decision (exempt documented calibration probes, or keep the literal rule and accept that no dense map can pass). No exemption applied by this session. |

## 6. Remaining work and limitations (for the next session)

1. **Owner decision needed:** IR-49-LATTICE-01 (lattice exemption vs literal rule). Nothing can
   be promoted until it is made.
2. **Lane + budget needed:** an explicitly assigned discovery-oriented method paragraph; the
   pre-registered H46-4/H46-5 and the ranked unexecuted slates are the natural candidates.
   Budget: 3 experiments / 2 hours, per protocol.
3. **Data provenance unchanged:** all competition rasters remain owner-mirror, hash-pinned,
   not organizer-authenticated (IR-32-DATA-01). The 38 extra rasters fetched this session are
   likewise owner-repository bytes pinned at `registry/extra_scored_manifest.json`; the
   `.cache/extra/` copies are regenerable from it.
4. **No organizer receipts:** every historical score stays OWNER-REPORT. If the owner can
   save submission-page receipts binding hashes to scores, the ledger becomes
   ORGANIZER-CONFIRMED and this instrument's inputs harden.
5. **Instrument scope:** the covariate audit is observational on n = 53; do not use it to
   project scores for unscored files, and re-run it (one command) after any new live score
   lands so the family/non-family ceilings stay current.

## 7. Run card (protocol rule 5)

```json
{
  "session": "arena/b4675e19-gemsdoe32 (Arena51)",
  "hypothesis": "H48-A: owner-reported live DTI is explained principally by H19-5 family membership, dot count within the family, and catalogue-proximity covariates; non-family detectors plateau below the family.",
  "mechanism": "DTI = T/(0.2*(T+S-M)+0.8*|G|): uncredited mass is penalized 0.2 per unit, so family thinning removes sub-break-even mass; family membership is therefore the dominant score covariate.",
  "named_non_fault_mimic_or_confound": "OWNER-REPORT transcription error; lineage collinearity (family masks are nested thinnings); >=0.10 fetch selection; n=48 observational fit.",
  "kind": "retrospective portfolio audit; 0 new experiment lanes; 0 holdout runs; 0 weekly slots; method_lane: null (none assigned)",
  "holdout_dti": "not applicable - no candidate generated this session; prior repo best unchanged: H38 0.116958 [0.100533, 0.132040] on GEMSDOE32-HIDE-RECOVER-v3.0, 22232 withheld",
  "correlation_and_overlap_vs_registry": "no new raster placed; the 48 fitted masks were deduplicated by dot-mask digest (3 cross-site byte-identical pairs found: 0.2600, 0.2708, 0.1563)",
  "raster_sha256": "none generated this session",
  "validator_output": "no new raster; suite green after IR-49-SYNC-01/02 repairs and the H50-merge reconciliation (197 passed, 3 skipped)",
  "submission_name": "NONE - no file authorized",
  "submission_note": "n/a",
  "key_results": {
    "n_unique_scored_masks": 53,
    "spearman_frac_within3_h195": 0.844,
    "spearman_frac_within3_champion": 0.865,
    "loo_all_r2": 0.720, "loo_all_rho": 0.861, "loo_all_mae": 0.0256,
    "loo_family_dotcount_r2": 0.881, "loo_family_dotcount_mae": 0.0072,
    "family_max": 0.2778, "nonfamily_max": 0.2478, "nonfamily_n": 36,
    "champion_loo_residual_vs_family_trend": 0.0101,
    "lattice_holes": 6649, "max_dots_passing_literal_rule": 22163
  },
  "verdict": "negative (no promotion; deliverables are the repaired pipeline, the exact lattice bound, and the quantified portfolio analysis)"
}
```

## 8. Sources for manual review

- [DrivenData competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/) — prize structure, two-round scoring of the same selected file, external-data rule. Re-read this session; **end date shown is Dec 3, 2026 11:59 p.m. UTC** (the rules PDF text and homepage agree).
- [Problem description & metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — DTI α=0.2, β=0.8, 300 m triangular kernel; submission format EPSG:32611, 100 m, float32 in [0,1]. Re-read this session, chunk by chunk.
- [Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — top rows re-read this session (`xiaofanhu` 0.4437 #1 at 2026-10-26 21:40 UTC).
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — 3 submissions per week; single GeoTIFF 100 m for the whole GeoDAWN area; Phase 1/Phase 2 scoring; generative-AI disclosure duty. Re-read this session (chunks 1–3).
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) (DOI [10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)) — CC0; survey specs (Area 1/2 flight line spacings) relevant to seam mimics. Re-read this session.
- [DOE GDR #1391 INGENIOUS compilation](https://gdr.openei.org/submissions/1391) (DOI [10.15121/1881483](https://doi.org/10.15121/1881483)) — CC-BY 4.0; 2-m temperature probes, QFaults v2, paleo-geothermal features, wellspring geochemistry. Re-read this session.
- [USGS: Structural discontinuities and hydrothermal systems (Siler 2023)](https://www.usgs.gov/publications/structural-discontinuities-and-their-control-hydrothermal-systems-great-basin-usa) — fault stepovers and terminations host the largest, most localized stress/strain effects and the most hydrothermal systems: the process basis for the discovery lane recommended in §4.
- [USGS: Depth predictions of chemical geothermometers (2025)](https://www.usgs.gov/data/depth-predictions-chemical-geothermometers-estimated-using-a-three-dimensonal-temperature) — deep spring systems concentrate in high-strain-rate and basin settings: a second process basis for discovery targeting.
- Local priors this document builds on: [`instrument-calibration.md`](instrument-calibration.md) (12-artifact local-instrument calibration), [`why-02778-analysis-20261025.md`](why-02778-analysis-20261025.md) (metric review), [`evidence/focus_site_winner_overlap_20261026.json`](../../evidence/focus_site_winner_overlap_20261026.json) (nine-site byte audit).
