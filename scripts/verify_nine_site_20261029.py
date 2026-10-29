#!/usr/bin/env python3
"""Byte-level verification of the nine focus-site files, the unique H51-1 file, and the r13 registry raster.

Writes evidence/nine_site_verification_20261029.json. Every number is MEASURED-HERE (computed from
the pinned bytes in this run) unless it is copied from a registry/evidence file and labelled as such.

Definitions (same as the repo's registry rules; see README section 'Standing Mission'):
  * dots  = pixels equal to 1 inside the training-feature footprint (gems32.holdout.load_holdout_context)
  * directional 3 px overlap A->B = fraction of A's dots lying within 3 px (Euclidean) of any B dot
  * rank correlation = Spearman over all footprint pixels of the two rasters (NaN-free footprint only)
  * r13 coverage = fraction of footprint pixels within 3 px of an r13 dot (the literal lattice rule)
Nothing here is a leaderboard score. Live scores are copied from the owner's list (OWNER-REPORT).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr, t as student_t

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import holdout  # noqa: E402
from gems32.paths import data_dir  # noqa: E402

OUT = ROOT / "evidence" / "nine_site_verification_20261029.json"
EVAL = ROOT / ".cache" / "work" / "eval"

# site, path (relative to repo), owner-reported live score (OWNER-REPORT, from the owner's brief 2026-10-29)
SITES = [
    ("GEMSDOE24", ".cache/gems_data/scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477),
    ("GEMSDOE25", "docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600),
    ("GEMSDOE27", ".cache/gems_data/scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449),
    ("GEMSDOE28", ".cache/registry/GEMSDOE28/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710),
    ("GEMSDOE30", ".cache/registry/GEMSDOE30/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600),
    ("GEMSDOE31", ".cache/registry/GEMSDOE31/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708),
    ("GEMSDOE32", "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", 0.2778),
    ("GEMSDOE33", ".cache/registry/GEMSDOE33/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632),
    ("GEMSDOE36", ".cache/registry/GEMSDOE36/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750),
]
UNIQUE_H51 = ("H51-1-EWSP (existing repo file)", "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif")
R13 = ("GEMSDOE13 r13-lattice-s5 (dense registry raster)", ".cache/gems_data/scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif")
PINNED_SHA = {  # from evidence/nine_site_best_files_audit.json (pinned byte digests)
    "GEMSDOE24": "68d0e2e4fcc594f9a23f56c44b885fee733d026d39be55e18ad2a07289525310",
    "GEMSDOE25": "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
    "GEMSDOE27": "33003374335d84bf885f2d8f5e9dd4c57044c8ec58fa6a0d7fa581e8bc41c11d",
    "GEMSDOE28": "5556aa1438fd67376b60d5ffc99228ec09dcc11a8408298a743ccb88d6163641",
    "GEMSDOE30": "8cf893ead5667df2",  # prefix only; full digest checked below against the audit file
    "GEMSDOE31": "07b6db440535404b",
    "GEMSDOE32": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "GEMSDOE33": "87f857d505e23247",
    "GEMSDOE36": "e15891020b9c5705",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_binary(path: Path, foot: np.ndarray) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        meta = {
            "crs": str(ds.crs),
            "shape": list(ds.shape),
            "dtype": ds.dtypes[0],
            "nodata": ds.nodata,
            "transform": list(ds.transform)[:6],
        }
    vals_in = np.unique(arr[foot])
    meta["unique_values_in_footprint"] = [float(v) for v in vals_in[:5]]
    meta["nan_in_footprint"] = int(np.isnan(arr[foot]).sum())
    meta["nan_outside_footprint"] = int(np.isnan(arr[~foot]).sum())
    dots = (arr == 1) & foot
    meta["dots"] = int(dots.sum())
    return dots, meta


def within3(a: np.ndarray, b: np.ndarray) -> float:
    """Fraction of a's dots lying within 3 px of any b dot."""
    if a.sum() == 0:
        return float("nan")
    dist_to_b = distance_transform_edt(~b)
    return float(((dist_to_b <= 3.0) & a).sum() / a.sum())


def main() -> int:
    ddir = data_dir()
    ctx = holdout.load_holdout_context(ddir)
    foot = ctx.foot
    n_foot = int(foot.sum())
    print(f"footprint pixels: {n_foot}")

    sets = {}
    for site, rel, live in SITES:
        p = ROOT / rel
        dots, meta = load_binary(p, foot)
        meta.update({"path": rel, "sha256": sha256(p), "bytes": p.stat().st_size, "live_owner_report": live})
        sets[site] = {"dots": dots, "meta": meta}
    dots, meta = load_binary(ROOT / UNIQUE_H51[1], foot)
    meta.update({"path": UNIQUE_H51[1], "sha256": sha256(ROOT / UNIQUE_H51[1]), "bytes": (ROOT / UNIQUE_H51[1]).stat().st_size})
    sets["H51-1"] = {"dots": dots, "meta": meta}
    dots, meta = load_binary(ROOT / R13[1], foot)
    meta.update({"path": R13[1], "sha256": sha256(ROOT / R13[1]), "bytes": (ROOT / R13[1]).stat().st_size})
    sets["r13"] = {"dots": dots, "meta": meta}

    pinned_check = {}
    audit = json.loads((ROOT / "evidence" / "nine_site_best_files_audit.json").read_text())
    for s in audit["sites"]:
        site = s["site"]
        if site in sets:
            pinned_check[site] = {"pinned_sha256": s["sha256"], "computed_sha256": sets[site]["meta"]["sha256"],
                                  "match": s["sha256"] == sets[site]["meta"]["sha256"]}

    names = [s[0] for s in SITES] + ["H51-1", "r13"]
    # directional 3 px overlap matrix
    overlap = {}
    for a in names:
        for b in names:
            if a == b:
                continue
            overlap[f"{a}->{b}"] = within3(sets[a]["dots"], sets[b]["dots"])
    # surface rank correlation for each pair (footprint pixels)
    rho = {}
    flat = {k: v["dots"][foot].astype(np.float32) for k, v in sets.items()}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rho[f"{a}|{b}"] = float(spearmanr(flat[a], flat[b]).correlation)
    # identical dot sets (exact equality on the footprint)
    identical = [f"{a}=={b}" for i, a in enumerate(names) for b in names[i + 1:]
                 if np.array_equal(sets[a]["dots"], sets[b]["dots"])]

    # r13 coverage: fraction of footprint within 3 px of r13 dots (literal lattice rule input)
    d_r13 = distance_transform_edt(~sets["r13"]["dots"])
    cov_all = float(((d_r13 <= 3.0) & foot).sum() / n_foot)
    beyond_px = int((foot & (d_r13 > 3.0)).sum())
    # bound: a file with N dots needs >=30% of its dots beyond 3 px of r13 -> N <= beyond_px / 0.30
    max_dots_literal = int(beyond_px / 0.30)

    # share of each file's dots within 200 m (2 px) and 300 m (3 px) of a catalogue (labels.tif) fault trace
    d_cat = distance_transform_edt(~ctx.labels)
    catalogue_prox = {}
    for k, v in sets.items():
        n_d = max(int(v["dots"].sum()), 1)
        catalogue_prox[k] = {"dots": int(v["dots"].sum()),
                             "share_within_200m_of_catalogue": round(float(((d_cat <= 2.0) & v["dots"]).sum() / n_d), 6),
                             "share_within_300m_of_catalogue": round(float(((d_cat <= 3.0) & v["dots"]).sum() / n_d), 6)}

    # mass versus owner-reported live score (n=9, PROJECTION only)
    x = np.array([sets[s[0]]["meta"]["dots"] for s in SITES], float)
    y = np.array([s[2] for s in SITES], float)
    n = len(x)
    A = np.vstack([np.ones(n), x]).T
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    s2 = float(resid @ resid / (n - 2))
    cov = s2 * np.linalg.inv(A.T @ A)
    tcrit = float(student_t.ppf(0.975, n - 2))
    r2 = 1 - float(resid @ resid) / float(((y - y.mean()) ** 2).sum())
    rho_mass = float(spearmanr(x, y).correlation)

    def pred(xv: float) -> dict:
        xv_vec = np.array([1.0, xv])
        mu = float(xv_vec @ beta)
        se_mean = float(np.sqrt(xv_vec @ cov @ xv_vec))
        se_pred = float(np.sqrt(s2 + se_mean ** 2))
        return {"dots": xv, "projection": round(mu, 4), "ci95_mean": [round(mu - tcrit * se_mean, 4), round(mu + tcrit * se_mean, 4)],
                "pi95_new_file": [round(mu - tcrit * se_pred, 4), round(mu + tcrit * se_pred, 4)]}

    out = {
        "schema_version": 1,
        "generated_by": "scripts/verify_nine_site_20261029.py",
        "evidence_classes": {
            "MEASURED-HERE": "computed from the pinned bytes in this run",
            "OWNER-REPORT": "live score as supplied by the owner (no organizer receipt in this repo)",
            "PROJECTION": "regression output on 9 owner-reported points; never a score",
        },
        "footprint_pixels": n_foot,
        "footprint_source": "gems32.holdout.load_holdout_context (np.isfinite of the template raster)",
        "inputs": {k: {kk: vv for kk, vv in v["meta"].items()} for k, v in sets.items()},
        "pinned_digest_check": pinned_check,
        "identical_dot_sets": identical,
        "directional_3px_overlap": {k: round(v, 6) for k, v in overlap.items()},
        "surface_spearman": {k: round(v, 6) for k, v in rho.items()},
        "r13_coverage": {"footprint_within_3px_of_r13": round(cov_all, 6), "footprint_beyond_3px_of_r13_px": beyond_px,
                         "max_dots_satisfying_literal_70pct_rule_bound": max_dots_literal,
                         "note": "bound = beyond_px / 0.30; raw footprint, before any known-fault exclusion (repo IR figure is 6,514 after exclusion)"},
        "mass_vs_owner_live": {
            "n": n, "ols_intercept": round(float(beta[0]), 6), "ols_slope_per_dot": float(beta[1]),
            "r2": round(r2, 4), "spearman_rho": round(rho_mass, 4), "label": "PROJECTION (n=9, owner-reported)",
            "predictions": [pred(37654.0), pred(40000.0), pred(44090.0), pred(max_dots_literal)],
        },
        "catalogue_proximity": catalogue_prox,
        "holdout_static_diagnostic": {},
    }
    for site, _, live in SITES + [("H51-1", UNIQUE_H51[1], None)]:
        p = EVAL / ("h51.holdout.json" if site == "H51-1" else f"{site.lower()}.holdout.json")
        if p.exists():
            d = json.loads(p.read_text())
            hr, sg = d["hide_and_recover"], d["sgmc_off_catalogue"]
            out["holdout_static_diagnostic"][site] = {
                "live_owner_report": live,
                "label": "HOLDOUT-DTI (static diagnostic, promotion_eligible=false)",
                "HIDE-RECOVER-v3.0_pooled_dti": round(hr["pooled_dti"], 6),
                "ci95": [round(v, 6) for v in hr["ci95_cluster_bootstrap"]],
                "n_withheld_positives": hr["n_withheld_positives"],
                "SGMC-CAL-v3.0_dti": round(sg["sgmc_prevalence_calibrated_dti"], 6),
                "sgmc_ci95": [round(v, 6) for v in sg["sgmc_calibrated_ci95"]],
            }
    # association checks on the nine focus files (n=9; owner-reported live scores). Confounded: see README.
    focus = [s[0] for s in SITES]
    live_v = [s[2] for s in SITES]
    share200 = [catalogue_prox[k]["share_within_200m_of_catalogue"] for k in focus]
    mass_v = [sets[k]["meta"]["dots"] for k in focus]
    static_hr = [out["holdout_static_diagnostic"][k]["HIDE-RECOVER-v3.0_pooled_dti"] for k in focus]
    from scipy.stats import spearmanr as _sp
    out["association_n9"] = {
        "note": "Spearman rank correlations over the nine focus files. n=9, owner-reported live scores; mass and catalogue share are confounded in this family, so no causal claim is made.",
        "rho_live_vs_dots": round(float(_sp(mass_v, live_v).correlation), 4),
        "rho_live_vs_share_within_200m_catalogue": round(float(_sp(share200, live_v).correlation), 4),
        "rho_static_HIDE_RECOVER_vs_live": round(float(_sp(static_hr, live_v).correlation), 4),
        "rho_static_HIDE_RECOVER_vs_share_within_200m_catalogue": round(float(_sp(static_hr, share200).correlation), 4),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print("identical:", identical)
    print("r13 coverage:", round(cov_all, 6), "beyond px:", beyond_px, "max dots literal:", max_dots_literal)
    print("mass-live r2:", round(r2, 3), "rho:", round(rho_mass, 3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
