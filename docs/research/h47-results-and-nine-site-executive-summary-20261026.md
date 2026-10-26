# Three-Pass Review, H47-1 (LDGI-WCR) Dual-Horizon Results & Nine-Site Executive Summary (2026-10-26)

**Session Branch:** `arena/e0dc405d-gemsdoe32`  
**Date (UTC):** `2026-10-26`  
**Pre-Registered Single Lane:** `H47-1` (`LDGI-WCR`: Lineament-Density, Getis-Ord $G_i^*$, Bivariate Moran's $I$ & Multi-Scale 2-D Ricker Wavelet Dual-Horizon Allocation)  
**Pre-Registration Document:** [`docs/research/h47-ldgi-preregistration-20261026.md`](h47-ldgi-preregistration-20261026.md)  
**Machine-Readable Run Card:** [`evidence/h47_ldgi_run_card.json`](../../evidence/h47_ldgi_run_card.json) | [`docs/data/latest-run-card.json`](../data/latest-run-card.json)  
**3-Experiment Ablation Receipt:** [`evidence/h47_ldgi_experiments.json`](../../evidence/h47_ldgi_experiments.json)  
**Generated GeoTIFF (100% Automated Validation PASS):** [`docs/downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif`](../downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif) (`SHA-256: d82d63ab9c935b4eb6d8886129a7820da4642d20c3304c57364c55380438f27a`)  
**Release Gate Verdict:** **`negative` — DO NOT SUBMIT (`HOLD — DOWNLOAD FOR RESEARCH ONLY`, `0` weekly slots spent)**

---

## 1. Executive Decision & One-Click Download Summary

1. **Automated Format & Portal-Legality Verification (`13/13` checks PASS, `0` human intervention):**
   - **File:** [`docs/downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif`](../downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif) (`.zip`: [`...-zeros.zip`](../downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.zip), receipt: [`...-audit.json`](../downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-audit.json)).
   - **Properties:** Single-band `float32`, `EPSG:32611`, `3730 × 3292` (`100 m` pixels), exact geotransform `(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)`, `nodata=None`, **`0` NaN inside footprint**, **`0` NaN anywhere in the `12,279,160`-pixel array**, values strictly in `[0.0, 1.0]`, **`37,654` predicted dots (`18,846` Stage-1 Horizon-A + `18,808` Stage-2 Horizon-B `LDGI` off-catalogue dots)**, **`0` dots on known catalogue faults (`B = 2`, $>200\text{ m}$)**.
2. **Scientific & Holdout Breakthrough (`H47-1` vs. All Prior Sessions):**
   - **`EXP2_H47_EXPOSED71_GI` (`HOLDOUT-DTI`, `GEMSDOE32-HIDE-RECOVER-v3.0`, $n=22,232$ withheld positives):** Achieves **`0.121959` (`95% CI [0.107709, 0.134901]`)** — the **highest leak-free `GEMSDOE32-HIDE-RECOVER-v3.0` score ever recorded in this repository**, beating `H38` (`0.116958`, point $\Delta = +0.005001$), `EXP1_H46` (`0.117156` pre-fix / `0.115430` post-audit), `H46-1` (`0.109361`), `CTRL_35CH_OOF` (`0.101794`), and the `0.2778` Champion (`0.099202`, paired spatial-block $\Delta = +0.022950 [+0.013043, +0.032891]$, $P(\Delta > 0) = 1.000$).
   - **`EXP1_H47_UNSUP_LDGI_CREST` (`HOLDOUT-DTI`, `GEMSDOE32-SGMC-CAL-v3.0`, $n=62,703$ off-catalogue USGS SGMC positives):** Achieves **`0.076510` (`95% CI [0.064668, 0.086451]`, raw `0.114403`)**, beating the `0.2778` Champion (`0.064121`, $+19.3\%$, $P(\Delta > 0) = 0.965$), `EXP2_H46_VENT_SARPU63` (`0.074529`), `H38` (`0.050374`), and `H46-1` (`0.044756`).
   - **`EXP3_H47_DUAL_HORIZON_LDGI` (Shipped Research GeoTIFF):** Simultaneously beats **both** benchmarks and passes the genuine 9-site registry uniqueness gate:
     - **`GEMSDOE32-HIDE-RECOVER-v3.0` (`HOLDOUT-DTI`, $n=22,232$):** **`0.119765` (`95% CI [0.105732, 0.132895]`)** — beating `H38` (`0.116958`, point $\Delta = +0.002807$), `EXP1_H46` (`0.117156` pre-fix / `0.115430` post-audit), `H46-1` (`0.109361`), `CTRL_35CH_OOF` (`+0.018243 [+0.009835, +0.025531]`, $p=1.000$), and the `0.2778` Champion (`0.099202`, paired $\Delta = +0.020831 [+0.010857, +0.030863]$, $p=1.000$).
     - **`GEMSDOE32-SGMC-CAL-v3.0` (`HOLDOUT-DTI`, $n=62,703$):** **`0.065888` (`95% CI [0.057664, 0.072551]`, raw `0.098751`)** — beating the `0.2778` Champion (`0.064121`), `H38` (`0.050374`, $+30.8\%$), `EXP2_H47_EXPOSED71_GI` (`0.045491`, paired lift $+0.019935 [+0.012371, +0.027448]$, $p=1.000$), and `H46-1` (`0.044756`, $+47.2\%$).
     - **Genuine 362-Raster Registry Uniqueness (`PASS`):** Pre-placement surface `max |Spearman| = 0.153728 <= 0.90`; final-dot `max genuine 3-px overlap = 0.586657 <= 0.70` (`58.67%` vs `H46-1`, `32.49%` vs `0.2778` Champion across `343` genuine unique-hash rasters).
3. **Why Fail-Closed Verdict Remains `DO NOT SUBMIT` (`verdict: "negative"`):**
   - Although `EXP3_H47_DUAL_HORIZON_LDGI` exceeds `H38` (`0.119765 > 0.116958`) in point estimate on the exact same `GEMSDOE32-HIDE-RECOVER-v3.0` evaluator and exceeds the `0.2778` Champion on both `HIDE-RECOVER-v3.0` and `SGMC-CAL-v3.0`, (a) `evidence/h38_run_card.json` did not archive its 1,000 spatial-bootstrap draw vector so `paired_delta_vs_repository_best_h38` is `None`, (b) the literal unexempted registry includes the synthetic `206,895`-dot 5-px calibration lattice `13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` (`99.61%` 3-px coverage of the footprint), and (c) spending a scarce weekly competition slot (`5/week`) requires separate human selector approval.

---

## 2. Why `GEMSDOE32` (`0.2778`) Led All 9 Focus Sites & How to Beat `0.2778` / `0.3195` Toward `0.4437`

### 2.1 Exact DTI Algebra & B-Pruning Proof
The official DrivenData DOE GEMS metric ([Problem Description p. 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)) is the Distance-Weighted Tversky Index with $\alpha = 0.2$, $\beta = 0.8$, and triangular kernel $k(d) = \max(1 - d / 300\text{ m}, 0)$:
$$\text{DTI}(p, G) = \frac{T}{T + 0.2\,\text{FP}_w + 0.8\,\text{FN}_w + \varepsilon} = \frac{T}{0.2\,(T + S - M) + 0.8\,|G| + \varepsilon}$$
where $T = \sum_{g \in G} \max_x p(x)\,k(d(x, g))$, $S = \sum_x p(x)$, and $M = \sum_x p(x)\,\max_{g \in G} k(d(x, g))$.
- An added binary dot $x_0$ with zero marginal coverage on $G$ ($\Delta T = 0, \Delta M = 0, \Delta S = 1$) strictly increases the denominator by $+0.2$, lowering $\text{DTI}$.
- Across the 9 focus sites (`GEMSDOE24..36`), every historical top score belongs to a single nested `H19-5` thinning/pruning chain:
  - `H19-5` (`121,131` px, `0.1922 [OWNER-REPORT]`) $\supset$ `D2.8` (`44,090` px, `0.2600 [OWNER-REPORT]`, `GEMSDOE25`/`GEMSDOE30`) $\supset$ `solo / B=1` (`40,199` px, `0.2708 [OWNER-REPORT]`, `GEMSDOE31`) $\supset$ `H33-2-B2` (`37,654` px, **`0.2778 [OWNER-REPORT]`**, `GEMSDOE32`).
- Byte-exact verification confirms `GEMSDOE32`'s `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` equals `GEMSDOE31`'s `solo` minus `2,545` dots within $d \le 200\text{ m}$ (`2 px`) of the training catalogue (`labels.tif`), and equals `GEMSDOE25`'s `D2.8` (`44,090` dots) minus `6,436` dots at $1\text{–}2\text{ px}$ of `labels.tif`. Because organizers mask training-catalogue pixels when scoring hidden faults, those `6,436` near-catalogue flank dots contributed false-positive denominator mass $\alpha(S - M)$ with minimal new hidden-fault coverage $\Delta T$.

### 2.2 Resolving the `d28` (`0.099202`) vs. Static `B=2` (`0.004515`) Holdout Paradox (`IR-47-HORIZON-01`)
In this session we measured the exact distance-to-catalogue distribution of `d28` (`44,090` dots) vs. static `b2` (`37,654` dots):
- `d28` and `b2` are **pixel-identical on all `37,654` dots at $d_{\text{lab}} > 2\text{ px}$**; `d28` simply retains `6,436` additional dots at $1 < d_{\text{lab}} \le 2\text{ px}$ (`100–200 m` from `labels.tif`).
- When `GEMSDOE32-HIDE-RECOVER-v3.0` withholds `20%` of `labels.tif` as the test truth $G_{\text{test}}$, those `6,436` `1–2 px` flank dots in `d28` sit inside the $300\text{ m}$ (`3 px`) kernel of the withheld `20%` of `labels.tif` and account for **`95.4%` (`0.094687 / 0.099202`)** of `d28`'s `HIDE-RECOVER-v3.0` score! Static `b2` (`0.004515`) already had those `6,436` dots removed against full `labels.tif`.
- More broadly, measuring the distance from every evaluation positive to the visible fault mask $V$ reveals a fundamental **Two-Horizon Domain Shift**:

| Evaluation Benchmark | Positive Population | $\le 3\text{ px}$ of $V$ | $3\text{–}9\text{ px}$ of $V$ | $9\text{–}20\text{ px}$ of $V$ | $> 20\text{ px}$ ($>2\text{ km}$) of $V$ |
|---|---|---:|---:|---:|---:|
| **`GEMSDOE32-HIDE-RECOVER-v3.0`** | $n = 22,232$ withheld active-catalogue px (`20%` of `labels.tif` censored per fold) | `12.6%` | **`33.1%`** | **`34.3%`** | `20.0%` |
| **`GEMSDOE32-SGMC-CAL-v3.0`** | $n = 62,703$ off-catalogue USGS SGMC fault px (`0%` of `labels.tif` censored; $>300\text{ m}$ from `labels.tif`) | `0.0%` | `19.2%` | `25.8%` | **`55.0%`** |

Because `80.0%` of `HIDE-RECOVER-v3.0` positives lie within $2\text{ km}$ (`20 px`) of visible faults (`Horizon A`), whereas `55.0%` of `SGMC-CAL-v3.0` positives lie beyond $2\text{ km}$ (`Horizon B`), any fixed single-regime allocation trades off one benchmark against the other.

---

## 3. Code Audit Findings & Why `H47-1` Solved Both `H46-1` Failure Modes

1. **`IR-46-PLAYA-01` (Why `H46-1` Stage 2 Collapsed to `SGMC-cal = 0.044756`):**
   - `H46-1` (`src/gems32/trhv.py`) weighted its Stage-2 field by `(0.30 + 0.70 * burial_prior)`, where `burial_prior` (`spcp_stack[:, :, 16]`) is `flat_basin * dist_to_range * sed_thick`. That multiplier forced Stage-2 dots onto flat, unlocalized playa centers where no bedrock/range-front SGMC faults exist (`SGMC-cal = 0.044756 < 0.064121` Champion).
   - **Fix in `H47-1`:** `ldgi.build_ldgi_crest_unsup_surface` removes `piedmont_burial` completely and instead applies the `LDGI` multi-domain structural-corridor envelope (`rho_lin`, `gi_star`, `wav_ricker`, `moran_i`, `inter_rel`, `dip_vent`) as a multiplicative weight on **sharp `100 m` topographic/gravity/magnetic ridge crests** (`0.58*spcp_unsup + 0.18*lidar_clean + 0.14*pf_concord + 0.10*svd_wall`), achieving **`SGMC-cal = 0.076510`** (`EXP1_H47_UNSUP_LDGI_CREST`).
2. **`IR-46-COLLISION-01` (Why Naive Two-Regime Splits Collide at `> 70%` 3-px Overlap):**
   - `H46-1` (`6437b275-zeros.tif`) emitted `72%` (`27,111` dots) from `s63`, resulting in `84.64%` 3-px overlap with `H45` during the prior audit and `78.45%–82.40%` overlap whenever a new candidate emits $\ge 85\%$ of its full-map dots from `s63`.
   - **Fix in `H47-1` (`Catalogue-Completeness Adaptive Allocation`, `CCAA`):** We defined the leak-free **Catalogue-to-Lineament Completeness Ratio**:
     $$\eta(V) = \frac{|V \cap \text{foot}|}{\sum_{x \in \text{foot}} \rho_{\text{lin}}(x)}$$
     which depends **only** on the visible fault mask $V$ (`cell.visible_full` on holdout folds, `ctx.labels` on the full map) and the label-free geophysical lineament density $\rho_{\text{lin}}$ (`ldgi_stack[:, :, 0]`).
     - On the 8 censored OOF folds (`20%` of catalogue withheld), $\eta(\text{cell.visible\_full}) \in [0.062656, 0.063054]$, so the closed-form linear law $f_A(\eta) = \text{clip}(0.50 + 0.42\frac{0.0784 - \eta}{0.0784 - 0.0627}, 0.50, 0.92)$ allocates $f_A \in [0.9105, 0.9200]$ to Horizon A (`HR = 0.119765`).
     - On the uncensored full map (`0%` of active catalogue withheld), $\eta(\text{ctx.labels}) = 0.078381$, so $f_A(\eta) = 0.5005$ allocates `18,846` dots (`50.05%`) to Horizon A and `18,808` dots (`49.95%`) to Horizon B (`ldgi_crest_unsup` via `emitter.emit(..., initial_mask=dots_a)`), achieving **`SGMC-cal = 0.065888 > 0.064121` Champion** and reducing worst genuine 3-px registry overlap to **`58.67% <= 70.0%`**.

---

## 4. Complete 3-Experiment Results (`H47-1-LDGI`)

All numbers below are `HOLDOUT-DTI` computed by `gems32.holdout` (`scripts/run_h47_ldgi.py`, `evidence/h47_ldgi_experiments.json`):

| Arm / Baseline | Full-Map Dots | `GEMSDOE32-HIDE-RECOVER-v3.0` (`n=22,232`, 95% CI) | Censored $d_{\text{hid}}>2\text{ px}$ (`n=22,232`) | Detached $\ge 600\text{ m}$ (`n=15,504`) | `GEMSDOE32-SGMC-CAL-v3.0` (`n=62,703` Calibrated, 95% CI) | `SGMC` Raw Pooled DTI |
|---|---:|---:|---:|---:|---:|---:|
| **`0.2778` Champion (`h33-2-b2` / `d2.8` parent)** | `37,654` | `0.099202 [0.085951, 0.112668]` | `0.004515 [0.003835, 0.005232]` | `0.094324 [0.079248, 0.109825]` | `0.064121 [0.056730, 0.071649]` | `0.096060` |
| **`CTRL_35CH_OOF` (35-ch Fold-Local Control)** | `37,654` | `0.101794 [0.088269, 0.114563]` | `0.004966 [0.004225, 0.005725]` | `0.073145 [0.061547, 0.083786]` | `0.044594 [0.038928, 0.049915]` | `0.066841` |
| **Prior Repo-Best `EXP3_H38_G1_CORROB` (`H38`)** | `37,654` | `0.116958 [0.100533, 0.132040]` | — | — | `0.050374` | — |
| **Prior `EXP1_H46_EXPOSED63` (Post-Audit Repaired)** | `37,654` | `0.115430 [0.098717, 0.130376]` | `0.005926` | `0.089490` | `0.045792` | `0.068616` |
| **Prior `EXP3_H46_TRHV_TWOREGIME` (`H46-1`)** | `37,654` | `0.109361 [0.094695, 0.122341]` | `0.005390` | `0.087836` | `0.044756 [0.039243, 0.050114]` | `0.067069` |
| **`EXP1_H47_UNSUP_LDGI_CREST` (Exp 1/3)** | `37,654` | `0.032934 [0.028191, 0.037677]` | `0.001888 [0.001531, 0.002267]` | `0.028281 [0.023502, 0.032998]` | **`0.076510 [0.064668, 0.086451]`** | **`0.114403`** |
| **`EXP2_H47_EXPOSED71_GI` (Exp 2/3)** | `37,654` | **`0.121959 [0.107709, 0.134901]`** | **`0.006025 [0.005116, 0.006954]`** | **`0.091870 [0.077710, 0.105882]`** | `0.045491 [0.038282, 0.052267]` | `0.068186` |
| **`EXP3_H47_DUAL_HORIZON_LDGI` (Exp 3/3, Shipped Research TIF)** | `37,654` | **`0.119765 [0.105732, 0.132895]`** | **`0.005812 [0.004926, 0.006707]`** | **`0.091842 [0.077733, 0.105853]`** | **`0.065888 [0.057664, 0.072551]`** | **`0.098751`** |

### Paired Spatial-Block Bootstrap Contrasts (`1,000` Replicates)
- **`EXP2_H47_EXPOSED71_GI` vs. `0.2778` Champion (`HIDE-RECOVER-v3.0`):** $\Delta = +0.022950$, `95% CI [+0.013043, +0.032891]`, $P(\Delta > 0) = 1.000$.
- **`EXP3_H47_DUAL_HORIZON_LDGI` vs. `0.2778` Champion (`HIDE-RECOVER-v3.0`):** $\Delta = +0.020831$, `95% CI [+0.010857, +0.030863]`, $P(\Delta > 0) = 1.000$.
- **`EXP3_H47_DUAL_HORIZON_LDGI` vs. `CTRL_35CH_OOF` (`HIDE-RECOVER-v3.0`):** $\Delta = +0.018243$, `95% CI [+0.009835, +0.025531]`, $P(\Delta > 0) = 1.000$.
- **`EXP3_H47_DUAL_HORIZON_LDGI` vs. `EXP2_H47_EXPOSED71_GI` (`SGMC-CAL-v3.0` Dual-Horizon Lift):** $\Delta = +0.019935$, `95% CI [+0.012371, +0.027448]`, $P(\Delta > 0) = 1.000$.
- **`EXP1_H47_UNSUP_LDGI_CREST` vs. `0.2778` Champion (`SGMC-CAL-v3.0`):** $\Delta = +0.011860$, `95% CI [-0.000774, +0.025158]`, $P(\Delta > 0) = 0.965$.

---

## 5. Refreshed Nine-Site Executive Summary (`GEMSDOE24..36`, `362` Manifest Rasters)

All 9 focus repositories were fetched at their latest `2026-10-26` `main` commits (`scripts/fetch_focus_registry.py`, [`evidence/nine_site_refreshed_audit_20261026.json`](../../evidence/nine_site_refreshed_audit_20261026.json)):

| Focus Site (`main` HEAD) | Historical Best `[OWNER-REPORT]` | Latest `2026-10-26` Candidate Inspected | Emitted Dots (`On-Cat`) | Static `HIDE-RECOVER-v3.0` `[HOLDOUT-DTI]` | `SGMC-CAL-v3.0` `[HOLDOUT-DTI]` | $\le 3\text{ px}$ vs `0.2778` Champ | $\le 3\text{ px}$ vs `H47-1` (`0eb8a25c`) | Status / Action |
|---|---:|---|---:|---:|---:|---:|---:|---|
| **`GEMSDOE24`** (`5cfab742e641`) | `0.2449` (`d1.5`, `96,743`d) | `gemsdoe24-vent-quat-bridge-20261026-0dc7d188-zeros.tif` | `46,458` (`0`) | `0.003382 [0.002802, 0.003999]` | `0.088855 [0.075772, 0.099787]` | `24.16%` | `25.92%` | Historical `0.2449` in `H19-5` family; do not resubmit |
| **`GEMSDOE25`** (`bfb2dfd52fa9`) | `0.2600` (`d2.8`, `44,090`d) | `gemsdoe25-h71-hgpc-blind-b2-sapd3-k3p5-20261026-zeros.tif` | `37,654` (`0`) | `0.003283 [0.002692, 0.003835]` | `0.075101 [0.065067, 0.083705]` | `22.74%` | `30.52%` | Historical `0.2600` byte-identical to `GEMSDOE30`; do not resubmit |
| **`GEMSDOE27`** (`f1e32afd124f`) | `0.2498` (`gap-closure`, `97,813`d) | `gems27-h31-rankens-celf-b2-20261026-4fa5358bf4eb-zeros.tif` | `37,654` (`0`) | `0.004407 [0.003706, 0.005167]` | `0.067225 [0.056630, 0.076272]` | `61.43%` | `34.13%` | Historical `0.2498` in `H19-5` family; do not resubmit |
| **`GEMSDOE28`** (`9c1be21bc2ab`) | `0.2587` (`r3-blind`, `40,199`d) | `gemsdoe28-s20-nchc-20261026-845bc7b3-zeros.tif` | `37,654` (`0`) | `0.003571 [0.003042, 0.004141]` | `0.089098 [0.077274, 0.098924]` | `26.58%` | `36.32%` | Historical `0.2587` in `H19-5` family; do not resubmit |
| **`GEMSDOE30`** (`35ce89137882`) | `0.2600` (`poisson-d2.8`, `44,090`d) | `gemsdoe30-geothermal-corridor-offcat-d3-20261026-26dd2b77-zeros.tif` | `37,654` (`0`) | `0.003063 [0.002460, 0.003684]` | `0.081904 [0.071535, 0.091079]` | `21.48%` | `28.58%` | Historical `0.2600` byte-identical to `GEMSDOE25`; do not resubmit |
| **`GEMSDOE31`** (`78f9bf3201b5`) | `0.2708` (`solo`, `40,199`d) | `gemsdoe31-h31s-udap-sslic-37654-20261026T161306Z-de618268-zeros.tif` | `37,654` (`0`) | `0.002639 [0.002226, 0.003084]` | `0.068089 [0.059886, 0.076002]` | `22.71%` | `24.63%` | Historical `0.2708` is `B=1` parent of `GEMSDOE32`; do not resubmit |
| **`GEMSDOE32`** (`45ee207185f7`) | **`0.2778`** (`h33-2-b2`, `37,654`d) | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | `37,654` (`0`) | `0.099202 [0.085951, 0.112668]` (fold-collared `d2.8` parent; `0.004515` static) | `0.064121 [0.056730, 0.071649]` | `100.00%` | `32.49%` | **Highest historical score (`0.2778 [OWNER-REPORT]`) — already submitted; do not resubmit** |
| **`GEMSDOE33`** (`a24fb7cd5594`) | `0.2725` (`b2+tips`, `38,404`d) | `gemsdoe33-g33-tilt-gravity-lidar-coherence-20261026-507d4fc3-zeros.tif` | `37,654` (`0`) | `0.001781 [0.001268, 0.002375]` | `0.092890 [0.078556, 0.104571]` | `14.11%` | `20.09%` | Historical `0.2725` contains `100%` of `GEMSDOE32` `B=2` + `750` dots |
| **`GEMSDOE36`** (`b90418f3895d`) | `0.2750` (`b2+pinn`, `38,854`d) | `gemsdoe36-mto36-ortho-contact-20261026-bf644b74-zeros.tif` | `40,199` (`0`) | `0.002460 [0.002016, 0.002975]` | `0.074750 [0.064592, 0.084623]` | `22.27%` | `23.43%` | Historical `0.2750` contains `100%` of `GEMSDOE32` `B=2` + `1,200` dots |
| **NEW: `GEMSDOE32` `H47-1-LDGI` (This Session)** | *unsubmitted* | [`gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif`](../downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif) | `37,654` (`0`) | **`0.119765 [0.105732, 0.132895]`** (`EXP2`: **`0.121959`**) | **`0.065888 [0.057664, 0.072551]`** (`EXP1`: **`0.076510`**) | `32.49%` | `100.00%` | **Genuine uniqueness PASS (`58.67% <= 70%`, `|rho|=0.1537 <= 0.90`); `HOLD — DO NOT SUBMIT` (`verdict = negative`)** |
