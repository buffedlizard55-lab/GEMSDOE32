# Standing brief — operative requirements (condensed, 2026-10-29)

> **Not verbatim.** This is a condensed record of the operative requirements in the 2026-10-29 session prompt, kept so every session starts from the same brief. The full prompt is very long and repeats itself. Earlier verbatim records are in `docs/research/standing-prompt-as-recorded-2026102*.md`.

## Objective
Place top of the DOE GEMS Prize leaderboard (DrivenData #306) with a **unique, portal-valid** single-band GeoTIFF whose dots target faults missing from the USGS/INGENIOUS catalogue, with emphasis on geothermal vents and conduits.

## Non-negotiable requirements
1. **Executive summary** on each focus site (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36): which file to download, its estimated score, and whether it is unique. Table columns: *file to download · estimated score · unique? · submit?*
2. **A unique TIF** must be generated and must be obviously downloadable. It must never be a copy of a previous submission (learning or education only). It must be obvious whether it is OK to download and submit.
3. **Values in [0, 1]**, EPSG:32611, 3730×3292, float32, one band, same geotransform as the template. Portal error to avoid: `Predicted values must be in range [0, 1]`.
4. **Submission name and note.** Unique name plus a note of at most 140 characters.
5. **Labels on every number:** `HOLDOUT-DTI` (evaluator version, number of withheld positives, 95% CI), `ORGANIZER-CONFIRMED` (copied from a submission-page receipt), `OWNER-REPORT` (owner's figure, no receipt), or `PROJECTION` (never a score).
6. **Leakage canary:** any feature with AUC > 0.90 alone on the holdout is leakage until proven otherwise.
7. **Lane and duplicate rules:** rank correlation > 0.90 with any registry raster, or > 70% of dots within 3 px of one registry raster's dots, is a duplicate. Check on the surface and on the final dots.
8. **Run card:** one JSON card per experiment (hypothesis, mechanism, named non-fault mimic, holdout DTI and CI, overlap vs registry, raster sha256, validator output, name and note, verdict). Negative results are deliverables.
9. **Budget:** 3 experiments or 2 hours per session. Promotion to a live slot is a separate selector step within the weekly cap. Never spend a slot on a duplicate or holdout-inferior file.
10. **Sources:** official and verified sources only, with links for manual review. No hallucinations. Flag every irregularity. No manual input from the owner is assumed.
11. **Core values** (`README.md` → *Arena Core Values*): Maximize P(Win); Own the Outcome.
12. **Passes:** implement, review for bugs and edge cases, then re-check against this brief.

## Session 2026-10-29 outcome (summary)
- Restored all 30 pinned inputs and the nine focus files by SHA-256 (sources: owner's GitHub repos at pinned refs). Test suite: 275 passed before the new regression file.
- No file is cleared for submission. Download for review: H51-1 EWSP (`-zeros.tif`). Best already-submitted: GEMSDOE32 `h33-h33-2-b2` (OWNER-REPORT 0.2778).
- Findings and blockers are in `docs/nine-site-verified-summary.html` and `registry/irregularities.json` (IR-20261029-V01 to V08).

## Open items and decisions (end of 2026-10-29 session)
- **Experiment budget (decision):** the three experiments already run count against the 3-experiment / 2-hour budget: (1) the nine-site verifier, (2) the H51-1 holdout, (3) the projection and association analysis. **Budget spent for this session.** No new experiment should start without a new session or owner approval.
- **H51 EXP1 reproduction: NOT RUN.** `scripts/run_h51_ewsp.py` needs `.cache/gems_work/feature_stack.npy` and `ewsp_labelfree_10ch.npy`. Neither exists in this workspace. Rebuilding them is a fourth experiment, and the script writes into `docs/downloads/`. The sha256 of the on-disk file (`f66f65e4…`) matches the pinned value, and the strict validator passed. That is the verification performed.
- **Leakage canary on the H51 file: NOT RUN.** The only feature-level canary available (`evidence/arena8a_exp1_canary_and_domains.json`, 57 channels, worst AUC 0.622, 2026-10-26) covers features, not this emitted file, and it needs the rebuilt stack. Scoring the file's pixels against holdout truth would measure skill, not leakage. **Owner or next session must run the canary before any slot consideration.**
- **Submission slots: none picked.** Promotion is a separate selector step within the weekly cap on the submission page.
- **Owner decisions needed:** literal r13 rule (IR-20261029-04, -V04); data-use terms for the public competition-data mirrors (IR-20261029-V06); confirm the leaderboard figures (IR-20261029-V05); correct the stored H51 note (IR-20261029-V07).
