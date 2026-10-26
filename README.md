# GEMSDOE32 — Auditable Concealed-Fault Discovery & Automated Submission System for the DOE GEMS Prize (DrivenData #306)

**Competition:** [DOE GEMS Prize](https://www.drivendata.org/competitions/306/competition-doe-gems/) · **Problem Description:** [Page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · **Official Rules (PDF):** [docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf) · **Live Site:** <https://buffedlizard55-lab.github.io/GEMSDOE32/> · **Executive Summary & How to Submit:** [docs/executive-summary.html](docs/executive-summary.html)

---

## 🔴 CURRENT SUBMISSION VERDICT (`2026-10-26`, Round 6): `DOWNLOAD FOR RESEARCH: YES · SUBMIT TO LIVE PORTAL: NO` (`verdict = negative`)

> **Unambiguous Automated Gate Verdict (Zero Human Inspector Required):**
> - **Newly Generated Unique Competition GeoTIFF (`H36-1C`, `2026-10-26`):** **OK TO DOWNLOAD FOR LOCAL / GIS / RESEARCH AUDIT (`download_ok = true`) · DO NOT UPLOAD TO DRIVENDATA (`ok_to_submit = false`, `verdict = negative`, `0` weekly slots spent).**
> - **Best Leaderboard Score Across All 9 Focus Sites (`GEMSDOE24..36`):** **`GEMSDOE32`'s `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (`0.2778` owner-reported live score, `37,654` dots)** — **already submitted and scored; do NOT re-upload it** (re-uploading wastes 1 of 3 weekly slots for zero information). Across all 9 focus repositories today, **spend `0` live submission slots**.

### ⬇ One-Click Validated Round-6 Deliverables (`GEMSDOE32-H36-1C-TDR-PDS-9FF9D6E2`)
- **[⬇ Download Primary All-Finite `[0, 1]` GeoTIFF (`gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif`, `206,761 B`)](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif)**
- **[⬇ Download Single-TIFF `.ZIP` Archive (`gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.zip`, `171,140 B`)](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.zip)**
- **[⬇ Download Masked Companion GeoTIFF (`-nan.tif`, `NaN` outside footprint)](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-nan.tif)**
- **[13-Point Automated Format & Range Receipt (`-audit.json`)](docs/downloads/gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-audit.json)** · **[Canonical JSON Run Card (`evidence/h36_tdr_pds_run_card.json`)](evidence/h36_tdr_pds_run_card.json)** · **[Exact Protocol Audit (`docs/data/protocol-audit.json`)](docs/data/protocol-audit.json)**
- **Historical `0.2778` Fleet Champion Reference (already scored — DO NOT re-submit):** [`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) (`sha256: e5eb6e7e380d98ad72a53c1bc4a1a9427042240d33fb85633da21b9d254ac94d`)

### Artifact Identification & Automated Gate Scorecard
- **Unique Submission Name:** `GEMSDOE32-H36-1C-TDR-PDS-9FF9D6E2`
- **Short Portal Note (`118 / 140` chars):**  
  `H36-1C TDR-PDS+Steger 37654d | HOLDOUT-DTI 0.1098 [0.0987,0.1227] v3-vis 22232pos | SGMC 0.0838<0.0961 | DO NOT SUBMIT`
- **Primary GeoTIFF SHA-256:** `f75ac7ae172eed0840b948beaa6587a532c0a44453c3ad90874f02967e0a887c`
- **Automated Non-Human Format Gate:** **PASS (`13/13`)** — `EPSG:32611`, `3730 × 3292` (`100 m`), single-band `float32`, `nodata = None`, all `12,279,160 / 12,279,160` cells finite in `[0.0, 1.0]`, `0` NaNs anywhere (permanently eliminating `"Predicted values must be in range [0, 1]"`), `37,654` emitted dots, `0` dots on `existing_faults.tif` or inside its `200 m` (`B = 2`) dead annulus.
- **Single-Feature Holdout Leakage Canary:** **PASS (`46/46` features)** — worst oriented holdout ROC-AUC = **`0.58412 <= 0.90`** (`dem_break_neg`); `dist_known_fault_px` strictly excluded from all CSV inputs.
- **Uniqueness vs. All `44` Genuine Submission/Detector Rasters (`GEMSDOE`..`GEMSDOE36`):** **PASS** — pre-placement surface `max |Spearman| = 0.15949 <= 0.90`; final `37,654` dots `max <=3 px overlap = 60.44% <= 70%` (`52.20%` vs. `0.2778` Champion; `83.84%` of dots sit completely off `H19-5`).
- **Why Verdict Is `NEGATIVE` (`DO NOT SUBMIT`):**
  1. **Holdout Honesty Across Instruments:** On repaired visible-only hide-and-recover (`GEMSDOE32-HOLDOUT-v3-visible-gated`, `22,232` withheld positives), `H36-1C` achieves **`HOLDOUT-DTI = 0.10982` `[0.09866, 0.12275]`** vs. raw Champion `0.09920` `[0.08202, 0.12219]`. However, `H19-5`/Champion had `d_catalogue == 0` zeroed prior to export (`IR-32-FIELD-01`); under identical `d_hidden == 0` censorship `H36-1C` scores **`0.07639 < 0.09920`**, and on independent off-catalogue USGS SGMC blind faults (`62,703` pixels `> 300 m` from `existing_faults.tif`, where Champion has zero masking handicap) `H36-1C` scores **`HOLDOUT-DTI = 0.08380` `[0.06079, 0.10993]` < Champion `0.09606` `[0.08482, 0.10773]`**.
  2. **Unmodified Literal Calibration-Lattice Gate (`IR-32-LATTICE-01`):** Under `src/gems32/release_gate.py` (no density exemptions), the non-geological synthetic $5\mathbb{Z}\times 5\mathbb{Z}$ calibration grid `13gems_20261001_r13-lattice-s5_v2_nan-outside.tif` (`206,895` dots, Euclidean covering radius $\sqrt{8} = 2.828 < 3.0\text{ px}$) covers `99.8713%` of the footprint, so `H36-1C` (`99.80% > 70%`) triggers a mandatory fail-closed stop.

---

> ### Our Core Values — kept central to every decision in this repository
> **Maximize P(Win).** *"Maximize the Probability of Winning"* is our decision-making framework. In every decision we weigh tradeoffs, assess risk, and choose the path that maximizes the probability that we win this prize. We set aside our emotions and make tough decisions in order to maximize P(Win). It frees us from constraints and clarifies that we must put the outcome first.
>
> **Own the Outcome.** We own results end to end — not just our individual slice of the work. When problems arise and we have the means to act, we act without waiting for permission or assignment. We treat failure and success as signals and use them to improve. We stay accountable to the final outcome.

---

## 🎯 Executive Summary Across the 9 Focus Sites (`2026-10-26`)

Every site below was audited directly against its GitHub `main` tree and pixel-compared against the shared GeoTIFF registry:

| Focus Site & Verified Repo | Latest Audited `HEAD` | Best Historical Scored File & Owner-Reported Score | Byte-Level Uniqueness / Duplicate Forensics | Latest `2026-10-26` Unique Research TIF | Actionable Verdict |
|---|---|---|---|---|---|
| **[GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32)** *(this repo)* | Active branch `arena/8e9171d6-gemsdoe32` | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` — **`0.2778` (FLEET #1)**, `37,654` dots (`h36-1-rung30`: `0.2710`; `h38-1-hf-euler`: `0.2707`) | **Canonical `B=2` Optimum** (`solo & (d_cat > 2)` = `d2.8 & (d_cat > 2)`). **Already scored — DO NOT re-upload** | `gemsdoe32-h36-1c-tdr-pds-steger-37654-20261026T012000Z-9ff9d6e2-zeros.tif` (`37,654` dots; **unique vs. 44 genuine detectors**: max `<=3 px` overlap `60.44%`, `|\rho| = 0.1595`) | **DOWNLOAD YES · SUBMIT NO** (`verdict = negative`) |
| **[GEMSDOE36](https://github.com/buffedlizard55-lab/GEMSDOE36)** | `a4c660a8` | `gemsdoe36-anderson-friction-pinn-b2-swap1200-20261005-a2a0b857-zeros.tif` — **`0.2750`**, `38,854` dots | **96.91% Exact-Pixel Superset Duplicate** of `GEMSDOE32` Champion (`37,654` Champion dots + `1,200` extra dots costing `-0.0028`; `IR-32-FAM-01`) | `gemsdoe36-h36-gps-graben-pair-20261026-bb29ce2a4bb4-zeros.tif` (`89.85% > 70%` overlap; `HOLDOUT-DTI 0.1320 < 0.1488`) | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE28](https://github.com/buffedlizard55-lab/GEMSDOE28)** | `94152be6` | `gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif` — **`0.2708`**, `40,199` dots | **100% Dot-Identical Twin** of `GEMSDOE31` `solo` (`d2.8 & (d_cat > 1)`, `0` symmetric pixel difference) | `gems28-s20-vesselness-lidarstep-20261026-7a7c5e44` (`37,500` dots; `HOLDOUT-DTI 0.08631 < 0.09881`) | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE31](https://github.com/buffedlizard55-lab/GEMSDOE31)** | `6ca63b0c` | `gems31-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan.tif` — **`0.2708`**, `40,199` dots | **100% Dot-Identical Twin** of `GEMSDOE28` `solo` (`0` symmetric pixel difference) | `gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif` (`37,654` dots; `HOLDOUT-DTI 0.04588 < 0.04812`) | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE33](https://github.com/buffedlizard55-lab/GEMSDOE33)** | `7deca206` | `GEMSDOE33-h33d-skel-b1-trim-t0p030-20261004-c309b3e826ae-zeros.tif` — **`0.2632`**, `41,865` dots | **Nested `H19-5` Family Trim** (`B=1` skeleton trim, `41,865` dots) | *Audit/feature restoration run; no new TIF emitted* | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE25](https://github.com/buffedlizard55-lab/GEMSDOE25)** | `de77cb6c` | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` — **`0.2600`**, `44,090` dots | **100% Dot-Identical Twin** of `GEMSDOE30` `poisson300m` (`IR-32-FAM-02`; `0` symmetric pixel difference) | *Designed-factorial ROD evaluation (`OK TO SUBMIT: NO`)* | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE30](https://github.com/buffedlizard55-lab/GEMSDOE30)** | `ac54b7f3` | `gems30-h19-5-poisson300m-20261002-144f41d11fd4-nan.tif` — **`0.2600`**, `44,090` dots | **100% Dot-Identical Twin** of `GEMSDOE25` `d2.8` (`IR-32-FAM-02`) | `gems30-PTA1-44090-20261025-9a3f7f9535a4.tif` (`44,090` dots; unique across `196` rasters; negative gate stop) | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE24](https://github.com/buffedlizard55-lab/GEMSDOE24)** | `2a2b9829` | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` — **`0.2194`**, `77,507` dots | **Dense `d=1.5` Ancestor** in `H19-5` family (`GVC1` `37,654`d unsubmitted corridor duplicate) | `gems24-crp1-compfront-xdepth-saddle-20261026-c679a967f700-zeros.tif` (`80.7% > 70%` overlap; `HOLDOUT-DTI 0.1375 < 0.1488`) | **DO NOT SUBMIT** (`negative`) |
| **[GEMSDOE27](https://github.com/buffedlizard55-lab/GEMSDOE27)** | `398cda94` | `H29-S (511898747886)` **`0.2190`** (`37,654` dots); `gems27-topo-gap-closure` **`0.2186`** (`78,763` dots) | `H29-S` is the **highest live-scored pure OOF ML surface outside `H19-5`** (`0.2190 < 0.2778`) | `gems27-h31-rankens-celf-b2-20261026-93c8af046660-allfinite.tif` (`37,654` dots; `HOLDOUT-DTI 0.03671 < 0.04402`) | **DO NOT SUBMIT** (`negative`) |

---

## 🔬 PhD-Level Analysis: Why `h33-h33-2-b2` Scored `0.2778`, Its Exact Ceiling, and How to Reach `0.3195` & `0.4413`

### 1. Exact Metric Algebra & Hidden Test Population Inversion
DrivenData scores submissions with the pooled Distance-Weighted Tversky Index ($\alpha = 0.2$, $\beta = 0.8$, $R = 300\text{ m} = 3\text{ px}$ triangular kernel $k(d) = \max(0, 1 - d/3)$, with known `existing_faults.tif` pixels masked out pixel-exactly before distance evaluation):
$$\text{DTI} = \frac{T}{T + 0.2 F + 0.8 (|G| - T)} = \frac{T}{0.8 T + 0.2 |P| + 0.8 |G|}$$
where $|P|$ is off-catalogue emitted mass, $|G|$ is hidden test fault pixel count, and $T = \sum_{g \in G} k(d(g, P))$. Adding $\Delta n$ dots with mean marginal credit $\bar{c} = \Delta T / \Delta n$ improves $\text{DTI}$ if and only if:
$$\bar{c} > \frac{0.2\,\text{DTI}}{1 - 0.8\,\text{DTI}} \quad \text{(exact finite-coverage form; } k > 0.2\,\text{DTI under } TP+FP=|P|\text{)}$$

Inverting our nested `H19-5` family (`src/gems32/live_anchor.py`) yields **`|G| ≈ 12,265` hidden test pixels (~1,226 km of unmapped fault strike, `0.24%` of footprint)**:
1. **`H19-5` (`121,131` px, `0.1922`):** Solid 1-px ridge covers $T_{\text{solid}} \approx 5,021$ (`40.9%` of $|G|$), drowned by $0.2 \times 121,131 = 24,226$ denominator units.
2. **`D2.8` (`44,090` px, `0.2600`, `GEMSDOE25` ≡ `GEMSDOE30`):** 2.8-px spacing along `H19-5` cuts $|P|$ by `-63.6%` (`-77,041` dots, saving `15,408` denominator units) while retaining `~90%` of $T_{\text{solid}}$ via overlapping $300\text{ m}$ triangular kernels.
3. **`Solo` (`40,199` px, `0.2708`, `GEMSDOE28` ≡ `GEMSDOE31`):** `D2.8 & (d_cat > 1)` removes `3,891` dots immediately adjacent (`d = 100 m`) to `existing_faults.tif` (realized credit `~0.0056/dot`, `10×` below break-even).
4. **`Champion h33-h33-2-b2` (`37,654` px, `0.2778`, `GEMSDOE32`):** `Solo & (d_cat > 2)` removes `2,545` more flank dots at $d \in \{\sqrt{2}, 2\}\text{ px}$ (`1,201` diagonal + `1,344` orthogonal; realized credit `~0.0156/dot < 0.0556` break-even), saving `509` denominator units at $T \approx 4,503$ (`36.7%` weighted recall).
5. **Why `B = 3` and `GEMSDOE36` (`0.2750`) Regress:** Our repaired `GEMSDOE32-HOLDOUT-v3-visible-gated` evaluator proves empirically (`tests/test_holdout_visible_gate.py`) that `HOLDOUT-DTI` rises monotonically from `H19-5` (`0.06879`) $\to$ `B=0` (`0.09674`) $\to$ `B=1` (`0.09898`) $\to$ **`B=2` (`0.09920`, peak)** and **drops at `B=3` (`0.09710`)** because hidden fault splays branch outside $200\text{ m}$. Meanwhile, `GEMSDOE36` kept all `37,654` Champion dots and added `1,200` low-yield dots, losing `-0.0028`.

### 2. Impossibility Theorem for `H19-5` Thinning vs. `0.3195` and `0.4413`
Because the entire un-thinned `121,131`-pixel `H19-5` support captures only $T_{\text{solid}} \approx 5,021$ (`40.9%` of $|G|$):
- Reaching **`0.3195`** (prior Phase-1 leaderboard benchmark) at $|P| = 37,654$ requires **$T \approx 5,430$ (`44.3%` weighted recall > $T_{\text{solid}}$)**.
- Reaching **`0.4413`** (current public leaderboard #1 `xiaofanhu`, `IR-32-SCORE-03`) at $|P| = 37,654$ requires **$T \approx 8,408$ (`68.6%` weighted recall)** — or even at $|P| = 25,000$ requires **$T \approx 7,172 > 5,021$**.

**Conclusion:** **No subset, thinning, or re-spacing of `H19-5` can ever reach `0.3195` or `0.4413`** (hard theoretical ceiling on `H19-5` is `~0.305–0.312`). Beating `0.2778` toward `0.3195–0.4413` requires discovering **~93–340 km of genuinely unmapped fault strike** off `H19-5` — specifically blind basin/piedmont faults (~39% of known and ~75% of undiscovered Great Basin geothermal systems; [Faulds et al., OSTI 1148722](https://www.osti.gov/biblio/1148722)) and unmapped modern ruptures such as the 2020 $M_w\ 6.5$ Monte Cristo Range sequence (`DOI: 10.1785/0220200371`).

---

## 🌋 Pre-Registered Round-6 Geological Hypotheses (`H36-1` .. `H36-5`) & Measured 3-Experiment Results

Full pre-registration written *before* running experiments: [`docs/research/hypotheses-round6-20261026.md`](docs/research/hypotheses-round6-20261026.md). Two byte-verified physical discoveries anchor Round 6:
1. **`IR-32-BAND-02`:** `training_features.tif` Band 6 (`tc`, `[+2.95, +88.6]`) correlates at **$\rho = +0.99942$** with GeoDAWN **Radiometric Total Count (`TC`)**, *not* magnetic tilt angle — explaining why prior tilt zero-crossing attempts on Band 6 failed (`AUC = 0.5058`). True Miller & Singh (1994) tilt angles $\arctan(\text{tmi\_vg}/\text{tmi\_hg})$ (Bands 9 & 3) and $\arctan(\text{iso\_grav\_anom\_vg}/\text{iso\_grav\_anom\_slope})$ (Bands 11 & 5) are computed here for the first time in `GEMSDOE32`.
2. **`IR-32-BAND-03`:** Band 18 (`iso_grav_anom_hg`) correlates at **$\rho = +0.9438$** with signed east–west $\partial g/\partial x$ ($\rho = +0.0273$ with $\partial g/\partial y$), encoding synthetic vs. antithetic half-graben polarity across accommodation zones.

| Rank | ID | Hypothesis | Layers | Physical Signature & Transform | Expected Gain / Cost / Data Availability | Status |
|---:|---|---|---|---|---|---|
| **1** | **`H36-1`** *(Selected Lane)* | **True Potential-Field Tilt-Phase, Depth-Persistent Magnetic & Piedmont-Drainage Curvilinear Skeleton (`TDR-PDS`)** | Official Bands `2,3,5,6,7,8,9,11,12,13,15,17,18,19`; `geodawn_extensions_u8.tif` (`Th/K, U/K, U/Th, TMI_up150`); `lidar_scarp_features_u8.tif` | True Miller–Singh magnetic/gravity tilt zero-crossing crests + `TMI_up150` survival + signed $\partial g/\partial x$ polarity reversal + 16-azimuth valley chains + 1 m LiDAR scarplet asymmetry $\to$ 500 m halo-excluded PU spatial-CV HistGB $\to$ Steger 1-px curvilinear crest NMS $\to$ `B=2` lazy-greedy 300 m emitter (`37,654` dots) | `+0.005..+0.020` over `H-CVF2` · Low–Med CPU · **100% locally cached & SHA-256 verified** | **EVALUATED (3/3 exps) $\to$ Unique TIF (`9ff9d6e2`), Verdict `NEGATIVE`** |
| **2** | **`H36-2`** | **Quaternary Volcanic-Vent & Geothermometer Azimuthal Feeder Corridors** | `gdr_volcanic_vents_in_footprint.csv` (`21` vents), `gdr_wellspring_in_footprint.csv` (`temp_c, geothermquartz_c, geothermchalc_c`; **`dist_known_fault_px` excluded**), Bands `2, 8` | $\sigma_3$-perpendicular NNE–SSW structural corridors linking off-catalogue Quaternary vents (`21/21 > 300 m`) and $\ge 60^\circ\text{C}$ geothermometers along RTP magnetic ridges | `+0.002..+0.008` · Low CPU · **100% locally cached** ([DOE GDR #1391](https://gdr.openei.org/submissions/1391)) | Evaluated inside `H36-1` (`AUC <= 0.90`) |
| **3** | **`H36-3`** | **Upward-Continuation Spectral Attenuation Ratio (`TMI_0` vs. `TMI_up150`)** | Band `3 (tmi_hg)`, `geodawn_extensions_u8.tif` Band `4 (TMI_up150)` | $|\nabla_h \text{TMI}_{\text{up150}}| / (\text{zpos}(\log(1+\text{tmi\_hg})) + 0.35)$ isolating deep basement faults from surficial volcanic float | `+0.003..+0.010` · Low CPU · **100% locally cached** (`DOI: 10.5066/P93LGLVQ`) | Evaluated inside `H36-1` (`AUC <= 0.90`) |
| **4** | **`H36-4`** | **Elevation-Residualized Radiometric `K/Th` + `U/Th` Redox Fronts & MT Clay-Cap Edges** | Band `6 (tc)`, `geodawn_extensions_u8.tif` (`Th/K, U/K, U/Th`), Bands `12, 17` | Elevation-residualized potassic alteration (`-Th/K`) + `|\nabla(U/Th)|` co-aligned with `|\nabla\log(1+\text{cond\_surf})|` | `+0.001..+0.006` · Low CPU · **100% locally cached** | Evaluated inside `H36-1` (`AUC 0.5456 <= 0.90`) |
| **5** | **`H36-5`** *(DATA-BLOCKED)* | **Relocated Microseismicity 3-D Plane Projection + 2020 Monte Cristo InSAR Phase Ridges** | USGS ComCat FDSN relocated hypocenters, Ruhl et al. (2021) catalog, ARIA/ASF Sentinel-1 unwrapped interferograms | 3-D RANSAC hypocentral fault-plane updip projection + coseismic InSAR phase-gradient discontinuities | `+0.008..+0.025` · Med CPU · **Blocked by sandbox egress** (`earthquake.usgs.gov` / `zenodo.org` / `asf.alaska.edu` unreachable here) | Registered; **not proposed as viable in sandbox** |

### Measured 3-Experiment Progression (`GEMSDOE32-HOLDOUT-v3-visible-gated`, Matched `37,654` Full-Map Dots)

| Arm / Experiment (`3/3` Budget Cap) | `HOLDOUT-DTI` (`v3` Visible-Gated Pooled, `22,232` withheld positives) | 95% Block-Bootstrap CI | Censored-`d=0` Control (`IR-32-FIELD-01`) | Off-Catalogue `SGMC` Raw `HOLDOUT-DTI` (`62,703` blind faults `>300 m`) | Off-Catalogue `SGMC` Calibrated `HOLDOUT-DTI` |
|---|---:|---|---:|---:|---:|
| **Baseline: `0.2778` Champion (`h33-h33-2-b2`)** | `0.09920` | `[0.08202, 0.12219]` | `0.09920` | **`0.09606`** `[0.08482, 0.10773]` | **`0.06412`** |
| **Exp 1 — `H36-1A` (Unsupervised Multi-Physics Crest)** | `0.06380` | `[0.04994, 0.07726]` | `0.04336` | **`0.16421`** *(+70.9% vs. Champ)* | **`0.11054`** |
| **Exp 2 — `H36-1B` (500 m Halo-Excluded PU HistGB + Steger)** | `0.10482` | `[0.09502, 0.11770]` | `0.07410` | `0.06832` | `0.04542` |
| **Exp 3 — `H36-1C` (Geometric-Mean Hybrid + Steger Crest)** | **`0.10982`** | **`[0.09866, 0.12275]`** | `0.07639` | `0.08380` `[0.06079, 0.10993]` | `0.05585` |

---

## 🛠️ Root Cause & Permanent Prevention of `"Predicted values must be in range [0, 1]"`

1. **Mechanism 1 — Whole-Array `NaN` Comparison Trap:** Writing `NaN` outside the active footprint causes NumPy checks of the form `((pred >= 0) & (pred <= 1)).all()` to evaluate to `False`, triggering `"Predicted values must be in range [0, 1]"`.
2. **Mechanism 2 — Unsanitized `float32` Sentinels:** `training_features.tif` contains `-3.4028235e+38` across `58,171` in-footprint band-pixels (`data/prepared_manifest.json`).
3. **Verified Fix (`audit_geotiff` + `validate_submission_geotiff`):** Every `*-zeros.tif` written by `gems32.submission.write_submission_pair` sets `nodata = None`, clips in-footprint values strictly to `[0.0, 1.0]`, writes `0.0` outside the footprint across all `12,279,160` cells (`0` NaNs anywhere), and verifies the bytes on disk automatically without human inspection (`docs/downloads/submissions_manifest.json`, `portal_illegal = []`).

---

## 🔁 End-to-End Autonomous Reproduction (`0` DrivenData Slots Used)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt tifffile
.venv/bin/python scripts/restore_data.py          # SHA-256-verified mirror restore into .cache/gems_data/
.venv/bin/python scripts/prepare_data.py          # Sanitizes 19 official bands into .cache/gems_work/
.venv/bin/python scripts/run_h36_tdr_pds_pipeline.py  # Canaries + writes H36-1C GeoTIFF/ZIP + Run Card
.venv/bin/python scripts/audit_shipped.py         # Re-verifies every .tif in docs/downloads/
.venv/bin/python scripts/audit_release_protocol.py # Updates docs/data/protocol-audit.json
.venv/bin/python scripts/build_site.py            # Renders docs/*.html and root *.html
.venv/bin/pytest tests -q                         # Full automated test & hygiene suite
```

---

## ⚠️ Flagged Irregularities & Remaining Limitations

Full machine-readable register: [`registry/irregularities.json`](registry/irregularities.json) (`27` audited items). Key Round-6 updates:
- **`IR-32-INSTR-03` (FIXED):** `src/gems32/holdout.py` (`GEMSDOE32-HOLDOUT-v3-visible-gated`) now derives `d_visible_sub` solely from visible faults per split, restoring exact live B-ladder monotony (`0.06879 < 0.09674 < 0.09898 < 0.09920 > 0.09710`).
- **`IR-32-BAND-02` & `IR-32-BAND-03` (FIXED):** Corrected Band 6 (`tc` = radiometric Total Count) and Band 18 (`iso_grav_anom_hg` = signed $\partial g/\partial x$) across `src/gems32/h36_tdr_pds.py`.
- **`IR-32-CONDUIT-01` (FIXED):** Retired contradictory `promote` banner on `H-GEO-CONDUIT` (`2d0d0c5e`, which had `70.25% > 70%` real-detector overlap and `0.04617 < 0.06412` SGMC holdout).
- **`IR-32-LATTICE-01` & `IR-32-SCORE-01` (OPEN LIMITATIONS):** (1) The synthetic $5\mathbb{Z}\times 5\mathbb{Z}$ calibration grid `13gems_r13-lattice-s5` covers `99.87%` of the footprint within `<= 3 px`, blocking any `> 20,593`-dot submission under a no-exemption scan unless calibration probes are segregated by role in a future template revision; (2) all `buffedlizard55-lab` leaderboard scores (`0.2778`, `0.2600` on `dotted-h19-5-d2-8-20261002-e56ea318af89-nan`, etc.) come from owner-reported ledgers rather than cryptographic DrivenData HTML receipts; (3) bridging `0.2778` to `0.3195–0.4413` requires raw relocated seismicity / InSAR (`H36-5`, blocked in this sandbox) and GPU multi-scale curvilinear U-Net training rather than 2-vCPU tree ensembles alone.

---

<details>
<summary><b>📋 Verbatim Standing Project Prompt (Read Every Session as the Starting Brief)</b></summary>

> Review the repo.
>
> I want to focus on the highest scoring submissions from the following sites, GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36.
>
> THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!
>
> MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION. DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION. BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION. IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.
>
> There should be an easy to download submission tif file as described by the prompt. Read the entire prompt. A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.
>
> PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.
> 1. UNIQUENESS. Check the lane against the registry before placement (surface rank correlation) and on the final dots; > 0.90 rank correlation or > 70% of dots within 3 px of one registry raster = duplicate -> log and stop.
> 2. REUSE. Use the template's cached feature stack, holdout evaluator, and submission writer. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
> 3. LEAKAGE. Run a single-feature canary on the holdout; AUC > 0.90 is leakage until proven otherwise.
> 4. LABELS. Every number is either HOLDOUT-DTI (with evaluator version, withheld positives count, 95% CI) or ORGANIZER-CONFIRMED (from a submission receipt). Never write a projection as a score.
> 5. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.
> 6. OUTPUT. End with one JSON Run Card: hypothesis, mechanism, named non-fault mimic, holdout DTI + CI, correlation/overlap vs registry, raster sha256, validator output, submission name + note (<=140 chars), verdict promote / negative. Negative results are valid deliverables — stop cleanly rather than tune past the cap.
>
> WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
> https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
> h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
>
> Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?
> Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition. Must be unique submission unlike any within the GEMSDOE sites above. Verify working line by line no hallucinations.
>
> Current competition leaderboard GEMSDOE high score: 0.3195 / 0.4413
>
> Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.
>
> Work line by line verifying from official verified trusted sources, provide links for manual review. There should be no manual input, work on your own to complete tasks. Flag any irregularities for review. No hallucinations.
>
> I tried to submit the document that i downloaded from the site but it returned this error on the submission form: "Predicted values must be in range [0, 1]"
> Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25
> Create a executive summary subpage that explains exactly how to make a submission into the contest.
> Create a github page for this repo that has clean ui, user friendly, simple and easy to use. It should be organized and clean.

</details>
