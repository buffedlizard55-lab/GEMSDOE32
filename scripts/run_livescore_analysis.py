#!/usr/bin/env python3
"""Arena48: live-score covariate audit across every locally pinned, owner-scored submission.

RETROSPECTIVE PORTFOLIO AUDIT — not a new experiment lane, no holdout runs, no weekly slots.
Every fitted score is OWNER-REPORT from docs/score-ledger.csv (IR-32-SCORE-01: no organizer
receipt binds any of these numbers to the exact raster bytes).  The outputs are diagnostics
about the portfolio; none of them is a leaderboard-score prediction, and none authorizes an
upload.

Steps:
1. join every parseable ledger row to local raster bytes (focus registry, data-manifest scored
   mirrors, this repo's docs/downloads, and the extra scored manifest) under the strict,
   deterministic rules of gems32.livescore.match_row;
2. deduplicate identical dot masks (zeros/nan twins, cross-site resubmissions) by mask digest
   and record conflicting scores for the same mask as irregularities;
3. compute intrinsic raster covariates (dot count, catalogue proximity, H19-5 family overlap,
   champion overlap, self-kernel redundancy) per unique mask;
4. fit honest leave-one-out diagnostics (per-feature Spearman, LOO linear regression,
   standardized betas) on OWNER-REPORT scores, overall and within the H19-5 family;
5. quantify the calibration-lattice pigeonhole bound exactly (IR-42-UNIQ-01);
6. write evidence/livescore_covariates_20261026.json with the full auditable join table.

Usage:  PYTHONPATH=src python3 scripts/run_livescore_analysis.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import livescore as LS  # noqa: E402
from gems32.paths import data_dir  # noqa: E402

EVIDENCE_OUT = ROOT / "evidence" / "livescore_covariates_20261026.json"

# Ledger rows whose automatic join was audited and rejected (deterministic exclusions, with
# reasons, so the join table stays reproducible).  Empty until an audit finding says otherwise.
MANUAL_EXCLUSIONS: dict[tuple[str, str], str] = {}


def load_reference_masks(ddir: Path) -> dict:
    import rasterio

    from gems32.livescore import read_mask

    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ddir / "labels.tif") as ds:
        catalogue = (ds.read(1) > 0) & foot

    h195_path = ddir / "scored" / "gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif"
    champion_path = ROOT / "docs" / "downloads" / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    lattice_path = ddir / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
    for p in (h195_path, champion_path, lattice_path):
        if not p.is_file():
            raise FileNotFoundError(f"reference raster missing: {p}")
    return {
        "footprint": foot,
        "catalogue": catalogue,
        "h195": read_mask(h195_path, foot),
        "champion": read_mask(champion_path, foot),
        "lattice": read_mask(lattice_path, foot),
    }


def build_candidate_pool() -> list[LS.Candidate]:
    """Every locally pinned raster that could be a scored submission (inputs excluded)."""
    pool: list[LS.Candidate] = []

    def add(path: Path, repo: str) -> None:
        if path.is_file() and path.suffix.lower() in (".tif", ".tiff"):
            pool.append(LS.Candidate(path=path, stem=path.stem, repo=repo))

    man = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    for r in man["rasters"]:
        add(ROOT / r["local"], r["repo"])

    dm = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    ddir = data_dir()
    for e in dm["files"]:
        if e["group"] == "scored":
            add(ddir / e["dest"], "scored-mirror")

    for p in sorted((ROOT / "docs" / "downloads").glob("*.tif")):
        add(p, "GEMSDOE32")

    extra = ROOT / "registry" / "extra_scored_manifest.json"
    if extra.is_file():
        ex = json.loads(extra.read_text())
        for r in ex["rasters"]:
            add(ROOT / r["local"], r["repo"])
    return pool


def main() -> int:
    t0 = time.time()
    ddir = data_dir()
    refs = load_reference_masks(ddir)
    foot, catalogue = refs["footprint"], refs["catalogue"]

    scored, excluded_rows = LS.parse_ledger(ROOT / "docs" / "score-ledger.csv")
    pool = build_candidate_pool()

    joins, unmatched = [], []
    for row in scored:
        if (row.site, row.submission) in MANUAL_EXCLUSIONS:
            unmatched.append({"site": row.site, "submission": row.submission,
                              "score": row.score,
                              "reason": "manual audit exclusion: " + MANUAL_EXCLUSIONS[(row.site, row.submission)]})
            continue
        cand, rule = LS.match_row(row, pool)
        if cand is None:
            unmatched.append({"site": row.site, "submission": row.submission,
                              "score": row.score, "reason": "no local raster matched"})
            continue
        joins.append({"site": row.site, "submission": row.submission, "score": row.score,
                      "rule": rule, "path": str(cand.path.relative_to(ROOT)), "repo": cand.repo})

    # ---- deduplicate identical dot masks ------------------------------------
    by_digest: dict[str, dict] = {}
    conflicts: list[dict] = []
    read_errors = []
    for j in joins:
        try:
            mask = LS.read_mask(ROOT / j["path"], foot)
        except Exception as exc:  # grid mismatch / unreadable -> excluded, never guessed
            read_errors.append({**j, "error": f"{type(exc).__name__}: {exc}"})
            continue
        digest = LS.mask_digest(mask)
        entry = by_digest.setdefault(digest, {"digest": digest, "mask": mask,
                                              "rows": [], "scores": set()})
        entry["rows"].append(j)
        entry["scores"].add(j["score"])

    unique_masks = []
    for entry in by_digest.values():
        scores = sorted(entry["scores"])
        if len(scores) > 1:
            conflicts.append({
                "digest": entry["digest"],
                "rows": [(r["site"], r["submission"], r["score"]) for r in entry["rows"]],
                "scores": scores,
                "action": "excluded from all fits: one mask cannot have two different live scores",
            })
            continue
        unique_masks.append({**entry, "score": scores[0]})

    # ---- features ------------------------------------------------------------
    feats, feat_errors = [], []
    for entry in unique_masks:
        try:
            f = LS.raster_features(entry["mask"], catalogue, refs["h195"], refs["champion"])
        except Exception as exc:
            feat_errors.append({"rows": [r["submission"] for r in entry["rows"]],
                                "error": f"{type(exc).__name__}: {exc}"})
            continue
        feats.append({
            "score": entry["score"],
            "dots": f.dots,
            "log10_dots": f.log10_dots,
            "frac_on_catalogue": f.frac_on_catalogue,
            "frac_within3_catalogue": f.frac_within3_catalogue,
            "median_dist_catalogue_px": f.median_dist_catalogue_px,
            "frac_within3_h195": f.frac_within3_h195,
            "frac_within3_champion": f.frac_within3_champion,
            "mean_self_kernel": f.mean_self_kernel,
            "representative_row": entry["rows"][0]["submission"],
            "n_ledger_rows": len(entry["rows"]),
            "digest": entry["digest"][:16],
        })
    feats.sort(key=lambda r: -r["score"])

    # ---- statistics ----------------------------------------------------------
    def col(key: str) -> np.ndarray:
        return np.array([r[key] for r in feats], float)

    y = col("score")
    single_feature = {}
    for key in LS.FEATURE_ORDER + ("dots", "frac_within3_champion", "median_dist_catalogue_px"):
        rho, p = LS.spearman(col(key), y)
        single_feature[key] = {"spearman_rho": rho, "p_value": p}

    family = [r for r in feats if r["frac_within3_h195"] >= 0.8]
    nonfamily = [r for r in feats if r["frac_within3_h195"] < 0.8]

    def sub_stats(rows: list[dict]) -> dict:
        if not rows:
            return {"n": 0}
        ys = [r["score"] for r in rows]
        return {"n": len(rows), "max": max(ys), "min": min(ys),
                "median": float(np.median(ys)),
                "best_row": max(rows, key=lambda r: r["score"])["representative_row"]}

    loo_all = loo_family = None
    betas = None
    if len(feats) >= len(LS.FEATURE_ORDER) + 4:
        x = np.column_stack([col(k) for k in LS.FEATURE_ORDER])
        finite = np.isfinite(x).all(axis=1)
        x, yf = x[finite], y[finite]
        loo_all = LS.loo_linear_regression(x, yf)
        betas = LS.full_fit_coefficients(x, yf, list(LS.FEATURE_ORDER))
        # attach per-row held-out predictions (aligned with feats order via the finite mask)
        finite_idx = [i for i, ok in enumerate(finite) if ok]
        for i, pred in zip(finite_idx, loo_all["predictions"]):
            feats[i]["loo_pred_all_features"] = round(float(pred), 5)
            feats[i]["loo_residual_all_features"] = round(float(feats[i]["score"] - pred), 5)
    if len(family) >= 4:
        xf = np.array([[r["log10_dots"]] for r in family], float)
        yfam = np.array([r["score"] for r in family], float)
        loo_family = LS.loo_linear_regression(xf, yfam)
        for i, pred in enumerate(loo_family["predictions"]):
            family[i]["loo_pred_family_dotcount"] = round(float(pred), 5)
        # Where does the champion sit on the family's own thinning trend?
        champ_rows = [r for r in family if r["frac_within3_champion"] >= 0.999]
        champ_leave_one_out = None
        if len(champ_rows) == 1 and len(family) >= 5:
            idx = family.index(champ_rows[0])
            keep = [i for i in range(len(family)) if i != idx]
            from sklearn.linear_model import LinearRegression
            m = LinearRegression().fit(xf[keep], yfam[keep])
            pred = float(m.predict(xf[idx:idx + 1])[0])
            champ_leave_one_out = {
                "champion_row": champ_rows[0]["representative_row"],
                "actual_owner_report": champ_rows[0]["score"],
                "predicted_from_rest_of_family": pred,
                "residual": champ_rows[0]["score"] - pred,
                "note": "linear trend of the family's own dot count; OWNER-REPORT-fitted diagnostic",
            }

    lattice = LS.lattice_hole_bound(refs["lattice"], foot)

    result = {
        "schema_version": 1,
        "arena": "arena48-livescore-covariates",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": "retrospective portfolio audit; no new experiment lane; 0 holdout runs; 0 weekly slots",
        "evidence_class": (
            "OWNER-REPORT-fitted diagnostics. Live scores are the owner's ledger transcription "
            "with no organizer receipt binding them to these bytes (IR-32-SCORE-01). Nothing here "
            "is a leaderboard-score prediction or upload authorization."
        ),
        "reference_masks": {
            "catalogue_positives": int(catalogue.sum()),
            "h195_dots": int(refs["h195"].sum()),
            "champion_dots": int(refs["champion"].sum()),
            "lattice_dots": int(refs["lattice"].sum()),
            "footprint_pixels": int(foot.sum()),
        },
        "ledger": {
            "scored_rows": len(scored),
            "excluded_rows": len(excluded_rows),
            "excluded_reasons": {},
            "joined_rows": len(joins),
            "unmatched_rows": len(unmatched),
            "unmatched": unmatched,
            "read_errors": read_errors,
        },
        "join_table": joins,
        "dedupe": {
            "unique_masks_with_score": len(unique_masks),
            "conflicting_score_masks": conflicts,
            "feature_errors": feat_errors,
        },
        "features": feats,
        "single_feature_spearman_vs_owner_score": single_feature,
        "family_split": {
            "rule": "family := frac_within3_h195 >= 0.8 (dots within 3 px of the dense H19-5 mask)",
            "family": sub_stats(family),
            "non_family": sub_stats(nonfamily),
        },
        "loo_linear_all": loo_all,
        "loo_linear_family_dotcount": loo_family,
        "champion_leave_one_out": champ_leave_one_out,
        "full_fit_standardized_betas": betas,
        "lattice_pigeonhole_bound": lattice,
        "runtime_seconds": round(time.time() - t0, 1),
    }
    for e in excluded_rows:
        r = e["reason"]
        result["ledger"]["excluded_reasons"][r] = result["ledger"]["excluded_reasons"].get(r, 0) + 1

    EVIDENCE_OUT.write_text(json.dumps(result, indent=1) + "\n")
    print(f"wrote {EVIDENCE_OUT}")
    print(f"joined {len(joins)} rows -> {len(unique_masks)} unique scored masks "
          f"({len(conflicts)} conflicts, {len(read_errors)} read errors)")
    print(f"family n={result['family_split']['family']['n']} "
          f"max={result['family_split']['family'].get('max')} · "
          f"non-family n={result['family_split']['non_family']['n']} "
          f"max={result['family_split']['non_family'].get('max')}")
    if loo_all:
        print(f"LOO(all) R2={loo_all['loo_r2']:.3f} rho={loo_all['loo_spearman']:.3f} "
              f"MAE={loo_all['loo_mae']:.4f}")
    if loo_family:
        print(f"LOO(family, dot count) R2={loo_family['loo_r2']:.3f} "
              f"rho={loo_family['loo_spearman']:.3f} MAE={loo_family['loo_mae']:.4f}")
    print(f"lattice: {lattice['hole_pixels']} holes; max passing dots "
          f"{lattice['max_dots_that_could_pass_literal_rule']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
