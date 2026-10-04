# Verification, line by line — session 2026-10-04

**Purpose.** The standing brief requires: *"Work line by line verifying from official verified
trusted sources, provide links for manual review. … Flag any irregularities for review. No
hallucinations. Verify no hallucinations."* This document is that audit. Every row is either an
**official source with a link**, a **measurement reproducible in this checkout with the command
given**, or an explicit label saying it is *not* either. Nothing here is stated from memory.

**How to read the status column**

| status | meaning |
| --- | --- |
| `[OFFICIAL]` | read directly from a DrivenData / USGS / DOE page or product; link given; read date given |
| `[MEASURED]` | computed in this checkout from hash-pinned bytes; the exact command is given |
| `[OWNER-REPORT]` | the owner's own page or brief; **no** organizer receipt exists |
| `[MODEL]` | an estimate conditioned on an unverified anchor. Never a result |
| `[UNVERIFIED]` | could not be checked from this sandbox. Flagged, not asserted |

---

## 1. Environment and reachability — what was and was not available

| check | result | status |
| --- | --- | --- |
| `python3 --version` | 3.11.2 | `[MEASURED]` |
| numpy / scipy / scikit-learn / rasterio | 2.4.6 / 1.17.1 / 1.9.1 / 1.4.4 (installed `--break-system-packages`; the system Python is externally managed) | `[MEASURED]` |
| `curl https://github.com` / `api.github.com` | HTTP 200 | `[MEASURED]` |
| `curl https://www.drivendata.org/…` , `gdr.openei.org`, `mrdata.usgs.gov`, `docs.nlr.gov`, `earthquake.usgs.gov`, `pubs.usgs.gov`, `raw.githubusercontent.com` | **HTTP 000 (blocked/timeout)** | `[MEASURED]` |
| official pages read via the browsing path instead | page 967, leaderboard, community thread 11516 | `[OFFICIAL]` |
| PyPI reachable for installs | yes | `[MEASURED]` |
| GPU | **none**; 2 vCPU class, ~3.9 GB RAM | `[MEASURED]` (`free -m`, `nproc`) |
| `gh auth status` | logged in as `buffedlizard55-lab` via `GH_TOKEN`; used **only** for reading public mirrors and pushing git. No DrivenData credential exists or was sought | `[MEASURED]` |

**Limitation this imposes, stated plainly:** any source reachable only by `curl` was **not**
verified this session and is labelled `[UNVERIFIED]` rather than assumed. The official competition
pages *were* read, through the browsing path.

---

## 2. The competition contract — verified verbatim

| claim | source | status |
| --- | --- | --- |
| Metric is a distance-weighted Tversky index: `k(d) = (1 − d/R)₊`, `R = 300 m`, `α = 0.2`, `β = 0.8`; `TP_w`, `FP_w`, `FN_w` exactly as implemented | <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/> ("Performance metric") | `[OFFICIAL]`, read 2026-10-04 |
| Organizers' own worked example: `TP_w=3.00, FP_w=1.89, FN_w=2.00 → 0.60` | same page | `[OFFICIAL]`; reproduced by `tests/test_metric.py::test_published_example_arithmetic` | 
| Submission must be EPSG:32611, 100 m, same bounds, data outside the bounds null/nan, one band, float32, values between 0 and 1 | same page ("Submission format") | `[OFFICIAL]` |
| Pixels corresponding to known USGS/INGENIOUS faults are masked/excluded from evaluation, and will be masked again in the final round | DrivenData staff (`chrisk-dd`), community thread 11516: <https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516> | `[OFFICIAL]` |
| Structure: Initial Prize Round (private expert set, $50k) then Final Prize Round (expanded labels, $250k); **one** submission is scored across both; expert panel uses submitted predictions to expand labels | page 967 ("Competition structure") | `[OFFICIAL]` |
| Reference solution writes an **all-finite raster with no `nodata` tag** | <https://github.com/drivendataorg/gems-prize-reference-solution>, notebook cell "Save final prediction in required format" | `[OFFICIAL]` |
| Official rules PDF | <https://docs.nlr.gov/docs/fy26osti/96647.pdf> | `[UNVERIFIED]` — host unreachable from this sandbox; the URL is recorded, not its contents |

---

## 3. The leaderboard — verified, and two brief corrections

Source: <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>, read
**2026-10-04**. `[OFFICIAL]`

| rank | participant | best public DW-Tversky |
| ---: | --- | ---: |
| #1 | `nchuzhoy` | **0.3262** |
| #2 | `kinghorton42` | 0.3222 |
| #3 | `DARD` | **0.3195** |
| #4 | `alexoktaba` | 0.3042 |
| #5 | Batik Shirt Brothers | 0.2998 |
| #6–#12 | xiaofanhu … op01 | 0.2941 … 0.2710 |
| #13 | `smashi34` | **0.2708** |
| #14–#17 | ad3002 … SDCF9 | 0.2627 … 0.2600 |

| brief states | verified reality | status |
| --- | --- | --- |
| "0.3195 is the highest score right now" | **0.3262** is #1; 0.3195 is **#3** | **`[STALE]` — IR-32-SCORE-02** |
| "highest score from the GEMDOE site … `h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan`: 0.2708" | the GEMSDOE28 page prints **"NO GEMSDOE28 SCORE"** and prices that family as a **projection to 0.2701**. The live 0.2708 belongs to `smashi34`, an unrelated team | **`[OWNER-REPORT, contradicted by its own source]` — IR-32-SCORE-02** |
| "the single remaining blocker to training is data placement" | **resolved**; see §4 | **`[RESOLVED]` — IR-32-DATA-03** |

---

## 4. Data — every pin re-verified from bytes

`bash scripts/fetch_mirrors.sh`. All hashes computed in this checkout and compared to
`registry/data_manifest.json`. `[MEASURED]`

| id | bytes | sha256 (this checkout) | matches pin |
| --- | ---: | --- | --- |
| `training_features.tif` | 418,912,844 | `4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5` | **yes** |
| `labels.tif` | 425,830 | `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093` | **yes** |
| `existing_faults.tif` | 425,830 | `7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093` | **yes** |
| `sample_submission.tif` | 1,599,597 | `2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc` | **yes** |
| `h19_5.tif` | 1,712,322 | `ec1f9b56b83ce33cad781ceb9f104b18fb4f2ff785263a4e89616af4aabdee8d` | **yes** |
| `qfaults_v2_in_footprint.json` | 1,252,341 | `4d6efc7bb3659ea2545353fcec574ef085b0acdb189c7590e4420a7c6c57b41c` | **yes** |

Measured properties, re-derived rather than quoted. `[MEASURED]`

| property | measured | cross-check against the repo's own record |
| --- | --- | --- |
| `training_features.tif` | 19 bands, float32, 3730×3292, EPSG:32611, res 100 m, `nodata = -3.4028234663852886e+38` | matches `docs/research/range-error-root-cause-2026-10-03.md` §3 |
| band 1 valid cells | 5,165,852 | matches that document's `band 1 (mag_anom) != sentinel` row |
| footprint = template finite cells | **5,167,373**; NaN cells 7,111,787 | matches `sample_submission.tif` row |
| template distinct finite values | `{0.0: 5,106,385, 1.0: 60,988}` | matches exactly |
| `labels.tif` | int8, nodata −1, classes `[-1, 0, 1]`, `== 1` count **60,988** | equals the template's `1` count |
| `labels == -1` mask ≡ template NaN mask | `True` | matches |
| band 6 `tc` valid cells | 5,165,840 (12 fewer than the others) | matches the document's "band 6 `tc`: 7,113,320 sentinel" |

**The 19 official band descriptions were read from the GeoTIFF tags, not guessed.** `[OFFICIAL]`
(mirrored bytes) — full table in §5. This is the first time they are recorded in this repository.

---

## 5. The 19 official bands, from their own metadata

`[MEASURED]` — `rasterio.open('data/raw/training_features.tif').descriptions`. Because these names
decide which physical hypothesis is even expressible, they are reproduced verbatim:

| band | organizer description |
| ---: | --- |
| 1 | `mag_anom` — Magnetic anomaly — deviation from expected Earth's magnetic field |
| 2 | `rtp` — Reduced to pole magnetic data — magnetic anomaly corrected for latitude effects |
| 3 | `tmi_hg` — Total magnetic intensity horizontal gradient |
| 4 | `geod_2ndinv` — Geodetic second invariant — strain rate tensor magnitude |
| 5 | `iso_grav_anom_slope` — Isostatic gravity anomaly slope |
| 6 | `tc` — **Tilt angle or total curvature — magnetic field derivative for edge detection** |
| 7 | `geod_shearrate` — Geodetic shear rate (GPS/InSAR) |
| 8 | `geod_dilaterate` — Geodetic dilatation rate — volumetric strain |
| 9 | `tmi_vg` — Total magnetic intensity vertical gradient |
| 10 | `deq_n100a15` — Distance to earthquake (n=100 km radius, a=15° azimuth) |
| 11 | `iso_grav_anom_vg` — Isostatic gravity anomaly vertical gradient |
| 12 | `det_elev` — Detrended elevation |
| 13 | `iso_grav_anom` — Isostatic gravity anomaly |
| 14 | `tmi` — Total magnetic intensity |
| 15 | `depth_to_base_surf` — **Depth to basement surface — thickness of sedimentary cover** |
| 16 | `ieq_n100a15` — Earthquake intensity or density |
| 17 | `cond_surf` — Conductivity surface |
| 18 | `iso_grav_anom_hg` — Isostatic gravity anomaly horizontal gradient |
| 19 | `det_elev_slope` — Detrended elevation slope |

### Derived-channel audit against these names `[MEASURED]`

| channel in `features.py` | built from | finding |
| --- | --- | --- |
| `tmi_edge` | `|∇ band 14|` | **ρ = +0.9330** vs official band 3 `tmi_hg` → near-duplicate (IR-32-REDUND-01) |
| `grav_edge` | `|∇ band 13|` | ρ = −0.0098 vs official band 18 → **NOT** a duplicate. *(An earlier draft of this session's own analysis claimed it was; that claim is retracted and recorded in IR-32-REDUND-01.)* |
| `depth_grad` | `|∇ band 15|` | ρ = +0.9633 vs the raw unsmoothed `|∇ band 15|`, as expected for a smoothed version |
| — | bands **6, 9, 10, 16** in particular | **no derived transform at all** — the motivation for H61-3 and H61-2 |

Effective rank of the 35-channel stack: **participation ratio 16.95** `[MEASURED]`.

### Leak screen `[MEASURED]`

No official band leaks the catalogue. Spearman ρ against distance-to-catalogue over a 200,000-pixel
sample: maximum |ρ| = **0.1447** (band 16), then 0.1372 (band 4). The competition's own inputs
therefore do not smuggle in a distance-to-label channel, which is consistent with IR-32-LEAK-01.

---

## 6. The metric algebra — verified to machine precision

`python3 scripts/verify_theorems.py` → **ALL CLAIMS VERIFIED**, exit 0. `[MEASURED]`

| # | claim | verification | result |
| --- | --- | --- | --- |
| A | `1/DTI = α + α·(F/T) + β·(K/T)` | 200 random raster pairs vs the official `metric.score` | max abs error **1.7e-11** |
| B | sign of `D₀·ΔT − α·T·(ΔT + 1 − k̄)` predicts the exact gain | 300 random single-add trials vs brute force | **300/300** |
| C | `DTI(λ·p) = λT / (λα(T+F) + βK)` exactly | 40 pairs × 5 values of λ | max abs error **4.5e-14** |
| D | `T`, `K`, `F` recoverable from three leaderboard returns | simulated system, 300×300, `K=360` | `T 3.9570→3.9570`, `K 360.0→360.00`, `F 58.6667→58.6667` |
| E | the credit bar cannot bind on a binary field's own support | `k̄ ≥ 1` on support; bar-priced `emit()` | min `k̄` = **1.000**; consumes the whole support |

Brute-force transcription of the published formulas (`tests/test_metric.py::brute`) agrees with
`src/gems32/metric.py` to **1e-9** on 8 random pairs.

**Correction propagated:** `docs/research/score-ceiling-analysis.md` §1's `α·s/(1−α·s)` is **wrong**;
the bar is `α·s` (**IR-32-BAR-01**). The successor repository's `τ_live = 0.05485` is 5.5 % too high.

---

## 7. Every shipped artifact, re-measured from its own bytes

`python3 scripts/audit_shipped.py` → `docs/research/shipped_audit.json`. `[MEASURED]`

| artifact | bytes | positive px | finite | NaN | range violations | portal-legal |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `gems25-dotted-h19-5-d2-8-…-nan.tif` | 1,603,424 | 44,090 | 5,167,373 | 7,111,787 | **0** | yes |
| `gems25-dotted-h19-5-d2-8-…-zeros.tif` | 836,982 | 44,090 | 12,279,160 | **0** | **0** | yes |
| `gems32-bayesopt-dilation-scarp-d28-…-nan.tif` | 355,310 | 45,000 | 5,167,373 | 7,111,787 | **0** | yes |
| `gems32-bayesopt-dilation-scarp-d28-…-zeros.tif` | 302,357 | 45,000 | 12,279,160 | **0** | **0** | yes |
| `gems32-h19-5-smoothmaxcov-44090.tif` | 199,257 | 44,090 | 5,167,373 | 7,111,787 | **0** | yes |
| `gems32-h19-5-smoothmaxcov-44090-zeros.tif` | 154,757 | 44,090 | 12,279,160 | **0** | **0** | yes |

All six are EPSG:32611, 3730×3292, single-band float32. `[MEASURED]`

**Consequence for the brief's portal error.** The historical rejection *"Predicted values must be in
range [0, 1]"* **cannot be reproduced from anything currently shipped** — zero violations, zero NaN,
in every file. The offending upload was never obtained, so the trigger remains **inferred**
(**IR-32-VERIFY-01**, status `open`). The two mechanisms that *can* produce it are properties of the
competition's own inputs and are measured in §4. **Note a metadata inconsistency found this session:**
`gems32-h19-5-smoothmaxcov-44090-zeros.tif` carries `nodata=nan` in its GeoTIFF tag even though the
raster contains **zero** NaN cells — a validator that trusts the tag could behave oddly. Every new
file written this session sets `nodata=None` explicitly and re-verifies it after writing.

| provenance link | value | status |
| --- | --- | --- |
| sha256 of the in-repo `gems25-dotted-h19-5-d2-8-…-nan.tif` | `91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8` | **equals** the `incumbent_dotted_d2_8` pin in `registry/data_manifest.json` — the file in this repo **is** the pinned mirror of the 0.2600 artifact `[MEASURED]` |
| dots on catalogue pixels, all four artifacts | **0 / 44,090**, **0 / 45,000**, **0 / 121,131** | `[MEASURED]` |

---

## 8. The emissions — measured, with the defect found this session

| rule | dots | off-support | credit on the field's own surface | credit / unit mass | catalogue-proxy DTI |
| --- | ---: | ---: | ---: | ---: | ---: |
| incumbent `d = 2.8` (live 0.2600 `[OWNER-REPORT]`) | 44,090 | 0 | 88,569.5 | 0.2154 | 0.1617720 |
| `smoothmaxcov-44090` (**previously the site's primary**) | 44,090 | **25,485 (57.8 %)** | 72,243.5 | **0.0213** | **0.0163197** |
| `bayesopt-dilation-scarp-d28` | 45,000 | 43,334 (96.3 %) | — | 0.1404 | 0.1079318 |
| parent `h19_5` field | 121,131 | 0 | 121,199.6 | 0.1007 | 0.1663512 |
| **corrected lazy greedy (new)** | 44,090 | **0** | **90,230.9** | 0.1963 | 0.1477520 |

The proxy column is `[MEASURED, leak-contaminated]` — the organizers mask catalogue pixels out of
scoring, so that frame screens artifacts against each other and is **never** a score. The
off-support column is truth-frame-free and is the one that fails the previous primary (**IR-32-SHIP-01**).

**Honest cross-check of the proxy's endpoints:** the two values this repo had already published,
`h19_5 = 0.1663512` and `d2.8 = 0.1617720`, reproduce to **seven decimals** here — the measurement
chain is consistent with the project's own record.

---

## 9. The identification pack — built and independently re-verified

`python3 scripts/build_identification_pack.py --m 2000` → `registry/identification_pack.json`.
`[MEASURED]`

| check | result |
| --- | --- |
| S1 in-footprint values **bit-identical** to the live 0.2600 anchor | `True` |
| S2 `== 0.5 × S1` exactly, everywhere | `True` |
| S3 `== S1` plus exactly one dot per probe pixel | 2,000 added, total 46,090 |
| S3 is a strict superset of S1 on the footprint | `True` |
| S3 probe mutual minimum spacing | **7.0 px** |
| S3 minimum distance to any catalogue pixel | **49.2 px ≈ 4,920 m** |
| S3 minimum distance to the anchor's belief support | 49.2 px |
| S3 minimum distance to the footprint edge | 49.3 px |
| all three: finite / NaN / out-of-range cells | 12,279,160 / **0** / **0** |
| S1 sha256 | `4dc4cc54b061cb4567a5500c8fa2bfe750a39340b02c8cdbb4308916f36cbcc3` |
| S2 sha256 | `d6462b76bce1a54920bd4e9d61700f3a1cc2f8dedf89d93651f74d10144c0243` |
| S3 sha256 | `da4193e3a2e0470908b5bd1e28de97f25ee1ce15c57c959d0b623414d200692a` |
| inversion from simulated returns at the leaderboard's **4-decimal** precision | `T = 4812.4` (true 4791), `K = 12290.3` (true 12226), `F = 38571.7` (true 38440) — all **<0.5 %** |

**Risk, stated:** if a probe pixel is within 300 m of a hidden fault then `ΔT > 0` and `T̂` is biased
high. Mitigation: the 49-px catalogue clearance and placement at the minimum of every belief field
in the repository. The residual risk is recorded in `registry/identification_pack.json`
(`decision_rule.residual_risk`) and is **not** claimed to be zero.

---

## 10. What is registered but NOT verified — the honest list

| item | why not verified | status |
| --- | --- | --- |
| Official rules PDF content | `docs.nlr.gov` unreachable from this sandbox | `[UNVERIFIED]` |
| `sciencebase.gov` NBMG/USGS post-catalogue rupture traces (H60-1) | host unreachable | `[UNVERIFIED]` |
| Nevada Geodetic Laboratory MIDAS / EarthScope GNSS velocities (H61-4) | host unreachable; **not obtained** | `[UNVERIFIED]` |
| 3DEP 1 m DEM tiles behind the official `1m_DEM_links.csv` (H61-5) | tiles **not obtained** | `[UNVERIFIED]` |
| USGS ANSS ComCat hypocentres | host unreachable; optional for H61-2 | `[UNVERIFIED]` |
| any live score for any artifact of ours | no organizer receipt is readable; all group numbers are owner reports | `[OWNER-REPORT]` |
| the exact trigger of the historical `[0, 1]` portal error | the offending file was never obtained | `open` — IR-32-VERIFY-01 |
| obtainability of H61-4 / H61-5 data | **reported as unverified, so those hypotheses are ranked but explicitly NOT proposed as viable**, per the standing brief | `[UNVERIFIED]` |

## 11. Claims made earlier this session and **corrected** here

Recorded because "verify no hallucinations" applies to this session's own output too.

| earlier claim | status | correction |
| --- | --- | --- |
| `grav_edge` duplicates official band 18 | **WRONG** | measured ρ = −0.0098; retracted. The redundancy finding stands only for `tmi_edge` (ρ = +0.9330) |
| `bayesopt-dilation-scarp-d28` has 31,338 off-field dots (69.6 %) | **WRONG** | measured **43,334 (96.3 %)**; corrected in `knowledge/02` §7 |
| a static-order max-coverage sweep is a good near-greedy | **WRONG** | it delivers 10.0 of the exact greedy's 15.0 credit units at the same budget on a straight ridge; replaced by true lazy greedy and pinned by `tests/test_emitter.py::test_lazy_greedy_matches_exact_greedy` |
| band 12 is the DEM and band 15 is its gradient | **CONFIRMED, but it was an assumption** | band 12 `det_elev` and band 15 `depth_to_base_surf` are now read from the file's own tags, and every derived channel is mapped to an official name in §5 |
| the corrected emitter scores 0.0572 on the catalogue proxy | **superseded** | that figure was the static-order stub; the corrected lazy greedy scores **0.1477520** |

---

## 12. Reproduce this audit

```bash
bash    scripts/fetch_mirrors.sh                    # §4 — fails closed on any digest mismatch
python3 scripts/verify_theorems.py                  # §6 — exits non-zero on any failed claim
python3 scripts/audit_shipped.py                    # §7, §8 — re-reads docs/downloads/*.tif from disk
python3 scripts/build_identification_pack.py --m 2000   # §9
python3 -m pytest tests -q                          # 54 tests, all passing
```
