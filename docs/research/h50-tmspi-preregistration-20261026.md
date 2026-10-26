# Frozen Pre-Registration: Five Untried Geological Hypotheses (`H50-1` .. `H50-5`) and Single-Lane Execution Plan (`H50-1: TM-SPI`)

**Frozen before any H50 experiment, feature construction, or holdout call.**
**Branch:** `arena/8b5ffdb0-gemsdoe32`
**Selected single lane (Protocol Rule 1):** `ARENA48-H1-TMSPI` / `H50-1`
**Budget (Protocol Rule 6):** ≤ 3 experiments, ≤ 2 hours, 0 DrivenData weekly slots.

Lane paragraph:

> ARENA48-H1-TMSPI — Unsupervised dual-field Thurston–Smith (1997) source-parameter local-wavenumber contact skeleton: compute Miller–Singh TDR on magnetics (`tmi_vg`, `tmi_hg`) and isostatic gravity (`iso_grav_anom_vg`, `iso_grav_anom_slope`) solely as the parent of \(k=|\nabla\mathrm{TDR}|\), retain Euler-\(N\approx 0\) contacts in the 0.4–6 km SPI depth window, weight by the Wijns (2005) theta-map edge strength \(\pi/2-\arccos(\mathrm{HG}/\mathrm{AS})\), take the geometric mean of magnetic and gravity contact credibilities, skeletonize by 3×3 morphological NMS (not Steger, not TDR zero-crossings), and pack 37,654 dots by exact 300 m CELF. Catalogue rasters are never read during feature construction.

---

## Why `h33-h33-2-b2` (`0.2778` OWNER-REPORT) leads the nine focus sites

The nested B-pruning sequence (H19-5 `121,131` → D2.8 `44,090` → B=1 `40,199` → B=2 `37,654`) is a **metric** mechanism, not a new geological detector: known-catalogue pixels are masked before scoring ([staff #11516](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)), so deleting predictions inside 200 m of mapped faults cuts wasted false-positive mass. Historical scores are **OWNER-REPORT**, not ORGANIZER-CONFIRMED. On this repository's hide-and-recover instrument the same file scores far below the live number (see prior run cards). Beating `0.2778` live requires covering *unmapped* traces the H19-5 family missed, not re-thinning that family (which fails the 70% 3-px uniqueness rule).

Official metric: Distance-Weighted Tversky Index, \(\alpha=0.2\), \(\beta=0.8\), 300 m triangular kernel, EPSG:32611 100 m grid ([problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)).

---

## Five candidate hypotheses (keyword-untried as a *primary* detector)

| Rank | ID | Layers | Physical signature | Why it can catch a catalogue-missing fault | Difference vs this repo | Expected DTI (prior, not a score) | Cost / data |
|---:|---|---|---|---|---|---|---|
| **1 (lane)** | **H50-1 TM-SPI** | Official bands 3 `tmi_hg`, 9 `tmi_vg`, 5 `iso_grav_anom_slope`, 11 `iso_grav_anom_vg` | Thurston–Smith local wavenumber \(k=\|\nabla\mathrm{TDR}\|\) × Wijns theta-map edge × mag∩grav geometric mean; morphological NMS | Blind basement contacts under alluvium keep Euler-\(N\approx 0\) k-depth even with no scarp (Faulds & Hinz 2015; ~75% of Great Basin systems are blind) | H36 used TDR *zero-crossings* + TDX as GBDT *features* + Steger NMS. This lane ranks SPI depth-windowed theta-map peaks and does not use DEM/LiDAR/PU/Steger | medium, uncertain | low; bands on disk |
| 2 | **H50-2** polarity-reversal accommodation zone | Band 18 `iso_grav_anom_hg` (signed \(\partial g/\partial x\)), Band 5 | Sign-change saddles of east- vs west-dipping half-grabens | Faulds et al. 2013: 41% of GB geothermal systems sit at step-overs / accommodation zones often omitted from Quaternary maps ([OSTI 1148722](https://www.osti.gov/biblio/1148722)) | H36 registered `H36-4` and used polarity as one of 46 channels; never the emission skeleton | medium | low; Band 18 on disk |
| 3 | **H50-3** Blakely–Simpson 1986 HGM peak picker | Bands 5 and 3 | 4-neighbour maxima of \(\|\nabla_h g\|\) and \(\|\nabla_h T\|\) | Classic USGS contact picker; independent of topography | Keyword-untried as a named method here (GEMSDOE73 used “Blakely” in a different pipeline) | low–medium | low |
| 4 | **H50-4** Getis-Ord \(G_i^*\) of lineament density | any 1-px crest field | Spatial hotspot of crest density as a multiplicative prior | Regional fabric corridors vs isolated noise | README listed it as untried; never executed | low | low |
| 5 | **H50-5** GeoDAWN block-normalized silica-core / potassic-halo DoG | `geodawn_rad_u8.tif` K, eTh, TC | Concentric DoG of low-TC silica cores vs high K/Th halos | Fossil epithermal vents with no scarp | H46-4 registered, not built. Needs `acquisition_block_id_100m.tif` (not in this restore) | low, data-blocked here | blocked |

No candidate requires a new host that is not already restored, except H50-5.

---

## Three frozen experiments (H50-1 only)

1. **EXP1_MAG_TMSPI** — magnetic theta × SPI window, morphological NMS, 37,654-dot CELF.
2. **EXP2_GRAV_TMSPI** — gravity theta × SPI window, same emission.
3. **EXP3_DUAL_CONCORDANCE** (selected file) — geometric mean of EXP1 and EXP2 beliefs, NMS, CELF.

Gates (fail closed; no human inspector):

- Canary: every TM-SPI channel `max(AUC, 1−AUC) ≤ 0.90` on public labels.
- Primary HOLDOUT-DTI on `GEMSDOE32-HOLDOUT-v3-visible-gated` (22,232 withheld positives) with paired 95% CI vs champion excluding 0.
- SGMC-cal diagnostic reported, not treated as a leaderboard score.
- Genuine uniqueness: Spearman ≤ 0.90 and ≤ 70% of dots within 3 px of any genuine local raster.
- Literal lattice overlap is reported; dense 37,654-dot maps fail it by pigeonhole (`IR-42-UNIQ-01`).
- Format: `scripts/submission_writer.py` / `audit_geotiff` all cells finite in `[0, 1]`.
- Promotion to a live slot is a **separate selector** step. This runner never spends a slot.

---

## Official sources

- [DrivenData GEMS problem / metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) DOI 10.5066/P93LGLVQ
- [INGENIOUS GDR #1391](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
- Wijns, Perez & Kowalczyk (2005), *Theta map: Edge detection in magnetic data*, Geophysics. https://doi.org/10.1190/1.1883351
- Thurston & Smith (1997), *Automatic conversion of magnetic data to depth, dip, and susceptibility*, Geophysics.
