# Arena9 preregistration — physics-protected reliable-negative PU within the MDRC lane

**Frozen before model fitting:** 2026-10-26 UTC  
**Lane:** `A9-H1 MDRC-PGRN-PU` only. No other hypothesis below will be implemented in this run.  
**Budget:** three experiments, no DrivenData upload, at most two hours of experimental runtime.  
**Promotion rule:** a live slot remains a separate selector decision. This run can only recommend `promote` when all fail-closed gates pass.

## Why this is the next experiment

The prior `A8A-H1 MDRC` run found a specific falsifiable failure: its label-free LiDAR and four-domain surfaces performed well on the off-catalogue SGMC proxy, but ordinary binary training marked every unlabelled pixel as a negative and suppressed that signal (`IR-A8A-PU-BIAS-01`). Elkan–Noto probability scaling alone cannot change a ranking, so it cannot improve a fixed-budget dot map. This run instead changes which unlabelled pixels may become **reliable negatives**: pixels with high label-free multi-physics concordance are protected from negative sampling. Catalogue labels are used only as positives; every fold derives distance-to-catalogue and its reliable-negative pool from that fold's visible fault segments.

## Five ranked, not-yet-tested geological hypotheses

| Rank | ID and hypothesis | Specific layers | Physical signature / transform | Why it may recover a missing rather than already-catalogued fault | Difference from this repository before this run | Expected HOLDOUT-DTI improvement / implementation cost | Viability |
|---:|---|---|---|---|---|---|---|
| **1** | **`A9-H1` Physics-Guarded Reliable-Negative PU (`MDRC-PGRN-PU`)** | Cached 35-channel official feature stack plus 22 label-free MDRC channels: 1 m 3DEP LiDAR step/dipole/coherence; RTP/TMI tilt; gravity/base/MT edges; GeoDAWN K/Th and redox; GDR temperature/geothermometer halo | Protect the upper tail of a label-free four-domain concordance rank from the negative pool; train spatially buffered bagged HistGB only on visible positives and low-concordance, >500 m reliable negatives; multiply the OOF posterior by a soft physical-concordance gate, ridge-sharpen, then B=2 + 300 m CELF | An unmapped blind or piedmont fault can have high independent LiDAR/potential-field/alteration evidence while being absent from the catalogue. Standard positive-vs-all-unlabelled training calls exactly that pixel negative; protecting it removes that asymmetric suppression without reading SGMC truth | `A8A` used all unlabelled training pixels as negatives. `H36-1` excluded a 500 m halo but did **not** exclude high multi-physics unlabelled candidates using a label-free prior. Formal Elkan–Noto rescaling was not used because it is rank-invariant | **Highest:** target `+0.008–0.025` over A8A (`0.10679`) and > current same-repo hide/recover best (`0.11696`); medium CPU, all data cached | **Selected and locally viable.** Inputs restored from hash-pinned owner mirrors; no new external data needed |
| 2 | `A9-H2` Shallow-source tilt-depth discordance | `rtp`, `tmi_hg`, `tmi_vg`, `TMI_up150`, `depth_to_base_surf`, gravity VG/HG | Miller–Singh tilt zero contour plus Salem inverse tilt-gradient depth; score where shallow magnetic-contact depth is much less than basin depth and the edge partly survives 150 m upward continuation | Flat alluvial basins can conceal faults that offset shallow volcanic interbeds; these retain a shallow potential-field contact without a mapped surface scarp | MDRC contains separate tilt and upward-continuation residual channels but has not fitted an explicit `z_tilt / z_base` discordance surface and persistence ratio | Moderate `+0.003–0.010`; low cost | Viable from cached official competition/GeoDAWN layers; not run because of the single-lane rule |
| 3 | `A9-H3` Alteration mass-balance boundary | GeoDAWN K, Th, U, Th/K, U/K, U/Th; `cond_surf`; RTP Laplacian | Robust local compositional residual (K conditional on Th+U) followed by multi-scale change-point/Hessian boundary detection, intersected with conductive-cap edge and magnetic-demagnetization trough | Hydrothermal alteration can outline a permeable conduit where young displacement is too small for inclusion in a Quaternary fault compilation | Existing code uses K/Th gradients and a weighted alteration channel; it does not residualize K against both Th and U before boundary detection | Small–moderate `+0.002–0.008`; low cost | Viable from cached USGS GeoDAWN-derived layers; not run |
| 4 | `A9-H4` Signed throw-persistence scarplet tensor | 1 m 3DEP `step_max`, `lapneg`, `lappos`, `downface_max`, `upface_max`, `cross_max`, `coh100`, strike | Require consistent signed downface/upface asymmetry and strike over nested 100–700 m windows; use a structure-tensor eigenvalue ratio and cross-scale persistence, not a single-scale weighted sum | Degraded sub-metre piedmont scarplets can be coherent over hundreds of metres yet too low-relief for regional mapping; fluvial risers should reverse/branch more often | MDRC uses local one-sided polarity and a 500 m chain mean, but no signed cross-scale persistence tensor | Moderate `+0.002–0.008`; medium cost | Viable from cached 3DEP-derived stack; not run |
| 5 | `A9-H5` Relocated microseismic up-dip planes | USGS ComCat event hypocentres and focal mechanisms; optional NBMG/USGS 2020 Monte Cristo rupture vectors | Robust 3-D planar clustering, strike/dip fit, up-dip projection to the surface, then density-ridge extraction | Seismically active blind faults need not have catalogue scarps and may post-date the source compilation | Competition earthquake bands are 100 km aggregates; no event-level planar relocation model exists in this repository | Potentially high; high data/quality-control cost | **Not currently viable in this sandbox.** Official free sources are USGS ComCat (`https://earthquake.usgs.gov/fdsnws/event/1/`) and USGS ScienceBase, but the current outbound allowlist does not permit either host. No claim is made that the required event quality is available until fetched and audited |

## Frozen three-experiment design for `A9-H1`

All three arms use the same 57 leak-screened channels, spatial folds, visible-fault-only 1.5 km training buffer, B=2 visible-fault exclusion, 37,654-dot budget, and exact 300 m triangular-kernel emitter.

1. **EXP1 `PGRN80`:** protect the top 20% of label-free MDRC concordance; sample reliable negatives from the lower 80% and farther than 500 m from visible faults.
2. **EXP2 `PGRN60`:** stricter contamination control; protect the top 40%, using only the lower 60% as reliable negatives.
3. **EXP3 `PGRN-BAG`:** average fold-local `PGRN60`, `PGRN70`, and `PGRN80` posteriors before applying the physical gate and ridge sharpening. This is the preregistered primary arm.

No threshold will be changed after looking at SGMC. The selected output is the arm with the highest compliant `GEMSDOE32-HIDE-RECOVER-v3.0` pooled DTI; SGMC is a secondary falsification gate, not a tuning label.

## Frozen automated gates

- **G1 leakage:** two-polarity single-feature AUC `<= 0.90` for all 57 channels.
- **G2 holdout:** selected arm beats both the exact-evaluator `0.2778` champion and the repository's current same-evaluator best (`H38-G1`, HOLDOUT-DTI `0.11696`) and has a positive paired spatial-bootstrap delta lower bound against the champion.
- **G3 independent off-catalogue check:** SGMC-calibrated DTI beats champion `0.06412`; SGMC labels are never used in model fitting or arm selection.
- **G4 uniqueness:** before placement, full-footprint `|Spearman| <= 0.90`; after placement, `|Spearman| <= 0.90` and directional within-3-pixel overlap `<= 70%` for every refreshed focus-registry raster. Constant/blank/data-template rasters are classified and reported, not silently treated as detector surfaces. The synthetic spacing-5 covering lattice is reported literally and separately because it covers essentially the whole footprint.
- **G5 format:** shared `submission_writer.py`; one `float32` band, exact template CRS/shape/transform, `nodata=None`, all 12,279,160 cells finite in `[0,1]`, zero known-catalogue pixels.

Only `G1 ∧ G2 ∧ G3 ∧ G4 ∧ G5` yields `verdict = promote`. Otherwise the unique GeoTIFF remains downloadable for research but is labelled **DO NOT SUBMIT**.

## Source chain for manual review

- Official organizer reference implementation: <https://github.com/drivendataorg/gems-prize-reference-solution>
- DOE GEMS competition problem/metric: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- USGS GeoDAWN data release landing page: <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
- OpenEI GDR INGENIOUS record 1391: <https://gdr.openei.org/submissions/1391>
- USGS 3DEP: <https://www.usgs.gov/3d-elevation-program>
- Elkan & Noto, learning classifiers from positive and unlabelled data: <https://doi.org/10.1145/1401890.1401920>

The competition and USGS/OpenEI pages are listed for manual review; this sandbox can currently retrieve GitHub but not those hosts. Local inputs are accepted only after matching the SHA-256 values in `registry/data_manifest.json`; that proves mirror integrity, not organizer authentication.
