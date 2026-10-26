"""Unit tests for the live-score covariate instrument (src/gems32/livescore.py)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32 import livescore as LS  # noqa: E402


# ---------------------------------------------------------------- matching rules
def test_normalize_strips_extensions_prefixes_and_variant_suffixes():
    assert LS.normalize_name("gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif") == \
        "gemsdoe32h33h332b220261004t220000ze5eb6e7e"
    assert LS.normalize_name("Hedge-v2_submission") == "hedgev2submission"
    assert LS.normalize_name("dotted-h19-5-d2-8-20261002-e56ea318af89-nan") == \
        "dottedh195d2820261002e56ea318af89"
    # repeated suffix stripping: -zeros-zeros
    assert LS.normalize_name("x-20260101T000000Z-zeros-zeros") == "x20260101t000000z"


def test_strong_tokens_exclude_dates_and_keep_hash_tokens():
    # a calendar date is 8+ digits but has no a-f letter -> excluded
    assert LS.strong_tokens("h33-2-b2-20261004T220000Z-e5eb6e7e") == {"e5eb6e7e"}
    # mixed hex tokens with letters and digits survive
    assert LS.strong_tokens("a-7f00890a-b2314b599") == {"7f00890a", "b2314b599"}
    # plain words are not tokens at all
    assert LS.strong_tokens("dotted-ridge-top2pct") == set()


def test_match_row_prefers_exact_then_same_site_then_shortest():
    cand = [
        LS.Candidate(Path("/a/gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"),
                     "gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan", "GEMSDOE24"),
        LS.Candidate(Path("/b/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"),
                     "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan", "GEMSDOE25"),
    ]
    row = LS.LedgerRow("GEMSDOE25", "dotted-h19-5-d2-8-20261002-e56ea318af89-nan", 0.26, "", "0.2600")
    got, rule = LS.match_row(row, cand)
    assert rule == "containment"
    assert got.repo == "GEMSDOE25"  # same site beats the alphabetically-first longer stem

    row2 = LS.LedgerRow("GEMSDOE", "gems-submission-20260925T001403Z-7f00890a", 0.1563, "", "0.1563")
    cand2 = [LS.Candidate(Path("/c/gemsdoe-ens12-adopted-7f00890a.tif"),
                          "gemsdoe-ens12-adopted-7f00890a", "GEMSDOE")]
    got2, rule2 = LS.match_row(row2, cand2)
    assert rule2 == "hash-token" and got2 is cand2[0]


def test_match_row_returns_none_when_only_a_date_token_matches():
    cand = [LS.Candidate(Path("/d/gemsdoe31-add-arm-d28-20261004-8acb75e1-allfinite.tif"),
                         "gemsdoe31-add-arm-d28-20261004-8acb75e1-allfinite", "GEMSDOE31")]
    row = LS.LedgerRow("GEMSDOE32", "h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros", 0.2778, "", "0.2778")
    got, rule = LS.match_row(row, cand)
    # containment must not fire (neither name contains the other) and the date token is weak
    assert got is None and rule == ""


# ---------------------------------------------------------------- geometry
def test_within3_fraction_directional():
    ref = np.zeros((20, 20), bool)
    ref[10, 10] = True
    mask = np.zeros((20, 20), bool)
    mask[10, 10] = True       # distance 0
    mask[10, 13] = True       # distance 3 -> inside
    mask[10, 14] = True       # distance 4 -> outside
    assert LS.within3_fraction(mask, ref) == pytest.approx(2 / 3)


def test_mask_digest_distinguishes_masks():
    a = np.zeros((5, 5), bool)
    a[2, 2] = True
    b = a.copy()
    b[2, 3] = True
    assert LS.mask_digest(a) != LS.mask_digest(b)
    assert LS.mask_digest(a) == LS.mask_digest(a.copy())


def test_raster_features_on_synthetic_masks():
    cat = np.zeros((40, 40), bool)
    cat[20, 5:35] = True                     # a catalogue line
    h195 = np.zeros((40, 40), bool)
    h195[20:22, 5:35] = True                 # dense family line on the same structure
    champ = cat.copy()

    mask = np.zeros((40, 40), bool)
    mask[20, 10:30:2] = True                 # dots on the catalogue line (family member)
    f = LS.raster_features(mask, cat, h195, champ)
    assert f.dots == 10
    assert f.frac_on_catalogue == 1.0
    assert f.frac_within3_catalogue == 1.0
    assert f.frac_within3_h195 == 1.0
    assert f.frac_within3_champion == 1.0
    assert f.median_dist_catalogue_px == 0.0
    assert 0.0 < f.mean_self_kernel <= 1.0

    far = np.zeros((40, 40), bool)
    far[2, 2] = True                          # far from everything
    far[2, 3] = True
    g = LS.raster_features(far, cat, h195, champ)
    assert g.frac_on_catalogue == 0.0
    assert g.frac_within3_catalogue == 0.0
    assert g.frac_within3_h195 == 0.0
    assert g.median_dist_catalogue_px > 3.0


def test_raster_features_rejects_empty_mask():
    cat = np.zeros((10, 10), bool)
    cat[5, 5] = True
    with pytest.raises(ValueError):
        LS.raster_features(np.zeros((10, 10), bool), cat, cat, cat)


# ---------------------------------------------------------------- statistics
def test_loo_linear_recovers_a_perfect_linear_relationship():
    rng = np.random.default_rng(7)
    x = rng.uniform(size=(40, 3))
    w = np.array([0.5, -1.2, 2.0])
    y = x @ w + 0.3
    out = LS.loo_linear_regression(x, y)
    assert out["loo_r2"] > 0.999
    assert out["loo_mae"] < 1e-6
    assert out["loo_spearman"] > 0.999


def test_loo_linear_on_pure_noise_is_near_zero_r2():
    rng = np.random.default_rng(11)
    x = rng.uniform(size=(60, 3))
    y = rng.uniform(size=60)
    out = LS.loo_linear_regression(x, y)
    assert out["loo_r2"] < 0.2
    assert out["loo_spearman_p"] > 0.05


def test_spearman_matches_scipy():
    rho, p = LS.spearman([1, 2, 3, 4, 5], [2, 4, 6, 8, 10])
    assert rho == pytest.approx(1.0)
    assert p < 0.01


def test_full_fit_coefficients_signs():
    rng = np.random.default_rng(3)
    x = rng.uniform(size=(50, 2))
    y = 2.0 * x[:, 0] - 1.0 * x[:, 1]
    coefs = LS.full_fit_coefficients(x, y, ["a", "b"])
    betas = {c["feature"]: c["standardized_beta"] for c in coefs}
    assert betas["a"] > 0 > betas["b"]
    assert abs(betas["a"]) > abs(betas["b"])


# ---------------------------------------------------------------- lattice bound
def test_lattice_hole_bound_spaced_grid_covers_almost_everything():
    foot = np.ones((60, 60), bool)
    lattice = np.zeros((60, 60), bool)
    lattice[::5, ::5] = True                  # spacing 5, radius 3 -> full interior coverage
    out = LS.lattice_hole_bound(lattice, foot)
    # interior is fully covered; only the outer border band beyond the last lattice points is holes
    assert out["footprint_within3_of_lattice"] > 0.9
    # holes/0.3 dots is tiny relative to the grid: a dense map cannot pass the literal rule
    assert out["max_dots_that_could_pass_literal_rule"] < 0.25 * foot.sum()
    # the bound is exactly holes/0.3
    assert out["max_dots_that_could_pass_literal_rule"] == int(np.floor(out["hole_pixels"] / 0.3))


def test_lattice_hole_bound_allows_sparse_maps_when_lattice_is_sparse():
    foot = np.ones((100, 100), bool)
    lattice = np.zeros((100, 100), bool)
    lattice[50, 50] = True                    # a single dot covers ~pi*9 area
    out = LS.lattice_hole_bound(lattice, foot)
    assert out["hole_pixels"] > 9000
    assert out["max_dots_that_could_pass_literal_rule"] > 30000


# ---------------------------------------------------------------- ledger parsing
def test_parse_ledger_handles_multiscore_and_official_rows(tmp_path):
    led = tmp_path / "ledger.csv"
    led.write_text(
        "site,submission,score,provenance,status,source_url,notes,evidence_class,as_of_utc\n"
        "GEMSDOE32,h33-x-zeros,0.2778,user brief,ok,http://x,,user-report,\n"
        "DrivenData official leaderboard,rank-1,0.4413,official,ok,http://y,,official,\n"
        "GEMSDOE91,two-scores,0.3195/0.3128,user brief,ok,http://z,,user-report,\n"
        "GEMSDOE92,unscored,UNSCORED-negative,user brief,ok,http://w,,user-report,\n"
    )
    scored, excluded = LS.parse_ledger(led)
    assert len(scored) == 1 and scored[0].score == 0.2778
    kinds = {e["reason"].split(";")[0].split("score")[0].strip() for e in excluded}
    assert len(excluded) == 3
