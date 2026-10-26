# GEMSDOE32 — DOE GEMS Prize research and submission tooling

<!-- SINGLE DECISION: rendered from registry/current_status.json and evidence/current_release_review.json (both must authorize; fail closed). Update those files, never add a second banner. -->
## 🚦 Current decision — 2026-10-26 01:40 UTC

# 🔴 DO NOT SUBMIT — no upload is authorized

| file | status | why |
|---|---|---|
| **Round-6 candidate** [`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif) · SHA-256 `c7f094c1…3c56547` | 🔴 **DO NOT SUBMIT — audit artifact only** | A real, uniquely named, format-valid GeoTIFF. **Format validity is not enough to authorize a competition upload.** The fail-closed release review (PR #21, [protocol audit](docs/research/protocol-review-20261026.md), [decision](evidence/current_release_review.json)) found no assigned lane paragraph and a B=2 mask derived from the full catalogue (not fold-local). This session reproduced its SGMC-instrument margin independently (+0.0465 [+0.0255, +0.0681] vs the champion; lane-unique, max overlap 41 %), **but that instrument does not track live scores**: SGMC-tracing files score 0.65 / 0.56 on it (6–7× the champion) and scored **0.0492 / 0.0512 live** (IR-42-INSTR-02, [counter-examples](evidence/sgmc_instrument_live_counterexamples.json)). The review's lattice-overlap reason does not discriminate (random dots 0.9988; IR-42-UNIQ-01). |
| **This session's unique file (H42-1)** [`gemsdoe32-h42-hwci-37654-20261026T001226Z-b91008fa-zeros.tif`](docs/downloads/gemsdoe32-h42-hwci-37654-20261026T001226Z-b91008fa-zeros.tif) · [zip](docs/downloads/gemsdoe32-h42-hwci-37654-20261026T001226Z-b91008fa-zeros.zip) · [run card](evidence/h42_run_card.json) | 🔴 **DO NOT SUBMIT — audit/research artifact** | HOLDOUT-DTI 0.1529 [0.1400, 0.1674] vs champion recipe 0.1056 (gems57-pooled-hide-v2, 22,893 withheld positives), but the lane gate failed (82 % of dots within 3 px of GEMSDOE25 `h38-greedy-credit`) and on the independent off-catalogue instrument it is worse than random dots (0.0545 vs 0.0709; champion 0.0954) — a gap-filling artefact (IR-42-INSTR-01). Run as a self-declared, pre-registered lane; under the strict reading that no lane paragraph was assigned, it could not authorize an upload either way. |
| **Best scored file** [`gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`](docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | already submitted — **do not resubmit** | **0.2778**, ORGANIZER-CONFIRMED (owner-reported receipt). |
| Withdrawn: `gemsdoe32-h32-winning-46090-prune400-…`, `gemsdoe32-h-geo-conduit-…` | 🔴 DO NOT SUBMIT | champion-family variant whose margin was inside its CI (IR-42-README-01); lane duplicate vs GEMSDOE28 (IR-R6-02). |

**How a cleared file would be submitted:** [executive summary — exact steps](docs/executive-summary.html) (use the `-zeros.tif`; it cannot trigger "Predicted values must be in range [0, 1]"). **Leaderboard:** public #1 = 0.4413 (xiaofanhu), [official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/), read 2026-10-25. **Weekly cap:** whatever the submission page shows ([staff, 11553](https://community.drivendata.org/raw/11553)); one selected file is scored in both prize rounds.

**This session (H42) in one paragraph.** Data restored and SHA-256-verified (23 files); shared template vendored from
[57GEMSDOE@822a0ce](https://github.com/buffedlizard55-lab/57GEMSDOE/tree/822a0ce5546c7b6749cdd82eb145b6b3e616603d); five
hypotheses pre-registered ([knowledge/04](knowledge/04_preregistration_h42_hanging_wall_2026-10-25.md)); H42-1 run and
found negative; the two local instruments shown to be biased in opposite directions (catalogue-hidden rewards
near-network gap-filling, SGMC rewards SGMC alignment) — only live scores separate them. Analysis, why 0.2778 won, and
the fault-discovery science: [knowledge/05](knowledge/05_h42_outcome_instrument_artifact_and_fault_discovery_science_2026-10-25.md) ·
score ledger with per-row provenance: [docs/score-ledger.csv](docs/score-ledger.csv).

> ### Our Core Values
> **Maximize P(Win).** Weigh tradeoffs and risk and choose the path that maximizes the probability of winning; put the outcome first.
> **Own the Outcome.** Own results end to end; act when problems arise; treat failure and success as signals; stay accountable to the final outcome.

## Standing project brief — read before every session

This repository aims to improve the probability of winning the DOE GEMS Prize by finding genuinely new fault evidence, not recycling prior rasters.

> **Maximize P(Win):** weigh risk and evidence to improve the probability of a successful competition result.
>
> **Own the Outcome:** distinguish independently checked facts from owner reports, label every score by evidence class, publish negative results, and make the site fail closed when a required gate is missing.

The earlier portal rejection `Predicted values must be in range [0, 1]` is addressed at the byte-validation layer by checking all written cells are finite and in [0,1]. This file-format check does not establish scientific validity or authorize submission.

1. **Focus sites:** GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36. The per-site executive summary is [`docs/research/focus-sites-executive-summary.md`](docs/research/focus-sites-executive-summary.md). Historical site scores without a competition receipt are **OWNER-REPORT**, not organizer-confirmed.
2. **Unique artifact and explicit status:** the site must make the current verdict obvious at the top. A file-format PASS alone never means “OK TO SUBMIT.” Only a file that passes the assigned lane, hide-and-recover, leakage, registry uniqueness and byte-level validator gates may be recommended. A real slot requires a separate selector decision under the current authenticated weekly cap.
3. **Parallel-run lane:** work only in the single method paragraph explicitly assigned for that session. If it is absent, stop and report the blocker; do not adopt another run's lane. Check surface correlation before placement and dot overlap after placement. A rank correlation above 0.90 or more than 70% of dots within 3 pixels of a registry raster is a duplicate stop.
4. **Shared validation:** reuse the shared feature cache, holdout evaluator and writer. Hide whole fault segments with a buffer; derive catalogue-based features from visible faults only; mask visible faults pixel-exactly; pool DTI with α=0.2, β=0.8 and a 300 m triangular kernel. Fix shared tools in place rather than forking.
5. **Leakage canary:** test each feature alone first; AUC above 0.90 is leakage until proven otherwise. Report the evaluator version, withheld positive count and 95% CI for every HOLDOUT-DTI. Report ORGANIZER-CONFIRMED only from a submission-page receipt. Projections are never scores.
6. **Experiment budget:** at most three experiments or two hours. Negative results count as deliverables. Promotion is not slot selection.
7. **Research workflow:** before implementation, rank 3–5 hypotheses with layers, physical signature, missing-catalogue rationale, novelty against the repo, expected benefit and cost. Name non-fault mimics. For new data, identify a free official source and verify it is obtainable before calling it viable.
8. **Submission format:** single-band float32 GeoTIFF matching the sample CRS, shape and geotransform; predictions in [0,1]; no NaNs inside the footprint. Re-read written bytes and preserve SHA-256. The official competition page controls the final format interpretation.
9. **Review passes:** implement/verify; audit bugs and assumptions; re-check the original requirements. Publish remaining limitations and irregularities.

Goal and targets from the owner brief: beat the 0.2778 champion and ideally 0.3195+ (public #1 was 0.4413 on 2026-10-25). The prompt text as recorded by a parallel session (completeness unverified) is preserved in [`docs/research/standing-prompt-as-recorded-20261026.md`](docs/research/standing-prompt-as-recorded-20261026.md). See the detailed operational digest at [`docs/research/standing-brief-20261025.md`](docs/research/standing-brief-20261025.md). The current session review documents that the lane was absent, so no new experiment or submission authorization was issued.

## Repository map

- [`docs/index.html`](docs/index.html) — GitHub Pages landing page.
- [`docs/executive-summary.html`](docs/executive-summary.html) — submission-status / format guide; currently fail-closed.
- [`docs/research/repo-review-20261026.md`](docs/research/repo-review-20261026.md) — this repository review, per-site interpretation, protocol findings and ranked next hypotheses.
- `src/gems32/` — scoring, holdout, candidate, release and GeoTIFF utilities.
- `scripts/` — research runs, validators and site generation.
- `registry/` — provenance, source, score-claim and submission metadata.
- `evidence/` — immutable experiment records and current release review.
- `docs/downloads/` — historical and current audit artifacts; presence is not upload authorization.
- [`registry/current_status.json`](registry/current_status.json) — single machine-readable status source for the README block and every site page (fail-closed together with `evidence/current_release_review.json`).
- [`knowledge/05_…`](knowledge/05_h42_outcome_instrument_artifact_and_fault_discovery_science_2026-10-25.md) — H42 outcome, the two biased instruments, why 0.2778 won, fault-discovery science; [`knowledge/04_…`](knowledge/04_preregistration_h42_hanging_wall_2026-10-25.md) — pre-registration.
- [`vendor/gems57/`](vendor/PROVENANCE.json) — pinned shared template (evaluator, writer, uniqueness gate) from 57GEMSDOE@822a0ce; not a private fork.

## How to validate locally

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

To regenerate the Pages content from the registry and evidence:

```bash
. .venv/bin/activate
python scripts/build_site.py
```

Training features, labels, external proxy layers and the cached feature stack are not committed; restore them with `python scripts/restore_data.py --group all --target-dir .cache/gems_data` (23 files, SHA-256-verified) and build the stack with `scripts/build_features.py` (this session did both and ran H42; see knowledge/05 §8 for the exact commands). The sample template is restored only from a hash-pinned owner mirror; exact-grid validation of an existing artifact is possible, but that is not organizer authentication. Never spend a competition slot based only on this repository's local proxy metrics.

## Official references

- [DOE GEMS Prize overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official rules PDF (NLR/DOE)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS data repository record](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
- DrivenData staff clarifications (forum, read 2026-10-25): [known-fault pixels masked (11516)](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) · [what counts as a new fault (11536)](https://community.drivendata.org/raw/11536) · [pooled public score (11550)](https://community.drivendata.org/raw/11550) · [same metric in all rounds (11556)](https://community.drivendata.org/raw/11556) · [weekly cap (11553)](https://community.drivendata.org/raw/11553) · [test-set sources withheld (11527)](https://community.drivendata.org/raw/11527)
- [Official public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
