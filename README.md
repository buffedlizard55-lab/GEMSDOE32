# GEMSDOE32 — DOE GEMS Prize Research, Validation & Submission System

<!-- SINGLE DECISION: rendered from registry/current_status.json and evidence/current_release_review.json (both must authorize; fail closed). Update those files, never add a second banner. -->
## 🚦 Current Decision — 2026-10-26 04:45 UTC

# 🔴 DO NOT SUBMIT — no upload is authorized (`DOWNLOAD FOR RESEARCH / AUDIT: YES · SUBMIT TO LIVE PORTAL: NO`)

| Artifact | Status | Evidence & Automated Validation Summary |
|---|---|---|
| **Arena8a unique file (`A8A-H1: MDRC` + Crest CreditBar, `44,090`d)**<br>[`gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.tif`](docs/downloads/gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.tif) (`230,275 B`) · [`.zip`](docs/downloads/gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.zip) (`197,576 B`) · [`-nan.tif`](docs/downloads/gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-nan.tif) · [`checks.json`](docs/downloads/checks-gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.tif.json) · [`Run Card`](evidence/arena8a_run_card.json) | 🔴 **DO NOT SUBMIT — audit/research artifact (`verdict = negative`)** | SHA-256 `0bbb3128c0e91a5f10003b1f92f2ef6030822a27b231299f7ce3c22d2d4d13e5`. Validated 100% automatically (`scripts/verify_arena8a_submission.py`): `EPSG:32611`, `3730×3292` `float32`, `nodata=None`, all `12,279,160` cells finite in `[0.0, 1.0]`, `0` NaN, `44,090` dots (`0` on-cat, `83.26%` off-`H19-5`). Canary PASS (`57/57`, `max AUC = 0.6217 <= 0.90`). Genuine uniqueness PASS across all 20 genuine rasters (`|Spearman| <= 0.4209 <= 0.90`; `within-3px <= 64.96% <= 70%`: `52.89%` vs `0.2778` Champion, `64.21%` vs `H36-1C`, `22.06%` vs `H42`, `19.37%` vs `R6-1`). Wins fold-local visible-only **`HOLDOUT-DTI = 0.10679 [0.08765, 0.12850]`** on `GEMSDOE32-HOLDOUT-v3-visible-only` (`22,232` withheld positives; paired difference vs `D2.8 vis-B2` is `+0.00784 [0.00397, 0.01113]`, 7/8 spatial-draw cells), **but fails Gate `G5`** on the off-catalogue SGMC diagnostic (run card: not a leaderboard score) due to `y=0` PU suppression `IR-A8A-PU-BIAS-01`, and literal 5-px lattice overlap (`99.04%`). Name: `GEMSDOE32-A8A-MDRC-CE1ABD39` · Note (`76/140`): `GEMSDOE32 A8A MDRC 44090d B2 \| visHoldout 0.1068 SGMC 0.0551 \| DO-NOT-SUBMIT`. |
| **Newest unique file (`H36-1C` TDR-PDS + Steger Crest)**<br>[`gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif) (`206,761 B`) · [`.zip`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.zip) (`171,140 B`) · [`-nan.tif`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-nan.tif) · [`audit.json`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-audit.json) · [`Run Card`](evidence/h36_tdr_pds_run_card.json) | 🔴 **DO NOT SUBMIT — audit/research artifact (`verdict = negative`)** | SHA-256 `f75ac7ae172eed0840b948beaa6587a532c0a44453c3ad90874f02967e0a887c`. Validated 100% without human intervention: `EPSG:32611`, `3730×3292` `float32`, `nodata=None`, all `12,279,160` cells finite in `[0.0, 1.0]`, `0` NaNs (prevents `"Predicted values must be in range [0, 1]"`), `37,654` dots (`0` on catalogue; `83.84%` off-`H19-5`). Leakage canary PASS (`46/46` channels, `max AUC = 0.58412 <= 0.90`). Genuine uniqueness PASS across all 44 genuine detector rasters (`max |Spearman| = 0.1595 <= 0.90`; `max 3-px overlap = 60.44% <= 70%`; `52.20%` vs `0.2778` Champion). Achieves **`HOLDOUT-DTI = 0.10982` `[0.09866, 0.12275]`** on `GEMSDOE32-HOLDOUT-v3-visible-gated` (`22,232` withheld positives; vs Champion HOLDOUT-DTI `0.09920`), **but fails closed** because the censorship-matched `d0==0` control is below the raw Champion HOLDOUT-DTI and the off-catalogue SGMC diagnostic gate fails (diagnostic, not a leaderboard score); literal 5-px calibration-lattice overlap is `99.80% > 70%` (`IR-32-LATTICE-01`). Archive name: `GEMSDOE32-H36-1C-TDR-PDS-9FF9D6E2` · Note (`118/140` chars): `H36-1C TDR-PDS+Steger 37654d \| HOLDOUT-DTI 0.1098 [0.0987,0.1227] v3-vis 22232pos \| SGMC 0.0838<0.0961 \| DO NOT SUBMIT`. |
| **Archived Round-6 candidate (`R6-1`)**<br>[`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif) · SHA-256 `c7f094c1…eae56547` | 🔴 **DO NOT SUBMIT — audit artifact only** | Real, uniquely named, format-valid GeoTIFF (`docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`). **Format validity is not enough to authorize a competition upload.** Fail-closed release review ([protocol audit](docs/research/protocol-review-20261026.md), [decision](evidence/current_release_review.json)) found non-fold-local B=2 masking and noted that SGMC-tracing files score `0.65 / 0.56` locally yet `0.0492 / 0.0512` live (`IR-42-INSTR-02`, [counter-examples](evidence/sgmc_instrument_live_counterexamples.json)). |
| **Round-6 Multi-Physics file (`EXP3_H38_G1_CORROB` — `H38-G1..G4`, 53ch LiDAR + GeoDAWN + GDR + CELF)**<br>[`gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif) (`209,987 B`) · [`.zip`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.zip) (`176,161 B`) · [`-nan.tif`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-nan.tif) · [`audit.json`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-audit.json) · [`H38 Run Card`](evidence/h38_run_card.json) | 🔴 **DO NOT SUBMIT — audit artifact (`verdict = negative`)** | SHA-256 `6efe140229c46b274ab7431bab0b9c1318ade642096ca8a1ff8c36317d2d68ff`. Validated automatically (`20/20 PASS`: `EPSG:32611`, `3730×3292` `float32`, `nodata=None`, all `12,279,160` cells finite in `[0.0, 1.0]`, `37,654` dots, `0` on catalogue, `81.2%` off-`H19-5`). 53-channel Leakage Canary PASS (`worst AUC = 0.6235 <= 0.90`). Achieves **repo-best `HOLDOUT-DTI = 0.11696` `[0.10053, 0.13204]`** on `GEMSDOE32-HIDE-RECOVER-v3.0` (`22,232` withheld positives; paired vs Champion HOLDOUT-DTI `0.09920`, Δ `+0.01776 [+0.00832, +0.02743]`; historical report's `0.2778` Champion value is OWNER-REPORT, not a holdout score) via `IR-32-LIDAR-01` quantile routing + 1m 3DEP LiDAR + GeoDAWN K/Th/U/TMI_up150 + GDR `#1391`, and passes `<= 70%` overlap vs all 26 live-scored cross-site detectors (`max 69.49%`; `58.78%` vs Champion), **but fails closed** because the off-catalogue SGMC diagnostic gate fails (diagnostic, not a leaderboard score) and the unexempted `<= 3 px` check hits local `hcvf2` (`77.56%`) + `r13-lattice-s5` (`99.71%`). Archive name: `GEMSDOE32-EXP3_H38_G1_CORROB-35859E28` · Note (`102/140` chars): `GEMS32 EXP3_H38_G1_CORROB 53ch LiDAR+GeoDAWN+GDR CELF 37654px HR=0.1170 SGMC=0.0504 HOLD-DO-NOT-SUBMIT`. |
| **Best scored file (`GEMSDOE32` Champion)**<br>[`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | **Already submitted — do NOT resubmit** | **`0.2778` (`OWNER-REPORT`)**; `37,654` dots; SHA-256 `c55bafc4…7ab6fa9`. Highest reported score across these 9 focus sites; no organizer receipt linking the score to these bytes is present in this repository. |
| **Withdrawn / superseded (`H42-1`, `h32-winning-46090`, `h-geo-conduit`)** | 🔴 **DO NOT SUBMIT** | `H42-1` (`b91008fa`): `81.9%` within 3 px of `GEMSDOE25` `h38-greedy-credit` (`> 70%`) and `0.0545 < random 0.0709` on off-catalogue SGMC (`IR-42-INSTR-01`). `h32-winning-46090` (`c3459dcd`): `84.0%` champion-family variant (`IR-42-README-01`). `h-geo-conduit` (`2d0d0c5e`): `70.24%` overlap vs `GEMSDOE28` (`IR-R6-02` / `IR-32-CONDUIT-01`). |

- **GitHub Pages Landing & Executive Summary:** [`docs/index.html`](docs/index.html) · [`docs/executive-summary.html`](docs/executive-summary.html) (exact portal upload procedure for when a future candidate clears every gate; use `-zeros.tif` so `"Predicted values must be in range [0, 1]"` can never occur).
- **Official Public Leaderboard (direct read `2026-10-26T04:32:28Z`):** `#1 = 0.4437` (`xiaofanhu`). The `0.4413` value is the cached `2026-10-25` snapshot; `0.3195` is historical, not current. See the [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) and [`evidence/live_leaderboard_snapshot_20261026.json`](evidence/live_leaderboard_snapshot_20261026.json). Weekly cap: governed by the authenticated submission screen ([staff clarification #11553](https://community.drivendata.org/raw/11553)).

---

## Arena Core Values

- **Maximize P(Win):** Weigh tradeoffs and risk and choose the path that maximizes the probability of winning. Always put the outcome first! Every weekly DrivenData submission slot is scarce information-bearing capital — never spend a live slot on a duplicate, unvalidated, or holdout-inferior raster.
- **Own the Outcome:** Own results end to end, from initial action to final result. Step up and take action when problems arise. Treat both failure and success as signals to learn and adapt. Stay accountable until the final outcome is achieved — including repairing shared broken evaluation instruments (`IR-32-INSTR-03` fixed in `src/gems32/holdout.py`), auditing band misidentifications (`IR-32-BAND-02`, `IR-32-BAND-03`), and reporting negative results honestly.

---

## 1. Executive Summary Across the 9 Focus Sites (`GEMSDOE24` .. `GEMSDOE36`)

Every historical live score below is labelled **`OWNER-REPORT`** (recorded in the portfolio history; no organizer receipt in this repository links raw `.tif` bytes to a live score — `IR-32-SCORE-01`). The supplied brief's `0.3195` is an older leaderboard observation, and `0.4413` was the cached `2026-10-25` public snapshot; the official leaderboard read at `2026-10-26T04:32:28Z` showed public `#1 = 0.4437` (`xiaofanhu`). The `0.2778` score is the highest **reported** score across these 9 focus sites, not organizer-authenticated evidence.

| Site & GitHub Repo | Cached HEAD from site audit (not freshly fetched here) | Best Historical Scored Submission (`OWNER-REPORT`) | Unique vs. Duplicate / Lineage Forensics | Latest recorded `2026-10-26` TIF & Gate Verdict | Submit Today? |
|---|---|---|---|---|---|
| **[GEMSDOE24](https://github.com/buffedlizard55-lab/GEMSDOE24)** | `2a2b9829` | `0.2477` (`h25-1-dotted-h19-5-d1-5`, `60,069`d) / `0.2194` (`h24-1-tip-relay`) | `d1-5` is superseded denser `H19-5` parent; `h24-1` is unique tip/relay below `0.2778` | `gemsdoe24-crp1-dipfan-stepover-37654-…-7764b339-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE25](https://github.com/buffedlizard55-lab/GEMSDOE25)** | `de77cb6c` | `0.2600` (`dotted-h19-5-d2-8-…-e56ea318af89`, `44,090`d) | **Dot-identical (`44,090 / 44,090`) to `GEMSDOE30`**; unpruned parent of `0.2778` | `h44` multi-physics lane (`verdict = negative`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE27](https://github.com/buffedlizard55-lab/GEMSDOE27)** | `398cda94` | `0.2449` (`topo-gap-closure-on-d1-5`) / `0.2190` (`H29-S`) | Gap-closure on `d1.5` hurt (`-0.0028`); `H29-S` unique below `0.2778` | `gems27-h31-range-front-step-50k-…-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE28](https://github.com/buffedlizard55-lab/GEMSDOE28)** | `94152be6` | `0.2710` (`h36-1-rung30`) / `0.2708` (`solo-8acb75e1`, `40,199`d) | **`0.2708` is dot-identical (`40,199 / 40,199`) to `GEMSDOE31`**; `B=1` parent of `0.2778` | `gems28-s20-asymmetric-hanging-wall-37654-…-8635a2a3-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE30](https://github.com/buffedlizard55-lab/GEMSDOE30)** | `ac54b7f3` | `0.2600` (`d28-poisson300m-offcat-44090`) | **100% pixel-identical duplicate of `GEMSDOE25`** (`0.2600 == 0.2600`) | `gemsdoe30-PTA1-piedmont-thermal-37654-…-669abcb3-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE31](https://github.com/buffedlizard55-lab/GEMSDOE31)** | `6ca63b0c` | `0.2708` (`h27-4-solo-d28-8acb75e1`, `40,199`d) | **100% pixel-identical duplicate of `GEMSDOE28`** (`40,199` dots) | `gemsdoe31-xfcoh31-37654-…-c00c6405-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32)** | *(current)* | **`0.2778` (`h33-h33-2-b2-…-e5eb6e7e`, `37,654`d) — PORTFOLIO CHAMPION** | **Unique optimal `B=2` endpoint** (`solo` minus `2,545` `1 < d_cat <= 2 px` flank dots); **already scored — do not resubmit** | `gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif` (`verdict = negative`, audit/research only) | **NO (`0.2778` already live)** |
| **[GEMSDOE33](https://github.com/buffedlizard55-lab/GEMSDOE33)** | `7deca206` (cached audit) | `0.2632` OWNER-REPORT (`h33d-analog-tip-stepover-r30`, `41,865`d per `evidence/nine_site_executive_audit_20261026.json`) | Distinct tip/step-over geometry; reported score is `0.0146` below GEMSDOE32's reported `0.2778` | Latest recorded lane negative (`DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE36](https://github.com/buffedlizard55-lab/GEMSDOE36)** | `a4c660a8` | `0.2750` (`anderson-geothermal-pinn-38854`, `38,854`d) | **96.9% superset duplicate of `GEMSDOE32` Champion** (`37,654` Champion dots + `1,200` extra dots costing `-0.0028`) | `gemsdoe36-gps-graben-step-37654-…-b29b41fc-zeros.tif` (`verdict = negative`) | **NO** |

**Portfolio Recommendation:** `GEMSDOE32`'s `h33-h33-2-b2` has the portfolio's highest **OWNER-REPORTED** focus-site score (`0.2778`); no score-to-file organizer receipt is present here. It is already recorded as submitted and should not be resubmitted. Spend **`0` DrivenData slots** unless a separate selector authorizes a new candidate.

---

## 2. Metric and evidence audit: why sparse H19-5 descendants may score better, and what is not identifiable from the public record

### 2.1 Exact Distance-Weighted Tversky (`DTI`) Algebra
With $\alpha = 0.2$, $\beta = 0.8$, 300 m (`R = 3 px`) triangular kernel $K(u) = \max(0, 1 - u/3)$, known-catalogue pixels masked before scoring ([staff post #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)), and binary dots $P \in \{0, 1\}$ ($|P| = N$):

$$\text{DTI} = \frac{T}{T + 0.2\,FP + 0.8\,FN} = \frac{T}{0.2(T + S - M) + 0.8|G|},$$

where $T=TP_w$, $S=\sum_x p(x)$, $M=\sum_x p(x)\max_{g\in G}K(d(x,g))$, and $FN=|G|-T$. This is the identity implemented in `src/gems32/metric.py`; the expression $0.8T+0.2|P|+0.8|G|$ used in some earlier summaries is **not** algebraically equivalent and is withdrawn.

The isolated-pixel break-even is $k>0.2\,DTI$ only when the added unit prediction raises an otherwise-uncovered truth pixel by its full kernel credit $k$. At `DTI = 0.2778`, that idealized bar is **0.05556**. For arbitrary additions to a partially covered field, no single `k` threshold suffices: compute actual marginal $\Delta TP_w, \Delta FP_w, \Delta FN_w$ and test $\Delta TP_w D > TP_w(\Delta TP_w+0.2\Delta FP_w+0.8\Delta FN_w)$. This distinction is unit-tested in `tests/test_metric.py`.

The exact hidden truth mass and weighted true-positive totals are unavailable here. Do not infer a unique recall or predict a leaderboard score from the historical score ladder alone.

### 2.2 Reported `B`-pruning sequence (scores are OWNER-REPORT)
The supplied submission records give this nested sequence: solid H19-5 (`121,131` positive cells; `0.1922`), D2.8 thinning (`44,090`; `0.2600`), B=1 solo (`40,199`; `0.2708`), then B=2 H33 (`37,654`; `0.2778`). The files are described in the registry as nested/related, and B=2 removes a further `2,545` pixels from the B=1 mask at catalogue distances of `1–2` pixels. Taken at face value, this is consistent with trimming low-credit predictions around known faults that are excluded from scoring. It is not causal proof: the hidden fault truth and score receipts linking the submitted bytes are unavailable in this checkout. No hidden TP/recall totals are inferred here.
### 2.3 What the historical scores can and cannot establish
The owner-reported score ladder and pixel-set nesting support a plausible metric mechanism: thinning can reduce false-positive mass while preserving much of a field's coverage. They do **not** reveal private truth mass, weighted TP, false positives, or recall, and therefore cannot establish an algebraic score ceiling for every subset of `H19-5` or exact TP requirements for `0.3195` / today's leaderboard leader. Earlier versions of this section reported TP/recall estimates using a denominator simplification that was not equivalent to the published metric; those estimates are withdrawn. The live leaderboard is time-varying; see the timestamped official-page capture at [`evidence/live_leaderboard_snapshot_20261026.json`](evidence/live_leaderboard_snapshot_20261026.json).
---

## 3. Pre-Registered Round-6 Geological Hypotheses (`H36-1` .. `H36-5`) & 3-Experiment Results

Full pre-registration: [`docs/research/hypotheses-round6-20261026.md`](docs/research/hypotheses-round6-20261026.md). During pre-implementation band forensics we uncovered and fixed:
- **`IR-32-BAND-02`:** Band 6 (`tc`) is **Airborne Radiometric Total Count** ($\rho = +0.99942$ with $0.41\,\text{K} + 0.48\,\text{eTh} + 0.21\,\text{eU}$), NOT gravity Terrain Correction!
- **`IR-32-BAND-03`:** Band 17 (`iso_grav_anom_slope`) is $|\nabla_h g_{\text{iso}}| \ge 0$, whereas Band 18 (`iso_grav_anom_hg`) is signed $\partial g_{\text{iso}}/\partial x$ (`[-2.21, +1.93]`).
- **`IR-32-INSTR-03` (FIXED in `src/gems32/holdout.py`):** Upgraded shared evaluator to `GEMSDOE32-HOLDOUT-v3-visible-gated` (`22,232` withheld positives), deriving `B`-gates solely from visible faults per fold and restoring exact monotonic concordance with the live B-ladder (`0.06879 < 0.09674 < 0.09898 < 0.09920`).

| Rank | ID | Hypothesis & Layers | Status |
|---|---|---|---|
| **#1** | **`H36-1`** | **True Potential-Field Tilt-Angle Zero-Contour + Piedmont Drainage-Scarp Co-Alignment (`TDR-PDS`)** (`tmi_vg`, `tmi_hg`, `tmi`, `iso_grav_anom_vg`, `iso_grav_anom_slope`, `iso_grav_anom_hg`, `dem`, `lidar_3dep_1m_scarps`) | **Executed (`H36-1A/B/C`) — Negative (`DO NOT SUBMIT`)** |
| **#2** | **`H36-2`** | **Anisotropic Potential-Field Horizontal-Gradient Curvature Tensor** (`iso_grav_anom_slope`, `tmi_hg`, `dem`, `2m_temp`) | Registered (untried; next priority) |
| **#3** | **`H36-3`** | **Hydrothermal Demagnetization Trough + K/eTh Alteration Halo** (`tmi`, `tmi_rtp`, `k`, `eth`, `eu`, `tc`, `tgt_geotherm`) | Registered (untried) |
| **#4** | **`H36-4`** | **Half-Graben Accommodation-Zone Polarity-Reversal Saddle Detector** (`iso_grav_anom_hg`, `iso_grav_anom_slope`, `dem`) | Registered (untried) |
| **#5** | **`H36-5`** | **Sentinel-1 InSAR Phase-Gradient & UNR Magnetotelluric Boundaries** (ASF ARIA/OPERA + ScienceBase MT) | Data-blocked in sandbox (`sciencebase.gov` / `asf.alaska.edu` unreachable) |

### 3-Experiment Execution Summary (`GEMSDOE32-HOLDOUT-v3-visible-gated`, `22,232` withheld positives, `B=2`, `37,654` dots)

| Arm | `HOLDOUT-DTI` (`v3-vis`, 95% CI) | Censored `d0==0` Control | Off-Catalogue USGS SGMC (`62,703` pos, 95% CI) | SGMC Calibrated |
|---|---|---|---|---|
| **Baseline: `0.2778` Champion (`h33-h33-2-b2`)** | `0.09920` `[0.08202, 0.12219]` | `0.09920` | `0.09606` `[0.08482, 0.10773]` | `0.06412` |
| **Exp 1 — `H36-1A` (Unsupervised Multi-Physics Crest)** | `0.06380` `[0.04994, 0.07726]` | `0.04336` | `0.16421` | `0.11054` |
| **Exp 2 — `H36-1B` (500 m Halo-Excluded PU HistGB + Steger)** | `0.10482` `[0.09502, 0.11770]` | `0.07410` | `0.06832` | `0.04542` |
| **Exp 3 — `H36-1C` (Geometric-Mean Hybrid + Steger Crest)** | **`0.10982`** `[0.09866, 0.12275]` | `0.07639` | `0.08380` `[0.06079, 0.10993]` | `0.05585` |


### 3B. Parallel Multi-Physics Suite (`H38-G1..H38-G4`, 53 Channels: Nearest-Filled Base35 + 1m 3DEP LiDAR + GeoDAWN K/Th/U/TMI_up150 + GDR `#1391`)

Shared template repairs in `src/gems32/features.py` (`_fill_nearest` eliminating footprint-border `-3.4e38` sentinel cliffs; `scripts/build_features.py` aligned to exact `5,167,373`-px `sample_submission.tif` footprint), `scripts/evaluate_holdout.py`, and `scripts/submission_writer.py`, plus `scripts/run_h38_geothermal_experiments.py` (`evidence/h38_geothermal_experiments.json`, `evidence/h38_run_card.json`, `evidence/nine_site_executive_audit_20261026.json`):
- **53-Channel Single-Feature Leakage Canary:** PASS (`worst AUC = 0.62350` on `coherence_s2 <= 0.90`).
- **LiDAR Survey-Selection Bias (`IR-32-LIDAR-01`):** 1 m 3DEP LiDAR covers `75.37%` of the Nevada footprint (`labels.tif` `1.26×` denser inside; off-catalogue `SGMC` `1.61×` denser outside).
- **Official Reference U-Net Inspection (`IR-32-REFNB-01`):** `drivendataorg/gems-prize-reference-solution` (`aebe92f7c8`) Cell 12 skips every `128×128` tile with `labels == 0` (leaving blind basins `0.0` at inference) while Cell 19 writes `0.0` outside footprint (`nodata=None`), motivating Rank-4 GPU roadmap **`H38-G4`** (full-footprint 53-channel 2D Tversky U-Net/SegFormer + `B=2` + 300 m CELF).
- **3-Experiment Progression (`GEMSDOE32-HIDE-RECOVER-v3.0`, `22,232` withheld positives, `37,654` dots):**
  1. `EXP1_H38_BASE35` (repaired 35ch OOF HistGB + `B=2` + 300 m CELF): `HOLDOUT-DTI = 0.09968 [0.08253, 0.11627]`, `SGMC_cal = 0.05371`
  2. `EXP2_H38_G1_MULTIPHYS` (53ch LiDAR + GeoDAWN + GDR): `HOLDOUT-DTI = 0.10687 [0.08950, 0.12280]`, `SGMC_cal = 0.04991`
  3. **`EXP3_H38_G1_CORROB`** (53ch + `IR-32-LIDAR-01` quantile routing + structural corroboration): **`HOLDOUT-DTI = 0.11696 [0.10053, 0.13204]`** (`+17.9%` over Champion `0.09920`), `SGMC_cal = 0.05037` -> **`DO NOT SUBMIT`** (`verdict = negative`).

---

## 4. Portal Error `"Predicted values must be in range [0, 1]"` — Root Cause & Verified Fix

1. **`float32` Sentinel Leakage:** `training_features.tif` encodes nodata as `-3.4028235e+38`, including **`3,061` pixels inside the active submission footprint**. Propagating un-sanitized bands leaks `-3.4e38` into `[0, 1]`.
2. **Whole-Raster Strict Validation:** `src/gems32/submission.py` + `src/gemsdoe32/submission.py` write primary `-zeros.tif` files with `nodata=None`, `float32`, `EPSG:32611`, `3730×3292`, clamping and verifying **all `12,279,160` cells finite in `[0.0, 1.0]` with `0` NaNs anywhere on disk**.

---

## 5. Autonomous Local Validation & Reproduction

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

# Unit, format, hygiene, repaired v3 holdout, and site-integrity suite
python -m pytest tests -q

# Optional full data restore + H36-1C rebuild + site regeneration
python scripts/restore_data.py
python scripts/prepare_data.py
python scripts/run_h36_tdr_pds_pipeline.py
python scripts/audit_shipped.py
python scripts/audit_release_protocol.py
python scripts/build_site.py
```

---

## 6. Official Trusted Sources & References

- **DOE GEMS Prize Overview:** <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- **Problem Description & Metric (`α=0.2, β=0.8`, 300 m kernel, `[0, 1]` range):** <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- **Official Public Leaderboard:** <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>
- **Official DOE/NLR Rules PDF:** <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- **Organizer Reference Solution:** <https://github.com/drivendataorg/gems-prize-reference-solution>
- **USGS GeoDAWN Airborne Survey:** <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
- **INGENIOUS Great Basin Data Record (#1391):** <https://gdr.openei.org/submissions/1391>
- **DrivenData Staff Clarifications:** [Known faults masked (#11516)](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) · [New fault definition (#11536)](https://community.drivendata.org/raw/11536) · [Pooled public score (#11550)](https://community.drivendata.org/raw/11550) · [Weekly cap (#11553)](https://community.drivendata.org/raw/11553) · [Test sources withheld (#11527)](https://community.drivendata.org/raw/11527) · [Same metric in all rounds (#11556)](https://community.drivendata.org/raw/11556)
- **Coordinate System (`EPSG:32611`):** <https://epsg.io/32611> · **Tversky Index:** <https://en.wikipedia.org/wiki/Tversky_index>

---

## 7. Arena8a Session (`2026-10-26`): Multi-Domain Ridge-Crest Concordance (`A8A-H1..H5`) & PU Suppression Discovery (`IR-A8A-PU-BIAS-01`)

![Arena8a MDRC 4-Panel Validation Diagnostic](docs/assets/fig_arena8a_mdrc.png)

- **Pre-registration & 5 Ranked Geological Hypotheses (`A8A-H1..A8A-H5`):** [`docs/research/arena8a-preregistration-and-hypotheses.md`](docs/research/arena8a-preregistration-and-hypotheses.md) (`A8A-H1` MDRC 4-domain crest concordance; `A8A-H2` Salem 2007 RTP tilt-depth intrabasinal horst edges; `A8A-H3` `K/Th` + RTP mag-low + `cond_surf` clay-cap breach; `A8A-H4` 1 m LiDAR relay-ramp strain tensor; `A8A-H5` [USGS ComCat API](https://earthquake.usgs.gov/fdsnws/event/1/) + [2020 M6.5 Monte Cristo Surface Rupture](https://www.sciencebase.gov/catalog/item/606f657fd34ef99870188ee5), `DATA-BLOCKED` in sandbox).
- **Experimental Receipts (`EXP1..EXP3`, `GEMSDOE32-HOLDOUT-v3-visible-only`, `22,232` withheld positives):**
  - **EXP1 (Label-Free Domain Physics, `0` labels):** `D1_LiDAR_Dipole` (`SGMC-cal = 0.10267`) and `MDRC_Unsup_4Domain` (`SGMC-cal = 0.07651`) **both beat `0.2778` Champion (`0.06412`) on off-catalogue USGS SGMC faults**, while `57/57` channels pass the leakage canary (`max AUC = 0.6217 <= 0.90`).
  - **EXP2 (4-Quadrant OOF HistGB):** Adding the 22 MDRC channels improves held-out quadrant AUC in `4/4` folds (`+0.0042` to `+0.0207`).
  - **EXP3 (1-px Ridge-Crest Sharpening + Credit-Bar Submodular Emission, `B=2`, `44,090` dots):** Wins **`HOLDOUT-DTI = 0.10679 [0.08765, 0.12850]`** vs `CTRL-35ch` (`0.09893`) and `D2.8 vis-B2` (`0.09920`, winning `7/8` spatial-draw cells, paired Δ 95% CI `[+0.0040, +0.0111]`), while supervised `y=0` training on `~labels` suppresses pre-Quaternary `SGMC` faults (`0.05509 < 0.06412`, `IR-A8A-PU-BIAS-01`). **Concrete next step:** Positive-Unlabeled (`PU`, Elkan–Noto / anchor-set) training on the 57-channel `MDRC` stack.
- **Standalone Zero-Human-Intervention Verifier:** `.venv/bin/python scripts/verify_arena8a_submission.py` · Run Card: [`evidence/arena8a_run_card.json`](evidence/arena8a_run_card.json).

---

<details>
<summary><b>Standing Competition Brief & Parallel-Run Protocol (preserved for auditability)</b></summary>

**Session-start rule:** read this standing brief and [`docs/research/standing-prompt-as-recorded-20261026.md`](docs/research/standing-prompt-as-recorded-20261026.md) before every project session; that file records the longer supplied prompt and documents its completeness caveat. The single-method lane paragraph is currently absent from the prompt context, so do not infer a lane or start a new experiment until explicitly specified. This is a live operational summary, not a claim that the archived transcript is complete.

> Review this project and other GEMSDOE projects focusing on 24, 25, 27, 28, 30, 31, 32, 33, 36. Provide a clear executive summary of the highest submissions and make it very clear and obvious which submission is best to submit for a high score on the leaderboard and whether it is unique or a duplicate of another submission.
>
> Maximize P(Win): Weigh tradeoffs and risk and choose the path that maximizes the probability of winning. Always put the outcome first!
> Own the Outcome: Own results end to end, from initial action to final result. Step up and take action when problems arise. Treat both failure and success as signals to learn and adapt. Stay accountable until the final outcome is achieved.
>
> Fix submission error: "Predicted values must be in range [0, 1]". Validate without human intervention, enforce Parallel-Run Protocol uniqueness (`Spearman <= 0.90` on surface and `<= 70%` within 3 px on final dots), single-feature leakage canary (`AUC <= 0.90`), `HOLDOUT-DTI` / `ORGANIZER-CONFIRMED` only for receipt-backed scores; otherwise label group claims `OWNER-REPORT`, budget cap (`<= 3` experiments or 2 hours), JSON Run Card, 3 review passes, and PR merge onto `main`. See [`docs/research/standing-prompt-as-recorded-20261026.md`](docs/research/standing-prompt-as-recorded-20261026.md) and [`docs/research/standing-brief-20261025.md`](docs/research/standing-brief-20261025.md).

</details>
