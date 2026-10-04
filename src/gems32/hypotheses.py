"""Registered candidate geological hypotheses for GEMSDOE32.

Each entry names the layers used, the physical signature, why it should find a fault the
USGS/INGENIOUS catalogue misses, and how it differs from what the group already ran.  The
``status`` field is the honest state: only hypotheses with a *measured* line get a number.
"""
from __future__ import annotations

import json
from pathlib import Path

HYPOTHESES = [
    {
        "id": "H60-1",
        "rank": 1,
        "title": "Post-catalogue coseismic surface ruptures (Monte Cristo Range 2020 Mw 6.5 and the "
                 "pre-2020 historical rupture set) as high-precision line targets",
        "layers": ["USGS/NBMG 2020 MCRE surface-rupture traces (Dee et al., NBMG TR-190; SRL 92(2A))",
                   "19 official bands only as a corroboration filter"],
        "signature": "exact mapped rupture polylines rasterised on the 100 m grid (no transform, no "
                     "detection: the geometry is the measurement)",
        "why_off_catalogue": "the competition labels are the pre-2020 USGS/INGENIOUS catalogue; the "
                             "MCRE rupture occurred on 2020-05-15 in *largely unmapped parts of the "
                             "Candelaria fault* and is by construction absent from a pre-2020 catalogue, "
                             "while being real, published and trivially verifiable by the expert panel",
        "differs_from_repo": "the group has emission, packing, Euler, slip-tendency, hydrothermal and "
                             "catalogue-difference families, but no arm built on post-catalogue "
                             "coseismic ruptures; H41/SGMC arms used *catalogue* vectors, which cannot "
                             "contain a fault that post-dates the catalogue",
        "expected_dti": "0.000 to +0.02 on the public split (single 28 km trace, ~2 % of the group's "
                        "emitted mass); unbounded on the final round because the expert panel can "
                        "verify the fault and add it to the expanded label set",
        "cost": "low (one vector download + rasterise + geometric thinning)",
        "data_status": "source located and documented (see registry/sources.json); obtainability from "
                       "this sandbox is blocked (sciencebase.gov unknown-host), so the arm ships as a "
                       "registered hypothesis with a CI fetch step, not as a claimed result",
        "status": "registered; not yet measured; no slot",
    },
    {
        "id": "H60-2",
        "rank": 2,
        "title": "Catalogue-difference emission: faults mapped in newer state datasets but absent "
                 "from the competition labels, gated by a geophysical corroboration filter",
        "layers": ["NBMG Qfaults-INGENIOUS v2 vectors (1,179 features in footprint)",
                   "GDR 1391 trace table", "USGS SGMC 1:24,000 faults", "19 bands for the gate"],
        "signature": "distance-to-nearest-newer-catalogue-trace < 2 px AND ridge/curvature corroboration "
                     "on the detrended DEM",
        "why_off_catalogue": "the hidden test set is *newly identified* faults: a newer state mapping "
                             "that post-dates the national catalogue is, by construction, a sample of "
                             "exactly that population",
        "differs_from_repo": "the group's H41/SGMC arms emitted catalogue vectors *without* a "
                             "geophysical gate and both lost their secondary proxy; here the gate is the "
                             "corroboration filter inside `emission.py` (credit bar), and the arm is "
                             "scored at matched mass",
        "expected_dti": "0 to +0.01 proxy",
        "cost": "medium (vector download + rasterisation + gate)",
        "data_status": "vectors are hash-pinned in the group's own mirrors (GEMSDOE24) and reachable "
                       "from this sandbox via the GitHub API",
        "status": "registered; partially measured (see evidence/)",
    },
    {
        "id": "H60-3",
        "rank": 3,
        "title": "Adaptive credit-bar emission: stop the emission where the marginal expected credit "
                 "per unit mass falls below 0.2 x DTI (the metric's own break-even)",
        "layers": ["any detector field"],
        "signature": "greedy maximum-expected-coverage packing of the field under the official "
                     "triangular kernel with an *adaptive* stopping rule",
        "why_off_catalogue": "not a geological hypothesis but the decision rule for every other one: "
                             "it removes the fixed-count budget that the group's sweeps showed to be "
                             "family-limited and replaces it with the metric's analytic bar",
        "differs_from_repo": "H37-1 fixed the packing objective but kept a matched *count*; here the "
                             "count is an output, and the same rule gives the discovery-weighted "
                             "variant used for the two-round objective",
        "expected_dti": "measured on the blocked holdout (see evidence/holdout_run1.json)",
        "cost": "low (already implemented)",
        "data_status": "n/a (no new data)",
        "status": "measured on the blocked holdout",
    },
    {
        "id": "H60-4",
        "rank": 4,
        "title": "Two-round discovery option value: lower the emission bar for candidates whose "
                 "verification is likely, because the same file is re-scored against the expanded "
                 "label set",
        "layers": ["any field", "published fault evidence for the verification prior"],
        "signature": "objective DTI_1 + rho * DTI_2 with rho set by the prize structure "
                     "($50k initial round vs $250k final round); the effective bar becomes "
                     "0.2 x DTI / (1 + rho)",
        "why_off_catalogue": "the initial-round label set is deliberately incomplete, so public-LB "
                             "maximisation under-prices true-but-unlabelled faults; the metric's "
                             "alpha = 0.2 (false positives four times cheaper than false negatives) "
                             "is the organisers' own statement that they want such predictions",
        "differs_from_repo": "no prior arm, gate or budget in the group's record uses the two-round "
                             "structure; every promotion bar to date is round-1 only",
        "expected_dti": "raises the *expected* final-round score; cannot be measured on any local "
                        "holdout and must be reasoned about from the published prize structure",
        "cost": "none (a change in the decision rule)",
        "data_status": "n/a",
        "status": "implemented as A3 in the holdout ladder and as `rho` in `bo.slot_gate`",
    },
    {
        "id": "H60-5",
        "rank": 5,
        "title": "Cross-scale drainage-network organisation (stream-power / knickpoint residuals) as "
                 "an independent lineament family",
        "layers": ["1 m / 10 m 3DEP DEM from the official link table (1m_DEM_links.csv)"],
        "signature": "chi-profile and knickpoint residuals along the channel network; aligned "
                     "knickpoints across a basin trace a fault that displaces the network but has no "
                     "preserved scarp",
        "why_off_catalogue": "targets faults in alluvium/valley fill with no topographic scarp, i.e. "
                             "exactly the class a surface-mapping catalogue lacks",
        "differs_from_repo": "the group ran a drainage arm (H43) that *passed* its primary screen and "
                             "was withheld on a secondary proxy; it was built on the 100 m detrended "
                             "surface, and a 1 m/10 m channel network with a chi transform is a "
                             "different measurement",
        "expected_dti": "0 to +0.01",
        "cost": "high (DEM tile download + hydrology)",
        "data_status": "the official link table is mirrored in the group's repo "
                       "(`data/dem_links.json`, sha256 8804dbff8754...); tile fetch needs CI egress",
        "status": "registered; not run (cost), no slot",
    },
]


def write_registry(path: str | Path = "registry/hypotheses.json") -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"hypotheses": HYPOTHESES}, indent=1) + "\n")
    return p


if __name__ == "__main__":
    print(write_registry())
