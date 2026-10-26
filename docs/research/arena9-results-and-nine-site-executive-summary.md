# Arena9 result, nine-site executive review, and submission decision

**Review date:** 2026-10-26 UTC  
**Focus:** `GEMSDOE24`, `25`, `27`, `28`, `30`, `31`, `32`, `33`, `36`  
**Score provenance:** every historical site score in this report is **OWNER-REPORTED**, not organizer-confirmed. No cryptographic DrivenData receipt in this checkout binds those scores to the reviewed bytes.

## Executive decision — read this first

### What is the best historical submission?

`GEMSDOE32` **`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros`**, owner-reported **`0.2778`**, remains the highest historical score among the nine focus sites. It was already submitted. **Do not resubmit it.** A duplicate upload spends a scarce slot and produces no new information.

### Is any newly generated file cleared to submit now?

**No.** The latest local file is:

- **Research download:** [`gemsdoe32-arena9-pgrn-pu37654-20261026T053246Z-4f7aba9b-zeros.tif`](../downloads/gemsdoe32-arena9-pgrn-pu37654-20261026T053246Z-4f7aba9b-zeros.tif)
- **SHA-256:** `8eee6e1a85708c9188c7b9d7f436deab621657aab22c3d9d48da9dd64c84e609`
- **Unique name:** `GEMSDOE32-A9-PGRN-PU-4F7ABA9B`
- **Portal note (74/140):** `GEMS32 A9 PGRN-PU 37654d | HR 0.0579 SGMC 0.0878 | research; DO-NOT-SUBMIT`
- **Decision:** **DOWNLOAD FOR RESEARCH/AUDIT: YES. SUBMIT TO DRIVENDATA: NO.**

The GeoTIFF is cryptographically new and its dot mask has zero exact matches among 304 refreshed registry files, but it is **not protocol-unique**: `99.4317%` of its dots are within three pixels of the registered spacing-5 calibration lattice (`>70%` stop threshold). More importantly, its primary fold-local `HOLDOUT-DTI = 0.05791 [0.04849, 0.06719]` is decisively below the `0.2778` Champion rule on the same evaluator (`0.09920 [0.08623, 0.11261]`) and the repository-best H38 result (`0.11696 [0.10053, 0.13204]`).

### Can we responsibly claim it will score above `0.2778`, `0.3195`, or `0.4413`?

**No.** The Arena9 result is negative. Its independent off-catalogue SGMC proxy improved (`0.08780 [0.07392, 0.09958]` versus Champion `0.06412 [0.05668, 0.07178]`), but the mandated primary holdout worsened by `-0.04129 [-0.05498, -0.02770]`. A proxy win cannot be converted into a leaderboard prediction. A score above `0.2778` remains scientifically possible, but no current `GEMSDOE32` artifact has earned that claim.

## Nine-site executive summary

The source for each “current” statement is the owner repository README at the post-run `main` commit pinned below and hashed in `evidence/focus_sites_release_review_20261026.json`. These are owner-authored project records, not organizer receipts. Evaluators differ between repositories, so their HOLDOUT-DTI values must **not** be ranked as if they were measured by one instrument. Arena9 itself was **not** rerun against these later heads: its 304-raster comparison remains frozen at the earlier refs in `registry/focus_registry_manifest.json`.

| Site (pinned `main`) | Highest historical submission (`OWNER-REPORTED`) | Current distinct work at reviewed HEAD | Clear action |
|---|---|---|---|
| [`GEMSDOE24`](https://github.com/buffedlizard55-lab/GEMSDOE24/commit/17496743a9695974370512db64d8140ea1ccfd2f) | `h25-1-dotted-h19-5-d1-5`, `0.2477` | `H24-DPRF1`: site reports `HOLDOUT-DTI 0.16379 [0.15045,0.17739]`, but its selector says `DO_NOT_SUBMIT`; our literal lattice recheck is `99.5645%` | **Do not submit.** Best current local signal in that repo, but not cleared under the requested literal registry rule |
| [`GEMSDOE25`](https://github.com/buffedlizard55-lab/GEMSDOE25/commit/66b97bc9a986aaf8175d283536775c9015a3d364) | `dotted-h19-5-d2-8`, `0.2600` | `H71-HGPC`, current README says holdout fail versus H35 and `DO NOT SUBMIT`; literal lattice recheck `100%` | **Do not submit** |
| [`GEMSDOE27`](https://github.com/buffedlizard55-lab/GEMSDOE27/commit/426426b402f90f4e0786990b4edd261d9dd48085) | `topo-gap-closure-t-v2-on-d1-5`, `0.2449`; independent H29 later `0.2190` | `H31-DRCG-WL` is labelled “OK TO DOWNLOAD AND SUBMIT” by that repo after a 27-raster check and `HOLDOUT-DTI 0.047302` on its own evaluator. **Cross-check irregularity:** refreshed all-focus literal check places `99.6149%` of its dots within 3 px of the registered lattice | **Do not submit under this prompt.** Its site-level approval used a narrower registry than the mandatory refreshed registry |
| [`GEMSDOE28`](https://github.com/buffedlizard55-lab/GEMSDOE28/commit/348ff086e29b9c48bb7104daacb647af31a184bf) | `h36-1-rung30-blind-r1`, `0.2710` | `S20-NCHC`: `HOLDOUT-DTI 0.131263 [0.120346,0.141838]` below same-run baseline `0.144433`; site verdict negative | **Do not submit** |
| [`GEMSDOE30`](https://github.com/buffedlizard55-lab/GEMSDOE30/commit/73db382d3c990d0aa0b5126997a67213cc56dee4) | `d28-poisson300m-offcat-44090`, `0.2600`, dot-identical lineage to GEMSDOE25 | Latest `FFL-1` is duplicate-stopped (`78.28%` within 3 px of `MSDB-1v2`); `G30-TAD` improved a local point estimate but paired CI crossed zero | **Do not submit** |
| [`GEMSDOE31`](https://github.com/buffedlizard55-lab/GEMSDOE31/commit/e6e85b357914068b3ba57ace0f899dde13f110a6) | `h27-4-solo-d28`, `0.2708` | `H31-S UDAP-SSLIC` has positive local confirmation but is explicitly research-only; current README reports `99.93%` lattice overlap | **Do not submit** |
| [`GEMSDOE32`](https://github.com/buffedlizard55-lab/GEMSDOE32/commit/174c1c3f3db3f23136d70b16781cab2097cb1643) | **`h33-h33-2-b2`, `0.2778` — nine-site best** | Arena9 PGRN-PU: primary `HOLDOUT-DTI 0.05791`, negative; H38 remains repository holdout best `0.11696`, also negative on other gates | **Do not resubmit Champion; do not submit Arena9/H38** |
| [`GEMSDOE33`](https://github.com/buffedlizard55-lab/GEMSDOE33/commit/565d663a9c6b5a68f405277d684a12be8dd8ae26) | `h33d-analog-tip-stepover-r30`, `0.2632` | `A33-R3-LLC`: screen `HOLDOUT-DTI 0.137868` vs CSHT `0.137555`, confirmation `0.131506` vs `0.132066`; paired CIs cross zero and selector finds 0 eligible | **Do not submit** |
| [`GEMSDOE36`](https://github.com/buffedlizard55-lab/GEMSDOE36/commit/4aa901be69307ea69c2a6fa0872135d6697e1d7a) | `anderson-geothermal-pinn-38854`, `0.2750`; exact Champion superset plus 1,200 dots | `MTO-36`: `HOLDOUT-DTI 0.067611 [0.058449,0.077867]`; paired CI vs matched control crosses zero and all-reference overlap reaches `100%` at the spacing-5 lattice | **Do not submit** |

**Portfolio conclusion:** the best historical score is still `0.2778`, and the best already-scored genuinely independent 2026-10-25 method reported in these sites is GEMSDOE27 H29 at `0.2190`. No refreshed candidate simultaneously clears comparable holdout superiority, the literal all-registry uniqueness rule, format validation, and the separate weekly-slot selector.

## Why `h33-h33-2-b2` is reported at `0.2778`

### What the bytes and owner history establish

The strongest evidence is a nested emission family, not a new detector:

1. `H19-5` emitted a broad corroborated support field (`121,131` positive pixels; owner-reported `0.1922`).
2. Kernel-scale thinning to `d=2.8 px` reduced neighboring predictions to `44,090` dots (owner-reported `0.2600`).
3. Removing `3,891` dots within `100 m` of the visible catalogue produced the B=1/solo rung (`40,199` dots, owner-reported `0.2708`).
4. Removing another `2,545` dots in the `100–200 m` catalogue annulus produced B=2 (`37,654` dots, owner-reported `0.2778`).
5. GEMSDOE36's owner record says adding 1,200 Anderson-mechanics dots back produced `0.2750`; GEMSDOE27's gap-closure variant is likewise reported below its parent.

The dot nesting and counts are byte-forensics facts. The score sequence is **OWNER-REPORTED**. Because no organizer receipt binds each score to each hash and the private truth is unavailable, it does **not** identify per-dot hidden credit, hidden TP/FP/FN, recall, or a causal B=2 effect.

### Metric-consistent scientific explanation

For distance-weighted Tversky with `alpha=0.2`, `beta=0.8`, and the 300 m triangular kernel,

`DTI = TPw / (TPw + 0.2 FPw + 0.8 FNw)`.

For binary predictions, let `T=TPw`, `S=sum(p)`, `M=sum_x p(x) max_g K(d(x,g))`, and `|G|` be hidden truth mass. Since `FNw=|G|-T`, the exact identity used by `src/gems32/metric.py` is:

`DTI = T / [0.2 (T + S - M) + 0.8 |G|]`.

The earlier expression `0.8 T + 0.2 S + 0.8 |G|` is not algebraically equivalent and is withdrawn. For an isolated added prediction that gives its full kernel credit `k` to previously uncovered truth, the idealized break-even condition is `k > 0.2 * DTI` (`0.05556` at `DTI=0.2778`). For arbitrary additions near already-covered truth, there is no universal scalar threshold: actual marginal `delta TPw`, `delta FPw`, and `delta FNw` must be evaluated.

The **plausible**, not proven, explanation is therefore metric-aligned subtraction: spacing reduced redundant predictions, and catalogue-annulus pruning removed mass with low marginal hidden-truth credit while preserving useful off-catalogue coverage. Known faults are masked in scoring, making that mechanism geologically and metrically credible, but only private truth could establish it causally.

This also explains why emission-only variants are unlikely to make a large leap: a result above the reported `0.2778` probably needs a field that ranks genuinely new off-catalogue fault geometry above H19-5's low-credit tail, not another small thinning or graft. Arena9 tested one such detector hypothesis and did not validate it.

## Arena9 scientific result

### Hypothesis

High label-free concordance among 1 m LiDAR scarps, magnetic tilt, gravity/basement/MT edges, and hydrothermal alteration might identify unlabelled faults that ordinary binary learning incorrectly treats as negatives. Arena9 protected the top physical-prior tail from the reliable-negative pool.

### Three frozen experiments

| Arm | Reliable-negative rule | `HOLDOUT-DTI` (`GEMSDOE32-HIDE-RECOVER-v3.0`, 22,232 withheld, 95% CI) | SGMC-cal `HOLDOUT-DTI` (`62,703` positives, 95% CI) |
|---|---|---:|---:|
| `EXP1_PGRN80` **selected by primary holdout** | protect top 20% physical concordance | **`0.05791 [0.04849,0.06719]`** | **`0.08780 [0.07392,0.09958]`** |
| `EXP2_PGRN60` | protect top 40% | `0.05267 [0.04349,0.06162]` | `0.08254 [0.07410,0.09007]` |
| `EXP3_PGRN_BAG` | average q60/q70/q80 | `0.05504 [0.04593,0.06404]` | `0.08446 [0.07334,0.09400]` |
| `0.2778 Champion rule` | historical D2.8 + fold-visible B=2 | `0.09920 [0.08623,0.11261]` | `0.06412 [0.05668,0.07178]` |
| H38 repository best | prior 53-channel run | `0.11696 [0.10053,0.13204]` | `0.05037 [0.04467,0.05548]` |

**Interpretation:** physics-protected PU transferred strongly to old SGMC map faults but failed to recover withheld Quaternary catalogue segments. That is a domain-shift signature, not evidence of leaderboard improvement. The non-fault processes most likely to mimic the protected signal are lithologic contacts, volcanic-flow margins, fan channels, and terrace risers.

## Automated validation

- Leakage canary: `57/57` channels pass; worst two-polarity AUC `0.62350 <= 0.90`.
- Pre-placement surface: `304` refreshed registry files, max `|Spearman| = 0.12942`; no threshold breach. One explicit `32×48` `GEMSDOE36` format-test file is grid-incompatible and reported as an irregularity.
- Final dots: max `|Spearman| = 0.07198`; exact dot-mask matches `0`; literal lattice overlap `99.4317% > 70%` -> duplicate-lane stop.
- GeoTIFF: one `float32` band, `EPSG:32611`, `3730×3292`, exact template transform, `nodata=None`, all `12,279,160` cells finite in `[0,1]`, zero NaN, zero known-catalogue positive pixels.
- Weekly slots used: `0`.
- Full machine record: [`evidence/arena9_run_card.json`](../../evidence/arena9_run_card.json).

## Irregularities requiring review

1. **Score provenance:** the supplied historical numbers are not backed here by organizer receipts. Keep `OWNER-REPORTED`; do not relabel them `ORGANIZER-CONFIRMED`.
2. **Conflicting targets:** `0.3195` and `0.4413` appear in the owner brief. A later `GEMSDOE32` main-head record reports a direct 2026-10-26 observation of `0.4437` and identifies `0.4413` as its cached 2026-10-25 value; this sandbox could not independently refresh DrivenData. None of these leaderboard values is a model score.
3. **Impossible literal 37,654-dot lattice gate:** the registered spacing-5 raster covers essentially the whole footprint within three pixels. Arena9, H24-DPRF1, and GEMSDOE27 H31 have `99.43%`, `99.56%`, and `99.61%` overlap respectively. Do not silently exempt it. A future preregistration must either use a sufficiently lower dot budget or obtain an explicit protocol revision before experimenting.
4. **Narrow-registry promotion mismatch:** GEMSDOE27 currently says H31 is approved after 27 comparisons, but it fails the refreshed literal lattice check. This report therefore does not authorize it.
5. **One malformed registry entry:** `GEMSDOE36/docs/downloads/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif` is `32×48`, not the competition grid. It is reported but cannot produce a meaningful rank/overlap measurement.

## Official/manual-review links

- DOE GEMS competition: <https://www.drivendata.org/competitions/306/competition-doe-gems/>
- Problem description and metric: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
- Organizer reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
- Official DOE/NLR rules PDF: <https://docs.nlr.gov/docs/fy26osti/96647.pdf>
- USGS GeoDAWN release: <https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and>
- OpenEI GDR INGENIOUS record 1391: <https://gdr.openei.org/submissions/1391>
- EPSG:32611: <https://epsg.io/32611>

Only GitHub was reachable from this sandbox. Competition, USGS, NLR, and OpenEI links are provided for manual review; they were not freshly fetched here. Mirrored inputs were accepted only after SHA-256 verification against `registry/data_manifest.json`, which proves mirror consistency rather than organizer authenticity.
