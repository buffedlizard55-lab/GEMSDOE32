#!/usr/bin/env python3
"""Build the primary submission GeoTIFF from the group's best live-scored field.

What is new here is the *emission rule*, not the detector: the field is the group's H19-5
surface (owner-reported 0.1922 live; its dotted descendants were reported at 0.2477/0.2600 --
all claims, see registry/irregularities.json).  The rule is the greedy maximum-expected-coverage
packing validated in `scripts/run_holdout.py`, run at the *same emitted mass* as the best
shipped file so the comparison is not a density effect (the group's own frozen sweep showed the
pinned artifact is the maximum of its density family).
"""
import argparse, json, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import grid, holdout, metric as M, emission as E, submission as SUB  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--field-tif", default="/tmp/gems32/data/h19_5.tif")
    ap.add_argument("--incumbent", default="/tmp/gems32/data/incumbent_d28.tif")
    ap.add_argument("--features", default="/tmp/gems32/data/training_features.tif")
    ap.add_argument("--labels", default="/tmp/gems32/data/labels.tif")
    ap.add_argument("--name", default="gems32-cover-r1-h19-5-d2-8-eq-mass")
    ap.add_argument("--stop-bar", type=float, default=None, help="optional credit bar (0.2*DTI)")
    ap.add_argument("--budget", type=int, default=44090)
    a = ap.parse_args()

    t0 = time.time()
    footprint = grid.read_footprint(a.features)
    labels = grid.read_labels(a.labels)
    with __import__("rasterio").open(a.field_tif) as s:
        f = np.nan_to_num(s.read(1), nan=0.0).astype(np.float32)
    field = np.clip(f, 0.0, 1.0) * footprint

    mask, trace = holdout.greedy_cover_adaptive(field, footprint, a.budget, stop_bar=a.stop_bar,
                                                min_dist=0.0)
    n = int(mask.sum())

    # ---- independent re-check of the emission itself
    audit = M.credit_audit(mask)
    inc = None
    if Path(a.incumbent).exists():
        with __import__("rasterio").open(a.incumbent) as s:
            inc = np.nan_to_num(s.read(1), nan=0.0).astype(np.float32) > 0
    stats = dict(
        rule="greedy max expected coverage under the official kernel; mass matched to the incumbent",
        emitted_px=n, footprint_px=int(footprint.sum()),
        budget=a.budget, stop_bar=a.stop_bar,
        marginal_tail=trace[-1] if trace else None,
        credit_audit=audit.__dict__,
        catalogue_overlap_px=int((mask & labels).sum()),
        field_px=int((field > 0).sum()),
        seconds=round(time.time() - t0, 1),
    )
    if inc is not None:
        stats["incumbent"] = dict(
            px=int(inc.sum()),
            overlap_px=int((mask & inc).sum()),
            jaccard=float((mask & inc).sum() / max(1, (mask | inc).sum())),
            catalogue_overlap_px=int((inc & labels).sum()),
        )
    out = SUB.build(mask, a.features, footprint, ROOT / "docs" / "downloads", a.name, outside="nan")
    out_zero = SUB.build(mask, a.features, footprint, ROOT / "docs" / "downloads",
                         a.name + "-zeros", outside="zero")
    stats["files"] = {"nan": out, "zeros": out_zero}
    (ROOT / "registry" / "submission_build.json").write_text(json.dumps(stats, indent=1) + "\n")
    print(json.dumps({k: v for k, v in stats.items() if k != "credit_audit"}, indent=1))
    print("credit audit:", audit)


if __name__ == "__main__":
    main()
