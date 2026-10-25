# Why `h33-2-b2` scored 0.2778 — and what beating it actually requires

*Round-5 analysis, 2026-10-25. Labels: **[ORGANIZER-CONFIRMED]** = owner-reported from the
DrivenData submission page (this repo cannot independently authenticate account-side receipts);
**[HOLDOUT-DTI]** = local proxy (`src/gems32/holdout.py`, draws 20/21); **[MODEL]** = algebra on
the published metric; **[measured-here]** = computed from bytes on disk this session
(`scripts/analyze_registry_overlap.py` → `evidence/registry_overlap.json`).*

## 1. The champion is the end of a subtraction ladder, not a new detector

**[measured-here]** The group's four best files are one belief field with dots successively
removed. The subset relations are exact at the pixel level:

| file | dots | live DTI | relation to the previous row |
|---|---:|---:|---|
| H19-5 (`…e27054cf…`) | 121,131 | 0.1922 | the base multiline-corroborated field, thresholded |
| d2.8 (`…e56ea318af89…`) | 44,090 | 0.2600 | ⊂ H19-5: raster-order dot-thin at 2.8 px spacing |
| solo (`…8acb75e1f2cc…`) | 40,199 | 0.2708 | == d2.8 minus its 3,891 dots within 1 px of the catalogue (**B = 1**) |
| **champion (`h33-2-b2…e5eb6e7e…`)** | **37,654** | **0.2778** | == solo minus its 2,545 dots within 2 px of the catalogue (**B = 2**) |
| Anderson PINN (GEMSDOE36) | 38,854 | 0.2750 | == champion **plus** 1,200 dots (champion ⊂ Anderson exactly) |

All live values **[ORGANIZER-CONFIRMED]** except H19-5/d2.8/solo provenance caveats in
`docs/score-ledger.csv` (IR-32-SCORE-02). Two corollaries matter for every future session:

* **No "consensus of independent top methods" exists in this group.** The two highest artifacts
  share 37,654 of 38,854 dots (Jaccard 0.969). Any ensemble argument over them is circular
  (IR-32-FAM-01). Likewise GEMSDOE30's `poisson300m` *is* GEMSDOE25's `d2-8`, dot for dot
  (IR-32-FAM-02) — and both report 0.2600, a free determinism check on the scorer.
* **The B-ladder is a controlled experiment the group accidentally ran on itself.** B = 0 → 1 → 2
  changed exactly one variable at a time: +0.0108, then +0.0070.

## 2. Why removing near-catalogue dots pays: the metric's arithmetic

The published metric is DTI = T / (0.2(T + S − M) + 0.8|G|) (`knowledge/01` §1, verified against
brute force in `tests/test_metric.py`). Known faults are masked out of scoring, so a dot earns
only if it lands within 300 m of a *hidden* fault pixel, with triangular weight
k(d) = 1 − d/300 m. Adding one dot of realised weight k raises DTI iff **k > 0.2·DTI** — at the
champion's level, k > 0.0556, i.e. the dot must land within ≈283 m of hidden truth *and* not be
redundant with a nearer dot.

**[MODEL]** Invert the champion/solo pair (nested sets, so the only unknowns are the flank
dots' total credit f and |G|). Under the thin-line regime (T ≈ M):

```
f = 85.12 − 0.0056·|G|      ⇒   mean credit of the 2,545 removed (100–200 m) dots
                            =   0.0161 /dot at |G| = 7,905 … 0.0055 /dot at |G| = 12,691
```

Both are 3–10× below the 0.0556 bar. The 100–200 m annulus around mapped faults is, empirically,
a place where hidden faults almost never are (plausible geologically: the catalogue is
fault-*zone* complete at that scale — a strand 150 m from a mapped trace would usually have been
mapped as part of it), yet every dot there pays the full α = 0.2 denominator tax. **B = 2 won
because it was the first emission with zero mass in the dead annulus.** It is denominator thrift,
not new geology — which is also why the trick is nearly exhausted:

* **B = 3** would remove the champion's 2,171 dots at 200–300 m. It helps iff their mean credit
  < 0.0556 (the breakeven is exact and |G|-free under the same algebra). At zero credit it would
  give ≈ 0.285–0.287; at annulus credit 0.08/dot it *loses* ≈ 0.004. The (2,3] annulus dots are
  field-selected survivors, so their credit plausibly exceeds the (1,2] annulus's 0.006–0.016.
  Expected Δ ≈ [−0.004, +0.009] — a cheap, genuinely uncertain experiment for the incumbent lane
  (this session could not run it: a strict subset fails the parallel-run lane rule by
  construction).
* **Anderson's +1,200 dots** imply 0.014–0.023 credit/dot, also below bar: adding mass near the
  champion's own lineaments is measured, live, to be negative. The frontier is placement quality,
  not budget.

## 3. What beating 0.2778 (and 0.4413) requires, in one line each

Under (★) at fixed mass S and fixed hidden set, T must scale in proportion to DTI:

* **0.30** needs **+8.0 %** mean credit per dot at 37,654 dots.
* **Public #1 = 0.4413** (read 2026-10-25, `registry/leaderboard_history.jsonl`) needs
  **+58.9 %** (= 0.4413/0.2778 − 1, |G|-invariant).

+59 % credit density is not an emission tweak; it is a different detector class (the reference
solution is a U-Net; the leaders have 17–51 submissions each). This session tested whether the
project's best *learned* field, finally emitted with champion discipline, could supply the first
+8 %. It could not (§5).

## 4. The instrument warning every future session must heed (IR-32-INSTR-03)

**[measured-here]** The `catalogue_hidden` holdout (hide 20 % of catalogue components per
quadrant-draw, recover) now provably scores the live B-ladder **backwards**:

| candidate | live | catalogue-hidden [HOLDOUT-DTI] | SGMC-cal [HOLDOUT-DTI] |
|---|---:|---:|---:|
| champion (B = 2) | **0.2778** | 0.00460 | 0.06412 |
| solo (B = 1) | 0.2708 | 0.03104 | 0.06301 |
| d2.8 (B = 0) | 0.2600 | 0.09832 | 0.06059 |

Mechanism: a B-gated candidate derived its exclusion zone from the *full* catalogue — including
the very components the instrument hides — so it is structurally forbidden from recovering them.
The instrument punishes exactly what the live scorer rewards. This is a candidate-side protocol
violation ("derive every catalogue-based feature only from the visible faults") that
`evaluate_candidate_holdout` does not correct for. **Rule going forward:** gate B-pruned
candidates only on instruments whose truth is off-catalogue by construction (SGMC), or re-derive
the candidate's gate per draw from visible faults only. The SGMC instrument ranks the ladder
correctly here (0.06412 > 0.06301 > 0.06059) and remains the fair local gate, with its known
weakness (ρ ≈ +0.54 at n = 12, IR-32-INSTR-02).

## 5. Round 5's two experiments — negative results, delivered as such

Both lanes were frozen in `docs/research/hypotheses-round5.md` *before* building; both files are
in `docs/downloads/`, portal-valid (12-point audit + independent second validator), and pass the
lane-uniqueness gates by wide margins. Both lose to the champion on the fair instrument.
**Verdict for both: negative — DO NOT SUBMIT.**

| | H-CVF2 (exp. 1) | H-SUP-SGMC (exp. 2) | champion |
|---|---:|---:|---:|
| field | 4-quadrant CV HistGB, 35ch stack | + SGMC-north positives | hand-built H19-5 lineage |
| dots | 37,654 | 37,654 | 37,654 |
| within-3px of champion | 49.7 % | 43.3 % | — |
| SGMC-cal [HOLDOUT-DTI] | 0.05876 | (contaminated) | **0.06412** |
| south-SGMC DTI [HOLDOUT-DTI] | 0.09017 | 0.07517 | **0.09289** |
| canary (worst channel AUC) | 0.6217 ✓ | (reused) | — |

Receipts: `evidence/hcvf2_run.json`, `evidence/hsupsgmc_run.json`. Two readings:

1. **The hand-built multiline-corroboration field still out-ranks the per-pixel learner** at
   champion-grade emission (SGMC coverage 8.94 % vs 8.19 % at identical mass). The learner's mass
   spreads over catalogue-*like* terrain; corroboration across independent line evidence appears
   to be doing real geological work that per-pixel appearance does not.
2. **SGMC supervision backfired spatially**: trained on north SGMC appearance, the field spent
   only 12,639 of 37,654 dots in the south (champion: 18,618) and under-covered held-out south
   SGMC truth (paired diff −0.0177, 95 % CI [−0.0345, +0.0033]). Learning SGMC appearance does
   not transfer across the map at champion level — consistent with SGMC's mixed
   vintage/positional quality and with the two live SGMC-tracing failures (0.0512, 0.0492).
   One honest nuance: in the *south only*, H-CVF2 (exp. 1) is within 3 % of the champion
   (0.09017 vs 0.09289, coverage 8.74 % vs 8.76 %); its deficit is northern. That observation is
   reported, not gated on — the frozen full-map verdict stands.

## 6. Ranked next levers (for the selector / next sessions)

1. **Submit the identification probes S2/S3 if slots allow** (already built, unscored): S2
   (λ = 0.5 scaling) identifies the scorer's value semantics — the unlock for soft-valued
   emission (H-F5), potentially the cheapest structural gain available; S3 (+2,000 far-field
   dots) + S1 pin (T, K, F) exactly. Only the team's best file counts toward standing, so probes
   cannot cost rank.
2. **B = 3** (incumbent lane): expected Δ ∈ [−0.004, +0.009]; decides whether the dead annulus
   ends at 200 m or 300 m.
3. **A real detector**: U-Net over the 19 bands + 1 m LiDAR context needs a GPU this sandbox
   lacks (2 vCPU / 3.9 GB). The +59 % to #1 lives there, not in emission.
4. **Raw seismicity (H-F4/H33-E)**: USGS FDSN is official and free but unreachable from this
   sandbox (HTTP 000, re-verified 2026-10-25); `scripts/fetch_earthquake_catalog.sh` is ready
   for any unrestricted machine. The 2020 Mw 6.5 Monte Cristo rupture — inside the footprint, on
   largely unmapped segments — remains the single most promising *known* hidden-fault population
   (`knowledge/01` §6).
5. **Fix the instrument, not just the model**: per-draw visible-only re-gating inside
   `evaluate_candidate_holdout` (IR-32-INSTR-03) so catalogue-hidden can judge B-gated files
   fairly; then re-run the ladder as a regression test (expected: B order restored).
