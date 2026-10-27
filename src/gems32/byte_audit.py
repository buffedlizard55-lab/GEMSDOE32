"""Read saved submission bytes without claiming organizer/template authentication."""
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def inspect_saved_raster(path: Path) -> dict:
    """Strict all-finite primary audit; historical grid is not an authenticated template."""
    with rasterio.open(path) as src:
        arr = src.read(1)
        finite = np.isfinite(arr)
        grid_ok = (src.crs == rasterio.crs.CRS.from_epsg(32611)
                   and src.shape == (3730, 3292)
                   and src.transform == from_origin(243350, 4508550, 100, 100))
        passed = bool(src.count == 1 and src.dtypes == ('float32',)
                      and finite.all() and ((arr >= 0) & (arr <= 1)).all() and grid_ok)
        return {
            'verified_this_review': True,
            'single_band_float32': src.count == 1 and src.dtypes == ('float32',),
            'crs': str(src.crs), 'shape': list(src.shape),
            'transform': list(src.transform)[:6], 'nodata': src.nodata,
            'finite_cells': int(finite.sum()), 'total_cells': int(arr.size),
            'min': float(arr[finite].min()) if finite.any() else None,
            'max': float(arr[finite].max()) if finite.any() else None,
            'positive_pixels': int(((arr > 0) & finite).sum()),
            'historical_grid_match': grid_ok,
            'strict_primary_passed': passed,
            'reference_template_verified_this_review': False,
            'limitation': 'Historical grid only; no footprint/catalogue or authenticated template check.',
        }
