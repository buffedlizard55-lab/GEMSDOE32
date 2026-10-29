#!/usr/bin/env python3
"""Nine-site candidate sweep (2026-10-29): which on-disk discrete submission is unique and best-supported?

Pool (uniqueness registry): every discrete binary GeoTIFF on disk with <= 100,000 in-footprint dots
from (a) the 451 pinned nine-site focus rasters (.cache/registry), (b) docs/downloads, (c) the scored
restore (.cache/gems_data/scored). Duplicate bytes are merged by SHA-256.

For each candidate, against every OTHER pool member (no exemptions, literal protocol):
  * directional dot overlap = share of candidate dots within 3 px of a registry dot (Euclidean, exact
    via cKDTree; equals the repo's distance_transform_edt(~reg)[dots] <= 3 rule);
  * rank correlation of the two binary dot fields (Spearman of binary fields == phi, exact).
Duplicate if overlap > 0.70 or rho > 0.90 (repo gate, gems32.release_gate.compare_registry rule).
The 13gems dense lattice (206,895 dots) is reported separately: it is excluded from the pool by the
<=100k rule and its literal overlap is recorded for every candidate to show the degeneracy.

Only candidates that pass the non-degenerate gate get the shared SGMC-cal holdout evaluator (the
instrument with positive association to live scores in evidence/audit_instrument_gate_20261029.json).
Writes evidence/candidate_sweep_20261029.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import holdout  # noqa: E402

DDIR = ROOT / ".cache" / "gems_data"
LATTICE_NAME = "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
OUT = ROOT / "evidence" / "candidate_sweep_20261029.json"
NINE_PREFIX = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")
TOL_DOTS = 100_000


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files_on_disk():
    cands = []
    for p in sorted((ROOT / ".cache" / "registry").rglob("*.tif")):
        repo = p.relative_to(ROOT / ".cache" / "registry").parts[0]
        if repo.startswith(NINE_PREFIX):
            cands.append(("focus:" + repo, p))
    for p in sorted((ROOT / "docs" / "downloads").glob("*.tif")):
        cands.append(("docs/downloads", p))
    for p in sorted((DDIR / "scored").glob("*.tif")):
        cands.append(("scored-restore", p))
    return cands


def dot_coords(path: Path, foot: np.ndarray):
    """Return (coords[N,2] int32 in-footprint dots, is_binary, n_outside_footprint)."""
    with rasterio.open(path) as ds:
        if ds.count != 1:
            return None, False, 0
        arr = ds.read(1)
    vals = np.unique(arr[np.isfinite(arr)])
    if not np.isin(vals, [0.0, 1.0]).all():
        return None, False, 0
    dots = (arr == 1.0)
    out_n = int((dots & ~foot).sum())
    dots &= foot
    rc = np.argwhere(dots).astype(np.int32)
    return rc, True, out_n


def phi_binary(na: int, nb: int, nab: int, N: int) -> float:
    """Pearson/phi of two binary fields on the footprint == Spearman of the fields (ties)."""
    den = math.sqrt(float(na) * float(N - na) * float(nb) * float(N - nb))
    return float((float(N) * nab - float(na) * nb) / den) if den > 0 else float("nan")


def main() -> int:
    t0 = time.time()
    ctx = holdout.load_holdout_context(DDIR)
    foot = np.asarray(ctx.foot, bool)
    H, W = foot.shape
    N = int(foot.sum())
    # ---- build pool ------------------------------------------------------------------------
    seen: dict[str, dict] = {}
    lattice_rc = None
    for group, p in files_on_disk():
        digest = sha256(p)
        if digest in seen:
            seen[digest]["aliases"].append(str(p.relative_to(ROOT)))
            continue
        rc, is_bin, out_n = dot_coords(p, foot)
        seen[digest] = dict(path=str(p.relative_to(ROOT)), group=group, sha256=digest, binary=is_bin,
                            dots=(None if rc is None else int(len(rc))), outside_footprint_dots=out_n,
                            rc=rc, aliases=[])
        if p.name == LATTICE_NAME:
            lattice_rc = rc
    # Identical DOT SETS are one submission even when the files differ in encoding (-nan vs -zeros).
    by_dots: dict[str, dict] = {}
    for e in seen.values():
        if not (e["binary"] and e["dots"] and 0 < e["dots"] <= TOL_DOTS):
            continue
        key = hashlib.sha256(np.ascontiguousarray(e["rc"]).tobytes()).hexdigest()
        if key in by_dots:
            by_dots[key]["aliases"].append(e["path"])
            by_dots[key]["aliases"].extend(e["aliases"])
        else:
            e["dotset_sha256"] = key
            by_dots[key] = e
    entries = list(by_dots.values())
    for e in entries:
        e["sha256"] = e["dotset_sha256"]
    dense = [e for e in seen.values() if e["binary"] and e["dots"] and e["dots"] > TOL_DOTS]
    # NOTE: entries are unique DOT SETS; the `aliases` list keeps every file (any encoding) that carries them.
    print(f"pool: {len(seen)} unique files; discrete <=100k: {len(entries)}; dense >100k: {len(dense)}", flush=True)

    # flat indices of every pool member's dots (exact pixel lookup into a registry's 3-px dilation)
    flat = {e["sha256"]: (e["rc"][:, 0].astype(np.int64) * W + e["rc"][:, 1]) for e in entries}
    n = len(entries)
    ov = np.full((n, n), np.nan)
    keys = [e["sha256"] for e in entries]
    for j, r in enumerate(entries):
        rm = np.zeros((H, W), bool)
        rm[r["rc"][:, 0], r["rc"][:, 1]] = True
        dil = (ndimage.distance_transform_edt(~rm) <= 3.0).ravel()   # Euclidean <= 3 px (repo rule)
        for i, c in enumerate(entries):
            if i == j:
                continue
            ov[i, j] = dil[flat[c["sha256"]]].mean()
        if j % 50 == 0:
            print(f"  dilation pass {j}/{n} {time.time()-t0:.0f}s", flush=True)
    # phi bound: phi <= N*min(na*ov, nb)/sqrt(na*nb*(N-na)*(N-nb)); compute exact phi only if bound > 0.9
    rows = []
    for i, c in enumerate(entries):
        na = int(c["dots"])
        worst_ov, worst_ov_name = -1.0, None
        worst_phi, worst_phi_name = -2.0, None
        for j, r in enumerate(entries):
            if i == j:
                continue
            o = float(ov[i, j])
            if o > worst_ov:
                worst_ov, worst_ov_name = o, r["path"]
            nb = int(r["dots"])
            bound = N * min(na * o, nb) / math.sqrt(float(na) * nb * (N - na) * (N - nb))
            if bound > 0.9 or o > 0.70:
                # exact phi needs the exact intersection (only computed for near-duplicates)
                nab = int(np.isin(flat[c["sha256"]], flat[r["sha256"]], assume_unique=True).sum())
                ph = phi_binary(na, nb, nab, N)
            else:
                ph = bound
            if ph > worst_phi:
                worst_phi, worst_phi_name = ph, r["path"]
        lat_ov = None
        if lattice_rc is not None:
            lm = np.zeros((H, W), bool)
            lm[lattice_rc[:, 0], lattice_rc[:, 1]] = True
            lat_ov = float(ndimage.distance_transform_edt(~lm).ravel()[flat[c["sha256"]]].__le__(3.0).mean())
        nondeg_pass = bool(worst_ov <= 0.70 and worst_phi <= 0.90)
        rows.append(dict(path=c["path"], group=c["group"], sha256=c["sha256"], dots=na,
                         outside_footprint_dots=c["outside_footprint_dots"], aliases=c["aliases"],
                         max_overlap_vs_pool=round(worst_ov, 6), max_overlap_vs_pool_with=worst_ov_name,
                         max_phi_vs_pool=round(worst_phi, 6), max_phi_vs_pool_with=worst_phi_name,
                         literal_lattice_overlap=(None if lat_ov is None else round(lat_ov, 6)),
                         nondegenerate_gate_pass=nondeg_pass))
        print(f"{c['path'][:70]:70s} dots={na:6d} maxOV={worst_ov:.3f} maxPhi={worst_phi:.3f} "
              f"latOV={lat_ov} pass={nondeg_pass}", flush=True)

    # ---- instrument on the passing set only -------------------------------------------------
    for row in rows:
        row["sgmc_cal"] = None
        row["sgmc_cal_ci95"] = None
        row["hr_b2"] = None
    passing = [r for r in rows if r["nondegenerate_gate_pass"]]
    for row in passing:
        p = ROOT / row["path"]
        with rasterio.open(p) as ds:
            m = (ds.read(1) == 1.0) & foot
        sg = holdout.evaluate_sgmc_with_ci(m, ctx, n_boot=300, name=row["path"])
        row["sgmc_cal"] = round(float(sg["sgmc_prevalence_calibrated_dti"]), 6)
        row["sgmc_cal_ci95"] = [round(float(x), 6) for x in sg["sgmc_calibrated_ci95"]]
        print("SGMC", row["path"][:80], row["sgmc_cal"], row["sgmc_cal_ci95"], flush=True)

    rows.sort(key=lambda r: (-(r["sgmc_cal"] if r["sgmc_cal"] is not None else -1), r["path"]))
    doc = dict(
        schema_version=1, session="2026-10-29 (arena/5f3e9cfe-gemsdoe32)",
        rule="duplicate if directional 3px dot overlap > 0.70 OR binary-field rank correlation > 0.90 vs ANY other pool member; no density exemptions",
        pool_unique_files=len(seen), pool_discrete_le_100k=len(entries), pool_dense_gt_100k=[d["path"] for d in dense],
        candidates=len(rows), passing_nondegenerate=len(passing),
        lattice_name=LATTICE_NAME, lattice_dots=(None if lattice_rc is None else int(len(lattice_rc))),
        instrument="SGMC-CAL-v3.0 (gems32.holdout.evaluate_sgmc_with_ci, 62,703 off-catalogue positives, n_boot=300)",
        rows=rows, runtime_s=round(time.time() - t0, 1),
    )
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print("wrote", OUT, "runtime", doc["runtime_s"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
