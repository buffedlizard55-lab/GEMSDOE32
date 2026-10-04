# Candidate Geological Hypotheses & Validation Register (GEMSDOE32)

**Author:** GEMSDOE32 Autonomous Research Session · **Date:** 2026-10-04  
**Guiding Values:** *Maximize P(Win)* · *Own the Outcome*  
**Validation Standard:** S-Block Holdout Cross-Validation & Bayesian Optimization Expected Improvement

---

## 1. Summary of Untried Geological Hypotheses

Before implementing new submissions, we generated 5 candidate geological hypotheses targeting blind and unmapped geothermal fault systems in the Great Basin. Each hypothesis leverages specific physical mechanisms, distinct data layers, and is evaluated against our leak-free spatial block holdout set.

| Hypothesis ID | Name & Core Concept | Key Data Layers | Physical Signature / Transform | Why Missing from USGS / INGENIOUS | Expected DTI Gain | Impl. Cost | Rank |
|---|---|---|---|---|---|---|:---:|
| **H32-1** | **Anisotropic Extensional Dilation & Permeability Tendency** | GeoDAWN TMI (`TMI_up150`), Structural Strike Tensors | $T_d = \sin^2(\theta - 115^\circ)$ dilation tendency aligned with regional $S_{hmin}$ | Catches blind normal faults under alluvium that have high permeability but no major surface scarp | **+0.040 to +0.060** | Low | **1** |
| **H32-2** | **Multi-Scale Topographic Knickpoint & Scarp Curvature** | 1m LiDAR DEM, Multi-scale Gaussian $\sigma=1,2,4$ | Profile curvature $-\frac{z_{xx}z_x^2 + 2z_{xy}z_xz_y + z_{yy}z_y^2}{p(1+p)^{1.5}}$ and Hessian eigenvalues | Uncovers subtle late-Pleistocene/Holocene scarps (10–50 cm) missed in 1:250k regional maps | **+0.025 to +0.045** | Moderate | **2** |
| **H32-3** | **Quaternary Volcanic Vent Alignment & Thermal Corridors** | GDR Quaternary Volcanics, 2m Thermal Probes | Anisotropic Gaussian directional kernel along $N30^\circ\text{E}$ strike | Detects blind hydrothermal upflow feeder faults connecting separate volcanic centers | **+0.020 to +0.035** | Low | **3** |
| **H32-4** | **En-Echelon Relay Ramp Step-Over Stress Concentrations** | USGS SGMC off-catalogue linework, Fault tip density | Second-order spatial interaction kernel on overlapping fault tips | Breached relay ramps contain complex cross-fault networks omitted from simplified regional shapefiles | **+0.015 to +0.030** | Moderate | **4** |
| **H32-5** | **GeoDAWN Radiometric Alteration & Magnetic Demagnetization** | Airborne Radiometric $K/Th$, $U/K$, Total Magnetic Intensity | Potassic alteration halo ($K$ enrichment) coupled with magnetic susceptibility low | Hydrothermal alteration halos extend 50–200 m into host rock, revealing buried fluid pathways | **+0.015 to +0.025** | Low | **5** |

---

## 2. Deep Dive into Top Candidates

### Hypothesis H32-1: Anisotropic Extensional Dilation Tendency
* **Tectonic Context:** The Great Basin / Walker Lane transition zone is governed by active WNW-ESE crustal extension ($\sigma_3 = S_{hmin} \approx 115^\circ \pm 10^\circ$).
* **Physics & Equation:** Faults striking $025^\circ - 035^\circ$ NNE experience the lowest normal stress $\sigma_n$ and maximum dilation tendency:
  $$T_d = \frac{\sigma_1 - \sigma_n}{\sigma_1 - \sigma_3} = \sin^2(\theta - \theta_{S_{hmin}})$$
* **Differentiation from prior repo code:** Prior iterations treated edge gradients isotropically. H32-1 explicitly weights predictions by the dynamic stress tensor and magnetic basement continuity.

### Hypothesis H32-2: Multi-Scale LiDAR Scarp Curvature
* **Geomorphic Context:** Fault scarps undergo progressive diffusive degradation over time. 
* **Physics & Equation:** Multi-scale profile curvature filters out high-frequency erosion rills while amplifying persistent tectonic knickpoints:
  $$k_{\text{prof}} = -\frac{z_{xx} z_x^2 + 2 z_{xy} z_x z_y + z_{yy} z_y^2}{(z_x^2 + z_y^2)(1 + z_x^2 + z_y^2)^{3/2}}$$

### Hypothesis H32-3: Quaternary Volcanic Vent & Thermal Corridors
* **Geothermal Context:** Magmatic heating and convective hydrothermal systems cluster along structural step-overs and deep feeder faults.
* **Physics:** Anisotropic bivariate kernel projection with $\sigma_{\text{along}} = 3000\text{ m}$ along strike ($N30^\circ\text{E}$) and $\sigma_{\text{across}} = 800\text{ m}$.

---

## 3. Spatially Blocked Holdout Validation Results

Evaluated across 2 spatial cross-validation blocks ($2 \times 2$ disjoint tiles) with catalogue positive masking:

| Candidate Configuration | Mean Holdout DTI | Surrogate EI | Live Spend Decision |
|---|:---:|:---:|:---:|
| `H32-1_Extensional_Dilation` | 0.1329 | 0.00030 | Hold (EI below threshold) |
| `H32-2_MultiScale_Scarp` | 0.1373 | 0.00268 | Hold (EI below threshold) |
| `H32-3_Vent_Corridor` | 0.1378 | 0.00000 | Hold |
| `H32-4_Relay_Stepover` | 0.1362 | 0.00115 | Hold |
| `H32-5_Alteration_Composite` | **0.1383** | 0.00000 | Hold |
| `H32-Top_BayesOpt_Hybrid` | 0.1347 | 0.00005 | Hold |

---

## 4. Official Verified References
- **NLR GEMS Rules (September 2026):** [docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- **DrivenData Problem Description:** [drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- **USGS GeoDAWN Geophysical Data (Glen & Earney 2024):** [doi.org/10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)
- **INGENIOUS Geothermal Data Compilation:** [gdr.openei.org/submissions/1391](https://gdr.openei.org/submissions/1391)
