# Standing Prompt & Sibling-Repo Submission Slate as Recorded — 2026-10-27 (`H49-1-CGTD`)

Recorded on `2026-10-27` for branch `arena/10401461-gemsdoe32`. Preserves the active mission, core values, Parallel-Run Protocol, and the exact sibling-repo submission slate audited in `evidence/nine_site_refreshed_audit_20261027.json` and `evidence/livescore_forensics_20261027.json`.

## Active Mission & Acceptance Criteria

1. Review `GEMSDOE32` and the 9 focus sites (`GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36`) plus the newly listed sibling submissions and organizations (`GEMSDOE90..92`, `KANLERGEMSDOE1..3`, `EUGGEMSDOE1..3`, `WBGGEMSDOE1..3`, `GINNYGEMSDOE1..3`, `GEMSDOEkarage1..3`, `ApartGEMSDOE1..3`, `GEMSDOESASS1..3`).
2. Provide an executive summary and subpage (`docs/executive-summary.html`) with an auditable table for every focus site showing: file to download, estimated/labeled score (`OWNER-REPORT` or `HOLDOUT-DTI`), uniqueness vs all other GEMSDOE sites, whether it is OK to download & submit, and step-by-step portal upload instructions (unique name + note `<= 140` chars).
3. Explain at a PhD level why `GEMSDOE32`'s `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` achieved `0.2778` (`OWNER-REPORT`, highest among the 9 focus sites) and design/test a scientifically grounded strategy targeting geothermal vents/conduits toward `0.3195` / `0.4437`.
4. Propose and rank 3–5 untried geological/geophysical hypotheses naming specific layers, physical signature/transform, why it catches faults missing from the USGS/INGENIOUS catalogue, how it differs from existing repo implementations, and free official external data obtainability.
5. Generate a UNIQUE single-band GeoTIFF submission (`EPSG:32611`, `3730 x 3292`, `float32`, values strictly in `[0, 1]` with `0` NaNs to prevent `"Predicted values must be in range [0, 1]"`), validated 100% automatically without human intervention, prominently downloadable at the top of the GitHub Pages site and executive summary, with unmistakable status on whether to submit.
6. Store the prompt in `README.md`, organize verified official sources/literature in auditable tables with links, maintain an up-to-date feed, execute 3 full verification passes (Pass 1 implement/verify, Pass 2 bug/edge-case review & fix, Pass 3 full prompt re-check), create and merge a PR onto `main`, and end the final response with the required JSON Run Card plus remaining suggestions and limitations.

## Parallel-Run Protocol

1. **Lane & Uniqueness:** Stay inside a single pre-registered method lane (`H49-1-CGTD` / `CG-TILT-NOISYOR`). Check both continuous surface before placement (`|Spearman| <= 0.90`) AND final dots (`<= 70%` of dots within `3 px` of any registry raster's dots); if exceeded, log as duplicate and stop. Never copy a previous submission except for calibration/learning.
2. **Reuse, don't rebuild:** Use cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`. Holdout = hide-and-recover (withhold whole fault segments with buffer, derive catalogue features only from visible faults, mask visible faults pixel-exactly, score pooled DTI with `alpha=0.2, beta=0.8`, `300 m` triangular kernel). Fix shared tool bugs in the template, never fork privately.
3. **Score labeling:** Label every number strictly as `HOLDOUT-DTI` (evaluator version, number of withheld positives, 95% CI) or `ORGANIZER-CONFIRMED` (copied from submission-page receipt; unverified owner log claims labeled `OWNER-REPORT` per repo convention, never `ORGANIZER-CONFIRMED`). Never write a projection as a score.
4. **Leakage canary:** Test every feature alone on holdout first; single-feature `AUC > 0.90` is leakage until proven otherwise.
5. **Run Card:** End response with one JSON card containing: `hypothesis`, `mechanism`, named non-fault mimic process, `holdout_dti` + 95% CI, correlation/overlap vs registry, raster `sha256`, validator output (no NaN inside footprint, values in `[0,1]`, CRS/shape/transform match), submission name + note (`<=140` chars), and `verdict` (`promote` or `negative`). Negative results are deliverables.
6. **Budget & Slot discipline:** Stop after `3` experiments or `2` hours. Do not spend weekly submission slots on candidates that fail to beat current holdout best; promotion to a live slot is a separate selector step.

## Sibling Submissions & Organizations Audited in Session `H49-1` (`2026-10-27`)

- `gemsdoe90-cnc-35k-20261027T174525Z-zeros.tif` (`GEMSDOE90`; `0.0749 OWNER-REPORT` in `docs/score-ledger.csv`)
- `gemsdoe91-s22-omtj-37654-20261027-02da6b3f04cc-zeros.tif` (`GEMSDOE91`; `0.0298 OWNER-REPORT` in `docs/score-ledger.csv`)
- `gemsdoe92-listricdip-b2-d28-37654-20261027T174719Z-427bdde8-zeros.tif` (`GEMSDOE92`; `0.0255 OWNER-REPORT` in `docs/score-ledger.csv`)
- `wbg2-offcatalogue-density-36k-20261027.tif` (verified in `WBGGEMSDOE1`; `IR-49-WBG-MISLABEL-01`)
- `wbg3-h3pack-34k-20261027T174337Z-zeros.tif` (verified in `WBGGEMSDOE2` with `whole_array_finite=False`; `IR-49-WBG-MISLABEL-01`)
- `wbggemsdoe3-skarpline-d32-20261027T180401Z-0f42d417-zeros.tif` (`WBGGEMSDOE3`; `97,608` dots)
- `gemsdoekarage3-s2-gvc-20261027T175325Z-754c549a-zeros.tif` (`GEMSDOEkarage3`)
- `apartgemsdoe1-udth-submod-e3-20261027T175525Z-zeros.tif` (`ApartGEMSDOE1`; `clump = 97.30%`)
- `apartgemsdoe3-s2-tipbridge-b2-37654-20261027T175215Z-cc30b59c-zeros.tif` (`ApartGEMSDOE3`)
- `gemsdoesass1-swgb-hrv2-37654-20261027T182315Z-b9647c08-zeros.tif` (`GEMSDOESASS1`; `89.24% <= 1.5 km`)
- Full 21-repo sibling-org scan (`scripts/fetch_sibling_orgs.py`): `KANLERGEMSDOE1..3`, `EUGGEMSDOE1..3` (`0` `.tif`), `WBGGEMSDOE1..3`, `GINNYGEMSDOE1..3` (`0` `.tif`), `GEMSDOEkarage1..3`, `ApartGEMSDOE1..3`, `GEMSDOESASS1..3`.
