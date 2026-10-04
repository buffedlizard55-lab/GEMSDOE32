# GEMSDOE32 — an auditable fault-discovery system for the DOE GEMS Prize (DrivenData #306)

> **Maximize P(Win)** · **Own the Outcome** — the Arena core values are the decision rule for every
> change in this repository.

**Competition:** [DOE GEMS Prize, DrivenData #306](https://www.drivendata.org/competitions/306/competition-doe-gems/)
· **Live site:** <https://buffedlizard55-lab.github.io/GEMSDOE32/> · **Metric page:**
[page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
· **Weekly limit:** 3 scored submissions, one file scored in **both** prize rounds.

---

## ⬇ One-click submission GeoTIFF

The site's home page puts the download first; the same file is in this repository at
`docs/downloads/`. Build it yourself with `scripts/build_submission.py` (nothing is hand-edited).

| file | what it is | status |
|---|---|---|
| `docs/downloads/gems32-cover-r1-h19-5-d2-8-eq-mass.tif` | single-band float32 GeoTIFF, EPSG:32611, 100 m, 3730×3292, every footprint pixel finite in [0, 1], NaN outside | **format-validated by independent re-read; unscored; not slot-approved** |
| `…-zeros.tif` | identical predictions, `0.0` outside the footprint | format fallback |
| `checks-<file>.json` | sha256, counts, min/max, range and footprint assertions | receipt |

The system that produced it, in one paragraph: the official metric is re-implemented exactly
(`src/gems32/metric.py`), reduced to the identity `DTI = T/(0.2(T+S−M)+0.8K)` and the marginal
**credit bar** `k > 0.2·DTI`; emission is a greedy maximum-expected-coverage packing of a detector
field under the metric's own kernel with that bar as the stopping rule; the rule is measured against
the incumbent at *matched emitted mass* on a spatially blocked hide-and-recover holdout
(`scripts/run_holdout.py`, preregistered before the run); and a Gaussian-process surrogate with
expected improvement decides whether a candidate has earned one of the three weekly slots
(`src/gems32/bo.py`).

---

## Standing prompt (read first, every session)

The full owner brief, preserved verbatim. It is the project's starting point and its acceptance
criteria.

> ```
> Review the repo.
>
> There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.
>
> Treat each weekly submission as an expensive query in a formal search, not a free trial. With at most three scored submissions a week and one slot that counts for both prize rounds, a live submission is a rate-limited, costly observation next to the unlimited cheap evaluations available on the local holdout — exactly the asymmetry Bayesian optimization exists for. Fit a probabilistic surrogate (a Gaussian process is the standard choice) over holdout DTI as a function of each candidate's design choices, and spend a real submission only when an acquisition function like expected improvement says the surrogate's uncertainty about beating the current best justifies the cost — turning "don't spend a slot on an idea that hasn't beaten holdout," already a rule here, from a one-time gut check into a running decision rule that also says what to try next. Log every holdout evaluation, submitted or not, as data for that surrogate, and treat any persistent gap between what the surrogate predicts and what the leaderboard returns as evidence the holdout itself has drifted from the live scoring distribution — a finding worth chasing, not noise to shrug off.
>
> Here are the results from submissions into the competition, separated by ....: [the group's
> per-repository score ledger, GEMSDOE .. GEMSDOE30, reproduced in the family registry — every entry
> is an owner report, not an organizer receipt]
>
> WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE
> SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:
> https://buffedlizard55-lab.github.io/GEMSDOE25/
> dotted-h19-5-d2-8-20261002-e56ea318af89-nan: 0.2600
>
> Why and how did this get the highest score and are we able to generate a submission that scores
> higher than 0.26? Answer the question using Phd level experience, knowledge, and judgement.
>
> The following is the leaderboard for the competition:
> https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/
> 0.3195 is the highest score right now so we need to design a new strategy, research, testing,
> analyzing, and generating submission system than the current website. It should be unique, take
> unique approaches to generating a submission that can score higher than 0.3195.
>
> Put this prompt into the repo readme and read it everytime we work on the project as a starting
> point to make sure we are building what we are aiming for and have a strong base to continue
> building and improving on making something useful for everyday use. It should solve the problem of
> having to manually check everything ourselves and having an up to date current feed.
>
> The following is taken from the Arena AI team and I think it makes a good point on building a
> successful project, so let's keep the Core Values and Own the Outcome as a focal point when
> building, developing, researching, suggesting upgrades, and implementing the work.
>
> Our Core Values — Maximize P(Win). "Maximize the Probability of Winning": our decision making
> framework. In every decision, we weigh tradeoffs, assess risk, and choose the path that maximizes
> the probability that Arena succeeds. We set aside our emotions and make tough decisions in order to
> maximize P(Win). "Maximize P(Win)" frees us from constraints and clarifies that we must put Arena
> first. — Own the Outcome. We own results end to end — not just our individual slice of the work.
> When problems arise and we have the means to act, we do so without waiting for permission or
> assignment. We treat failure and success as signals and use them to improve. At Arena, we stay
> accountable to the final outcome.
>
> Work line by line verifying from official verified trusted sources, provide links for manual
> review. There should be no manual input, work on your own to complete tasks. Flag any
> irregularities for review. No hallucinations.
>
> Verify no hallucinations. The goal of this project is to get a full list that follow our
> requirements. No hallucinations. Verify line by line.
>
> We need to focus on being able to generate a submission into the competition. The site should be
> able to generate a TIF file that is required for submission. It should be as easy as download to
> click a File to submit into the competition. This needs to be in the executive summary or the very
> beginning of the site. it should be obvious when you visit the site.
>
> I tried to submit the document that i downloaded from the site but it returned this error on the
> submission form: "Predicted values must be in range [0, 1]". Also we need to give it a unique name
> and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25.
>
> [the DrivenData submit form verbatim: "You can submit a single-band GeoTIFF (.tif) file, or a .zip
> file containing a single GeoTIFF, with your predictions. It must match the submission format's CRS,
> shape, and geotransform." …]
>
> Create a executive summary subpage that explains exactly how to make a submission into the contest.
>
> Work on the next steps from the previous sessions first.
>
> The goal of this project is to place top of the leaderboard in this competition. We need to create
> a project that can compete and place top of the leaderboard. We need to understand the problem,
> collect all the data and organize it into a clean easily auditable table with official verified
> links for manual verification. [guidelines: overview page, about page, download the data, create and
> train your own model, the official reference solution, generate predictions matching the submission
> format] Tell me what are you limitations and what you need access to during this project. We will
> need to find free publicly available sources and data from official and verified sources if we are
> to use 3rd party or external data.
>
> this pdf outlines how submissions must be entered into the competition.
> https://docs.nlr.gov/docs/fy26osti/96647.pdf
>
> You must be able to do your own research, deep research, scientific literature research and
> organize the knowledge so that we can critically think through the problem and generate a solution
> through scientific and free publicly available information. this must be done autonomously and must
> be constantly reviewed and improved upon. Provide suggestions and improvements and implement them.
>
> ❌ No DrivenData auth → cannot auto-download training_features.tif, labels.tif, sample_submission.tif,
> 1m_DEM_links.csv from the data page (verified redirect to login). See below for links from the
> above site. [the owner's mirrored Dropbox links]
>
> Site creation: Create a github page for this repo that has clean ui, user friendly, simple and
> easy to use. It should be organized and clean. It should include all relevant information in an
> easy to read format with official verified links as sources for review. Work line by line verify
> everything no hallucinations.
>
> The single remaining blocker to training is data placement: run `bash scripts/download_competition_data.sh`
> on any unrestricted machine into `data/`, then `python scripts/prepare_data.py` — after that the
> full train→inference→validate pipeline is ready to run (GPU needed for training; metric/losses/
> validation all verified working here on CPU).
>
> you need to complete the above task by yourself. Work line by line verifying from official
> verified trusted sources, provide links for manual review. There should be no manual input, work on
> your own to complete tasks. Flag any irregularities for review. No hallucinations. Verify no
> hallucinations. The goal of this project is to get a full list that follow our requirements.
> No hallucinations. Verify line by line.
>
> Run this task through multiple passes. Pass 1: Implement the task completely and verify the result.
> Pass 2: Review your work for bugs, missing requirements, incorrect assumptions, and edge cases.
> Fix everything you find. Pass 3: Re-check the entire implementation against the original request.
> Improve accuracy, reliability, completeness, and code quality. Fix any remaining issues. Do not
> stop after the first pass. Each pass must build on the previous one. Before finishing, verify that
> the final result fully satisfies the original request. Work line by line verify everything no
> hallucinations.
>
> Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions
> for what work still needs to be done and any limitations that is in the way of a successful
> project. It should be worked on in this next session or the next session. Work line by line verify
> everything no hallucinations.
> ```

### Standing constraints extracted from the brief

1. Verify line by line from official, trusted sources; give links for manual review; flag
   irregularities; never present a proxy or an owner report as an organizer-verified result.
2. Work autonomously: no manual inputs, no credentials.
3. The site must make a one-click submission GeoTIFF obvious at the top, with a unique name and a
   short note for the submit form, and an executive-summary subpage explaining the exact upload.
4. Do not spend a weekly slot on an idea that has not beaten the best comparable spatially blocked
   holdout — and make that a *running* decision rule with a surrogate and an acquisition function.
5. Log every holdout evaluation; treat a persistent surrogate-vs-leaderboard gap as holdout drift.
6. Keep the Core Values central: **Maximize P(Win)** and **Own the Outcome**.
7. Run multiple review passes and verify against the original request before finishing.
8. Keep large datasets out of Git; use hash-pinned provenance and label owner mirrors as
   unauthenticated.

---

## Repository map

```
src/gems32/
  metric.py       official distance-weighted Tversky index + the identity + the credit bar (verified)
  grid.py         geometry/footprint/IO and the independent format validator
  emission.py     dot-thin (incumbent), greedy max-expected-coverage packing, credit-bar stopping
  features.py     35-channel structural stack from the 19 official bands (+ derived transforms)
  detector.py     CPU-feasible detectors (HistGradientBoosting / logistic) for harness work
  holdout.py      preregistered spatially blocked hide-and-recover harness, arm ladder
  bo.py           GP surrogate, expected improvement, cost-aware slot gate, drift report
  submission.py   writer (+zip) and receipt
  feed.py         live feed (sources, leaderboard snapshot, build state)
  hypotheses.py   the five registered candidate hypotheses
scripts/          fetch_data, build_features, run_holdout, build_submission, build_site, refresh_feed
registry/         sources, data manifest, leaderboard history, irregularities, hypotheses, preregistration
evidence/         raw run outputs (JSON) — every number on the site comes from here
docs/             the GitHub Pages site (generated) and the downloadable GeoTIFFs
tests/            metric, emission, grid, bo, submission
```

### Reproduce everything from a clean checkout

```bash
pip install -r requirements.txt
python3 scripts/fetch_data.py          # hash-verified fetch of the pinned mirrors (GitHub API)
python3 scripts/build_features.py      # ~3 min on 2 vCPU: 35-channel stack (~1.7 GB memmap)
python3 scripts/run_holdout.py         # preregistered blocked holdout, writes evidence/holdout_run1.json
python3 scripts/build_submission.py    # writes docs/downloads/*.tif + checks JSON
python3 scripts/build_site.py          # regenerates the site from the registry
python3 -m pytest tests -q
```

## Where the system stands

* **The exact metric, verified.** `tests/test_metric.py` reproduces the published worked example
  (TPw=3.00, FPw=1.89, FNw=2.00 → 0.60) and checks the identity and the credit bar against a
  brute-force transcription of the published formulas on random rasters.
* **The credit bar is the decision rule.** `dDTI > 0 ⇔ k > 0.2·DTI`: 0.052 at the group's best
  (0.26), 0.065 at the current public leaderboard #1 (0.3262, read 2026-10-04). The group's own
  measured credit rate (0.0548 per added dot) sits on that bar.
* **A validated emission rule, at matched mass.** `evidence/holdout_run1.json` compares greedy
  max-expected-coverage packing with the incumbent raster-order dot-thin cascade at the same emitted
  count, on four spatially blocked folds, with the official metric.
* **A slot gate with a cost model.** `bo.slot_gate` refuses a submission unless the candidate beats
  the incumbent on the holdout *and* the surrogate's expected improvement clears the slot cost; the
  two-round objective (`DTI_1 + ρ·DTI_2`) lowers the bar only for candidates with a plausible path to
  expert verification.
* **A live feed.** 19 official sources with links and last-observed status, the public leaderboard
  snapshot history, and the repository's own build state — so nothing has to be checked by hand.

## Limitations (stated, not hidden)

* The competition rasters here are **owner mirrors, not organizer bytes** (IR-32-DATA-01).
* Every live score in the family record is an **owner report** (IR-32-SCORE-01); the only verified
  scores are the *other teams'* rows read from the public leaderboard.
* The holdout truth is the **visible catalogue**, which structurally cannot reward a prediction that
  is off-catalogue — exactly the population the real test set is drawn from (IR-32-PROXY-01).
* No GPU here, so the detector used in the harness is a CPU GBDT, not the U-Net of the official
  reference solution; the harness validates *emission rules*, and says so.
* The `[0, 1]` rejection is explained from the data, not from a public validator (IR-32-VERIFY-01).

## Sources

Every source is listed with its role and verification status in
[`registry/sources.json`](registry/sources.json) and rendered at
<https://buffedlizard55-lab.github.io/GEMSDOE32/sources.html>.
