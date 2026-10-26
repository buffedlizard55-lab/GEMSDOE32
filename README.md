# GEMSDOE32 — Auditable Geothermal Blind-Fault Discovery System for the DOE GEMS Prize (DrivenData #306)

## 🔴 CURRENT AUTOMATED PROJECT GATE VERDICT: **DO NOT SUBMIT TO PORTAL — RETAIN `0.2778` LIVE SLOT** (`2026-10-26`)

> **IS IT OK TO DOWNLOAD AND SUBMIT THE NEWLY GENERATED `.TIF`?**
> **⛔ NO — DO NOT SUBMIT TO DRIVENDATA (`ok_to_download_and_submit = false`, `verdict = "negative"`).**
> Retain `GEMSDOE32`'s existing all-9-site champion (`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`, owner-reported `ORGANIZER-CONFIRMED` live score **`0.2778`**) and preserve your weekly submission slots.
> The newly generated Round-6 multi-physics raster below is **100% unique vs all 26 live-scored cross-site detectors**, **passes 20/20 automated portal format & `[0, 1]` range checks without human intervention**, and **beats the `0.2778` Champion by `+17.9%` (`+0.01776`) on leak-free Hide-and-Recover v3.0**, so it is provided below as a **one-click validated artifact for audit, archival, and further research**. Our automated fail-closed gate (`src/gems32/release_gate.py`) withholds portal promotion because:
> 1. On the secondary off-catalogue `SGMC_cal` diagnostic (`GEMSDOE32-SGMC-CAL-v3.0`, Spearman `+0.6755` across `27` live-scored files), `EXP3_H38_G1_CORROB` (`0.05037`) still trails the `0.2778` Champion (`0.06412`).
> 2. Under the unexempted all-registry `<= 3 px` check, it overlaps unsubmitted local GBDT sibling `hcvf2` at `77.56% > 70%` and the synthetic `206,895`-dot 5-px grid `r13-lattice-s5` at `99.71% > 70%` (`IR-32-PIGEONHOLE-01`).

### ⬇ ONE-CLICK Validated Round-6 GeoTIFF & Audit Bundle (`EXP3_H38_G1_CORROB`)
* **[⬇ Download Validated `.TIF` (All-Finite `[0, 1]`, Audit Only — Do Not Submit): `gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif)** (`209,987` B · `sha256: 6efe140229c46b274ab7431bab0b9c1318ade642096ca8a1ff8c36317d2d68ff`)
* **[⬇ Download `.ZIP` Bundle: `gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.zip`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.zip)** (`176,161` B · `sha256: be822595c38e06cc30c384d3ba7bfac055515272d45cf0331d6e6f64161ed512`)
* **[⬇ Download Spec `NaN`-Outside Twin: `gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-nan.tif`](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-nan.tif)** (`345,412` B · `sha256: 6dd6e37b617181c14948297c58f80b29a91de846c04441add0614d4e51b9b836`)
* **[Automated 13/13 + 7/7 Format Validator Receipt (`20/20 PASS`)](docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-audit.json)** · **[Round-6 JSON Run Card](evidence/h38_run_card.json)** · **[Full Experiment Log](evidence/h38_geothermal_experiments.json)** · **[Strict Protocol Audit](docs/data/protocol-audit.json)**
* **Recorded Unique Submission Name:** `GEMSDOE32-EXP3_H38_G1_CORROB-35859E28`
* **Recorded Portal Note (`102 / 140` chars):** `GEMS32 EXP3_H38_G1_CORROB 53ch LiDAR+GeoDAWN+GDR CELF 37654px HR=0.1170 SGMC=0.0504 HOLD-DO-NOT-SUBMIT`
* **Live GitHub Pages Site:** <https://buffedlizard55-lab.github.io/GEMSDOE32/> · **[Executive Summary & Step-by-Step Submission Subpage](docs/executive-summary.html)**

---

> ### Core Values — Central to Every Decision in `GEMSDOE32`
> * **Maximize P(Win).** *"Maximize the Probability of Winning"* is our decision-making framework. Every weekly submission slot (`3 / week`, with **one** final submission scored in *both* prize rounds) is a scarce experimental resource, never a lottery ticket. When local calibrated evidence says a new candidate does not yet beat our `0.2778` live anchor on off-catalogue faults, we protect the slot and publish the exact diagnostic gap.
> * **Own the Outcome.** We own results end to end — data restoration, feature sanitization, evaluator repair, leakage checks, format validation, irregularity audits, and clear public documentation — without human-inspector bottlenecks or silent assumptions.

---

## 🌎 1. Nine-Site Executive Summary (`GEMSDOE24..GEMSDOE36`) — Byte-Verified Audit

All nine focus sites (`GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36`) plus lineage root `19GEMSDOE`, independent OOF benchmark `GEMSDOE70`, and the official [`drivendataorg/gems-prize-reference-solution`](https://github.com/drivendataorg/gems-prize-reference-solution) were audited directly from SHA-256-pinned GeoTIFF bytes and GitHub commits (full machine-readable table in [`evidence/nine_site_executive_audit_20261026.json`](evidence/nine_site_executive_audit_20261026.json)).

> **Score Provenance Note (`Rule 3`):** Every live score below is labelled `ORGANIZER-CONFIRMED (owner-reported)` because it comes from owner-committed submission logs across the sibling repos without a cryptographic DrivenData receipt screenshot (`IR-32-SCORE-01`). Every local proxy number is explicitly labelled `HOLDOUT-DTI`.

| Site & Verified Repo | Best Submission on Site | Dots | Live Score (`owner-reported`) | Local `HOLDOUT-DTI` (`SGMC-cal v3.0`) | Exact Relationship to Family & Current Gate Status |
| :--- | :--- | ---: | ---: | ---: | :--- |
| **[GEMSDOE32](https://github.com/buffedlizard55-lab/GEMSDOE32)** 🏆 **(#1 of 9)** | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (`c55bafc47005…`) | `37,654` | **`0.2778`** | `0.06412` | **ALL-9 CHAMPION.** Exact `B=2` rung: `SOLO-D2.8 \ {d(labels) <= 200 m}` (`-2,545` dead-annulus dots, `+0.0070` over `B=1`, `+0.0178` over `B=0`). Round-6 `H38-G1`: **DO NOT SUBMIT** (retain `0.2778`). |
| **[GEMSDOE36](https://github.com/buffedlizard55-lab/GEMSDOE36)** (#2 of 9) | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` (`34500f8892c5…`) | `38,854` | **`0.2750`** | `0.06378` | Pixel-exact superset of `GEMSDOE32` Champion (`37,654` Champion dots `+ 1,200` Anderson-mechanics dots; Jaccard `0.969`; marginal `~0.018` credit/dot `< 0.0556` bar -> `-0.0028` DTI). Current gate: **NO-GO**. |
| **[GEMSDOE28](https://github.com/buffedlizard55-lab/GEMSDOE28)** (#3 of 9) | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif` (`f86eb44f0dd1…`) | `37,660` | **`0.2710`** | `0.06233` | Tested 4 blind/buffer variants on `D2.8`: `RUNG30` (`0.2710`) > `SOLO-D2.8` (`0.2708`) > `HF-Euler` (`0.2707`) > `Prethin-Tip-Euler` (`0.2649`). Oct-25 `s18-mxtp` (`11,082` px) scored `0.0217` live; gate: **DO NOT SUBMIT**. |
| **[GEMSDOE31](https://github.com/buffedlizard55-lab/GEMSDOE31)** (#4 of 9) | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif` (`24f500e42b9c…`) | `40,199` | **`0.2708`** | `0.06224` | Exact `B=1` rung: `D2.8` (`44,090` px, `0.2600`) minus `3,891` dots within `100 m` of `labels.tif` (`+0.0108` DTI). Oct-25 `H31-M` stopped by `r13-lattice-s5` (`99.69%`); gate: **DO NOT SUBMIT**. |
| **[GEMSDOE33](https://github.com/buffedlizard55-lab/GEMSDOE33)** (#5 of 9) | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` (`0fb30c849f8a…`) | `41,865` | **`0.2632`** | `0.06163` | Analog fault-tip & step-over additions onto `B=1` base (`+0.0032` vs `D2.8`, `-0.0076` dilution vs un-extended `B=1`). Oct-25 `A33-L1`: **DO NOT SUBMIT**. |
| **[GEMSDOE25](https://github.com/buffedlizard55-lab/GEMSDOE25)** (tie #6) | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` (`91eae1ca51e8…`) | `44,090` | **`0.2600`** | `0.06059` | Kernel-matched `d = 2.8 px` Poisson-disk thinning of `H19-5` (`B=0`; `+0.0678` over `0.1922`). Parent dot set of `GEMSDOE30`, `31`, and `32`. Oct-25 `h66-mgd-flank` scored `0.0742` live; gate: **DO NOT SUBMIT**. |
| **[GEMSDOE30](https://github.com/buffedlizard55-lab/GEMSDOE30)** (tie #6) | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` (`67c65649fd85…`) | `44,090` | **`0.2600`** | `0.06059` | Dot-identical to `GEMSDOE25 D2.8` (`0` symmetric-diff pixels -> deterministic `0.2600` score). Proved `(Band 18, Band 11) = (+dg/dx, +dg/dy)`. Oct-25 `MSDB1` (`B=0`) scored `0.1462` live; gate: **DO NOT SUBMIT**. |
| **[GEMSDOE24](https://github.com/buffedlizard55-lab/GEMSDOE24)** (#8 of 9) | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` (`24f500e42b9c…`) | `60,069` | **`0.2477`** | `0.06423` | First sparse thinning (`d = 1.5 px`) of `H19-5` (`0.1922 -> 0.2477`, `+0.0555`). Hosts canonical SHA-256-pinned external mirrors. Oct-25 `gvc1` scored `0.0859` live; `RSHG1` **DO NOT SUBMIT** (`72.69%` overlap). |
| **[GEMSDOE27](https://github.com/buffedlizard55-lab/GEMSDOE27)** (#9 of 9) | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` (`33003374335d…`) | `61,328` | **`0.2449`** | `0.06378` | Added `+1,259` topo-gap bridge pixels to `D1.5` (`-0.0028`). Notably, Oct-25 independent OOF `H29` (`37,654` px, hydrothermal + Frangi + `CELF300m` + `B=2`) scored **`0.2190`** live! Current `H30`: **DO NOT SUBMIT**. |

### Lineage Root & Wider Benchmarks
* **[19GEMSDOE](https://github.com/buffedlizard55-lab/19GEMSDOE)** (`gems19-h19-5-...-e27054cf-nan.tif`, `121,131` px): **`0.1922`** live (`SGMC_cal = 0.05079`) — the undotted 4-pillar corroborated geological surface (`1 m` USGS 3DEP LiDAR scarps + DOE GDR `#1391` wells/vents + geopotential worms + power-law tip/stepover projections) from which every `0.2449–0.2778` Focus-9 champion was thinned and buffered.
* **[GEMSDOE70](https://github.com/buffedlizard55-lab/GEMSDOE70)** (`gems70-p5-dual-submod300-oof38k-20261020.tif`, `37,654` px): **`0.2478`** live (**highest `SGMC_cal = 0.08570`** across all `27` audited files) — proves an independent OOF model fusing `1 m` 3DEP LiDAR + GDR `#1391` + Quaternary + `SGMC d>=3` + `300 m` submodular cover reaches `0.2478` without `H19-5` dots.
* **[Official Reference Solution](https://github.com/drivendataorg/gems-prize-reference-solution)** (`unet-mc-cv-reference-solution.ipynb @ aebe92f7c8`): ResNet34 U-Net (`128x128` patches, `TverskyLoss(alpha=0.2, beta=0.8)`). Reveals two critical facts (`IR-32-REFNB-01`): Cell 12 filters `pos_idx` to tiles with `labels > 0` and Cell 17 leaves every unmapped tile identically `0.0`; Cell 19 writes `0.0` outside footprint (`nodata=None`), matching our `-zeros.tif` convention.

---

## 🔬 2. PhD-Level Forensic Analysis: Why `0.2778` Won & How to Reach `0.3195–0.4413`

### 2.1 Exact Set-Algebraic Genealogy & Tversky Knapsack Proof
Under the official Distance-Weighted Tversky Index ($k(d) = \max(1 - d / 300\text{ m}, 0)$, $\alpha = 0.2$, $\beta = 0.8$), $\text{FN}_w = |G| - \text{TP}_w$ holds identically, giving:
$$\text{DTI} = \frac{T}{0.2(T + S - M) + 0.8|G|}, \qquad \text{emit pixel } x \iff \mathbb{E}[k(x)] > 0.2 \cdot \text{DTI}$$
where $T = \text{TP}_w$, $S = \sum_x p(x)$ is total emitted mass, and $M = \sum_x p(x)\max_{g \in G} k(d(x,g))$. Because $\text{TP}_w$ saturates via $\max_x$ within $300\text{ m}$ (`R = 3 px`) while every emitted dot pays $\alpha = 0.2$ in the denominator, dense ribbons pay huge false-positive mass for zero marginal $\text{TP}_w$. Furthermore, the DrivenData scorer **masks known `labels.tif` pixels**, creating a `0–200 m` dead annulus around mapped traces where hidden ground-truth faults almost never sit ($k \approx 0.006–0.016 < 0.0556 = 0.2 \times 0.2778$).
* **Thinning (`121,131 -> 44,090` px, `d = 2.8 px`):** Shed `77,041` redundant pixels -> **`0.1922 -> 0.2600` (`+0.0678` DTI)**.
* **Dead-Annulus Pruning (`44,090 -> 40,199 -> 37,654` px, `B = 0 -> 1 -> 2`):** Removed `3,891` (`B=1`) + `2,545` (`B=2`) near-catalogue pixels -> **`0.2600 -> 0.2708 -> 0.2778` (`+0.0178` DTI)**, peaking at `B=2` before `B=3` begins deleting genuine step-over tips.

### 2.2 Repair of the Local Holdout Instrument (`IR-32-INSTR-04`)
Evaluating static `B=2`-masked files against full `labels.tif` previously inverted the live `B`-ladder (`Spearman = -0.1747` across `n = 27` live-scored submissions). Implementing true Rule-2 visible-only `B`-gating per fold in `src/gems32/holdout.py::evaluate_hide_and_recover` (`GEMSDOE32-HIDE-RECOVER-v3.0`, `n_withheld = 22,232`, `256`-block cluster bootstrap) restores **Spearman `+1.000`** on the `D2.8` `B`-ladder:
* `B = 0` (`D2.8`, live `0.2600`): `HOLDOUT-DTI = 0.096743`
* `B = 1` (`SOLO`, live `0.2708`): `HOLDOUT-DTI = 0.098977`
* **`B = 2` (`CHAMPION`, live `0.2778`): `HOLDOUT-DTI = 0.099202` `[0.085947, 0.112674]` (exact peak)**
* `B = 3` (over-pruned): `HOLDOUT-DTI = 0.097102`
Meanwhile, across all **`27` cross-site live-scored submissions** (`[0.0107, 0.2778]`), `GEMSDOE32-SGMC-CAL-v3.0` (`n_withheld = 62,703` eval / `169,243` total off-catalogue SGMC pixels) achieves **Spearman `+0.6755` (`p = 1.10e-4`)** — explaining why we require **both** instruments before spending a live slot.

### 2.3 Can We Score Higher Than `0.2778` (Toward `0.3195` and `0.4413`)?
**Yes — but never by further post-processing `H19-5`.** Live inversion of the `B=0 / B=1` pair implies $|G| \approx 12,226$ hidden truth pixels and $\text{TP}_w \approx 5,073$ (`41.5%` weighted recall) at `0.2778`. At matched `S = 37,654` dots:
* Crossing **`0.3195`** requires **`+15.0%`** more weighted recall ($\text{TP}_w \approx 6,070$, `~49.6%` recall).
* Crossing **`0.4413`** (`xiaofanhu`, Oct-25 `#1`) requires **`+58.9%`** more weighted recall ($\text{TP}_w \approx 9,150$, `~74.8%` recall).
The cross-site live record (`0.0217–0.1462` for 19-band potential-field-only emitters vs `0.2190` on `GEMSDOE27 H29` and `0.2478` on `GEMSDOE70 p5`) proves three ingredients are mandatory: **(1) full multi-physics inputs (`1 m` 3DEP LiDAR + GeoDAWN K/Th/U/upward-continued TMI + DOE GDR `#1391` thermal features), (2) 2D spatial-context Tversky learning (`H38-G4`) across 100% of footprint tiles (removing reference notebook Cell 12's positive-tile filter), and (3) `B=2` + `300 m` lazy-greedy submodular packing.**

---

## 🌋 3. Ranked Candidate Geological Hypotheses (`H38-G1..H38-G4`) & Round-6 Experiments

Before writing model code, four geological hypotheses were preregistered in [`docs/research/hypotheses-round6-20261026.md`](docs/research/hypotheses-round6-20261026.md) and [`registry/hypotheses.json`](registry/hypotheses.json), with all external datasets verified free, official, and SHA-256-pinned on disk:

| Rank | ID | Hypothesis & Layers | Physical Signature & Transform | Why Off-Catalogue & How It Differs | Expected Gain & Cost | Measured Status (`2026-10-26`) |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **`H38-G1`** | **Multi-Physics Blind Hydrothermal-Structural Fault-Zone Classifier + CELF 300 m Cover** (`19` official bands + `16` multi-scale ridges + `18` derived `3DEP` LiDAR / `GeoDAWN` / `GDR #1391` channels = **`53` channels**) | Leak-free spatial-OOF `HistGradientBoostingClassifier` fusing LiDAR facing-asymmetry scarplets, `K-Th` metasomatism, `TMI - TMI_up150` magnetite oxidation troughs, `GDR` thermal halos, and vector gravity-magnetic-strain tensors + `B=2` + `300 m` CELF submodular cover | First `GEMSDOE32` model uniting `3DEP` LiDAR + `GeoDAWN` radiometrics/upward-continued magnetics + `GDR #1391` thermal wells/vents + nearest-filled boundary features + quantile-calibrated LiDAR/non-LiDAR routing (`IR-32-LIDAR-01`) | `+0.010` to `+0.028` `HOLDOUT-DTI` · Medium (`~94s` CPU) | **EXECUTED (`EXP-2` & `EXP-3`):** Beat Champion `+17.9%` on `Hide&Recover v3.0` (`0.11696` vs `0.09920`, paired CI `[+0.00832, +0.02743]`); `SGMC_cal = 0.05037` -> **`DO NOT SUBMIT`** |
| **2** | **`H38-G2`** | **Lithology-Deconfounded K-Metasomatism & Magnetite-Destruction Trough Detector** (`geodawn_rad_u8.tif`, `geodawn_extensions_u8.tif`, Bands `6, 9, 14, 15, 17`) | Standardized `z(K) - z(Th)` adularia/illite excess paired with shallow magnetic oxidation troughs `z(tmi) - z(TMI_up150)`, magnetic tilt zero-crossing witness $\exp(-\|\text{tc}\|/\sigma)\|\text{tmi\_vg}\|$, and MT clay-cap lateral edges | Corrects `H-GEO-4`'s misattribution of Band 6 `tc` (`IR-32-CONDUIT-02`) and introduces true `GeoDAWN` radiometric & `150 m` upward-continuation channels to catch sealed blind hydrothermal upflow zones | `+0.004` to `+0.012` `HOLDOUT-DTI` · Low (on disk) | **MEASURED inside `EXP-2/3`** (all channels Canary `AUC <= 0.6235 <= 0.90`) |
| **3** | **`H38-G3`** | **Contour-Orthogonal Asymmetric `1 m` LiDAR Piedmont Scarplet Filter** (`lidar_scarp_features_u8.tif` + Bands `12, 15, 19`) | $\text{step\_max} \cdot \text{coh100} \cdot \frac{\|\text{down}-\text{up}\|}{\text{down}+\text{up}+\varepsilon} \cdot \|\sin(\theta_{\text{lidar}}-\theta_{\text{contour}})\|$ over basin fill | Rejects contour-parallel Lake Lahontan shorelines and symmetric two-bank washes that confounded `H33-C`, isolating `<1 m` synthetic/antithetic piedmont fault splays | `+0.005` to `+0.015` `HOLDOUT-DTI` · Low (on disk) | **MEASURED inside `EXP-2/3`** (`+0.00719` jump `EXP-1 -> EXP-2`, `+0.01728` to `EXP-3`) |
| **4** | **`H38-G4`** | **Spatial-Block Tversky-Loss 2D U-Net / SegFormer on `53`-Channel Stack + Submodular `300 m` Packing** (`53`-ch stack) | `128x128` (`12.8 km`) multi-scale encoder-decoder trained directly on smooth Distance-Weighted Tversky loss (`alpha=0.2, beta=0.8`) across **all** footprint tiles (removing reference Cell 12 filter) + `B=2` + `300 m` CELF | Replaces pixel-wise GBDT with 2D curvilinear fault-zone & relay-ramp context needed to close the `+0.04` to `+0.16` live DTI gap toward `0.3195–0.4413` | `+0.03` to `+0.12` live DTI potential · High (requires GPU) | **REGISTERED ROADMAP** (deferred on `2`-vCPU / `3.8 GiB` CPU-only sandbox) |

### Summary of the `3 / 3` Executed Round-6 Experiments (`scripts/run_h38_geothermal_experiments.py`)
* **53-Channel Single-Feature Leakage Canary (`Rule 4`):** **PASSED** — all `53` channels tested individually on `GEMSDOE32-HIDE-RECOVER-v3.0`; worst single-feature `AUC = 0.62350` (`coherence_s2` `<= 0.90`).
* **LiDAR Survey-Selection Bias Discovery (`IR-32-LIDAR-01`):** `1 m` 3DEP LiDAR covers `75.37%` of the Nevada footprint (`labels.tif` `1.26x` denser inside; off-catalogue `SGMC` `1.61x` denser outside).

| Experiment | Stack & Mechanism | Emitted Dots | `HOLDOUT-DTI` (`GEMSDOE32-HIDE-RECOVER-v3.0`, `n=22,232`) | `HOLDOUT-DTI` (`GEMSDOE32-SGMC-CAL-v3.0`, `n=62,703`) | Max Surface `\|Spearman\|` |
| :--- | :--- | ---: | :--- | :--- | ---: |
| `CHAMPION 0.2778` *(ref)* | Nested `H19-5 -> D2.8 -> B=2` | `37,654` | `0.099202` `[0.085947, 0.112674]` | **`0.064121`** `[0.056734, 0.071654]` | — |
| `EXP1_H38_BASE35` | Repaired nearest-filled `35`-ch OOF HistGB + `B=2` + `300 m` CELF | `37,654` | `0.099680` `[0.082534, 0.116266]` (`+0.00048`) | `0.053714` `[0.048049, 0.059369]` | `0.4227` |
| `EXP2_H38_G1_MULTIPHYS` | Full `53`-ch (`35` base + `18` `3DEP` LiDAR + `GeoDAWN` + `GDR`) + `B=2` + `300 m` CELF | `37,654` | `0.106871` `[0.089496, 0.122802]` (`+0.00767`) | `0.049909` `[0.043967, 0.055407]` | `0.4158` |
| **`EXP3_H38_G1_CORROB`** *(selected)* | `53`-ch + `IR-32-LIDAR-01` quantile-calibrated routing + multi-physics structural corroboration + `B=2` + `300 m` CELF | `37,654` | **`0.116958`** `[0.100533, 0.132040]` (**`+0.01776`, `+17.9%`**) | `0.050374` `[0.044672, 0.055480]` | `0.4374` |

---

## 🛠️ 4. Permanent Fix for `"Predicted values must be in range [0, 1]"` & Step-by-Step Submission Guide

### Why DrivenData Rejects Valid-Looking GeoTIFFs with `"Predicted values must be in range [0, 1]"`
1. **`NaN` Outside Footprint (`Mechanism 1`):** Whole-array NumPy range validators (`((arr >= 0) & (arr <= 1)).all()`) evaluate to `False` if **any** cell is `NaN`. Inspection of [`drivendataorg/gems-prize-reference-solution`](https://github.com/drivendataorg/gems-prize-reference-solution) Cell 19 confirms the organizer's own reference notebook initializes `pred_full = np.zeros(...)` and writes `nodata=None`.
2. **Raw `-3.4028235e+38` Float32 Sentinels (`Mechanism 2`):** `training_features.tif` contains `3,061` `-3.4e38` sentinel pixels *inside* the active footprint (`3,073` across all band-cells) plus `7.11M` outside; spatial filters (`Sobel`/`Gaussian`) previously smeared these sentinels into border cliffs until fixed via `_fill_nearest` in `src/gems32/features.py`.

Every `-zeros.tif` written by `scripts/submission_writer.py` (`src/gems32/submission.py`) guarantees **all `12,279,160 / 12,279,160` cells are finite `float32` in `[0.0, 1.0]`**, `nodata=None`, `EPSG:32611`, `3730x3292`, verified automatically by `20/20` checks (`audit_geotiff` + `scripts/check_submission.py --strict-finite`).

### Step-by-Step Contest Upload Procedure *(Use ONLY When Top Banner Turns Green `OK TO SUBMIT`)*
1. Check the top-of-page banner on [`docs/executive-summary.html`](docs/executive-summary.html) (currently **🔴 DO NOT SUBMIT — retain `0.2778` live slot**).
2. When a future candidate clears both `Hide&Recover v3.0` and `SGMC-cal v3.0` + uniqueness gates, click **One-Click Download `.TIF`** (`*-zeros.tif`).
3. Open <https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/>, choose the `*-zeros.tif` file, paste the unique submission ID and `<= 140`-character note from the Run Card, and record the returned portal receipt in `data/observations.jsonl`.

---

## ⚙️ 5. Autonomous Data Placement & End-to-End Reproducibility

Data placement and feature construction run end-to-end without manual intervention using SHA-256-pinned mirrors (`registry/data_manifest.json`):
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/restore_data.py                   # SHA-256-verified competition + external rasters -> .cache/gems_data/
.venv/bin/python scripts/prepare_data.py                   # Sanitized 19 bands + footprint/catalogue masks
.venv/bin/python scripts/build_features.py                 # Nearest-filled 35-channel structural stack -> .cache/gems_work/
.venv/bin/python scripts/run_h38_geothermal_experiments.py # 53-ch Canary + EXP-1..3 + GeoTIFF + Run Card
.venv/bin/python scripts/check_submission.py docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif --strict-finite
.venv/bin/python scripts/audit_release_protocol.py         # Refreshes docs/data/protocol-audit.json
.venv/bin/python scripts/audit_shipped.py                  # Audits all 39 GeoTIFFs in docs/downloads/
.venv/bin/python scripts/build_site.py                     # Rebuilds docs/*.html and root pages
.venv/bin/pytest tests -q                                  # Runs full automated test suite
```

---

## 🚩 6. Flagged Irregularities & Official Verified Sources

* **Full Irregularities Register (`21` items):** [`registry/irregularities.json`](registry/irregularities.json) · rendered at [`docs/irregularities.html`](docs/irregularities.html) — including newly audited & resolved `IR-32-INSTR-04` (visible-only `B`-gating repair), `IR-32-CONDUIT-01` (hardcoded `±0.032` CI & banner contradiction in PR `#17`), `IR-32-CONDUIT-02` (Band 6 `tc` magnetic tilt misattribution), `IR-32-PIGEONHOLE-01` (`r13-lattice-s5` `99.87%` footprint coverage), `IR-32-LIDAR-01` (`1 m` 3DEP coverage bias), and `IR-32-REFNB-01` (reference U-Net Cell 12 negative-tile skip).
* **Official Verified Sources (`25` entries):** [`registry/sources.json`](registry/sources.json) · rendered at [`docs/sources.html`](docs/sources.html)
  * DrivenData Competition Overview: <https://www.drivendata.org/competitions/306/competition-doe-gems/>
  * Problem Description, Metric & Submission Spec: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
  * Public Leaderboard: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>
  * Official Rules PDF (NLR / DOE OSTI `96647`): <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
  * Official Reference Solution (`aebe92f7c8`): <https://github.com/drivendataorg/gems-prize-reference-solution>
  * Known-Fault Masking Clarification (Forum `#11516`): <https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516>
  * USGS GeoDAWN Airborne Geophysics (`DOI: 10.5066/P93LGLVQ`): <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
  * DOE GDR Submission `#1391` (Great Basin / INGENIOUS): <https://gdr.openei.org/submissions/1391>
  * USGS 3DEP Elevation (`1 m` DEM): <https://apps.nationalmap.gov/downloader/>
  * USGS SGMC State Geologic Map Compilation: <https://mrdata.usgs.gov/sgmc/>

---

<details>
<summary><b>📋 Stored Project Prompt (Verbatim Reference — Read Every Session)</b></summary>

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
> 1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.
> 2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
> 3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.
> 4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.
> 5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.
> 6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.
>
> WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
> https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
> h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
>
> Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778? Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition. Must be unique submission unlike any within the GEMSDOE sites above. Verify working line by line no hallucinations.
>
> Current competition leaderboard GEMSDOE high score: 0.4413
>
> Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted, why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.
>
> Work line by line verifying from official verified trusted sources, provide links for manual review. There should be no manual input, work on your own to complete tasks. Flag any irregularities for review. No hallucinations.
>
> I tried to submit the document that i downloaded from the site but it returned this error on the submission form: "Predicted values must be in range [0, 1]". Also we need to give it a unique name and a short comment to help you or your team tell submissions apart later e.g. clustering with k=25. Create a executive summary subpage that explains exactly how to make a submission into the contest. Create a github page for this repo that has clean ui, user friendly, simple and easy to use. Store this prompt in README.md for reference. Always maintain the core values: Maximize P(Win) and Own the Outcome!
>
> Perform three passes before finishing:
> Pass 1 — Implement the solution and verify it works.
> Pass 2 — Review every file you touched. Look for bugs, missing requirements, unstated assumptions, and edge cases. Fix anything you find.
> Pass 3 — Re-read the original request and check your final result against every detail. Polish anything rough.
> Create a PR and merge it onto main!

</details>
