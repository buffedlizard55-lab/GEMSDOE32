# GEMSDOE32 — U.S. DOE Geothermal Fault Discovery (DrivenData GEMS #306): Gaussian Process Bayesian Optimization Surrogate, 0.2600 Forensic Autopsy & Multi-Physics Submodular Prune-and-Augment

[![Competition](https://img.shields.io/badge/DrivenData-DOE_GEMS_%23306-0284c7)](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
[![Top Candidate H32-D](https://img.shields.io/badge/Slot_%231_H32--D-0.15188_Drift_Holdout_(4%2F4_Quads)-059669)](docs/downloads/gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-zeros.tif)
[![Validator Audit](https://img.shields.io/badge/Range_%5B0%2C_1%5D_Audit-12%2F12_PASS-10b981)](docs/downloads/submissions_manifest.json)
[![Executive Summary](https://img.shields.io/badge/Docs-Executive_Summary_%26_Math_Treatise-f59e0b)](docs/executive-summary.html)

---

## ⚡ Immediate 1-Click Submission Downloads & Copy-Paste DrivenData Notes (Top of Repo)

Per the official [DOE GEMS Prize Rules (NREL/TP-5700-96647)](https://docs.nlr.gov/docs/fy26osti/96647.pdf), teams are capped at **3 submissions per week** and select **one single submission** before the deadline to be evaluated across both the Initial Prize Round ($50,000 across 5 winners) and Final Prize Round ($250,000 across 5 winners).

Every candidate allocated a weekly slot below strictly beats our verified `0.2600` LB baseline (`D2.8`) across **all three holdout metrics** (`catalogue_hidden_mean`, `sgmc_prevalence_calibrated_dti`, and `drift_corrected_holdout_mean`) with **zero on-catalogue pixel waste (`on_catalogue_positive_pixels == 0`)** and passes all **12 automated range-`[0, 1]` validator checks** ([`docs/downloads/submissions_manifest.json`](docs/downloads/submissions_manifest.json)).

- **GitHub Pages Main Hub (with 1-Click `.tif` Downloads at Very Top):** [`docs/index.html`](docs/index.html)
- **Executive Summary & PhD Mathematical Deep-Dive Subpage:** [`docs/executive-summary.html`](docs/executive-summary.html)
- **Monotonic Holdout & GP Surrogate Evaluation Log:** [`data/holdout_surrogate_log.json`](data/holdout_surrogate_log.json) · [`data/holdout_surrogate_log.csv`](data/holdout_surrogate_log.csv)

| Weekly Slot / Role | Candidate ID | Emitted Dots (`px`) | Cat-Hidden DTI (`vs D2.8`) | SGMC-Cal DTI (`vs D2.8`) | Drift-Cal Holdout (`vs D2.8`) | GP EI (`×10⁻³`) | Co-Kriging LB Posterior | 1-Click `0.0`-Outside Primary (`-zeros.tif`) | 1-Click `NaN`-Outside Twin (`-nan.tif`) |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- | :--- |
| **SLOT #1 (Primary)** | **`H32-D`** | **46,090** | **0.10122** (`+0.00290`, **4/4 Quads**) | **0.06129** (`+0.00070`) | **0.15188** (`+0.00388`, **4/4 Quads**) | **3.825** | **0.2716 ± 0.0069** | [`gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-zeros.tif`](docs/downloads/gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-zeros.tif) (`250.6 KB`, `f81e26d7…`) | [`gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-nan.tif`](docs/downloads/gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-nan.tif) (`385.7 KB`, `c3a0cbb1…`) |
| **SLOT #2** | **`H32-C`** | **45,890** | **0.10005** (`+0.00172`, 3/4 Quads) | **0.06331** (`+0.00272`, **Best SGMC**) | **0.15086** (`+0.00285`, 3/4 Quads) | **2.923** | **0.2657 ± 0.0069** | [`gemsdoe32-h32c-mt-claycap-breach-45890-20261004T183200Z-a5963d0a-zeros.tif`](docs/downloads/gemsdoe32-h32c-mt-claycap-breach-45890-20261004T183200Z-a5963d0a-zeros.tif) (`250.7 KB`, `fe96521c…`) | [`gemsdoe32-h32c-mt-claycap-breach-45890-20261004T183200Z-a5963d0a-nan.tif`](docs/downloads/gemsdoe32-h32c-mt-claycap-breach-45890-20261004T183200Z-a5963d0a-nan.tif) (`385.8 KB`, `c09ebb73…`) |
| **SLOT #3** | **`H32-A`** | **46,090** | **0.10002** (`+0.00169`, 3/4 Quads) | **0.06158** (`+0.00099`) | **0.15083** (`+0.00283`, **4/4 Quads**) | **2.806** | **0.2681 ± 0.0069** | [`gemsdoe32-h32a-dip-projected-step-46090-20261004T183200Z-838fcd84-zeros.tif`](docs/downloads/gemsdoe32-h32a-dip-projected-step-46090-20261004T183200Z-838fcd84-zeros.tif) (`250.4 KB`, `dee5c5c6…`) | [`gemsdoe32-h32a-dip-projected-step-46090-20261004T183200Z-838fcd84-nan.tif`](docs/downloads/gemsdoe32-h32a-dip-projected-step-46090-20261004T183200Z-838fcd84-nan.tif) (`385.8 KB`, `564d569b…`) |
| **Reserve #1 (Equal-Budget)** | **`H32-D-Eq44090`** | **44,090** | **0.10004** (`+0.00172`, 3/4 Quads) | **0.06066** (`+0.00006`) | **0.15053** (`+0.00252`, 3/4 Quads) | **2.611** | **0.2692 ± 0.0069** | [`gemsdoe32-h32d-equalbudget-44090-20261004T183200Z-350cdc3f-zeros.tif`](docs/downloads/gemsdoe32-h32d-equalbudget-44090-20261004T183200Z-350cdc3f-zeros.tif) (`244.0 KB`, `133bacd0…`) | [`gemsdoe32-h32d-equalbudget-44090-20261004T183200Z-350cdc3f-nan.tif`](docs/downloads/gemsdoe32-h32d-equalbudget-44090-20261004T183200Z-350cdc3f-nan.tif) (`379.3 KB`, `cc03eb84…`) |
| **Reserve #2** | **`H32-B`** | **45,890** | **0.09894** (`+0.00061`, 3/4 Quads) | **0.06174** (`+0.00115`) | **0.14928** (`+0.00127`, **4/4 Quads**) | **1.564** | **0.2645 ± 0.0069** | [`gemsdoe32-h32b-transtensional-swarm-45890-20261004T183200Z-27b7c9e6-zeros.tif`](docs/downloads/gemsdoe32-h32b-transtensional-swarm-45890-20261004T183200Z-27b7c9e6-zeros.tif) (`249.6 KB`, `fe0b5114…`) | [`gemsdoe32-h32b-transtensional-swarm-45890-20261004T183200Z-27b7c9e6-nan.tif`](docs/downloads/gemsdoe32-h32b-transtensional-swarm-45890-20261004T183200Z-27b7c9e6-nan.tif) (`384.9 KB`, `1a3b1d63…`) |
| **0.2600 LB Reference** | **`D2.8-Ref`** | **44,090** | **0.09832** (`0.00000`) | **0.06059** (`0.00000`) | **0.14801** (`0.00000`) | **0.884** | **0.2600 (Scored LB)** | [`gemsdoe32-d28-ref02600-repro-44090-20261004T183200Z-426073b6-zeros.tif`](docs/downloads/gemsdoe32-d28-ref02600-repro-44090-20261004T183200Z-426073b6-zeros.tif) (`243.8 KB`, `e4985b78…`) | [`gemsdoe32-d28-ref02600-repro-44090-20261004T183200Z-426073b6-nan.tif`](docs/downloads/gemsdoe32-d28-ref02600-repro-44090-20261004T183200Z-426073b6-nan.tif) (`379.3 KB`, `fe01ebd3…`) |

### Copy-Pasteable DrivenData Submission Notes

- **Slot #1 Primary (`H32-D`, `0.0`-Outside Primary):**
  ```text
  GEMSDOE32 Slot #1 Primary (H32-D): Submodular 300m-kernel prune-and-augment on D2.8 (-500 uncorroborated speckles, +2,500 off-catalogue dots across H32-B Kostrov transtensional/swarm, H32-C MT clay-cap breach, and H32-A dip-projected step ridges; 46090 px; 4/4 quadrants won on cat_hid=0.10122 and drift_cal=0.15188, sgmc_cal=0.06129; range [0,1] verified; file=gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-zeros.tif; sha256=f81e26d7).
  ```
- **Slot #1 Twin (`H32-D`, `NaN`-Outside Twin):**
  ```text
  GEMSDOE32 Slot #1 Primary (H32-D): Submodular 300m-kernel prune-and-augment on D2.8 (-500 uncorroborated speckles, +2,500 off-catalogue dots across H32-B Kostrov transtensional/swarm, H32-C MT clay-cap breach, and H32-A dip-projected step ridges; 46090 px; 4/4 quadrants won on cat_hid=0.10122 and drift_cal=0.15188, sgmc_cal=0.06129; range [0,1] verified; file=gemsdoe32-h32d-submodular-multipysics-46090-20261004T183200Z-4de30601-nan.tif; sha256=c3a0cbb1).
  ```
- **Slot #2 (`H32-C`, `0.0`-Outside Primary):**
  ```text
  GEMSDOE32 Slot #2 (H32-C): Magnetotelluric (MT) conductive clay-cap breaching & depth-to-basement strike alignment prune-and-augment (-400 weak dots, +2,200 high-posterior off-catalogue dots; 45890 px; cat_hid=0.10005, sgmc_cal=0.06331, drift_cal=0.15086; range [0,1] verified; file=gemsdoe32-h32c-mt-claycap-breach-45890-20261004T183200Z-a5963d0a-zeros.tif; sha256=fe96521c).
  ```
- **Slot #3 (`H32-A`, `0.0`-Outside Primary):**
  ```text
  GEMSDOE32 Slot #3 (H32-A): Dip-projected subsurface-to-surface fault step parity de-aliasing prune-and-augment (-500 weak dots, +2,500 off-catalogue dots; 46090 px; cat_hid=0.10002, sgmc_cal=0.06158, drift_cal=0.15083, 4/4 drift quadrants won; range [0,1] verified; file=gemsdoe32-h32a-dip-projected-step-46090-20261004T183200Z-838fcd84-zeros.tif; sha256=dee5c5c6).
  ```
- **Reserve #1 Equal-Budget (`H32-D-Eq44090`, `0.0`-Outside Primary):**
  ```text
  GEMSDOE32 Reserve #1 Equal-Budget Ablation (H32-D-Eq44090): Exact 44,090-dot parity with D2.8 (-1,200 uncorroborated D2.8 speckles replaced by +1,200 H32-B/C/A multi-physics dots; 44090 px; cat_hid=0.10004 vs 0.09832, sgmc_cal=0.06066 vs 0.06059, drift_cal=0.15053 vs 0.14801; range [0,1] verified; file=gemsdoe32-h32d-equalbudget-44090-20261004T183200Z-350cdc3f-zeros.tif; sha256=133bacd0).
  ```
- **Reserve #2 (`H32-B`, `0.0`-Outside Primary):**
  ```text
  GEMSDOE32 Reserve #2 (H32-B): Geodetic Kostrov transtensional coupling & microseismic swarm permeability tensor prune-and-augment (-400 weak dots, +2,200 off-catalogue dots; 45890 px; cat_hid=0.09894, sgmc_cal=0.06174, drift_cal=0.14928, 4/4 drift quadrants won; range [0,1] verified; file=gemsdoe32-h32b-transtensional-swarm-45890-20261004T183200Z-27b7c9e6-zeros.tif; sha256=fe0b5114).
  ```

---

## 📜 Full Task Prompt & Arena AI Core Values

<details open>
<summary><strong>Click to expand/collapse Full Prompt &amp; Arena AI Core Values</strong></summary>

```text
Include the full prompt and the Arena AI core values in the README.md:

# Arena AI Core Values:

## 1. "Maximize P(Win)"

If you want to win a competition, then you optimize for the right tail of the score distribution. What does it take to have a real shot at winning?

It requires trying diverse, high-upside ideas — and being disciplined about how you test them. When you're stuck in a loop making small tweaks that don't move the score, step back and try a fundamentally different approach.

Look at the full set of data sources and physics layers available in this problem. Ask: what physical signal in this data is no one else exploiting yet? Formulate a clear hypothesis about why a new feature, transform, or model architecture should capture something the current pipeline misses, then test it cleanly against your local holdout before spending a scarce weekly submission slot.

## 2. "Own the Outcome"

Don't stop at "the code runs." Own the final result end-to-end.

Verify that your local validation metric actually tracks the leaderboard — and when it doesn't, treat that gap as the most important bug to diagnose. Check your outputs visually and numerically before declaring victory: inspect the raster values, CRS, nodata handling, and pixel distributions of every `.tif` you produce so a preventable formatting error never wastes a submission.

Take the time to understand why a past submission scored what it did before jumping to the next idea.

---

### Formal Bayesian Optimization Surrogate Over Holdout Score

To make disciplined use of the 3-submissions-per-week budget, maintain a formal **Bayesian Optimization (Gaussian Process) surrogate model** that predicts holdout DTI as a function of the candidate's design choices (feature weights, thresholds, morphology / thinning parameters, post-processing radii, etc.).

- **Log every holdout evaluation** — whether or not the candidate is ultimately submitted — in a structured file in the repo (e.g. `data/holdout_surrogate_log.json` or `.csv`) so the surrogate's dataset grows monotonically across experiments.
- **Never spend a submission slot on an idea that has not beaten the current holdout best.** Let the surrogate's expected improvement (or upper confidence bound) over the current best govern which candidates earn one of the 3 weekly slots.
- **Analyze surrogate vs. leaderboard discrepancies as holdout drift:** When a candidate with a strong holdout score underperforms on the leaderboard (or vice versa), do not just discard the point — record the `(holdout_score, leaderboard_score)` pair and analyze whether a systematic gap is emerging between the holdout distribution and the hidden test distribution. Use that residual to recalibrate the holdout construction or weight the surrogate toward the regimes where holdout and leaderboard agree.

---

Study our previous research and submission to understand how we got 0.2600 for `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` and reproduced it in https://github.com/buffedlizard55-lab/GEMSDOE29 and https://github.com/buffedlizard55-lab/GEMSDOE30 (feel free to inspect our other repos for the DOE Geothermal competition as well). Explain at a PhD level why this worked, and how we can do even better to beat 0.2600 and the current 0.3195 #1 score on the leaderboard.

Before writing any code, generate 3–5 candidate geological hypotheses for detecting geothermal vents or blind faults that are missing from the USGS catalogue. For each hypothesis, specify:
(1) which input layers it uses,
(2) the exact physical signature or mathematical transform,
(3) why this signal would catch faults the current catalogue misses, and
(4) how it differs from every hypothesis already tested in this repo.
Rank them by expected DTI improvement and implementation cost, then implement and validate the top-ranked one on the spatially-blocked holdout set.

Fix the error `Predicted values must be in range [0, 1]` for the submission, make sure to have unique file names and provide short submission notes, and put the 1-click download for the `.tif` submissions at the very top of the `index.html` and in an executive summary subpage as well.

Please download the competition data from Dropbox and place the extracted files in `data/`, or run `bash scripts/download_competition_data.sh` and `python3 scripts/prepare_data.py`, and run the pipeline for me. Work autonomously with zero manual input required. Make sure to review everything line by line to make sure everything is verified with official verified links for manual review, flag any irregularities, no hallucinations. Create a PR and merge it as well. Run the task through 3 passes: Pass 1 to implement and verify, Pass 2 to review and fix any bugs or edge cases, Pass 3 to re-check against all requirements before finishing.
```
</details>

---

## 1. Root-Cause Diagnosis & Permanent Fix for `"Predicted values must be in range [0, 1]"`

Forensic inspection of `training_features.tif` (`3730 × 3292`, `EPSG:32611`, 19 `float32` bands) and DrivenData's reference `make_submission.ipynb` revealed two compounding causes of the `"Predicted values must be in range [0, 1]"` submission error:

1. **Unmasked `-3.4028235e+38` Float32 Sentinel Leakage Inside the Active Footprint (`IR-32-01`):**
   Inside the `5,167,373`-pixel active study footprint (`np.isfinite(sample_submission.tif)`), `training_features.tif` encodes missing geophysical survey cells using the IEEE-754 float32 minimum value `-3.4028235e+38`: specifically, **3,061 pixels** in bands 1–5 and 7–19, and **3,073 pixels** in band 6 (`tc`), totaling **58,171 sentinel band-pixel instances** ([`data/prepared_manifest.json`](data/prepared_manifest.json)). Any spatial filter (`gaussian_filter`, `np.gradient`) applied prior to converting `abs(v) > 1e30` to `NaN` corrupts surrounding footprint pixels with `-3.4e38` or `NaN`.
2. **Whole-Array Range Check `((arr >= 0.0) & (arr <= 1.0)).all()` on Outside-Footprint Cells:**
   In IEEE-754 arithmetic, `np.nan >= 0.0` evaluates to `False`. DrivenData's reference `make_submission.ipynb` fills the `7,111,787` outside-footprint cells with `0.0` (`nodata=None`).

**Permanent Resolution (`scripts/prepare_data.py` + `src/gems32/submission.py`):**
- `scripts/prepare_data.py` strips all `abs(v) > 1e30` and non-finite pixels before any spatial operator and logs exact counts in [`data/prepared_manifest.json`](data/prepared_manifest.json).
- `src/gems32/submission.py` clamps all in-footprint values to `[0.0, 1.0]`, zeroes all `60,988` public catalogue pixels (`pred[labels] = 0.0`), and writes paired GeoTIFFs (`-zeros.tif` with `12,279,160 / 12,279,160` finite `[0.0, 1.0]` cells and `-nan.tif` with `5,167,373 / 5,167,373` finite `[0.0, 1.0]` in-footprint cells), verified by a 12-point automated audit (`all_checks_passed == True` across all 12 `.tif` files).

---

## 2. PhD-Level Forensic Autopsy of `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` (0.2600 LB) & How to Surpass 0.2600 and 0.3195 / 0.3262

![Forensic Autopsy of D2.8 vs H19-5 and H32-D](docs/assets/fig1_d28_forensic_autopsy.png)

### 2.1 Byte- and Pixel-Level Identity Across GEMSDOE25, GEMSDOE29, and GEMSDOE30
Direct pixel comparison ([`evidence/d28_forensic_autopsy.json`](evidence/d28_forensic_autopsy.json)) confirms that all three `0.2600` leaderboard submissions—`dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` (`GEMSDOE25`), `gems29-refd28-repro-20261003-1cc7dc534d51-nan.tif` (`GEMSDOE29`), and `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` (`GEMSDOE30`)—are **100% pixel-identical (`max_abs_diff = 0.0`)**:
- Exactly **44,090 positive pixels** (`0.8532%` of the 5,167,373-pixel footprint).
- **0 pixels** overlapping the 60,988 positive pixels of `labels.tif`.
- Strict pixel subsets (`(D2.8 & ~H19-5).sum() == 0`) of `H19-5` (`121,131` px, LB `0.1922`) and `D1.5` (`60,069` px, LB `0.2477`).

### 2.2 Mathematical Proof of Why Thinning `H19-5` Raised Leaderboard DTI by +35.3% (`0.1922 → 0.2477 → 0.2600`)
The official metric is the **Distance-Weighted Tversky Index (DTI)** with $\alpha = 0.2$ (false positives), $\beta = 0.8$ (false negatives), and linear buffer decay radius $R = 300\text{ m} = 3.0\text{ px}$:

$$k(d) = \max\!\left(1 - \frac{d}{3.0},\; 0\right), \qquad \text{TP}_p = \sum_{p \in P} k(d(p, G)), \qquad \text{TP}_g = \sum_{g \in G} k(d(g, P))$$

$$\text{TP}_w = \frac{\text{TP}_p + \text{TP}_g}{2}, \qquad \text{DTI}(P, G) = \frac{\text{TP}_w}{0.2\,|P| + 0.8\,|G| + 0.8\,(\text{TP}_g - \text{TP}_p)}$$

Because $\text{TP}_g(P, G) = \sum_{g \in G} \max_{p \in P} k(\|g - p\|_2)$ only depends on the **single nearest predicted dot** $p \in P$ to each ground-truth pixel $g \in G$, $\text{TP}_g(P, G)$ is a **monotone submodular set function** of $P$:
- Along a continuous 1-pixel-wide ridge (`H19-5`, `121,131` px), adjacent pixels at 100 m spacing have 300 m kernel disks that overlap by **63.6%**.
- Thinning `H19-5` to `D2.8` (`44,090` px, `36.40%` of `H19-5` pixels) sheds **77,041 redundant pixels** (cutting the false-positive denominator penalty $0.2\,\Delta|P|$ by **`-15,408.2` units**), while retaining **75.89%** of the total 300 m triangular kernel integral (`287,694.44` vs `379,108.97`) and increasing covered footprint per dot from `5.31 px/dot` to `13.13 px/dot`!

### 2.3 Three Structural Flaws in `D2.8` & Quantitative Path Past `0.2600` and `0.3195` / `0.3262`
1. **Score-Blind Row-Major BFS at `min_dist = 2.4 px` (`IR-32-04`):** `GEMSDOE25/src/gems25/thinning.py` generated `d2.8` via `dot_thin(h19_5, min_dist=2.4)` in row-major scan order without sorting by geological posterior score, allowing low-confidence ridge tips to suppress adjacent high-confidence fault intersections.
2. **10,099 Single-Pixel Speckles (Including 1,732 Uncorroborated Noise Dots):** Connected-component analysis proves that `10,099` of `D2.8`'s `44,090` dots (`22.9%`) sit on isolated 1-pixel components of `H19-5`, including `1,732` speckles where `H19-4 == 0`, `H16-1 == 0`, `Ens12 == 0`, and 3DEP LiDAR scarp `< 0.05`.
3. **Down-Dip Potential-Field Offset & Concealed Blind Conduits:** Normal faults dipping at $45^\circ\text{–}60^\circ$ produce horizontal gravity/magnetic gradient maxima shifted **150–300 m down-dip (basin-ward)** of the surface fault trace (`H32-A`), while active releasing step-overs (`H32-B`) and argillic clay-cap upflow zones (`H32-C`) lack topographic scarps. Surgical pruning of uncorroborated speckles paired with priority-ordered Poisson-disk augmentation across `H32-A/B/C` (`H32-D`) wins **4/4 spatial quadrants** on both `catalogue_hidden_mean` (`0.10122` vs `0.09832`) and `drift_corrected_holdout_mean` (`0.15188` vs `0.14801`).

---

## 3. Pre-Implementation Candidate Geological Hypotheses (`H32-A..D`) & Holdout Validation

Before writing pipeline code, we audited all hypotheses previously tested across `GEMSDOE16..30` and formulated **four untried candidate geological hypotheses**:

| Pre-Impl Rank | Hypothesis ID | Input Layers Used | Physical Signature / Mathematical Transform | Why It Catches Uncatalogued Faults & Differs From Prior Repos | Pre-Impl Expected Gain & Cost | Verified 4-Quadrant Holdout Result |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **#1** | **`H32-D`** | Joint fusion of `H32-A`, `H32-B`, `H32-C`, `D2.8`, `H19-5/H19-4/H16-1/TGC/Ens12`, `labels.tif` | Prunes 500 weakest uncorroborated `D2.8` speckles and adds +2,500 off-catalogue dots (+1,100 `H32-B`, +800 `H32-C`, +600 `H32-A`) at $r_{\min}=2.35\text{ px}$ (`46,090` px; also tested at exact equal budget `44,090` px in `H32-D-Eq44090`). | Removes BFS speckle waste while filling $>300\text{ m}$ holes on dipping range-front, transtensional swarm, and clay-cap conduits without losing `D2.8`'s multi-line backbone. | `+0.0030` to `+0.0045` Holdout DTI; Low cost (~18s CPU) | **Cat-Hid: `0.10122`** (`+0.00290`, **4/4 Quads**)<br/>**SGMC-Cal: `0.06129`** (`+0.00070`)<br/>**Drift-Cal: `0.15188`** (`+0.00388`, **4/4 Quads**) |
| **#2** | **`H32-A`** | `[13] iso_grav_anom`, `[18] iso_grav_anom_hg`, `[2] rtp`, `[3] tmi_hg`, `[15] depth_to_base_surf`, `[17] cond_surf`, `[12] det_elev`, `[19] det_elev_slope`, 3DEP 1m LiDAR | Cross-strike Odd (fault step) vs Even (intrusion) parity $P_{\text{step}} = |\text{Odd}|/(|\text{Odd}|+|\text{Even}|+\epsilon)$ at $\pm 250\text{ m}$, advected up-dip by $\Delta s(\mathbf{x}) = \text{clip}(1.2 + 1.8\,z_+(Z_{\text{base}}), 1.2, 3.0)\text{ px}$. | Corrects the 150–300 m down-dip hanging-wall shift of $45^\circ\text{–}60^\circ$ dipping normal faults beneath alluvial fans. No prior repo decomposed Odd/Even parity or advected gradients up-dip. | `+0.0015` to `+0.0030` Holdout DTI; Low cost (~8s CPU) | **Cat-Hid: `0.10002`** (`+0.00169`, 3/4 Quads)<br/>**SGMC-Cal: `0.06158`** (`+0.00099`)<br/>**Drift-Cal: `0.15083`** (`+0.00283`, **4/4 Quads**) |
| **#3** | **`H32-C`** | `[15] depth_to_base_surf`, `[17] cond_surf`, `[6] tc`, `[2] rtp`, `[12] det_elev`, GeoDAWN Th/K & U/K ratios, 3DEP LiDAR | Angular strike alignment $\cos^2\theta = (\nabla Z_{\text{base}}\cdot\nabla S)^2 / (\|\nabla Z_{\text{base}}\|^2\|\nabla S\|^2)$ gated by MT conductive clay-cap breaching (`cond_surf`) and radiometric alteration edges. | Detects zero-relief blind hydrothermal conduits where argillic alteration erases topographic scarps above a basement step. Prior repos never computed vector strike alignment with `depth_to_base_surf`. | `+0.0015` to `+0.0030` Holdout DTI; Low cost (~7s CPU) | **Cat-Hid: `0.10005`** (`+0.00172`, 3/4 Quads)<br/>**SGMC-Cal: `0.06331`** (`+0.00272`, **Best SGMC**)<br/>**Drift-Cal: `0.15086`** (`+0.00285`, 3/4 Quads) |
| **#4** | **`H32-B`** | `[4] geod_2ndinv`, `[7] geod_shearrate`, `[8] geod_dilaterate`, `[10] deq_n100a15`, `[16] ieq_n100a15`, `[3] tmi_hg`, `[19] det_elev_slope`, 3DEP LiDAR | Kostrov transtensional invariant $\Psi_{\text{transt}} = z_+(\dot{\epsilon}_{kk}>0)\,z_+(\dot{\gamma}) / (z_+(I_2)+0.35)$ coupled with microseismic swarm excess $\ln(1+\text{deq}) - 0.75\ln(1+\text{ieq})$. | Captures active Walker Lane / Great Basin releasing step-overs and fluid-driven swarm permeability where individual quaternary splays are unmapped. | `+0.0010` to `+0.0025` Holdout DTI; Low cost (~6s CPU) | **Cat-Hid: `0.09894`** (`+0.00061`, 3/4 Quads)<br/>**SGMC-Cal: `0.06174`** (`+0.00115`)<br/>**Drift-Cal: `0.14928`** (`+0.00127`, **4/4 Quads**) |

![4-Quadrant Holdout Validation](docs/assets/fig3_h32_hypotheses_quadrant_validation.png)
![Spatial Fault Discovery Maps](docs/assets/fig4_spatial_fault_discovery_maps.png)

---

## 4. Formal Gaussian Process Bayesian Optimization Surrogate & Holdout-to-Leaderboard Drift Analysis

![GP Surrogate and Drift Calibration](docs/assets/fig2_bo_gp_surrogate_and_drift.png)

### 4.1 Three-Mechanism Diagnosis of Surrogate-vs-Leaderboard Drift
1. **SGMC Off-Catalogue Prevalence Drift (`4.94×` Density Inflation, `IR-32-03`):** Raw `sgmc_off_catalogue` has $|G_{\text{SGMC}}| = 62,703$ pixels vs estimated live leaderboard hidden truth $|G_{\text{LB}}| \approx 12,691$ pixels, under-penalizing false positives by $4.94\times$ and ranking the 206,895-pixel uniform grid `GEMS13-Lattice-S5` (true LB `0.0904`) at `0.25092`. Calibrating prevalence to $|G_{\text{LB}}| = 12,691$ predicts `GEMS13-Lattice-S5` at **`0.09361`** (matching true LB `0.0904` within `0.0032`!).
2. **Retrospective Catalogue-Halo Leakage in `GEMSDOE10` (`IR-32-02`):** Pre-built historical rasters `gems10-h28-dotted-ridge` (LB `0.1753`) and `gems10-h25-ctx-ridge` (LB `0.1303`) used full `labels.tif` proximity halos at build time (`4,045` and `12,866` on-catalogue pixels), leaking withheld `hidden_test` components when evaluated retrospectively (`cat_hid = 0.20575` and `0.15725`). Isolating `retrospective_halo_leakage = True` removes this bias.
3. **Catalogue-Exclusion Censorship Calibration:** Combining `0.65 * debiased_catalogue_hidden + 0.35 * sgmc_prevalence_calibrated` into `drift_corrected_holdout_mean` achieves **Pearson $r = +0.9398$ and Spearman $\rho = +0.9333$** across all 9 non-leaking scored DrivenData submissions.

---

## 5. Reproducible Pipeline Execution & Verification

```bash
# 1. Restore/verify all 22 SHA-256-pinned competition, external, and historical scored rasters
bash scripts/download_competition_data.sh

# 2. Sanitize -3.4028235e+38 sentinels and prepare 19 float32 bands in .cache/gems_work/bands/
python3 scripts/prepare_data.py

# 3. Run 4-quadrant holdout validation, GP Bayesian Optimization surrogate, and build/audit GeoTIFFs
PYTHONPATH=src python3 scripts/run_pipeline.py

# 4. Regenerate GitHub Pages documentation (docs/index.html & docs/executive-summary.html)
python3 scripts/build_docs.py

# 5. Run the automated pytest verification suite
PYTHONPATH=src pytest -v
```

---

## 6. Verified Official Reference Links

- **DrivenData Competition Overview & Metric Spec (#306):** https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- **DrivenData Live Public Leaderboard:** https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- **DOE GEMS Official Prize Rules (NREL/TP-5700-96647, Sept 2026):** https://docs.nlr.gov/docs/fy26osti/96647.pdf
- **INGENIOUS Great Basin Regional Dataset Compilation (OpenEI GDR #1391):** https://gdr.openei.org/submissions/1391 (`doi:10.15121/1881483`)
- **USGS ScienceBase Official Layer Releases:** GeoDAWN (`doi:10.5066/P93LGLVQ`), Great Basin MT Conductance (`doi:10.5066/P9TWT2LU`), Isostatic Gravity & Magnetics (`doi:10.5066/P9Z6SA1Z`), Detrended Elevation (`doi:10.5066/P9MQRCBY`), Quaternary Fault Slip/Dilation (`doi:10.5066/P9YL58W6`).
- **Cited Fault-Detection Literature:** Mattéo et al. (2021) JGR Solid Earth (`doi:10.1029/2020JB021269`); Hermant et al. (2025) 50th Stanford Geothermal Workshop (`https://pangea.stanford.edu/ERE/db/GeoConf/papers/SGW/2025/Hermant.pdf`).
