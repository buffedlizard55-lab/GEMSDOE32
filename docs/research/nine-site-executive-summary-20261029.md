# Nine-site executive summary — 2026-10-29

Branch `arena/5f3e9cfe-gemsdoe32` · base `main@148a914` · session 14:22–~16:20 UTC · budget 3 experiments / 2 h · **slots used: 0 · experiments used: 0 · submissions made: 0**

> **DO NOT SUBMIT — no file is submit-authorized today.** Format validation passing (`scripts/check_submission.py --strict-finite`, exit 0) is not upload authorization. The one new download-for-review candidate fails the literal lattice gate, has no fold-local holdout receipt, and has no canary AUC.

Every number below is labelled with its class:
**OWNER-REPORT** = score as reported by the owner, not organizer-confirmed · **MEASURED-HERE** = computed in this session from a pinned file · **HOLDOUT-DTI** = spatially blocked hide-and-recover estimate (never a leaderboard score) · **PROXY** = SGMC-CAL off-catalogue proxy (not organizer) · **PROJECTION** = regression output, not a score.

## 1. Answers to the brief

| Question | Answer |
|---|---|
| Which file to download? | **None cleared for submission.** For review only: `gemsdoe33-r3-da-hgcm-submod-37654-20261025-a6a8552e-zeros.tif` (sha256 `2c1b6483…`, 37,654 dots). It lives in the GEMSDOE33 sibling repo (ref `7b422fa`) and was not copied into this repo. |
| Safe to download and submit? | **No.** See §4 for the blockers. |
| Passes format checks with no human steps? | **Yes** for the review candidate (`check_submission.py --strict-finite`, exit 0; values in [0, 1], EPSG:32611, 3730×3292, float32, one band). This is format only. |
| Estimated score for the new file? | **Not estimable.** Across 13 live receipts, SGMC-cal explains R² = 0.18. Its 95% prediction interval for a new file is about 0.04–0.38 (PROJECTION). No score is reported. |
| Why did `h33-h33-2-b2` (GEMSDOE32, 0.2778) score highest? | **Not established by repo evidence.** It is the B=2 end of a subtraction ladder (solo minus 2,545 dots within 200 m of the catalogue). Its static HOLDOUT-DTI is 0.0045, far below GEMSDOE24/25 (≈0.097), so the holdout does not explain the score. The owner-reported score is the only support. |
| Is a higher score achievable? | **Unproven.** The 2026-10-28 leaderboard read puts #1 at 0.4544 (`evidence/leaderboard_read_20261028.json`, not re-read today). No candidate in this repo is both unique-enough and has a validated expected gain. |
| Leaderboard conflict | **0.4413 (brief) vs 0.3195 (cited #26) vs 0.4544 (#1 in the dated read).** The 0.4413 figure has no repo source. Unresolved. Logged as IR-20261029-01. |

## 2. Per-site table (listed files)

Uniqueness = directional 3 px dot overlap against the other eight listed files (`evidence/listed_vs_listed_20261029.json`). Duplicate rule = above 0.70.

| Site | File to download (listed) | Score | Estimated score | Unique vs other listed sites? |
|---|---|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-…-989f59505db1` (60,069 dots) | 0.2477 OWNER-REPORT | none (already scored) | **No** — 1.00 vs GEMSDOE25 and GEMSDOE27 |
| GEMSDOE25 | `…dotted-h19-5-d2-8-…-e56ea318af89` (44,090) | 0.2600 OWNER-REPORT | none | **No** — 1.00 vs GEMSDOE24 and GEMSDOE27 |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-…-5512495c6bd1` (61,328) | 0.2449 OWNER-REPORT | none | **No** — 0.98 vs GEMSDOE24 and GEMSDOE25 |
| GEMSDOE28 | `h36-1-rung30-blind-r1-…-b531dae0a36f` (37,660) | 0.2710 OWNER-REPORT | none | **No** — 1.00 vs GEMSDOE24, 25, 27 |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-…-91eae1ca` (44,090) | 0.2600 OWNER-REPORT | none | **No** — dot-identical to GEMSDOE25 (IR-32-FAM-02) |
| GEMSDOE31 | `h27-4-solo-d28-…-8acb75e1` (40,199) | 0.2708 OWNER-REPORT | none | **No** — 1.00 vs GEMSDOE24, 25, 27 |
| GEMSDOE32 | `h33-h33-2-b2-…-e5eb6e7e-zeros` (37,654) | **0.2778 OWNER-REPORT (group best)** | none | **No** — 1.00 vs GEMSDOE24, 25, 27, 31, 36; ≥0.998 vs GEMSDOE28, 33 |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-…-cb490425926e` (41,865) | 0.2632 OWNER-REPORT | none | **No** — 0.997–0.998 vs GEMSDOE24, 25, 27; 0.93 vs GEMSDOE32, 36 |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-9b9ea4e6` (38,854) | 0.2750 OWNER-REPORT | none | **No** — 0.97–0.98 vs every other listed site |

Reading: the nine listed files are nested or near-identical under the repo's own 3 px rule. No listed site can satisfy the uniqueness requirement against the others as the rule is currently written. This is IR-20261029-03 and needs owner direction.

## 3. Candidate review (MEASURED-HERE unless labelled)

Gates: the 3 px non-degenerate gate (max overlap ≤ 0.70 and rank correlation ≤ 0.90 against all 231 deduplicated discrete pool files); literal lattice gate (< 0.70); SGMC enrichment (probe, top-25 only); holdout DTI at matched mass (37,654 ± 1%).

| Candidate | Dots | SGMC-cal PROXY [CI] | HOLDOUT-DTI static [CI] (diagnostic) | Literal lattice | Non-degenerate max overlap | Format | Verdict |
|---|---|---|---|---|---|---|---|
| **GEMSDOE33 r3-da-hgcm** (sibling repo) | 37,654 | 0.0795 [0.0731, 0.0863] | **0.0120 [0.0102, 0.0140]** | 0.9997 **FAIL** | 0.507 (vs GEMSDOE27) PASS | PASS | **Download for review only.** Not submit-authorized. |
| GEMSDOE32 R6-1 stepprofile-b2 (this repo) | 37,654 | 0.0949 [0.0850, 0.1055] | 0.0034 [0.0026, 0.0042] (below champion) | 0.9782 **FAIL** | 0.441 PASS | PASS | DO NOT SUBMIT (repo record, 2026-10-26; holdout also below champion). |
| GEMSDOE24 tmcg-b decoupled-basin (sibling) | 37,722 | 0.0732 [0.0606, 0.0868] | 0.0412 [0.0326, 0.0508] | 1.0000 **FAIL** (repo says 62.28%; conflict, IR-20261029-07) | 0.541 PASS | not run | DO NOT SUBMIT (repo record: unverified fold-local HR). |
| GEMSDOE30 h3a-residual-ridge | **78,256** | 0.0691 [0.0591, 0.0771] | 0.0793 | 0.9983 FAIL | 0.450 PASS | not run | **Excluded: not matched mass** (2.1× dots). |
| Champion `h33-h33-2-b2` (reference) | 37,654 | 0.0641 [0.0566, 0.0710] | 0.0045 [0.0038, 0.0053] | 0.9992 FAIL | **1.00 vs GEMSDOE24 d1.5** FAIL | PASS | Already submitted (owner-report). Its dots are a 3 px subset of a listed site's file. |

Leakage probe (SGMC truth share within 1 px; base rate 3.57%): excluded GEMSDOE30 vent-structural-offcat (52.7%, 14.7×), GEMSDOE25 h79-cthm-crustal-sgmc (8.0×), GEMSDOE30 sgmc-hedge-d10-85k (2.8×). r3-da-hgcm is 1.83× (passes the ≤ 2.5× rule). Full data: `evidence/sgmc_leakage_probe_20261029.json`.

Holdout pool run (HOLDOUT-DTI, static, 18 eligible files): `evidence/holdout_eligible_pool_20261029.json`. Two files beat the champion at matched mass on the static diagnostic (r3-da-hgcm, tmcg-b). Both are DO NOT SUBMIT or download-only. The static diagnostic is promotion-ineligible (§4).

## 4. Why nothing is submit-authorized

1. **Literal lattice gate (owner rule)** fails for every eligible file (minimum 0.978). Random champion-sized dot sets score 99.85–99.91%, so the rule is degenerate (IR-20261029-04). Owner written direction is needed: exempt dense calibration rasters, or replace the rule with a non-degenerate duplicate test.
2. **Holdout is static.** The evaluator's own provenance warning reads "Static predictions cannot establish fold-local catalogue features or leakage-free training." Every HOLDOUT-DTI number here is a diagnostic. A fold-local rerun of each candidate's generator is required (IR-20261029-05).
3. **No canary AUC** was run this session (required ≤ 0.90).
4. **Instrument is weak.** Static HOLDOUT-DTI vs live receipts: rho −0.27 (p 0.37, n = 13). SGMC-cal vs live: rho +0.58 (p 0.039, n = 13), R² 0.18. The dense GEMSDOE13 lattice (206,895 dots) has SGMC 0.094 against live 0.090, so SGMC may track dot mass. Mass-invariance is untested (IR-20261029-08).
5. **No slot has been spent.** The protocol requires a beaten incumbent at matched mass on a non-diagnostic holdout. None exists yet.

## 5. Hypotheses (3–5), none validated, none slot-eligible

Each is stated with its falsification test. Validation happens on the spatially blocked holdout, and no hypothesis is promoted on static numbers.

- **H-A — fold-local replication of the r3-da-hgcm and tmcg-b static gains.** Claim: their static HOLDOUT-DTI gains (0.0120 and 0.0412) survive a fold-local rerun. Falsified if the fold-local DTI CI overlaps the champion's CI [0.0038, 0.0053]. Needs the sibling generator code and the GEMSDOE33 round-3 run card (IR-20261029-11).
- **H-B — mass-invariance of SGMC-cal.** Claim: SGMC-cal is independent of dot count. Falsified if matched-mass resampling of the GEMSDOE13 lattice drops SGMC by more than its CI half-width. Cheap, no slot.
- **H-C — a non-degenerate duplicate test.** Claim: a rank-correlation or density-normalised overlap rule separates random sets from structured ones, unlike the literal lattice rule. Falsified if random champion-sized sets pass at rates similar to the structured candidates. Needs owner input on the rule.
- **H-D — new live receipts to recalibrate the proxy.** Claim: five or more new live scores would tighten the PROJECTION. Falsified if the R² stays below 0.3. Needs owner-supplied scores; not automatable.

## 6. Verifications and sources

- Official competition page and reference solution: `https://www.drivendata.org/competitions/306/competition-doe-gems/` and `https://github.com/drivendataorg/gems-prize-reference-solution`. **Not fetched this session.** CONTRIBUTING forbids automated access to drivendata.org, so the leaderboard figures above are from the 2026-10-28 dated read in `evidence/` and are not re-verified.
- Repo evidence: `registry/irregularities.json` (IR-20261029-01 to -12), `evidence/audit_instrument_gate_20261029.json`, `evidence/candidate_sweep_20261029.json` (deduplicated, 231 unique dot sets), `evidence/listed_vs_listed_20261029.json`, `evidence/listed_site_uniqueness_20261029.json`, `evidence/sgmc_leakage_probe_20261029.json`, `evidence/holdout_eligible_pool_20261029.json`, `evidence/candidate_decision_20261029.json`, `evidence/run_card_20261029_r3_da_hgcm.json`.
- Scripts run this session: `scripts/audit_instrument_and_gate_20261029.py`, `scripts/sweep_candidates_20261029.py`, `scripts/holdout_eligible_pool_20261029.py`, `scripts/listed_site_uniqueness_20261029.py`, `scripts/listed_vs_listed_20261029.py`, `scripts/evaluate_holdout.py`, `scripts/check_submission.py`.
- Restored data: 451 focus rasters and 30 pinned inputs, every SHA-256 verified (`.cache/registry/nine_site_all_restore_20261029.json`, `data/restore_receipt.json`).
- Baseline tests: `pytest tests -q` gave 269 passed, 3 subtests passed (before this session's edits).

## 7. Three passes (per CONTRIBUTING)

- **Pass 1 — build:** sweep, probe, holdout pool, listed-site matrices, run card, irregularities.
- **Pass 2 — adversarial review:** found and corrected a sweep dedupe bug (v2 double-counted `-nan`/`-zeros` twins). Found that the champion fails uniqueness against GEMSDOE24, and that the listed files are mutually near-duplicate. Found the static-holdout promotion-ineligibility. Each finding is an IR entry.
- **Pass 3 — re-read the brief:** the brief asked for a unique, submittable TIF. None is cleared, and the reasons are above. Scores are not estimated. The leaderboard conflict stays open.

## 8. Remaining work and limitations

- Owner decision on the degenerate lattice gate and on per-site versus family uniqueness (IR-03, IR-04).
- Reconcile the leaderboard figures with one manual read of the public page (IR-01).
- Fold-local holdout reruns for any candidate that is to be considered (IR-05, H-A).
- Canary AUC for any candidate (IR-12).
- Locate the GEMSDOE33 round-3 hypothesis and run card (IR-11).
- Correct the H51 comparator label (IR-02) and reconcile the tmcg-b lattice number (IR-07).
- Limitations: no GPU; holdout and SGMC computed on owner-supplied mirror rasters (not organizer-authenticated); the sibling-repo candidate is not verified against this repo's pins; the README prompt record is the 2026-10-27 recording, not a new verbatim copy.

Not done this session: no drivendata.org access, no submission, no slot, no new model training, no change to any pinned data digest.
