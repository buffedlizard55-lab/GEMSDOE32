"""Fail-closed parallel-run gates. These never allocate competition submission slots."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr


def compare_registry(surface, dots, footprint, registry, *, stage="final"):
    """Exact footprint ranks and directional <=3px dot overlap, without density exemptions.

    registry maps names to (continuous_surface, positive_dot_mask). No sampling is
    permitted here: a sample correlation is not the requested full-surface test.
    Undefined correlations, missing references, and empty dots fail closed.
    """
    if stage not in {"surface", "final"}:
        raise ValueError("stage must be surface or final")
    surface, footprint = np.asarray(surface), np.asarray(footprint, bool)
    if stage == "final" and dots is None:
        raise ValueError("final dot check requires dots")
    dots = np.zeros(footprint.shape, bool) if dots is None else np.asarray(dots, bool)
    if surface.shape != footprint.shape or dots.shape != footprint.shape:
        raise ValueError("surface/dots/footprint shape mismatch")
    if not footprint.any() or not np.isfinite(surface[footprint]).all():
        raise ValueError("empty footprint or nonfinite candidate surface")
    dots = dots & footprint
    rows = []
    for name, (other_surface, other_dots) in registry.items():
        other_surface, other_dots = np.asarray(other_surface), np.asarray(other_dots, bool)
        if other_surface.shape != footprint.shape or other_dots.shape != footprint.shape:
            raise ValueError(f"registry shape mismatch: {name}")
        other_dots = other_dots & footprint
        rho = None
        if np.isfinite(other_surface[footprint]).all():
            x, y = surface[footprint], other_surface[footprint]
            if np.ptp(x) > 0 and np.ptp(y) > 0:
                rho = float(spearmanr(x, y).statistic)
        overlap = None
        if dots.any() and other_dots.any():
            overlap = float((distance_transform_edt(~other_dots)[dots] <= 3).mean())
        duplicate = (rho is not None and rho > .90) or (stage == 'final' and overlap is not None and overlap > .70)
        rows.append(dict(registry=name, spearman=rho, within_3px_fraction=overlap,
                         duplicate=duplicate, measurable=rho is not None and (stage == 'surface' or overlap is not None)))
    passed = bool(rows) and (stage == 'surface' or bool(dots.any())) and all(r['measurable'] and not r['duplicate'] for r in rows)
    return dict(stage=stage, rule="literal rho>0.90 OR directional overlap>0.70; no density exemptions",
                comparisons=rows, passed=passed, stop=not passed)


def promotion_decision(*, lane, surface_check, final_check, canary_aucs,
                       holdout, incumbent, same_evaluation, validator):
    """Only a recommendation, not authorization to spend a slot. Missing evidence rejects."""
    aucs = list(canary_aucs)
    gates = dict(
        lane=bool(lane and lane.strip()),
        surface=surface_check.get('stage') == 'surface' and surface_check.get('passed') is True,
        final=final_check.get('stage') == 'final' and final_check.get('passed') is True,
        canaries=bool(aucs) and all(np.isfinite(a) and 0 <= a <= .90 for a in aucs),
        holdout=bool(same_evaluation and holdout and incumbent
                     and holdout.get('n_withheld_positives', 0) > 0
                     and len(holdout.get('ci95', [])) == 2
                     and np.isfinite([holdout.get('dti', np.nan), incumbent.get('dti', np.nan),
                                      *holdout.get('ci95', [])]).all()
                     and 0 <= holdout['ci95'][0] <= holdout['dti'] <= holdout['ci95'][1] <= 1
                     and holdout['dti'] > incumbent['dti']),
        format=bool(validator) and all(v is True for v in validator.values()),
    )
    return dict(gates=gates, verdict='promote' if all(gates.values()) else 'negative',
                selector_required=True, slot_used=False)
