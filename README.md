# GEMSDOE32 — an auditable fault-discovery system for the DOE GEMS Prize (DrivenData #306)

**Competition:** [DOE GEMS Prize](https://www.drivendata.org/competitions/306/competition-doe-gems/)
· **Metric page:** [page 967](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
· **Live site:** <https://buffedlizard55-lab.github.io/GEMSDOE32/> · **Weekly budget:** 3 scored
submissions, and exactly one file is scored in **both** prize rounds.

*Working charter — **Maximize P(Win)** and **Own the Outcome** (Arena Core Values): every change in
this repository exists to raise the probability of placing at the top of that leaderboard, and every
number is owned end to end — traceable to a file in `registry/` or `evidence/`, or labelled a claim.*

---

## ⬇ The submission file

| | |
|---|---|
| **primary** | [`docs/downloads/gems32-h19-5-smoothmaxcov-44090.tif`](docs/downloads/gems32-h19-5-smoothmaxcov-44090.tif) — sha256 `2dc67f4bdb8d1bf2…` |
| format | single-band float32 GeoTIFF, EPSG:32611, 100 m, 3292×3730, 44,090 predicted pixels, every footprint pixel finite in **[0, 1]**, NaN outside the footprint |
| fallback | `…-zeros.tif` — identical predictions, `0.0` outside the footprint (for a validator that dislikes NaN); the `.zip` holds the same single GeoTIFF |
| receipt | `docs/downloads/checks-…tif.json` — sha256, counts, min/max, CRS, range and footprint assertions, from an independent re-read of the written bytes |
| note to paste | `gems32-h19-5-smoothmaxcov-44090 \| H19-5 field, smoothed-density max-coverage emission, 44,090 px mass-matched to the incumbent \| paired model-MC +0.025 vs incumbent; not a score` |

**Status, in one breath.** The file is *format-validated* and *mass-matched* to the group's best
owner-claimed artifact (44,090 px), and its emission rule was derived — not tuned — from the
competition metric: cover the surface blurred by the inferred 1.85 px truth scatter, which is the
matched filter for the model's own credit. Measured against the incumbent's raster-order dotting at
identical mass on the live-anchored truth model with the official metric: **+0.0247 ± 0.0005,
12/12 paired draws positive**; the packing rule itself is **+0.0100 mean, 4/4 folds positive** on the
blocked catalogue holdout. It is **not** organizer-scored, and no slot is spent until
`bo.slot_gate` approves one on the record (`registry/observations.jsonl`).

---

## What this repository knows that the group's own sites did not

1. **The exact metric, reduced to a decision rule.** `DTI = T/(0.2(T+S−M)+0.8|G|)` and therefore
   `add mass ⇔ k > 0.2·DTI` — the credit bar (0.0520 at the group's claimed 0.2600, 0.0652 at the
   public leader's 0.3262). Verified against a brute-force transcription of the published formulas
   (27 tests) and corroborated by the group's independent empirical measurement of 0.0548 credit per
   dot. **This explains why dotting won:** the metric taxes redundant mass at 0.2 per unit, and a
   3 px kernel makes ~2.4 px spacing the optimum.
2. **The two instruments disagree, and that is now a published finding.** The catalogue-truth
   holdout says surface-coverage packing is *better* (+0.0100, 4/4 folds); the live-anchored truth
   model says it is *worse* (−0.0033, 0/12 draws). Mechanism: the hidden set is scattered *around*
   the surface, so covering the surface is the wrong objective. Fixing the objective (blur by the
   scatter) converts the disagreement into **+0.0247 (12/12 draws)** over the incumbent. This is the
   brief's "holdout drift, worth chasing rather than noise" made concrete — see IR-32-PROXY-02.
3. **No public catalogue can supply the missing faults.** GDR QFaults v2 — the newest official
   compilation the group obtained — lies within 300 m of the competition's own catalogue for all but
   **1 of its 59,065 pixels**. The only large off-catalogue official population is the older USGS
   SGMC (**61,664 px** beyond 300 m), and the group's best field is only **1.4×** enriched there.
   That is the measured size of the unexploited discovery lane.
4. **The 2020 Monte Cristo Range Mw 6.5 rupture is inside the footprint** and broke largely unmapped
   ground with displacements mostly < 5 cm ([USGS field response](https://pubs.usgs.gov/publication/70217872),
   SRL 92(2A) 823–829) — a real, verifiable, post-catalogue fault class. It leads the ranked
   hypotheses.
5. **A slot gate with a price on information.** `src/gems32/bo.py` fits a GP surrogate over the
   design space, computes expected improvement, refuses candidates that have not beaten the
   incumbent at matched mass, refuses repeats, and prices the two-round objective
   (`DTI₁ + ρ·DTI₂`, bar `0.2·DTI/(1+ρ)` for a discovery candidate). Every evaluation — submitted or
   not — is appended to `registry/observations.jsonl` as training data.

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
  metric.py        official distance-weighted Tversky index, the identity, the credit bar (verified)
  grid.py          geometry, footprint, IO, the independent format validator, sha256
  emission.py      dot-thin (incumbent), exact greedy max-coverage packing (fast + reference), bar stop
  features.py      35-channel structural stack from the 19 official bands
  detector.py      CPU-feasible detectors for the harness (HGB / logistic), memmap-friendly sampling
  holdout.py       preregistered, spatially blocked hide-and-recover harness; mass-matched arm ladder
  bo.py            GP surrogate, expected improvement, cost-aware slot gate, drift report, obs log
  submission.py    writer (+zip) and receipt
  feed.py          the site's machine-readable feed (sources, claims, evidence, build state)
  hypotheses.py    the five registered candidate hypotheses
scripts/           fetch_data · build_features · run_holdout · run_truth_model_mc ·
                   optimise_emission_models · verify_shipped_mc · build_submission · build_site ·
                   refresh_feed · log_observations · run_h60_2
registry/          sources, data manifest + sha256, leaderboard history, claims, hypotheses,
                   preregistration, irregularities, observations (the surrogate's training data)
evidence/          raw run outputs (JSON) — every number on the site comes from here
docs/              the generated GitHub Pages site + the downloadable GeoTIFFs
tests/             metric, emission, submission, BO slot gate (27 tests)
knowledge/         the PhD-level write-ups (why 0.2600, what can beat 0.3195, what cannot)
```

### Reproduce everything from a clean checkout

```bash
pip install -r requirements.txt
python3 scripts/fetch_data.py            # sha256-verified fetch of every pinned mirror (GitHub API)
python3 scripts/build_features.py        # ~3 min on 2 vCPU: 35-channel stack (~1.7 GB memmap)
python3 scripts/run_holdout.py --tag 2 --prereg-id GEMSDOE32-PREREG-2 --prior-dti 0.26 --budget 9000
python3 scripts/run_truth_model_mc.py --draws 16
python3 scripts/optimise_emission_models.py --draws 16
python3 scripts/build_submission.py      # writes docs/downloads/*.tif + the format receipt
python3 scripts/verify_shipped_mc.py --draws 12
python3 scripts/log_observations.py      # folds + model draws + claims -> the surrogate's log
python3 scripts/build_site.py
python3 -m pytest tests -q
```

## Where the system stands

* **Metric:** verified (brute force + published worked example + algebra + marginal rule).
* **Emission:** the credit bar is derived; the packing rule is exact (candidate-set greedy with a
  certificate that reproduces the reference implementation on 13/13 random and structured cases) and
  is measured, at matched mass, to beat the incumbent's rule by +0.0247 under the live-anchored model
  and +0.0100 on the catalogue holdout (where the two instruments disagree, both numbers are shown).
* **Detector:** honest baseline only. A CPU gradient-boosted tree reaches AUC 0.63–0.73 in-block;
  the official reference solution's U-Net is out of reach here (2 vCPU, no GPU). The emission rule is
  detector-agnostic, so the harness result carries over; the *field* does not.
* **Slot discipline:** no submission is automatable by design; the gate, its cost model, and the
  observation log are the record of *why* each slot would be spent.
* **The site** (`docs/`, regenerated by `scripts/build_site.py` in CI) opens with the download, then
  the evidence, then the sources, the leaderboard and the irregularity register.

## Limitations (stated, not hidden)

* The competition rasters here are **owner mirrors, not organizer bytes** (IR-32-DATA-01); every
  digest is pinned in `registry/data_manifest.json` and re-verified on each fetch.
* Every number the group ever reported as a score is an **owner report** (IR-32-SCORE-01). The only
  scores read here from an official page are the *other teams'* public-leaderboard rows.
* The generative truth model (12,691 px, σ = 1.85 px) is itself owner-report-derived; *absolute*
  scores from it are conditional, and only the **paired** differences are used for decisions.
* The holdout's truth is the visible catalogue and cannot reward a genuinely new fault
  (IR-32-PROXY-01); it is a cheap screen, not the objective.
* No GPU, so the shipped field is the group's H19-5 surface, not a newly trained deep model — the
  system improves *how* a field is turned into credit, not (yet) the field physics.
* The `[0, 1]` portal rejection is explained from the data, not from a public validator
  (IR-32-VERIFY-01). In 2020 the Monte Cristo rupture also showed the hidden set can include faults
  that are hard to see in the given bands at all (H60-1).

## Sources

Twenty-four official sources, with the role each plays and its verification status, are listed in
[`registry/sources.json`](registry/sources.json) and rendered at
<https://buffedlizard55-lab.github.io/GEMSDOE32/sources.html>. The competition host
(`drivendata.org`) is **never** requested by any script here.
