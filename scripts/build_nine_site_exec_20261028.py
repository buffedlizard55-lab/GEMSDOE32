#!/usr/bin/env python3
"""Build the nine-site executive summary (docs/nine-site-static-recheck-20261028.html) from evidence.

Inputs (all produced by this session's scripts; nothing typed by hand except PUBLISHED):
  evidence/focus9_independent_verification_20261028.json   format, sha256, pairwise + registry uniqueness
  evidence/holdout_static_recheck_20261028.json           static HIDE-RECOVER and SGMC-cal per file
PUBLISHED = owner-reported leaderboard names/scores copied from the session prompt (OWNER-REPORT).
Writes evidence/evaluator_rank_check_20261028.json and docs/nine-site-static-recheck-20261028.html.

Labels used on the page:
  OWNER-REPORT    score claimed in the owner's submission log (no DrivenData receipt in this repo)
  HOLDOUT-DTI     repo evaluator (evaluator version, n withheld positives, 95% CI) on the file's bytes
  PROJECTION      linear fit of OWNER-REPORT on SGMC-cal across the nine sites; NOT a score
"""
from __future__ import annotations

import html
import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
VER = json.loads((ROOT / "evidence" / "focus9_independent_verification_20261028.json").read_text())
HOLD = json.loads((ROOT / "evidence" / "holdout_static_recheck_20261028.json").read_text())["results"]
RANK_OUT = ROOT / "evidence" / "evaluator_rank_check_20261028.json"
PAGE = ROOT / "docs" / "nine-site-static-recheck-20261028.html"

PUBLISHED = {  # OWNER-REPORT, from the session prompt's leaderboard-name list (best file per site)
    "GEMSDOE24": 0.2477, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449, "GEMSDOE28": 0.2710,
    "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708, "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632,
    "GEMSDOE36": 0.2750,
}
SITES = list(PUBLISHED)
H51 = "H51-1-EWSP (candidate)"
SITE_PAGE = {s: f"https://buffedlizard55-lab.github.io/{s}/" for s in SITES}


def _hold_for(path: str) -> dict:
    for v in HOLD.values():
        if v["path"] == path:
            return v
    raise KeyError(path)


def _file_link(name: str, row: dict) -> str:
    """Official location: the owning GitHub repo at the pinned ref (site files) or this repo (local)."""
    if row.get("repo_path", "").startswith("local"):
        fn = Path(row["path"]).name
        return f"downloads/{fn}", fn
    repo, rel = row["repo_path"].split("/", 1)
    url = f"https://github.com/buffedlizard55-lab/{repo}/blob/{row['ref']}/{rel}"
    return url, Path(rel).name


def _overlap(a: str, b: str) -> float:
    for p in VER["pairwise_among_candidates"]:
        if p["A"] == a and p["B"] == b:
            return p["share_A_dots_within_3px_of_B"]
    raise KeyError((a, b))


def _rho(a: str, b: str) -> float:
    for p in VER["pairwise_among_candidates"]:
        if p["A"] == a and p["B"] == b:
            return p["spearman_footprint"]
    raise KeyError((a, b))


def main() -> int:
    cands = VER["candidates"]
    uniq = VER["uniqueness_summary"]
    rows = []
    for s in SITES:
        c = cands[s]
        h = _hold_for(c["path"])
        others = [t for t in SITES if t != s]
        max_ov_focus = max(_overlap(s, t) for t in others)
        max_rho_focus = max(_rho(s, t) for t in others)
        u = uniq[s]
        rows.append({
            "site": s, "published": PUBLISHED[s], "file_name": Path(c["path"]).name,
            "file_sha256": c["sha256"], "dots": c["dots_inside_footprint"], "format_pass": c["format_pass"],
            "link": _file_link(s, c)[0], "src_repo_path": c.get("repo_path"),
            "hr": h["hide_recover_b2"], "sg": h["sgmc_cal"],
            "max_overlap_other_focus": max_ov_focus, "max_rho_other_focus": max_rho_focus,
            "unique_vs_focus": max_ov_focus <= 0.70 and max_rho_focus <= 0.90,
            "max_overlap_registry_le100k": u["max_share_within_3px_vs_registry_le100k"],
            "max_overlap_registry_all": u["max_share_within_3px_vs_all_registry_incl_dense"],
            "r13_overlap": u["share_within_3px_vs_r13_dense"],
            "identical_variants_excluded": u["identical_dot_set_variants_excluded"],
        })

    # Evaluator agreement (n = 9 sites, OWNER-REPORT vs static SGMC-cal and HIDE-RECOVER)
    pub = np.array([r["published"] for r in rows])
    sg = np.array([r["sg"]["prevalence_calibrated_dti"] for r in rows])
    hr = np.array([r["hr"]["pooled_dti"] for r in rows])
    rho_sg, p_sg = stats.spearmanr(pub, sg)
    rho_hr, p_hr = stats.spearmanr(pub, hr)
    lr = stats.linregress(sg, pub)
    n = len(sg)
    h51 = cands[H51]
    h51_sg = _hold_for(h51["path"])["sgmc_cal"]["prevalence_calibrated_dti"]
    # 95% prediction interval for a new single file on the SGMC-cal line
    t = stats.t.ppf(0.975, n - 2)
    resid_se = np.sqrt(np.sum((pub - (lr.intercept + lr.slope * sg)) ** 2) / (n - 2))
    xbar = sg.mean()
    sxx = np.sum((sg - xbar) ** 2)
    se_pred = resid_se * np.sqrt(1 + 1 / n + (h51_sg - xbar) ** 2 / sxx)
    yhat = lr.intercept + lr.slope * h51_sg
    proj = {"label": "PROJECTION (not a score)", "n_sites_fit": n,
            "point": round(float(yhat), 4), "pi95": [round(float(yhat - t * se_pred), 4), round(float(yhat + t * se_pred), 4)],
            "fit": {"slope": round(float(lr.slope), 4), "intercept": round(float(lr.intercept), 4), "r2": round(float(lr.rvalue ** 2), 4)}}
    rank = {"schema_version": 1, "n_sites": n,
            "spearman_published_vs_sgmc_cal": round(float(rho_sg), 4), "p_sgmc": float(p_sg),
            "spearman_published_vs_hide_recover": round(float(rho_hr), 4), "p_hide_recover": float(p_hr),
            "h51_projection": proj, "h51_sgmc_cal_static": h51_sg,
            "caveat": "n=9 site files; OWNER-REPORT scores; correlation is not causation; PROJECTION is not a leaderboard estimate."}
    RANK_OUT.write_text(json.dumps(rank, indent=1) + "\n")

    PAGE.write_text(render(rows, rank, cands, h51))
    print(json.dumps({"rank": {k: rank[k] for k in ("spearman_published_vs_sgmc_cal", "spearman_published_vs_hide_recover")},
                      "h51_projection": proj}, indent=1))
    return 0


def esc(x) -> str:
    return html.escape(str(x))


def render(rows, rank, cands, h51) -> str:
    best = max(rows, key=lambda r: r["published"])
    h51_row = cands[H51]
    h51_hold = _hold_for(h51_row["path"])
    h51_ov_focus = max(_overlap(H51, s) for s in SITES)
    h51_ov_le100k = VER["uniqueness_summary"][H51]["max_share_within_3px_vs_registry_le100k"]
    h51_ov_all = VER["uniqueness_summary"][H51]["max_share_within_3px_vs_all_registry_incl_dense"]
    h51_r13 = VER["uniqueness_summary"][H51]["share_within_3px_vs_r13_dense"]
    cham = next(r for r in rows if r["site"] == "GEMSDOE32")
    ci = lambda v: f"[{v[0]:.4f}, {v[1]:.4f}]"

    trs = []
    for r in rows:
        is_best = r["site"] == best["site"]
        badge = ("<b style='color:#0a7d2c'>BEST PUBLISHED</b> &mdash; already submitted (OWNER-REPORT). "
                 "Re-submitting adds no information." if is_best else
                 "Already submitted (OWNER-REPORT). Not unique vs other focus sites.")
        uniq_txt = ("<span class=ok>YES</span>" if r["unique_vs_focus"] else
                    f"<span class=no>NO</span> (max {r['max_overlap_other_focus']*100:.1f}% within 3 px)")
        trs.append(
            f"<tr><td><b>{esc(r['site'])}</b><br><a href='{SITE_PAGE[r['site']]}'>site</a></td>"
            f"<td><a href='{esc(r['link'])}'>{esc(r['file_name'])}</a><br><span class=mut>sha256 {esc(r['file_sha256'][:16])}&hellip; &middot; {r['dots']:,} dots &middot; format {'PASS' if r['format_pass'] else 'FAIL'}</span></td>"
            f"<td>{r['published']:.4f}<br><span class=mut>OWNER-REPORT</span></td>"
            f"<td>{r['sg']['prevalence_calibrated_dti']:.4f} {ci(r['sg']['calibrated_ci95'])}<br><span class=mut>HOLDOUT-DTI SGMC-CAL-v3.0 &middot; n=62,703</span></td>"
            f"<td>{r['hr']['pooled_dti']:.4f} {ci(r['hr']['ci95'])}<br><span class=mut>HOLDOUT-DTI HIDE-RECOVER-v3.0 &middot; n=22,232</span></td>"
            f"<td>{uniq_txt}</td><td>{badge}</td></tr>")

    trs.append(
        "<tr class=cand><td><b>H51-1-EWSP</b><br><span class=mut>new candidate (this repo)</span></td>"
        f"<td><a href='downloads/{esc(Path(h51_row['path']).name)}'>{esc(Path(h51_row['path']).name)}</a><br>"
        f"<span class=mut>sha256 {esc(h51_row['sha256'][:16])}&hellip; &middot; {h51_row['dots_inside_footprint']:,} dots &middot; format {'PASS' if h51_row['format_pass'] else 'FAIL'}</span></td>"
        "<td>none (not submitted)</td>"
        f"<td>{h51_hold['sgmc_cal']['prevalence_calibrated_dti']:.4f} {ci(h51_hold['sgmc_cal']['calibrated_ci95'])}<br><span class=mut>HOLDOUT-DTI SGMC-CAL-v3.0 &middot; below champion {cham['sg']['prevalence_calibrated_dti']:.4f}</span></td>"
        f"<td>{h51_hold['hide_recover_b2']['pooled_dti']:.4f} {ci(h51_hold['hide_recover_b2']['ci95'])}<br><span class=mut>HOLDOUT-DTI HIDE-RECOVER-v3.0 &middot; below champion {cham['hr']['pooled_dti']:.4f}</span></td>"
        f"<td><span class=ok>YES vs nine focus sites</span> (max {h51_ov_focus*100:.1f}%)<br>"
        f"<span class=ok>YES vs all &le;100k-dot registry rasters</span> (max {h51_ov_le100k*100:.1f}%)<br>"
        f"<span class=no>NO vs dense registry rasters</span> (max {h51_ov_all*100:.1f}%; r13 {h51_r13*100:.1f}%)</td>"
        "<td><b style='color:#b00020'>DOWNLOAD FOR REVIEW ONLY &middot; DO NOT SUBMIT</b><br>"
        f"Projection (not a score): {rank['h51_projection']['point']:.3f}, 95% PI {rank['h51_projection']['pi95'][0]:.3f} to {rank['h51_projection']['pi95'][1]:.3f}.</td></tr>")

    tbl = ("<div class=tw><table><thead><tr><th>Site</th><th>File to download</th><th>Published score</th>"
           "<th>Static holdout: SGMC-cal (higher = better)</th><th>Static holdout: HIDE-RECOVER</th>"
           "<th>Unique? (70% &amp; rho&le;0.90)</th><th>Submit?</th></tr></thead><tbody>" + "".join(trs) + "</tbody></table></div>")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nine-site executive summary &middot; GEMSDOE32</title>
<style>
body{{font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f7f8fa;color:#14181f}}
main{{max-width:1180px;margin:0 auto;padding:22px}}
h1{{margin:6px 0 4px;font-size:26px}} h2{{margin:26px 0 8px;font-size:19px;border-bottom:1px solid #d7dbe3;padding-bottom:4px}}
.mut{{color:#5b6472;font-size:12.5px}} .box{{border-radius:10px;padding:14px 16px;margin:12px 0;background:#fff;border:1px solid #d7dbe3}}
.stop{{border-left:6px solid #b00020}} .go{{border-left:6px solid #0a7d2c}} .warn{{border-left:6px solid #b7791f}}
table{{border-collapse:collapse;width:100%;background:#fff;font-size:13.5px}} th,td{{border:1px solid #d7dbe3;padding:7px 8px;vertical-align:top;text-align:left}}
th{{background:#eef1f6}} tr.cand td{{background:#fff7e6}} .tw{{overflow-x:auto}}
.ok{{color:#0a7d2c;font-weight:600}} .no{{color:#b00020;font-weight:600}} a{{color:#1d4ed8}}
code{{background:#eef1f6;padding:1px 4px;border-radius:4px;font-size:12.5px;overflow-wrap:anywhere}}
li{{margin:3px 0}}
</style></head><body><main>
<p class=mut><a href='index.html'>Home</a> &middot; <a href='executive-summary.html'>How to submit</a> &middot; <a href='nine-site-review.html'>Earlier nine-site audit</a></p>
<h1>Nine-site executive summary &mdash; which file, what score, is it unique</h1>
<p class=mut>Generated by <code>scripts/build_nine_site_exec_20261028.py</code> from <code>evidence/focus9_independent_verification_20261028.json</code>, <code>evidence/holdout_static_recheck_20261028.json</code> and <code>evidence/evaluator_rank_check_20261028.json</code>. Snapshot 2026-10-28 (UTC). Branch <code>arena/73853a05-gemsdoe32</code>.</p>

<div class='box stop'><b style='font-size:17px'>Answer: no file is cleared for submission today.</b>
<ul>
<li><b>Highest published score among the nine sites:</b> GEMSDOE32 <code>h33-h33-2-b2</code> = <b>0.2778</b> (OWNER-REPORT). It is already submitted, so re-submitting it adds nothing.</li>
<li><b>Unique new file:</b> <code>H51-1-EWSP</code> is the only file in the family that passes the 70% and rho&le;0.90 uniqueness rules against the nine sites and every &le;100k-dot registry raster. <b>It is not verified better than the champion</b> on the same holdout evaluators, so it is download-for-review only.</li>
<li><b>Blocker for H51 submission:</b> it is {h51_ov_all*100:.1f}% within 3 px of the dense <code>r13-lattice-s5</code> raster (206,895 dots), above the 70% rule. This is an owner decision (see irregularities).</li>
</ul></div>

<h2>Live leaderboard context (fetched 2026-10-28)</h2>
<div class='box warn'>
<ul>
<li>Live #1 is <b>0.4544</b> (xiaofanhu); #2 is 0.3916; <b>0.3195 is rank #26</b> (kpomazi), not the top score.</li>
<li>The prompt's <b>0.4413</b> and <b>0.3195</b> were earlier #1 snapshots (repo registry: 2026-10-25 and 2026-10-03). They are stale, not the current top.</li>
<li>Source: <a href='https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/'>DrivenData leaderboard</a> (public scores; the final ranking uses a private set).</li>
</ul></div>

<h2>Executive table (one row per site, plus the new candidate)</h2>
<p class=mut>Legend: <b>OWNER-REPORT</b> = claimed in the owner's log, no DrivenData receipt. <b>HOLDOUT-DTI</b> = repo evaluator on the file's own bytes, with evaluator version, withheld positives and 95% cluster-bootstrap CI. <b>PROJECTION</b> = fitted estimate, not a score. No ORGANIZER-CONFIRMED score exists in this repo.</p>
{tbl}

<h2>Which evaluator tracks the leaderboard? (n = 9 sites)</h2>
<div class=box>
<ul>
<li>Published score vs <b>SGMC-cal</b> (off-catalogue USGS SGMC faults, prevalence-calibrated): Spearman <b>{rank['spearman_published_vs_sgmc_cal']:+.3f}</b> (p={rank['p_sgmc']:.3g}).</li>
<li>Published score vs <b>HIDE-RECOVER</b> (withheld catalogue segments): Spearman <b>{rank['spearman_published_vs_hide_recover']:+.3f}</b> (p={rank['p_hide_recover']:.3g}). It runs the opposite way.</li>
<li>Reading: SGMC-cal is the evaluator that agrees with the leaderboard ordering. HIDE-RECOVER should not be used to rank files for submission.</li>
<li>Caveat: 9 points; OWNER-REPORT scores; a correlation, not a causal result.</li>
<li>H51 PROJECTION from the SGMC-cal line: <b>{rank['h51_projection']['point']:.3f}</b>, 95% prediction interval {rank['h51_projection']['pi95'][0]:.3f} to {rank['h51_projection']['pi95'][1]:.3f}. This is <b>not a score</b>.</li>
</ul></div>

<h2>What a new file must do to beat 0.2778</h2>
<div class=box>
<ul>
<li>On the SGMC-cal evaluator, the champion scores {cham['sg']['prevalence_calibrated_dti']:.6f}. The highest of the nine is GEMSDOE36 at 0.064444 (published 0.2750).</li>
<li>H51 scores {h51_hold['sgmc_cal']['prevalence_calibrated_dti']:.6f} on the same evaluator, below the champion, with overlapping CIs. Its advantage is uniqueness, not a verified score gain.</li>
<li>Next experiment (not run this session, budget spent): emit a new file that maximises SGMC-cal under the uniqueness constraints, then re-check it on the same static evaluators before any slot is spent.</li>
</ul></div>

<h2>Irregularities for owner review</h2>
<div class='box warn'><ol>
<li><b>H51 headline uses fold-local numbers.</b> The 0.115134 HIDE-RECOVER figure comes from per-fold re-emitted arms, not the downloadable bytes. The static receipt of the bytes gives <b>{h51_hold['hide_recover_b2']['pooled_dti']:.6f}</b> (below the champion's {cham['hr']['pooled_dti']:.6f}). <a href='../evidence/h51_ewsp_static_evaluator_receipt.json'>receipt</a>. Corrected in <code>registry/current_status.json</code>.</li>
<li><b>Dense registry raster.</b> <code>13gems_20261001_r13-lattice-s5_v2</code> (206,895 dots) makes any dense file fail the literal 70% rule (measured: 6,649 footprint cells lie beyond 3 px of r13; a greedy 2.8 px packing gives about 1,969 outside-collar dots, which caps a 70%-compliant file near 6.6k dots at the greedy bound and about 22k at the cell-count bound; see evidence). Decide: an exemption, or a sparse-file rule.</li>
<li><b>Nine-site audit pointers were stale.</b> 7 of the 9 files listed in <code>evidence/nine_site_best_files_audit.json</code> were not at the paths listed. This page resolves each file by SHA-256 from the fetched focus-repo manifest instead.</li>
<li><b>Sample template contradicts the official text.</b> <code>sample_submission.tif</code> has 60,988 cells equal to 1, but the official page describes it as predicting total fault absence. <a href='https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/'>official page</a>.</li>
<li><b>Outside-footprint zeros.</b> The official page says outside-bounds values are null or NaN. The <code>-zeros.tif</code> files use 0 outside. The owner reports that the champion was accepted, but no receipt is in the repo.</li>
<li><b>Data provenance.</b> Competition rasters come from an owner mirror (not organizer-authenticated). The SHA-256 values match the repo's pinned hashes.</li>
<li><b>Prompt numbers stale.</b> See the leaderboard box above.</li>
</ol></div>

<h2>Sources (check manually)</h2>
<ul>
<li><a href='https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/'>Problem statement, metric, submission format</a> (verified 2026-10-28: DTI alpha 0.2, beta 0.8, 300 m triangular kernel, float32 in [0,1], EPSG:32611, 100 m)</li>
<li><a href='https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/'>Leaderboard</a></li>
<li><a href='https://pubs.usgs.gov/ds/1052/'>USGS Data Series 1052 (SGMC source; directory verified, title on ds1052.pdf still to check manually)</a></li>
<li><a href='https://github.com/drivendataorg/gems-prize-reference-solution'>Official reference solution</a></li>
</ul>
</main></body></html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
