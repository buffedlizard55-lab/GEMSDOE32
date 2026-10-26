# ARENA48 results + 9-site executive summary — 2026-10-26

## 0. Decision in one paragraph

**There is no new file to submit this week.** The unique ARENA48
JXSTEP file was generated exactly as requested and passed the full
automated validation, but it failed the pre-registered promotion
gates: it does not beat the already-submitted GEMSDOE32 champion on
both holdout instruments, and its calibrated projection is far below
0.2778. The best-scored file in the 9-site group remains the
already-submitted GEMSDOE32 champion `h33-h33-2-b2` at **0.2778
(label: OWNER-REPORT — copied from the project score ledger; no
organizer receipt exists in any repo, irregularity IR-32-SCORE-01)**.
Do not resubmit it. No final-pick choice is made here: promotion of
one evaluated file belongs to the separate weekly-slot selector.

## 1. Required table — file to download / score / unique?

Scores are **estimated scores**. Every number is labelled **only**
`HOLDOUT-DTI`, `OWNER-REPORT`, or `MODEL projection`. There is **no**
`ORGANIZER-CONFIRMED` number anywhere in the 9 repositories (no
submission-page receipts are recorded), so none is claimed.
“Unique” means byte/dot-unique versus the other 8 focus winners AND
the refreshed 375-raster registry; measured this session from raster
bytes (`evidence/arena48_focus9_overlap.json`), not from filenames.

| # | Site | File to download (one click) | Estimated score (label) | Dots (bytes) | Unique vs other 8 + registry? | Submit? |
|---|---|---|---|---|---|---|---|
| 1 | GEMSDOE24 | `gemsdoe24-h25-1-dotted-h19-5-d1-5-20261004T214830Z-9c65c327-zeros.tif` | 0.2477 (OWNER-REPORT) | 60,069 | **NO** — H19-5 family; min pairwise within-3px overlap 86.72% | NO |
| 2 | GEMSDOE25 | `gemsdoe25-dotted-h19-5-d2-8-20261004T211823Z-6879afa0-zeros.tif` | 0.2600 (OWNER-REPORT) | 44,090 | **NO** — same family | NO |
| 3 | GEMSDOE27 | `gemsdoe27-topo-gap-closure-t-v2-on-d1-5-zeros.tif` | 0.2449 (OWNER-REPORT) | 61,328 | **NO** — same family (addition-only variant) | NO |
| 4 | GEMSDOE28 | `gemsdoe28-h36-1-rung30-blind-r1-20261004T211259Z-5ea18b5d-zeros.tif` | 0.2710 (OWNER-REPORT) | 37,660 | **NO** — same family | NO |
| 5 | GEMSDOE30 | `gemsdoe30-d28-poisson300m-offcat-20261004T211800Z-1d92a601-zeros.tif` | 0.2600 (OWNER-REPORT) | 44,090 | **NO** — **dot-mask identical to GEMSDOE25** (re-verified from bytes) | NO |
| 6 | GEMSDOE31 | `gemsdoe31-h27-4-solo-d28-20261026T000000Z-d313af60-zeros.tif` | 0.2708 (OWNER-REPORT) | 40,199 | **NO** — same family | NO |
| 7 | **GEMSDOE32 (group best, already submitted)** | [`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](../downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | **0.2778 (OWNER-REPORT)** | 37,654 | **NO** — same family; exact subset of GEMSDOE36 and of GEMSDOE25(D2.8) | **KEEP — already submitted; do not resubmit** |
| 8 | GEMSDOE33 | `gemsdoe33-h33d-analog-tip-stepover-20261011T012847Z-bb0dd0b4-zeros.tif` | 0.2632 (OWNER-REPORT) | 41,865 | **NO** — same family | NO |
| 9 | GEMSDOE36 | `gemsdoe36-anderson-geothermal-pinn-20261004T213300Z-dd13f007-zeros.tif` | 0.2750 (OWNER-REPORT) | 38,854 | **NO** — champion **+1,200 dots** (superset, re-verified) | NO |
| 10 | **NEW — GEMSDOE32 ARENA48 JXSTEP (this work)** | [`gemsdoe32-arena48-jxstep-37654-20261026T215839Z-6a28221e-zeros.tif`](../downloads/gemsdoe32-arena48-jxstep-37654-20261026T215839Z-6a28221e-zeros.tif) · [zip](../downloads/gemsdoe32-arena48-jxstep-37654-20261026T215839Z-6a28221e-zeros.zip) | HOLDOUT-DTI 0.1063 [0.0921, 0.1207] (below); **MODEL projection of live score ≈ 0.098, interval [0, 0.222] — NOT a score** | 37,654 | **YES** — unique vs all 9 focus winners and vs 375 registry rasters (see §4; lattice caveat) | **NO — research artifact; verdict negative** |

One-click download links also appear on the site front page
(status block → “Newest unique artifact”). Cross-repo files (rows
1–6, 8, 9) live in their own repos under the exact paths recorded
in `evidence/arena48_focus9_overlap.json`; only rows 7 and 10 are
served from this repo's `docs/downloads/`.

## 2. Per-site executive summary (one line each)

- **GEMSDOE24** — H19-5 family winner `h25-1-dotted-h19-5-d1-5`,
  0.2477 (OWNER-REPORT). Over-dotted early rung; superseded by the
  champion. Do not submit.
- **GEMSDOE25** — `dotted-h19-5-d2-8`, 0.2600 (OWNER-REPORT). The
  D2.8 rung of the same ladder; the champion is a strict subset of
  it. Do not submit.
- **GEMSDOE27** — topo-gap-closure addition on `d1-5`, 0.2449
  (OWNER-REPORT). Addition lowered the score vs its parent (0.2477):
  the cleanest group evidence that extra sub-bar dots hurt. Do not
  submit.
- **GEMSDOE28** — `h36-1-rung30-blind-r1`, 0.2710 (OWNER-REPORT).
  Blind rung near the top of the ladder, still the same family. Do
  not submit.
- **GEMSDOE30** — `d28-poisson300m-offcat`, 0.2600 (OWNER-REPORT).
  **Dot-for-dot identical to GEMSDOE25** (same mask, different
  filename/value history) — re-verified from bytes this session.
  Do not submit (it would be a duplicate).
- **GEMSDOE31** — `h27-4-solo-d28`, 0.2708 (OWNER-REPORT). The B=1
  rung (see §3). Do not submit.
- **GEMSDOE32** — champion `h33-h33-2-b2`, **0.2778
  (OWNER-REPORT)**, group best, **already submitted**. This repo's
  ARENA48 JXSTEP file is new and unique but scored below the
  promotion bar on holdout (verdict negative). Do not submit
  anything new from this repo this week.
- **GEMSDOE33** — `h33d-analog-tip-stepover`, 0.2632 (OWNER-REPORT).
  Same family. Do not submit.
- **GEMSDOE36** — `anderson-geothermal-pinn`, 0.2750 (OWNER-REPORT).
  Verified superset: champion + 1,200 dots, scoring −0.0028 vs the
  champion — independent confirmation that bar-exact deletion, not
  addition, is what paid. Do not submit.

**Which single submission is best?** The question is moot this week:
the best-scored file (GEMSDOE32 champion, 0.2778 OWNER-REPORT) is
already submitted, all 9 winners are one non-unique family, and the
only unique new file (ARENA48) failed its gates. If a future file
passes every gate, the weekly-slot selector makes the pick — this
lane's job is only to bring it evaluated candidates.

## 3. Why did `h33-h33-2-b2` score 0.2778, and can we beat it?

The official metric (verified line-by-line on the organizer's
problem page, §6) is the distance-weighted Tversky index

`DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw)`, triangular kernel
`k(d)=max(1−d/3,0)` over 300 m.

For a binary dot map, a dot at distance `d` from the nearest hidden
ground-truth pixel adds credit `k(d)` to TPw only for the single
best-covered ground-truth pixel and adds redundancy-weighted FP
cost shared when several dots compete for the same ground-truth
pixel. The champion is the B=2 rung of a measured deletion ladder
(all rungs OWNER-REPORT):

| Rung | Dots | Score (OWNER-REPORT) |
|---|---|---|
| H19-5 base | 121,131 | 0.1922 |
| D2.8 (GEMSDOE25/30) | 44,090 | 0.2600 |
| B=1 solo (GEMSDOE31) | 40,199 | 0.2708 |
| **B=2 champion (GEMSDOE32)** | **37,654** | **0.2778** |
| Champion +1,200 (GEMSDOE36) | 38,854 | 0.2750 |

New byte-level evidence this session
(`evidence/arena48_pass2_verification.json` →
`champion_ladder_annulus_from_bytes`, distances to the *visible*
catalogue on the restored grid):

- D2.8 → B=1 removed exactly **3,891 dots, all at distance exactly
  1.0 px** from catalogue faults (100% with d ≤ 1).
- B=1 → champion removed exactly **2,545 dots, all with
  1.414 px ≤ d ≤ 2.0 px** (100% in the (1,2] annulus).
- Champion retains **0 dots with d ≤ 2 px** from the catalogue.

So the champion is exactly the parent field's dots with the
0–2 px catalogue annulus deleted — no more, no less. Mechanically:
near-catalogue dots mostly buy fractional credit `k(d)` that is
already paid by better-placed neighbours, while their FP cost is
real (shared-redundancy). Deleting the annulus removes mostly
redundant credit at full marginal cost, which raises DTI; every
addition experiment across 9 repos (GEMSDOE27 gap-closure, GEMSDOE36
+1,200, this lane's earlier additions) moved the score down or not
at all. This is why 0.2778 is the group best: it is the only rung
that deleted exactly to the kernel's efficient frontier.

**Can >0.2778 be achieved?** In principle yes — the public
leaderboard (§6) reaches 0.4437, so the hidden fault population
certainly rewards maps far better than ours. But *within this
project's evidence*, no tested mechanism has beaten the champion on
both holdout instruments: the repo-best catalogue-hidden holdout
(H38-G1, HOLDOUT-DTI 0.1170) loses on the off-catalogue SGMC
instrument; ARENA48 (below) improves over the champion recipe on
one instrument and loses on the other. The honest statement is:
**>0.2778 is achievable by a better detector, not by editing the
champion's dots.** The next ranked, still-untried mechanisms
(A48-H2 ASTD, A48-H3 BADOG) are in the preregistration.

The user-cited leaderboard numbers 0.4413 and 0.3195 were checked
against the live public leaderboard at fetch time (§6): current #1
is 0.4437; 0.4413/0.3195 no longer appear in the top rows — flagged
as stale snapshot values, not used as targets anywhere in the
promotion math.

## 4. ARENA48 JXSTEP: hypothesis, results, verdict

Preregistered before any result
(`docs/research/arena48-preregistration-and-hypotheses.md`).

**Hypothesis (A48-H1-JXSTEP).** A blind fault juxtaposes different
rock packages, producing a *plateau-to-plateau step* in basement
depth / potential-field / conductivity / radioelement channels —
geometrically distinct from both broad ramps (folds, basin tilt)
and thin line anomalies (dykes, fault gouge: the named non-fault
mimics). `src/gems32/juxtaposition.py` measures exactly that
(inner ±2.5 px vs outer ±6.5 px plateaus, 4 orientations,
step-vs-ramp discrimination), label-free, on bands 15/13/17/6 +
5×5 roughness of band 12. No prior run in any of the 9 repos
implemented a step-vs-ramp juxtaposition detector.

**Results** (all HOLDOUT-DTI; evaluator
`GEMSDOE32-HIDE-RECOVER-v3.0`, n=22,232 withheld positives;
off-catalogue second instrument `GEMSDOE32-SGMC-CAL-v3.0`,
n=62,703). Full record: `evidence/arena48_jxstep_run_card.json`,
`evidence/arena48_jxstep_experiments.json`; independent re-check:
`evidence/arena48_pass2_verification.json`; figure:
`docs/assets/fig_arena48_jxstep.png`.

| Arm | HR HOLDOUT-DTI [95% CI] | SGMC-cal HOLDOUT-DTI [95% CI] |
|---|---|---|
| Champion recipe (control, replicated exactly) | 0.09920 | 0.06412 |
| CTRL-35 replica | 0.09969 [0.0837, 0.1151] | 0.05369 |
| EXP1 unsupervised `jx_concordant` only | 0.05509 | 0.06203 |
| EXP2 35ch+JX7 HistGB | 0.10362 | 0.05525 |
| **EXP3 EXP2 85% + `jx_quiescent` 15% (final)** | **0.10630 [0.0921, 0.1207]** | **0.06141 [0.0533, 0.0683]** |
| H38-G1 (repo best, prior session) | 0.11696 | 0.05037 |

- Leakage canary: PASS (worst single-feature holdout AUC 0.6235,
  `coherence_s2`; all JX channels ≤ 0.576). No channel is leakage.
- Paired bootstrap EXP3 vs champion recipe (HR): +0.00709, 95% CI
  [−0.00038, +0.01427] → **not significant** (gate needs CI > 0).
  vs CTRL-35: +0.00660 [+0.00090, +0.01185] → significant. SGMC vs
  champion: −0.00271 [−0.00998, +0.00421] → loses.
- EXP1 is mechanistically informative: with **zero supervision**,
  the pure juxtaposition field nearly matches the champion on the
  off-catalogue SGMC instrument (0.0620 vs 0.0641) while being weak
  on catalogue-hidden recovery (0.0551). The signal is real but
  partial — consistent with SGMC-type (map-contact) faults carrying
  steps and many catalogue faults being thin-line features.
- Diagnostic: panel A of the figure shows rectilinear texture in
  `jx_concordant`, consistent with airborne-survey flight-line
  seams responding to the step operator (GeoDAWN line spacings are
  documented at 200/400 m). This is flagged as irregularity
  IR-A48-JX-01 and is exactly what A48-H3 (block normalization) is
  designed to remove before any JXSTEP rerun.
- Uniqueness: refreshed registry = 375 rasters. Pre-placement
  surfaces: EXP2 gated field worst |Spearman| 0.2385 (vs local
  unsubmitted H38-G1); `jx_quiescent` worst |Spearman| 0.0627.
  Final dots: worst genuine within-3px overlap 68.46% (vs local
  unsubmitted `hcvf2`); the literal all-registry gate fails only
  against the 206,895-dot calibration lattice `r13-lattice-s5`,
  which covers 99.87% of the footprint within 3 px and makes the
  literal ≤70% rule unsatisfiable by *any* 37,654-dot map (the
  champion itself scores 99.92% against it) — standing irregularity
  IR-42-UNIQ-01; the genuine-detector reading is the operative one
  and it passes. Two registry rasters could not be measured
  (IR-A48-REG-01/02, §7) and are recorded, not silently skipped.
- Validation (no human inspection): shared writer + validator —
  EPSG:32611, 3730×3292, float32, all 12,279,160 cells finite,
  values in [0,1], 0 NaN in footprint, 0 on-catalogue dots, strict
  whole-array portal check PASS; ZIP contains exactly one TIFF
  byte-identical to the primary; sha256
  `4aa4d8f2f5fb39af64af69d575a13c14f146204e5147e9ee10cbb267895c43a6`.

**Verdict: `negative`.** Failed gates: HR point > H38 0.116958;
paired HR vs champion CI > 0; SGMC-cal ≥ champion. The file exists,
is unique, is portal-valid, and must **not** be submitted:
**MODEL projection** of its live score from the drift instrument
(n=12, Spearman ρ=+0.53, p≈0.09 n.s., LOO MAE 0.0534) is ≈ 0.098
with interval [0, 0.222] — a projection, never a score — far below
0.2778 (OWNER-REPORT).

If a future selector ever needs its portal identity:
submission name `GEMSDOE32-A48-JXSTEP-4AA4D8F2`, note (≤140 chars):
“A48-H1 JXSTEP juxtaposition 37654d B2 | HR=0.1063 SGMC=0.0614 |
research artifact”.

## 5. Exactly how to submit (when a file is ever authorized)

1. Use **only** a `-zeros.tif` primary (or its `.zip` containing
   exactly that one TIFF). Never upload a `-nan.tif` first.
2. Portal error `Predicted values must be in range [0, 1]`: this
   project's root cause was the float32 no-data sentinel
   −3.4028234663852886e+38 and NaN cells reaching the writer. The
   shared writer now guarantees: single band, float32, EPSG:32611,
   3730×3292, 100 m, `nodata=None`, every cell finite and in [0,1],
   0 NaN. Automated proof, no human inspection:
   `python scripts/check_submission.py --strict-finite <file>.tif`
   (must print PASS). The official page says data outside the
   footprint should be null/NaN; the in-footprint constraint (the
   one the portal enforces with that error) is values in [0,1]. The
   `-nan.tif` twin (identical dots, NaN outside) is kept only as a
   fallback if a portal variant ever requires it.
3. On DrivenData: Competitions → DOE GEMS Prize (#306) →
   **Submissions → Upload submission** → choose the `-zeros.tif`
   (or `-zeros.zip`) → set the unique **submission name** and the
   ≤140-character note from the run card → submit → wait for status
   `Scored`, then copy the score from the submission page. Only a
   score copied from that receipt may ever be labelled
   `ORGANIZER-CONFIRMED`; until then it is `OWNER-REPORT`.
4. After uploading, verify the uploaded bytes: sha256 of the file
   you uploaded must equal the run-card sha256 (above).
5. Remember the prize structure (official page): **one chosen
   submission counts for both rounds**; the final round rescores it
   on an expert-expanded hidden set. Never burn the pick on an
   unpromoted file.

## 6. Official sources (fetched and checked line-by-line)

- Problem/metric/submission format:
  https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  (α=0.2, β=0.8, 300 m triangular kernel; single-layer float32,
  EPSG:32611, 100 m, values in [0,1]; one chosen submission both
  rounds; Initial Prize top-5 × $10k on a fixed private set, Final
  $250k on expert-expanded set; external data allowed with licence.)
- Public leaderboard (fetched 2026-10-26):
  https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
  (#1 0.4437, #2 0.3916, #3 0.3904 — user-cited 0.4413/0.3195 are
  stale; flagged, not used.)
- Competition rules PDF: https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Reference solution: https://github.com/drivendataorg/gems-prize-reference-solution
- USGS GeoDAWN (data provenance, CC0):
  https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and
  (DOI 10.5066/P93LGLVQ; 200/400 m line spacings — relevant to
  IR-A48-JX-01.)
- INGENIOUS compilation, GDR submission 1391 (CC-BY-4.0):
  https://gdr.openei.org/submissions/1391 (DOI 10.15121/1881483.)

## 7. Irregularities flagged this session

- **IR-A48-JX-01** — rectilinear flight-line-like texture in
  `jx_concordant` (figure panel A): the step operator partially
  responds to survey acquisition seams. Blocks any JXSTEP rerun
  until A48-H3 block normalization is applied.
- **IR-A48-REG-01** — `GEMSDOE31/docs/downloads/gemsdoe31-csdu-stepover-8cf9dc27-nan.tif`
  has non-finite values *inside* the footprint (not measurable by
  the registry audit; would also fail the portal range check).
- **IR-A48-REG-02** — `GEMSDOE36/docs/downloads/GEMS36_FORMAT_TEST_NOT_SUBMISSION.tif`
  is on a mismatched grid (format test by name; not measurable).
- Standing: **IR-32-SCORE-01** (no organizer receipts; all group
  scores OWNER-REPORT), **IR-42-UNIQ-01** (literal lattice gate
  unsatisfiable), **IR-42-INSTR-02** (SGMC-only gating invalid).

## 8. What to run next (ranked, from the preregistration)

1. **A48-H3 BADOG** (block-adaptive normalization of GeoDAWN
   channels; acquisition-block raster already verified present in
   the GEMSDOE24 mirror) — removes IR-A48-JX-01; then rerun JXSTEP
   once. New hash pin required for the block raster.
2. **A48-H2 ASTD** (along-strike termination density) — needs no
   new data.
3. **A48-H4 CHI/knickpoint** — blocked until a raw DEM is reachable
   (band 12 is detrended; 3DEP unreachable from this sandbox).
4. **A48-H5 MSEIS** — blocked by network allowlist (USGS ComCat).

Budget note: this lane used its ≤3 experiments (EXP1–EXP3). The
next lane starts from the preregistration ranking, not from editing
ARENA48's dots.
