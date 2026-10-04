# Quarantined artifacts — kept for the audit trail, never offered as a download

Nothing in this directory is a submission candidate. Each file is here because it was measured to be
defective and the measurement is more useful than the file.

| file | measured defect | evidence |
| --- | --- | --- |
| `QUARANTINED-gems32-heatfield-44090-cv-supconfined-zeros.tif` | **emits dots on the published catalogue**, which the live scorer masks out of scoring: those dots cost `alpha = 0.2` each and can earn nothing. It fails the repository's own `zero_on_catalogue_leakage` check. | measured 2026-10-04: 44,090 dots, of which **6,528 of its 44,090 dots (14.8 %)** lie on `labels.tif` (== `existing_faults.tif`, sha256 `7ba308ccdc...`). The H33 primary has **0** dots within 100 m of the catalogue. |
| `QUARANTINED-gems32-h19-5-smoothmaxcov-44090-zeros.tif` | same defective artifact in the all-finite container, **plus a stray `nodata = NaN` tag on a raster that contains no NaN at all**. That tag/content mismatch is exactly the configuration the DrivenData validator could reject with *"Predicted values must be in range [0, 1]"* — the site's own Mechanism 2. A non-candidate file must not carry portal risk. | measured 2026-10-04 with `rasterio`: `nodata` is `nan`, `np.isnan(arr).sum() == 0`, and every cell outside the footprint is `0.0`. |
| `QUARANTINED-gems32-h19-5-smoothmaxcov-44090.tif` | **57.8 % of its 44,090 dots (25,485) lie off the belief field it was packing**, and it scores **0.01632** against the only real truth raster versus the incumbent's **0.16177** — a **10×** collapse in credit per unit mass at an identical budget. | `IR-32-SHIP-01`; reproduced by `scripts/audit_shipped.py`. The proxy number is leak-contaminated and is *not* a score, but the off-support fraction and the 10× collapse are both structural facts about the file. |

This file was previously offered one click from the recommended primary on the site. That was a
defect in the site, not just in the file: a known-broken artifact must not sit next to the download
button. It is quarantined here and `scripts/audit_shipped.py` now builds the site's manifest from
the files in `docs/downloads/` only, so it cannot reappear.

All remaining files in `docs/downloads/` re-open clean under the 12-point portal validator
(`docs/downloads/submissions_manifest.json`, `portal_illegal: []`).
