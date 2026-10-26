# GEMSDOE32 — DOE GEMS Prize research and submission tooling

## Current decision — 2026-10-26

# 🔴 DO NOT SUBMIT the current Round-6 candidate

The file below is a real, uniquely named GeoTIFF and its bytes pass the recorded format/range checks. **That is not enough to authorize a competition upload.** This review found that the assigned method paragraph is absent and that the previous candidate's B=2 mask was derived from the full catalogue before hide-and-recover evaluation. The run therefore does not demonstrate the required fold-local, visible-fault-only feature construction. Its promotion gate relied on an external SGMC comparison, while the recorded catalogue hide-and-recover result did not beat the incumbent.

- **Audit artifact only (not upload-authorized):** [`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif)
- SHA-256: `c7f094c1f4d00f2dd9a056dc80fecc94bf1d636363acd020c9da3659eae56547`
- Automated byte check in this review: single-band float32, EPSG:32611, 3730×3292, all 12,279,160 cells finite, range [0,1], nodata unset, 37,654 positive cells.
- **Grid caveat:** the competition template is not present in this checkout, so the previous exact-template geometry comparison could not be rerun from source data in this review.
- No new submission slot was used. No organizer score is claimed for this candidate.

The full audit and blockers are in [`docs/research/repo-review-20261026.md`](docs/research/repo-review-20261026.md), the session review card is [`evidence/review_run_card_20261026.json`](evidence/review_run_card_20261026.json), and the machine-readable decision is [`evidence/current_release_review.json`](evidence/current_release_review.json). The historical Round-6 evidence remains preserved at [`evidence/round6_run_card.json`](evidence/round6_run_card.json); it is not the current release authorization.

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

See the detailed operational digest at [`docs/research/standing-brief-20261025.md`](docs/research/standing-brief-20261025.md). The current session review documents that the lane was absent, so no new experiment or submission authorization was issued.

## Repository map

- [`docs/index.html`](docs/index.html) — GitHub Pages landing page.
- [`docs/executive-summary.html`](docs/executive-summary.html) — submission-status / format guide; currently fail-closed.
- [`docs/research/repo-review-20261026.md`](docs/research/repo-review-20261026.md) — this repository review, per-site interpretation, protocol findings and ranked next hypotheses.
- `src/gems32/` — scoring, holdout, candidate, release and GeoTIFF utilities.
- `scripts/` — research runs, validators and site generation.
- `registry/` — provenance, source, score-claim and submission metadata.
- `evidence/` — immutable experiment records and current release review.
- `docs/downloads/` — historical and current audit artifacts; presence is not upload authorization.

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

Competition data access requires the user's DrivenData login and is not present in this checkout. Restore the hash-pinned data/cache before rerunning any holdout or exact-grid validator. Never spend a competition slot based only on this repository's local proxy metrics.

## Official references

- [DOE GEMS Prize overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official rules PDF (NLR/DOE)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS data repository record](https://gdr.openei.org/submissions/1391)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index](https://en.wikipedia.org/wiki/Tversky_index)
