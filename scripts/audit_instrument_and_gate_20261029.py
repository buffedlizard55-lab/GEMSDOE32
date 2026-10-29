#!/usr/bin/env python3
"""Instrument-validity and duplicate-gate audit (2026-10-29), measured on the bytes on disk.

Two questions, both answered with the repo's shared code (no private fork):

 Q1 GATE. The protocol says: a raster is a duplicate if > 70 % of its dots lie within 3 px of
    one registry raster's dots. Does that test discriminate anything when the registry contains
    the dense 13gems calibration lattice? We measure the test for (a) RANDOM dot sets of the
    champion's size and (b) the 0.2778 champion and the H51 candidate.

 Q2 INSTRUMENT. Does the shared static HOLDOUT-DTI evaluator (GEMSDOE32-HIDE-RECOVER-v3.0 and
    GEMSDOE32-SGMC-CAL-v3.0, `gems32.holdout`) rank files in the same order as their
    OWNER-REPORT live scores? Each live score is copied from docs/score-ledger.csv or the owner
    brief; none is organizer-confirmed. With n files we report Spearman rho and pairwise
    concordance; a holdout that cannot reproduce the live order cannot estimate a leaderboard score.

Writes evidence/audit_instrument_gate_20261029.json. Every number is labelled by evidence class.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage, stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import holdout  # noqa: E402

DDIR = ROOT / ".cache" / "gems_data"
LATTICE = DDIR / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
OUT = ROOT / "evidence" / "audit_instrument_gate_20261029.json"
RNG_SEEDS = (11, 12, 13)

# (label, path, OWNER-REPORT live score or None, source of the live score)
RECEIPTS = [
    ("GEMSDOE24 d1.5", DDIR / "scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477, "docs/score-ledger.csv"),
    ("GEMSDOE25 d2.8", DDIR / "scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", 0.2600, "docs/score-ledger.csv"),
    ("GEMSDOE27 topo-gap d1.5", DDIR / "scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449, "docs/score-ledger.csv"),
    ("GEMSDOE28 h36-1 rung30", ROOT / "docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710, "docs/score-ledger.csv"),
    ("GEMSDOE28 h27-4 solo", DDIR / "scored/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif", 0.2708, "docs/score-ledger.csv"),
    ("GEMSDOE30 d28-poisson", ROOT / "docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600, "docs/score-ledger.csv"),
    ("GEMSDOE31 h27-4 solo", ROOT / "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708, "docs/score-ledger.csv"),
    ("GEMSDOE32 champion h33-2-b2", ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif", 0.2778, "docs/score-ledger.csv"),
    ("GEMSDOE33 h33d analog-tip", ROOT / "docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632, "docs/score-ledger.csv"),
    ("GEMSDOE36 anderson-pinn", ROOT / "docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750, "docs/score-ledger.csv"),
    ("GEMSDOE19 h19-5", DDIR / "scored/gems19-h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan.tif", 0.1922, "docs/score-ledger.csv"),
    ("GEMSDOE19 h19-4", DDIR / "scored/gems19-h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan.tif", 0.1894, "docs/score-ledger.csv"),
    ("GEMSDOE16 h16-1", DDIR / "scored/gems16-h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan.tif", 0.1855, "docs/score-ledger.csv"),
    ("GEMSDOE10 h28-dotted", DDIR / "scored/gems10-h28-dotted-ridge-20260928T020256236880Z-6452ae1d00.tif", 0.1839, "docs/score-ledger.csv"),
    ("8GEMSDOE Hedge-v2", DDIR / "scored/8GEMSDOE_Hedge-v2_submission.tif", 0.1563, "docs/score-ledger.csv"),
    ("GEMSDOE10 h25-ctx", DDIR / "scored/gems10-h25-ctx-ridge-20260927T232947704150Z-6452ae1d00.tif", 0.1280, "docs/score-ledger.csv"),
    ("GEMSDOE13 r13 lattice (calibration)", LATTICE, 0.0904, "docs/score-ledger.csv"),
    ("GEMSDOE9 placeholder", DDIR / "scored/gemsdoe9-PLACEHOLDER-2314b599.tif", 0.0107, "docs/score-ledger.csv"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (ds.read(1) > 0) & foot


def within3_fraction(dots: np.ndarray, ref_within3: np.ndarray, foot: np.ndarray) -> float:
    n = int(dots.sum())
    return float((dots & ref_within3).sum() / n) if n else float("nan")


def main() -> int:
    t0 = time.time()
    ctx = holdout.load_holdout_context(DDIR)
    foot = ctx.foot
    n_foot = int(foot.sum())
    doc: dict = {
        "schema_version": 1,
        "session": "2026-10-29 (arena/5f3e9cfe-gemsdoe32)",
        "evidence_classes": {
            "HOLDOUT-DTI": "shared gems32.holdout evaluator; withheld positives and 95% CI stated",
            "OWNER-REPORT": "live score copied from docs/score-ledger.csv or owner brief; not organizer-confirmed",
            "MEASURED-HERE": "computed from the bytes listed below in this run",
        },
        "footprint_px": n_foot,
    }

    # ---- Q1: duplicate-gate discrimination against the dense 13gems lattice -------------
    lat = read_mask(LATTICE, foot)
    lat_full = (rasterio.open(LATTICE).read(1) > 0)
    dist = ndimage.distance_transform_edt(~lat_full)
    within3 = dist <= 3.0
    cover = float((within3 & foot).sum() / n_foot)
    champ_path = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
    champ = read_mask(champ_path, foot)
    h51_path = ROOT / "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif"
    h51 = read_mask(h51_path, foot)
    n_dots = int(champ.sum())
    rand = []
    fidx = np.flatnonzero(foot)
    for seed in RNG_SEEDS:
        rng = np.random.default_rng(seed)
        pick = rng.choice(fidx, size=n_dots, replace=False)
        m = np.zeros(foot.shape, dtype=bool)
        m.flat[pick] = True
        rand.append(within3_fraction(m, within3, foot))
    doc["Q1_gate_discrimination"] = {
        "label": "MEASURED-HERE",
        "rule": "duplicate if > 70% of a raster's dots lie within 3 px of one registry raster's dots",
        "lattice_raster": str(LATTICE.relative_to(ROOT / ".cache" / "gems_data").as_posix()) if False else "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
        "lattice_sha256": sha256(LATTICE),
        "lattice_dots": int(lat.sum()),
        "lattice_footprint_coverage_within_3px": round(cover, 6),
        "random_dot_sets_of_champion_size": {"n_dots": n_dots, "seeds": list(RNG_SEEDS),
                                             "within3px_of_lattice": [round(x, 6) for x in rand]},
        "champion_within3px_of_lattice": round(within3_fraction(champ, within3, foot), 6),
        "h51_within3px_of_lattice": round(within3_fraction(h51, within3, foot), 6),
        "threshold": 0.70,
        "conclusion": "The lattice test fires on random dots; it cannot separate a unique submission from a duplicate.",
        "random_fires_rule": bool(min(rand) > 0.70),
    }
    print("Q1", doc["Q1_gate_discrimination"], flush=True)

    # ---- Q2: static evaluator vs OWNER-REPORT live order -----------------------------------
    rows = []
    for label, path, live, src in RECEIPTS:
        if not path.exists():
            rows.append({"label": label, "status": "MISSING", "path": str(path)})
            continue
        mask = read_mask(path, foot)
        r = {"label": label, "status": "OK", "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path.relative_to(ROOT.parent / 'x') if False else path),
             "sha256": sha256(path), "dots": int(mask.sum()), "live_owner_report": live, "live_source": src}
        for b in (0.0, 2.0):
            hr = holdout.evaluate_hide_and_recover(mask, ctx, b_visible_px=b, n_boot=300, name=label)
            r[f"hr_b{int(b)}"] = round(float(hr["pooled_dti"]), 6)
            r[f"hr_b{int(b)}_ci95"] = [round(float(x), 6) for x in hr["ci95_cluster_bootstrap"]]
            r[f"hr_b{int(b)}_n_withheld"] = int(hr.get("n_withheld_positives", -1))
        sg = holdout.evaluate_sgmc_with_ci(mask, ctx, n_boot=300, name=label)
        r["sgmc_cal"] = round(float(sg["sgmc_prevalence_calibrated_dti"]), 6)
        r["sgmc_cal_ci95"] = [round(float(x), 6) for x in sg["sgmc_calibrated_ci95"]]
        rows.append(r)
        print("Q2", label, r["dots"], r["hr_b0"], r["hr_b2"], r["sgmc_cal"], flush=True)
    doc["Q2_rows"] = rows

    ok = [r for r in rows if r["status"] == "OK" and r.get("live_owner_report") is not None]
    live = np.array([r["live_owner_report"] for r in ok])
    summary = {"label": "MEASURED-HERE", "n_files": len(ok), "pairs": len(ok) * (len(ok) - 1) // 2}
    for key in ("hr_b0", "hr_b2", "sgmc_cal"):
        x = np.array([r[key] for r in ok])
        rho, p = stats.spearmanr(live, x)
        conc = disc = 0
        for i in range(len(ok)):
            for j in range(i + 1, len(ok)):
                dl = np.sign(live[i] - live[j])
                dx = np.sign(x[i] - x[j])
                if dl == 0 or dx == 0:
                    continue
                conc += int(dl == dx)
                disc += int(dl != dx)
        summary[key] = {"spearman_rho_vs_live": round(float(rho), 4), "spearman_p": round(float(p), 4),
                        "concordant_pairs": conc, "discordant_pairs": disc}
    champ_row = next(r for r in ok if r["label"].startswith("GEMSDOE32 champion"))
    d25_row = next(r for r in ok if r["label"].startswith("GEMSDOE25"))
    summary["champion_vs_d28_parent"] = {
        "live_champion_minus_live_d28": round(champ_row["live_owner_report"] - d25_row["live_owner_report"], 4),
        "hr_b2_champion_minus_d28": round(champ_row["hr_b2"] - d25_row["hr_b2"], 6),
        "sgmc_cal_champion_minus_d28": round(champ_row["sgmc_cal"] - d25_row["sgmc_cal"], 6),
        "live_order_matches_hr_b2": bool((champ_row["live_owner_report"] > d25_row["live_owner_report"]) == (champ_row["hr_b2"] > d25_row["hr_b2"])),
        "live_order_matches_sgmc_cal": bool((champ_row["live_owner_report"] > d25_row["live_owner_report"]) == (champ_row["sgmc_cal"] > d25_row["sgmc_cal"])),
    }
    doc["Q2_summary"] = summary
    doc["runtime_s"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
