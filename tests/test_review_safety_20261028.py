"""Shared tools must not change predictions, trust stale blobs, or hide impossibility."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pytest
import rasterio
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import fetch_focus_registry as fetch
import submission_writer as writer
import evaluate_holdout as evaluator
from refresh_focus_review import binary_spearman
from gems32 import submission
from gems32.release_gate import dot_budget_feasibility
from gemsdoe32.submission import validate_submission_geotiff


def write_tif(path, array, x=243350):
    with rasterio.open(path, 'w', driver='GTiff', width=array.shape[1], height=array.shape[0],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=rasterio.transform.from_origin(x, 4508550, 100, 100)) as dst:
        dst.write(array.astype('float32'), 1)


@pytest.mark.parametrize('value', [.000001, .5, -.1, 1.1, np.nan, np.inf, -np.inf])
def test_binary_contract_never_silently_changes_invalid_values(value):
    a = np.zeros((3, 3))
    a[1, 1] = value
    with pytest.raises(ValueError, match='no implicit thresholding'):
        submission.require_binary_mask(a, np.ones((3, 3), bool))


def test_binary_contract_preserves_dots_and_ignores_only_outside():
    a = np.array([[np.nan, 0], [1, 0]])
    foot = np.array([[False, True], [True, True]])
    result = submission.require_binary_mask(a, foot)
    assert result.dtype == bool and np.array_equal(result, [[False, False], [True, False]])


def test_writer_binary_roundtrip_and_missing_metrics_stay_null(tmp_path, monkeypatch):
    for key, val in [('EXPECTED_HEIGHT', 8), ('EXPECTED_WIDTH', 8),
                     ('EXPECTED_TOTAL_PIXELS', 64), ('EXPECTED_FOOTPRINT_PIXELS', 64)]:
        monkeypatch.setattr(submission, key, val)
    a = np.zeros((8, 8), dtype='float32')
    write_tif(tmp_path / 'sample_submission.tif', a)
    write_tif(tmp_path / 'labels.tif', a)
    a[3, 4] = 1
    meta = dict(candidate_id='test', description='synthetic test, never a competition submission',
                submission_note_zeros='Test binary', submission_note_nan='Test binary')
    bundle = writer.write_validated_submission(a, 'test', meta, ddir=tmp_path,
                                              out_dir=tmp_path/'out', timestamp_tag='test')
    with rasterio.open(tmp_path/'out'/bundle['zeros_tif']['filename']) as ds:
        assert np.array_equal(ds.read(1), a)
    assert bundle['holdout_metrics']['catalogue_hidden_mean'] is None
    import zipfile
    with zipfile.ZipFile(bundle['zeros_zip']['path']) as zf:
        assert zf.namelist() == [bundle['zeros_tif']['filename']]
        assert hashlib.sha256(zf.read(zf.namelist()[0])).hexdigest() == bundle['zeros_tif']['sha256']


def test_writer_rejects_wrong_catalogue_grid_before_output(tmp_path):
    a = np.zeros((8, 8), dtype='float32')
    write_tif(tmp_path/'sample_submission.tif', a)
    write_tif(tmp_path/'labels.tif', a, x=243450)
    with pytest.raises(ValueError, match='Catalogue grid'):
        writer.write_validated_submission(a, 'test', {}, ddir=tmp_path, out_dir=tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_writer_note_expansion_bound_before_output(tmp_path):
    a = np.zeros((8, 8), dtype='float32')
    write_tif(tmp_path/'sample_submission.tif', a)
    write_tif(tmp_path/'labels.tif', a)
    meta = dict(candidate_id='test', description='test',
                submission_note_zeros='{filename}{filename}{filename}', submission_note_nan='test')
    with pytest.raises(ValueError, match='after expansion'):
        writer.write_validated_submission(a, 'x'*80, meta, ddir=tmp_path, out_dir=tmp_path/'out')
    assert not (tmp_path/'out').exists()


@pytest.mark.parametrize('slug', ['../escape', '/absolute', 'x/y'])
def test_writer_cannot_escape_output_directory(tmp_path, slug):
    a = np.zeros((8, 8), dtype='float32')
    write_tif(tmp_path/'sample_submission.tif', a)
    write_tif(tmp_path/'labels.tif', a)
    with pytest.raises(ValueError, match='safe filename'):
        writer.write_validated_submission(a, slug, {}, ddir=tmp_path, out_dir=tmp_path/'out')


def test_validator_shape_mismatch_returns_failure_not_index_error(tmp_path):
    write_tif(tmp_path/'tpl.tif', np.zeros((8, 8)))
    write_tif(tmp_path/'sub.tif', np.zeros((4, 4)))
    report = validate_submission_geotiff(tmp_path/'sub.tif', tmp_path/'tpl.tif', True)
    assert not report.passed
    assert not next(c for c in report.checks if c.name == 'dimensions').passed


def test_same_size_stale_registry_cache_is_refetched(tmp_path, monkeypatch):
    dest = tmp_path/'GEMSDOE24/docs/test.tif'
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b'bad!')
    wanted = b'good'
    blob = hashlib.sha1(b'blob 4\0' + wanted).hexdigest()
    calls = []
    def download(*args, **kwargs):
        calls.append(args)
        kwargs['stdout'].write(wanted)
    monkeypatch.setattr(fetch.subprocess, 'run', download)
    row = fetch.fetch_one('GEMSDOE24', 'a'*40, 'docs/test.tif', 4, tmp_path, blob)
    assert len(calls) == 1 and row['git_blob_verified']
    assert dest.read_bytes() == wanted
    fetch.fetch_one('GEMSDOE24', 'a'*40, 'docs/test.tif', 4, tmp_path, blob)
    assert len(calls) == 1


def test_corrupt_download_cannot_enter_registry(tmp_path, monkeypatch):
    def corrupt(*args, **kwargs):
        kwargs['stdout'].write(b'bad!')
    monkeypatch.setattr(fetch.subprocess, 'run', corrupt)
    monkeypatch.setattr(fetch.time, 'sleep', lambda _: None)
    blob = hashlib.sha1(b'blob 4\0good').hexdigest()
    row = fetch.fetch_one('GEMSDOE24', 'a'*40, 'docs/x.tif', 4, tmp_path, blob)
    assert row['status'] == 'FAILED'
    assert not list(tmp_path.rglob('*.tif')) and not list(tmp_path.rglob('*.partial'))


def test_truncated_tree_never_becomes_a_complete_registry(monkeypatch):
    def get(url):
        return {'sha': 'a'*40} if '/commits/' in url else {'truncated': True, 'tree': []}
    monkeypatch.setattr(fetch, 'gh_json', get)
    with pytest.raises(RuntimeError, match='truncated'):
        fetch.list_repo('GEMSDOE24')


def test_exact_binary_rank_correlation():
    rng = np.random.default_rng(32)
    for _ in range(10):
        a, b = rng.random(1000) < .2, rng.random(1000) < .3
        assert binary_spearman(a, b) == pytest.approx(spearmanr(a, b).statistic)
    assert binary_spearman(np.zeros(10, bool), np.ones(10, bool)) is None


def test_budget_bound_and_threshold_are_exact():
    allowed = np.ones((20, 20), bool)
    reference = np.zeros_like(allowed)
    reference[::5, ::5] = True
    measured = dot_budget_feasibility(allowed, reference, 100)
    upper = measured['max_feasible_distinct_dots']
    assert upper > 0
    assert dot_budget_feasibility(allowed, reference, upper)['feasible']
    assert not dot_budget_feasibility(allowed, reference, upper+1)['feasible']
    assert not dot_budget_feasibility(allowed, np.zeros_like(allowed), 1)['feasible']
    with pytest.raises(ValueError):
        dot_budget_feasibility(allowed, reference, 0)


def test_review_preserves_negative_decision_and_fresh_evidence():
    r = json.loads((ROOT/'evidence/focus_review_20261028.json').read_text())
    assert len(r['winners']) == 9 and len(r['directional_comparisons']) == 72
    assert not r['new_tif_generated'] and not r['ok_to_submit']
    assert r['leaderboard_estimate'] is None and r['experiments_used'] == 0
    for w in r['winners']:
        assert w['git_blob_verified'] and w['leaderboard_estimate'] is None
        assert not w['unique_among_nine_winners'] and not w['ok_to_submit']
    bound = r['budget_feasibility']
    assert not bound['feasible']
    assert bound['max_feasible_distinct_dots'] == min(bound['allowed_pixels'], 10*bound['outside_3px_pixels']//3)
    assert not r['literal_lattice_check']['passed']


@pytest.mark.parametrize('value', [-.1, 1.0000000001, np.nan, np.inf])
def test_probability_writer_rejects_invalid_values_before_float32_rounding(tmp_path, value):
    from gemsdoe32.submission import write_submission_geotiff
    write_tif(tmp_path/'tpl.tif', np.zeros((4, 4)))
    a = np.zeros((4, 4), dtype='float64')
    a[1, 1] = value
    with pytest.raises(ValueError, match='no silent clipping'):
        write_submission_geotiff(a, tmp_path/'tpl.tif', tmp_path/'out/sub.tif')
    assert not (tmp_path/'out').exists()


def test_probability_writer_preserves_probabilities(tmp_path):
    from gemsdoe32.submission import write_submission_geotiff
    write_tif(tmp_path/'tpl.tif', np.zeros((4, 4)))
    a = np.full((4, 4), .25, dtype='float32')
    write_submission_geotiff(a, tmp_path/'tpl.tif', tmp_path/'sub.tif', note='Synthetic unit test')
    with rasterio.open(tmp_path/'sub.tif') as ds:
        assert np.array_equal(ds.read(1), a)


def test_core_holdout_rejects_soft_predictions_and_invalid_buffer():
    from types import SimpleNamespace
    from gems32.holdout import evaluate_hide_and_recover
    ctx = SimpleNamespace(foot=np.ones((4, 4), bool), cells=[])
    with pytest.raises(ValueError, match='no implicit thresholding'):
        evaluate_hide_and_recover(np.full((4, 4), .01), ctx)
    with pytest.raises(ValueError, match='nonnegative'):
        evaluate_hide_and_recover(np.ones((4, 4)), ctx, b_visible_px=-1)
    with pytest.raises(ValueError, match='OOF keys'):
        evaluate_hide_and_recover({'invented': np.ones((4, 4))}, ctx)


def test_cli_rejects_npz_soft_values_before_evaluating(tmp_path, monkeypatch):
    from types import SimpleNamespace
    ctx = SimpleNamespace(foot=np.ones((4, 4), bool),
                          cells=[SimpleNamespace(key='fold', bbox=(slice(0, 4), slice(0, 4)))])
    monkeypatch.setattr(evaluator.holdout, 'load_holdout_context', lambda _: ctx)
    path = tmp_path/'oof.npz'
    np.savez(path, fold=np.full((4, 4), .02))
    with pytest.raises(ValueError, match='no implicit thresholding'):
        evaluator.evaluate_path(path, ddir=tmp_path)


def test_cli_static_result_is_not_promotion_evidence(tmp_path, monkeypatch):
    from types import SimpleNamespace
    ctx = SimpleNamespace(foot=np.ones((4, 4), bool))
    monkeypatch.setattr(evaluator.holdout, 'load_holdout_context', lambda _: ctx)
    monkeypatch.setattr(evaluator.holdout, 'evaluate_hide_and_recover', lambda *a, **k: {})
    monkeypatch.setattr(evaluator.holdout, 'evaluate_sgmc_with_ci', lambda *a, **k: {})
    monkeypatch.setattr(evaluator.holdout, 'evaluate_candidate_holdout', lambda *a, **k: {
        'catalogue_hidden_mean': .1, 'sgmc_prevalence_calibrated_dti': .1, 'drift_corrected_holdout_mean': .1})
    p = tmp_path/'binary.npy'
    np.save(p, np.zeros((4, 4)))
    result = evaluator.evaluate_path(p, ddir=tmp_path)
    assert not result['promotion_eligible'] and result['mode'] == 'static_binary_diagnostic'


def test_review_renderer_is_offline_deterministic_and_hides_stale_download(tmp_path, monkeypatch):
    import build_review_audit as render
    # The committed page is reproducibly generated from pinned evidence.
    before = (ROOT/'docs/nine-site-review.html').read_text()
    assert render.build() == before
    # Simulate a future registry update: never label old bytes as newly audited.
    import shutil
    (tmp_path/'evidence').mkdir()
    (tmp_path/'registry').mkdir()
    (tmp_path/'docs').mkdir()
    shutil.copy(ROOT/render.EVIDENCE, tmp_path/render.EVIDENCE)
    s = json.loads((ROOT/'registry/current_status.json').read_text())
    s['newest_unique']['sha256'] = '0'*64
    (tmp_path/'registry/current_status.json').write_text(json.dumps(s))
    monkeypatch.setattr(render, 'ROOT', tmp_path)
    text = render.build()
    assert 'This audit is stale' in text
    assert '<a class="btn alt"' not in text
