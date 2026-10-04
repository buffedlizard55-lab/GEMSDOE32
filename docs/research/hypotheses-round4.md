# Round-4 candidate geological hypotheses (H33-1 … H33-5)

**Session:** GEMSDOE32, 2026-10-04 · **Author:** autonomous agent · **Status:** **round complete,
shipped UNSCORED.** The winning arm is a **removal** arm (catalogue-flank buffer B = 2 on the
0.2708 base), not any of the addition hypotheses below. The two flagship addition arms — H33-1 (GDR
measured geothermometry) and H33-5 (detector-field tip/step-over) — are **falsified as addition arms**
and reported as such. See §2.3 and §2.4.

Every layer name below is the **organiser's own band description**, read from `training_features.tif`
band tags and recorded in `registry/sources.json`, or the exact column name of an official GDR 1391
table. Nothing is inferred.

---

## 0. What was audited before proposing anything

| source | what it established |
| --- | --- |
| `src/gems32/hypotheses.py`, `features.py` | H32-A…D and the 35-channel stack already in this repo |
| 16GEMSDOE `docs/research/hypothesis_register.md` | its rank-3 hypothesis **H18-5 "thermal-anchor linking"** proposed the GDR spring/well/sinter/volcanic prior and recorded its status verbatim as **"Premise measured; operator not built"** |
| GEMSDOE28 `docs/downloads/manifest.json` | the group's best live-scored artifact (`8acb75e1f2cc`, owner-reported **0.2708**) and every digest used to pin it |
| `registry/data_manifest.json` | **no GEMSDOE27/28 artifact was present at all** before this session, so the repository could not reproduce — let alone improve on — its own best live score (IR-33-DATA-01) |

Consequence: the H18-5 thermal-anchor operator is **genuinely unbuilt across the whole group**, and
the 0.2708 emission was **not reproducible from this checkout**. Both are fixed here.

---

## 1. The five candidates, ranked

Rank is by expected DTI improvement first and implementation cost second. "Data on disk" means the
raster is already sha256-pinned in `registry/data_manifest.json`.

| rank | id | layers / data | physical signature | why it finds a fault the catalogue lacks | differs from | cost |
| ---: | --- | --- | --- | --- | --- | --- |
| **1** | **H33-2** catalogue-flank exclusion sweep | `existing_faults.tif` (byte-identical to `labels.tif`), the 0.2708 emission | delete every dot with `d(catalogue) ≤ B` px, B ∈ {1,2,3} | it finds nothing — it *stops paying* for mass the scorer masks out. This is the only axis with a **measured live gain** (+0.0108 at B = 1) | the group ran the blind r = 1 prune **once**, live, and never swept B | trivial |
| **2** | **H33-1** GDR measured-geothermometer upflow conduit | GDR 1391 `spring_chemistry_20220808`: `geothermquartz_c`, `geothermchalc_c`, `geothermcat_c`, `temp_c`, `dist_known_fault_px` × bands 12 `det_elev`, 3 `tmi_hg`, 15 `depth_to_base_surf` | IDW surface (L = 20 px, k = 8, σ = 3) of the **per-site maximum of three independent reservoir-temperature estimators**, conjoined with a label-free lineament score `S = z(T)·(0.45 + 0.55·z(L))`, emitted as a 4-direction NMS crest | a reservoir > 150 °C implies a magmatic/deep-circulating heat source; the fluid reaches the surface along a permeable fault whose trace need not have a scarp. **184 geothermometer sites in the footprint, 53 above 150 °C, 15 of them more than 3 km from any catalogued fault** — those 15 must be fed by something unmapped | H18-5 proposed it and built nothing; GEMSDOE28's H38-1 used a *modelled conductive heat-flow residual* (DeAngelo et al. 2022), not **measured spring chemistry** | low (~40 s) |
| **3** | **H33-5** detector-field tip / step-over corridor | `h19_5`, `h19_4`, `h16_1` (the group's own corroborated ridge surfaces) | morphological close, then 8-neighbour endpoints (1 neighbour) and junctions (≥ 3); Gaussian density × corroboration count, emitted off-catalogue | Great Basin geothermal systems concentrate at fault terminations and relay ramps (Faulds & Hinz 2015; Siler et al. 2019). Sourcing the tips from the **detector's own field** rather than the catalogue lets the prior point off-catalogue | 16GEMSDOE's H18-3a sourced endpoints/junctions from `labels.tif` — a km-scale prior that cannot point where the catalogue does not | low (~20 s) |
| **4** | **H33-3** 2 m temperature-probe thermal lineaments | **needs new data**: GDR 1391 `2m Temperature Probes.zip` | shallow 2 m thermal anomaly; the elongated axis of the anomaly is a lineament | a 2 m anomaly is the most direct surface expression of an upflow; metre-scale probes resolve what a 100 m grid cannot | no group repo has used the 2 m probe layer | low once obtained |
| **5** | **H33-4** paleogeothermal sinter / tufa conduit | **needs new data**: GDR 1391 `Paleo Geothermal Features.zip` | mapped sinter and tufa deposits mark *past* upflow; the now-active conduit is typically blind | a paleo system's active trace is the canonical "fault missing from the catalogue" | proposed in 16GEMSDOE, never built | low once obtained |

### H33-3 / H33-4 data-obtainability check (required by the brief)

Both need rasters that are **not** in `data/raw`. The specific free, official source is named and its
obtainability was checked by reading the official resource page:

| resource | official URL | published size | licence | obtainable? |
| --- | --- | --- | --- | --- |
| 2 m Temperature Probes.zip | <https://gdr.openei.org/files/1391/2m_temperature_probe_INGENIOUS_regional_data.zip> | 1.03 MB | CC BY 4.0 | **listed and readable on the official GDR 1391 page** (DOI 10.15121/1881483). Not fetchable from this sandbox — `gdr.openei.org` is blocked by the sandbox egress policy; 16GEMSDOE's `evidence/ci/external_verification.json` records successful GDR downloads from a GitHub-hosted runner |
| Paleo Geothermal Features.zip | <https://gdr.openei.org/files/1391/paleo_geothermal_regional.zip> | 82.04 kB | CC BY 4.0 | same |

They are therefore **ranked and named, not proposed as ready**, exactly as the brief requires.
`src/gems32/hypotheses33.py::missing_external_inputs()` reports their presence at runtime so the
claim cannot silently go stale.

---

## 2. Validation of the top candidate

### 2.1 The instrument problem, stated before any result

The repository's own catalogue holdout **cannot rank live**: its truth *is* the catalogue, and the
organisers mask catalogue pixels out of scoring. Measured in this checkout
(`data/holdout_surrogate_log.json`), the co-kriging drift model predicts **0.2225** for the group's
live **0.2708** file — a **−0.0483** error, the worst in the set, and the wrong *sign* on the
D2.8 → 0.2708 contrast. It was −0.0424 (0.2284) before the 13 GEMSDOE27/28 group artifacts were
added to the slot log: **adding live-scored data made the honest model worse**, which is registered
as IR-33-DRIFT-01 and is exactly the surrogate-vs-leaderboard gap the standing brief says to chase.

So a new instrument was built and **validated before use**:

> **LM** — the exact official distance-weighted Tversky index, evaluated on the four spatially
> blocked quadrants, against a truth set that is off-catalogue *by construction*: the USGS State
> Geologic Map Compilation fault pixels lying more than 300 m from every catalogue pixel inside the
> eroded test domain (62,703 px). Because the truth excludes the catalogue, mass spent on the
> catalogue and its flank is charged α and earns nothing — exactly what the live scorer does.

LM was scored against **six known live orderings**. Prevalence-calibrated LM (`|G| = 12,691 px`
scaled per fold) reproduces **3/6**, and they are the three that matter for the current operating
point:

| ordering | live | LM-calibrated | margin |
| --- | --- | --- | --- |
| H27-4-R1-SOLO > D2.8 | 0.2708 > 0.2600 | 0.263051 vs 0.251593 | **+0.011458** |
| D2.8 > D1.5 | 0.2600 > 0.2477 | 0.251593 vs 0.248393 | +0.003200 |
| LATTICE-S5 > PLACEHOLDER | 0.0904 > 0.0445 | 0.436622 vs 0.097651 | +0.338952 |

The first row is the important one: **LM recovers +0.011458 where the live record shows +0.0108** —
a 6 % agreement from an instrument that has never seen a leaderboard score. It fails on dense
emissions (> 120 k dots), where the dense SGMC truth rewards spraying mass; that failure is recorded
as the instrument's validity domain, not hidden.

### 2.2 The live-anchored decision rule

The D2.8 → 0.2708 pair is a controlled natural experiment: the two emissions differ by exactly one
mechanism (3,891 dots at `d(catalogue) = 1` px deleted). Inverting
`DTI = S / (0.2·n_p + 0.8·G + 0.8(TP_g − TP_p))` under the zero-credit-loss assumption gives

* `TP_w = 5,073.3`, `D = 18,734.4`, mean credit per dot **0.1262**, implied weighted recall
  **0.4150** at `|G| = 12,226`;
* the B = 1 removal could have absorbed **210.7** units of weighted credit and still gained.

That yields the running rule the brief asks for — *for a proposed removal of `dn` dots costing
`dS` weighted credit, the gain condition is `dS < TP_w·(0.2·dn − 0.8(dS − dTP_g))/D`* — and a
**safety factor** = budget / measured cost.

### 2.3 Measured result (all numbers from `evidence/h33_validation.json`)

| candidate | dots | LM-cal | LM margin | folds | safety | projected live | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **H33-2-B2** (flank B = 2 on the 0.2708 base) | **37,654** | **0.267921** | **+0.004870** | **4/4** | **2.08** | **0.2747** | **SLOT-ELIGIBLE** |
| H33-2B2 + H33-1 | 38,554 | 0.268029 | +0.004978 | 4/4 | 2.08 | 0.2746 | SLOT-ELIGIBLE |
| H33-1 P600 A1800 | 41,999 | 0.265690 | +0.002639 | 2/4 | — | — | rejected (folds, credit/dot 0.00541 < τ) |
| H33-5 P300 A900 | 41,099 | 0.264921 | +0.001870 | 3/4 | — | — | rejected (folds, credit/dot 0.00767 < τ) |
| H33-2-B3 | 35,483 | 0.264368 | +0.001317 | 3/4 | 1.27 | 0.2738 | rejected (safety < 2.0) |
| H33-1 P300 A900 | 41,099 | 0.263575 | +0.000524 | 2/4 | — | — | rejected |
| BASE 0.2708 | 40,199 | 0.263051 | 0 | — | — | 0.2708 | base |
| D2.8 0.2600 | 44,090 | 0.251593 | −0.011458 | 0/4 | — | — | reference |

**The headline is a negative one, and it is reported as such:** all three *addition* arms —
including the flagship H33-1 GDR geothermometer conduit — earn **0.0022–0.0077 credit per added dot**
against a live break-even bar of **τ = α·DTI = 0.2 × 0.2708 = 0.05416**. They are 7–25× too
expensive. The measured far-field credit per dot at this operating point is simply not enough to pay
for new mass, which is the same conclusion GEMSDOE28 reached for H35-1 and which only its H38-1 arm
has ever beaten.

**What did work** is a one-step extrapolation of the single live-validated mechanism: extending the
catalogue-flank exclusion from B = 1 to B = 2 removes 2,545 more dots (6.3 % of the mass) for 58.6
units of weighted credit against off-catalogue truth (1.5 %), against a budget of 125.1 — a
**2.08× safety factor**, projected live **0.2747**.

### 2.4 The drift finding (IR-33-LM-01)

LM-calibrated, used outside its validated regime, ranks a 7,943-dot "safe-mass-pruned" variant of
the 0.2708 emission at **0.4413** — 1.35× the entire leaderboard's top score. That variant is
constructed to be TP-neutral against off-catalogue truth (every deleted dot earns zero TP_p credit
and is the unique nearest dot of no truth pixel), so the instrument is telling us 80 % of the
group's best emission is pure waste. **The live record refutes this**: the same emission scores
0.2708.

Quantified: if the removal really were TP-neutral live, the score would be 0.4130. For the pruned
file not to exceed the current leader (0.3262), at least **16 % of the 0.2708 emission's weighted
credit** must sit on dots that SGMC off-catalogue truth calls credit-neutral and redundant. The
SGMC geologic-map fault population therefore covers only part of the live hidden truth, and
**LM-cal is only licensed for small, mechanism-matched perturbations** — which is why the slot gate
also requires a live-anchored safety factor and not just an LM margin.

---

## 3. What is shipped

| file | dots | role |
| --- | ---: | --- |
| file | dots | role |
| --- | ---: | --- |
| `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 37,654 | **primary** — all-finite, no nodata, values in [0,1] |
| `…-e5eb6e7e-zeros.zip` | 37,654 | the primary in the portal's other accepted container (one GeoTIFF inside) |
| `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-nan.tif` | 37,654 | NaN-outside twin (the competition's own format) |
| `gemsdoe32-h33-h33-2b2-plus-h33-1-20261004T220000Z-31588dc7-{zeros,nan}.tif` | 38,554 | secondary — flank B = 2 plus 900 GDR thermal-conduit dots |

Both are **UNSCORED**. No organizer score exists for any artifact in this repository.
`scripts/audit_shipped.py` re-opens every file on disk and reports **portal-illegal artifacts: none**.

### 3.1 The load-bearing claim, re-verified from the rasters themselves

The claim that the 0.2600 → 0.2708 step is a *pure* catalogue-flank prune is the foundation of the
live-anchored inversion, so it was re-checked pixel-exactly against the two published rasters rather
than taken from the group's own notes:

```
D2.8  (gems24-h25-1-dotted-h19-5-d2-8-…-e56ea318af89-nan.tif)   44,090 dots
0.2708 (gems28-h27-4-r1-solo-d2-8-…-8acb75e1f2cc-allfinite.tif)  40,199 dots
D2.8 dots within 1 px (100 m) of existing_faults.tif              3,891
D2.8 dots within 2 px (200 m)                                    6,436
D2.8 dots within 3 px (300 m)                                    8,607
(D2.8 AND dist>1) == 0.2708 file, pixel-exact                 True   (0 discrepancies either way)
existing_faults.tif sha256 == labels.tif sha256                  True  (7ba308ccdc…)
```

So the 0.2708 record is exactly the D2.8 emission with its 3,891 catalogue-adjacent dots deleted and
nothing else changed — a single-mechanism controlled experiment supplied by the live record, for
free.

---

## 4. Irregularities raised this round

| id | severity | what |
| --- | --- | --- |
| IR-33-DATA-01 | high | before this session **no GEMSDOE27/28 artifact was present in this checkout at all**, so the repository could not reproduce — let alone improve on — its own best live score. Fixed: 16 owner-mirror rasters fetched via the GitHub API, sha256-pinned in `registry/data_manifest.json` (38 files), `scripts/fetch_mirrors.sh` re-run **38/38 PASS**. They are owner mirrors, **not** organiser upload receipts. |
| IR-33-DUP-01 | medium | the legacy leaderboard row `GEMS27-TGC-v2-on-D1.5` carried **0.2392** while the corrected record for the same artifact carries **0.2449**. The legacy row is now suffixed `-DUPLICATE-REMOVED` and skipped in `scripts/run_pipeline.py`. **Root cause unresolved**: both numbers are owner reports. |
| IR-33-DRIFT-01 | medium | adding the 13 group artifacts moved the co-kriging drift-corrected Spearman/Pearson from >0.80/>0.92 to **0.697/0.835**, and the 0.2708 anchor is still under-predicted by −0.0483. |
| IR-33-LM-01 | high | outside its validated regime LM-cal ranks a 7,943-dot pruned variant at **0.4413**; the live record refutes it (see §2.4). |
| IR-34-ROOT-01 | high | GitHub Pages publishes the repository **root**, so the root landing page's one-click download buttons (`downloads/…`, resolved from the root) 404'd, and three further root pages still headlined the superseded H32-D primary. Fixed in `scripts/build_site.py` (prefix-aware `download_block`, all ten root pages regenerated as canonical redirects); `tests/test_site.py` re-reads the bytes and fails on any link that is not on disk. |
