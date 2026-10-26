#!/usr/bin/env python3
"""Project Arena9 run-card facts into the fail-closed release registries."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    card_path = ROOT / "evidence" / "arena9_run_card.json"
    card = json.loads(card_path.read_text())
    if card["verdict"] != "negative" or card["ok_to_submit_to_live_portal"] is not False:
        raise RuntimeError("This updater is frozen for the negative Arena9 result")

    status_path = ROOT / "registry" / "current_status.json"
    status = json.loads(status_path.read_text())
    hr = card["holdout_dti"]
    sg = card["off_catalogue_holdout_dti"]
    sa = card["correlation_overlap_vs_registry"]["surface_before_placement"]
    fa = card["correlation_overlap_vs_registry"]["final_dots"]
    validator = card["validator_output"]
    audit_path = str(Path(card["raster_path"]).with_name(Path(card["raster_path"]).stem.replace("-zeros", "-audit") + ".json"))
    zip_path = str(Path(card["raster_path"]).with_suffix(".zip"))
    status["updated_utc"] = card["generated_utc"]
    status["any_file_ok_to_submit"] = False
    status["headline"] = "No file in this repository is authorized for upload; Arena9 is a format-valid negative result."
    status["arena9_candidate"] = {
        "file": card["raster_path"],
        "zip": zip_path,
        "receipt": audit_path,
        "run_card": "evidence/arena9_run_card.json",
        "preregistration": "docs/research/arena9-preregistration-and-hypotheses.md",
        "sha256": card["raster_sha256"],
        "bytes": (ROOT / card["raster_path"]).stat().st_size,
        "dots": card["validator_output"]["independent_validator"]["checks"][0].get("dots", 37654),
        "submission_name": card["submission_name"],
        "note": card["submission_note"],
        "verdict": "DO NOT SUBMIT",
        "ok_to_download": True,
        "ok_to_submit": False,
        "hypothesis": "A9-H1 physics-guarded reliable-negative PU on the 57-channel MDRC stack",
        "reasons": [
            f"Primary HOLDOUT-DTI failed: {hr['selected_pooled_dti']:.5f} [{hr['selected_ci95'][0]:.5f}, {hr['selected_ci95'][1]:.5f}] < Champion {hr['champion_02778_same_evaluator']:.5f} and repository best H38 {hr['repository_best_h38_same_evaluator']:.5f}; paired delta vs Champion {hr['paired_delta_vs_champion']['point_delta']:+.5f} [{hr['paired_delta_vs_champion']['ci95'][0]:+.5f}, {hr['paired_delta_vs_champion']['ci95'][1]:+.5f}].",
            f"Independent off-catalogue SGMC improved to {sg['selected_prevalence_calibrated_dti']:.5f} [{sg['selected_ci95'][0]:.5f}, {sg['selected_ci95'][1]:.5f}] vs Champion {sg['champion_prevalence_calibrated_dti']:.5f}, but proxy improvement cannot override the failed primary holdout.",
            f"Surface uniqueness passed across {sa['registry_rasters']} refreshed registry files (max |Spearman| {sa['worst_abs_spearman']:.5f}), but final-dot lane uniqueness failed at {fa['worst_within_3px_fraction']:.2%} > 70% against the registered spacing-5 calibration lattice.",
            "The dot mask is not pixel-identical to any refreshed registry raster and the GeoTIFF is cryptographically new, but that is weaker than the mandatory lane-overlap rule.",
            "The full-grid format validator passes; format validity alone is not scientific or slot authorization."
        ],
        "holdout": {
            "A9 PGRN80": {"dti": hr["selected_pooled_dti"], "ci95": hr["selected_ci95"]},
            "0.2778 Champion": {"dti": hr["champion_02778_same_evaluator"], "ci95": hr["champion_ci95"]},
            "H38 repository best": {
                "dti": hr["repository_best_h38_same_evaluator"],
                "ci95": [0.100533, 0.132040]
            }
        },
        "holdout_label": f"HOLDOUT-DTI ({hr['evaluator_version']}, {hr['n_withheld_positives']} withheld positives, 95% spatial-block CI)",
        "off_catalogue_instrument": {
            "A9 PGRN80": {"dti": sg["selected_prevalence_calibrated_dti"], "ci95": sg["selected_ci95"]},
            "0.2778 Champion": {"dti": sg["champion_prevalence_calibrated_dti"], "ci95": sg["champion_ci95"]}
        },
        "off_catalogue_label": f"HOLDOUT-DTI ({sg['evaluator_version']}, {sg['n_withheld_positives']} off-catalogue SGMC positives, 95% spatial-block CI)",
        "surface_worst_abs_spearman": sa["worst_abs_spearman"],
        "final_worst_abs_spearman": fa["worst_abs_spearman"],
        "final_worst_within_3px": fa["worst_within_3px_fraction"],
        "registry_rasters": fa["registry_rasters"],
        "exact_mask_matches": 0,
        "format_test_registry_irregularities": fa["malformed_or_missing"],
        "gates": card["automated_gates"]
    }
    status_path.write_text(json.dumps(status, indent=1) + "\n")

    # The legacy site catalogue still drives a few historical pages. Point its primary metadata at
    # Arena9 as the newest audit artifact while retaining its fail-closed verdict and the R6 history.
    submission_path = ROOT / "registry" / "submission_build.json"
    submission = json.loads(submission_path.read_text())
    old_primary = {
        "name": submission.get("name"),
        "record": "evidence/round6_run_card.json",
        "withdrawn": True,
        "reason": "Superseded as the headline audit artifact by Arena9; remains DO NOT SUBMIT."
    }
    previous = submission.setdefault("previous_primaries", [])
    if (old_primary["name"] and old_primary["name"] != Path(card["raster_path"]).stem
            and not any(item.get("name") == old_primary["name"] for item in previous)):
        previous.insert(0, old_primary)
    zeros_bytes = (ROOT / card["raster_path"]).stat().st_size
    bundle_audit = json.loads((ROOT / audit_path).read_text())
    nan_path = Path(card["raster_path"]).with_name(card["nan_twin_filename"])
    submission.update({
        "name": Path(card["raster_path"]).stem,
        "note": card["submission_note"],
        "status_line": card["decision"],
        "file": {
            "path": card["raster_path"], "sha256": card["raster_sha256"],
            "bytes": zeros_bytes, "positive_px": fa["candidate_dots"]
        },
        "file_zeros": {"path": card["raster_path"], "sha256": card["raster_sha256"], "bytes": zeros_bytes},
        "zip": {
            "path": zip_path, "sha256": card["zip_sha256"],
            "bytes": (ROOT / zip_path).stat().st_size
        },
        "candidate_id": card["submission_name"],
        "hypothesis": "A9-H1-MDRC-PGRN-PU",
        "verdict": "negative",
        "ok_to_submit": False,
        "on_catalogue_pixels": validator["on_catalogue_positive_pixels"],
        "catalogue_hidden_mean": hr["selected_pooled_dti"],
        "drift_corrected_holdout_mean": hr["selected_pooled_dti"],
        "sgmc_prevalence_calibrated_dti": sg["selected_prevalence_calibrated_dti"],
        "pack": [{
            "role": "NaN-outside archival twin; not portal-safe under strict-finite mode",
            "path": str(nan_path),
            "sha256": bundle_audit["nan_tif"]["sha256"],
            "bytes": (ROOT / nan_path).stat().st_size
        }],
        "evidence": "evidence/arena9_run_card.json",
        "historical_run_verdict": "negative",
        "historical_ok_to_submit": False,
        "status_line_current": card["decision"],
        "arena9_candidate": "evidence/arena9_run_card.json"
    })
    submission.pop("sgmc_exact_dti", None)
    submission.pop("sgmc_exact_champion_dti", None)
    submission_path.write_text(json.dumps(submission, indent=1) + "\n")

    review_path = ROOT / "evidence" / "current_release_review.json"
    review = json.loads(review_path.read_text())
    review["reviewed_utc"] = card["generated_utc"]
    review["decision_scope"] = "Repository-wide release authorization after the Arena9 PGRN-PU run; historical artifact findings are preserved."
    previous_artifact = review.get("artifact")
    if previous_artifact and previous_artifact.get("path") != card["raster_path"]:
        review.setdefault("historical_artifact_review", previous_artifact)
    review["artifact"] = {
        "path": card["raster_path"],
        "sha256": card["raster_sha256"],
        "format_byte_audit": {
            "verified_this_review": validator["independent_validator_passed"],
            "single_band_float32": validator["dtype"] == "float32",
            "crs": validator["crs"],
            "shape": validator["shape"],
            "transform": validator["transform"],
            "nodata": validator["nodata"],
            "finite_cells": validator["full_grid_finite_pixels"],
            "total_cells": validator["shape"][0] * validator["shape"][1],
            "min": validator["min"],
            "max": validator["max"],
            "positive_pixels": fa["candidate_dots"]
        },
        "reference_grid_reaudit": {
            "status": "PASS" if validator["independent_validator_passed"] else "FAIL",
            "reference_template_provenance": "hash-pinned owner mirror; not organizer-authenticated",
            "validator": "scripts/check_submission.py --strict-finite",
            "checks": [check["name"] for check in validator["independent_validator"]["checks"]],
            "limitation": "Format/grid pass only; not an organizer receipt, scientific validation, or release authorization."
        }
    }
    review["latest_candidate"] = {
        "run_card": "evidence/arena9_run_card.json",
        "raster": card["raster_path"],
        "sha256": card["raster_sha256"],
        "verdict": card["verdict"],
        "format_passed": card["automated_gates"]["G5_format_and_range"],
        "primary_holdout_passed": card["automated_gates"]["G2_holdout_beats_champion_and_repo_best"],
        "literal_registry_passed": card["automated_gates"]["G4_final_registry_unique"]
    }
    review["submission_authorization"] = {
        "ok_to_download_and_submit": False,
        "verdict": "negative",
        "slot_used": False,
        "reasons": status["arena9_candidate"]["reasons"],
        "next_required": (
            "Do not upload Arena9. A future lane must beat H38 on the same fold-local hide-and-recover evaluator "
            "and satisfy the literal all-registry overlap rule. The spacing-5 registry lattice makes a 37,654-dot "
            "map infeasible under that rule; do not invent an exemption—resolve the protocol or use a preregistered "
            "lower budget before any further experiment."
        )
    }
    review_path.write_text(json.dumps(review, indent=2) + "\n")
    print("Updated registry/current_status.json and evidence/current_release_review.json from Arena9 run card")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
