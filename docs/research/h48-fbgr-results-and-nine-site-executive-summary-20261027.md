# H48-1-FBGR Results, Live-Score Covariate Forensics & Refreshed Nine-Site Executive Summary (2026-10-27)

**Session branch:** `arena/1b3cd3f5-gemsdoe32` · **Date:** `2026-10-27` · **Experiments used:** `3 / 3` · **Weekly slots spent:** `0`  
**Newest research artifact:** `docs/downloads/gemsdoe32-h48-fbgr-dualcover-axial28-37654-20261027T180500Z-4d38a240-zeros.tif` (`SHA-256: 4177f236b7c6a26fdf39d85f0896d1a83da745c9a36b04be7fe201a0076bf29f`)  
**Release verdict:** **DO NOT SUBMIT** (`verdict: "negative"`, `ok_to_submit: false`, `download_for_research_ok: true`)

---

## 1. Executive Summary & Refreshed Nine-Site Decision Table (`2026-10-27`)

Across **519 cached GeoTIFF entries** (**416** in the 9 focus sites `GEMSDOE24..36`, **38** extra scored rasters across `GEMSDOE70/76/63/37/29/22/3/12GEMSDOE`, and **65** sibling-org rasters across `KANLERGEMSDOE1..3` and `WBGGEMSDOE1..3`; **466** unique SHA-256 hashes), **no new file is authorized for live portal upload today (`any_file_ok_to_submit = false`)**:

1. **Historical focus-site winners (`0.2449`–`0.2778` `OWNER-REPORT`):** All nine historical site highs belong to **one nested `H19-5` thinning/pruning family** (minimum pairwise 3-px overlap `86.72% > 70%`). `GEMSDOE32`'s `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (`0.2778` `OWNER-REPORT`, `37,654` dots) is already scored — **do not resubmit**.
2. **2026-10-26 Live-Return Calibration (`OWNER-REPORT`):** Five genuinely non-`H19-5` submissions scored live on `2026-10-26`: `GEMSDOE27 H31-1` achieved **`0.2250`** (`OWNER-REPORT`, genuine unique), while `GEMSDOE36 KPL-36` (`0.1647`, `99.17%` duplicate of `GEMSDOE32 H38`), `GEMSDOE33 S33-SEISDIL` (`0.0963`), `GEMSDOE25 H66-BGHF` (`0.0742`), and `GEMSDOE28 S21-DGRC` (`0.0206`) underperformed for exact, measurable spatial reasons quantified in §3 (`evidence/livescore_forensics_20261027.json`).
3. **This session's `H48-1-FBGR` (`EXP3`, `37,654` dots, `B = 2`, `min_sep_px = 2.8`):**
   - **Beats the `0.2778` Champion on primary `HOLDOUT-DTI`** (`GEMSDOE32-HIDE-RECOVER-v3.0`, `n = 22,232`): **`0.115341` `[0.100168, 0.130524]`** vs Champion **`0.099202` `[0.085951, 0.112668]`** (`paired Δ = +0.016217`, 95% CI `[+0.008599, +0.024287]`, `p = 1.000`).
   - **Sets a stationary repository high on `Detached >= 600 m` withheld fault segments** (`n = 15,504`): **`0.101168` `[0.085002, 0.117569]`**, beating both the `0.2778` Champion (`0.094324`, `p = 0.957`) and `H47-1-LDGI` (`0.091842`).
   - **Passes 83/83 leakage canaries** (max oriented AUC `0.586868 <= 0.90`), **13/13 GeoTIFF byte/range checks** (`0` NaNs anywhere, `[0.0, 1.0]`, `float32`, `EPSG:32611`, `3730x3292`), and **100% of genuine discrete (`<=100k`-dot) uniqueness checks** across all orgs (`max |Spearman| = 0.63146 <= 0.90`; max focus-site 3-px dot overlap **`65.94% <= 70.0%`**; max all-org `<=100k`-dot overlap **`68.82% <= 70.0%`**).
   - **Held fail-closed (`DO NOT SUBMIT`)** because: (i) off-catalogue `SGMC-cal v3.0` (`0.056798` `[0.050345, 0.063015]`, though `+39.4%` above `EXP2`'s `0.04072`) trails the `0.2778` Champion (`0.064121`), and (ii) unexempted literal `release_gate.compare_registry` flags the `206,895`-dot `r13-lattice-s5` calibration grid (`99.78%`, `IR-51-LATTICE-01`) and `WBGGEMSDOE1/2` continuous `5.11M`-pixel research surfaces (`IR-48-WBG-SURFACE-01`).

### Nine-Site Executive Decision Table (`2026-10-27` Refreshed Commits)

| Focus Site (`HEAD`) | Historical Best File (`OWNER-REPORT`) | Newest `2026-10-26/27` Candidate (`SHA-256` prefix) | Labeled Score / `HOLDOUT-DTI` (`HIDE-RECOVER-v3.0`, `n=22,232`; `SGMC-cal`, `n=62,703`) | Genuine Unique (`|ρ|<=0.90` & `<=70%` 3-px)? | OK to Download & Submit? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GEMSDOE24** (`2521cb67`) | `24gems-d15-h19-5-…-6eb7b9c3.tif` (`0.2535` `OWNER-REPORT`) | `24gems-s20-h1-swcr-20261027T011022Z-7552b2e9b80d-zeros.tif` (`c6f261d7…`, `37,654`d) | Hist `0.2535` `OWNER-REPORT`; `GVC1` `0.0859` `OWNER-REPORT`; `S20-H1` static HR `0.0029`, `SGMC-cal` `0.0684` (`HOLDOUT-DTI`) | Hist: **NO** (`H19-5`); `S20-H1`: **YES** (`52.9%` vs Champ) | **NO — DO NOT SUBMIT** |
| **GEMSDOE25** (`5a60fb47`) | `gems25-dotted-h19-5-d2-8-…-zeros.tif` (`0.2600` `OWNER-REPORT`) | `gems25-h71-bh-celf2-8-37654-20261026-cb6580747463-zeros.tif` (`cb658074…`, `37,654`d) | Hist `0.2600` `OWNER-REPORT`; `H66` `0.0742` `OWNER-REPORT`; `H71-BH` static HR `0.0033`, `SGMC-cal` `0.0689` (`HOLDOUT-DTI`) | Hist: **NO** (`100%` = `GEMSDOE30`); `H71-BH`: **YES** (`30.5%` vs Champ) | **NO — DO NOT SUBMIT** |
| **GEMSDOE27** (`69d6f033`) | `gems27-gapclose-d15-…-allfinite.tif` (`0.2449` `OWNER-REPORT`) | `gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif` (`2c002b02…`, `42,000`d) | Hist `0.2449` `OWNER-REPORT`; **`H31-1` Live `0.2250` `OWNER-REPORT`** (`SGMC-cal` `0.0695` `HOLDOUT-DTI`) | Hist: **NO** (`H19-5`); `H31-1`: **YES** (`29.3%` vs Champ; **already scored**) | **NO — ALREADY SUBMITTED** (`0.2250` trails `0.2778`) |
| **GEMSDOE28** (`67dbdf4d`) | `gems28-blind-rung-…-allfinite.tif` (`0.2587` `OWNER-REPORT`) | `gems28-s22-ctxhgb-20261026-e23dabcec6e2-allfinite.tif` (`77934be6…`, `42,000`d) | Hist `0.2587` `OWNER-REPORT`; `S21` `0.0206` `OWNER-REPORT`; `S22` `SGMC-cal` `0.0566` (`HOLDOUT-DTI`, `12.3%` flat basin) | Hist: **NO** (`H19-5`); `S22`: **YES** (`39.2%` vs Champ) | **NO — DO NOT SUBMIT** (`12.3%` flat-basin spill) |
| **GEMSDOE30** (`3c3d7255`) | `gems30-offcat-d28-…-zeros.tif` (`0.2600` `OWNER-REPORT`) | `30gems_20261026T222638Z_CSR1-aniso-corrob-celf37654_a2eb8544_zeros.tif` (`a2eb8544…`, `37,654`d) | Hist `0.2600` `OWNER-REPORT`; `CSR1` static HR `0.0029`, `SGMC-cal` `0.0604` (`HOLDOUT-DTI`) | Hist: **NO** (`100%` = `GEMSDOE25`); `CSR1`: **YES** (`26.9%` vs Champ) | **NO — DO NOT SUBMIT** |
| **GEMSDOE31** (`fbebc017`) | `gems31-solo-b1-…-zeros.tif` (`0.2708` `OWNER-REPORT`) | `gemsdoe31-h31u-strainseis-corrob-37654-20261026T224505Z-f34c9107-zeros.tif` (`f34c9107…`, `37,654`d) | Hist `0.2708` `OWNER-REPORT`; `H31U` static HR `0.0028`, `SGMC-cal` `0.0598` (`HOLDOUT-DTI`) | Hist: **NO** (`100%` = `GEMSDOE28` B1); `H31U`: **YES** (`34.9%` vs Champ) | **NO — DO NOT SUBMIT** |
| **GEMSDOE32** (`1398109a`) | `gemsdoe32-h33-h33-2-b2-…-e5eb6e7e-zeros.tif` (**`0.2778`** `OWNER-REPORT`) | **`gemsdoe32-h48-fbgr-dualcover-axial28-37654-20261027T180500Z-4d38a240-zeros.tif`** (`4177f236…`, `37,654`d) | Champ **`0.2778` `OWNER-REPORT`** (already submitted); **`H48-1` `HOLDOUT-DTI` `0.115341` `[0.100168, 0.130524]`, Detached `0.101168`, `SGMC-cal` `0.056798`** | Champ: **NO** (`H19-5`); **`H48-1`: YES** (`65.94% <= 70%` focus; `68.82% <= 70%` all-org `<=100k`) | **NO — DO NOT SUBMIT** (`SGMC-cal` < `0.0641` & `r13-lattice` stop; research download OK) |
| **GEMSDOE33** (`122e2240`) | `gems33-b2-analog-…-zeros.tif` (`0.2640` `OWNER-REPORT`) | `gems33-fsml2cc-anisotropic-20261027-be8f0284c048-zeros.tif` (`be8f0284…`, `37,654`d) | Hist `0.2640` `OWNER-REPORT`; `S33-SEISDIL` `0.0963` `OWNER-REPORT`; `FSML2CC` `SGMC-cal` `0.0640` (`HOLDOUT-DTI`) | Hist: **NO** (`H19-5`); `FSML2CC`: **YES** (`34.1%` vs Champ) | **NO — DO NOT SUBMIT** |
| **GEMSDOE36** (`75769423`) | `gems36-anderson-pinn-…-zeros.tif` (`0.2750` `OWNER-REPORT`) | `gems36-kpl36-exp3-dualregime-pu-37654-20261026T170655Z-447cdab8-zeros.tif` (`529d7924…`, `37,654`d) | Hist `0.2750` `OWNER-REPORT`; `KPL-36` **`0.1647` `OWNER-REPORT`** (`SGMC-cal` `0.0468` `HOLDOUT-DTI`) | Hist: **NO** (`Champ + 1,200d`); `KPL-36`: **NO** (`99.17%` within 3 px of `GEMSDOE32 H38`) | **NO — DO NOT SUBMIT** |

---

## 2. PhD-Level Derivation: Why `GEMSDOE32` Scored `0.2778` and What Separates `0.2778` from `0.4437`

### 2.1 Exact Metric Algebra (`alpha = 0.2`, `beta = 0.8`, `R = 300 m`)
Let $G_{\text{hid}} = G_{\text{tot}} \setminus V$ denote the organizer's hidden fault pixels (after pixel-exact masking of the visible `labels.tif` compilation $V$, $|V| = 60,988$) and let $k(d) = \max(0, 1 - d/300\,\text{m})$. Using $\text{FN}_w = |G_{\text{hid}}| - \text{TP}_w$, $T = \text{TP}_w = \sum_{g \in G_{\text{hid}}} \max_{x} p(x)\,k(d(x,g))$, $S = \sum_x p(x)$, and $M = \sum_x p(x)\max_{g \in G_{\text{hid}}} k(d(x,g))$, the official Distance-Weighted Tversky Index reduces identically to:

$$\text{DTI}(p) = \frac{T}{0.2\,(T + S - M) + 0.8\,|G_{\text{hid}}|}$$

Differentiating with respect to a candidate binary dot $x_0$ with marginal uncovered-truth gain $\Delta T(x_0)$ and self-match $m(x_0) = \max_{g \in G_{\text{hid}}} k(d(x_0,g))$ yields the exact inclusion condition:

$$\Delta \text{DTI}(x_0) > 0 \iff \Delta T(x_0) + 0.2\,\text{DTI}\cdot m(x_0) > 0.2\,\text{DTI}\cdot\bigl(1 + \Delta T(x_0)\bigr)$$

In the isolated-dot regime ($m(x_0) \ll 1$), a dot raises $\text{DTI}$ if and only if its **marginal uncovered kernel credit** satisfies $\Delta T(x_0) > \frac{0.2\,\text{DTI}}{1 - 0.2\,\text{DTI}}$ (`0.0588` at `DTI = 0.2778`; `0.0974` at the public #1 `0.4437`).

### 2.2 Why the Nested `H19-5 -> D2.8 -> B=1 -> B=2` (`0.2778`) Ladder Monotonically Rose
Byte-exact set inclusion across the archived GeoTIFFs establishes:
- `H19-5` (`121,131` px, `0.1922` `OWNER-REPORT`) $\supset$ `D2.8` (`44,090` px, `0.2600`) $\supset$ `Solo / B=1` (`40,199` px, `0.2708`) $\supset$ **`H33-2-B2` (`37,654` px, `0.2778`)**.
- **Step 1 (`121,131 -> 44,090`, `+0.0678`):** Continuous 3-px-wide ribbons pack redundant neighbors inside the $300\,\text{m}$ triangular kernel where $\Delta T(x_0) \approx 0$ (truth already covered by an adjacent pixel) while $\Delta S = +1$ still pays the full $0.2$ false-positive denominator tax. Enforcing $d \ge 2.8\,\text{px}$ (`280 m` along-strike spacing on a $300\,\text{m}$ kernel) eliminates `63.6%` of $S$ while preserving `>93%` of $T$.
- **Step 2 (`44,090 -> 40,199 -> 37,654`, `+0.0178`):** Removing the `3,891` dots at $d(x, V) = 1\,\text{px}$ (`B=1`) and `2,545` dots at $1 < d(x, V) \le 2\,\text{px}$ (`B=2`) removes halo predictions triggered by the DEM/gravity signature of **already-mapped** faults in $V$. Because $V$ is masked pixel-exactly rather than buffered in $G_{\text{tot}}$, parallel flanks `100–200 m` off a mapped scarp earn zero credit unless a distinct unmapped strand lies within `300 m`.
- **Step 3 (`GEMSDOE36` `37,654 + 1,200 = 38,854`, `0.2750`):** Appending `1,200` uncalibrated Andersonian dots lowered the score by `-0.0028`, proving their average marginal credit was below `0.0588`.

---

## 3. Forensic Spatial-Covariate & Clumping Audit of All 10 Live-Scored Non-Family Runs (`evidence/livescore_forensics_20261027.json`)

| Raster ID | Score (`Class`) | Dots | `>1.5 km` Off-Cat | `1 m` LiDAR Gap (`24.6%` base) | Flat Deep Basin (`<2°`, `>300m`) | `>=3` Nbrs in `<=3 px` (`Clump>=3`) | Footprint `300 m` Kernel Cov |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `GEMSDOE32` `H33-B2` Champion | **`0.2778`** (`OWNER-REPORT`) | `37,654` | **`58.4%`** | **`23.6%`** | **`0.4%`** | **`0.69%`** | **`5.86%`** |
| `GEMSDOE70` Dual-Anchor | **`0.2478`** (`OWNER-REPORT`) | `36,000` | **`54.9%`** | **`25.7%`** | **`0.2%`** | `15.11%` | `5.18%` |
| `GEMSDOE76` Submod-Offcat | **`0.2343`** (`OWNER-REPORT`) | `37,654` | `35.3%` | **`20.2%`** | **`3.3%`** | `3.41%` | `5.61%` |
| `GEMSDOE27` `H31-1` DRCG-WL | **`0.2250`** (`OWNER-REPORT`) | `42,000` | **`52.4%`** | **`20.9%`** | **`4.3%`** | **`0.19%`** | **`6.31%`** |
| `GEMSDOE36` `KPL-36` EXP3 | `0.1647` (`OWNER-REPORT`) | `37,654` | `49.5%` | `19.7%` | `2.1%` | **`42.57%` (!)** | `4.17%` |
| `GEMSDOE63` CVaR-Thin | `0.1190` (`OWNER-REPORT`) | `54,864` | `55.4%` | `25.2%` | `4.0%` | `0.00%` | `9.31%` |
| `GEMSDOE33` `S33-SEISDIL` | `0.0963` (`OWNER-REPORT`) | `40,199` | `54.7%` | `23.3%` | `0.4%` | `0.70%` | `6.24%` |
| `GEMSDOE24` `GVC1` Conduit | `0.0859` (`OWNER-REPORT`) | `37,654` | **`14.0%` (!)** | `15.0%` | **`10.4%` (!)** | `0.70%` | `5.71%` |
| `GEMSDOE25` `H66-BGHF` | `0.0742` (`OWNER-REPORT`) | `46,000` | **`9.1%` (!)** | `19.7%` | **`15.5%` (!)** | `0.12%` | `7.15%` |
| `GEMSDOE28` `S21-DGRC` | `0.0206` (`OWNER-REPORT`) | `37,654` | **`3.5%` (!)** | `19.1%` | **`13.2%` (!)** | `2.45%` | `5.47%` |
| **`GEMSDOE32` `H48-1-FBGR` (this run)** | *unscored* (`HOLDOUT-DTI`) | `37,654` | `42.8%` | **`30.4%`** | **`3.6%`** | **`0.98%`** | **`5.89%`** |

Three quantitative laws govern every single live return above:
1. **Far-field reach (`>1.5 km` from `labels.tif`):** Every `>0.22` live model places **`52.4%–58.4%`** of its budget beyond `1.5 km` from `labels.tif`. Models that crowd `86%–96.5%` of dots into the `200–1,500 m` collar (`S21` `0.0206`, `H66` `0.0742`, `GVC1` `0.0859`) collapse catastrophically.
2. **Flat-basin exclusion (`slope < 2°` & `depth > 300 m`):** Every `>0.22` model keeps flat deep basin allocation $\le 4.3\%$; `10.4\%\text{–}15.5\%$ flat-basin spill destroys precision.
3. **3-px ribbon clumping (`Clump>=3`):** `GEMSDOE36 KPL-36` (`0.1647`) had `49.5%` far-field reach and `2.1%` flat-basin discipline, yet lost `~0.06–0.08` DTI because raw greedy CELF on smooth `200–400 m`-wide GBDT ribbons placed parallel flanks `2–3 px` apart (`Clump>=3 = 42.57%`), slashing footprint `300 m` coverage from `5.86%` to `4.17%`.

---

## 4. `H48-1-FBGR` Three-Experiment Ablation Results (`evidence/h48_fbgr_experiments.json`)

| Arm (`37,654` full-map dots, `B = 2`) | `HIDE-RECOVER-v3.0` (`n = 22,232`) | Censored `d_hid > 2 px` (`n = 22,232`) | Detached `>= 600 m` (`n = 15,504`) | `SGMC-cal v3.0` (`n = 62,703`) |
| :--- | :---: | :---: | :---: | :---: |
| **`0.2778` Champion (`D2.8` / `B=2` baseline)** | `0.099202` `[0.085951, 0.112668]` | `0.004519` `[0.003706, 0.005344]` | `0.094324` `[0.079248, 0.109825]` | **`0.064121`** `[0.056730, 0.071649]` |
| **`EXP1`: Single-Regime `83`-ch + Axial `d=2.8`** | `0.115254` `[0.100591, 0.129625]` | `0.005164` `[0.004400, 0.005897]` | `0.100353` `[0.084695, 0.116895]` | `0.055814` `[0.049368, 0.061879]` |
| **`EXP2`: Dual-Cover `83/71`-ch + Raw CELF (`d=0.0`)** | `0.103264` `[0.088533, 0.117621]` | `0.006172` `[0.005176, 0.007208]` | `0.091426` `[0.076253, 0.107268]` | `0.040721` `[0.034978, 0.046504]` |
| **`EXP3`: `H48-1-FBGR` Dual-Cover + Axial `d=2.8`** | **`0.115341`** `[0.100168, 0.130524]` | `0.005176` `[0.004385, 0.005902]` | **`0.101168`** `[0.085002, 0.117569]` | `0.056798` `[0.050345, 0.063015]` |

### Key Scientific Takeaways & What `H48-1-FBGR` Proved
1. **Axial `min_sep_px = 2.8` + 4-azimuth NMS (`EXP3` vs `EXP2`) is decisive (`p = 1.000` on both benchmarks):** Enforcing `min_sep_px = 2.8` inside shared `gems32.emitter.emit` boosted `HIDE-RECOVER-v3.0` by **`+0.012020` `[+0.007382, +0.017186]`** (`p = 1.000`), boosted `Detached >= 600 m` from `0.091426` to **`0.101168` (`+0.009742`)**, and boosted `SGMC-cal v3.0` from `0.040721` to **`0.056798` (`+0.016038 = +39.4%` relative, `p = 1.000`)**, cutting `Clump>=3` to **`0.98%`**.
2. **Stationary Dual-Cover (`M_Full` `83`-ch + strictly LiDAR-free `M_Sub` `71`-ch) recovers the `24.63%` 1 m LiDAR gap:** `EXP3` emits `11,452` dots (`30.4%`) in the LiDAR gap vs `19.0%` in `H47-1`, lifting `SE` quadrant `HIDE-RECOVER` DTI from `0.14755` (`EXP1`) to **`0.15185` (`EXP3`)** and achieving the highest stationary `Detached >= 600 m` score (`0.101168`) in the repository without any non-stationary `eta(V)` switch (`IR-48-CCAA-01`).
3. **Why `SGMC-cal` (`0.056798`) trailed the `0.2778` Champion (`0.064121`) — exact diagnosis for `H49`:** Because `build_stationary_fbgr_surface` combined OOF probability `p_dual` with the label-free FBGR conduit crest purely **multiplicatively** (`p_dual * mod`), and supervised `HistGradientBoostingClassifier` posteriors decay from `~0.40` inside `1.5 km` of visible faults to `~0.03` beyond `2 km` (due to positive-unlabeled suppression on unmapped regions), `EXP3` still placed `57.2%` of its dots inside `2–15 px` (`42.8%` `>15 px` vs `58.4%` for the `0.2778` Champion). Replacing multiplicative `p_dual * mod` with a **stationary max-envelope floor** $\max\bigl(p_{\text{dual}}\cdot\text{mod},\; c_{\text{far}}\cdot C_{\text{FBGR}}\bigr)$ (calibrated once so `>1.5 km` allocation matches the `53%–58%` live-winner band) is the single cleanest step to clear Gate `G5` (`SGMC-cal >= 0.065`) in `H49`.

---

## 5. Limitations & Needed External Access

1. **Outbound sandbox network egress whitelist:** This environment restricts direct outbound HTTP to `github.com`, `codeload.github.com`, `api.github.com`, `registry.npmjs.org`, `pypi.org`, and `files.pythonhosted.org`. Direct downloads from `gdr.openei.org` (`3D MT` Great Basin resistivity volumes, `H48-4`), `service.iris.edu` / `earthquake.usgs.gov` (relocated hypocenters, `H48-5`), and `asf.alaska.edu` (Sentinel-1 InSAR coherence, `H48-5`) are therefore **DATA-BLOCKED** until mirrored into a SHA-256-pinned GitHub release asset (`registry/data_manifest.json`).
2. **Score provenance (`IR-32-SCORE-01`):** Historical focus-site and `2026-10-26` scores are recorded as `OWNER-REPORT`; no organizer-signed portal receipt binding SHA-256 bytes to DrivenData submission IDs is stored in git.
3. **Calibration-lattice & continuous-surface literal rule (`IR-51-LATTICE-01`, `IR-48-WBG-SURFACE-01`):** `GEMSDOE24`'s `206,895`-dot 5-px calibration grid (`r13-lattice-s5`) covers `99.87%` of the footprint within `3 px`, and `WBGGEMSDOE1/2` store continuous `5.11M–5.17M`-pixel non-zero research surfaces (`within_3px = 100%` for any dot mask). Until `release_gate.compare_registry` formally restricts the `<=70%` dot-overlap check to discrete submission masks (`<=100,000` positive pixels, excluding calibration grids) and evaluates continuous surfaces solely by Spearman `|rho| <= 0.90`, all `37,654`-dot candidates remain fail-closed (`verdict: "negative"`, `ok_to_submit: false`).
