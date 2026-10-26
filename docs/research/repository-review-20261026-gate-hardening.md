# Repository review — promotion-gate hardening (2026-10-26)

## Executive decision: DO NOT SUBMIT

No new competition-ready TIFF was generated in this review. Existing TIFF links in
[the executive summary](../executive-summary.html) are research downloads, not upload
permission. No weekly slot was spent. A higher leaderboard score is not established.

The supplied prompt does not contain its promised single assigned method paragraph.
This review therefore stays in infrastructure/audit work rather than choosing another
parallel run's geology lane. Historical restore receipts do not establish that data
or caches exist now: `data/` contains manifests/logs, and `.cache/gems_data` is absent.

## Nine-site historical comparison

These are **OWNER-REPORT**, as supplied in the prompt, not independently authenticated
ORGANIZER-CONFIRMED receipts. Ranking is historical, not a predicted future score.

| Site | Best reported submission | Reported DTI | Current advice |
|---|---|---:|---|
| GEMSDOE24 | h25-1-dotted-h19-5-d1-5 | 0.2477 | Do not resubmit |
| GEMSDOE25 | dotted-h19-5-d2-8 | 0.2600 | Do not resubmit |
| GEMSDOE27 | topo-gap-closure-t-v2-on-d1-5 | 0.2449 | Do not resubmit |
| GEMSDOE28 | h36-1-rung30-blind-r1 | 0.2710 | Do not resubmit |
| GEMSDOE30 | d28-poisson300m-offcat-44090 | 0.2600 | Do not resubmit |
| GEMSDOE31 | h27-4-solo-d28 | 0.2708 | Do not resubmit |
| GEMSDOE32 | h33-h33-2-b2 | **0.2778** | Historical best of these nine; already submitted |
| GEMSDOE33 | h33d-analog-tip-stepover-r30 | 0.2632 | Do not resubmit |
| GEMSDOE36 | anderson-geothermal-pinn-38854 | 0.2750 | Do not resubmit |

The README records catalogue-flank pruning and reduced prediction mass as an
explanation for the champion's improvement. This is a plausible metric mechanism,
not proof of new fault discovery. Its inversion of hidden truth mass is model-dependent,
not an organizer observation. Likewise, a historical pruning ladder cannot establish
an optimum over all possible geological models. The prompt quotes three different
leaderboard targets; none was freshly verified here.

## Ranked candidate extensions — not experimental results

Expected improvement ranking is qualitative; no score or novelty guarantee is assigned.
These extend existing families, so exact implementation novelty needs a code/registry
comparison after an explicit lane is supplied. No new external dataset is assumed.

| Rank / cost | Proposed layers and transform | Missing-fault mechanism | Named non-fault mimic / difference |
|---|---|---|---|
| 1 / medium | Existing MDRC stack: estimate positive-label propensity within coverage/relief strata; cross-fit PU risk | Avoid treating uncatalogued structures as certain negatives | Lithologic contacts; extends recorded MDRC PU next step, **not a new untouched family** |
| 2 / medium | Existing LiDAR elevation: compare signed cross-profile curvature at several widths, demand persistent step polarity | Buried/weak scarps can remain below catalogue mapping thresholds | Lahontan shoreline terraces; adds polarity-stability rejection to existing step-profile methods |
| 3 / medium | GeoDAWN magnetic/radiometric cache: local edge displacement and orientation agreement, with survey-seam veto | Independent physical contrasts could support covered structural boundaries | Intrusive contacts and flight-line seams; tests disagreement rather than existing simple ridge concordance |
| 4 / high | Existing topography and magnetic channels: orientation-conditioned spatial residual model fit only on training blocks | Find structures poorly explained by regional terrain/lithology background | Drainage boundaries; residualizes confounding instead of adding another raw edge layer |

All four are **blocked for this run**: no designated lane and no restored feature cache.
No claim that official-source availability has been checked is made. Test each feature
alone, reconstruct catalogue features only from visible faults, use buffered whole
segments, and stop on a literal registry duplicate before placement or after dots.
Do not exempt dense lattices without an explicit protocol revision.

## Implemented shared fix

`src/gems32/release_gate.py` previously accepted a positive point-estimate difference
with overlapping uncertainty and even `validator={"range": true}`. It now requires:

- Candidate and incumbent HOLDOUT-DTI with evaluator version, positive count and valid CI.
- Matching evaluator identifiers and positive counts, plus explicit same-evaluation evidence.
- A paired spatial improvement CI with its lower bound strictly above zero.
- Named single-band, finite, range, CRS, shape and transform checks, all true.
- Existing lane, pre-placement surface, final-dot and feature-canary gates.

This is still an evidence consumer, not an evaluator or a cryptographic attestation.
Matching version/count alone does not prove matching folds; `same_evaluation` must
come from a matched fold construction. Legacy pipeline callers lacking the new
paired evidence deliberately receive `negative`. Promotion remains separate from
slot authorization. Historical run cards have not been rewritten as new results.

Corrected the registry's champion provenance from “ORGANIZER-CONFIRMED
(owner-reported receipt)” to OWNER-REPORT. Owner reports are not authenticated receipts.

## Three review passes

1. Inspected README, source gate, tests, current release decision and local data state;
   implemented the shared evidence requirements.
2. Added regressions for absent/nonpositive/NaN/reversed paired intervals, incomplete
   validators, absent provenance and mismatched evaluation identifiers/counts.
3. Ran the full suite: **115 passed, 9 skipped**. Skips are not successful data-backed
   experiments. No source-data evaluation or current leaderboard verification occurred.

## Sources and access limitations

- [Organizer reference repository](https://github.com/drivendataorg/gems-prize-reference-solution): GitHub API availability checked in this review; not a current portal receipt.
- [Official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).
- [Official leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and).
- [GDR INGENIOUS record](https://gdr.openei.org/submissions/1391).

Non-GitHub official links above are manual-review references, **not freshly verified**:
this environment restricts outbound network hosts. No DrivenData credentials or weekly
cap were available. Next session: establish the lane, restore hash-pinned inputs/cache,
update pipeline callers to provide paired evidence and named validator outputs, then
run at most three experiments. Do not spend a slot until a separate selector authorizes it.
