# Euler-lane pre-registration (2026-10-27) — frozen before any Euler fit

**Lane (single method paragraph — this session stays inside it).** ARENA-EULER: sliding-window
3-D Euler deconvolution (Reid et al. 1990; structural index N = 0.25) of the official RTP
magnetic field (band 2) and isostatic gravity field (band 13), retaining depth-concordant
fault-contact solutions (source depth z0 in [300 m, 3,500 m], small horizontal offset and
small least-squares residual, Euler depth concordant between the magnetic and gravity
solutions and with band 15 `depth_to_base_surf`), used *only* as extra label-free channels
in fold-local HistGradientBoosting out-of-fold models on the shared 35-channel template
stack, packed by the shared `gems32.emitter.emit(..., min_sep_px=2.8)` at 37,654 dots
strictly >200 m (B = 2) from visible catalogue faults. No other method family is
implemented this session; the four hypotheses below E1 are ranked backlog only.

## Five candidate hypotheses (layers / signature / why off-catalogue / differs / rank)

| Rank | ID | Layers | Physical signature | Why it should catch a catalogue-missing fault | Differs from repo | Cost / data |
|---|---|---|---|---|---|---|
| 1 (lane) | E1 Euler depth-cluster | Bands 2 `rtp`, 13 `iso_grav_anom`, 15 `depth_to_base_surf`; FFT vertical derivative | Windowed (9×9) least-squares Euler solutions (x0,y0,z0,B); density of low-residual, depth-concordant contacts | Buried basement–alluvium contacts under 50–200 m of Quaternary fill have no scarp for the USGS/INGENIOUS mappers but still offset density/magnetisation at depth | `tmspi.py` uses a local-wavenumber *proxy* `k=|∇TDR|`, `z≈1/k`; no prior code solves the 4-unknown Euler normal equations or cross-checks magnetic vs gravity z0. GEMSDOE40's live Euler (0.0397, owner report) was unfiltered — this lane filters by residual/offset/depth concordance and never emits Euler alone without the GBM test (EXP1 measures exactly that failure mode) | Low (~5 min FFT + chunked solve). 100% in-band, SHA-pinned |
| 2 | E2 Eikonal relay geodesics | Bands 7/8 strain, 13 gradient, GDR #1391 vents | Fast-marching minimum-action paths between en-échelon tips curved by potential-field strike | Relay ramps/step-overs host geothermal upwelling (Faulds & Hinz 2015) with throw below mapping threshold | Already registered as H48-3; Euclidean tip cones exist, no PDE geodesic. **Backlog — not implemented (single-lane rule)** | Medium; in-band + pinned GDR |
| 3 | E3 Phillips curvature tensor | Bands 2, 13, 14 | Full curvature tensor of potential fields (Phillips et al. 2007), strike-coherent maxima | Curvature maxima track buried contact strike where gradient magnitude is diffuse | Registered as H36-2, never run standalone. **Backlog** | Low; in-band |
| 4 | E4 Multi-depth MT persistence | Band 17 `cond_surf` + external 3-D MT cubes | Sub-vertical <15 Ω·m roots persisting 0.5→10 km depth | Images fluid-filled fault zones under conductive playa clay, blind to LiDAR/radiometrics | Only a single 2 km slice (band 17) is in the cube. **Data-blocked here** — free source: DOE GDR / EarthScope MT (https://gdr.openei.org/), CC-BY; sandbox egress allows only github/pypi, so NOT obtainable in this sandbox → not proposed as viable now | Medium; external mirror needed |
| 5 | E5 Relocated seismicity planes + InSAR | External GrowClust/ComCat + Sentinel-1 | RANSAC hypocentre planes 2–12 km + InSAR phase-gradient breaks | Active blind faults (e.g. 2020 M6.5 Monte Cristo Range) light up seismically with no pre-existing scarp | Registered as H33-E/H48-5. **Data-blocked here** — free official source: USGS ComCat FDSN https://earthquake.usgs.gov/fdsnws/event/1/ and ASF Vertex Sentinel-1; both outside sandbox egress whitelist → deferred, not viable now | High; external |

## Frozen protocol (shared tools only — no private fork)

- Features: template cached stack (`scripts/build_features.py` → `.cache/gems_work/feature_stack.npy`, 35 ch) + new `src/gems32/euler.py` stack (7 ch). Every catalogue-based feature is derived **only from fold-visible faults**.
- Holdout: `gems32.holdout` hide-and-recover — whole fault segments withheld with 1.5 km collar, visible faults masked pixel-exactly, pooled DTI (α=0.2, β=0.8, 300 m triangular kernel), evaluator `GEMSDOE32-HIDE-RECOVER-v3.0` (22,232 withheld positives) + off-catalogue `GEMSDOE32-SGMC-CAL-v3.0` (62,703 SGMC positives). Champion reference: `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` re-scored on the *same* evaluator in this run.
- Leakage canary: every feature alone, two-polarity AUC vs catalogue; AUC > 0.90 = leakage, abort.
- Uniqueness (pre-placement surface AND final dots): Spearman ρ vs every registry raster ≤ 0.90 and ≤70% of dots within 3 px of any one registry raster (`gems32.release_gate` / `registry_audit`); drift beyond either = duplicate, log and stop.
- Emission/writing: shared `gems32.emitter.emit` + `scripts/submission_writer.py` (zeros variant, nodata=None, all 12,279,160 cells finite in [0,1] — fixes the portal error “Predicted values must be in range [0, 1]”).
- Budget: ≤3 experiments, ≤2 h. Promotion (`verdict=promote`) requires: canaries pass, fold-local HOLDOUT-DTI beats the same-evaluator champion with paired 95% CI > 0, no SGMC-cal regression vs champion, literal uniqueness passes, saved-byte validator passes. Weekly-slot selection is a separate step — this run spends **0 slots**.
- Named non-fault mimic: unfaulted pluton margins and dike edges (also Euler contacts) and tabular basalt flow margins; de-confounded by requiring magnetic–gravity depth concordance + GBM context (strain, MT, topography) rather than Euler response alone.

## Experiments (frozen)

1. **EXP1_EULER_ONLY** — unsupervised Euler joint-density surface → CELF 37,654 dots. Tests whether Euler alone repeats GEMSDOE40's 0.0397 failure.
2. **EXP2_BASE35_OOF** — fold-local HGBT on 35 template channels only (control).
3. **EXP3_BASE35_EULER_OOF** — same fits + 7 Euler channels (treatment); if it wins, the live candidate is the full-catalogue retrain of EXP3 with `min_sep_px=2.8`.

*Official sources for manual review:* Reid et al. 1990 Euler deconvolution (Geophysics 55, 80–91);
Blakely 1995 *Potential Theory in Gravity and Magnetic Applications* (FFT vertical derivative);
competition metric https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ ;
GeoDAWN https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and ;
INGENIOUS https://gbcge.org/current-projects/ingenious/ ; EPSG:32611 https://epsg.io/32611 ;
Tversky index https://en.wikipedia.org/wiki/Tversky_index .
