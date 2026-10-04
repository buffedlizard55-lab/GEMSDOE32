"""GEMSDOE32 — auditable fault-discovery system for the DOE GEMS Prize (DrivenData #306).

Modules
-------
metric      : exact distance-weighted Tversky index (DTI) + its algebra + the marginal emission rule
grid        : competition grid geometry, footprint, raster IO
emission    : emitters (dots, skeleton, greedy max-coverage) and the decision-theoretic threshold
features    : multi-scale structural feature stack built from the 19 official bands
detector    : CPU-feasible detectors (ridge score, logistic, GBDT)
holdout     : spatially blocked hide-and-recover harness
bo          : Gaussian-process surrogate + expected improvement + cost-aware slot gate
submission  : format-validated writer/validator for the competition GeoTIFF
feed        : live source feed (official sources) + leaderboard snapshot
hypotheses  : the registered candidate geological hypotheses
"""

__version__ = "0.1.0"
