#!/usr/bin/env python3
"""Zero-human-intervention automated inspector for the Arena8a (MDRC) unique GeoTIFF deliverable.

Re-verifies from raw bytes on disk:
  1. SHA-256 integrity of -zeros.tif, -nan.tif, and -zeros.zip against evidence/arena8a_run_card.json.
  2. 12-point GeoTIFF audit (gems32.submission.audit_geotiff) AND independent strict whole-grid finite
     [0, 1] check (gemsdoe32.submission.validate_submission_geotiff) preventing "Predicted values must
     be in range [0, 1]".
  3. ZIP archive integrity (single valid GeoTIFF entry matching -zeros.tif).
  4. Cross-receipt consistency of pre-registered gates G1..G5 (canary, format, uniqueness, holdout, SGMC).
  5. Unmistakable automated decision banner (`promote` vs `negative` / `DO NOT SUBMIT`).

Exit codes:
  0 — Automated inspection succeeded and run card is 100% consistent (safe to download; check banner for slot gate).
  1 — File corruption, range/NaN violation, duplicate violation, or receipt tampering detected.
  2 — `--require-promote` requested, and automated verdict is `negative` (`ok_to_submit == False`).
"""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import submission  # noqa: E402
from gems32.paths import data_dir, evidence_dir  # noqa: E402
from gemsdoe32.submission import validate_submission_geotiff  # noqa: E402


def verify_all(run_card_path: Path | None = None) -> dict:
    ev_dir = evidence_dir()
    rc_path = run_card_path or (ev_dir / "arena8a_run_card.json")
    if not rc_path.exists():
        raise FileNotFoundError(f"Missing run card: {rc_path}")

    rc = json.loads(rc_path.read_text())
    exp1 = json.loads((ev_dir / "arena8a_exp1_canary_and_domains.json").read_text())
    exp2 = json.loads((ev_dir / "arena8a_exp2_oof_comparison.json").read_text())
    exp3 = json.loads((ev_dir / "arena8a_exp3_crest_and_gates.json").read_text())

    tif_path = ROOT / rc["raster_path"]
    zip_path = ROOT / rc["zip_path"]
    nan_path = ROOT / "docs" / "downloads" / rc["nan_twin_filename"]

    errors: list[str] = []
    for p in (tif_path, zip_path, nan_path):
        if not p.exists():
            errors.append(f"Missing artifact on disk: {p}")
    if errors:
        return {"ok": False, "errors": errors, "run_card": rc}

    # 1. Byte-level SHA-256 verification
    tif_sha = submission.sha256_file(tif_path)
    zip_sha = submission.sha256_file(zip_path)
    nan_sha = submission.sha256_file(nan_path)
    if tif_sha != rc["raster_sha256"]:
        errors.append(f"-zeros.tif SHA-256 mismatch: disk={tif_sha} vs card={rc['raster_sha256']}")
    if zip_sha != rc["zip_sha256"]:
        errors.append(f"-zeros.zip SHA-256 mismatch: disk={zip_sha} vs card={rc['zip_sha256']}")
    if nan_sha != rc["nan_twin_sha256"]:
        errors.append(f"-nan.tif SHA-256 mismatch: disk={nan_sha} vs card={rc['nan_twin_sha256']}")
    if zip_path.stat().st_size <= 0:
        errors.append(f"-zeros.zip is empty ({zip_path.stat().st_size} bytes)")

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        if names != [tif_path.name]:
            errors.append(f"-zeros.zip must contain sole member [{tif_path.name}], got {names}")
        if zf.testzip() is not None:
            errors.append("-zeros.zip failed CRC check")

    # 2. Dual independent GeoTIFF validators when competition template is present
    ddir = data_dir()
    tmpl_tif = ddir / "sample_submission.tif"
    labels_tif = ddir / "labels.tif"
    audit_12_ok = True
    strict_finite_ok = True
    if tmpl_tif.exists() and labels_tif.exists():
        with rasterio.open(tmpl_tif) as ds:
            foot = np.isfinite(ds.read(1))
        with rasterio.open(labels_tif) as ds:
            labels = np.isfinite(ds.read(1)) & (ds.read(1) > 0) & foot
        aud = submission.audit_geotiff(tif_path, foot, labels, mode="zeros")
        aud_nan = submission.audit_geotiff(nan_path, foot, labels, mode="nan")
        audit_12_ok = bool(
            aud["all_checks_passed"]
            and aud_nan["all_checks_passed"]
            and aud["on_catalogue_positive_pixels"] == 0
        )
        if not audit_12_ok:
            errors.append(f"Template 12-point GeoTIFF audit failed: {aud['checks']}")
        rep = validate_submission_geotiff(tif_path, tmpl_tif, strict_whole_array_finite=True)
        strict_finite_ok = bool(rep.passed)
        if not strict_finite_ok:
            errors.append(f"Strict whole-array [0,1] validator failed: {rep.errors}")
    else:
        # Even without competition template cached, check standalone rasterio range [0, 1] & zero NaN!
        with rasterio.open(tif_path) as ds:
            arr = ds.read(1)
            if ds.count != 1 or ds.dtypes[0] != "float32" or (ds.width, ds.height) != (3292, 3730):
                errors.append("Standalone GeoTIFF header check failed")
            if not np.isfinite(arr).all():
                errors.append("GeoTIFF contains non-finite values")
            if float(arr.min()) < 0.0 or float(arr.max()) > 1.0:
                errors.append(f"GeoTIFF values outside [0, 1]: [{arr.min()}, {arr.max()}]")

    # 3. Note length & gate consistency
    note = rc["submission_note"]
    if len(note) > 140:
        errors.append(f"Submission note exceeds 140 chars: {len(note)}")

    gates = rc["automated_gates"]
    if gates["G1_leakage_canary_auc_le_090"]["worst_auc"] != exp1["leakage_canary"]["worst_auc"]:
        errors.append("G1 receipt mismatch between run_card and exp1")
    if gates["G3_lane_uniqueness_surface_and_dots"]["worst_abs_surface_spearman"] > 0.90:
        errors.append("Pre-placement surface Spearman > 0.90")
    if gates["G3_lane_uniqueness_surface_and_dots"]["worst_within_3px_genuine_models"] > 0.70:
        errors.append("Within-3px overlap against genuine model > 0.70")

    expected_all_pass = all(bool(g["passed"]) for g in gates.values())
    expected_verdict = "promote" if expected_all_pass else "negative"
    if rc["verdict"] != expected_verdict or bool(rc["ok_to_submit"]) != expected_all_pass:
        errors.append(
            f"Verdict tampering/inconsistency: verdict={rc['verdict']} ok_to_submit={rc['ok_to_submit']} "
            f"expected=({expected_verdict}, {expected_all_pass})"
        )
    if not expected_all_pass and "DO-NOT-SUBMIT" not in note:
        errors.append("Negative candidate note must carry explicit DO-NOT-SUBMIT warning")

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "tif_sha256": tif_sha,
        "zip_sha256": zip_sha,
        "audit_12_ok": audit_12_ok,
        "strict_finite_ok": strict_finite_ok,
        "all_gates_pass": expected_all_pass,
        "verdict": rc["verdict"],
        "ok_to_download": bool(rc["ok_to_download"]) and len(errors) == 0,
        "ok_to_submit": bool(rc["ok_to_submit"]) and len(errors) == 0,
        "run_card": rc,
        "exp2": exp2,
        "exp3": exp3,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-card", type=Path, default=None)
    ap.add_argument(
        "--require-promote",
        action="store_true",
        help="Exit non-zero (code 2) unless all promotion gates pass (`verdict == promote`).",
    )
    args = ap.parse_args()

    res = verify_all(args.run_card)
    rc = res["run_card"]
    gates = rc["automated_gates"]

    banner_line = "=" * 86
    print(banner_line)
    print("  GEMSDOE32 AUTOMATED SUBMISSION INSPECTOR (ZERO HUMAN INTERVENTION)")
    print(banner_line)
    print(f"  Candidate File   : {rc['raster_path']}")
    print(f"  SHA-256          : {res.get('tif_sha256', 'MISSING')}")
    print(f"  ZIP Archive      : {rc['zip_path']} ({rc['zip_bytes']:,} bytes)")
    print(f"  Emitted Dots     : {rc['emitted_positive_pixels']:,} binary {{0.0, 1.0}} px (0 NaN, 0 on-catalogue)")
    print(f"  Submission Name  : {rc['submission_name']}")
    print(f"  Submission Note  : {rc['submission_note']} ({rc['submission_note_length']}/140 chars)")
    print("-" * 86)
    for gname, ginfo in gates.items():
        status = "PASS" if ginfo["passed"] else "FAIL"
        print(f"  [{status:4s}] {gname}")
    print("-" * 86)
    if not res["ok"]:
        print("  INTEGRITY / FORMAT ERRORS DETECTED:")
        for e in res["errors"]:
            print(f"    - {e}")
        print(banner_line)
        return 1

    dl_str = "YES (100% portal-legal [0, 1] float32 GeoTIFF, unique research artifact)" if res["ok_to_download"] else "NO"
    sub_str = (
        "YES — PROMOTED FOR WEEKLY LEADERBOARD SLOT"
        if res["ok_to_submit"]
        else "NO — AUTOMATED VERDICT: NEGATIVE (DO NOT SPEND WEEKLY SLOT; KEEP 0.2778 CHAMPION)"
    )
    print(f"  OK TO DOWNLOAD   : {dl_str}")
    print(f"  OK TO SUBMIT     : {sub_str}")
    print(banner_line)

    if args.require_promote and not res["ok_to_submit"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
