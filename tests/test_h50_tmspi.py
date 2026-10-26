"""H50 TM-SPI artifact contract: format, uniqueness vs champion, fail-closed submit flag."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

from gems32.tmspi import geometric_mean_concordance, spi_contact_weight

ROOT = Path(__file__).resolve().parents[1]
STEM = "gemsdoe32-h50-tmspi-dualconcord-37654-20261026T214025Z-f0e385b9"
ZEROS = ROOT / "docs" / "downloads" / f"{STEM}-zeros.tif"
ZIP = ROOT / "docs" / "downloads" / f"{STEM}-zeros.zip"
CARD = ROOT / "evidence" / "h50_tmspi_run_card.json"
STATUS = ROOT / "registry" / "current_status.json"
CHAMP = ROOT / "docs" / "downloads" / "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
EXPECTED_SHA = "c534effe023f2876b08239384d075be313d489a8dc3bf8dbf22f7d6509872112"


def test_h50_zeros_tif_is_portal_safe_and_hashed():
    import hashlib

    assert ZEROS.is_file() and ZIP.is_file()
    sha = hashlib.sha256(ZEROS.read_bytes()).hexdigest()
    assert sha == EXPECTED_SHA
    with rasterio.open(ZEROS) as ds:
        assert ds.count == 1 and ds.dtypes[0] == "float32"
        assert "32611" in str(ds.crs)
        arr = ds.read(1)
    assert arr.shape == (3730, 3292)
    assert np.isfinite(arr).all()
    assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
    assert int((arr > 0).sum()) == 37121


def test_h50_is_unique_vs_champion_and_not_authorized():
    pytest.importorskip("scipy")
    from scipy.ndimage import distance_transform_edt

    card = json.loads(CARD.read_text())
    st = json.loads(STATUS.read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert st["any_file_ok_to_submit"] is False
    assert card["leakage_canary"]["passed"] is True
    assert card["leakage_canary"]["max_single_feature_auc"] <= 0.90
    if CHAMP.is_file():
        with rasterio.open(ZEROS) as ds:
            h50 = ds.read(1) > 0
        with rasterio.open(CHAMP) as ds:
            champ = ds.read(1) > 0
        ov = float((distance_transform_edt(~champ)[h50] <= 3).mean())
        assert ov <= 0.70


def test_floored_concordance_prefers_dual_domain():
    foot = np.ones((6, 6), bool)
    mag = np.zeros((6, 6))
    grav = np.zeros((6, 6))
    mag[1, 1] = 4.0
    grav[1, 1] = 4.0
    mag[4, 4] = 4.0
    out = geometric_mean_concordance(mag, grav, foot)
    assert out[1, 1] > out[4, 4] > 0
    assert float(spi_contact_weight(np.array([0.05]))[0]) > 0.5
