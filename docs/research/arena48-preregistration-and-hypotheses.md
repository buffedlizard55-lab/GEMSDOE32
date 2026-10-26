# ARENA48 preregistration — five ranked hypotheses, one frozen lane (2026-10-26)

**Frozen before any ARENA48 experiment:** 2026-10-26T21:31:49Z · Branch `arena/a57e7506-gemsdoe32`
**Competition:** DOE GEMS Prize, DrivenData #306 — [competition](https://www.drivendata.org/competitions/306/competition-doe-gems/) ·
[problem & metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) ·
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)

**Evidence labels (Protocol Rule 3, applied to every number in this session):**
`HOLDOUT-DTI` = local evaluator result, always stated as (evaluator version, withheld positives, 95% CI).
`OWNER-REPORT` = a score the owner recorded from a DrivenData screen; this repository holds **no**
submission-page receipt linking any group file's bytes to its score (IR-32-SCORE-01), so
`ORGANIZER-CONFIRMED` is used for **no** group score, including 0.2778.
`MODEL` = algebra / projection on the published metric or on a local calibration.
**A projection is never written as a score.** Live public-leaderboard rows read directly from the
official page this session are labelled with their read timestamp.

**Lane-assignment irregularity (flagged, not hidden):** the PARALLEL-RUN PROTOCOL says
"Your lane is the single method paragraph below", but the supplied prompt contains no distinct
assigned method paragraph (same absence recorded by ARENA47). This document therefore freezes
exactly one lane (§2) before any experiment and stays inside it. If its surface rank-correlation
vs any registry raster exceeds 0.90, or >70% of its final dots fall within 3 px of one genuine
registry raster's dots, it is logged as a duplicate and stopped (Protocol Rule 1). The synthetic
5-px calibration lattice (`13gems_20261001_r13-lattice-s5_v2`, 206,895 dots, 99.87% footprint
coverage within 3 px; champion itself 99.92%) is reported separately as IR-42-UNIQ-01 — it is a
calibration ruler, and the literal all-raster result is always shown alongside the genuine result.

**Budget (Protocol Rule 6):** at most **3 experiments**, ~2 h. Verdict `promote` only recommends
the file to the separate weekly-slot selector; this session does not spend a slot.

**Shared tools only (Protocol Rule 2):** cached 35-channel stack (`src/gems32/features.py`),
`scripts/evaluate_holdout.py` → `src/gems32/holdout.py` (`GEMSDOE32-HIDE-RECOVER-v3.0`:
whole-component hide-and-recover, 15-px collar, catalogue features/gates derived only from
visible faults per cell, pixel-exact visible masking, pooled DTI α=0.2 β=0.8, 300 m triangular
kernel, 22,232 withheld positives) and `scripts/submission_writer.py` → `src/gems32/submission.py`.
No private forks of evaluator/writer/metric.

---

## 1. Five candidate geological hypotheses not yet tried *as executed lanes*, ranked

Ranking = expected DTI improvement ÷ implementation cost, judged before running anything.
"Expected" is qualitative judgement only — no projected live score is stated for any hypothesis.

| Rank | ID | Layers | Physical signature / transform | Why it should catch a fault *missing* from USGS/INGENIOUS | How it differs from everything executed in this repo | Expected gain · cost · data |
|---:|---|---|---|---|---|---|
| **1 — BUILD** | **A48-H1 JXSTEP: fault-juxtaposition step concordance** | Official bands 15 `depth_to_base_surf`, 13 `iso_grav_anom`, 17 `cond_surf`, 6 `tc` (radiometric total count, verified ρ=+0.99942 vs GeoDAWN TC — *not* tilt), 12 `det_elev` (only to build a surface-*roughness* field and a DEM-quiescence gate) | A fault *juxtaposes two different blocks*. At 4 orientations, fit a concentrated **step-vs-ramp** cross-profile (inner ±2–3 px means vs outer ±6–7 px means; score = step × clip(2−ramp-ratio,0,1)) independently in basement depth, gravity, conductivity, radiometric composition and DEM roughness (local σ), then require **same-orientation concordance** across fields (geometric mean at the argmax orientation), with a quiescent variant that down-weights pixels where the *elevation* itself already steps | The catalogue is a surface-scarp compilation: a fault whose elevation scarp is buried/degraded is structurally absent from it, but its block juxtaposition still steps basement depth, density (gravity), alteration conductivity, surface texture/age and radiometrics across the trace. Concordance across independent physics is what an expert drafter uses to draw a fault with no scarp | R6-1 fit step-vs-ramp to **elevation only**; H35-C/H32-C used gradient-*magnitude* alignment of cond/depth; MDRC used a basement-step *magnitude* channel inside a 57-ch HistGB; Arena41 screened `grad_mag(depth)`. Nobody has (a) fit step-concentration to non-elevation fields, (b) required same-orientation concordance across ≥3 fields, (c) used a *second-moment* (roughness) step, or (d) gated on elevation *quiescence* to target the no-scarp population (H61-1 registered the quiescence idea in Round 2 but was never run) | Moderate–high · Low (label-free convolutions + one HistGB OOF; all bands on the hash-pinned mirror, DOI [10.5066/P93LGLVQ](https://doi.org/10.5066/P93LGLVQ)) |
| 2 | A48-H2 ASTD: analytic-signal contact-depth vs basement discordance | Bands 2 `rtp`, 3 `tmi_hg`, 9 `tmi_vg`, 15 `depth_to_base_surf`, GeoDAWN `TMI_up150` | Roest 3D analytic signal \|A\|=√(tmi_hg²+tmi_vg²); structural-index-1 depth z_AS=\|A\|/\|∇\|A\|\|; target crests where z_AS ≪ depth_to_base inside deep basins (a shallow displaced magnetic horizon above deep basement) | Intra-basin faults displace shallow Neogene volcanic horizons under flat playa — zero scarp, but a shallow magnetic contact where basement is kilometres deep | Proposed as H44-3 and one analytic-signal channel exists inside SPCP (`spcp.py` ch 5–6), but the *depth-discordance ratio* vs band 15 was never built or gated standalone (grep-verified 2026-10-26: no `z_AS`/discordance in `src/`) | Moderate in blind basins only · Low · data cached |
| 3 | A48-H3 BADOG: survey-block-normalised silica-core / potassic-annulus DoG | `acquisition_block_id_100m.tif` (GeoDAWN 4-block polygons), `geodawn_rad_u8` K/eTh/eU/TC, extensions Th/K/U/K/U/Th, band 6 `tc` | Standardise radiometrics *within* each GeoDAWN acquisition block (kills flight-season/radon seams), then difference-of-Gaussians: low-TC silica-leached core (σ=1.5 px) ringed by high-K/Th adularia/illite halo (σ=5 px) | Fossil/blind geothermal upflow zones have zoned silicic-core→potassic-halo alteration along the conduit fault with no scarp required | Proposed as H46-4, explicitly "reserved for next round"; H38/H44 used *global* z(K)−z(Th) with no block normalisation and no annulus geometry. **Obtainability checked this session:** `data/external/audit_sources/acquisition_block_id_100m.tif` exists in the GEMSDOE24 mirror (verified via `gh api` tree listing 2026-10-26) — viable, but not yet in `registry/data_manifest.json`, so it needs a new hash pin before use | Low–moderate (vent-localised) · Low · obtainable (above) |
| 4 | A48-H4 CHI: drainage χ / knickpoint disequilibrium lineaments | Needs true DEM (USGS 3DEP, [usgs.gov/3d-elevation-program](https://www.usgs.gov/3d-elevation-program)); band 12 is *detrended* elevation and cannot be flow-routed | Channel-steepness (k_sn) / χ residuals aligned along strike: an active concealed fault perturbs drainage profiles far beyond its scarp | Streams respond to blind uplift/slip even when no scarp is preserved in the fan surface | H60-5 registered it (Round 2) and it was never run in any GEMSDOE repo lane that scored; **not viable in this sandbox** (3DEP tiles unreachable under the github/pypi/npm allowlist; detrended band 12 is not a routable DEM). Named here only with its free official source; *not proposed as viable this session* | Unknown · High · **blocked** |
| 5 | A48-H5 MSEIS: relocated microseismicity hypocentre lineaments | USGS FDSN/ComCat event catalogue, free official ([earthquake.usgs.gov/fdsnws/event/1](https://earthquake.usgs.gov/fdsnws/event/1/)) | Linear hypocentre clusters (fault-plane illumination) projected to surface traces; the competition's two seismic bands are ~100-km-smoothed and carry no fault-scale signal | Active faults slip seismically whether mapped or not (e.g. the 2020 Mw 6.5 Monte Cristo Range rupture ran largely on unmapped segments) | Never built; every seismic attempt used the smoothed bands. **Not viable in this sandbox** (`earthquake.usgs.gov` outside the allowlist; `scripts/fetch_earthquake_catalog.sh` is ready for an unrestricted machine) | Moderate · High · **blocked** |

## 2. Frozen lane (single method paragraph) and the ≤3 experiments

**Lane A48-H1-JXSTEP:** *Build seven label-free juxtaposition channels from official bands
13/15/17/6 and a DEM-roughness field derived from band 12 — per-field oriented step-vs-ramp
concentration (`jx_step_depth`, `jx_step_grav`, `jx_step_cond`, `jx_step_tc`, `jx_step_rough`),
their same-orientation concordance (`jx_concordant`, geometric mean of the robust-normalised
per-field scores at each orientation, maximised over orientation), and a blind variant
(`jx_quiescent` = concordant × exp(−normalised elevation step)) — test every channel alone
(leakage canary, two-sided AUC ≤ 0.90, Protocol Rule 4), then (Exp 1) emit the unsupervised
`jx_concordant` crest alone, (Exp 2) add the seven channels to the shared 35-channel stack in a
4-quadrant spatially-buffered (1.5 km collar) HistGB OOF with hard-flank negatives exactly as
the shared H38 recipe, and (Exp 3, only by the pre-registered rule below) sequentially residual-allocate
at most 15% of the 37,654-dot budget to the `jx_quiescent` crest after the Exp-2 emission; every
emission is per-cell visible-only B=2 (>200 m from *visible* faults) via the shared exact
300 m lazy-greedy emitter, scored pooled on `GEMSDOE32-HIDE-RECOVER-v3.0` (22,232 withheld
positives) with the off-catalogue `GEMSDOE32-SGMC-CAL-v3.0` diagnostic (62,703 positives),
uniqueness-checked on the pre-placement surface and on final dots, and written only through
`scripts/submission_writer.py` as an all-finite `nodata=None` `-zeros.tif` in [0,1].*

**Named non-fault mimic:** unfaulted lithologic contacts (Mesozoic pluton walls, ash-flow-tuff
unit boundaries, caldera margins) and Pleistocene Lake Lahontan shoreline benches juxtapose the
same fields without a through-going geothermal conduit fault. De-confounding inside the lane:
step-*concentration* (a gradational contact is a ramp, c→0), same-orientation concordance across
independent physics, and the supervised OOF (Exp 2) learning which juxtapositions co-occur with
mapped faults. The mimic is also the main failure risk and is stated on the run card.

**Pre-registered Exp-3 rule (no post-hoc search):** run Exp 3 *only if* Exp 2's paired
HIDE-RECOVER Δ vs the same-run CTRL-35ch replica is > 0 (point) **and** Exp 2's SGMC-cal point
is below the Champion's 0.064121; Exp 3 then residual-allocates exactly 15% to `jx_quiescent`.
If Exp 2 already meets both, Exp 3 is skipped and Exp 2 is the final field. If Exp 2's HR point
≤ CTRL, Exp 3 instead fuses fields geometrically (OOF^0.7 × rank-normalised concordant^0.3) once.
No fourth experiment under any outcome.

**Controls (not counted as experiments, as in H45):** same-run CTRL-35ch HistGB replica,
Champion-recipe (D2.8 mask re-gated per-cell at visible B=2, the shared evaluator's
`b_visible_px=2` mode), and the static Champion file on SGMC.

## 3. Frozen promotion gates (fail-closed; all must pass for `verdict = promote`)

1. **Canary:** every input channel two-sided AUC ≤ 0.90.
2. **Holdout win:** pooled `HOLDOUT-DTI` (`GEMSDOE32-HIDE-RECOVER-v3.0`, 22,232 withheld
   positives) exceeds the repository best on the same evaluator, H38-G1 `0.116958
   [0.100533, 0.132040]` (`evidence/h38_run_card.json`), with a paired spatial-block bootstrap
   ΔCI vs the Champion recipe and vs CTRL whose lower bound is > 0 where paired draws exist.
   (H38's own bootstrap draws are not archived, so vs H38 only the point comparison is claimed.)
3. **No SGMC regression:** `GEMSDOE32-SGMC-CAL-v3.0` calibrated DTI ≥ Champion `0.064121`.
4. **Uniqueness:** pre-placement surface max |Spearman| ≤ 0.90 **and** final dots ≤ 70% within
   3 px vs every *genuine detector* registry raster (refreshed focus registry); the literal
   lattice number is reported and expected to fail for any dense map (IR-42-UNIQ-01) — if the
   literal rule is enforced with no exemption, the verdict is `negative` regardless, and this
   is stated, not silently exempted.
5. **Format:** saved-byte strict audit — single float32 band, EPSG:32611, 3730×3292, exact
   transform `(100,0,243350,0,−100,4508550)`, `nodata=None`, all 12,279,160 cells finite in
   [0,1], 0 NaN inside the footprint, 0 on-catalogue dots (`scripts/check_submission.py
   --strict-finite`). This is the automated fix for the portal error
   `Predicted values must be in range [0, 1]`: no float32 sentinel (−3.4028235e+38) and no
   NaN/nodata tag can reach the validator.
6. **Selector:** even a `promote` verdict does not spend a weekly slot; the separate selector
   decides within the cap on the submission page.

## 4. Score estimation — what will and will not be claimed

The brief asks for an estimated live score. Protocol Rule 3 forbids writing a projection as a
score, and this repo's own calibration (`docs/research/instrument-calibration.md`, n=12 scored
artifacts) measured the best local ranker (`drift_corrected_holdout_mean`) at Spearman ρ=+0.53,
**not significant** (p≈0.09), LOO MAE 0.053. The executive summary will therefore carry, for the
new file only, a clearly-labelled `MODEL` projection: a leave-one-out linear fit of
owner-reported live score on `drift_corrected_holdout_mean` from those 12 artifacts, applied to
the candidate's drift value, reported with its LOO residual spread as an interval and the
calibration's n/ρ/MAE printed next to it. If the interval includes values below 0.2778, the
summary will say so. Historical focus-site numbers in the table are `OWNER-REPORT`, never
`ORGANIZER-CONFIRMED`.

**Official sources for manual review:** [competition](https://www.drivendata.org/competitions/306/competition-doe-gems/) ·
[problem/metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
[about](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/) ·
[data (login)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) ·
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) ·
[rules PDF 96647](https://docs.nlr.gov/docs/fy26osti/96647.pdf) ·
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) ·
[GeoDAWN DOI 10.5066/P93LGLVQ](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) ·
[INGENIOUS](https://gbcge.org/current-projects/ingenious/) ·
[GDR 1391 DOI 10.15121/1881483](https://gdr.openei.org/submissions/1391) ·
[EPSG:32611](https://epsg.io/32611) · [Tversky index](https://en.wikipedia.org/wiki/Tversky_index) ·
[USGS FDSN](https://earthquake.usgs.gov/fdsnws/event/1/) · [USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
