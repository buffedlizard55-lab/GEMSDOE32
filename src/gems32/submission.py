"""Format-validated submission builder: mask -> GeoTIFF (+ zip) + independent receipt."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np

from . import grid


def build(mask: np.ndarray, template_path: str | Path, footprint: np.ndarray,
          out_dir: str | Path, name: str, outside: str = "nan") -> dict:
    """Write ``<name>.tif`` (and a ``.zip``) and an independent re-read receipt."""
    out_dir = Path(out_dir)
    tif = out_dir / f"{name}.tif"
    grid.write_submission(mask, template_path, tif, footprint, outside=outside)
    receipt = grid.check_submission(tif, footprint)
    receipt["rule"] = ("single-band float32 GeoTIFF, EPSG:32611, 100 m, same bounds as the "
                       "training data, every footprint pixel finite in [0, 1], "
                       f"outside = {outside}")
    zf = out_dir / f"{name}.zip"
    with zipfile.ZipFile(zf, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(tif, arcname=tif.name)
    receipt["zip"] = dict(path=str(zf), bytes=zf.stat().st_size,
                          sha256=hashlib.sha256(zf.read_bytes()).hexdigest())
    (out_dir / f"checks-{name}.json").write_text(json.dumps(receipt, indent=1) + "\n")
    return receipt
