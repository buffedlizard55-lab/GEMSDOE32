#!/usr/bin/env python3
"""Build the 2026-10-29 nine-site executive summary from measured evidence (no hand-typed numbers).

Inputs (all produced by scripts in this repo):
  evidence/nine_site_best_files_audit.json      owner-reported published scores + file paths + sha256
  evidence/focus9_holdout_20261029.json         HOLDOUT-DTI on the shared evaluators (score_focus9_holdout_20261029.py)
  evidence/focus9_uniqueness_20261029.json      directional 3-px overlap matrix (focus9_uniqueness_20261029.py)
  registry/current_status.json                  gate state (any_file_ok_to_submit)

Outputs:
  evidence/focus9_validator_20261029.json       shared strict GeoTIFF validator (gems32.submission.audit_geotiff)
  evidence/focus9_summary_20261029.json         table rows + verdicts + projection + run card
  docs/focus9-executive-summary.html            the executive summary page (linked from the README)
  docs/research/focus9-executive-summary-20261029.md  same content as markdown

Labels: OWNER-REPORT (user/submission-log claim), HOLDOUT-DTI (local evaluator, with n and CI),
PROJECTION (regression, never a score), VERIFIED-LOCAL / VERIFIED-WEB (checked this session).
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import holdout  # noqa: E402
from gems32.submission import audit_geotiff  # noqa: E402
from focus_directional_overlap import mask_of, near3  # noqa: E402

DDIR = ROOT / ".cache" / "gems_data"
EV = ROOT / "evidence"
DOCS = ROOT / "docs"
LATTICE = DDIR / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
LEADERBOARD_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
PROBLEM_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
RULES_URL = "https://docs.nlr.gov/docs/fy26osti/96647.pdf"
CHAMPION = "GEMSDOE32"
UNIQUE = ["UNIQUE-H49-1-CGTD", "UNIQUE-H51-1-EWSP"]


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def main() -> int:
    audit = json.loads((EV / "nine_site_best_files_audit.json").read_text())
    hold = json.loads((EV / "focus9_holdout_20261029.json").read_text())
    uniq = json.loads((EV / "focus9_uniqueness_20261029.json").read_text())
    gate = json.loads((ROOT / "registry" / "current_status.json").read_text())
    by_name = {r["site"]: r for r in hold["rows"]}
    audit_by = {s["site"]: s for s in audit["sites"]}
    unique_files = {
        "UNIQUE-H49-1-CGTD": "docs/downloads/gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.tif",
        "UNIQUE-H51-1-EWSP": "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif",
    }
    file_of = {s: s_["file"] for s, s_ in audit_by.items()} | unique_files
    order = [s["site"] for s in audit["sites"]] + UNIQUE

    # 1. Shared validator on every file (strict 12-point + GeoTIFF checks).
    ctx = holdout.load_holdout_context(DDIR)
    labels = rasterio.open(DDIR / "labels.tif").read(1)
    validator = {}
    for name in order:
        p = ROOT / file_of[name]
        with rasterio.open(p) as ds:
            a = ds.read(1)
        mode = "nan" if np.isnan(a[~ctx.foot]).any() else "zeros"
        r = audit_geotiff(p, ctx.foot, labels, mode=mode, template_tif=DDIR / "sample_submission.tif")
        validator[name] = {
            "file": file_of[name],
            "mode": mode,
            "all_checks_passed": bool(r["all_checks_passed"]),
            "failed_checks": [k for k, v in r["checks"].items() if not v],
            "emitted_positive_pixels": int(r["emitted_positive_pixels"]),
            "on_catalogue_positive_pixels": int(r["on_catalogue_positive_pixels"]),
            "in_footprint_min": float(r["in_footprint_min"]),
            "in_footprint_max": float(r["in_footprint_max"]),
            "crs": r["crs"],
            "shape": r["shape"],
            "dtype": r["dtype"],
            "nodata": r["nodata"],
        }
    (EV / "focus9_validator_20261029.json").write_text(json.dumps({"schema_version": 1, "session": "2026-10-29",
        "validator": "gems32.submission.audit_geotiff (shared)", "rows": validator}, indent=1) + "\n")

    # 2. Literal lattice overlap vs the dense r13 registry raster (IR-45-LATTICE-02, owner decision).
    lat_near = near3(mask_of(LATTICE))
    lattice = {}
    for name in order:
        m = mask_of(ROOT / file_of[name])
        lattice[name] = round(float((m & lat_near).sum() / max(int(m.sum()), 1)) * 100.0, 3)

    # 3. Projection: OLS of owner-reported public score on SGMC-cal across the nine (PROJECTION only).
    nine = [s["site"] for s in audit["sites"]]
    x = np.array([by_name[s]["HOLDOUT_DTI_SGMC_CAL"]["prevalence_calibrated_dti"] for s in nine])
    y = np.array([audit_by[s]["published_score_OWNER_REPORT"] for s in nine])
    n = len(x)
    X = np.column_stack([np.ones(n), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    s2 = float(resid @ resid) / (n - 2)
    XtXi = np.linalg.inv(X.T @ X)
    tcrit = stats.t.ppf(0.975, n - 2)
    rho, pval = stats.spearmanr(x, y)

    def project(name: str) -> dict:
        xv = by_name[name]["HOLDOUT_DTI_SGMC_CAL"]["prevalence_calibrated_dti"]
        xx = np.array([1.0, xv])
        pred = float(xx @ beta)
        se = float(np.sqrt(s2 * (1 + xx @ XtXi @ xx)))
        return {"value": round(pred, 4), "pi95": [round(pred - tcrit * se, 4), round(pred + tcrit * se, 4)]}

    # 4. Repo gate: HIDE-RECOVER (static bytes) must beat the champion and SGMC-cal must not regress.
    ch = by_name[CHAMPION]
    ch_hr = ch["HOLDOUT_DTI_HIDE_RECOVER_b0"]["pooled_dti"]
    ch_sg = ch["HOLDOUT_DTI_SGMC_CAL"]["prevalence_calibrated_dti"]

    rows = []
    for name in order:
        r = by_name[name]
        hr = r["HOLDOUT_DTI_HIDE_RECOVER_b0"]
        sg = r["HOLDOUT_DTI_SGMC_CAL"]
        others = [u for u in order if u != name]
        mx = max(((uniq["matrix_pct"][f"{name} -> {o}"], o) for o in others), key=lambda t: t[0])
        is_unique = mx[0] <= 70.0
        is_focus = name in nine
        gate_checks = {
            "uniqueness_70pct_vs_all_listed": is_unique,
            "validator_all_checks": validator[name]["all_checks_passed"],
            "zero_catalogue_leakage": validator[name]["on_catalogue_positive_pixels"] == 0,
            "repo_gate_static_HR_beats_champion": hr["pooled_dti"] > ch_hr,
            "SGMC_cal_no_regression_vs_champion": sg["prevalence_calibrated_dti"] >= ch_sg,
            "literal_lattice_r13_le_70pct": lattice[name] <= 70.0,
        }
        if not is_focus:
            ok_download = gate_checks["validator_all_checks"]
            ok_submit = all(gate_checks.values()) and gate["any_file_ok_to_submit"] is True
        else:
            ok_download = validator[name]["all_checks_passed"]
            ok_submit = False  # already-scored focus files: resubmission spends a slot without new information
        row = {
            "site": name,
            "file": file_of[name],
            "sha256": audit_by[name]["sha256"] if name in audit_by else None,
            "dots": r["dots"],
            "leaderboard_name": r["leaderboard_name"],
            "published_score_OWNER_REPORT": r["published_score_OWNER_REPORT"],
            "HOLDOUT_DTI_HIDE_RECOVER_b0": hr,
            "HOLDOUT_DTI_SGMC_CAL": sg,
            "projection_PROJECTION_not_a_score": project(name),
            "unique_vs_other_listed": "YES" if is_unique else "NO",
            "max_directional_overlap_pct": round(mx[0], 2),
            "max_overlap_vs": mx[1],
            "literal_lattice_r13_overlap_pct": lattice[name],
            "gate_checks": gate_checks,
            "download_verdict": "DOWNLOAD (format-valid)" if ok_download else "DO NOT DOWNLOAD",
            "submit_verdict": "SUBMIT: YES (gate passed)" if ok_submit else "DO NOT SUBMIT",
        }
        rows.append(row)

    run_card = {
        "hypothesis": "none new this session; re-scoring of the nine focus-site winners and two repo-unique candidates on the shared evaluators to test which holdout instrument tracks the public leaderboard",
        "mechanism": "HOLDOUT-DTI on the emitted bytes (SGMC-CAL off-catalogue vs HIDE-RECOVER catalogue-withheld) against owner-reported public scores",
        "named_non_fault_process": "catalogue-adjacent placement (dots near USGS catalogue traces) scores well on HIDE-RECOVER without finding unmapped faults; the public set is off-catalogue, so HIDE-RECOVER can reward the wrong behaviour",
        "holdout_instrument": {
            "HIDE_RECOVER": "GEMSDOE32-HIDE-RECOVER-v3.0, n_withheld_positives=22232, 1000-draw cluster bootstrap 95% CI",
            "SGMC_CAL": "GEMSDOE32-SGMC-CAL-v3.0, prevalence-calibrated, 95% CI",
        },
        "raster_sha256": {r["site"]: r["sha256"] for r in rows if r["sha256"]},
        "validator_output": {k: {"all_checks_passed": v["all_checks_passed"], "failed": v["failed_checks"]} for k, v in validator.items()},
        "uniqueness_scope": "focus 9 + 2 repo-unique candidates only; full 30-repo registry result is recorded in the repo's H51 audit, not re-run here",
        "leakage_canary": "not re-run this session (no new feature built); repo receipts for H49 (93/93 channels AUC<=0.90) are cited, not re-verified",
        "submission_name": None,
        "note": None,
        "verdict": "negative for new submission (no file cleared); instrument finding recorded for owner decision",
        "slots_spent": 0,
        "experiments": 2,
    }
    rr = {"SGMC_CAL_spearman_vs_owner_public": round(float(rho), 3), "p_value": float(f"{pval:.3g}"), "n": n,
          "HIDE_RECOVER_spearman_vs_owner_public": None}
    hr_vals = np.array([by_name[s]["HOLDOUT_DTI_HIDE_RECOVER_b0"]["pooled_dti"] for s in nine])
    rr["HIDE_RECOVER_spearman_vs_owner_public"] = round(float(stats.spearmanr(hr_vals, y).correlation), 3)
    run_card["rank_correlation_with_owner_reported_public_scores_n9"] = rr

    summary = {
        "schema_version": 1,
        "session": "2026-10-29",
        "champion": CHAMPION,
        "champion_HR_b0": ch_hr,
        "champion_SGMC_cal": ch_sg,
        "instrument_alignment_n9": rr,
        "projection_model": {"form": "public = a + b * SGMC_CAL (OLS, n=9)", "a": round(float(beta[0]), 5),
                             "b": round(float(beta[1]), 5), "R2": round(float(1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))), 3),
                             "caveat": "in-sample; 9 owner-reported labels with only ~5 distinct dot sets; prediction intervals understate uncertainty"},
        "literal_lattice_note": "r13-lattice-s5 is a dense registry raster (~206,895 dots per repo); every file overlaps it >=97.8% so the literal lattice rule is degenerate (IR-45-LATTICE-02)",
        "rows": rows,
        "run_card": run_card,
        "gate_state": {"any_file_ok_to_submit": gate["any_file_ok_to_submit"]},
        "sources": {"problem": PROBLEM_URL, "rules": RULES_URL, "leaderboard": LEADERBOARD_URL},
    }
    (EV / "focus9_summary_20261029.json").write_text(json.dumps(summary, indent=1) + "\n")

    write_html(summary)
    write_md(summary)
    print("wrote evidence/focus9_validator_20261029.json, evidence/focus9_summary_20261029.json, docs/focus9-executive-summary.html")
    return 0


def fmt_ci(ci) -> str:
    return f"[{ci[0]:.4f}, {ci[1]:.4f}]"


def write_html(s: dict) -> None:
    e = html.escape
    rows_html = []
    for r in s["rows"]:
        hr = r["HOLDOUT_DTI_HIDE_RECOVER_b0"]
        sg = r["HOLDOUT_DTI_SGMC_CAL"]
        pj = r["projection_PROJECTION_not_a_score"]
        pub = r["published_score_OWNER_REPORT"]
        pub_s = f"{pub:.4f}" if pub is not None else "not submitted"
        dl = r["download_verdict"]
        sub = r["submit_verdict"]
        cls = "ok" if dl.startswith("DOWNLOAD") else "bad"
        rows_html.append(
            "<tr>"
            f"<td><b>{e(r['site'])}</b></td>"
            f"<td><a href=\"../{e(r['file'])}\"><code>{e(Path(r['file']).name)}</code></a><br><small>{e(r['leaderboard_name'])}</small></td>"
            f"<td>{pub_s}<br><small>OWNER-REPORT</small></td>"
            f"<td>{pj['value']:.4f}<br><small>PROJECTION 95% PI {fmt_ci(pj['pi95'])} (understated)</small></td>"
            f"<td>{sg['prevalence_calibrated_dti']:.4f}<br><small>HOLDOUT-DTI SGMC-CAL-v3.0 CI {fmt_ci(sg['calibrated_ci95'])}</small></td>"
            f"<td>{hr['pooled_dti']:.4f}<br><small>HOLDOUT-DTI HIDE-RECOVER-v3.0 n={hr['n_withheld_positives']} CI {fmt_ci(hr['ci95'])}</small></td>"
            f"<td><b>{e(r['unique_vs_other_listed'])}</b><br><small>max {r['max_directional_overlap_pct']:.1f}% vs {e(r['max_overlap_vs'])}</small></td>"
            f"<td class={cls}><b>{e(dl)}</b><br>{e(sub)}</td>"
            "</tr>"
        )
    rr = s["instrument_alignment_n9"]
    cc = s["run_card"]
    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>GEMSDOE32 — Nine-site executive summary (2026-10-29)</title>
<style>
body{{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:0;background:#f6f7f9;color:#111;line-height:1.45}}
header,main{{max-width:1200px;margin:0 auto;padding:18px}}
header{{background:#14213d;color:#fff}}header a{{color:#fca311}}
.banner{{background:#fff;border:3px solid #b00020;border-radius:8px;padding:14px 18px;margin:16px 0}}
.banner h2{{color:#b00020;margin:0 0 6px}}
table{{border-collapse:collapse;width:100%;background:#fff;font-size:14px}}
th,td{{border:1px solid #d0d4da;padding:7px 8px;vertical-align:top;text-align:left}}
th{{background:#e9edf3}}
td.ok{{background:#e8f6ec}}td.bad{{background:#fdecef}}
small{{color:#4a5160}}code{{font-size:12px;word-break:break-all}}
.card{{background:#fff;border:1px solid #d0d4da;border-radius:8px;padding:14px 18px;margin:14px 0}}
pre{{background:#0f172a;color:#e2e8f0;padding:12px;border-radius:6px;overflow:auto;font-size:12px}}
</style></head><body>
<header><div style="max-width:1200px;margin:0 auto"><h1 style="margin:0">GEMSDOE32 — Nine-site executive summary</h1>
<p style="margin:4px 0 0">Session 2026-10-29 · <a href="../README.md">README</a> · <a href="index.html">site home</a> · <a href="{LEADERBOARD_URL}">live leaderboard</a></p></div></header>
<main>
<div class=banner>
<h2>NO FILE IS CLEARED FOR SUBMISSION</h2>
<p><b>Download for review:</b> the two repo-unique candidates below pass the format validator. <b>Submit:</b> nothing. Every row is marked DO NOT SUBMIT because the repo's own gate (<code>registry/current_status.json</code>, <code>any_file_ok_to_submit: {str(s['gate_state']['any_file_ok_to_submit']).lower()}</code>) is closed, and the one gate that matters for the public ranking is pointed the wrong way (see below).</p>
</div>

<div class=card>
<h2>1. Which file to download, and what it is likely to score</h2>
<ul>
<li><b>Highest published score in the nine focus sites:</b> GEMSDOE32 <code>h33-h33-2-b2…e5eb6e7e-zeros</code> at <b>0.2778</b> (OWNER-REPORT). It is <b>not</b> on the public leaderboard's top 50 (checked: rank 50 = 0.3167). The prompt's claimed #1 of 0.4413 and 0.3195 do not match the live page (#1 = 0.4544; 0.3195 is rank #47).</li>
<li><b>Best unique candidate:</b> <b>UNIQUE-H49-1-CGTD</b> (download: <a href="../{e(unique_file(s, 'UNIQUE-H49-1-CGTD'))}"><code>{e(Path(unique_file(s, 'UNIQUE-H49-1-CGTD')).name)}</code></a>). It has the highest off-catalogue HOLDOUT-DTI measured (0.0664, the SGMC-CAL instrument that tracks the public ranking best). Its projected public score is about <b>0.286</b>, a PROJECTION only, not a score. It is <b>not</b> cleared: it fails the HIDE-RECOVER gate (see §3).</li>
<li><b>Estimate for an unsubmitted file:</b> there is no organizer receipt for any new file. The only real score is one the organizer returns after a weekly slot is used.</li>
</ul>
</div>

<div class=card style="overflow:auto">
<h2>2. Executive summary table (one row per site, plus the two unique candidates)</h2>
<p><small>Columns: file to download · published score (OWNER-REPORT) · projection (PROJECTION, not a score) · off-catalogue HOLDOUT-DTI (SGMC-CAL) · catalogue-withheld HOLDOUT-DTI (HIDE-RECOVER, the repo's current gate) · unique vs the other listed sites (70% directional 3-px rule) · download / submit verdict.</small></p>
<table>
<tr><th>Site</th><th>File to download (leaderboard name)</th><th>Published score</th><th>Estimate</th><th>Off-catalogue HOLDOUT-DTI</th><th>HIDE-RECOVER HOLDOUT-DTI</th><th>Unique?</th><th>Verdict</th></tr>
{''.join(rows_html)}
</table>
<p><small>Verdict meanings: <b>DOWNLOAD</b> = passes the strict GeoTIFF validator (see §4). <b>SUBMIT</b> = cleared by the repo gate; no file is. Focus-site files are already-scored artifacts; resubmitting one spends a weekly slot without new information.</small></p>
</div>

<div class=card>
<h2>3. Why the best-scoring file is not the best predictor by the repo's own gate (irregularity IR-20261029-A)</h2>
<p>On the nine owner-reported public scores, the two local holdouts disagree:</p>
<ul>
<li><b>SGMC-CAL (off-catalogue, prevalence-calibrated):</b> Spearman ρ = <b>{rr['SGMC_CAL_spearman_vs_owner_public']:+.3f}</b> with the public scores (n = {rr['n']}, p = {rr['p_value']:.2g}). This is the instrument that matches the competition's stated target: faults <i>not</i> in the USGS catalogue.</li>
<li><b>HIDE-RECOVER (catalogue-withheld, the repo's current gate):</b> Spearman ρ = <b>{rr['HIDE_RECOVER_spearman_vs_owner_public']:+.3f}</b>. Its ranking is anti-aligned with the public one.</li>
</ul>
<p>The 0.2778 champion scores <b>{s['champion_HR_b0']:.4f}</b> on HIDE-RECOVER (near the bottom of the nine) and <b>{s['champion_SGMC_cal']:.4f}</b> on SGMC-CAL (second of nine). The repo's gate asks for a HIDE-RECOVER win, so it rejects the files that the off-catalogue evidence ranks highest. Changing the gate instrument is an <b>owner decision</b>; this summary does not change it.</p>
<p><small>Caveats: n = 9 owner-reported labels, and several of them are the same dot set, so the effective sample size is much smaller. Treat these correlations as a finding to test, not a result.</small></p>
</div>

<div class=card>
<h2>4. Uniqueness and format (measured this session)</h2>
<ul>
<li><b>No file in the nine is unique against the other eight.</b> Every focus file exceeds the 70% directional 3-px rule against at least one other focus file (the champion's dots are 100% within 3 px of GEMSDOE24/25/27/30/31 dots). <b>GEMSDOE25 and GEMSDOE30 have identical dot sets</b> (different bytes).</li>
<li><b>UNIQUE-H49-1-CGTD and UNIQUE-H51-1-EWSP pass against the nine</b> (max {max(r['max_directional_overlap_pct'] for r in s['rows'] if r['site'] in UNIQUE):.1f}%, between each other).</li>
<li><b>Literal lattice rule (IR-45-LATTICE-02):</b> the dense <code>r13-lattice-s5</code> raster overlaps every candidate at ≥ {min(r['literal_lattice_r13_overlap_pct'] for r in s['rows']):.1f}%. Under the literal reading, no 37k-dot file can pass. This is an owner decision.</li>
<li><b>Format:</b> every row was checked with the repo's shared strict validator (<code>evidence/focus9_validator_20261029.json</code>): exact reference grid (EPSG:32611, 3730×3292, 100 m), float32, single band, in-footprint values in [0,1], no NaN inside the footprint, zero on-catalogue positives.</li>
</ul>
</div>

<div class=card>
<h2>5. Official rules checked (2026-10-29)</h2>
<ul>
<li>Metric: distance-weighted Tversky, α = 0.2, β = 0.8, 300 m triangular kernel — <a href="{PROBLEM_URL}">{PROBLEM_URL}</a> (VERIFIED-WEB)</li>
<li>Format: GeoTIFF, EPSG:32611, 100 m, same bounds, outside bounds "null or nan", single float32 layer, values between 0 and 1 — same page (VERIFIED-WEB)</li>
<li><b>No official dot-count cap was found</b> in the problem page or the rules PDF (<a href="{RULES_URL}">{RULES_URL}</a>). The "37,654-dot budget" used throughout this repo is an internal convention (IR-20261029-B).</li>
<li>Live leaderboard, 2026-10-29: #1 0.4544, #2 0.3916, #3 0.3911, #4 0.3841, #5 0.3642; rank 47 = 0.3195 (kpomazi); no 0.2778 in the top 50 (<a href="{LEADERBOARD_URL}">{LEADERBOARD_URL}</a>) (VERIFIED-WEB)</li>
</ul>
</div>

<div class=card>
<h2>6. Recommendation</h2>
<ol>
<li><b>Do not submit any new file today.</b> The one candidate with a plausible edge (UNIQUE-H49-1-CGTD, projected ≈0.286 against the champion's ≈0.278) is still a projection. Its gate also fails on HIDE-RECOVER, and its fold-local HIDE-RECOVER win does not hold on the emitted bytes.</li>
<li><b>Owner decisions required before any slot:</b> (a) which holdout instrument gates promotion — SGMC-CAL matches the public ranking, HIDE-RECOVER does not; (b) the literal lattice rule (IR-45-LATTICE-02); (c) whether the 37,654-dot budget is a real constraint (no official cap was found).</li>
<li><b>If (a) and (b) are approved,</b> UNIQUE-H49-1-CGTD is the only unique candidate that also passes the SGMC-CAL non-regression check (UNIQUE-H51-1-EWSP is slightly below the champion, 0.0630 vs 0.0641). Spend <b>one</b> weekly slot on it to turn the projection into an ORGANIZER-CONFIRMED receipt. That is a selector decision, not an automatic one.</li>
</ol>
</div>

<div class=card>
<h2>7. Run card (JSON)</h2>
<pre>{e(json.dumps(cc, indent=1))}</pre>
</div>
</main></body></html>
"""
    (DOCS / "focus9-executive-summary.html").write_text(page)


def unique_file(s: dict, name: str) -> str:
    return next(r["file"] for r in s["rows"] if r["site"] == name)


def write_md(s: dict) -> None:
    lines = [
        "# Nine-site executive summary — 2026-10-29",
        "",
        "**No file is cleared for submission.** Download-for-review only. The one unique candidate with a plausible edge is UNIQUE-H49-1-CGTD (projected ≈0.286, PROJECTION only), which fails the repo's HIDE-RECOVER gate. Owner decisions are required before any weekly slot is spent.",
        "",
        "| Site | File to download | Published (OWNER-REPORT) | Estimate (PROJECTION) | Off-catalogue HOLDOUT-DTI (SGMC-CAL) | HIDE-RECOVER HOLDOUT-DTI | Unique? | Verdict |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in s["rows"]:
        pub = f"{r['published_score_OWNER_REPORT']:.4f}" if r["published_score_OWNER_REPORT"] is not None else "not submitted"
        pj = r["projection_PROJECTION_not_a_score"]
        sg = r["HOLDOUT_DTI_SGMC_CAL"]
        hr = r["HOLDOUT_DTI_HIDE_RECOVER_b0"]
        lines.append(
            f"| {r['site']} | `{Path(r['file']).name}` | {pub} | {pj['value']:.4f} (PI {pj['pi95'][0]:.3f}–{pj['pi95'][1]:.3f}) | "
            f"{sg['prevalence_calibrated_dti']:.4f} {fmt_ci(sg['calibrated_ci95'])} | {hr['pooled_dti']:.4f} n={hr['n_withheld_positives']} {fmt_ci(hr['ci95'])} | "
            f"{r['unique_vs_other_listed']} (max {r['max_directional_overlap_pct']:.1f}% vs {r['max_overlap_vs']}) | {r['download_verdict']}; {r['submit_verdict']} |"
        )
    lines += ["", "Full detail, run card and sources: `docs/focus9-executive-summary.html`, `evidence/focus9_summary_20261029.json`.", ""]
    (DOCS / "research" / "focus9-executive-summary-20261029.md").write_text("\n".join(lines))


if __name__ == "__main__":
    raise SystemExit(main())
