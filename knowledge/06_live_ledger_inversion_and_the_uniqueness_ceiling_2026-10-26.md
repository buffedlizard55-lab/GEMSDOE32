# 06 — Live-Ledger Inversion and the uniqueness ceiling (2026-10-26, H47)

**Read this before designing any new candidate.** Full analysis:
[`docs/research/h47-results-and-nine-site-executive-summary-20261026.md`](../docs/research/h47-results-and-nine-site-executive-summary-20261026.md).

## What the live ledger is

There are 123 owner-reported live scores, of which 118 have restorable exact bytes; after collapsing
identical masks, 111 distinct rasters remain. Together they are the only measurement of the hidden
public truth. Catalogue-based holdouts measure a different population. SGMC-tracing files score at
the **random-equivalent level** live: 0.0512 and 0.0492, against ≈0.046 for random dots.

## The instrument

`src/gems32/ledger_inversion.py` (LLI) builds on two exact identities: E[TP_w] = Σ π·K_p and
E[|G|] = Σ π. The matched mass uses the line-truth 1/3 ratio. Truth density π is log-additive over
**feature** strata. Run `scripts/fetch_live_ledger_rasters.py`, then
`scripts/run_live_ledger_inversion.py --designs S3`.

Validation on 111 rasters: LOO MAE **0.0219**, Spearman **0.927**; leave-site-out 0.0223 / 0.923.
It over-predicts the champion family by ~+0.006. **Use it for go/no-go ranking with ±0.022 bands.
It produces projections, never scores.**

## What it found (robust across every fit)

1. **Catalogue-proximal depletion:** truth density is 0.01–0.07× (1–2 px), 0.05–0.15× (2–3 px) and
   0.14–0.22× (3–5 px) of the far field, and ≈1× beyond 5 px. This explains the B-ladder
   (0.2600 → 0.2708 → 0.2778).
2. **Network concentration:** 73–96% of the hidden truth lies within 300 m of the H19-5 ridge
   network, mostly in its 1-px halo.
3. **Physical strata add nothing measurable** at the stratum level: slope, LiDAR step and SGMC
   proximity do not improve held-out prediction.
4. **The side of the halo is not identifiable** (H47-1 NEGATIVE). A huge in-sample effect gave zero
   out-of-sample gain and flipped across restarts. Lesson: an LLI factor must improve held-out error
   before it informs a design.

## The uniqueness ceiling

The 70%/3 px duplicate rule, applied to the dense H19-5 raster (121,131 px), forces ≥30% of a unique
file's dots off the network. That is where only 4–27% of the truth lives, at an expected 0.002–0.018
credit per dot against a 0.0556 break-even. The best unique file built (H47) projects at
**0.240–0.248** against the champion's 0.283–0.285, and loses on HOLDOUT-DTI (0.0784 vs 0.0992).

**Unless a detector reaches ≥7× stratum-average lift off the network, unique files cost ≈0.04 DTI.**
This is an owner decision point (IR-47-UNIQ-CEILING).

## Highest-value next steps

1. **Segment-level LLI.** Fit truth density on attributes of each H19-5 segment (length, strike
   coherence, LiDAR step, coupling, catalogue distance), using the ~30 champion-family variants that
   keep different segment subsets. Then prune false segments. This is the precision route to
   0.3195+, and it needs the owner's rule decision.
2. **Trace snapping.** Test 1 m-LiDAR-based localisation of the halo traces (sub-kernel).
3. **Re-run LLI with every new live score**, especially files with a large off-network share; each
   such score directly measures the off-network density.
