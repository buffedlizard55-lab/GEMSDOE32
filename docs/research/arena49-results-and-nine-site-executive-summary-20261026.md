# ARENA49-H1-PCG results and nine-site executive summary (2026-10-26)

**Verdict: 🔴 DO NOT SUBMIT YET — HOLD FOR THE SEPARATE WEEKLY-SLOT SELECTOR.**
Download for research/audit: **YES**. Live DrivenData upload: **NO** (0 weekly slots used by this session).

This is the first candidate in this repo whose shared `promotion_decision` returned `promote`
(all seven of its gates pass, including a paired HOLDOUT-DTI win and no SGMC-cal regression),
but promotion is **not** upload authorisation: the repo gate rule additionally requires
(i) a separate weekly-slot selector decision, and (ii) disposition of the literal
calibration-lattice gate, which fail-closes at 1.000 (see below). Both remain open.

Primary file (format-valid, genuine-unique):

[`docs/downloads/gemsdoe32-arena49-pcg-dualconcord-37654-20261026T220056Z-54e97629-zeros.tif`](../downloads/gemsdoe32-arena49-pcg-dualconcord-37654-20261026T220056Z-54e97629-zeros.tif)
· [single-TIFF ZIP](../downloads/gemsdoe32-arena49-pcg-dualconcord-37654-20261026T220056Z-54e97629-zeros.zip)
· [run card](../../evidence/arena49_pcg_run_card.json)
· [pre-registration](arena49-pc-preregistration-20261026.md)

| Field | Value |
|---|---|
| SHA-256 | `93c21c4cc18735aaeea44626b0697d72b96f9048ab817d9f0c5fb27381ef5f0f` |
| Dots | 35,487 (37,209 emitted at the 37,654 budget, then full-catalogue B=2 removed 1,722; independently re-verified: 0 dots on catalogue, 0 within 2 px) |
| Portal name | `GEMSDOE32-ARENA49-PCG-54E97629` |
| Note (68/140) | `ARENA49 PCG dual-concord 35487d B2 \| HR=0.0283 vis=0.0283 \| research` |
| Unique vs genuine registry rasters? | **YES** — max 3-px overlap 43.09% (vs Arena9 PGRN-PU) ≤ 70%; max surface \|Spearman\| 0.0664 ≤ 0.90; 16.11% vs the 0.2778 champion; 43 peers checked |
| Literal calibration lattice | 1.000 vs `13gems r13-lattice-s5` — FAIL literal rule, reported not exempted (IR-42-UNIQ-01: the same test scores ≈0.999 on random and champion dots because the 5-px lattice covers the footprint by construction; it cannot discriminate any dense candidate) |
| OK to download | YES (research/audit) |
| OK to submit | **NO — selector decision + lattice disposition required first** |

## HOLDOUT-DTI (not a live-score estimate)

| Arm | Evaluator | n withheld | HOLDOUT-DTI | 95% CI |
|---|---|---|---|---|
| **ARENA49 EXP3 dual PCG (file)** | `GEMSDOE32-HOLDOUT-v3-visible-gated` | 22,232 | **0.02826** | [0.02234, 0.03386] |
| ARENA49 EXP3 dual PCG | `GEMSDOE32-HIDE-RECOVER-v3.0` | 22,232 | 0.02826 | [0.02373, 0.03237] |
| Champion `h33-h33-2-b2`, same evaluators (flat mask) | same | 22,232 | 0.00452 | [0.00390, 0.00524] |
| Paired Δ (EXP3 − champion, 8 cells) | same | — | **+0.02360** | [+0.01775, +0.02944], p(pos)=1.0 |
| ARENA49 EXP3 SGMC-cal | `GEMSDOE32-SGMC-CAL-v3.0` | 62,703 | **0.07033** | [0.06364, 0.07608] |
| Champion SGMC-cal | same | 62,703 | 0.06412 | — |

Caveats, stated plainly:

1. The paired win is against the champion **flat mask** on this evaluator. It is **not** the
   0.09920 callable/OOF champion number (IR-45-EVAL-02) and it is **not** a projection of the
   0.2778 OWNER-REPORT live score. No live-score estimate is claimed for this file.
2. SGMC-cal is the off-catalogue diagnostic that sank H50 (0.01644) and Arena9; here it
   **beats** the champion proxy (0.07033 vs 0.06412) — the first genuine-unique candidate in
   this repo to do so while also winning the flat-mask holdout. That is evidence the PCG field
   generalises off-catalogue, not a leaderboard score.
3. Leakage canary: 5/5 channels, max two-polarity AUC 0.5531 ≤ 0.90 (no leakage signal).
4. Validator, independently re-run after writing (`scripts/check_submission.py --strict-finite`):
   PASSED — EPSG:32611, 3730×3292, float32, `nodata=None`, all 12,279,160 cells finite in
   [0,1], 0 NaN. This fixes the portal error *"Predicted values must be in range [0, 1]"* by
   construction (zeros variant).

## Three experiments (budget 3/3, 0.10 h)

| Exp | Support | Dots (pre-B2) | 3-px vs champion | HOLDOUT-DTI vis-gated | SGMC-cal |
|---|---|---|---|---|---|
| EXP1 DEM-PCG (Band 12) | 473,158 | 37,219 | 15.84% | 0.02900 [0.02382, 0.03383] | 0.07065 |
| EXP2 GRAV-PCG (Band 13) | 512,387 | 37,244 | 13.58% | 0.02066 [0.01696, 0.02428] | 0.03274 |
| **EXP3 dual concordance (file)** | 473,158 | 37,209 | 16.11% | **0.02826 [0.02234, 0.03386]** | 0.07033 |

EXP1 (DEM-only) scored marginally above EXP3 on both instruments (Δ +0.00074 holdout,
+0.00031 SGMC-cal; CIs overlap). EXP3 was retained as the file because the pre-registration
froze it as the shipped candidate before any results existed — switching arms after seeing
scores would be post-hoc selection. EXP1 is the named, measured follow-up for the selector /
next session: it is simpler, but its shoreline-bench mimic rejection is weaker by design.

**Why this lane worked where TM-SPI (H50) did not:** phase congruency is amplitude-invariant,
so a low-throw scarp step in `det_elev` ranks as strongly as a range-front scarp, whereas
H50's theta/SPI weighting and every gradient/Hessian detector in this repo scale with throw
amplitude. The catalogue-hidden population the holdout withholds is dominated by exactly
those low-amplitude scarps (canary AUCs ≈0.51–0.55 show the field is not leaking the answer).

## Why 0.2778 scored highest among the nine sites (OWNER-REPORT)

B-pruning of the H19-5 dotted ridge (121,131 → D2.8 44,090 → B=1 40,199 → B=2 37,654) removes
predictions inside 200 m of known faults that the official metric already masks
([staff #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)).
That is a false-positive trim, not a new detector. No organizer receipt in this repo links
those bytes to 0.2778, so the number remains OWNER-REPORT, not ORGANIZER-CONFIRMED.

## Nine focus sites — which file, what number, unique?

Scores in the "best historical" column are **OWNER-REPORT**, not ORGANIZER-CONFIRMED.
"Unique vs family?" is the ≤70% 3-px / ≤0.90 Spearman rule against the other site-best files.
**Estimated-score column for the new file is HOLDOUT-DTI only — no live projection exists.**

| Site | File to download | Best historical (OWNER-REPORT) / HOLDOUT-DTI estimate | Unique vs the other 8? | Submit today? |
|---|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5` | 0.2477 | NO (H19-5 family) | NO |
| GEMSDOE25 | `dotted-h19-5-d2-8` | 0.2600 | NO (dot-identical to GEMSDOE30) | NO |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5` | 0.2449 | NO (H19-5 relative) | NO |
| GEMSDOE28 | `h36-1-rung30-blind-r1` | 0.2710 | NO (B-pruned H19-5) | NO |
| GEMSDOE30 | `d28-poisson300m-offcat-44090` | 0.2600 | NO (duplicate of GEMSDOE25) | NO |
| GEMSDOE31 | `h27-4-solo-d28` | 0.2708 | NO (duplicate of GEMSDOE28 B=1) | NO |
| **GEMSDOE32** | **`h33-h33-2-b2` already submitted** | **0.2778 (portfolio best)** | NO (B=2 of the same family) | **NO — do not resubmit** |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30` | 0.2632 | NO (family relative) | NO |
| GEMSDOE36 | `anderson-geothermal-pinn-38854` | 0.2750 | NO (champion + 1,200 dots) | NO |
| **This session ARENA49** | [`gemsdoe32-arena49-pcg-dualconcord-37654-20261026T220056Z-54e97629-zeros.tif`](../downloads/gemsdoe32-arena49-pcg-dualconcord-37654-20261026T220056Z-54e97629-zeros.tif) | HOLDOUT-DTI 0.02826 [0.02234, 0.03386] (visible-gated, 22,232 withheld); SGMC-cal 0.07033 — **not a live estimate** | **YES** (43.09% max genuine 3-px; \|ρ\| 0.0664) | **NO — HOLD for selector + lattice disposition** |

**Portfolio recommendation:** keep GEMSDOE32 `h33-h33-2-b2` (0.2778 OWNER-REPORT) as the
historical best of these nine. ARENA49-PCG is the strongest genuine-unique candidate this
repo has produced on the shared instruments and is the file the separate selector should
consider first for a weekly slot — after disposing of IR-42-UNIQ-01 (the literal lattice
gate that every dense candidate, including the champion, fails by construction).
Zero weekly slots were used by this session.

## Irregularities flagged

- **IR-ARENA49-LANE-01** — session prompt's "single method paragraph" was absent (placeholder
  thresholds). Rank-1 hypothesis adopted as lane in the frozen pre-registration; recorded here.
- **IR-42-UNIQ-01 (re-confirmed)** — literal lattice overlap 1.000 for this candidate; the
  lattice is a synthetic 5-px covering grid, so this gate currently blocks *every* dense file
  including the 0.2778 champion. Selector must either exempt calibration probes by manifest
  role or accept the genuine-raster gate (43.09% / 0.0664, PASS) as the operative test.
- **IR-45-EVAL-02 (unchanged)** — flat-mask champion 0.00452 ≠ callable champion 0.09920;
  all comparisons here are flat-vs-flat on identical evaluators and are labelled as such.

## Official sources

- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://github.com/drivendataorg/gems-prize-reference-solution
- Kovesi (1999), *Image Features From Phase Congruency*: https://www.peterkovesi.com/papers/Kovesi_Videre_v1n3001.pdf
- Monogenic phase congruency lineaments (GeoConvention 2016): https://geoconvention.com/wp-content/uploads/abstracts/2016/147_GC2016_Monogenic_Phase_Congruency.pdf
- USGS GeoDAWN: https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and (DOI 10.5066/P93LGLVQ)

## Run card (JSON, abbreviated — full card: `evidence/arena49_pcg_run_card.json`)

```json
{
  "hypothesis_id": "ARENA49-H1-PCG",
  "mechanism": "Amplitude-invariant log-Gabor phase-congruency steps in det_elev + iso_grav_anom, dual-field concordance, CELF 37,654 budget, B=2",
  "named_non_fault_mimic": "Lake Lahontan shoreline benches (DEM-only) and basin-fill density contacts (gravity-only), down-weighted by concordance",
  "holdout_dti": "HOLDOUT-DTI 0.02826 [0.02234, 0.03386], GEMSDOE32-HOLDOUT-v3-visible-gated, 22,232 withheld; SGMC-cal 0.07033 [0.06364, 0.07608] vs champion 0.06412",
  "correlation_overlap_vs_registry": "max genuine |Spearman| 0.0664; max genuine 3-px 43.09% (Arena9); lattice 1.000 (IR-42-UNIQ-01)",
  "raster_sha256": "93c21c4cc18735aaeea44626b0697d72b96f9048ab817d9f0c5fb27381ef5f0f",
  "validator": "PASS strict-finite: EPSG:32611 3730x3292 float32 nodata=None, all cells finite in [0,1], 0 on-catalogue",
  "submission_name": "GEMSDOE32-ARENA49-PCG-54E97629",
  "submission_note": "ARENA49 PCG dual-concord 35487d B2 | HR=0.0283 vis=0.0283 | research",
  "verdict": "negative (release verdict) — promotion_decision=promote on shared gates, ok_to_submit=false: selector + lattice disposition required, 0 slots used"
}
```
