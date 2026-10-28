# Standing request — 2026-10-28

Read this, README, and the current review at the start of each session. This is a **condensed operative record**, not a verbatim reproduction of the long, duplicated conversation prompt. The conversation remains authoritative; prior recorded prompts and score ledgers are preserved.

## Mission

Build a reproducible, scientifically grounded DOE GEMS fault-prediction system that improves the chance of a top competition result. Focus on GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33 and GEMSDOE36, using the other listed projects for historical comparison rather than copying their submissions.

**Highest urgency:** generate a genuinely unique, validated single-band submission TIF—not a renamed, repackaged, noisy or otherwise cosmetically different previous submission. Make the download and its exact upload authorization obvious at the beginning of the site and in an executive-summary subpage. Show filename, any defensible score estimate (otherwise unavailable), uniqueness, validator evidence, unique submission name and a note of at most 140 characters. Prevent the portal error “Predicted values must be in range [0, 1]”.

## Parallel-run constraints

1. Stay in the explicitly assigned single method lane. The current prompt does not identify that paragraph; do not assume a previous lane is assigned again. Rank correlation above 0.90 or more than 70% of candidate dots within 3 pixels of any registry reference means duplicate: log and stop. Check full surface before placement and final dots afterward. No silent dense-reference exemptions.
2. Reuse the shared cached features, `scripts/evaluate_holdout.py`, `scripts/submission_writer.py` and the canonical modules. Fix shared bugs once, not in private forks. Hide whole fault segments with buffers; derive catalogue-based features only from visible faults; mask visible fault pixels exactly; evaluate pooled DTI with alpha 0.2, beta 0.8 and the 300 m triangular kernel.
3. Performance evidence must be HOLDOUT-DTI (evaluator, withheld-positive count, 95% CI) or ORGANIZER-CONFIRMED (submission-page receipt). Unverified supplied claims may be retained as clearly unconfirmed claims, never promoted to confirmed results. A projection is never a score.
4. Test every feature alone on holdout. AUC above 0.90 is a leakage alarm until explained.
5. End with one JSON run card: hypothesis, mechanism, named non-fault mimic, holdout/CI, registry correlation/overlap, raster SHA-256, exact saved-byte validation, submission name/note and promote/negative verdict. Negative results are deliverables.
6. Stop after three experiments or two hours. Promotion to an actual weekly slot is a separate selector step within the authenticated current cap. Never use a slot for a candidate that has not beaten the current best on the same holdout instrument.

## Scientific and engineering duties

- Review prior next steps first. Explain why H33-B2 has the best supplied historical claim without inventing hidden labels or score causes. The prompt's competing leaderboard maxima are not a current verified leaderboard.
- Before a new model, propose three to five untried hypotheses: specific layers, transform/signature, why missing-catalogue faults might respond, novelty versus inspected code, non-fault mimic, expected qualitative benefit and cost. Validate the top candidate on spatially blocked holdout. Name and check obtainable free official sources before declaring any new external-data idea viable.
- Research geothermal-relevant faults while distinguishing them from verified vents/reservoirs. Keep an auditable knowledge base and source links, indicating exactly which sources were actually fetched.
- Automate inspections, gates and status reporting. Do not replace absent evidence with “human inspector required”; return a precise automatic blocked/negative result. Do not bypass legitimate separate slot selection.
- Use a clean GitHub Pages interface with individual summaries for all focus sites. Do not imply that files in this repository also update sibling websites.
- Preserve large rasters/caches using existing ignored storage conventions. State data, network, authentication and compute limitations honestly. GPU availability is not automatically a training prerequisite.
- Make three passes: implement and verify; find/fix bugs and edge cases; recheck against the request and test again. Open a PR from the fixed session branch and merge when verified. Record unfinished work and limitations for the next session.

## Core values

**Maximize P(Win):** choose the path most likely to improve the real objective; protect scarce competition slots rather than optimizing a misleading proxy or claiming success without evidence.

**Own the Outcome:** own data provenance, scientific validity, reproducibility, file format, release decision and publication end to end. Treat failures as evidence; fix what can be fixed autonomously and expose unresolved constraints.
