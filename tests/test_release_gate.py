import numpy as np
import pytest
import rasterio
from gems32.release_gate import compare_registry, promotion_decision, REQUIRED_VALIDATOR_CHECKS
from gems32.submission import audit_geotiff


def test_dense_registry_is_not_exempt():
    shape = (20, 20)
    s = np.arange(400).reshape(shape)
    dots = np.zeros(shape, bool)
    dots[10, 10] = True
    # Perfect covering grid still fails the literal rule despite unrelated ranks.
    result = compare_registry(s, dots, np.ones(shape, bool), {'dense': (-s, np.ones(shape, bool))})
    assert result['stop'] and result['comparisons'][0]['within_3px_fraction'] == 1


def test_identical_surface_stops_before_placement():
    s = np.arange(400).reshape(20, 20)
    r = compare_registry(s, s % 50 == 0, np.ones(s.shape, bool), {'same': (s, s % 51 == 0)})
    assert r['stop'] and r['comparisons'][0]['spearman'] > .90


def test_missing_and_constant_registry_fail_closed():
    s = np.arange(100).reshape(10, 10)
    assert compare_registry(s, s > 50, s >= 0, {})['stop']
    assert compare_registry(s, s > 50, s >= 0, {'constant': (s * 0, s > 50)})['stop']


def test_missing_lane_or_canary_blocks_promotion():
    args = dict(lane='test', surface_check={'passed': True, 'stage': 'surface'}, final_check={'passed': True, 'stage': 'final'},
                canary_aucs=[.6], holdout={'dti': .2, 'ci95': [.1, .3], 'n_withheld_positives': 10, 'evaluator_version': 'test-v1'},
                incumbent={'dti': .1, 'ci95': [.05, .15], 'n_withheld_positives': 10, 'evaluator_version': 'test-v1'}, same_evaluation=True,
                paired_delta_ci95=[.01, .2], validator=dict.fromkeys(REQUIRED_VALIDATOR_CHECKS, True))
    assert promotion_decision(**args)['verdict'] == 'promote'
    for update in ({'lane': ''}, {'canary_aucs': [.91]}, {'same_evaluation': False},
                   {'validator': {}}, {'holdout': None}):
        assert promotion_decision(**(args | update))['verdict'] == 'negative'


def test_shifted_transform_and_wrong_crs_rejected_before_pixel_checks(tmp_path):
    tpl = tmp_path / 'template.tif'
    meta = dict(driver='GTiff', height=8, width=8, count=1, dtype='float32',
                crs='EPSG:32611', transform=rasterio.transform.from_origin(243350, 4508550, 100, 100))
    with rasterio.open(tpl, 'w', **meta) as ds:
        ds.write(np.zeros((8, 8), 'float32'), 1)
    for change in ({'transform': rasterio.transform.from_origin(243351, 4508550, 100, 100)},
                   {'crs': 'EPSG:32612'}):
        out = tmp_path / 'bad.tif'
        with rasterio.open(out, 'w', **(meta | change)) as ds:
            ds.write(np.zeros((8, 8), 'float32'), 1)
        with pytest.raises(ValueError, match='CRS/shape/transform'):
            audit_geotiff(out, np.ones((8, 8), bool), np.zeros((8, 8), bool), template_tif=tpl)


def test_surface_check_can_run_before_dots_exist():
    s = np.arange(100).reshape(10, 10)
    r = compare_registry(s, None, s >= 0, {'other': (-s, s > 50)}, stage='surface')
    assert r['passed']
    with pytest.raises(ValueError, match='requires dots'):
        compare_registry(s, None, s >= 0, {'other': (-s, s > 50)})


def test_audit_rejects_out_of_range_nonfinite_and_fractional_catalogue(tmp_path, monkeypatch):
    from gems32 import submission
    for name, value in [('EXPECTED_HEIGHT', 8), ('EXPECTED_WIDTH', 8),
                        ('EXPECTED_TOTAL_PIXELS', 64), ('EXPECTED_FOOTPRINT_PIXELS', 64)]:
        monkeypatch.setattr(submission, name, value)
    tpl = tmp_path / 'sample.tif'
    meta = dict(driver='GTiff', height=8, width=8, count=1, dtype='float32',
                crs='EPSG:32611', transform=rasterio.transform.from_origin(243350, 4508550, 100, 100))
    with rasterio.open(tpl, 'w', **meta) as ds:
        ds.write(np.zeros((8, 8), 'float32'), 1)
    foot = np.ones((8, 8), bool)
    labels = np.zeros((8, 8), bool)
    labels[2, 2] = True
    assert audit_geotiff(tpl, foot, labels, template_tif=tpl)['all_checks_passed']
    for value in [np.nan, np.inf, -1, 1.01, .25]:
        a = np.zeros((8, 8), 'float32')
        a[2, 2] = value
        out = tmp_path / 'candidate.tif'
        with rasterio.open(out, 'w', **meta) as ds:
            ds.write(a, 1)
        with pytest.raises(ValueError, match='audit failed'):
            audit_geotiff(out, foot, labels, template_tif=tpl)


@pytest.mark.parametrize('change', [
    {'paired_delta_ci95': None},
    {'paired_delta_ci95': [-.01, .2]},
    {'paired_delta_ci95': [0, .2]},
    {'paired_delta_ci95': [np.nan, .2]},
    {'paired_delta_ci95': [.2, .1]},
    {'validator': {'range': True}},
    {'validator': dict.fromkeys(REQUIRED_VALIDATOR_CHECKS - {'crs_match'}, True)},
    {'incumbent': {'dti': .1}},
    {'holdout': {'dti': .2, 'ci95': [.1, .3], 'n_withheld_positives': 10}},
    {'incumbent': {'dti': .1, 'ci95': [.05, .15], 'n_withheld_positives': 11,
                   'evaluator_version': 'test-v1'}},
    {'incumbent': {'dti': .1, 'ci95': [.05, .15], 'n_withheld_positives': 10,
                   'evaluator_version': 'different-v2'}},
])
def test_promotion_requires_complete_matched_evidence(change):
    args = dict(lane='test', surface_check={'passed': True, 'stage': 'surface'},
                final_check={'passed': True, 'stage': 'final'}, canary_aucs=[.6],
                holdout={'dti': .2, 'ci95': [.1, .3], 'n_withheld_positives': 10,
                         'evaluator_version': 'test-v1'},
                incumbent={'dti': .1, 'ci95': [.05, .15], 'n_withheld_positives': 10,
                           'evaluator_version': 'test-v1'},
                same_evaluation=True, paired_delta_ci95=[.01, .2],
                validator=dict.fromkeys(REQUIRED_VALIDATOR_CHECKS, True))
    result = promotion_decision(**(args | change))
    assert result['verdict'] == 'negative'
    assert result['selector_required'] and not result['slot_used']
