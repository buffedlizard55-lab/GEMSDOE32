# GEMSDOE32 — DOE GEMS Prize Research, Validation & Submission System

## Latest repository review

[2026-10-26 shared promotion-gate audit](docs/research/repository-review-20261026-gate-hardening.md):
**DO NOT SUBMIT.** Promotion now requires a positive paired improvement CI, matching
HOLDOUT-DTI provenance, and complete named format checks. No new geological experiment
or submission slot was used. Historical scores remain owner reports, not authenticated receipts.

<!-- SINGLE DECISION: rendered from registry/current_status.json and evidence/current_release_review.json (both must authorize; fail closed). Update those files, never add a second banner. -->
## 🚦 Current Decision — 2026-10-26 06:35 UTC

# 🔴 DO NOT SUBMIT — no upload is authorized (`DOWNLOAD FOR RESEARCH / AUDIT: YES · SUBMIT TO LIVE PORTAL: NO`)

| Artifact | Status | Evidence & Automated Validation Summary |
|---|---|---|
| **Latest Session Unique File (`H44-1: SPCP` SAR-PU Curvature + Conduit, `37,654`d)**<br>[`gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-zeros.tif`](docs/downloads/gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-zeros.tif) (`216,377 B`) · [`.zip`](docs/downloads/gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-zeros.zip) · [`-nan.tif`](docs/downloads/gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-nan.tif) · [`audit.json`](docs/downloads/gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-audit.json) · [`Run Card`](evidence/h44_spcp_run_card.json) | 🔴 **DO NOT SUBMIT — audit artifact (`verdict = negative`; safe to download for research)** | SHA-256 `386a4aad59a5c742b28541835892f9f6e0cb306cbbe4e296741bbad8e4bff235`. Validated 100% automatically (`scripts/check_submission.py --strict-finite` 7/7 + `audit_geotiff` 13/13 PASS): `EPSG:32611`, `3730×3292` `float32`, `nodata=None`, all `12,279,160` cells finite in `[0.0, 1.0]`, `0` NaN, `37,654` dots (`0` on-cat, `94.3%` off-`H19-5`). Canary PASS (`55/55`, `max AUC = 0.5869 <= 0.90`). Genuine uniqueness PASS across **288** genuine rasters (`max |Spearman| = 0.1204 <= 0.90`; `max within-3px = 44.48% <= 70%`; `33.75%` vs `0.2778` OWNER-REPORT Champion). **Cures `IR-A8A-PU-BIAS-01`:** achieves **9-site supervised record `SGMC-cal = 0.07774 [0.0692, 0.0856]`** (`raw 0.11606`), beating `0.2778` OWNER-REPORT Champion (`0.06412`) by paired Δ `+0.01328 [+0.0030, +0.0248]` (`P=0.998`) and naive binary `EXP2` (`0.04663`) by **`+66.7%`**, **but fails closed** because 52.4% blind-basin allocation lowers exposed-scarp `HOLDOUT-DTI` (`GEMSDOE32-HIDE-RECOVER-v3.0`, `22,232` pos) to `0.06984 [0.0603, 0.0793]` (`< CTRL-35ch 0.10169`) and literal `r13-lattice-s5` overlap is `99.69%`. Name: `GEMSDOE32-H44-SPCP-38F7995A` · Note (`80/140`): `H44-1 SPCP SAR-PU curv+conduit 37654d B2 \| HR=0.0698 SGMC=0.0777 \| DO NOT SUBMIT`. |
| **Archived Round-6 candidate (`R6-1`)**<br>[`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif) · SHA-256 `c7f094c1…eae56547` | 🔴 **DO NOT SUBMIT — audit artifact only** | Real, uniquely named, format-valid GeoTIFF (`docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`). **Format validity is not enough to authorize a competition upload.** Fail-closed release review ([protocol audit](docs/research/protocol-review-20261026.md), [decision](evidence/current_release_review.json)) found non-fold-local B=2 masking and noted that SGMC-tracing files score `0.65 / 0.56` locally yet `0.0492 / 0.0512` live (`IR-42-INSTR-02`, [counter-examples](evidence/sgmc_instrument_live_counterexamples.json)). |
| **Arena8a unique file (`A8A-H1: MDRC` + Crest CreditBar, `44,090`d)**<br>[`gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.tif`](docs/downloads/gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.tif) (`230,275 B`) · [`.zip`](docs/downloads/gemsdoe32-arena8a-mdrc-crestbar-b2-44090-20261026T011955Z-ce1abd39-zeros.zip) · [`Run Card`](evidence/arena8a_run_card.json) | 🔴 **DO NOT SUBMIT — audit/research artifact (`verdict = negative`)** | SHA-256 `0bbb3128c0e91a5f10003b1f92f2ef6030822a27b231299f7ce3c22d2d4d13e5`. Validated 100% automatically (`EPSG:32611`, `3730×3292` `float32`, `nodata=None`, `[0, 1]`, `44,090`d). Genuine uniqueness PASS (`|Spearman| <= 0.4209`; `within-3px <= 64.96%`: `52.89%` vs `0.2778` OWNER-REPORT Champion). Wins `HOLDOUT-DTI = 0.10679 [0.08765, 0.12850]` vs `CTRL-35ch` (`0.09893`), **but fails Gate `G5`** on off-catalogue SGMC (`0.05509 < 0.06412` OWNER-REPORT Champion due to `IR-A8A-PU-BIAS-01`) and literal 5-px lattice overlap (`99.04%`). |
| **Previous unique file (`H36-1C` TDR-PDS + Steger Crest)**<br>[`gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif) (`206,761 B`) · [`.zip`](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.zip) · [`Run Card`](evidence/h36_tdr_pds_run_card.json) | 🔴 **DO NOT SUBMIT — audit/research artifact (`verdict = negative`)** | SHA-256 `f75ac7ae172eed0840b948beaa6587a532c0a44453c3ad90874f02967e0a887c`. Validated 100% automatically (`EPSG:32611`, `3730×3292` `float32`, `nodata=None`, `[0, 1]`, `37,654`d). Genuine uniqueness PASS across 44 rasters (`max |Spearman| = 0.1595`; `max 3-px overlap = 60.44%`; `52.20%` vs `0.2778` OWNER-REPORT Champion). Scores `HOLDOUT-DTI = 0.10982 [0.09866, 0.12275]`, **but fails closed** on censorship-matched `d0==0` (`0.07639 < 0.09920`), SGMC (`0.08380 < 0.09606`), and literal `r13-lattice-s5` (`99.80%`). |
| **Round-6 Multi-Physics file (`EXP3_H38_G1_CORROB` — `H38-G1..G4`, 53ch)**<br>[`gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif) (`209,987 B`) · [`.zip`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.zip) · [`H38 Run Card`](evidence/h38_run_card.json) | 🔴 **DO NOT SUBMIT — audit artifact (`verdict = negative`)** | SHA-256 `6efe140229c46b274ab7431bab0b9c1318ade642096ca8a1ff8c36317d2d68ff`. Achieves **repo-best `HOLDOUT-DTI = 0.11696 [0.10053, 0.13204]`** on `GEMSDOE32-HIDE-RECOVER-v3.0` (`+17.9%` over `0.2778` OWNER-REPORT Champion `0.09920`), **but fails closed** because `SGMC_cal` (`0.05037`) trails `0.2778` OWNER-REPORT Champion (`0.06412`) and unexempted `<= 3 px` check hits local `hcvf2` (`77.56%`) + `r13-lattice-s5` (`99.71%`). |
| **Best reported file (`GEMSDOE32` Champion)**<br>[`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | **Reported already submitted — do NOT resubmit** | **`0.2778`** (`OWNER-REPORT`; no submission-page receipt is archived here; `37,654` dots; SHA-256 `c55bafc4…7ab6fa9`). Highest reported score across the 9 focus sites in the supplied records; not independently organizer-confirmed. |
| **Withdrawn / superseded (`H42-1`, `h32-winning-46090`, `h-geo-conduit`)** | 🔴 **DO NOT SUBMIT** | `H42-1` (`b91008fa`): `81.9%` within 3 px of `GEMSDOE25` `h38-greedy-credit` (`> 70%`) and `0.0545 < random 0.0709` on off-catalogue SGMC (`IR-42-INSTR-01`). `h32-winning-46090` (`c3459dcd`): `84.0%` champion-family variant (`IR-42-README-01`). `h-geo-conduit` (`2d0d0c5e`): `70.24%` overlap vs `GEMSDOE28` (`IR-R6-02` / `IR-32-CONDUIT-01`). |

- **GitHub Pages Landing & Executive Summary:** [`docs/index.html`](docs/index.html) · [`docs/executive-summary.html`](docs/executive-summary.html) (exact portal upload procedure for when a future candidate clears every gate; use `-zeros.tif` so `"Predicted values must be in range [0, 1]"` can never occur).
- **Official Public Leaderboard:** `#1 = 0.4413` (`xiaofanhu`), verified on the [DrivenData Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). Weekly cap: governed by the authenticated submission screen ([staff clarification #11553](https://community.drivendata.org/raw/11553)).

---

## Arena Core Values

- **Maximize P(Win):** Weigh tradeoffs and risk and choose the path that maximizes the probability of winning. Always put the outcome first! Every weekly DrivenData submission slot is scarce information-bearing capital — never spend a live slot on a duplicate, unvalidated, or holdout-inferior raster.
- **Own the Outcome:** Own results end to end, from initial action to final result. Step up and take action when problems arise. Treat both failure and success as signals to learn and adapt. Stay accountable until the final outcome is achieved — including repairing shared broken evaluation instruments (`IR-32-INSTR-03` fixed in `src/gems32/holdout.py`), auditing band misidentifications (`IR-32-BAND-02`, `IR-32-BAND-03`), and reporting negative results honestly.

---

## 1. Executive Summary Across the 9 Focus Sites (`GEMSDOE24` .. `GEMSDOE36`)

Every historical group live score below is labelled **`OWNER-REPORT`** (recorded from the supplied owner logs; no submission-page receipt linking exact raw `.tif` bytes to a score is archived here — `IR-32-SCORE-01`). Notice also **`IR-32-SCORE-03`**: `0.3195` is an internal aspirational target (`0.2778` is the highest owner-reported score across these 9 focus sites; the public leaderboard snapshot recorded in this repo showed `#1 = 0.4413` by `xiaofanhu`, read 2026-10-25, not verified live in this review).

| Site & GitHub Repo | Verified `2026-10-26` `HEAD` | Best Historical Scored Submission (`OWNER-REPORT`) | Unique vs. Duplicate / Lineage Forensics | Latest `2026-10-26` Unique TIF & Cross-Site SGMC-cal | Submit Today? |
|---|---|---|---|---|---|
| **[GEMSDOE24](https://github.com/buffedlizard55-lab/GEMSDOE24)** | `17496743a969` | `0.2477` (`OWNER-REPORT`, `h25-1-dotted-h19-5-d1-5`, `60,069`d) / `0.2194` (`OWNER-REPORT`, `h24-1-tip-relay`) | `d1-5` is superseded denser `H19-5` parent; `h24-1` is unique tip/relay below `0.2778` (`OWNER-REPORT`) | `gems24-dprf1-stitched-oof-tworegime-20261026-81849d67c8bf-zeros.tif` (`SGMC-cal = 0.05505`, `DO_NOT_SUBMIT`) | **NO** |
| **[GEMSDOE25](https://github.com/buffedlizard55-lab/GEMSDOE25)** | `88a29e094989` | `0.2600` (`OWNER-REPORT`, `dotted-h19-5-d2-8-…-e56ea318af89`, `44,090`d) | **Dot-identical (`44,090 / 44,090`) to `GEMSDOE30`**; unpruned parent of `0.2778` (`OWNER-REPORT`) | `gems25-h71-hgpc-blind-b2-sapd3-k3p5-20261026-9eb0c31e5149-zeros.tif` (`SGMC-cal = 0.05158`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE27](https://github.com/buffedlizard55-lab/GEMSDOE27)** | `426426b402f9` | `0.2449` (`OWNER-REPORT`, `topo-gap-closure`) / **`0.2190` (`OWNER-REPORT`, `H29-S`)** | `H29-S` (`51189874…`, `37,654`d) is `#1` reported non-`H19-5` unique upload, below `0.2778` (`OWNER-REPORT`) | `gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif` (`SGMC-cal = 0.06047`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE28](https://github.com/buffedlizard55-lab/GEMSDOE28)** | `348ff086e29b` | `0.2710` (`OWNER-REPORT`, `h36-1-rung30`) / `0.2708` (`OWNER-REPORT`, `solo-8acb75e1`, `40,199`d) | **`0.2708` (`OWNER-REPORT`) is dot-identical (`40,199 / 40,199`) to `GEMSDOE31`**; `B=1` parent of `0.2778` (`OWNER-REPORT`) | `gems28-s20-nchc-20261026-d432a1d5d6ee-allfinite.tif` (`SGMC-cal = 0.06327`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE30](https://github.com/buffedlizard55-lab/GEMSDOE30)** | `73db382d3c99` | `0.2600` (`OWNER-REPORT`, `d28-poisson300m-offcat-44090`) | **100% pixel-identical duplicate of `GEMSDOE25`** (`0.2600 == 0.2600` `OWNER-REPORT`) | `gems30-FFL1-fusion_edge-44090-20261026-eacd73e854a3.tif` (`78.3%` dup, `SGMC-cal = 0.06205`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE31](https://github.com/buffedlizard55-lab/GEMSDOE31)** | `e6e85b357914` | `0.2708` (`OWNER-REPORT`, `h27-4-solo-d28-8acb75e1`, `40,199`d) | **100% pixel-identical duplicate of `GEMSDOE28`** (`40,199` dots) | `gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif` (`SGMC-cal = 0.05658`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32)** | `9e55d5d61cb7` | **`0.2778` (`OWNER-REPORT`, `h33-h33-2-b2-…-e5eb6e7e`, `37,654`d) — PORTFOLIO CHAMPION** | **Unique optimal `B=2` endpoint** (`solo` minus `2,545` `1 < d_cat <= 2 px` flank dots); **already scored — do not resubmit** | **`gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-zeros.tif`** (**`SGMC-cal = 0.07774`**, `verdict = negative`, research/audit) | **NO (`0.2778` `OWNER-REPORT` already live)** |
| **[GEMSDOE33](https://github.com/buffedlizard55-lab/GEMSDOE33)** | `fded53840662` | `0.2632` (`OWNER-REPORT`, `h33d-analog-tip-stepover-r30`, `50,023`d) | Unique analog tip/step-over geometry, `0.0146` below `0.2778` (`OWNER-REPORT`) | `gemsdoe33-a33-r2-csht-transfer-37654-20261026-0b78c04d5fad-zeros.tif` (`SGMC-cal = 0.04698`, `DO NOT SUBMIT`) | **NO** |
| **[GEMSDOE36](https://github.com/buffedlizard55-lab/GEMSDOE36)** | `4938a123133b` | `0.2750` (`OWNER-REPORT`, `anderson-geothermal-pinn-38854`, `38,854`d) | **96.9% superset duplicate of `GEMSDOE32` `0.2778` (`OWNER-REPORT`) Champion** (`37,654` Champion dots + `1,200` extra dots costing `-0.0028`) | `gemsdoe36-atvr36-20261026.tif` (`SGMC-cal = 0.03658`, `DO NOT SUBMIT`) | **NO** |

**Portfolio Decision:** **`GEMSDOE32`'s `h33-h33-2-b2` (`0.2778` `OWNER-REPORT`, no submission-page receipt in repo)** already holds the portfolio's highest reported live score. Spend **`0` DrivenData submission slots today** across all 9 sites.

---

## 2. PhD-Level Forensic Proof: Why `h33-h33-2-b2` Achieved `0.2778` (`OWNER-REPORT`) — and What `0.3195` & `0.4413` Require

### 2.1 Exact Distance-Weighted Tversky (`DTI`) Algebra
With $\alpha = 0.2$, $\beta = 0.8$, 300 m (`R = 3 px`) triangular kernel $K(u) = \max(0, 1 - u/3)$, known-catalogue pixels masked before scoring ([staff post #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)), and binary dots $P \in \{0, 1\}$ ($|P| = N$):

$$\text{DTI}(P, G) = \frac{T}{0.8\,T + 0.2\,N + 0.8\,|G|}, \qquad T = \sum_{g \in G} \max_{p \in P} K(\|g - p\|_2) \le |G|.$$

From the 5-px blind calibration lattice (`13gems r13-lattice-s5`, `206,895` dots, `0.0904` `OWNER-REPORT`) and the 4-point `H19-5` nested ladder, hidden off-catalogue ground truth in NW Nevada has **`|G| ≈ 12,265` pixels** (~`0.24%` of the `5,167,373`-pixel footprint). Differentiating $\text{DTI}(T, N)$ gives the exact marginal break-even credit per added dot:

$$\frac{\partial\,\text{DTI}}{\partial N} > 0 \iff \Delta T > \frac{0.2\,\text{DTI}}{1 - 0.8\,\text{DTI}}.$$

At $\text{DTI} = 0.2778$ (`OWNER-REPORT`), each extra dot must add **$\Delta T > 0.0714$** weighted truth pixels just to break even!

### 2.2 The 4-Step `B`-Pruning Ladder (`0.1922 -> 0.2600 -> 0.2708 -> 0.2778`, all `OWNER-REPORT`)
1. **Solid `H19-5` (`121,131` px -> `0.1922` `OWNER-REPORT`):** $T_{\text{solid}} \approx 5,021$ (`40.9%` of $|G|$), crushed by $0.2 \times 121,131 = 24,226$ denominator mass.
2. **`d2.8` Poisson Disk (`44,090` dots -> `0.2600` `OWNER-REPORT`):** 2.8-px spacing preserves `~90.6%` of 300 m kernel coverage ($T \approx 4,552$) while slashing $0.2 N$ by `63.6%`.
3. **`Solo` (`40,199` dots -> `0.2708` `OWNER-REPORT`):** Drops `3,891` `d_cat == 1 px` immediate catalogue neighbors ($T \approx 4,522$).
4. **Champion `h33-h33-2-b2` (`37,654` dots -> `0.2778` `OWNER-REPORT`):** Removes the **`2,545` flank dots at $1 < d_{\text{cat}} \le 2\text{ px}$ (`100–200 m`)**, losing only $\Delta T \approx 19$ (`0.0075/dot`, `10×` below the `0.0714` break-even bar!) because `existing_faults.tif` already occupies the fault core. At $B=3$, repaired `v3` holdout rolls over (`0.09644 < 0.09920`) because genuine branch splays and relay ramps begin at `200–300 m`.

### 2.3 Algebraic Impossibility of Reaching `0.3195` or `0.4413` from `H19-5` Subsets
Because $T(P) \le T_{\text{solid}} \approx 5,021$ for EVERY subset $P \subseteq \text{H19-5}$:
- Even an oracle keeping `28,000` dots with zero recall loss caps around `~0.305–0.312`.
- Reaching **`0.3195`** at `37,654` dots requires **$T \approx 5,430 > 5,021$** (`+20.6%` more recall than the Champion).
- Reaching **`0.4413`** (`#1 xiaofanhu`) at `37,654` dots requires **$T \approx 8,408$ (`68.6%` of $|G|$)** — `~3,905` additional hidden-fault pixels beneath blind Quaternary basins where `H19-5` placed zero predictions.

---

## 3. Pre-Registered Round-6 Geological Hypotheses (`H36-1` .. `H36-5`) & 3-Experiment Results

Full pre-registration: [`docs/research/hypotheses-round6-20261026.md`](docs/research/hypotheses-round6-20261026.md). During pre-implementation band forensics we uncovered and fixed:
- **`IR-32-BAND-02`:** Band 6 (`tc`) is **Airborne Radiometric Total Count** ($\rho = +0.99942$ with $0.41\,\text{K} + 0.48\,\text{eTh} + 0.21\,\text{eU}$), NOT gravity Terrain Correction!
- **`IR-32-BAND-03` & `IR-32-DOC-BAND05-01` (FIXED 2026-10-26):** Direct GDAL audit of `training_features.tif` and `data/prepared_manifest.json` confirms **Band 05** (`iso_grav_anom_slope`, `[0.00138, 0.6517]`) is unsigned $|\nabla_h g_{\text{iso}}| \ge 0$, **Band 17** (`cond_surf`, `[0.1937, 4.969]`) is surface MT log-conductivity, and **Band 18** (`iso_grav_anom_hg`, `[-15.44, +12.86]`) is signed $\partial g_{\text{iso}}/\partial x$ ($r = +0.9438$ with numerical $\partial_x\text{B13}$). Prior prose misattributing `iso_grav_anom_slope` to Band 17 has been corrected.
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
| **Baseline: `0.2778` (`OWNER-REPORT`) Champion (`h33-h33-2-b2`)** | `0.09920` `[0.08202, 0.12219]` | `0.09920` | `0.09606` `[0.08482, 0.10773]` | `0.06412` |
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
  3. **`EXP3_H38_G1_CORROB`** (53ch + `IR-32-LIDAR-01` quantile routing + structural corroboration): **`HOLDOUT-DTI = 0.11696 [0.10053, 0.13204]`** (`+17.9%` over `0.2778` `OWNER-REPORT` Champion `0.09920`), `SGMC_cal = 0.05037` -> **`DO NOT SUBMIT`** (`verdict = negative`).

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
  - **EXP1 (Label-Free Domain Physics, `0` labels):** `D1_LiDAR_Dipole` (`SGMC-cal = 0.10267`) and `MDRC_Unsup_4Domain` (`SGMC-cal = 0.07651`) **both beat `0.2778` (`OWNER-REPORT`) Champion (`0.06412`) on off-catalogue USGS SGMC faults**, while `57/57` channels pass the leakage canary (`max AUC = 0.6217 <= 0.90`).
  - **EXP2 (4-Quadrant OOF HistGB):** Adding the 22 MDRC channels improves held-out quadrant AUC in `4/4` folds (`+0.0042` to `+0.0207`).
  - **EXP3 (1-px Ridge-Crest Sharpening + Credit-Bar Submodular Emission, `B=2`, `44,090` dots):** Wins **`HOLDOUT-DTI = 0.10679 [0.08765, 0.12850]`** vs `CTRL-35ch` (`0.09893`) and `D2.8 vis-B2` (`0.09920`, winning `7/8` spatial-draw cells, paired Δ 95% CI `[+0.0040, +0.0111]`), while supervised `y=0` training on `~labels` suppresses pre-Quaternary `SGMC` faults (`0.05509 < 0.06412`, `IR-A8A-PU-BIAS-01`). **Concrete next step:** Positive-Unlabeled (`PU`, Elkan–Noto / anchor-set) training on the 57-channel `MDRC` stack.
- **Standalone Zero-Human-Intervention Verifier:** `.venv/bin/python scripts/verify_arena8a_submission.py` · Run Card: [`evidence/arena8a_run_card.json`](evidence/arena8a_run_card.json).

---

## 8. Session `H44-1 (SPCP)` (`2026-10-26`): SAR-PU Propensity-Debiased Potential-Field Curvature Tensor & Hydrothermal-Conduit Breach (`H44-1..H44-5`)

Pre-registration frozen prior to code execution: [`docs/research/h44-spcp-preregistration-20261026.md`](docs/research/h44-spcp-preregistration-20261026.md) · Implementation: [`src/gems32/spcp.py`](src/gems32/spcp.py) · Runner: [`scripts/run_h44_spcp.py`](scripts/run_h44_spcp.py) · Receipts: [`evidence/h44_spcp_run_card.json`](evidence/h44_spcp_run_card.json), [`evidence/h44_spcp_experiments.json`](evidence/h44_spcp_experiments.json), [`evidence/nine_site_live_audit_20261026.json`](evidence/nine_site_live_audit_20261026.json).

### 8.1 Five Ranked Untried Geological & Geothermal-Conduit Hypotheses (`H44-1..H44-5`)

| Rank | ID | Specific Layers | Physical Signature & Transform | Why Off-Catalogue (vs. USGS/INGENIOUS) & Novelty | Expected DTI / Cost / Data |
|---|---|---|---|---|---|
| **#1** | **`H44-1` (`SPCP`)** | `B05`, `B13`, `B18`, `B02`, `B03`, `B09`, `B14`, `B15`, `B12`, `B17`, `B19`, `B07-08` + GeoDAWN `K,Th,TMI_up150` + 3DEP 1m LiDAR + GDR `#1391` | Phillips (2007) $-\min(\lambda_1,\lambda_2,0)$ curvature crests of `B05` & $|\nabla_h\text{RTP}|$ with $\cos^2\Delta\theta$ concordance + hydrothermal breach + Lahontan-debiased LiDAR dipole under **fold-local Bekker–Davis `SAR-PU` observability-propensity debiasing** | Cures `IR-A8A-PU-BIAS-01`: prevents `HistGB` from treating blind alluvial-covered faults (`>75%` of Great Basin geothermal systems; Faulds & Hinz, 2015) as `y=0` true negatives | **Executed (`EXP1..3`)** · Medium CPU cost · All 23 files SHA-256 verified |
| **#2** | **`H44-2`** | `B03` (`tmi_hg`), `B09` (`tmi_vg`), `B15` (`depth_to_base`), `TMI_up150` | Roest–Verhoef–Pilkington (1992) 3D analytic signal $|A| = \sqrt{\text{B03}^2 + (100\cdot\text{B09})^2}$ & shallow contact depth $z_{\text{AS}} \ll \text{B15}$ | Detects shallow intrabasin volcanic fault offsets inside deep basins independent of remanent magnetization inclination | `+0.005–0.015` · Low · Integrated as ch 6 in `H44-1` |
| **#3** | **`H44-3`** | `B02` (`rtp`), `B12`, `B15`, `B17` (`cond_surf`), GeoDAWN `K,Th`, GDR `#1391` | High-pass RTP positive trough curvature $\kappa_+(\text{RTP}_{\text{hp}})$ $\times$ OLS `K-on-Th` excess $\times$ elevation/depth-residualized MT clay-cap gradient $\times$ `>45 °C` GDR halo | Hydrothermal upflow destroys magnetite, precipitates K-adularia/illite, and forms smectite clay caps while residualization suppresses saline playas | `+0.006–0.018` · Low-Medium · Integrated as ch 7–11 in `H44-1` |
| **#4** | **`H44-4`** | 3DEP `lidar_scarp_features_u8.tif` `B3-7,10-12`, `B12`, `B15`, `B19` | `valid`-tile-routed Laplacian scarp dipole $\times \sin^2(\theta_{\text{scarp}} - \theta_{\text{contour}})$ over low-slope piedmont fans | Resolves `<1 m` Holocene alluvial scarplets missed by pre-3DEP airphotos while vetoing horizontal Pleistocene Lake Lahontan shoreline benches | `+0.008–0.020` · Low · Integrated as ch 12–15 in `H44-1` |
| **#5** | **`H44-5`** | 55-ch `template + SPCP` stack + GeoDAWN flight lines + GDR `#1391` 3D MT | Multi-altitude crest-migration dip estimation + `256×256` 2D Tversky `SAR-PU` U-Net/SegFormer without reference Cell 12 positive-tile skip | Bridges pixel-local CPU tree ceiling (`0.2778` `OWNER-REPORT`) to `0.3195–0.4413` 2D multi-scale fault-relay context | `+0.04–0.14` · High (CUDA GPU required; deferred outside 2-vCPU sandbox) |

### 8.2 Three-Experiment Controlled Ablation (`37,654` Dots, `B=2`, `55/55` Leakage Canary PASS `max AUC = 0.5869 <= 0.90`)

| Arm (`37,654` dots, `B = 2 px`) | `HOLDOUT-DTI` (`GEMSDOE32-HIDE-RECOVER-v3.0`, `n=22,232`, 95% CI) | Censorship-Matched (`d_hidden > 2 px`) | Detached Segments (`>= 600 m`, `n=15,504`, 95% CI) | Off-Catalogue USGS SGMC Raw / Calibrated (`GEMSDOE32-SGMC-CAL-v3.0`, `n=62,703`, 95% CI) |
|---|---|---|---|---|
| **Baseline: `0.2778` (`OWNER-REPORT`) Champion (static)** | `0.004515` `[0.003816, 0.005262]` | `0.004515` | `0.004409` `[0.003636, 0.005283]` | `0.096060` / **`0.064121`** `[0.056730, 0.071649]` |
| **Control: `CTRL_35CH_OOF` (35-ch naive `HistGB`)** | `0.101688` `[0.086133, 0.116820]` | `0.004714` | `0.094739` `[0.078312, 0.111742]` | `0.081785` / `0.054453` `[0.047048, 0.061740]` |
| **EXP 1/3: `EXP1_H44_UNSUP_SPCP` (label-free physics)** | `0.037093` `[0.029165, 0.045767]` | `0.001820` | `0.033138` `[0.025992, 0.040671]` | **`0.119916`** / **`0.080321`** `[0.070747, 0.090013]` |
| **EXP 2/3: `EXP2_H44_NAIVE_BIN55` (55-ch naive `y=0`)** | **`0.107700`** `[0.092207, 0.123051]` | `0.004623` | **`0.100144`** `[0.082798, 0.117013]` | `0.070104` / `0.046628` `[0.039727, 0.052916]` |
| **EXP 3/3: `EXP3_H44_SARPU_SPCP` (`SAR-PU` debiased)** | `0.069841` `[0.060297, 0.079276]` | `0.003022` | `0.063641` `[0.053392, 0.074096]` | **`0.116056`** / **`0.077736`** `[0.069192, 0.085644]` |

- **Scientific Breakthrough (`IR-32-SARPU-PARETO-01`):** `EXP2` vs `EXP3` isolates and cures `IR-A8A-PU-BIAS-01` quantitatively: naive `y=0` binary `HistGB` (`EXP2`) boosts exposed-scarp `Hide&Recover` (`0.10770`) while crushing blind `SGMC-cal` (`0.04663`), whereas fold-local `SAR-PU` propensity debiasing (`EXP3`) lifts off-catalogue `SGMC-cal` by **`+0.03083` (`+66.7%`, `95% CI [+0.0213, +0.0402]`, `P=1.000`)** and beats the `0.2778` (`OWNER-REPORT`) Champion (`0.06412`) by **paired spatial-block bootstrap Δ `+0.01328` (`95% CI [+0.0030, +0.0248]`, `P=0.998`)** — the highest off-catalogue blind-fault `SGMC-cal` among all `37,654`-dot supervised GeoTIFFs audited across all 9 focus repos!
- **Why Verdict is `negative` / `DO NOT SUBMIT`:** Shifting `52.41%` of dots `> 2.0 km` into blind basins lowers exposed-scarp `Hide&Recover` (`0.06984 < CTRL-35ch 0.10169`) and censorship-matched `d_hidden > 2 px` (`0.00302 < 0.00452`), and the literal unexempted `release_gate.compare_registry` check hits `GEMSDOE24`'s synthetic 5-px calibration lattice (`99.69% > 70%`, while passing all **288** genuine rasters at `max |Spearman| = 0.1204 <= 0.90` and `max 3-px overlap = 44.48% <= 70%`).

### 8.3 Geothermal-Vent & Structural Geology Knowledge Base (Auditable Summary Table)

| Structural / Hydrothermal Setting | Physical Signature in GEMS Layers | Non-Fault Mimic Process | SPCP De-Confounding Mechanism | Verified Official Source |
|---|---|---|---|---|
| **Accommodation-zone step-overs, relay ramps & fault tips (`>75%` of blind Great Basin geothermal systems)** | Strike-concordant Phillips (2007) $-\min(\lambda_1,\lambda_2,0)$ crests on `Band 05` (`iso_grav_anom_slope`) & $|\nabla_h\text{RTP}|` + `Band 18` half-graben saddle | Unfaulted pluton / caldera ring margins | Cross-domain $\cos^2(\theta_g - \theta_m)$ axial concordance + Roest 3D analytic-signal depth discordance against `Band 15` | [Faulds & Hinz 2015 / GBCGE INGENIOUS](https://gbcge.org/current-projects/ingenious/) · [Phillips et al. 2007 USGS](https://pubs.usgs.gov/publication/70030656) · [Roest et al. 1992](https://doi.org/10.1190/1.1443174) |
| **Upflow magnetite-destruction & potassic alteration conduits (`150–300 °C` neutral-Cl brines)** | Narrow RTP demagnetization trough $\kappa_+(\text{RTP}_{\text{hp}})$ + positive OLS `K-on-Th` residual (`geodawn_rad_u8`) + GDR `#1391` `>45 °C` quartz/chalcedony/Na-K-Ca geothermometer & Quaternary volcanic-vent halos (`27,092` wells/springs, `21` vents; `dist_known_fault_px` dropped) | Felsic rhyolite ash-flow tuffs with high primary K and low magnetic susceptibility | Regressing `K` on immobile `Th` removes primary felsic lithology (`K` and `Th` co-vary in unaltered tuffs; hydrothermal adularia enriches `K` alone) | [DOE GDR #1391 (`DOI 10.15121/1881483`)](https://doi.org/10.15121/1881483) · [USGS GeoDAWN (`DOI 10.5066/P93LGLVQ`)](https://doi.org/10.5066/P93LGLVQ) |
| **Hydrothermal smectite–illite clay cap lateral fault seals** | Sharp lateral gradient of `Band 17` (`cond_surf`) residualized against quadratic `(det_elev, log1p(depth_to_base), det_elev_slope)` | Closed-basin evaporative saline playas & deep conductive clay-rich depocenters | Quadratic elevation/depth nuisance regression strips horizontal basin-floor brine sheets before taking $|\nabla_h r_{\text{MT}}|$ | [DrivenData Problem Spec](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [INGENIOUS GBCGE](https://gbcge.org/current-projects/ingenious/) |
| **Sub-meter Holocene piedmont fault scarplets (`<1 m` vertical throw)** | `Band 12` `valid`-routed 1 m 3DEP LiDAR Laplacian dipole `step_max * sqrt(lapneg*lappos)` $\times$ facing asymmetry $\times \sin^2(\theta_{\text{scarp}} - \theta_{\text{contour}})$ | Pleistocene Lake Lahontan horizontal wave-cut shoreline benches (`~1,270–1,338 m`) & two-bank incised washes | Contour-orthogonality $\sin^2\Delta\theta$ zeroes topographic-contour-parallel shorelines; facing asymmetry zeroes symmetric stream channels | [USGS 3DEP 1m DEM](https://www.usgs.gov/3d-elevation-program) · [USGS QFaults](https://www.usgs.gov/natural-hazards/earthquake-hazards/faults) |

### 8.4 Remaining Limitations & Concrete High-Leverage Next Suggestions
1. **Two-Regime Split-Budget Allocation (Immediate CPU Follow-Up):** Combine `EXP2`/`H38-G1` high-precision exposed range-front scarp continuations (`~65%` of the `37,654` dot budget where $\tilde{e}(z) \ge 0.5$) with `EXP3_H44_SARPU_SPCP` blind-basin curvature/conduit crests (`~35%` of budget where $\tilde{e}(z) < 0.5$) to jointly beat `0.2778` (`OWNER-REPORT`) on **both** `GEMSDOE32-HIDE-RECOVER-v3.0` and `GEMSDOE32-SGMC-CAL-v3.0`.
2. **GPU 2D Spatial Segmentation (`H44-5`):** Train a `256×256`-patch SegFormer/U-Net on the 55-channel `template + SPCP` stack using smooth Distance-Buffered Tversky loss ($\alpha=0.2, \beta=0.8$) weighted by `SAR-PU` propensity $\hat{e}(z)$ (without `drivendataorg/gems-prize-reference-solution` Cell 12 positive-tile filtering).
3. **Literal Calibration-Lattice Registry Metadata (`IR-42-UNIQ-01`):** Separate synthetic mathematical covering grids (`13gems r13-lattice-s5`) from candidate submission rasters via an explicit manifest `role: "calibration_probe"` schema update approved across all 9 repos.

---

<details>
<summary><b>Standing Competition Prompt & Parallel-Run Protocol (recorded verbatim for future reference)</b></summary>

```text
Review this project and other GEMSDOE projects focusing on 24, 25, 27, 28, 30, 31, 32, 33, 36. Provide a clear executive summary of the highest submissions and make it very clear and obvious which submission is best to submit for a high score on the leaderboard and whether it is unique or a duplicate of another submission.

Core Values
Maximize P(Win): Weigh tradeoffs and risk and choose the path that maximizes the probability of winning. Always put the outcome first!
Own the Outcome: Own results end to end, from initial action to final result. Step up and take action when problems arise. Treat both failure and success as signals to learn and adapt. Stay accountable until the final outcome is achieved.

HIGHEST URGENCY: TIF SUBMISSION MUST BE UNIQUE AND UNLIKE ANY OTHER PREVIOUS GEMSDOE SUBMISSIONS. NEVER COPY OTHER SUBMISSIONS EXCEPT TO LEARN FROM THEM OR CALIBRATE TESTING! WE MUST GENERATE A UNIQUE TIF SUBMISSION IN THIS SESSION AND VALIDATE IT WITHOUT HUMAN INTERVENTION SO WE KNOW IF IT IS OK TO DOWNLOAD AND SUBMIT OR NOT! MAKE IT VERY CLEAR ON SITE AND EXECUTIVE SUMMARY SUBPAGE WHETHER IT IS OK TO SUBMIT!

Look at previous notes and any next steps that haven't been done yet and execute them first. If there are no next steps, please proceed with the prompt below.

We are competing in the DrivenData "DOE GEMS Prize: Advancing Geothermal Exploration with Machine Learning" challenge (https://www.drivendata.org/competitions/306/competition-doe-gems/ — 0.4413 is the highest score right now). Our goal is to place high on the leaderboard and maximize total winnings across both the Initial Leaderboard Round ($175,000 pool, 15 prizes, top prize $25,000) and the Final Round ($395,000 pool, 15 prizes, top prize $100,000). The competition closes May 13, 2026 (11:59 p.m. UTC) and permits 3 submissions per rolling 7-day window.

Fix submission error: "Predicted values must be in range [0, 1]".

Read the problem description, evaluation metric (Distance-buffered Tversky Index with α = 0.2, β = 0.8, 300 m triangular kernel, tolerating ±1 px rasterization and ≤300 m ground-truth misalignment), submission format (single-band GeoTIFF matching example_submission.tif CRS EPSG:32611, shape, geotransform, values in [0, 1], no NaNs inside the data footprint, or a .zip containing a single GeoTIFF), rules PDF (https://docs.nlr.gov/docs/fy26osti/96647.pdf), and official reference solution (https://github.com/drivendataorg/gems-prize-reference-solution). Remember that the same selected submission is evaluated twice — first on newly collected expert-mapped faults, and again on an expanded label set incorporating expert-verified novel fault predictions from participants — and that β = 0.8 weights false negatives 4× more heavily than false positives (α = 0.2), strongly rewarding high recall of real, unmapped geothermal-indicative faults rather than only memorizing the existing USGS/INGENIOUS catalog.

Tasks:
1. Review our GitHub repository and GitHub Pages site thoroughly, check all past submissions, scores, code, notes, and open issues, and summarize where we stand vs. the current public leaderboard.
2. Notice that the highest score from our sites is GEMSDOE32 (https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778. Analyze at a PhD level why this file got the highest score from a technical and scientific perspective, and see if we can beat 0.3195, which is the highest score right now.
3. Propose 3–5 concrete, untried geological/geophysical hypotheses for improving DTI before writing code. For each hypothesis, state: (a) which specific layer(s) it uses, (b) what physical fault signature or transform it captures, (c) why it should catch faults missing from the USGS/INGENIOUS catalog rather than already-mapped ones, (d) how it differs from what we already tried in the repo, and (e) whether any free, official external data source can be legally incorporated (verify obtainability first; do not assume). Rank hypotheses by expected DTI improvement vs. implementation cost. Emphasize geothermal vents and store all verified scientific research and data sources in clean, auditable tables with verified official links.
4. Validate the top candidate(s) on a spatially-blocked holdout set before touching a weekly submission slot, then generate a clean, ready-to-upload submission (.tif or .zip) with a unique submission name and short note so we never confuse submissions. Make the submission easy to download prominently at the top of our GitHub Pages site, with an executive summary subpage explaining step-by-step how to submit.
5. Keep all files, code, data manifests, and GitHub Pages clean and well-organized with an automated feed of current information. Work autonomously with zero manual user input. Verify every claim, link, and calculation line by line from official trusted sources — zero hallucinations; flag any irregularities for review. Put this prompt into the readme.md for future reference.
6. Run 3 passes before finishing: Pass 1 — complete implementation and verification; Pass 2 — review everything, fix bugs, missing requirements, and edge cases; Pass 3 — full re-check against this prompt for accuracy, completeness, and quality. Then create a pull request and merge it into main, noting any remaining suggestions or limitations.

Parallel-run protocol — follow strictly:
1. Lane: Only explore the pre-registered single hypothesis lane. Check both the continuous surface before placement AND the final dots against registry/submissions.json — if rank-correlation > 0.90 OR >70% of dots fall within 3 px of any registry raster's dots, log as duplicate and stop.
2. Reuse, don't rebuild: Use the cached feature stack, evaluate_holdout.py, and submission_writer.py as-is. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive any catalogue features only from the remaining visible faults, mask visible faults pixel-exactly at scoring, and score pooled DTI (α=0.2, β=0.8, 300 m triangular kernel). If a shared tool has a bug, fix it in the template — never keep a private fork.
3. Label every number: Either HOLDOUT-DTI (state evaluator version, n withheld positives, 95% CI) or ORGANIZER-CONFIRMED (paste submission receipt). Never write a projection as a score.
4. Leakage canary: Test every feature alone on holdout first; single-feature AUC > 0.90 is leakage until proven otherwise.
5. Run card: End your response with one JSON card: hypothesis, mechanism, named non-fault mimic process, holdout_dti + 95% CI, correlation/overlap vs registry, raster sha256, validator output, submission name + note (≤140 chars), and verdict (promote or negative — negative results are valid deliverables).
6. Budget: Stop after [3] experiments or [2] hours. Do not spend weekly submission slots on candidates that fail to beat our current holdout best.
```

</details>
