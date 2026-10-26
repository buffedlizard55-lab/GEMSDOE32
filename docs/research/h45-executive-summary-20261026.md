# Executive Summary — Nine Focus Sites + New Unique H45 Submission (2026-10-26)

## 🔴 DOWNLOAD DECISION — READ FIRST

| Question | Answer |
|---|---|
| Is there a new, unique TIF generated this session? | **YES** — `gemsdoe32-h45-kernelspacing-37654dots-20261026T163401Z-2fe5944c-zeros.tif` (SHA-256 `b14bba00d6053e75e5c72d9e68fac52f607fe40de1c356111baea85e1ceee538`), in `docs/downloads/` with `.zip` + `-audit.json` |
| Is it OK to download? | **YES — for audit/research only** |
| Is it OK to submit to DrivenData? | 🔴 **NO — DO NOT SUBMIT.** It failed 3 promotion gates (below). No weekly slot was spent. |
| Why not? | (1) The new kernel-spacing hypothesis was **falsified** on holdout; (2) the winning control arm (HOLDOUT-DTI 0.1009) does **not** beat the repo holdout best (H38, 0.11696); (3) literal lane-overlap is 71.91% > 70% vs one dense registry raster |
| Best file to submit if a slot must be used? | **None new.** The already-submitted 0.2778 champion must not be resubmitted. Wait for a lane that beats H38 on hide-and-recover. |
| Submission name / note (if ever authorized — currently NOT) | Name: `GEMSDOE32-H45-KS-2FE5944C` · Note (110/140): `H45-1 kernel-spacing KS0 37654d \| HOLDOUT-DTI 0.1009 [0.0859,0.1162] HIDE-RECOVER-v3.0 n=22232 \| DO NOT SUBMIT` |

**Format safety (the "Predicted values must be in range [0, 1]" error):** the H45
`-zeros.tif` passes `scripts/check_submission.py --strict-finite` — single-band
float32, EPSG:32611, 3730×3292, transform matched to template, nodata=None, all
12,279,160 cells finite in [0.0, 1.0], values exactly {0,1}, 37,654 dots, 0 on the
catalogue. That error is caused by NaN/outside-footprint sentinels in `-nan.tif`
variants; **only ever upload a `-zeros.tif` (or its .zip)**.

## 1. Nine focus sites — highest reported submission per site

All scores below are **OWNER-REPORT** (owner's submission log; no organizer receipt
linking exact bytes to score is stored in this repo — IR-32-SCORE-01). They are
**not** ORGANIZER-CONFIRMED and **not** HOLDOUT-DTI.

| Site | Best reported submission | Reported score | What it is (byte-verified lineage) | Duplicate warning |
|---|---|---:|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | H19-5 surface thinned at 1.5 px | Parent family of all later dotted files |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | Same surface thinned at 2.8 px, 44,090 dots | **Dot-identical to GEMSDOE30's 0.2600 file** (IR-32-FAM-02) — submitting both wastes a slot |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | Gap-closure on the d1.5 emission | Same H19-5 family |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | Blind-rung variant, 37,660 dots | Siblings at 0.2707–0.2708 differ by <0.003 — one family, not four independent results |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | Poisson-300 m off-catalogue emission | **Identical dots to GEMSDOE25 best** |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | Solo d2.8 base | Exact parent of the GEMSDOE32 champion |
| **GEMSDOE32** | **`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`** | **0.2778** | Solo d2.8 **minus 2,545 dots within 2 px of the catalogue**, 37,654 dots | Already submitted — **never resubmit** |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | Analog tip/step-over extension, 41,865 dots | Adding dots to the champion family *lowered* the reported score |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | PINN variant, 38,854 dots | **Contains all 37,654 champion dots** (IR-32-FAM-01); +1,200 dots cost −0.0028 |

**Which single submission is "best" across the nine sites?** The GEMSDOE32 champion
(0.2778, OWNER-REPORT). It is already submitted, so it is **not** a download-to-submit
candidate. Every other site's best is the same H19-5 dotted family at a different
thinning/buffer operating point — the nine sites are one lineage, not nine methods.

## 2. Why did 0.2778 score highest? (PhD-level answer)

The metric is DTI = TP / (0.2·(TP+FP) + 0.8·|G|) with a 300 m triangular kernel
(α=0.2, β=0.8; official: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
Catalogue (known-fault) pixels are masked out of scoring (organizer clarification,
DrivenData community thread 11516). Therefore dots within ~200 m of a mapped fault
can earn almost no credit toward *hidden* (uncatalogued) truth but still pay FP
mass. The champion is exactly the 0.2708 solo base with those dots deleted
(B=2 px buffer): fewer, purely off-catalogue dots → less FP per unit TP → higher
DTI. The ladder 0.2600 (44,090 dots) → 0.2708 (B=1) → 0.2778 (B=2) is consistent
with that mechanism, and GEMSDOE36 shows the reverse (adding 1,200 dots: −0.0028).
**Caveat:** no organizer receipt links these bytes to these scores, hidden-truth
TP/FP/FN are unobservable, so this is a lineage-supported mechanism, not proof of
causality. The current public leaderboard #1 is 0.4437 (read 2026-10-26,
`evidence/live_leaderboard_snapshot_20261026.json`); 0.4413 and 0.3195 in the brief
are older snapshots.

## 3. New work this session — H45-1 Kernel-Spacing (3 experiments, budget exhausted)

Pre-registration: `docs/research/h45-kernel-spacing-preregistration-20261026.md`.
Hypothesis: dots closer than the 300 m kernel radius redundantly cover the same
truth pixels, so hard ≥4 px separation + a smaller budget should raise credit/dot.
Mimic that could fake it: smooth probability blobs over pluton margins (spacing
would just spread false positives). Leakage canary: **PASS** (35/35 channels,
worst AUC 0.577 ≤ 0.90). All numbers are **HOLDOUT-DTI, GEMSDOE32-HIDE-RECOVER-v3.0,
22,232 withheld positives, 95% CI** unless labelled otherwise.

| Experiment | Config | HOLDOUT-DTI [95% CI] | SGMC-cal diagnostic (not a score) |
|---|---|---:|---:|
| EXP1 `KS0-37654` | min-sep 0, 37,654 dots (control) | **0.10086 [0.0859, 0.1162]** | 0.06838 |
| EXP2 `KS4-20000` | min-sep 4 px, 20,000 dots | 0.08646 [0.0717, 0.1009] | 0.05396 |
| EXP3 `KS4-12000` | min-sep 4 px, 12,000 dots | 0.07170 [0.0581, 0.0847] | 0.04160 |

**Result: hypothesis FALSIFIED.** With β=0.8, lost coverage (FN) costs 4× more than
saved FP; thinning/spacing away dots monotonically lowers DTI. This also explains,
in reverse, why the champion's *targeted* B=2 deletion (removing only provably
worthless near-catalogue dots) helped while *blind* spacing does not.

## 4. Required deliverable table — file, estimated score, uniqueness

"Estimated score" below is a **PROJECTION** (0.2778 OWNER-REPORT × candidate/champion
SGMC-cal ratio on GEMSDOE32-SGMC-CAL-v3.0) — a model, **never a measured score**.
Only a DrivenData submission receipt can create an ORGANIZER-CONFIRMED score.

| File to download | Status | Estimated score (label) | Unique vs the nine sites? |
|---|---|---|---|
| `docs/downloads/gemsdoe32-h45-kernelspacing-37654dots-20261026T163401Z-2fe5944c-zeros.tif` (+ `.zip`, `-audit.json`) | 🔴 **DO NOT SUBMIT** (download for audit: YES) | HOLDOUT-DTI 0.10086 [0.0859, 0.1162] (n=22,232); PROJECTION ≈0.296 — **not a score, do not quote as one** | **Cryptographically new** (SHA-256 `b14bba00…e538`, not byte- or dot-identical to any of 324 registry rasters); surface Spearman PASS (max \|ρ\|=0.2198 ≤ 0.90 vs 314 genuine rasters); **literal dot-overlap FAIL**: 71.91% of dots within 3 px "
...[truncated 1473 chars]