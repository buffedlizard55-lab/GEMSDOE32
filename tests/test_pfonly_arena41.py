"""Arena41 PF-ONLY lane: operator unit tests + shipped-file gate tests."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]

def test_dot_thin_respects_min_distance_and_budget():
    from gems32.pfonly import dot_thin
    rng = np.random.default_rng(0)
    f = rng.random((120, 120)).astype(np.float32)
    m = dot_thin(f, np.ones_like(f, bool), 150, min_dist=2.8)
    assert m.sum() == 150
    ys, xs = np.nonzero(m)
    for i in range(len(ys)):
        d2 = (ys[i+1:] - ys[i])**2 + (xs[i+1:] - xs[i])**2
        assert (d2 >= 2.8**2 - 1e-9).all()

def test_dot_thin_takes_highest_first():
    from gems32.pfonly import dot_thin
    f = np.zeros((20, 20), np.float32); f[5, 5] = 0.9; f[5, 6] = 1.0; f[15, 15] = 0.8
    m = dot_thin(f, np.ones_like(f, bool), 2, min_dist=2.8)
    assert m[5, 6] and m[15, 15] and not m[5, 5]

def test_upward_continue_damps_short_wavelengths():
    from gems32.pfonly import upward_continue
    x = np.zeros((64, 64), np.float32); x[::2] = 1.0  # Nyquist stripes
    up = upward_continue(x, 3.0)
    assert float(np.std(up)) < 0.25 * float(np.std(x))
    slow = np.tile(np.sin(np.linspace(0, 2*np.pi, 64)), (64, 1)).astype(np.float32)
    ups = upward_continue(slow, 3.0)
    assert float(np.std(ups)) > 0.5 * float(np.std(slow))

def test_pooled_dti_matches_direct_formula():
    from gems32.pfonly import pooled_dti_from_folds
    folds = {"a": {"tp": 100.0, "fp": 50.0, "n_truth": 200}, "b": {"tp": 20.0, "fp": 30.0, "n_truth": 80}}
    r = pooled_dti_from_folds(folds)
    expect = 120.0 / (120.0 + 0.2*80.0 + 0.8*160.0)
    assert abs(r["pooled_dti"] - expect) < 1e-9
    assert r["n_withheld_positives"] == 280

def test_arena41_file_gates_and_verdict_consistent():
    reg = ROOT / "registry" / "arena41_submission.json"
    if not reg.exists():
        pytest.skip("arena41 build not in this checkout")
    a = json.loads(reg.read_text())
    tif = ROOT / "docs" / "downloads" / a["file"]
    assert tif.is_file()
    import hashlib
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == a["sha256"]
    chk = json.loads((ROOT / "docs" / "downloads" / f"checks-{a['file']}.json").read_text())
    c = chk["checks"]
    assert c["portal_legal"] and c["values_outside_0_1"] == 0 and c["nan_cells"] == 0
    assert c["dots_on_catalogue"] == 0 and c["dots_within_200m_catalogue"] == 0
    assert chk["profile"]["nodata"] == "None"
    # verdict must agree with the pre-registered gates recorded at build time
    assert a["verdict"] == "negative" and a["ok_to_submit"] is False
    assert len(a["note_le140"]) <= 140

def test_champion_zip_contains_the_tif():
    import zipfile
    z = ROOT / "docs" / "downloads" / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.zip"
    if not z.exists():
        pytest.skip("champion zip absent")
    names = zipfile.ZipFile(z).namelist()
    assert names == ["gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"]
    assert zipfile.ZipFile(z).getinfo(names[0]).file_size > 100_000
