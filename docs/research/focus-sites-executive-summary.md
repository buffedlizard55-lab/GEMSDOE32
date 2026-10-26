# Executive summary — the 9 focus sites, reported 0.2778 result, and current submission status

**Date:** 2026-10-26 · **Round:** 6 · **Competition:** DOE GEMS Prize (DrivenData #306)
**Evidence classes (used on every number):** `[OWNER-REPORT]` = recorded from a
DrivenData submission screen; **this repository holds no organizer receipt linking
any group file's bytes to its score** (IR-32-SCORE-01), so the label
ORGANIZER-CONFIRMED is *not* used for any group score, including 0.2778.
`[HOLDOUT-DTI]` = local instrument (evaluator, withheld positives, 95 % CI stated).
`[MODEL]` = algebra on the published metric. `[measured-here]` = computed from
bytes on disk in this session (reproduce: `scripts/run_round6.py`).

---

## 1. Per-site verdicts (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36)

| Site | Its highest-scoring submission | Score `[OWNER-REPORT]` | What it actually is `[measured-here]` | Submit it today? |
|---|---|---:|---|---|
| [GEMSDOE24](https://buffedlizard55-lab.github.io/GEMSDOE24/) | `h25-1-dotted-h19-5-d1-5-…-989f59505db1` (60,069 dots) | 0.2477 | H19-5 field thinned at 1.5 px. A *parent* of the champion lineage. Later lane `gems24-gvc1` scored 0.0859. | **No** — superseded by its sparser descendants |
| [GEMSDOE25](https://buffedlizard55-lab.github.io/GEMSDOE25/) | `dotted-h19-5-d2-8-…-e56ea318af89` (44,090) | 0.2600 | Same field at 2.8 px. Direct parent of solo and champion. Later lane scored 0.0742. | **No** — superseded |
| [GEMSDOE27](https://buffedlizard55-lab.github.io/GEMSDOE27/) | `topo-gap-closure-t-v2-on-d1-5-…-5512495c6bd1` | 0.2449 | d1.5 **plus** gap-closure mass — scored *below* d1.5 (0.2477): a controlled demonstration that adding low-credit mass hurts. Later lane 0.2190. | **No** |
| [GEMSDOE28](https://buffedlizard55-lab.github.io/GEMSDOE28/) | `h36-1-rung30-blind-r1-…-b531dae0a36f` | **0.2710** | Best of a four-file ~0.27 cluster (solo 0.2708, h38-1 0.2707, h32-1 0.2649). The cluster is one family at slightly different prunes, not four independent methods. | **No** — already scored; family exhausted |
| [GEMSDOE30](https://buffedlizard55-lab.github.io/GEMSDOE30/) | `d28-poisson300m-offcat-44090-…-91eae1ca` | 0.2600 | **Dot-for-dot identical to GEMSDOE25's d2.8** (same 44,090 dots, same score — a free determinism check on the scorer, IR-32-FAM-02). Later lane 0.1462. | **No** — exact duplicate of GEMSDOE25 |
| [GEMSDOE31](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/) | `h27-4-solo-d28-…-8acb75e1` (40,199) | 0.2708 | The B=1 solo file — same `8acb75e1` lineage as GEMSDOE28's solo. | **No** — duplicate lineage, already scored |
| [GEMSDOE32](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) | `h33-h33-2-b2-…-e5eb6e7e-zeros` (37,654) | **0.2778 [OWNER-REPORT]** | Reported B=2 thinning of the solo field; lineage is described in stored byte-audit evidence, but the score is not receipt-verified. | **No** — historical artifact only; do not resubmit. R6-1 is also not approved (§4). |
| [GEMSDOE33](https://buffedlizard55-lab.github.io/GEMSDOE33/) | `h33d-analog-tip-stepover-r30-…-cb490425926e` (41,865) | 0.2632 | Fault-tip/step-over analog lane. Genuinely different geometry, but below the champion. | **No** — already scored lower |
| [GEMSDOE36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/) | `anderson-geothermal-pinn-38854-…-9b9ea4e6-zeros` (38,854) | 0.2750 | **Contains all 37,654 champion dots + 1,200 extras** (champion ⊂ Anderson exactly, IR-32-FAM-01). The extras cost −0.0028. The "PINN" framing adds no independent discovery over the champion. | **No** — champion superset, already scored lower |

**The pattern across the supplied nine-site history:** the checked-in byte-audit evidence describes **one** nested discovery lineage
(H19-5 multiline corroboration) and every top score is a pruning of it. No
"consensus of independent top methods" exists to ensemble — GEMSDOE30 duplicates
25, GEMSDOE31 duplicates 28, GEMSDOE36 contains 32. Any future gain must come
from a *different field*, which is what Round 6 builds (§4).

## 2. A plausible metric explanation for the reported 0.2778 (not causal proof)

**The metric is a budget.** Official DTI (α=0.2, β=0.8, triangular kernel
k(d)=1−d/300 m) reduces exactly to `DTI = T / (0.2(T+S−M) + 0.8|G|)`
(`knowledge/01`, verified vs brute force in `tests/test_metric.py`).
Differentiating: **a dot raises DTI iff its realised credit k > 0.2·DTI** —
0.0520 at 0.26, 0.0556 at 0.2778, 0.0652 at the 0.3262-era leader. `[MODEL]`

**The reported-score ladder** `[OWNER-REPORT]`; construction relationships are described by stored raster-audit evidence, not an organizer receipt:
H19-5 solid (121,131 dots, 0.1922) ⊃ d2.8 (44,090, 0.2600) ⊃ solo/B=1 (40,199,
0.2708) ⊃ **champion/B=2 (37,654, 0.2778)** ⊂ Anderson (38,854, 0.2750).
Champion ⊂ d2.8 exactly (37,654/37,654 dots, sha256 `c55bafc4…`). Each step
*removed* dots whose credit sat below the bar:

- **Thinning** (121k→44k): adjacent ridge pixels' 300 m kernel disks overlap
  63.6 %; the thin kept 75.9 % of kernel integral with 36.4 % of the mass.
- **B=1** (−3,891 dots ≤100 m from catalogue): known faults are masked in
  scoring, so these earned ≈0 but each paid 0.2. Gain +0.0108.
- **B=2** (−2,545 more at 100–200 m, implied credit ≈0.006–0.016/dot ≪ bar
  0.0556): first file with *zero* dots inside 200 m. Gain +0.0070 → 0.2778.
- **Anderson's +1,200** ran the same arithmetic backwards (−0.0028), and
  GEMSDOE27's gap-closure did too (0.2449 < 0.2477). Subtraction pays;
  addition of sub-bar mass costs. Three independent confirmations.

**Can we beat 0.2778?** In principle, yes: better-placed predictions can increase expected kernel credit per emitted pixel. The evidence in this checkout does not establish that any new method beats the reported value. The user's prompt gives conflicting leaderboard snapshots (0.3195 and 0.4413), neither authenticated here. Do not turn either into a projection or target score.

## 3. Five ranked hypotheses (full text: `hypotheses-round6.md`)

1. **R6-1 Step-profile scarp detector** — previously built; **negative** under the strict review (§4). `det_elev` step-vs-ramp profile geometry. Low compute cost, but not currently testable without data and a fold-local emitter.
2. **R6-2 Cross-gradient phase pairing** (mag×gravity gradient angle). Untried; cache-dependent.
3. **R6-3 Nuisance-residualised conductivity ridge**. Untried; cache-dependent.
4. **R6-4 Relocated microseismicity lineaments** — free official USGS FDSN
   source named; **blocked in this sandbox** (allowlist), fetcher ready.
5. **R6-5 1 m LiDAR scarplet chains** — free official USGS 3DEP source named;
   **blocked in this sandbox**. Neither blocked idea is claimed viable here.

## 4. Existing R6-1 artifact — **DO NOT SUBMIT** (post-hoc protocol review)

- **File (ONE-CLICK):** [`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](../downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif) · [.ZIP](../downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.zip) · SHA-256 `c7f094c1f4d00f2dd9a056dc80fecc94bf1d636363acd020c9da3659eae56547`
- **Unique name:** `GEMSDOE32-R6-STEP-23FBBB51`
- **Audit-only note:** `R6-1 STEP 37654d | audit artifact only | failed required holdout/registry overlap gates | NOT FOR UPLOAD`
- **Method (new lane):** label-free signed cross-profile step detector on
  `det_elev` only (step-vs-ramp concentration × structure-tensor coherence),
  champion emission geometry (B=2, Poisson 2.8 px, 37,654 dots). Mimic named:
  Lake Lahontan shoreline terraces / road cuts.
- **Automated format validation PASS:** one-band float32, EPSG:32611, 3730×3292; exact transform matches the hash-pinned sample template (SHA-256 `2176d08e…54d35cbc`); no nodata tag; all 12,279,160 cells finite in [0,1]; 37,654 positive pixels. This is a local format result on an owner mirror, not organizer acceptance.
- **[HOLDOUT-DTI, leakage-affected / inadmissible for promotion]:** evaluator `gems32.holdout` draws 20/21, 22,232 withheld positives; candidate pooled DTI 0.003376 [95% CI 0.002512, 0.004535] vs incumbent 0.004515 [95% CI 0.003943, 0.005250]. These are separate intervals, not paired. More importantly, candidate emission was filtered using the full catalogue before the holdout evaluator received it; hidden label geometry influenced placement. Do not cite these as a valid promotion HOLDOUT-DTI.
- **Literal uniqueness gate FAILED:** candidate dots are 97.82% within 3 px of the registered calibration raster, above the exact 70% limit. Pre-placement surface correlation against this raster was not recorded, so the required all-registry surface check is also incomplete. The earlier R6 procedure exempted the lattice; the user protocol did not.
- **Verdict:** **NEGATIVE / DO NOT SUBMIT.** The old `PROMOTE` text is superseded. No organizer score exists for this file. The TIF is retained for audit only; there is no approved file to upload.
## 5. Irregularities flagged this round

- **IR-R6-01:** 0.2778 (and every group score) was labelled
  "ORGANIZER-CONFIRMED" in places without any receipt. Downgraded to
  OWNER-REPORT everywhere this round.
- **IR-R6-02:** Former primary `geo-conduit` was bannered "OK TO SUBMIT"
  while failing the ≤70 % gate (70.24 % vs h28) and trailing the champion on
  SGMC-cal (0.0462 vs 0.0641); the site also showed contradictory red/green
  banners. Demoted; single-verdict banner installed.
- **IR-R6-03:** Previous report treated the dense calibration lattice as exempt from the literal ≤70% gate. The current review applies the user's unqualified “any registry raster” wording: R6-1 fails with 97.82% dot overlap.
- **IR-R6-04:** Along-strike (N–S) shifted null retains SGMC signal (0.121);
  across-strike collapses (0.089). Consistent with N–S structural grain;
  documented in `evidence/round6_pass2_controls.json`, not gated.

## 6. Limitations & next steps

- Data are hash-pinned **owner mirrors**, not organizer-authenticated
  (DrivenData login wall). Leaderboard #1 (0.4413) is owner-stated, unread here.
- R6-1's SGMC result is not a valid promotion basis because its placement leaked full-catalogue geometry; its candidate mask must be rebuilt from visible faults per fold before reuse.
- R6-2/R6-3 require restoring the source data and feature stack. R6-4 seismicity and R6-5 1 m LiDAR additionally require an unrestricted machine and confirmed access to the named official source. Do not spend a slot before the corrected holdout beats the comparable incumbent.
- No GPU here (2 vCPU / 3.9 GB): the U-Net route to +59 % credit needs
  external compute. The official reference solution supports CPU training
  (slower), so GPU is a speed limit, not a hard blocker.

**Official sources for manual review:** [competition](https://www.drivendata.org/competitions/306/competition-doe-gems/) ·
[problem & metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) ·
[leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) ·
[rules PDF 96647](https://docs.nlr.gov/docs/fy26osti/96647.pdf) ·
[reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) ·
[GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) ·
[INGENIOUS](https://gbcge.org/current-projects/ingenious/) ·
[GDR 1391](https://gdr.openei.org/submissions/1391) ·
[EPSG:32611](https://epsg.io/32611) ·
[Tversky index](https://en.wikipedia.org/wiki/Tversky_index) ·
[USGS FDSN](https://earthquake.usgs.gov/fdsnws/event/1/) ·
[USGS 3DEP](https://www.usgs.gov/3d-elevation-program)
