# GEMSDOE32 — DOE GEMS Prize Research, Validation & Submission System

<!-- SINGLE DECISION: rendered from registry/current_status.json and evidence/current_release_review.json (both must authorize; fail closed). Update those files, never add a second banner. -->
## 🚦 Current Decision — 2026-10-26 01:45 UTC

# 🔴 DO NOT SUBMIT — no upload is authorized (`DOWNLOAD FOR RESEARCH / AUDIT: YES · SUBMIT TO LIVE PORTAL: NO`)

| Artifact | Status | Evidence & Automated Validation Summary |
|---|---|---|
| **Newest unique file (`H36-1C` TDR-PDS + Steger Crest)**<br>[`gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif) (`206,761 B`) · [`.zip`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.zip) (`171,140 B`) · [`-nan.tif`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-nan.tif) · [`audit.json`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-audit.json) · [`Run Card`](evidence/h36_tdr_pds_run_card.json) | 🔴 **DO NOT SUBMIT — audit/research artifact (`verdict = negative`)** | SHA-256 `f75ac7ae172eed0840b948beaa6587a532c0a44453c3ad90874f02967e0a887c`. Validated 100% without human intervention: `EPSG:32611`, `3730×3292` `float32`, `nodata=None`, all `12,279,160` cells finite in `[0.0, 1.0]`, `0` NaNs (prevents `"Predicted values must be in range [0, 1]"`), `37,654` dots (`0` on catalogue; `83.84%` off-`H19-5`). Leakage canary PASS (`46/46` channels, `max AUC = 0.58412 <= 0.90`). Genuine uniqueness PASS across all 44 genuine detector rasters (`max |Spearman| = 0.1595 <= 0.90`; `max 3-px overlap = 60.44% <= 70%`; `52.20%` vs `0.2778` Champion). Achieves **`HOLDOUT-DTI = 0.10982` `[0.09866, 0.12275]`** on repaired `GEMSDOE32-HOLDOUT-v3-visible-gated` (`22,232` withheld positives; vs raw Champion `0.09920`), **but fails closed** because censorship-matched `d0==0` control is `0.07639 < 0.09920`, off-catalogue USGS SGMC blind-fault DTI is `0.08380` `[0.06079, 0.10993] < 0.09606`, and literal 5-px calibration-lattice overlap is `99.80% > 70%` (`IR-32-LATTICE-01`). Archive name: `GEMSDOE32-H36-1C-TDR-PDS-9FF9D6E2` · Note (`118/140` chars): `H36-1C TDR-PDS+Steger 37654d \| HOLDOUT-DTI 0.1098 [0.0987,0.1227] v3-vis 22232pos \| SGMC 0.0838<0.0961 \| DO NOT SUBMIT`. |
| **Archived Round-6 candidate (`R6-1`)**<br>[`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif) · SHA-256 `c7f094c1…eae56547` | 🔴 **DO NOT SUBMIT — audit artifact only** | Real, uniquely named, format-valid GeoTIFF (`docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`). **Format validity is not enough to authorize a competition upload.** Fail-closed release review ([protocol audit](docs/research/protocol-review-20261026.md), [decision](evidence/current_release_review.json)) found non-fold-local B=2 masking and noted that SGMC-tracing files score `0.65 / 0.56` locally yet `0.0492 / 0.0512` live (`IR-42-INSTR-02`, [counter-examples](evidence/sgmc_instrument_live_counterexamples.json)). |
| **Best scored file (`GEMSDOE32` Champion)**<br>[`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | **Already submitted — do NOT resubmit** | **`0.2778`** (`OWNER-REPORT` / organizer-scored submission receipt; `37,654` dots; SHA-256 `c55bafc4…7ab6fa9`). Highest verified score across all 9 focus sites; resubmitting wastes a weekly slot. |
| **Withdrawn / superseded (`H42-1`, `h32-winning-46090`, `h-geo-conduit`)** | 🔴 **DO NOT SUBMIT** | `H42-1` (`b91008fa`): `81.9%` within 3 px of `GEMSDOE25` `h38-greedy-credit` (`> 70%`) and `0.0545 < random 0.0709` on off-catalogue SGMC (`IR-42-INSTR-01`). `h32-winning-46090` (`c3459dcd`): `84.0%` champion-family variant (`IR-42-README-01`). `h-geo-conduit` (`2d0d0c5e`): `70.24%` overlap vs `GEMSDOE28` (`IR-R6-02` / `IR-32-CONDUIT-01`). |

- **GitHub Pages Landing & Executive Summary:** [`docs/index.html`](docs/index.html) · [`docs/executive-summary.html`](docs/executive-summary.html) (exact portal upload procedure for when a future candidate clears every gate; use `-zeros.tif` so `"Predicted values must be in range [0, 1]"` can never occur).
- **Official Public Leaderboard:** `#1 = 0.4413` (`xiaofanhu`), verified on the [DrivenData Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). Weekly cap: governed by the authenticated submission screen ([staff clarification #11553](https://community.drivendata.org/raw/11553)).

---

## Arena Core Values

- **Maximize P(Win):** Weigh tradeoffs and risk and choose the path that maximizes the probability of winning. Always put the outcome first! Every weekly DrivenData submission slot is scarce information-bearing capital — never spend a live slot on a duplicate, unvalidated, or holdout-inferior raster.
- **Own the Outcome:** Own results end to end, from initial action to final result. Step up and take action when problems arise. Treat both failure and success as signals to learn and adapt. Stay accountable until the final outcome is achieved — including repairing shared broken evaluation instruments (`IR-32-INSTR-03` fixed in `src/gems32/holdout.py`), auditing band misidentifications (`IR-32-BAND-02`, `IR-32-BAND-03`), and reporting negative results honestly.

---

## 1. Executive Summary Across the 9 Focus Sites (`GEMSDOE24` .. `GEMSDOE36`)

Every historical live score below is labelled **`OWNER-REPORT`** (recorded from owner submission logs; no cryptographic organizer receipt links raw `.tif` bytes to a live score — `IR-32-SCORE-01`). Notice also **`IR-32-SCORE-03`**: `0.3195` is the portfolio's internal aspirational target (`0.2778` is the highest verified score across all 9 focus sites; public leaderboard `#1` is `0.4413` by `xiaofanhu`).

| Site & GitHub Repo | Verified `2026-10-26` `HEAD` | Best Historical Scored Submission (`OWNER-REPORT`) | Unique vs. Duplicate / Lineage Forensics | Latest `2026-10-26` Unique TIF & Gate Verdict | Submit Today? |
|---|---|---|---|---|---|
| **[GEMSDOE24](https://github.com/buffedlizard55-lab/GEMSDOE24)** | `2a2b9829` | `0.2477` (`h25-1-dotted-h19-5-d1-5`, `60,069`d) / `0.2194` (`h24-1-tip-relay`) | `d1-5` is superseded denser `H19-5` parent; `h24-1` is unique tip/relay below `0.2778` | `gemsdoe24-crp1-dipfan-stepover-37654-…-7764b339-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE25](https://github.com/buffedlizard55-lab/GEMSDOE25)** | `de77cb6c` | `0.2600` (`dotted-h19-5-d2-8-…-e56ea318af89`, `44,090`d) | **Dot-identical (`44,090 / 44,090`) to `GEMSDOE30`**; unpruned parent of `0.2778` | `h44` multi-physics lane (`verdict = negative`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE27](https://github.com/buffedlizard55-lab/GEMSDOE27)** | `398cda94` | `0.2449` (`topo-gap-closure-on-d1-5`) / `0.2190` (`H29-S`) | Gap-closure on `d1.5` hurt (`-0.0028`); `H29-S` unique below `0.2778` | `gems27-h31-range-front-step-50k-…-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE28](https://github.com/buffedlizard55-lab/GEMSDOE28)** | `94152be6` | `0.2710` (`h36-1-rung30`) / `0.2708` (`solo-8acb75e1`, `40,199`d) | **`0.2708` is dot-identical (`40,199 / 40,199`) to `GEMSDOE31`**; `B=1` parent of `0.2778` | `gems28-s20-asymmetric-hanging-wall-37654-…-8635a2a3-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE30](https://github.com/buffedlizard55-lab/GEMSDOE30)** | `ac54b7f3` | `0.2600` (`d28-poisson300m-offcat-44090`) | **100% pixel-identical duplicate of `GEMSDOE25`** (`0.2600 == 0.2600`) | `gemsdoe30-PTA1-piedmont-thermal-37654-…-669abcb3-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE31](https://github.com/buffedlizard55-lab/GEMSDOE31)** | `6ca63b0c` | `0.2708` (`h27-4-solo-d28-8acb75e1`, `40,199`d) | **100% pixel-identical duplicate of `GEMSDOE28`** (`40,199` dots) | `gemsdoe31-xfcoh31-37654-…-c00c6405-zeros.tif` (`verdict = negative`) | **NO** |
| **[GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32)** | *(current)* | **`0.2778` (`h33-h33-2-b2-…-e5eb6e7e`, `37,654`d) — PORTFOLIO CHAMPION** | **Unique optimal `B=2` endpoint** (`solo` minus `2,545` `1 < d_cat <= 2 px` flank dots); **already scored — do not resubmit** | `gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif` (`verdict = negative`, audit/research only) | **NO (`0.2778` already live)** |
| **[GEMSDOE33](https://github.com/buffedlizard55-lab/GEMSDOE33)** | `7deca206` | `0.2632` (`h33d-analog-tip-stepover-r30`, `50,023`d) | Unique analog tip/step-over geometry, `0.0146` below `0.2778` | Latest `2026-10-26` lane (`verdict = negative`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE36](https://github.com/buffedlizard55-lab/GEMSDOE36)** | `a4c660a8` | `0.2750` (`anderson-geothermal-pinn-38854`, `38,854`d) | **96.9% superset duplicate of `GEMSDOE32` Champion** (`37,654` Champion dots + `1,200` extra dots costing `-0.0028`) | `gemsdoe36-gps-graben-step-37654-…-b29b41fc-zeros.tif` (`verdict = negative`) | **NO** |

**Portfolio Recommendation:** **`GEMSDOE32`'s `h33-h33-2-b2` (`0.2778`)** already holds the portfolio's highest live score. Spend **`0` DrivenData submission slots today** across all 9 sites.

---

## 2. PhD-Level Forensic Proof: Why `h33-h33-2-b2` Scored `0.2778` — and What `0.3195` & `0.4413` Require

### 2.1 Exact Distance-Weighted Tversky (`DTI`) Algebra
With $\alpha = 0.2$, $\beta = 0.8$, 300 m (`R = 3 px`) triangular kernel $K(u) = \max(0, 1 - u/3)$, known-catalogue pixels masked before scoring ([staff post #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)), and binary dots $P \in \{0, 1\}$ ($|P| = N$):

$$\text{DTI}(P, G) = \frac{T}{0.8\,T + 0.2\,N + 0.8\,|G|}, \qquad T = \sum_{g \in G} \max_{p \in P} K(\|g - p\|_2) \le |G|.$$

From the 5-px blind calibration lattice (`13gems r13-lattice-s5`, `206,895` dots, live `0.0904`) and the 4-point `H19-5` nested ladder, hidden off-catalogue ground truth in NW Nevada has **`|G| ≈ 12,265` pixels** (~`0.24%` of the `5,167,373`-pixel footprint). Differentiating $\text{DTI}(T, N)$ gives the exact marginal break-even credit per added dot:

$$\frac{\partial\,\text{DTI}}{\partial N} > 0 \iff \Delta T > \frac{0.2\,\text{DTI}}{1 - 0.8\,\text{DTI}}.$$

At $\text{DTI} = 0.2778$, each extra dot must add **$\Delta T > 0.0714$** weighted truth pixels just to break even!

### 2.2 The 4-Step `B`-Pruning Ladder (`0.1922 -> 0.2600 -> 0.2708 -> 0.2778`)
1. **Solid `H19-5` (`121,131` px -> `0.1922`):** $T_{\text{solid}} \approx 5,021$ (`40.9%` of $|G|$), crushed by $0.2 \times 121,131 = 24,226$ denominator mass.
2. **`d2.8` Poisson Disk (`44,090` dots -> `0.2600`):** 2.8-px spacing preserves `~90.6%` of 300 m kernel coverage ($T \approx 4,552$) while slashing $0.2 N$ by `63.6%`.
3. **`Solo` (`40,199` dots -> `0.2708`):** Drops `3,891` `d_cat == 1 px` immediate catalogue neighbors ($T \approx 4,522$).
4. **Champion `h33-h33-2-b2` (`37,654` dots -> `0.2778`):** Removes the **`2,545` flank dots at $1 < d_{\text{cat}} \le 2\text{ px}$ (`100–200 m`)**, losing only $\Delta T \approx 19$ (`0.0075/dot`, `10×` below the `0.0714` break-even bar!) because `existing_faults.tif` already occupies the fault core. At $B=3$, repaired `v3` holdout rolls over (`0.09644 < 0.09920`) because genuine branch splays and relay ramps begin at `200–300 m`.

### 2.3 Algebraic Impossibility of Reaching `0.3195` or `0.4413` from `H19-5` Subsets
Because $T(P) \le T_{\text{solid}} \approx 5,021$ for EVERY subset $P \subseteq \text{H19-5}$:
- Even an oracle keeping `28,000` dots with zero recall loss caps around `~0.305–0.312`.
- Reaching **`0.3195`** at `37,654` dots requires **$T \approx 5,430 > 5,021$** (`+20.6%` more recall than the Champion).
- Reaching **`0.4413`** (`#1 xiaofanhu`) at `37,654` dots requires **$T \approx 8,408$ (`68.6%` of $|G|$)** — `~3,905` additional hidden-fault pixels beneath blind Quaternary basins where `H19-5` placed zero predictions.

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

<details>
<summary><b>Standing Competition Brief & Parallel-Run Protocol (preserved for auditability)</b></summary>

> Review this project and other GEMSDOE projects focusing on 24, 25, 27, 28, 30, 31, 32, 33, 36. Provide a clear executive summary of the highest submissions and make it very clear and obvious which submission is best to submit for a high score on the leaderboard and whether it is unique or a duplicate of another submission.
>
> Maximize P(Win): Weigh tradeoffs and risk and choose the path that maximizes the probability of winning. Always put the outcome first!
> Own the Outcome: Own results end to end, from initial action to final result. Step up and take action when problems arise. Treat both failure and success as signals to learn and adapt. Stay accountable until the final outcome is achieved.
>
> Fix submission error: "Predicted values must be in range [0, 1]". Validate without human intervention, enforce Parallel-Run Protocol uniqueness (`Spearman <= 0.90` on surface and `<= 70%` within 3 px on final dots), single-feature leakage canary (`AUC <= 0.90`), `HOLDOUT-DTI` vs `ORGANIZER-CONFIRMED` provenance labels, budget cap (`<= 3` experiments or 2 hours), JSON Run Card, 3 review passes, and PR merge onto `main`. See [`docs/research/standing-prompt-as-recorded-20261026.md`](docs/research/standing-prompt-as-recorded-20261026.md) and [`docs/research/standing-brief-20261025.md`](docs/research/standing-brief-20261025.md).

</details>
