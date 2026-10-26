#!/usr/bin/env python3
"""H42-1 — hanging-wall conditional intensity (HWCI). Pre-registered in
``knowledge/04_preregistration_h42_hanging_wall_2026-10-25.md`` (commit 86de6eb, frozen before
any H42 number existed).

Shared tools only (PARALLEL-RUN PROTOCOL rule 2): the pinned ``vendor/gems57`` template supplies the
folds (``holdout.buffered_component_draw``), the exact scorer (``evaluate_holdout.evaluate`` +
``pooled_summary``), the emitter (``emit.emit_decimated``), the network geometry
(``network.nearest_frame`` / ``local_strike`` / ``offset_components`` / ``rel_strike``), the
registry gate (``uniqueness``) and the fail-closed writer (``submission_writer``).  The cached
35-channel feature stack is ``.cache/gems_work/feature_stack.npy`` (``scripts/build_features.py``).

Stages (each cached under ``.cache/gems_work/h42/``):
  0 inputs + champion construction check      3 LOQO fits for HWCI / SYM / EVID + emission + scoring
  1 per-draw relational context                4 pooled paired bootstrap (G2, G3)
  2 leakage canary (G1) — stops on failure     5 final refit, surface gate, dots, final gate, writer
Outputs: ``evidence/h42_run.json`` and ``evidence/h42_run_card.json`` (written whatever the verdict).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import emit as g57emit  # noqa: E402
from gems57 import evaluate_holdout as g57eval  # noqa: E402
from gems57 import grid as g57grid  # noqa: E402
from gems57 import holdout as g57hold  # noqa: E402
from gems57 import network as g57net  # noqa: E402
from gems57 import submission_writer as g57write  # noqa: E402
from gems57 import uniqueness as g57uniq  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
WORK = ROOT / ".cache" / "gems_work"
CACHE = WORK / "h42"
STACK = WORK / "feature_stack.npy"
D28 = DATA / "scored" / "gems24-h25-1-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
CHAMPION = ROOT / "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif"
REGISTRY_MANIFEST = ROOT / "registry" / "focus_registry_manifest.json"
PREREG = "knowledge/04_preregistration_h42_hanging_wall_2026-10-25.md"
PREREG_COMMIT = "86de6eb"

SEEDS = (20, 21)
HIDE_FRAC = 0.20
BUFFER_PX = 3
B_GATE_PX = 2
N_NEG = 300_000
FINAL_BUDGET = 37_654          # the champion's emitted mass (matched comparison)
AUC_LIMIT = 0.90
RNG_SEED = 20261025
GBM = dict(max_iter=200, learning_rate=0.06, max_leaf_nodes=31, min_samples_leaf=200,
           l2_regularization=1.0, random_state=RNG_SEED)

# cached stack channel indices (src/gems32/features.py CHANNELS order)
STACK_COLS = {"rtp": 1, "tmi_hg": 2, "grav_slope": 4, "det_elev": 11, "iso_grav": 12,
              "depth_base": 14, "cond": 16, "slope": 18, "curv_s1": 19, "curv_s2": 20,
              "ridge_s1": 21, "ridge_s2": 22, "relief5": 24, "tophat2": 25, "tmi_edge": 26,
              "grav_edge": 28, "cond_edge": 29, "depth_grad": 30, "coherence_s2": 31}
LIDAR_COLS = {"ex_max": 0, "ex_mean": 1, "step_max": 2, "lapneg_max": 3, "lappos_max": 4,
              "downface_max": 5, "upface_max": 6, "cross_max": 7, "relief": 8, "coh100": 9,
              "lidar_valid": 11}
EVIDENCE = list(STACK_COLS) + list(LIDAR_COLS)
RELATIONAL = ["logd", "d_perp", "d_par_abs", "rel_strike", "coh_q", "vis_density"]
SIDE = ["dz", "dzn", "side"]
ARMS = {"HWCI": EVIDENCE + RELATIONAL + SIDE, "SYM": EVIDENCE + RELATIONAL, "EVID": EVIDENCE}
ALL_FEATS = EVIDENCE + RELATIONAL + SIDE


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_mask(path: Path) -> np.ndarray:
    with rasterio.open(path) as s:
        a = s.read(1)
    return np.isfinite(a) & (a > 0)


# ----------------------------------------------------------------------------- static inputs
class Static:
    def __init__(self, grid):
        self.grid = grid
        H, W = grid.shape
        self.stack = np.load(STACK, mmap_mode="r").reshape(H * W, -1)
        with rasterio.open(DATA / "external" / "lidar_scarp_features_u8.tif") as s:
            if (s.height, s.width) != (H, W) or s.transform != g57grid.TRANSFORM:
                raise SystemExit("lidar grid mismatch")
            self.lidar = s.read()                       # (12, H, W) uint8
        z = np.asarray(self.stack[:, STACK_COLS["det_elev"]]).reshape(H, W).astype(np.float32)
        self.zs = ndi.gaussian_filter(z, 2.0).astype(np.float32)
        del z
        self.dem_strike = self._dem_strike(self.zs)

    @staticmethod
    def _dem_strike(zs: np.ndarray, sigma: float = 2.0) -> np.ndarray:
        """Lineament strike of the smoothed DEM, same convention as gems57.network.local_strike."""
        gy, gx = np.gradient(zs)
        jxx = ndi.gaussian_filter(gx * gx, sigma)
        jyy = ndi.gaussian_filter(gy * gy, sigma)
        jxy = ndi.gaussian_filter(gx * gy, sigma)
        del gx, gy
        theta = 0.5 * np.arctan2(2.0 * jxy, jxx - jyy) + np.pi / 2.0
        del jxx, jyy, jxy
        strike = (np.degrees(np.arctan2(np.cos(theta), -np.sin(theta))) % 180.0).astype(np.float32)
        return strike

    def evidence(self, idx: np.ndarray) -> np.ndarray:
        order = np.argsort(idx)
        s_idx = idx[order]
        out = np.empty((idx.size, len(EVIDENCE)), np.float32)
        cols = list(STACK_COLS.values())
        block = np.asarray(self.stack[s_idx][:, cols], np.float32)
        out[order, : len(cols)] = block
        del block
        lid = self.lidar.reshape(self.lidar.shape[0], -1)
        for j, b in enumerate(LIDAR_COLS.values()):
            out[:, len(cols) + j] = lid[b, idx].astype(np.float32)
        return out


class Context:
    """Catalogue-relational fields computed from one *visible* catalogue mask only."""

    def __init__(self, static: Static, visible: np.ndarray):
        d, iy, ix = g57net.nearest_frame(visible)
        self.d = d.astype(np.float32)
        self.iy = iy.astype(np.int32)
        self.ix = ix.astype(np.int32)
        del d, iy, ix
        strike, coh = g57net.local_strike(visible, smooth_px=3.0)
        self.strike_vis = np.nan_to_num(strike, nan=0.0).astype(np.float32)
        self.coh_vis = coh.astype(np.float32)
        del strike, coh
        self.density = ndi.uniform_filter(visible.astype(np.float32), size=21)
        self.static = static

    def relational(self, idx: np.ndarray) -> np.ndarray:
        W = self.d.shape[1]
        r, c = np.divmod(idx, W)
        qy, qx = self.iy.ravel()[idx], self.ix.ravel()[idx]
        d = self.d.ravel()[idx]
        sq = self.strike_vis[qy, qx]
        d_par, d_perp, _ = g57net.offset_components((r - qy).astype(np.float64),
                                                     (c - qx).astype(np.float64), sq)
        rel = g57net.rel_strike(self.static.dem_strike.ravel()[idx], sq)
        zs = self.static.zs
        dz = zs.ravel()[idx] - zs[qy, qx]
        out = np.empty((idx.size, len(RELATIONAL) + len(SIDE)), np.float32)
        out[:, 0] = np.log1p(np.minimum(d, 300.0))
        out[:, 1] = np.minimum(d_perp, 300.0)
        out[:, 2] = np.minimum(np.abs(d_par), 300.0)
        out[:, 3] = rel
        out[:, 4] = self.coh_vis[qy, qx]
        out[:, 5] = self.density.ravel()[idx]
        out[:, 6] = np.clip(dz, -400.0, 400.0)
        out[:, 7] = np.clip(dz / np.maximum(d, 1.0), -50.0, 50.0)
        out[:, 8] = np.sign(dz) * (np.abs(dz) > 5.0)
        return out

    def features(self, idx: np.ndarray) -> np.ndarray:
        return np.concatenate([self.static.evidence(idx), self.relational(idx)], axis=1)


def cols_for(arm: str) -> list[int]:
    return [ALL_FEATS.index(f) for f in ARMS[arm]]


# ----------------------------------------------------------------------------- registry index
def registry_index(footprint: np.ndarray) -> tuple[dict, list[dict]]:
    """Dedupe the focus registry by sha256; exclude (with reasons) files not on the scoring grid."""
    man = json.loads(REGISTRY_MANIFEST.read_text())
    by_sha: dict[str, dict] = {}
    excluded = []
    for r in man["rasters"]:
        if r.get("status") != "ok":
            excluded.append(dict(file=r.get("path"), reason="fetch failed"))
            continue
        e = by_sha.setdefault(r["sha256"], dict(repo_first=r["repo"], sources=[], cache_file=r["local"],
                                                 sha256=r["sha256"]))
        e["sources"].append(f"{r['repo']}:{r['path']}")
    rasters = []
    for sha, e in by_sha.items():
        p = ROOT / e["cache_file"]
        try:
            with rasterio.open(p) as s:
                ok = (s.count == 1 and (s.height, s.width) == footprint.shape
                      and s.crs is not None and s.crs.to_epsg() == 32611 and s.transform == g57grid.TRANSFORM)
            if not ok:
                excluded.append(dict(file=e["sources"][0], reason="not on the 3730x3292 EPSG:32611 scoring grid"))
                continue
        except Exception as exc:  # unreadable bytes cannot be a portal-valid submission either
            excluded.append(dict(file=e["sources"][0], reason=f"unreadable: {exc}"))
            continue
        rasters.append(e)
    idx = dict(rasters=rasters, complete_accessible_scan=(man["n_failed"] == 0), errors=[],
               refs=man["refs"], generated_utc=man["generated_utc"])
    return idx, excluded


def gate_registry(arr: np.ndarray, footprint: np.ndarray, index: dict, phase: str) -> dict:
    t0 = time.time()
    res = g57uniq.compare_array_to_registry(arr, index, footprint, include_reverse=True)
    two = g57uniq.two_phase_summary(res["rows"], int(footprint.sum()),
                                    expected_rasters=len(index["rasters"]))
    rows = sorted([r for r in res["rows"] if "error" not in r],
                  key=lambda r: -r["my_dots_within_3px_of_theirs"])[:8]
    top_rho = sorted([r for r in res["rows"] if r.get("spearman_full_footprint") is not None],
                     key=lambda r: -r["spearman_full_footprint"])[:5]
    slim = lambda r: {k: r.get(k) for k in ("repo", "submission", "their_dots", "my_dots_within_3px_of_theirs",
                                            "their_dots_within_3px_of_mine", "spearman_full_footprint",
                                            "jaccard_dot_sets")}
    out = dict(phase=phase, seconds=round(time.time() - t0, 1),
               registry_rasters=len(index["rasters"]), errors=res["missing_or_invalid"],
               worst_spearman=res["worst_spearman_full_footprint"], worst_spearman_submission=res["worst_rho_submission"],
               worst_dot_overlap_literal=res["worst_dot_overlap"], worst_overlap_submission_literal=res["worst_overlap_submission"],
               literal=two["literal_reading"], like_for_like=two["like_for_like_reading"],
               top_overlap_rows=[slim(r) for r in rows], top_rho_rows=[slim(r) for r in top_rho])
    rho_fire = two["literal_reading"]["rho_firings"] > 0
    out["duplicate"] = bool(rho_fire or two["like_for_like_reading"]["duplicate"] or res["missing_or_invalid"])
    return out


# ----------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bootstrap", type=int, default=1000)
    a = ap.parse_args()
    t_start = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    report: dict = dict(hypothesis="H42-1 hanging-wall conditional intensity (HWCI)", preregistration=PREREG,
                        preregistration_commit=PREREG_COMMIT, experiment_number=1, experiments_authorized=3,
                        started_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        evaluator_version=g57eval.VERSION, template="vendor/gems57 (57GEMSDOE@822a0ce)",
                        deviations=[])
    out_json = ROOT / "evidence" / "h42_run.json"

    def save():
        report["elapsed_seconds"] = round(time.time() - t_start, 1)
        out_json.write_text(json.dumps(report, indent=1, allow_nan=False, default=float) + "\n")

    # ---- stage 0: inputs and champion construction
    grid = g57grid.load_grid(DATA)
    fp, cat = grid.footprint, grid.catalogue
    H, W = grid.shape
    report["inputs"] = {str(p.relative_to(ROOT)): sha256(p) for p in
                        (DATA / "training_features.tif", DATA / "existing_faults.tif", DATA / "sample_submission.tif",
                         DATA / "external" / "lidar_scarp_features_u8.tif", D28, CHAMPION)}
    d_cat = ndi.distance_transform_edt(~cat).astype(np.float32)
    d28, champ = read_mask(D28) & fp, read_mask(CHAMPION) & fp
    report["champion_construction"] = dict(
        d28_dots=int(d28.sum()), champion_dots=int(champ.sum()),
        champion_equals_d28_minus_within_2px=bool((((d28 & (d_cat > 2))) == champ).all()))
    log(f"grid ok; footprint {int(fp.sum())}, catalogue {int(cat.sum())}; champion check "
        f"{report['champion_construction']}")
    static = Static(grid)
    log("static evidence ready")

    # ---- stage 1/2: folds, per-draw context, canary
    draws = {}
    for seed in SEEDS:
        folds, _ = g57hold.buffered_component_draw(grid, seed=seed, hide_frac=HIDE_FRAC, buffer_px=BUFFER_PX)
        draws[seed] = folds
    report["folds"] = {f"draw{s}": [f["receipt"] for f in folds] for s, folds in draws.items()}
    report["withheld_positive_pixels"] = {f"draw{s}": int(sum(int(f["truth"].sum()) for f in folds))
                                          for s, folds in draws.items()}
    log(f"folds built: {report['withheld_positive_pixels']}")

    rng = np.random.default_rng(RNG_SEED)
    canary_rows: dict[str, list] = {f: [] for f in ALL_FEATS}
    contexts = {}
    samples = {}
    for seed, folds in draws.items():
        visible = folds[0]["visible"]
        masked_known = folds[0]["masked_known"]
        ctx = Context(static, visible)
        contexts[seed] = ctx
        # per-region samples (positives = withheld truth; negatives = eligible non-catalogue pixels)
        for f in folds:
            region = f["region"]
            pos = np.flatnonzero((f["truth"] & region).ravel())
            pool = np.flatnonzero((region & fp & ~masked_known & ~f["truth"]).ravel())
            neg = rng.choice(pool, size=min(N_NEG // 4, pool.size), replace=False)
            Xp, Xn = ctx.features(pos), ctx.features(neg)
            samples[(seed, f["fold"])] = (Xp, Xn)
            y = np.r_[np.ones(len(Xp)), np.zeros(len(Xn))]
            X = np.vstack([Xp, Xn])
            for j, name in enumerate(ALL_FEATS):
                col = X[:, j]
                auc = 0.5 if np.ptp(col) == 0 else float(roc_auc_score(y, col))
                canary_rows[name].append(dict(draw=seed, fold=f["name"], auc=auc, n_pos=int(len(Xp))))
        log(f"draw {seed}: context + samples ready")
    canary = {}
    for name, rows in canary_rows.items():
        w = np.array([r["n_pos"] for r in rows], float)
        auc = float(np.average([r["auc"] for r in rows], weights=w))
        canary[name] = dict(pooled_auc=auc, max_abs_auc=max(auc, 1 - auc),
                            worst_cell=max(max(r["auc"], 1 - r["auc"]) for r in rows))
    worst = max(canary, key=lambda k: canary[k]["worst_cell"])
    report["canary"] = dict(limit=AUC_LIMIT, per_feature=canary, worst_feature=worst,
                            worst_cell_auc=canary[worst]["worst_cell"],
                            passed=bool(all(v["worst_cell"] <= AUC_LIMIT for v in canary.values())))
    save()
    log(f"canary worst {worst} = {canary[worst]['worst_cell']:.3f}; passed={report['canary']['passed']}")
    if not report["canary"]["passed"]:
        report.update(verdict="negative", stopped_reason="leakage-canary (G1)")
        save()
        write_card(report, None, None, None)
        return 2

    # ---- stage 3: LOQO fits, emission, exact scoring
    terms = {arm: np.zeros(0) for arm in list(ARMS) + ["CHAMP_RECIPE"]}
    fold_rows = []
    importances = {}
    for seed, folds in draws.items():
        ctx = contexts[seed]
        gate = ctx.d > B_GATE_PX
        for f in folds:
            q = f["fold"]
            region = f["region"]
            allowed = region & fp & ~f["masked_known"] & gate
            champ_dots = d28 & allowed
            budget = int(champ_dots.sum())
            preds = {"CHAMP_RECIPE": champ_dots}
            Xtr = np.vstack([np.vstack(samples[(seed, j)]) for j in range(4) if j != q])
            ytr = np.concatenate([np.r_[np.ones(len(samples[(seed, j)][0])), np.zeros(len(samples[(seed, j)][1]))]
                                  for j in range(4) if j != q])
            test_idx = np.flatnonzero((region & fp).ravel())
            Xte = ctx.features(test_idx)
            for arm in ARMS:
                cols = cols_for(arm)
                model = HistGradientBoostingClassifier(**GBM).fit(Xtr[:, cols], ytr)
                prob = np.zeros(H * W, np.float32)
                prob[test_idx] = model.predict_proba(Xte[:, cols])[:, 1].astype(np.float32)
                ranked, _ = g57emit.emit_decimated(prob.reshape(H, W), allowed, tile_px=3)
                preds[arm] = g57emit.emit_prefix(ranked, budget)
                del prob, ranked
            for arm, dots in preds.items():
                res, t = g57eval.evaluate(dots.astype(np.float32), f, fp, block_side=200,
                                          origin=(0, 0), global_shape=(H, W))
                terms[arm] = t if terms[arm].size == 0 else terms[arm] + t
                fold_rows.append(dict(draw=seed, fold=f["name"], arm=arm, dti=res["dti"], tp=res["tp"],
                                      fp=res["fp"], fn=res["fn"], n_truth=res["n_truth"],
                                      emitted=res["n_emitted"], budget=budget))
            log(f"draw {seed} fold {f['name']}: budget {budget}; " + ", ".join(
                f"{r['arm']} {r['dti']:.4f}" for r in fold_rows[-len(preds):]))
            del Xtr, ytr, Xte
            report["fold_rows"] = fold_rows
            save()

    # ---- stage 4: pooled paired bootstrap
    summ = g57eval.pooled_summary(terms, draws=a.bootstrap, seed=520810, candidate="HWCI")
    report["pooled"] = summ
    sc, pdiff = summ["scores"], summ["paired_differences"]
    g2 = pdiff["SYM"]["delta"] > 0 and pdiff["SYM"]["ci95"][0] > 0
    g3 = pdiff["CHAMP_RECIPE"]["delta"] > 0 and pdiff["CHAMP_RECIPE"]["ci95"][0] > 0
    report["gates"] = dict(G1_canary=report["canary"]["passed"], G2_hypothesis_side_signal=bool(g2),
                           G3_beats_champion_recipe=bool(g3))
    log("pooled: " + ", ".join(f"{k} {v['dti']:.4f} {v['ci95']}" for k, v in sc.items()))
    log("paired vs HWCI: " + ", ".join(f"{k} {v['delta']:+.4f} {v['ci95']}" for k, v in pdiff.items()))
    save()

    # ---- stage 5: final refit, surface gate, dots, final gate, writer
    Xs, ys = [], []
    for (seed, q), (Xp, Xn) in samples.items():
        Xs += [Xp, Xn]
        ys += [np.ones(len(Xp)), np.zeros(len(Xn))]
    cols = cols_for("HWCI")
    final_model = HistGradientBoostingClassifier(**GBM).fit(np.vstack(Xs)[:, cols], np.concatenate(ys))
    del Xs, ys, samples
    full_ctx = Context(static, cat)
    del contexts
    prob = np.zeros(H * W, np.float32)
    fidx = np.flatnonzero(fp.ravel())
    for chunk in np.array_split(fidx, 6):
        prob[chunk] = final_model.predict_proba(full_ctx.features(chunk)[:, cols])[:, 1].astype(np.float32)
    prob = prob.reshape(H, W)
    surface = np.where(fp, prob / max(float(prob.max()), 1e-12), 0.0).astype(np.float32)
    np.save(CACHE / "final_surface.npy", surface)
    index, excluded = registry_index(fp)
    report["registry_scope"] = dict(manifest=str(REGISTRY_MANIFEST.relative_to(ROOT)), unique_rasters=len(index["rasters"]),
                                    excluded=excluded, refs=index["refs"])
    log(f"registry: {len(index['rasters'])} unique on-grid rasters ({len(excluded)} excluded)")
    report["surface_gate"] = gate_registry(surface, fp, index, "surface-before-placement")
    save()
    log(f"surface gate: rho {report['surface_gate']['worst_spearman']}, duplicate={report['surface_gate']['duplicate']}")
    allowed = fp & ~cat & (full_ctx.d > B_GATE_PX)
    ranked, _ = g57emit.emit_decimated(prob, allowed, tile_px=3)
    dots = g57emit.emit_prefix(ranked, FINAL_BUDGET)
    final = dots.astype(np.float32)
    np.save(CACHE / "final_dots.npy", dots)
    report["final_dots"] = dict(n=int(dots.sum()), on_catalogue=int((dots & cat).sum()),
                                within_2px_of_catalogue=int((dots & (d_cat <= 2)).sum()),
                                median_dist_to_catalogue_px=float(np.median(d_cat[dots])),
                                frac_hanging_wall_side=float((full_ctx.relational(np.flatnonzero(dots.ravel()))[:, 6] < 0).mean()),
                                overlap_with_champion_3px=float(g57uniq.dot_overlap(final, champ.astype(np.float32))))
    report["final_gate"] = gate_registry(final, fp, index, "final-dots")
    save()
    log(f"final gate: overlap {report['final_gate']['like_for_like']['worst_forward_overlap_dot_fields']}, "
        f"duplicate={report['final_gate']['duplicate']}")
    report["feature_importance_note"] = "HistGradientBoosting has no native importances; see ablation arms SYM/EVID."

    g4 = not report["surface_gate"]["duplicate"] and not report["final_gate"]["duplicate"]
    report["gates"]["G4_lane_unique"] = bool(g4)
    content = hashlib.sha256(np.packbits(dots[fp]).tobytes()).hexdigest()[:8]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"gemsdoe32-h42-hwci-{int(dots.sum())}-{stamp}-{content}-zeros"
    hd = sc["HWCI"]
    ok_submit = bool(report["canary"]["passed"] and g2 and g3 and g4)
    verdict_word = "OK TO SUBMIT" if ok_submit else "DO NOT SUBMIT"
    note = (f"GEMSDOE32 H42 hanging-wall HWCI {int(dots.sum())} dots B2 | HOLDOUT {hd['dti']:.4f} | id {content}"
            + ("" if ok_submit else " | research only"))
    report["submission"] = dict(name=name, note=note, note_chars=len(note), verdict_word=verdict_word)
    path = ROOT / "docs" / "downloads" / f"{name}.tif"
    receipt = g57write.write_submission(path, final, DATA / "sample_submission.tif", fp, note=note, name=name,
                                        catalogue=cat, metadata=dict(hypothesis="H42-1", verdict=verdict_word))
    chk = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_submission.py"), str(path),
                          "--template", str(DATA / "sample_submission.tif"), "--strict-finite"],
                         capture_output=True, text=True, env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"})
    report["validator"] = dict(template_writer=receipt["validator"], template_report_ok=receipt["template_report"]["ok"],
                               check_submission_exit=chk.returncode,
                               check_submission_tail=chk.stdout.strip().splitlines()[-1] if chk.stdout else chk.stderr[-300:])
    g5 = bool(receipt["template_report"]["ok"] and chk.returncode == 0)
    report["gates"]["G5_format"] = g5
    ok_submit = ok_submit and g5
    report["verdict"] = "promote" if ok_submit else "negative"
    report["ok_to_submit"] = ok_submit
    report["raster_sha256"] = receipt["sha256"]
    report["file"] = f"docs/downloads/{name}.tif"
    save()
    write_card(report, receipt, name, note)
    log(f"DONE verdict={report['verdict']} file={name}.tif sha={receipt['sha256'][:12]}")
    return 0


def _diag_summary(diag):
    """Compact, card-sized view of scripts/h42_finalize.py diagnostics (full detail in evidence/h42_run.json)."""
    if not diag:
        return None
    d4 = diag["D4_sgmc_off_catalogue"]
    d2 = diag["D2_band_matched_null"]
    return dict(
        D4_independent_sgmc_off_catalogue=dict(
            truth_pixels=d4.get("truth_pixels"), evaluator_version=d4.get("evaluator_version"),
            scores={k: dict(dti=v["dti"], ci95=v["ci95"]) for k, v in d4["scores"].items()},
            paired_vs_H42={k: dict(delta=v["delta"], ci95=v["ci95"]) for k, v in d4["paired_differences"].items()},
            reading="H42 final raster is below the champion AND below random dots on off-catalogue truth: the "
                    "catalogue-hidden gain is a gap-filling artefact of the instrument, not transferable skill."),
        D2_band_matched_null=dict(fired_excluding_space_filling=d2["n_fired_excluding_space_filling"],
                                  worst=d2["rows"][1] if len(d2["rows"]) > 1 else (d2["rows"][0] if d2["rows"] else None)),
        D1_space_filling=diag["D1_space_filling"]["space_filling_rasters"],
        D3_surface_corrected={k: v for k, v in diag["D3_surface_corrected"].items() if k != "statistic"},
    )


def write_card(report: dict, receipt, name, note) -> None:
    pooled = report.get("pooled", {})
    sc = pooled.get("scores", {})
    card = dict(
        hypothesis=report["hypothesis"] + " — P(new fault | distance, topographically signed side, strike alignment "
                   "to the nearest visible trace, local scarp evidence), fitted by fault-component hide-and-recover.",
        mechanism="Synthetic/antithetic hanging-wall splays and basinward-stepping piedmont scarps form on the "
                  "down-thrown side of mapped normal faults at 0.3-3 km; the side is signed by smoothed det_elev "
                  "relative to the nearest visible trace (no dip attribute needed).",
        non_fault_mimic="Pluvial Lake Lahontan shorelines and fan-toe/terrace risers: level, scarp-like steps that lie "
                        "on the same (basinward) side the hypothesis favours; not separable without absolute elevation.",
        holdout={k: dict(evidence_class="HOLDOUT-DTI", evaluator_version=v.get("evaluator_version"), dti=v.get("dti"),
                         ci95=v.get("ci95"), withheld_positive_pixels=v.get("withheld_positive_pixels"))
                 for k, v in sc.items()},
        paired_differences_vs_HWCI=pooled.get("paired_differences"),
        canary=dict(passed=report.get("canary", {}).get("passed"), worst_feature=report.get("canary", {}).get("worst_feature"),
                    worst_cell_auc=report.get("canary", {}).get("worst_cell_auc")),
        correlation_overlap_vs_registry=dict(surface=report.get("surface_gate"), final=report.get("final_gate")) if report.get("final_gate") else None,
        raster_sha256=report.get("raster_sha256"),
        validator_output=report.get("validator"),
        submission_name=name, note=note,
        gates=report.get("gates"),
        verdict_reasons=report.get("verdict_reasons", []),
        diagnostics_post_run=_diag_summary(report.get("diagnostics_post_run")),
        verdict=report.get("verdict"), ok_to_submit=bool(report.get("ok_to_submit", False)),
        organizer_confirmed_score=None, submission_slots_used=0, experiments_run=report.get("experiment_number"),
        deviations=report.get("deviations"), elapsed_seconds=report.get("elapsed_seconds"),
    )
    (ROOT / "evidence" / "h42_run_card.json").write_text(json.dumps(card, indent=1, allow_nan=False, default=float) + "\n")


if __name__ == "__main__":
    sys.exit(main())
