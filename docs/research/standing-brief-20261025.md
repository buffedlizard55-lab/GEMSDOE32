# Standing project brief — read before every session

This is an explicit operational digest of the owner's 2026-10-25 request, **not a verbatim
transcript**. The conversation remains authoritative. Earlier README text describing an
ellipsized prompt as “verbatim” is inaccurate.

## Outcome and values

Review previous-session work first. Maximize P(Win); Own the Outcome. Build an autonomous,
auditable geothermal/fault-discovery research system and clean GitHub Pages site. Seek genuinely
better competition predictions, not plausible-looking maps or recycled submissions.

## Non-negotiable submission policy

* Generate a unique competition-format single-band GeoTIFF only within the assigned method lane.
  Never copy a previous submission except for explicitly labelled education or audit.
* One-click download and an unambiguous OK TO SUBMIT / DO NOT SUBMIT status must appear first.
  File-format validity, novelty, holdout performance, and selector authorization are different gates.
* Exact sample CRS, shape and transform; no NaN inside footprint; values in [0,1]. Prefer the
  all-finite zero-outside version for avoiding the previously reported range error.
* Give a unique name and a note of at most 140 characters. Provide an executive-summary subpage
  with upload instructions. Do not spend a weekly slot on an unvalidated idea.

## Parallel protocol

* Stay within the session's single method paragraph. If absent, record the blocker rather than
  choosing another lane. Exact surface rank correlation >0.90 OR >70% of candidate dots within
  3 pixels of any registry raster means duplicate; log and STOP. Check before placement and
  again on final dots. No private density exemptions.
* Reuse shared cache, shared hide-and-recover evaluator and writer. Withhold whole fault
  segments with a buffer, derive catalogue features using visible faults only, mask visible faults
  pixel-exactly, pool DTI with alpha=0.2, beta=0.8 and a 300 m triangular kernel.
* Feature-alone canaries first; AUC >0.90 is leakage until proved otherwise.
* Report HOLDOUT-DTI with evaluator version, withheld positives and 95% CI, or
  ORGANIZER-CONFIRMED only with an actual receipt. Unverified owner reports stay explicitly
  unverified; projections are never scores. Negative results are deliverables.
* Stop after three experiments or two hours, whichever comes first. Promotion does not select
  a real submission slot. Read the current authenticated weekly cap, never assume an old one.
* End with one JSON run card: hypothesis, mechanism, named nonfault mimic, holdout + CI,
  registry correlation/overlap, raster SHA256, validator output, name, short note, promote/negative.

## Scientific workflow

Before implementation propose three to five ranked hypotheses naming layers, transform, physical
signature, missing-catalogue rationale, novelty against local code, benefit and cost. Validate the
best within-lane candidate against the comparable spatial holdout incumbent. Do not pretend a
geological hypothesis is established truth. New data must be free, official and actually obtainable
before it is called viable. Store auditable sources, research, failures and irregularities.

Prioritize GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36. Explain the reported H33-2-B2 winner
without inventing receipt evidence or treating a reported leaderboard snapshot as current. Source
links in the request include DrivenData competition 306, its official GitHub reference solution,
USGS GeoDAWN, GDR 1391, INGENIOUS, EPSG:32611 and NLR document 96647.

## Delivery

Three passes: implement and verify; inspect defects/assumptions/edge cases and fix; re-check the
original requirements and remaining gaps. Run tests and validate written bytes, not intentions.
Publish a PR from the fixed Arena branch and merge only if safe. Document limitations and next
steps. Never claim unavailable data, missing cache, inaccessible source or unknown result was
verified. Do not request secrets or silently consume organizer slots.
