# Euler-lane results & nine-site executive summary (2026-10-27)

## 🔴 Decision first — read this box

**No file is OK to download-and-submit to DrivenData today.** This session generated one new,
genuinely unique, portal-valid GeoTIFF (Euler E1, below) and tested it under the frozen
protocol. It **failed the promotion gates**, so its verdict is **negative — DO NOT SUBMIT**
(0 weekly slots spent). The best historical file (`0.2778`, GEMSDOE32) was already submitted —
resubmitting it spends a slot for zero new information. *Download for research/audit: YES.
Submit to the live portal: NO for every file in this repository right now.*

| File to download | Estimated score (labelled — read the class) | Unique vs the other GEMSDOE sites? | OK to submit? |
|---|---|---|---|
| **NEW** `docs/downloads/gemsdoe32-euler-e1-37654-20261028T000236Z-71f0a187-zeros.tif` (SHA-256 `9a9d00d0…bed17`, 37,654 dots) — audit/research only | **HOLDOUT-DTI** `0.0987 [0.0845, 0.1139]` (`GEMSDOE32-HIDE-RECOVER-v3.0`, n=22,232 withheld positives) + off-catalogue **HOLDOUT-DTI** `0.0663 [0.0558, 0.0751]` (`SGMC-CAL-v3.0`, n=62,703). **These are local proxy estimates, NOT a predicted leaderboard score.** No live score exists. | **YES (genuine)** — surface max \|Spearman\| `0.153 ≤ 0.90`, final-dots max `61.20% ≤ 70%` within 3 px vs 443 registry rasters (238 unique masks). Literal rule incl. the 206,895-dot calibration lattice: **NO** (99.97% — mathematically impassable, §5) | **🔴 NO — DO NOT SUBMIT** (Euler increment null; below repo holdout best) |
| `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` (GEMSDOE32 champion, 37,654 dots) | `0.2778` **OWNER-REPORT** (owner submission log; no organizer receipt in this repo — not ORGANIZER-CONFIRMED) | NO — head of the single H19-5 family (see nine-site table) | **NO — already submitted; do not resubmit** |
| Any of the other eight site winners (table §2) | `0.2449–0.2750` **OWNER-REPORT** | NO — all nine winners are one thinning/pruning family (min pairwise 3-px overlap 86.72% > 70%) | **NO — already scored / superseded** |

**Submission name (if a future selector ever clears a descendant):** `GEMSDOE32-EULER-E1-71F0A187` ·
**Portal note (52/140 chars):** `Euler E1 37654d B2 HR0.0987 SGMC0.0663 DO NOT SUBMIT` — the note itself carries the
do-not-submit verdict so the file cannot be mistaken for a cleared entry.

---

## 1. Why did `h33-2-b2` reach 0.2778, and can we beat it? (PhD-level, evidence-labelled)

**Metric.** Official DTI (α=0.2, β=0.8, 300 m triangular kernel k(d)=max(1−d/3px,0)):
`DTI = TP/(TP+0.2·FP+0.8·FN) = T/(0.2(T+S−M)+0.8|G|)` (`src/gems32/metric.py`, brute-force
verified in `tests/test_metric.py`). A single added dot with kernel credit k improves DTI
iff (isolated-dot case) **k > α·DTI** — 0.0556 at DTI 0.2778. Every sub-bar dot is a pure
0.2-tax. Official source: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/

**Byte-verified ladder (all scores OWNER-REPORT, lineage measured from rasters on disk):**
H19-5 solid (121,131 dots, 0.1922) ⊃ d2.8 thin (44,090, 0.2600) ⊃ solo/B=1 (40,199, 0.2708)
⊃ **B=2 champion (37,654, 0.2778)** ⊂ Anderson/PINN superset (38,854 = champion+1,200, 0.2750).
Thinning removed kernel-redundant ribbon mass; B=1/B=2 removed 6,436 dots within 200 m of
mapped faults (masked in scoring ⇒ ≈0 credit, full FP tax); Anderson's +1,200 sub-bar dots
cost −0.0028. Subtraction of sub-bar mass pays; addition costs. This explains the *family
ordering*; it does **not** prove causality for the private-truth score, and no receipt binds
these bytes to 0.2778 in this repo (IR-32-SCORE-01).

**Can a new file beat 0.2778 — or the public top (0.3195 historical; 0.4413 observed
2026-10-25; 0.4437 observed 2026-10-26, other teams' public rows, not ours)?** Only with a
*better-ordered field* (higher mean credit per dot at fixed mass), not with more pruning of
the same field — the ladder is exhausted (B=3 is a duplicate-lane subset). At fixed mass,
reaching ~0.44 needs roughly +59% mean credit over the champion (metric algebra, MODEL —
not a forecast). This session tested whether Euler contacts supply that field. **They do
not (§3): the Euler increment is statistically zero.** The credible remaining lever is a
spatial-context model (buffered-CV U-Net/SegFormer trained on the Distance-Weighted Tversky
loss, fixing the reference solution's fault-free-tile skip) on GPU-class compute — registered
as H38-G4/H47-5 backlog, not run here (CPU sandbox). No slot should be spent until a
candidate beats the *repository holdout best* (H47-1: HOLDOUT-DTI 0.121959, same evaluator
family) with a paired CI excluding zero **and** clears SGMC + uniqueness.

## 2. Nine focus sites — best submission per site (all OWNER-REPORT; byte-audited 2026-10-27)

Fresh registry: 443 rasters at pinned refs (`registry/focus_registry_manifest.json`);
nine winners re-hashed (`evidence/nine_site_best_files_audit.json`, SHA-256 all match).

| Site | Best file (dots) | Score (OWNER-REPORT) | Unique? | Download & submit today? |
|---|---|---|---|---|
| GEMSDOE24 | `gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif` (60,069) | 0.2477 | NO (family; ρ=0.9896 vs GEMSDOE27 winner) | NO — parent, superseded |
| GEMSDOE25 | `gems25-dotted-h19-5-d2-8-…-nan.tif` (44,090) | 0.2600 | NO (dot-identical to GEMSDOE30, ρ=1.0) | NO — superseded |
| GEMSDOE27 | `gems27-topo-gap-closure-t-v2-on-d1-5-…-nan.tif` (61,328) | 0.2449 | NO (family; min overlap 86.72% to champion) | NO — gap-closure addition scored below its parent |
| GEMSDOE28 | `gems28-h36-1-rung30-blind-r1-…-nan.tif` (37,660) | 0.2710 | NO (family) | NO — already scored |
| GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-44090-….tif` (44,090) | 0.2600 | NO (exact duplicate of GEMSDOE25) | NO — duplicate |
| GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-…-nan.tif` (40,199) | 0.2708 | NO (B=1 parent of champion, ρ=0.9676) | NO — already scored |
| **GEMSDOE32** | **`gemsdoe32-h33-h33-2-b2-…-zeros.tif` (37,654)** | **0.2778 (group best)** | NO (family head; ρ=0.9843 vs GEMSDOE36) | **NO — already submitted** |
| GEMSDOE33 | `GEMSDOE33-h33d-analog-tip-stepover-r30-….tif` (41,865) | 0.2632 | NO (family + tip additions) | NO — already scored lower |
| GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-…-zeros.tif` (38,854) | 0.2750 | NO (champion + 1,200 dots exactly) | NO — superset, scored lower |

Site pages for manual review: https://buffedlizard55-lab.github.io/GEMSDOE24/ ·
/GEMSDOE25/ · /GEMSDOE27/ · /GEMSDOE28/ · /GEMSDOE30/ · /GEMSDOE31/docs/ ·
/GEMSDOE32/docs/index.html · /GEMSDOE33/ · /GEMSDOE36/docs/ (replace prefix per site).
**Best single historical submission overall: GEMSDOE32 `h33-2-b2` (0.2778 OWNER-REPORT).**
There is no independent-method consensus to ensemble — it is one lineage.

## 3. Euler lane — three frozen experiments (HOLDOUT-DTI, `HIDE-RECOVER-v3.0`, n=22,232)

Pre-registration: `docs/research/euler-lane-preregistration-20261027.md` (5 ranked hypotheses;
E2–E5 backlog/data-blocked with named free sources — USGS ComCat
https://earthquake.usgs.gov/fdsnws/event/1/, DOE GDR https://gdr.openei.org/ — both outside
this sandbox's egress whitelist, hence explicitly *not* claimed viable here).
Canary: 42/42 features pass (max AUC 0.6246 ≤ 0.90; worst Euler channel 0.5501) — no leakage.

| Arm | HOLDOUT-DTI [95% CI] | SGMC-cal HOLDOUT-DTI [95% CI] (n=62,703) |
|---|---|---|
| EXP1 Euler-only (unsupervised) | 0.043570 [0.037967, 0.049253] | 0.040763 [0.035194, 0.045755] |
| EXP2 Base-35 OOF (control) | 0.098657 [0.084694, 0.113447] | 0.070150 [0.059197, 0.081233] (OOF union) |
| **EXP3 Base+Euler OOF (treatment)** | **0.098705 [0.084538, 0.113874]** | 0.070936 [0.059763, 0.082025] (OOF union); live retrain 0.066255 [0.055751, 0.075125] |
| Champion raster (actual bytes, flat) | 0.004515 [0.003816, 0.005262] | 0.064121 [0.056730, 0.071649] |

Paired EXP3−EXP2 = **+0.000048 [−0.003698, +0.003732], P(Δ>0)=0.522 — Euler adds nothing**
once the GBM already sees gravity/magnetic gradients. EXP1 confirms raw Euler repeats the
GEMSDOE40 live failure mode (owner-reported 0.0397 there). EXP3 beats the champion *raster*
on hide-and-recover (+0.0942, CI excludes 0) only because that instrument rewards
catalogue-like placement while the champion deliberately targets off-catalogue truth —
**this contrast must never be quoted as an expected live gain.** Against the repository's
own holdout best (H47-1, 0.121959) EXP3 loses. **Verdict: negative. Negative results are
deliverables — do not re-run Euler as a GBM feature without a new physical filter.**

## 4. How to submit (when — and only when — a future file is cleared)

1. On the site, check the top banner: green “Upload authorized” only. Today it is red.
2. Download the cleared file's **`-zeros.tif`** (or its single-TIFF `.zip`). The zeros variant
   has `nodata=None` and 0 NaNs in all 12,279,160 cells, every value in [0,1] — this is the
   fix for the portal error **“Predicted values must be in range [0, 1]”** (caused by NaN /
   −3.4e38 sentinel pixels; the `-nan.tif` twin is archival only). Euler E1 zeros file:
   13/13 checks PASS (`submission.audit_geotiff`: EPSG:32611, 3730×3292, float32, exact
   transform [100,0,243350,0,−100,4508550], 0 on-catalogue dots).
3. DrivenData → *New submission* → choose the `.tif` (single-band GeoTIFF, or `.zip` with one
   GeoTIFF) → paste the file's unique submission **name** and ≤140-char **note** (above) →
   *Create*. Competition: https://www.drivendata.org/competitions/306/competition-doe-gems/
   · format/rules: https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
   · rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
4. Save the submission-page receipt and log the score as ORGANIZER-CONFIRMED only from that
   receipt. Until then every group score stays OWNER-REPORT.

Validation here is fully automated (canary → holdout → uniqueness → saved-byte validator →
run card); no human visual inspection is used or needed.

## 5. Irregularities flagged (for review)

- **IR-EULER-01:** first Euler build OOMed (float64 full-grid normal equations); fixed once in
  `src/gems32/euler.py` (256-row strips, <1 GB), synthetic-depth unit test passes.
- **IR-EULER-02:** older cards quote the champion at HOLDOUT-DTI 0.099202 — that is a
  fold-collared *re-emission proxy*; the actual 0.2778 raster scores 0.004515 flat on
  `HIDE-RECOVER-v3.0`. Comparisons must state which object was scored.
- **IR-51-LATTICE-01 (pre-existing):** the r13-lattice-s5 calibration grid covers 99.87% of
  the footprint within 3 px, so *no* dense raster (champion included) can pass the literal
  ≤70% rule against it. Needs an owner protocol decision (exempt calibration grids); until
  then every candidate fail-closes on the literal gate even when genuine uniqueness passes.
- Registry audit incomplete: 2/443 entries malformed (incl. GEMSDOE36
  `GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif`, 32×48 test grid) — counted, never hidden.
- Data provenance: competition rasters are SHA-pinned owner mirrors (DrivenData login wall),
  not organizer-authenticated. Leaderboard tops (0.3195/0.4413/0.4437) are dated public
  observations of other teams. Sandbox egress blocks ComCat/GDR/ASF (E4/E5 deferred).

## 6. Limitations & next step

CPU-only sandbox (no GPU): the U-Net/SegFormer lever (H38-G4) needs external compute.
Recommended next session (in order): (1) owner decision on IR-51-LATTICE-01; (2) GPU
buffered-CV Tversky U-Net with the same canary/holdout/uniqueness gates; (3) only then a
selector review for one weekly slot. **Do not submit Euler E1, the champion again, or any
prior-session artifact.**

*Run card:* `evidence/euler_lane_run_card.json` · *Experiments:* `evidence/euler_lane_experiments.json`
· *Uniqueness:* `evidence/euler_uniqueness.json` · *Nine-site audit:* `evidence/nine_site_best_files_audit.json`
*Official sources:* competition & metric (above) · leaderboard
https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ · reference solution
https://github.com/drivendataorg/gems-prize-reference-solution · GeoDAWN
https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
· INGENIOUS https://gbcge.org/current-projects/ingenious/ · GDR 1391
https://gdr.openei.org/submissions/1391 · EPSG:32611 https://epsg.io/32611 · Tversky
https://en.wikipedia.org/wiki/Tversky_index · Reid et al. 1990, Geophysics 55, 80–91.
