#!/usr/bin/env python3
"""Retrospective gate audit; never trains, generates predictions, or submits to DrivenData.

Requires the sample, existing_faults and lattice entries from registry/data_manifest.json
in GEMS_DATA_DIR. Does not equate a binary final raster with its missing pre-placement surface.
"""
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gems32.paths import data_dir
from gems32.submission import audit_geotiff, sha256_file


def main():
    root = data_dir()
    manifest = json.loads((ROOT / 'registry/data_manifest.json').read_text())
    destinations = ['sample_submission.tif', 'existing_faults.tif',
                    'scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif']
    for dest in destinations:
        entry = next(e for e in manifest['files'] if e['dest'] == dest)
        if sha256_file(root / dest) != entry['sha256']:
            raise ValueError(f'Unverified mirror: {dest}')
    with rasterio.open(root / destinations[0]) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(root / destinations[1]) as ds:
        labels = ds.read(1) > 0
    with rasterio.open(root / destinations[2]) as ds:
        a = ds.read(1)
        lattice = np.isfinite(a) & (a > 0) & foot
    distance = distance_transform_edt(~lattice)
    primary = json.loads((ROOT / 'registry/submission_build.json').read_text())['file']['path']
    arena = json.loads((ROOT / 'registry/arena41_submission.json').read_text())['file']
    paths = [ROOT / primary, ROOT / 'docs/downloads' / arena]
    rows = []
    for p in paths:
        receipt = audit_geotiff(p, foot, labels, template_tif=root / destinations[0])
        with rasterio.open(p) as ds:
            dots = (ds.read(1) > 0) & foot
        frac = float((distance[dots] <= 3).mean()) if dots.any() else None
        rows.append(dict(file=p.relative_to(ROOT).as_posix(), validator=receipt,
                         registry_reference=destinations[2], within_3px_fraction=frac,
                         literal_duplicate=frac is not None and frac > .70,
                         surface_rank_correlation=None, surface_status='not available; not inferred from dots',
                         ok_to_submit=False, verdict='negative'))
    result = dict(schema=1, kind='retrospective audit, not a new experiment',
                  provenance='hash-pinned owner mirrors, not organizer-authenticated',
                  method_lane=None, new_experiments=0, weekly_slots_used=0,
                  rule='literal directional >70% within 3px: log duplicate and STOP; no density exemption',
                  results=rows, ok_to_submit=False)
    out = ROOT / 'docs/data/protocol-audit.json'
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(out.relative_to(ROOT))
    for row in rows:
        print(row['file'], row['within_3px_fraction'], 'DO NOT SUBMIT')


if __name__ == '__main__':
    main()
