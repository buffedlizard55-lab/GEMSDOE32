"""Re-check the H45-1 two-regime submission-candidate against the CURRENT registry.

Why this exists: the original H45 run (evidence/h45_tworegime_run_card.json) scanned the 304-entry manifest
that existed at the time. Later sessions pinned more rasters (manifest now 324 entries) and added GEMSDOE32
downloads that are not in any manifest (e.g. docs/downloads/*2fe5944c*). This script scans BOTH sets, in both
overlap directions, and writes evidence/h45_uniqueness_recheck_20261026.json.

Rules (PARALLEL-RUN PROTOCOL uniqueness, applied as stated in the H45 preregistration):
  surface: footprint Spearman > 0.90 -> flag
  final dots: share of the candidate's dots within 3 px of the other raster's dots > 70% -> flag
  Both directions are reported; the protocol test uses the candidate->other direction.
The candidate's surface is its own submitted value raster (a proxy: the run-time composite surface was not saved).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
CAND = ROOT / "docs/downloads/gemsdoe32-h45-tworegime-split-37654-20261026T161610Z-35245379-zeros.tif"
NAN_VARIANT = ROOT / "docs/downloads/gemsdoe32-h45-tworegime-split-37654-20261026T161610Z-35245379-nan.tif"
OUT = ROOT / "evidence/h45_uniqueness_recheck_20261026.json"


def _ranks(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, kind="mergesort")
    r = np.empty(a.shape, dtype=np.float64)
    r[order] = np.arange(a.size, dtype=np.float64)
    # average ties
    sa = a[order]
    _, first, counts = np.unique(sa, return_index=True, return_counts=True)
    for f, c in zip(first, counts):
        if c > 1:
            r[order[f:f + c]] = (2 * f + c - 1) / 2.0
    return r


def _load(path: Path):
    with rasterio.open(path) as ds:
        return ds.read(1).astype(np.float32), ds.shape


def main() -> int:
    cand_raw, shape = _load(CAND)
    foot_raw, _ = _load(NAN_VARIANT)
    foot = np.isfinite(foot_raw)
    cand = np.nan_to_num(cand_raw, nan=0.0)
    cand_dots = (cand > 0) & foot
    cand_rank = _ranks(cand[foot].astype(np.float64))
    cand_dt = distance_transform_edt(~cand_dots)

    targets: list[tuple[str, Path, str]] = []
    man = json.loads((ROOT / "registry/focus_registry_manifest.json").read_text())
    seen = {}
    for r in man["rasters"]:
        if r.get("status") != "ok":
            continue
        seen.setdefault(r["sha256"], (f"{r['repo']}:{r['path']}", ROOT / r["local"]))
    for sha, (name, p) in seen.items():
        targets.append((name, p, sha))
    targets = [t for t in targets if t[2] not in {hashlib.sha256(CAND.read_bytes()).hexdigest(), hashlib.sha256(NAN_VARIANT.read_bytes()).hexdigest()}]
    cand_sha = hashlib.sha256(CAND.read_bytes()).hexdigest()
    nan_sha = hashlib.sha256(NAN_VARIANT.read_bytes()).hexdigest()
    own = {cand_sha, nan_sha}  # the candidate's own two variants are not peers
    for sha in list(seen):
        if sha in own:
            del seen[sha]
    targets = [(n, p_, sh) for (n, p_, sh) in targets if sh not in own]
    for p in sorted((ROOT / "docs/downloads").glob("*.tif")):
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if sha in own or sha in seen:
            continue
        targets.append((f"GEMSDOE32:docs/downloads/{p.name}", p, sha))

    rows, skipped = [], []
    for name, p, sha in targets:
        if not p.exists():
            skipped.append({"name": name, "reason": "local file missing"})
            continue
        arr, shp = _load(p)
        if shp != shape:
            skipped.append({"name": name, "reason": f"shape={shp}"})
            continue
        other = np.nan_to_num(arr, nan=0.0)
        oth_dots = (other > 0) & foot
        rho = float(np.corrcoef(cand_rank, _ranks(other[foot].astype(np.float64)))[0, 1])
        oth_dt = distance_transform_edt(~oth_dots)
        n_c, n_o = int(cand_dots.sum()), int(oth_dots.sum())
        c_to_o = float((oth_dt[cand_dots] <= 3).mean()) if n_c else None
        o_to_c = float((cand_dt[oth_dots] <= 3).mean()) if n_o else None
        rows.append({"name": name, "sha256": sha, "other_dots": n_o,
                     "spearman_footprint": round(rho, 6),
                     "cand_dots_within_3px_of_other": round(c_to_o, 6) if c_to_o is not None else None,
                     "other_dots_within_3px_of_cand": round(o_to_c, 6) if o_to_c is not None else None})
        print(f"{name[:90]:90s} rho={rho:+.4f} c->o={c_to_o:.4f} o->c={o_to_c:.4f}", flush=True)

    flag_s = [r for r in rows if abs(r["spearman_footprint"]) > 0.90]
    flag_d = [r for r in rows if (r["cand_dots_within_3px_of_other"] or 0) > 0.70]
    worst_s = max(rows, key=lambda r: abs(r["spearman_footprint"]))
    worst_d = max(rows, key=lambda r: r["cand_dots_within_3px_of_other"] or 0)
    result = {
        "schema_version": 1,
        "candidate": CAND.relative_to(ROOT).as_posix(),
        "candidate_sha256": cand_sha,
        "candidate_dots": int(cand_dots.sum()),
        "footprint_px": int(foot.sum()),
        "rules": {"surface_spearman_flag_gt": 0.90, "final_dots_within_3px_flag_gt": 0.70,
                  "protocol_direction": "candidate -> other (share of candidate dots within 3 px of other raster)"},
        "n_targets_checked": len(rows),
        "n_targets_skipped": len(skipped),
        "skipped": skipped,
        "n_surface_flags": len(flag_s),
        "n_final_dot_flags": len(flag_d),
        "worst_surface": worst_s,
        "worst_final_dots": worst_d,
        "passes_surface_gate": len(flag_s) == 0,
        "passes_final_dot_gate": len(flag_d) == 0,
        "flagged_final_dot_peers": sorted(flag_d, key=lambda r: -r["cand_dots_within_3px_of_other"])[:20],
        "note": "Surface uses the candidate's value raster as proxy (composite run-time surface was not saved).",
    }
    OUT.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ["n_targets_checked", "n_surface_flags", "n_final_dot_flags",
                                             "passes_surface_gate", "passes_final_dot_gate"]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
