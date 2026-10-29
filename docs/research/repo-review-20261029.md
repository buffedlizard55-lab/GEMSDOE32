# Repository review — 2026-10-29 (branch `arena/2149a383-gemsdoe32`)

**Scope:** a read-only review of the repository state, the nine focus-site (`GEMSDOE24`…`GEMSDOE36`) best files, the live leaderboard, and the submission gate. **No new raster was generated and no upload was made.** Every number below is labeled by evidence class:

- **VERIFIED-LOCAL**: recomputed in this session from bytes on disk.
- **VERIFIED-WEB**: fetched in this session from an official URL.
- **OWNER-REPORT**: a score reported by the user or recorded in the repo; no organizer receipt is in the repo.
- **HOLDOUT-DTI**: a local holdout number. Not re-run this session (see §5).

---

## 1. Bottom line

1. **No file is cleared for upload.** `registry/current_status.json` has `any_file_ok_to_submit: false`. The newest unique file (`H51-1-EWSP`) has `ok_to_submit: false`. The repo's own gate rules still stand, and this review does not change them.
2. **The best-scored focus-site file is `GEMSDOE32` `h33-h33-2-b2…-zeros.tif` at `0.2778`** (OWNER-REPORT). It is the only focus-site winner whose bytes are in this checkout *and* whose hash matches the repo's record. It is also already submitted (per the repo), so resubmitting it spends a slot without adding information.
3. **The live leaderboard is not at `0.3195` or `0.4413`.** Fetched 2026-10-29: #1 is **0.4544**, #2 is **0.3916**, #3 is **0.3911** ([leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)). The prompt cites both `0.4413` and `0.3195`; neither matches the live page.
4. **Seven of the nine focus-site winners cannot be downloaded from this repo.** Their hashes are recorded, but the files are not in `docs/downloads/`. See §3 (IR-R1).
5. **Every pair among the nine focus-site winners exceeds the 70% within-3-px overlap rule** (36 of 36 pairs, per `evidence/nine_site_best_files_audit.json`). None of the nine can be resubmitted as a "unique" file. Uniqueness has to come from a new raster.

---

## 2. What was verified, and how

| # | Check | Command / source | Result | Class |
|---|---|---|---|---|
| 1 | Unit and integration tests | `/tmp/venv/bin/python -m pytest tests -q` (Python 3.11.2, `requirements.txt`) | **259 passed, 10 skipped**, 3 subtests passed, 22 s | VERIFIED-LOCAL |
| 2 | `GEMSDOE32` 0.2778 file bytes | `rasterio` read of `docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | SHA-256 `c55bafc4…ab6fa9` (matches registry). float32, **3730×3292**, 1 band, **EPSG:32611**, res **100 m**, transform `(100, 0, 243350, 0, -100, 4508550)`, nodata `None`, **NaN = 0**, min **0**, max **1**, values outside [0,1] = **0**, non-zero cells = **37,654** | VERIFIED-LOCAL |
| 3 | `H51-1-EWSP` zeros file | same | SHA-256 `f66f65e4…651740` (matches README/registry). Same grid, NaN = 0, range [0,1], 37,654 non-zero | VERIFIED-LOCAL |
| 4 | `H49-1-CGTD` zeros file | same | SHA-256 `4d8d7c05…e511fd` (matches README). Same grid, NaN = 0, range [0,1], 37,654 non-zero | VERIFIED-LOCAL |
| 5 | `-nan.tif` variant of `H33-2` | same | Same grid; **NaN = 7,111,787** (all cells outside the footprint); values in [0,1] where finite | VERIFIED-LOCAL |
| 6 | Nine-site audit hashes | Recomputed SHA-256 for each `file` path in `evidence/nine_site_best_files_audit.json` | **2 of 9 paths exist** (`GEMSDOE25`, `GEMSDOE32`); both hashes match. **7 of 9 are missing** (IR-R1) | VERIFIED-LOCAL |
| 7 | Gate status | `registry/current_status.json` | `any_file_ok_to_submit=false`; `newest_unique.ok_to_submit=false` | VERIFIED-LOCAL |
| 8 | Live leaderboard | `fetch_page` of the DrivenData leaderboard | #1 `0.4544`, #2 `0.3916`, #3 `0.3911`, #4 `0.3841`, #5 `0.3642` (Best public DW-Tversky) | VERIFIED-WEB |
| 9 | Competition data needed for holdout | `ls data/`, `ls .cache/gems_data` | `data/` holds 4 manifests/receipts only. `.cache/gems_data` **does not exist**. The holdout cannot be re-run from this checkout | VERIFIED-LOCAL |
| 10 | Official format spec | Linked in the README (`docs.nlr.gov/docs/fy26osti/96647.pdf`) | **Not re-read this session.** The format facts above come from the repo's own excerpts and the local byte checks | not verified this session |

---

## 3. Executive summary: best file per focus site

Source: `evidence/nine_site_best_files_audit.json` (scores are **OWNER-REPORT**). "In repo" means the file is in `docs/downloads/` and its hash matches the audit.

| Site | Best file (leaderboard name) | Score (OWNER-REPORT) | SHA-256 (prefix) | In this repo? | Unique vs. other focus sites? |
|---|---|---|---|---|---|
| **GEMSDOE32** | `h33-h33-2-b2-…-e5eb6e7e-zeros` | **0.2778** | `c55bafc4…` | **Yes** (hash verified) | **No** — all 36 pairs exceed 70% overlap |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-…-9b9ea4e6-zeros` | 0.2750 | `e1589102…` | No | No (same family) |
| GEMSDOE28 | `h36-1-rung30-blind-r1-…-b531dae0a36f-nan` | 0.2710 | `5556aa14…` | No | No (same family) |
| GEMSDOE31 | `h27-4-solo-d28-…-8acb75e1-nan` | 0.2708 | `07b6db44…` | No | No (same family) |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-…-cb490425926e` | 0.2632 | `87f857d5…` | No | No (same family) |
| GEMSDOE25 | `dotted-h19-5-d2-8-…-e56ea318af89-nan` | 0.2600 | `91eae1ca…` | **Yes** (hash verified) | No (same family) |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-…-91eae1ca` | 0.2600 | `8cf893ea…` | No | No (same family) |
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-…-989f59505db1-nan` | 0.2477 | `68d0e2e4…` | No | No (same family) |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-…-5512495c6bd1-nan` | 0.2449 | `33003374…` | No | No (same family) |

**Estimated score for downloadable files:** there is no valid holdout estimate for any file in this table. The `0.2778` value is an owner-reported published score. Holdout numbers for the nine files were not re-run this session. Earlier holdout headlines in the README (e.g. `H51-1 0.115134`) were **retracted** by the 2026-10-28 static re-check: the emitted H51 bytes score **0.002289** on the static evaluator, below the 0.004515 champion (`registry/current_status.json`).

**Recommendation for the leaderboard:** do **not** resubmit any of these files. The 0.2778 file is already in. The other eight would spend a slot on a duplicate.

---

## 4. Leaderboard fact check

| Claim in the prompt | Live page (2026-10-29) | Status |
|---|---|---|
| "Current competition leaderboard GEMSDOE high score: 0.4413" | #1 = **0.4544** (xiaofanhu), #2 = 0.3916 | Does not match |
| "0.3195 is the highest score right now" | #1 = 0.4544 | Does not match |
| "highest score … 0.2778" (GEMSDOE32) | Not checked: only the first of three page chunks was read, and no row showing 0.2778 appeared in it | **Not verified** — OWNER-REPORT |

Source: [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/). The leaderboard column is "Best public DW-Tversky."

---

## 5. Irregularities flagged for review

| ID | Severity | Finding | Evidence | Suggested action |
|---|---|---|---|---|
| **IR-R1** | **High** | 7 of 9 focus-site best files are **not in the repo**. The audit paths point to `docs/downloads/…` files that do not exist. The site table cannot link them as downloads. | §2 row 6; `ls docs/downloads` | Restore the bytes from the sibling repos, or drop the rows from the audit |
| **IR-R2** | **High** | Prompt scores (`0.4413`, `0.3195`) disagree with the live leaderboard (`0.4544`) and with each other. | §4 | Owner to confirm the current leaderboard figure and the organizer receipt for the 0.2778 submission |
| **IR-R3** | **High** | The 0.2778 score has **no organizer receipt** in the repo. Every score in the nine-site table is OWNER-REPORT. | `registry/current_status.json` `evidence_class` | Store the submission-page receipt in `evidence/` |
| **IR-R4** | **High** | The README's "Holdout" headline for `H51-1-EWSP` (`0.115134`) was superseded by the static re-check (`0.002289`). The README top block still leads with the older figure. | README §"2026-10-28 static re-check"; `registry/current_status.json` `headline` | Remove the superseded figure from the README top block |
| **IR-R5** | Medium | Two defaults conflict. README §4 says the primary `-zeros.tif` files have `nodata=None` with zeros outside. IR-30-019 says the writer "defaults to published-format NaN outside." The top-scoring file (0.2778) is zeros-outside; the public spec (per the repo's own IR-30-019) says null/NaN outside. Whether the portal accepted zeros-outside is **OWNER-REPORT only**. | `README.md` §4; `docs/irregularities.md` IR-30-019 | Owner to confirm which format the portal accepted, and make the writer default match it |
| **IR-R6** | Medium | Holdout evaluation cannot be reproduced from this checkout: `.cache/gems_data` is absent, and `data/` holds only manifests. | §2 row 9 | Run `scripts/restore_data.py` (fetches from `codeload.github.com`, an allowed host) before any new holdout work |
| **IR-R7** | Medium | The two evaluators still disagree on the champion (`IR-45-EVAL-02`). No canonical instrument has been chosen. | README §0.3 | Owner to pick one canonical evaluator |
| **IR-R8** | Medium | The literal lattice rule (`IR-45-LATTICE-02`) is still undecided. A dense map has about 99.7% overlap with `r13-lattice-s5`. | README §0.3 | Owner decision |
| **IR-R9** | Low | The protocol's **lane paragraph** is missing from the prompt, so the lane is provisional (`IR-45-LANE-01`). | README §"Standing Mission" | Owner to supply the lane text |
| **IR-R10** | Low | The prompt asks for the same review repeatedly. The README already contains the standing mission and the verbatim prompt. This review only adds a pointer. | README top block; `docs/research/standing-prompt-as-recorded-20261026.md` | None |

---

## 6. Can a new unique TIF be generated and validated now?

**Not in this session, and it would not be cleared if it were.** Three blockers:

1. **Holdout data is absent** (IR-R6). A candidate cannot be validated without the training features and labels. Restoring them is feasible from allowed hosts, but it has not been done.
2. **The gate requires a holdout win with a paired CI above zero, against the current same-evaluator best.** No current candidate meets that bar on the static evaluator (IR-R4).
3. **The lane is provisional** (IR-R9), and the lattice rule is undecided (IR-R8). Both block promotion under the repo's own rules.

Any new generation should be run through the existing `scripts/evaluate_holdout.py` and `scripts/submission_writer.py` path with a fixed evaluator, and its output should be recorded in a run card before any slot decision. The user's requirement to make the upload status obvious is already met by the README's top block and `registry/current_status.json`: they say **DO NOT SUBMIT**.

---

## 7. Suggested next steps (ordered by expected value)

1. **Restore the holdout data** (`scripts/restore_data.py` → `.cache/gems_data`, pinned SHA-256 per file). Re-run the holdout on the 0.2778 bytes to get a local HOLDOUT-DTI for the one file we know scored well. This converts the strongest claim from OWNER-REPORT to a checked number.
2. **Obtain the organizer receipt** for the 0.2778 submission and store it in `evidence/`. This is the only way to make the top score ORGANIZER-CONFIRMED.
3. **Restore or remove the 7 missing focus-site files** (IR-R1), so the summary table is fully downloadable.
4. **Owner decisions:** the canonical evaluator (IR-R7), the lattice rule (IR-R8), the lane text (IR-R9), and the zeros-vs-NaN format (IR-R5).
5. **Only after 1–4:** generate one new candidate in a *new* lane, validated under the leakage canary (AUC ≤ 0.90), the uniqueness rules, and the paired holdout test, with a run card before any slot decision.

---

## 8. Run card (review only)

```json
{
  "hypothesis": "none — read-only repository review",
  "mechanism": "not applicable",
  "named_non_fault_process": "not applicable",
  "holdout_dti": "not re-run (data absent, IR-R6)",
  "correlation_overlap_vs_registry": "not computed this session",
  "raster_sha256": {
    "GEMSDOE32_0.2778_zeros": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "H51-1-EWSP_zeros": "f66f65e469deda8ab34c380f46ffd2af23feb95a0ac45230f9829d2950651740",
    "H49-1-CGTD_zeros": "4d8d7c051caf60fbd6cf24a4eceb8c921209a25225634fc54df143e5d8e511fd"
  },
  "validator_output": "3 zeros files: NaN=0, values in [0,1], float32, 3730x3292, EPSG:32611, 100 m, transform matches; 1 nan file: NaN=7,111,787 outside footprint",
  "submission_name": "none",
  "note": "none — no file cleared",
  "verdict": "negative (no new candidate; review only)",
  "tests": "259 passed, 10 skipped"
}
```

---

## Sources

- DrivenData competition leaderboard (fetched 2026-10-29): https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
- DrivenData problem statement and metric (linked from the README; not re-read this session): https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
- Reference solution (linked; not re-read this session): https://github.com/drivendataorg/gems-prize-reference-solution
- Official format PDF (linked; not re-read this session): https://docs.nlr.gov/docs/fy26osti/96647.pdf
- Repo evidence: `registry/current_status.json`, `evidence/nine_site_best_files_audit.json`, `docs/research/range-error-root-cause-2026-10-03.md`, `docs/irregularities.md`
