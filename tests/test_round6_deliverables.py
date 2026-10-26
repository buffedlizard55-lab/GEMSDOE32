"""Tests for Round-6 shared tool fixes, Run Card schema, 9-site audit, and site consistency."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

from gems32.features import _fill_nearest
from gems32.holdout import (
    DRAWS,
    FOLDS,
    HoldoutContext,
    PreparedCell,
    evaluate_hide_and_recover,
    evaluate_sgmc_with_ci,
)
from gems32.metric import kernel

ROOT = Path(__file__).resolve().parents[1]


def test_fill_nearest_prevents_footprint_border_cliff():
    foot = np.zeros((20, 20), dtype=bool)
    foot[4:16, 4:16] = True
    raw = np.full((20, 20), -3.4028235e38, dtype=np.float32)
    raw[foot] = 1500.0
    filled, idx = _fill_nearest(raw, foot)
    assert idx[0].shape == (20, 20)
    assert np.isfinite(filled).all()
    assert np.allclose(filled, 1500.0)

    empty_filled, _ = _fill_nearest(raw, np.zeros((20, 20), dtype=bool))
    assert np.isfinite(empty_filled).all()
    assert np.allclose(empty_filled, 0.0)


def test_evaluate_hide_and_recover_and_sgmc_with_ci():
    foot = np.ones((80, 80), dtype=bool)
    labels = np.zeros((80, 80), dtype=bool)
    labels[10, 10:30] = True
    hidden = np.zeros((80, 80), dtype=bool)
    hidden[55, 20:50] = True
    sgmc = np.zeros((80, 80), dtype=bool)
    sgmc[65, 15:65] = True

    d_vis = distance_transform_edt(~labels).astype(np.float32)
    k_hid = kernel(distance_transform_edt(~hidden)).astype(np.float32)
    cells = []
    for ds in DRAWS:
        for f in FOLDS:
            cells.append(
                PreparedCell(
                    key=f"draw{ds}_fold{f}",
                    fold=f,
                    seed=ds * 10 + f,
                    bbox=(slice(0, 80), slice(0, 80)),
                    active_sub=~labels,
                    truth_coords=np.nonzero(hidden),
                    k_dg_sub=k_hid,
                    n_truth=int(hidden.sum()),
                    d_vis_sub=d_vis,
                )
            )
    ctx = HoldoutContext(
        foot=foot,
        labels=labels,
        sgmc_off=sgmc,
        near_visible=d_vis <= 3.0,
        quad=np.zeros((80, 80), dtype=np.int8),
        quad_bboxes={f: (slice(0, 80), slice(0, 80)) for f in FOLDS},
        cells=cells,
        sgmc_truth_coords=np.nonzero(sgmc),
        sgmc_k_dg=kernel(distance_transform_edt(~sgmc)).astype(np.float32),
        sgmc_n_truth=int(sgmc.sum()),
        sgmc_quad_truth_coords={f: np.nonzero(sgmc) for f in FOLDS},
        sgmc_quad_n_truth={f: int(sgmc.sum()) for f in FOLDS},
    )
    near_vis_noise = np.zeros((80, 80), dtype=bool)
    near_vis_noise[11, 10:30] = True
    pred = hidden | near_vis_noise
    res_b0 = evaluate_hide_and_recover(pred, ctx, b_visible_px=0.0, n_boot=32, seed=3, name="syn_b0")
    res_b2 = evaluate_hide_and_recover(pred, ctx, b_visible_px=2.0, n_boot=32, seed=3, name="syn_b2")
    assert res_b2["evaluator_version"] == "GEMSDOE32-HIDE-RECOVER-v3.0"
    assert res_b2["pooled_dti"] > res_b0["pooled_dti"]
    lo, hi = res_b2["ci95_cluster_bootstrap"]
    assert 0.0 <= lo <= hi <= 1.0

    sg = evaluate_sgmc_with_ci(sgmc, ctx, n_boot=32, seed=5, name="syn_sgmc")
    assert sg["evaluator_version"] == "GEMSDOE32-SGMC-CAL-v3.0"
    assert sg["sgmc_raw_pooled_dti"] > 0.9
    slo, shi = sg["sgmc_calibrated_ci95"]
    assert 0.0 <= slo <= shi <= 1.0


def test_h38_run_card_and_shipped_geotiff_integrity():
    rc = json.loads((ROOT / "evidence" / "h38_run_card.json").read_text())
    required = {
        "hypothesis",
        "mechanism",
        "named_non_fault_mimic",
        "holdout_dti",
        "registry_uniqueness",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "submission_note",
        "verdict",
    }
    assert required.issubset(rc.keys())
    assert len(rc["submission_note"]) <= 140
    assert rc["verdict"] in ("promote", "negative")
    assert rc["verdict"] == "negative"
    assert rc["ok_to_download_and_submit"] is False

    tif_path = ROOT / "docs" / "downloads" / rc["raster_filename"]
    assert tif_path.is_file()
    assert hashlib.sha256(tif_path.read_bytes()).hexdigest() == rc["raster_sha256"]

    val = rc["validator_output"]
    assert val["all_13_checks_passed"] is True
    assert val["nan_inside_footprint"] == 0
    assert val["values_in_0_1"] is True
    assert val["full_grid_finite_pixels"] == 12_279_160
    assert val["on_catalogue_positive_pixels"] == 0
    assert val["emitted_positive_pixels"] == 37_654

    with rasterio.open(tif_path) as ds:
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert str(ds.crs) == "EPSG:32611"
        assert (ds.height, ds.width) == (3730, 3292)
        assert ds.nodata is None
        arr = ds.read(1)
        assert np.isfinite(arr).all()
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0


def test_hypotheses_layers_are_lists_and_nine_sites_audited():
    hyp = json.loads((ROOT / "registry" / "hypotheses.json").read_text())
    for h in hyp["hypotheses"]:
        assert isinstance(h["layers"], list), f"{h['id']} layers must be list[str], got {type(h['layers'])}"

    nine = json.loads((ROOT / "evidence" / "nine_site_executive_audit_20261026.json").read_text())
    site_names = [s["site"] for s in nine["focus_sites"]]
    assert site_names == [
        "GEMSDOE24",
        "GEMSDOE25",
        "GEMSDOE27",
        "GEMSDOE28",
        "GEMSDOE30",
        "GEMSDOE31",
        "GEMSDOE32",
        "GEMSDOE33",
        "GEMSDOE36",
    ]
    assert nine["overall_focus_9_best"]["site"] == "GEMSDOE32"
    assert nine["overall_focus_9_best"]["score"] == 0.2778


def test_no_contradictory_promote_banner_when_gate_is_negative():
    sub = json.loads((ROOT / "registry" / "submission_build.json").read_text())
    assert sub["ok_to_submit"] is False
    assert sub["verdict"] == "negative"
    for rel in ("index.html", "executive-summary.html", "docs/index.html", "docs/executive-summary.html"):
        txt = (ROOT / rel).read_text()
        assert "VERDICT: DO NOT SUBMIT TO PORTAL" in txt
        assert "ONE-CLICK DOWNLOAD .TIF (VALIDATED READY)" not in txt
        assert "[0.00000, 0.00000]" not in txt
        assert "0.10053" in txt and "0.13204" in txt
        assert "Format Receipt (20/20 PASS)" in txt


def test_readme_relative_links_and_cli_help():
    import re
    import subprocess
    import sys

    readme = (ROOT / "README.md").read_text()
    for target in re.findall(r"\]\(([^)#\s]+)\)", readme):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        assert (ROOT / target).exists(), f"Broken relative link in README.md: {target}"

    for cli in ("scripts/evaluate_holdout.py", "scripts/submission_writer.py"):
        r = subprocess.run([sys.executable, str(ROOT / cli), "--help"], capture_output=True, text=True, check=False)
        assert r.returncode == 0, f"{cli} --help failed: {r.stderr}"
