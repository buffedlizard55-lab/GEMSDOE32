#!/usr/bin/env python3
"""Re-fetch nine named historical winners at current pinned heads; audit, never promote.

This is a bounded nine-winner review, NOT a complete submission/registry census.
Score claims are supplied by the user; GitHub bytes do not authenticate a score.
Use the shared registry fetcher, shared format validator and shared literal gate.
"""
from __future__ import annotations

import concurrent.futures as cf
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import subprocess

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gems32.paths import data_dir
from gems32.release_gate import compare_registry, dot_budget_feasibility
from gemsdoe32.submission import validate_submission_geotiff
from audit_nine_site_best import SITES
from fetch_focus_registry import fetch_one, list_repo
from restore_data import restore_entry, sha256_file


def binary_spearman(a: np.ndarray, b: np.ndarray) -> float | None:
    """Exact Spearman for tied binary samples equals their phi coefficient."""
    n = a.size
    na, nb = int(a.sum()), int(b.sum())
    if na in (0, n) or nb in (0, n):
        return None
    both = int(np.count_nonzero(a & b))
    return float((n * both - na * nb) / np.sqrt(float(na * nb) * (n-na) * (n-nb)))


def fetch_winner(spec):
    site, stem, suffix, claim = spec
    ref, files = list_repo(site)
    matches = [f for f in files if Path(f['path']).name == suffix]
    if len(matches) != 1:
        raise RuntimeError(f'{site}: expected one exact historical filename; found {len(matches)}')
    f = matches[0]
    row = fetch_one(site, ref, f['path'], f['size'], ROOT / '.cache/registry', f['sha'])
    if row['status'] != 'ok':
        raise RuntimeError(f'{site}: pinned artifact fetch failed: {row}')
    row.update(leaderboard_name=stem, unconfirmed_user_claim=claim,
               claim_status='USER-REPORTED; no organizer receipt; not an estimated or confirmed score',
               leaderboard_estimate=None,
               download_url=f"https://github.com/buffedlizard55-lab/{site}/blob/{ref}/{f['path']}?raw=true")
    return row


def inspect(path: Path, template: Path, foot: np.ndarray, labels: np.ndarray):
    validation = validate_submission_geotiff(path, template, strict_whole_array_finite=True).to_dict()
    with rasterio.open(path) as ds:
        arr = ds.read(1)
        grid = {'shape': list(ds.shape), 'crs': str(ds.crs), 'transform': list(ds.transform)[:6],
                'nodata_repr': str(ds.nodata), 'dtype': ds.dtypes[0], 'bands': ds.count}
    if arr.shape != foot.shape:
        raise ValueError(f'Cannot compare mismatched raster {path}')
    if not np.isfinite(arr[foot]).all():
        raise ValueError(f'Nonfinite surface inside footprint: {path}')
    vals = arr[foot]
    dots = (arr > 0) & foot
    facts = dict(grid=grid, validator=validation, positive_pixels=int(dots.sum()),
                 positive_on_catalogue=int((dots & labels).sum()),
                 finite_inside_footprint=bool(np.isfinite(vals).all()),
                 all_cells_finite=bool(np.isfinite(arr).all()),
                 min_inside=float(vals.min()), max_inside=float(vals.max()),
                 binary_inside=bool(np.isin(vals, [0, 1]).all()),
                 footprint_pixel_sha256=hashlib.sha256(vals.astype('<f4').tobytes()).hexdigest(),
                 sha256=sha256_file(path))
    return facts, vals, dots


def main():
    ddir = data_dir()
    manifest = json.loads((ROOT / 'registry/data_manifest.json').read_text())
    needed = {'labels', 'sample_submission', 'calib_13gems_20261001_r13-lattice-s5_v2_nan-ou'}
    restored = [restore_entry(e, ddir) for e in manifest['files'] if e['id'] in needed]
    template = ddir / 'sample_submission.tif'
    with rasterio.open(template) as ds:
        foot = np.isfinite(ds.read(1)) & (ds.read_masks(1) > 0)
    with rasterio.open(ddir / 'labels.tif') as ds:
        labels = (ds.read(1) > 0) & foot
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        winners = list(ex.map(fetch_winner, SITES))
    values, masks = {}, {}
    for row in winners:
        facts, vals, dots = inspect(ROOT / row['local'], template, foot, labels)
        row.update(facts)
        values[row['repo']], masks[row['repo']] = vals, dots
        print(f"{row['repo']}: {row['positive_pixels']} dots; strict format {row['validator']['passed']}", flush=True)
    pairs = []
    # One distance array at a time: bounded memory on small CI/sandbox machines.
    for target in winners:
        b = target['repo']
        distances = distance_transform_edt(~masks[b])
        for source in winners:
            a = source['repo']
            if a == b:
                continue
            if source['binary_inside'] and target['binary_inside']:
                rho = binary_spearman(values[a] > 0, values[b] > 0)
            else:
                rho = float(spearmanr(values[a], values[b]).statistic)
                rho = rho if np.isfinite(rho) else None
            overlap = float(np.mean(distances[masks[a]] <= 3)) if masks[a].any() else None
            pairs.append(dict(candidate=a, reference=b, full_footprint_spearman=rho,
                              directional_within_3px=overlap,
                              byte_identical=source['sha256'] == target['sha256'],
                              footprint_pixels_identical=source['footprint_pixel_sha256'] == target['footprint_pixel_sha256'],
                              duplicate=(rho is not None and rho > .90) or (overlap is not None and overlap > .70)))
        del distances
    for row in winners:
        comparisons = [p for p in pairs if p['candidate'] == row['repo']]
        row['max_directional_overlap'] = max(p['directional_within_3px'] for p in comparisons)
        row['duplicates_against_other_winners'] = [p['reference'] for p in comparisons if p['duplicate']]
        row['unique_among_nine_winners'] = not row['duplicates_against_other_winners']
        row['ok_to_submit'] = False
    del values, masks
    status = json.loads((ROOT / 'registry/current_status.json').read_text())
    latest = status['newest_unique']
    current_path = ROOT / latest['file']
    facts, _, dots = inspect(current_path, template, foot, labels)
    if facts['sha256'] != latest['sha256']:
        raise ValueError('Current artifact SHA-256 disagrees with release registry')
    lattice_path = ddir / 'scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif'
    with rasterio.open(lattice_path) as ds:
        lattice = np.where(foot, ds.read(1), 0)
    lattice_check = compare_registry(dots.astype(np.float32), dots, foot,
                                    {'literal-calibration-lattice': (lattice, lattice > 0)}, stage='final')
    distances = distance_transform_edt(~((lattice > 0) & foot))
    lattice_coverage = float(np.mean(distances[foot] <= 3))
    result = dict(schema_version=1, generated_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Nine named historical winners from the request, fetched at pinned current heads; not all submissions.',
                  source_checkout_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  template_provenance='SHA-pinned owner mirror; not organizer-authenticated',
                  restored_inputs=restored, footprint_pixels=int(foot.sum()),
                  winners=winners, directional_comparisons=pairs,
                  current_artifact=dict(file=latest['file'], submission_name=latest['submission_name'],
                                        note=latest['note'], **facts),
                  literal_lattice_check=lattice_check,
                  lattice_footprint_coverage_within_3px=lattice_coverage,
                  budget_feasibility=dot_budget_feasibility(foot & ~labels, (lattice > 0) & foot, facts['positive_pixels']),
                  leaderboard_estimate=None, new_tif_generated=False, experiments_used=0, weekly_slots_used=0,
                  verdict='negative', ok_to_submit=False)
    out = ROOT / 'evidence/focus_review_20261028.json'
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(f'Wrote {out}; no new TIF and no slot used.')


if __name__ == '__main__':
    main()
