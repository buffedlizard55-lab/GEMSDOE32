# Round-2 candidate hypotheses — five things we have not tried, ranked

**Date:** 2026-10-04 · **Supersedes the ranking in** `registry/hypotheses.json` (H60-1…H60-5 are kept
and re-ranked below) · **Machine-readable:** `registry/hypotheses.json`

The brief asks for **3–5 candidate geological hypotheses we have not tried yet**, each naming *the
specific layer(s) involved*, *the physical signature being targeted*, *why it should catch a fault
missing from the USGS/INGENIOUS catalogue rather than one already in it*, and *how it differs from
anything already implemented in this repo*, ranked by **expected DTI improvement against
implementation cost**, with the top candidate validated on the spatially-blocked holdout before any
weekly slot is touched.

Every layer name below is the **organizer's own band description**, read from the GeoTIFF tags of
`training_features.tif` rather than inferred. Table and provenance:
`registry/sources.json`, and the measured band table in `docs/research/verification-2026-10-04.md`.

---

## 0. The measured facts that constrain every hypothesis

These four measurements decide which hypotheses can possibly matter. They are established in
`knowledge/02_the_ceiling_and_the_instrument.md`; nothing below is worth proposing that contradicts
them.

1. **The metric rewards coverage of the hidden faults and nothing else, subject to wasted mass.**
   `1/DTI = 0.2 + 0.2·(F/T) + 0.8·(K/T)` — verified to 1e-15. The leaderboard ranks `T/(0.2F+0.8K)`.
   `K` is common to every submission, so **a hypothesis matters iff it raises `T` (weighted credit
   on *hidden* faults) without raising `F` proportionally**.
2. **A dot pays for itself iff its incremental credit exceeds `0.2·DTI`** — `0.052` at DTI 0.26,
   i.e. it must land within **≈ 284 m of a hidden fault**. Verified 300/300 against the official
   implementation. So "a bit near a fault" is worth almost all of the credit; "definitely a fault"
   is worth nothing extra.
3. **Every locally measurable truth raster is the visible catalogue, and the organizers mask
   catalogue pixels out of scoring** (staff, thread 11516). Therefore **no local holdout can reward
   a genuinely new fault.** A local win is a *screen*, never evidence. This is the single most
   important constraint on hypothesis design: a hypothesis whose value is only demonstrable on the
   catalogue is worthless.
4. **The live ladder is monotone in emission mass while the catalogue proxy is anti-monotone**
   (121,131 px → 0.1922 live / 0.16635 proxy; 60,069 → 0.2477 / 0.17193; 44,090 → 0.2600 /
   0.16177). So the emission budget cannot be chosen locally, and the hidden-set recall has never
   been measured.

**Design consequence.** A hypothesis earns a high rank here only if it (a) added or removed mass
*where the current field is wrong*, rather than re-shaping mass the field already places, and (b)
has a mechanism whose target population is **by construction absent from a surface catalogue**.
Re-shaping is what the group has spent most of its arms on (NMS, ridge thinning, gap closure,
rung re-packing, flank pruning), and the live ladder shows the returns are now small: the marginal
step from 60,069 to 44,090 px bought +0.0123, whereas 121,131 → 60,069 bought +0.0555.

---

## H61-1 — Basement-step lineaments gated by surface quiescence

| | |
| --- | --- |
| **layers** | `depth_to_base_surf` ("Depth to basement surface — thickness of sedimentary cover"), `det_elev_slope`, `det_elev`, `iso_grav_anom` + `iso_grav_anom_hg` / `_vg` / `_slope` |
| **signature** | **Multi-scale ridge extraction on ‖∇(cover thickness)‖.** A fault-block boundary juxtaposes two different cover thicknesses, so it is a *step* in `depth_to_base_surf`; the boundary is therefore the **crest line of the gradient field**, extracted as a ridge (Sato/Frangi-style Hessian ridge at 3 scales) and then skeletonised — not the gradient blob. **Gate:** promote a ridge pixel only where surface expression is *low* (small `det_elev_slope`, small surface curvature). |
| **why off-catalogue** | A Quaternary surface-fault catalogue records what is *exposed*. A block boundary under thick basin fill has no surface trace to map, so it cannot be in a surface catalogue — while the basement step is exactly what `depth_to_base_surf` measures. The **quiescence gate is the discriminator**: it removes precisely the population the catalogue already contains (faults with scarps) and keeps the population it structurally cannot contain. |
| **differs from this repo** | `src/gems32/features.py` contains only `depth_grad = smoothed ‖∇ band15‖` — a first-derivative *magnitude*. It never (a) extracts the gradient's **ridge line**, (b) uses the cover-thickness *value* as a concealment weight, (c) applies a surface-quiescence gate, or (d) works at more than one scale. The repo's separate "concealment prior" idea (H-34-01 in a sibling repository) used SGMC map-unit polygons, not the **official cover-thickness raster**, which is a direct physical measurement rather than a lithology proxy. |
| **expected DTI** | highest of the five: it is the only hypothesis here that changes **where** mass goes rather than how it is packed |
| **cost** | **low** — one official band, already on disk and hash-verified; no new data |
| **falsified by** | the blocked holdout showing no improvement over the same-mass control with the gate on vs gate off; or the gate populated only in already-covered areas |

**Honest risk.** Concealed faults may be *under-represented* in the hidden set if the expert panel
mapped primarily from surface expression. That is a real, testable bet, and `IR-32-PROXY-01`
already records the complementary risk.

---

## H61-2 — Seismicity lineament coupling

| | |
| --- | --- |
| **layers** | `ieq_n100a15` ("Earthquake intensity or density"), `deq_n100a15` ("Distance to earthquake"), corroborated by `det_elev` and `det_elev_slope` |
| **signature** | The seismicity fields are supplied as **2-D scalars**. Extract their **anisotropic ridge/coherence maxima** (structure tensor → coherence + orientation, then non-maximum suppression along the minor axis at two scales) rather than thresholding them, and require a coincident **curvature inflection** in the detrended surface. A line of relocated hypocentres is a fault plane; a density blob is not. |
| **why off-catalogue** | Instrumental seismicity is a **dynamic** inventory. Faults that are blind, that are creeping, or whose slip rate is too low to have preserved a Quaternary scarp still rupture small earthquakes; a geomorphic catalogue records only the last of those three. This is a different *physical* population, not a different transform of the same one. |
| **differs from this repo** | `features.py` carries bands 10 and 16 **only as raw columns**; no derived channel uses them, no registry arm uses seismicity, and the two bands have no ridge, coherence or orientation transform anywhere in the tree. |
| **expected DTI** | second: moderate coverage gain concentrated in the basin-interior areas the field currently under-serves |
| **cost** | **low** — bands already on disk; the free USGS **ANSS Comprehensive Earthquake Catalog (ComCat)** API would add hypocentral *depths* for 3-D plane fitting, but the hypothesis is testable without it |
| **falsified by** | ridge pixels landing on already-covered trace, i.e. no change to `T` at matched mass |

---

## H61-3 — Tilt-angle (TDR) zero-crossing magnetic edge lineaments

| | |
| --- | --- |
| **layers** | `tc` ("Tilt angle or total curvature — magnetic field derivative **for edge detection**"), `tmi_vg`, `tmi_hg`, `rtp`, `tmi` |
| **signature** | The **zero-crossing contour of the tilt angle** rather than its magnitude. The tilt-angle derivative is the standard *depth-independent* locator for a magnetic contact: its zero contour sits over the contact regardless of source depth, whereas the magnitude peaks wander with depth. Pair it with `tmi_vg` (vertical gradient) as an independent witness and reject where the two disagree. |
| **why off-catalogue** | TDR edges respond to **subsurface** magnetisation contrasts irrespective of exposure. A magnetisation boundary can be a fault contact under cover, or a fault whose surface trace is obscured — both invisible to a surface catalogue. |
| **differs from this repo** | `features.py` derives `tmi_edge = ‖∇ band14‖` and `rtp_edge = ‖∇ band2‖` but **never touches band 6 or band 9**. Band 6 is the layer the organizers themselves describe as being *for edge detection*, and it has **no derived channel** in this repo at all. Measured redundancy note: `tmi_edge` correlates with official band 3 at **ρ = +0.9330** (IR-32-REDUND-01), so the repo is currently spending a channel to recompute a supplied layer while leaving the purpose-built edge layer unused. |
| **expected DTI** | third: strongest in the magnetics-covered north, weak elsewhere |
| **cost** | **low** — bands already on disk |
| **falsified by** | the zero-contour producing a dense network with no coincidence with any structural band (a known failure mode of TDR in low-latitude / noisy data) |

---

## H61-4 — GNSS-derived full 2-D strain tensor → principal-axis anisotropic matched filter

| | |
| --- | --- |
| **layers** | *Official bands are insufficient*: `geod_2ndinv`, `geod_shearrate`, `geod_dilaterate` are **three scalars of a tensor** — the second invariant, the shear rate and the dilatation rate. A tensor's **orientation is not recoverable** from its invariants. |
| **external source** | Free and official, **named as the brief requires**: the **Nevada Geodetic Laboratory MIDAS** velocity field (<http://geodesy.unr.edu/>) and/or the **EarthScope / UNAVCO** GNSS velocity products (<https://www.unavco.org/>). |
| **signature** | Reconstruct the full 2-D strain-rate tensor from the GNSS velocity field, take its **principal extensional axis**, and use that azimuth as the orientation prior of an **oriented matched filter**: a fault strikes approximately perpendicular to σ₃, so the filter is tuned per pixel rather than isotropically. |
| **why off-catalogue** | Orientation is what predicts *which way* a missing fault must run. With an azimuth prior you can search for evidence of a fault at the mechanically favoured strike even where the topographic expression is ambiguous — the class of fault that gets omitted from hand-mapped catalogues. |
| **differs from this repo** | No arm in this repo uses the orientation of the supplied geodetic tensor, because it is not available in the supplied data. |
| **expected DTI** | fourth: it *sharpens* rather than *extends*, which the live ladder says is still worth doing, but the coverage gain is indirect |
| **cost** | **medium** |
| **⚠ obtainability not verified** | This source **was not reachable from this sandbox**, and per the brief a candidate needing external data must have its source **checked as obtainable before being proposed as viable**. It is therefore **ranked and registered, and explicitly NOT proposed as ready to run.** |

---

## H61-5 — Metre-scale scarp matched filter from the official 1 m DEM link table

| | |
| --- | --- |
| **layers** | *external:* the 1 m / 10 m 3DEP DEM tiles listed in the official `1m_DEM_links.csv`, plus `det_elev`/`det_elev_slope` for context |
| **signature** | An **anisotropic matched filter for metre-scale scarps** — a fault with < 1 m of throw averaged over a 100 m cell is invisible in the provided grid by construction. |
| **why off-catalogue** | Below-grid-resolution scarps are precisely the class a 1:24,000-scale surface compilation omits. |
| **differs from this repo** | The repo has **no LiDAR arm at all**. H60-5 (chi/knickpoint residuals) is registered but was never run; this variant is a matched filter on the scarp itself, which is a different and cheaper measurement. |
| **expected DTI** | fifth by cost-effectiveness: the physics is sound but the tile fetch and hydrology are heavy on 2 vCPU |
| **cost** | **high** |
| **⚠ obtainability not verified** | As H61-4. Registered, ranked, **not proposed as ready**. |

---

## Ranking

| rank | id | hypothesis | layers | expected gain | cost | new data? |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | **H61-1** | Basement-step lineaments, quiescence-gated | `depth_to_base_surf`, `det_elev_slope`, `det_elev`, `iso_grav_anom*` | high | **low** | **no** |
| 2 | **H61-2** | Seismicity lineament coupling | `ieq_n100a15`, `deq_n100a15`, `det_elev*` | moderate | **low** | no (ComCat optional) |
| 3 | **H61-3** | Tilt-angle zero-crossing edges | `tc`, `tmi_vg`, `tmi_hg`, `rtp`, `tmi` | moderate | **low** | no |
| 4 | H61-4 | GNSS strain tensor → orientation prior | geodetic invariants + **NGNL MIDAS / EarthScope GNSS** | indirect | medium | **yes — unverified** |
| 5 | H61-5 | Metre-scale scarp matched filter | **official `1m_DEM_links.csv` 3DEP tiles** | indirect | high | **yes — unverified** |
| — | H60-1 | Post-catalogue coseismic ruptures (carried forward) | NBMG/USGS rupture traces | high on the **final** round | low | yes — `sciencebase.gov`, unverified |

## Validation status — stated plainly

**The top candidate (H61-1) has not been promoted, and no weekly slot is requested for it.** The
preregistered, spatially blocked holdout (`GEMSDOE32-PREREG-2`, 4 quadrant blocks, 30 px buffer,
matched-mass control, `registry/preregistration.json`) is the gate, and it is the *same* instrument
that already returns the **opposite** answer to the live leaderboard on emission questions — which
is exactly why it is a screen and not a verdict.

The reason this document does not end with a promoted candidate is not caution for its own sake. It
is the measurement in §0.3: **no local truth raster in this competition can reward a genuinely new
fault, and the team's hidden-set recall has never been measured.** Spending a slot on H61-1 before
that measurement exists would be spending it blind. The three-slot identification pack
(`knowledge/02_the_ceiling_and_the_instrument.md` §6, `registry/identification_pack.json`) is what
converts the next H61-1 evaluation from a guess into an experiment with a known denominator — and
it is the sequence this project should run first.
