from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio

from gems32.registry_audit import _phi_binary, audit_final_dots, audit_surface


def _write(path: Path, arr: np.ndarray) -> dict:
    meta = {
        "driver": "GTiff",
        "height": arr.shape[0],
        "width": arr.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:32611",
        "transform": rasterio.transform.from_origin(243350, 4508550, 100, 100),
    }
    with rasterio.open(path, "w", **meta) as ds:
        ds.write(arr.astype(np.float32), 1)
    return meta


def test_phi_handles_products_larger_than_uint64():
    a = np.zeros(200_000, bool)
    b = np.zeros(200_000, bool)
    a[::2] = True
    b[::3] = True
    rho = _phi_binary(a, b)
    assert rho is not None and np.isfinite(rho)


def test_literal_dense_registry_fails_final_not_surface(tmp_path):
    shape = (20, 20)
    foot = np.ones(shape, bool)
    surface = np.arange(np.prod(shape), dtype=np.float32).reshape(shape)
    dots = np.zeros(shape, bool)
    dots[::4, ::4] = True
    template = tmp_path / "template.tif"
    _write(template, np.zeros(shape, np.float32))
    dense = tmp_path / "dense.tif"
    _write(dense, np.ones(shape, np.float32))
    manifest = {
        "rasters": [{"repo": "R", "path": "dense.tif", "sha256": "x", "local": "dense.tif"}],
        "n_failed": 0,
    }
    surf = audit_surface(surface, foot, manifest, root=tmp_path, template_tif=template)
    final = audit_final_dots(surface, dots, foot, manifest, root=tmp_path, template_tif=template)
    assert surf["passed"]  # constant surface has no rank-correlation above threshold
    assert not final["passed"]
    assert final["worst_within_3px_fraction"] == 1.0


def test_identical_binary_registry_fails_both_checks(tmp_path):
    shape = (20, 20)
    foot = np.ones(shape, bool)
    dots = np.zeros(shape, bool)
    dots[::3, ::3] = True
    surface = dots.astype(np.float32)
    template = tmp_path / "template.tif"
    _write(template, np.zeros(shape, np.float32))
    same = tmp_path / "same.tif"
    _write(same, surface)
    manifest = {
        "rasters": [{"repo": "R", "path": "same.tif", "sha256": "x", "local": "same.tif"}],
        "n_failed": 0,
    }
    assert not audit_surface(surface, foot, manifest, root=tmp_path, template_tif=template)["passed"]
    result = audit_final_dots(surface, dots, foot, manifest, root=tmp_path, template_tif=template)
    assert not result["passed"]
    assert result["worst_abs_spearman"] > 0.99
    assert result["worst_within_3px_fraction"] == 1.0
