# GEMSDOE32 — DOE GEMS Prize research and submission tooling

## Current decision — 2026-10-26 review: **DO NOT SUBMIT ANY FILE**

The existing Round-6 STEP GeoTIFF is retained **for audit only**, not as an upload-ready
submission: [`gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif`](docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif)
(SHA-256 `c7f094c1f4d00f2dd9a056dc80fecc94bf1d636363acd020c9da3659eae56547`). A local byte read
confirms a single-band float32 raster, EPSG:32611, 3730×3292, values 0–1 and 37,654 positive cells. Exact strict comparison against the pinned owner-mirror
`sample_submission.tif` now passes (SHA-256 `2176d08e…54d35cbc`). This is **format evidence only**,
not scientific/uniqueness approval or organizer acceptance.

**Why it is not cleared:** the candidate was placed using a B=2 exclusion derived from the full
fault catalogue, then scored against hidden catalogue segments. The evaluator did not recompute
that catalogue-derived exclusion from each fold's visible faults, so the result has held-out-label
leakage and is not an admissible hide-and-recover comparison. The recorded **[HOLDOUT-DTI, leakage-affected/inadmissible]** is 0.00338 vs incumbent 0.00452 (evaluator `gems32.holdout` draws 20/21; 22,232 withheld positives; separate 95% CIs [0.00251, 0.00453] and [0.00394, 0.00525], not a paired interval); the point estimate is lower. In addition, 97.82% of its dots are within 3 px of a
registered calibration raster, exceeding the literal 70% duplicate threshold. The earlier
promotion improperly excluded this raster from the gate. Full findings: [three-pass repo review](docs/research/protocol-review-20261026.md), [run card](evidence/round6_run_card.json).

**No new raster was generated during this review.** The ignored source/cache files and cached feature
stack required for a valid fresh evaluation are absent. No weekly slot was used. Do not upload the
STEP artifact, the prior GEO-CONDUIT artifact, or any other checked-in raster based on this README.
The supplied historical values (0.2778 for the H33-2-B2 file and conflicting leaderboard values 0.3195/0.4413) are **[OWNER-REPORT / user-provided]**, not organizer-confirmed here; there is no submission receipt or current authenticated leaderboard
snapshot in this checkout. They are not holdout scores or predictions for a new submission.

**Competition links:** [official overview](https://www.drivendata.org/competitions/306/competition-doe-gems/) · [problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) · [official reference solution](https://github.com/drivendataorg/gems-prize-reference-solution) · [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) · [GDR 1391](https://gdr.openei.org/submissions/1391) · [EPSG:32611](https://epsg.io/32611).

> **Maximize P(Win)** — choose experiments by evidence, not optimism. **Own the Outcome** — correct misleading status claims and report negative results.

---

> ### 📋 STANDING PROJECT BRIEF (operational digest; not a verbatim transcript — read every session)
>
> Review the repo. 
> 
> I want to focus on  the highest scoring submissions from the following sites, GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36.
> 
> THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!
> 
> MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION.  DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION.  BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION.  IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.
> 
> There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.  A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.
> 
> PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.
> 
> 1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.
> 
> 2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_holdout.py and submission_writer.py. Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.
> 
> 3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.
> 
> 4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.
> 
> 5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.
> 
> 6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.
> 
> The following sites should serve as a starting point for understanding how to generate TIF submissions...
> 
> WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
> https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html
> h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778
> 
> Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?
> Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition.  Must be unique submission unlike any within the GEMSDOE sites above.  Verify working line by line no hallucinations.
> 
> Current competition leaderboard GEMSDOE high score: 0.4413
> 
> Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.
> 
> Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.
> 
> I tried to submit the document that i downloaded from the site but it returned this error on the submission form: "Predicted values must be in range [0, 1]"
> Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25
> Create a executive summary subpage that explains exactly how to make a submission into the contest.
> Create a github page for this repo that has clean ui, user friendly, simple and easy to use.  It should be organized and clean.
> The single remaining blocker to training is data placement: run `bash scripts/download_competition_data.sh` on any unrestricted machine into `data/`, then `python scripts/prepare_data.py` — after that the full train→inference→validate pipeline is ready to run.

---

## Research notes and current next steps

### How to interpret the reported 0.2778

The supplied history labels `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` as 0.2778. This is an **OWNER-REPORT** in this checkout, not a score bound to the file by an organizer receipt. The locally recorded byte-family analysis describes a nested H19-5 → D2.8 → B=1 → B=2 sequence. If the reported score/file pairings and construction are correct, thinning and exclusion can improve a distance-weighted Tversky objective by dropping mass whose expected marginal credit is below its false-positive cost. This is a plausible metric mechanism, not proof of hidden-fault causation or generalization.

The request itself gives conflicting leaderboard values, 0.3195 and 0.4413. Neither is independently refreshed here; neither should be presented as a current official value or used to make a score projection. A new method can beat a reported baseline in principle, but this repo currently has no admissible evidence that one does.

### Focus-site executive summary

The complete per-site table for GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, and GEMSDOE36 is in [the focus-site executive summary](docs/research/focus-sites-executive-summary.md). Its historical scores are labelled OWNER-REPORT and every prior file is audit-only. Do not reuse a prior raster as a submission.

### Hypotheses and experiment discipline

The five ranked geological hypotheses, target bands/transforms, rationale, named mimics, and cost notes are in [Round-6 preregistration](docs/research/hypotheses-round6.md). The earlier R6-1 signed `det_elev` step-vs-ramp concept is not cleared: the B=2 exclusion used full-catalogue labels before holdout scoring, and final dots fail the literal registry overlap limit. Candidate hypotheses are not expected score gains. R6-2/R6-3 require source data and the actual feature stack; R6-4 needs the official [USGS FDSN event service](https://earthquake.usgs.gov/fdsnws/event/1/); R6-5 needs [USGS 3DEP](https://www.usgs.gov/3d-elevation-program). External hosts are not reachable in this sandbox and those data were not fetched.

### Upload checklist (only after a future explicit approval)

The current status is **DO NOT SUBMIT ANY FILE**. If a future run receives a green `OK TO DOWNLOAD AND SUBMIT` verdict after all gates pass:

1. Use the exact artifact named in the current release banner and verify its SHA-256 against the run card.
2. Open the [DrivenData DOE GEMS submission page](https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/) and select the GeoTIFF or ZIP only if the banner explicitly authorizes upload.
3. Copy that run's unique submission name and note (≤140 characters) exactly; do not reuse names or notes from archived runs.
4. Submit through the competition form. The project does not automatically upload, consume a weekly slot, or claim organizer acceptance from local validation.

## Key links

- [Official competition overview](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [Official problem description and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — not authenticated/refreshed in this review
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR INGENIOUS submission 1391](https://gdr.openei.org/submissions/1391)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)
- [Tversky index reference](https://en.wikipedia.org/wiki/Tversky_index)

See [protocol review](docs/research/protocol-review-20261026.md) for three-pass findings, evidence labels, current limitations, and the test record. Read `docs/research/standing-brief-20261025.md` before each project session; it is an operational digest, not the verbatim original user prompt.
