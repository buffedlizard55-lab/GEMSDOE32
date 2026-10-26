# H50 TM-SPI results and nine-site executive summary (2026-10-26)

**Verdict: 🔴 DO NOT SUBMIT.** Download for research/audit: YES. Live DrivenData upload: NO. 0 weekly slots used.

Primary file (format-valid, genuine-unique, scientifically negative vs live-score family):

[`docs/downloads/gemsdoe32-h50-tmspi-dualconcord-37654-20261026T214025Z-f0e385b9-zeros.tif`](../downloads/gemsdoe32-h50-tmspi-dualconcord-37654-20261026T214025Z-f0e385b9-zeros.tif)

| Field | Value |
|---|---|
| SHA-256 | `c534effe023f2876b08239384d075be313d489a8dc3bf8dbf22f7d6509872112` |
| Dots | 37,121 (0 on catalogue, B=2) |
| Portal name | `GEMSDOE32-H50-TMSPI-F0E385B9` |
| Note (70/140) | `H50 TM-SPI dual-concord 37121d B2 \| HR=0.0126 vis=0.0126 \| research` |
| Unique vs 9 focus-site family? | **YES** (max 3-px 18.5% ≤ 70%; \|Spearman\| 0.0095 ≤ 0.90; 14.2% vs 0.2778 champion) |
| OK to download | YES (research/audit) |
| OK to submit | **NO** |

## HOLDOUT-DTI (not a live-score estimate)

| Arm | Evaluator | n withheld | HOLDOUT-DTI | 95% CI |
|---|---|---|---|---|
| H50 EXP3 dual concordance | `GEMSDOE32-HOLDOUT-v3-visible-gated` (flat mask) | 22,232 | 0.01261 | [0.01091, 0.01420] |
| Champion `h33-h33-2-b2` same evaluator | same | 22,232 | 0.00452 | [0.00390, 0.00524] |
| Paired Δ (H50 − champion) | same cells | 8 cells | +0.00809 | [0.00575, 0.01006] p(pos)=1.0 |
| H50 SGMC-cal | `GEMSDOE32-SGMC-CAL-v3.0` | 62,703 | 0.01644 | [0.01427, 0.01864] |
| Champion SGMC-cal | same | 62,703 | 0.06412 | — |

The paired win is **only** against the champion *flat mask* on this evaluator (the same 0.0045 number ARENA47 reported). It is **not** the 0.09920 callable/OOF champion number (`IR-45-EVAL-02`) and it is **not** a projection of the 0.2778 OWNER-REPORT live score. SGMC-cal loses. Literal lattice raster was not in `docs/downloads`; that gate fail-closes (`IR-42-UNIQ-01`).

Leakage canary: 9/9 channels, max AUC 0.5206 ≤ 0.90.

## Why 0.2778 scored highest among the nine sites (OWNER-REPORT)

B-pruning of the H19-5 dotted ridge (121,131 → D2.8 44,090 → B=1 40,199 → B=2 37,654) removes predictions inside 200 m of known faults that the official metric already masks ([staff #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)). That is a false-positive trim, not a new detector. No organizer receipt in this repo links those bytes to 0.2778.

A unique PF contact skeleton (this lane) does **not** automatically beat that family on the live metric: it covers a different, mostly blind-basement population and currently places too little mass on the high-credit unmapped continuations the H19-5 family already owns.

## Nine focus sites — which file, what number, unique?

Scores in the “best historical” column are **OWNER-REPORT**, not ORGANIZER-CONFIRMED. “Unique vs family?” is 3-px overlap ≤ 70% against the other eight site-best files.

| Site | File to download (if any) | Best historical (OWNER-REPORT) | Unique vs the other 8? | Submit today? |
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
| **This session H50** | [`gemsdoe32-h50-tmspi-dualconcord-37654-20261026T214025Z-f0e385b9-zeros.tif`](../downloads/gemsdoe32-h50-tmspi-dualconcord-37654-20261026T214025Z-f0e385b9-zeros.tif) | HOLDOUT-DTI 0.01261 (not a live estimate) | **YES** (18.5% max genuine 3-px) | **NO** (gates fail) |

**Portfolio recommendation:** keep GEMSDOE32 `h33-h33-2-b2` (0.2778 OWNER-REPORT) as the historical best of these nine. Spend **zero** weekly slots on H50.

## Three experiments (budget 3 / 3, 0.03 h)

| Exp | Support | Dots | 3-px vs champion | HOLDOUT-DTI vis-gated | SGMC-cal |
|---|---|---|---|---|---|
| EXP1 mag TM-SPI | 51,114 | 37,120 | 14.24% | 0.01215 [0.01026, 0.01396] | 0.01612 |
| EXP2 grav TM-SPI | 94,593 | 37,177 | 14.77% | 0.01289 [0.00816, 0.01823] | 0.01309 |
| **EXP3 dual concordance (file)** | 50,114 | 37,121 | 14.20% | **0.01261 [0.01091, 0.01420]** | 0.01644 |

Negative result is a deliverable: SPI/theta-map contacts are **lane-unique** and leak-free, but they do not recover the catalogue-hidden population the live 0.2778 family covers.

## Official sources

- https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- https://github.com/drivendataorg/gems-prize-reference-solution
- https://doi.org/10.1190/1.1883351 (Wijns theta map)
- Thurston & Smith (1997) SPI / local wavenumber
