"""Never infer a format pass from a hash or mutate registries in dry-run."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems32.byte_audit import inspect_saved_raster

ROOT = Path(__file__).resolve().parents[1]


def raster(path, value=0):
    with rasterio.open(path, 'w', driver='GTiff', width=2, height=2, count=1,
                       dtype='float32', crs='EPSG:32611',
                       transform=from_origin(243350, 4508550, 100, 100)) as dst:
        dst.write(np.full((2, 2), value, dtype='float32'), 1)


@pytest.mark.parametrize('value', [0, 2, float('nan')])
def test_wrong_grid_never_passes(tmp_path, value):
    path = tmp_path / 'tiny.tif'
    raster(path, value)
    audit = inspect_saved_raster(path)
    assert not audit['strict_primary_passed']
    assert audit['total_cells'] == 4
    assert not audit['reference_template_verified_this_review']


def fixture_sync(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location('sync_under_test', ROOT / 'scripts/sync_submission_build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    status = json.loads((ROOT / 'registry/current_status.json').read_text())
    source = ROOT / status['newest_unique']['file']
    target = tmp_path / 'primary.tif'
    target.write_bytes(source.read_bytes())
    status['newest_unique']['file'] = 'primary.tif'
    status['newest_unique']['run_card'] = 'card.json'
    status['newest_unique']['zip'] = None
    (tmp_path / 'card.json').write_text('{"verdict":"negative"}')
    release = {'artifact': {'path': 'old.tif', 'sha256': 'a' * 64},
               'latest_candidate': {'sha256': 'a' * 64}}
    for attr, name, content in [('BUILD', 'build.json', {}), ('STATUS', 'status.json', status),
                                 ('RELEASE', 'release.json', release)]:
        path = tmp_path / name
        path.write_text(json.dumps(content))
        monkeypatch.setattr(module, attr, path)
    monkeypatch.setattr(module, 'ROOT', tmp_path)
    return module


def test_dry_run_stale_review_is_read_only(tmp_path, monkeypatch):
    module = fixture_sync(tmp_path, monkeypatch)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    monkeypatch.setattr(sys, 'argv', ['sync', '--dry-run'])
    assert module.main() == 0
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tmp_path.iterdir()}
    assert before == after


def test_missing_card_cannot_reconcile(tmp_path, monkeypatch):
    module = fixture_sync(tmp_path, monkeypatch)
    (tmp_path / 'card.json').unlink()
    monkeypatch.setattr(sys, 'argv', ['sync'])
    assert module.main() == 1


def test_non_dry_sync_records_real_measurement(tmp_path, monkeypatch):
    module = fixture_sync(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, 'argv', ['sync'])
    assert module.main() == 0
    review = json.loads(module.RELEASE.read_text())
    measured = review['artifact']['format_byte_audit']
    assert measured['strict_primary_passed']
    assert measured['positive_pixels'] == 37654
    assert review['artifact']['reference_grid_reaudit']['status'] == 'NOT_REVERIFIED'
    assert not review['submission_authorization']['ok_to_download_and_submit']


@pytest.mark.parametrize('value', [-1.0, 1.01, float('nan'), float('inf')])
def test_correct_grid_invalid_predictions_fail(tmp_path, value):
    path = tmp_path / 'invalid.tif'
    with rasterio.open(path, 'w', driver='GTiff', width=3292, height=3730, count=1,
                       dtype='float32', compress='deflate', crs='EPSG:32611',
                       transform=from_origin(243350, 4508550, 100, 100)) as dst:
        arr = np.zeros((3730, 3292), dtype='float32')
        arr[0, 0] = value
        dst.write(arr, 1)
    measured = inspect_saved_raster(path)
    assert measured['historical_grid_match']
    assert not measured['strict_primary_passed']


def test_review_never_projects_a_score_or_authorizes_upload():
    card = json.loads((ROOT / 'evidence/review_audit_20261027.json').read_text())
    assert card['holdout']['leaderboard_estimate'] is None
    assert card['experiments_used'] == 0
    assert not card['ok_to_submit']
    assert card['verdict'] == 'negative'
    assert len(card['note']) <= 140
    page = (ROOT / 'docs/nine-site-review.html').read_text()
    assert page.count('spatial duplicate family') == 9
    assert 'DO NOT SUBMIT' in page
