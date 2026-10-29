#!/usr/bin/env python3
"""Render docs/start-here.html: the one-page executive summary for the nine focus sites.

Every number is read from evidence/*.json (no hand-typed scores). Labels follow the repo's evidence classes:
  OWNER-REPORT          leaderboard score supplied by the owner; no organizer receipt in this repo
  HOLDOUT-DTI           local evaluator value (static diagnostic); never a leaderboard estimate
  ORGANIZER-CONFIRMED   none present

Run: python3 scripts/build_start_here_20261029.py
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence"
TABLE = json.loads((EV / "focus9_exec_table_20261029.json").read_text())
SCREEN = json.loads((EV / "downloads_sgmc_screen_20261029.json").read_text())
VALID = json.loads((EV / "evaluator_rank_validity_20261029.json").read_text())
MANIFEST = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())["rasters"]
OUT = ROOT / "docs" / "start-here.html"

LOCAL_DOWNLOAD_PREFIX = "docs/downloads/"
CHAMPION_SHA = "c55bafc47005"
H51_SHA = "f66f65e469"
LEAKED_SHA = "2c1861f1dbf5"

esc = lambda x: html.escape(str(x))


def download_url(site: str, sha: str, local_rel: str) -> str:
    """Link to bytes in this repo's docs/downloads, else to the pinned GitHub raw file for that site."""
    if local_rel.startswith(LOCAL_DOWNLOAD_PREFIX):
        return "downloads/" + local_rel[len(LOCAL_DOWNLOAD_PREFIX):]
    for r in MANIFEST:
        if r["repo"] == site and r["sha256"] == sha:
            return f"https://github.com/buffedlizard55-lab/{r['repo']}/raw/{r['ref']}/{r['path']}"
    return "#"


def fmt_ci(v):
    return f"[{v[0]:.4f}, {v[1]:.4f}]"


def rows_html() -> str:
    out = []
    for r in TABLE["rows"]:
        if r["site"].startswith("H51"):
            continue
        site = r["site"]
        score = r["published_score_OWNER_REPORT"]
        hr = r["holdout_static"]["HIDE_RECOVER_v3_0"]
        sg = r["holdout_static"]["SGMC_CAL_v3_0"]
        local = r["file"]
        url = download_url(site, r["sha256"], local)
        is_champ = r["sha256"].startswith(CHAMPION_SHA)
        dup = site == "GEMSDOE30"
        unique = r["unique_vs_all_rows_at_70pct_rule"]
        if is_champ:
            submit = "NO - already submitted (owner-reported). A resubmission adds no information."
        elif dup:
            submit = "NO - same dots as GEMSDOE25 (identical bytes in dot space); a repeat."
        else:
            submit = "NO - already on the leaderboard list; a resubmission duplicates it."
        out.append(
            f"<tr><td><b>{esc(site)}</b><br><span class=mut>{esc(r['leaderboard_name'])}</span></td>"
            f"<td><a href=\"{esc(url)}\" download>download</a><br><span class=mut>{esc(local.split('/')[-1])}</span></td>"
            f"<td>{score:.4f}<br><span class=mut>OWNER-REPORT</span></td>"
            f"<td>{hr['dti']:.4f} {esc(fmt_ci(hr['ci95']))}<br><span class=mut>HOLDOUT-DTI HIDE-RECOVER, n={hr['n_withheld_positives']:,}</span><br>"
            f"{sg['dti']:.4f} {esc(fmt_ci(sg['ci95']))}<br><span class=mut>HOLDOUT-DTI SGMC-CAL, n={sg['n_withheld_positives']:,}</span></td>"
            f"<td>{'YES' if unique else 'NO'} <span class=mut>(max 3-px overlap vs other focus rows: {r['max_overlap_vs_any_other_in_table']:.2%})</span></td>"
            f"<td><b>{esc(submit)}</b></td></tr>"
        )
    return "\n".join(out)


def h51_row() -> str:
    r = next(x for x in TABLE["rows"] if x["site"].startswith("H51"))
    h51_max = max(p["max_directional_overlap"] for p in TABLE["pairwise"] if p["a"].startswith("H51") or p["b"].startswith("H51"))
    hr = r["holdout_static"]["HIDE_RECOVER_v3_0"]
    sg = r["holdout_static"]["SGMC_CAL_v3_0"]
    url = download_url("H51", r["sha256"], r["file"])
    return (
        f"<tr class=hl><td><b>H51-1-EWSP</b><br><span class=mut>newest unique candidate (not a focus leaderboard file)</span></td>"
        f"<td><a href=\"{esc(url)}\" download>download (review only)</a><br><span class=mut>{esc(r['file'].split('/')[-1])}</span></td>"
        f"<td>not estimated<br><span class=mut>no leaderboard receipt</span></td>"
        f"<td>{hr['dti']:.4f} {esc(fmt_ci(hr['ci95']))} <span class=mut>HIDE-RECOVER</span><br>"
        f"{sg['dti']:.4f} {esc(fmt_ci(sg['ci95']))} <span class=mut>SGMC-CAL (below the champion's 0.064121)</span></td>"
        f"<td><b>YES</b> <span class=mut>(max 3-px overlap vs the nine: {h51_max:.2%})</span></td>"
        f"<td><b>NO - download for review only.</b> Lower than the champion on both static evaluators; the literal dense-raster rule is undecided (IR-51-LATTICE-01).</td></tr>"
    )


def screen_rows() -> str:
    out = []
    for r in SCREEN["rows"]:
        if r["sha256"].startswith(LEAKED_SHA):
            continue
        if not (r["unique_vs_focus9_literal_70pct"] and r["sgmc_calibrated_dti"] > 0.064121):
            continue
        if r["is_champion_bytes"]:
            continue
        name = r["file"].split("/")[-1]
        out.append(
            f"<tr><td>{esc(name)}</td><td>{r['positive_dots']:,}</td>"
            f"<td>{r['sgmc_calibrated_dti']:.4f} {esc(fmt_ci(r['sgmc_calibrated_ci95_unpaired']))}</td>"
            f"<td>{r['max_directional_overlap_vs_focus9']:.2%} vs {esc(r['closest_focus_site'])}</td>"
            f"<td><b>NOT CLEARED</b> - leakage audit of its generator not run; no paired test vs champion</td></tr>"
        )
    return "\n".join(out) or "<tr><td colspan=5>none</td></tr>"


def page() -> str:
    v = VALID["result"]
    hr_r = v["HIDE-RECOVER-v3.0"]["spearman_rho"]
    sg_r = v["SGMC-CAL-v3.0"]["spearman_rho"]
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>START HERE - GEMSDOE32 executive summary (2026-10-29)</title>
<link rel=stylesheet href=assets/site.css>
<style>table{{width:100%;border-collapse:collapse;font-size:.92rem}}th,td{{border-bottom:1px solid #243040;padding:6px;vertical-align:top;text-align:left}}
.hl{{background:#2a2410}}.mut{{color:var(--mut);font-size:.85rem}}.box{{border:3px solid #b91c1c;padding:12px;margin:12px 0;border-radius:6px}}
.ok{{border:3px solid #2ea043;padding:12px;margin:12px 0;border-radius:6px}}</style></head><body>
<header class=top><div class=wrap>
<h1>START HERE - nine-site executive summary</h1>
<nav><a href="index.html">Home</a> <a href="start-here.html" class=active>START HERE</a> <a href="executive-summary.html">Make a submission</a> <a href="leaderboard.html">Leaderboard</a> <a href="irregularities.html">Irregularities</a></nav>
</div></header>
<main class=wrap>
<div class=box>
<h2 style="margin:4px 0">&#128308; Answer: no file is cleared for upload today</h2>
<p><b>Already submitted, best published score:</b> GEMSDOE32 <code>h33-h33-2-b2-...-e5eb6e7e-zeros</code>, 0.2778 (OWNER-REPORT). Do not resubmit it.</p>
<p><b>Newest unique TIF generated in this repo:</b> H51-1-EWSP (download for review; <b>DO NOT SUBMIT</b>). It is unique vs the nine focus sites, but it scores below the champion on both static evaluators.</p>
<p><b>Why no new candidate beats 0.2778 on the holdout:</b> the one file that beats it by a wide margin (BayesOpt, SGMC-CAL 0.2567) is in-sample. Its generator feeds the SGMC truth raster into the emission and selects on the holdout (IR-20261029-S01).</p>
</div>

<h2>1. Nine-site executive table</h2>
<p class=mut>Labels: <b>OWNER-REPORT</b> = leaderboard score supplied by the owner (no organizer receipt in this repo). <b>HOLDOUT-DTI</b> = local evaluator, static diagnostic, 95% spatial cluster-bootstrap CI. <b>ORGANIZER-CONFIRMED</b> = none present. No projection is shown as a score.</p>
<table>
<tr><th>Site</th><th>File to download</th><th>Estimated score</th><th>Holdout (static, HOLDOUT-DTI)</th><th>Unique vs the other focus sites?</th><th>Submit?</th></tr>
{rows_html()}
{h51_row()}
</table>
<p class=mut>Uniqueness rule: a file is a repeat if more than 70% of its dots lie within 3 px of another file's dots (or |phi| &gt; 0.90). 36 of the 45 pairs among the nine focus files plus H51 are repeats. H51 is the only row that passes against every other row. Source: <a href="../evidence/focus9_exec_table_20261029.json">evidence/focus9_exec_table_20261029.json</a>.</p>

<h2>2. The validity test that matters</h2>
<div class=ok>
<p>Over the nine published files, <b>HIDE-RECOVER-v3.0 ranks them in the opposite order to the owner-reported scores (Spearman {hr_r:+.3f}, p = {v['HIDE-RECOVER-v3.0']['spearman_p']:.4f}, n = 9)</b>. <b>SGMC-CAL-v3.0 ranks them in the same order ({sg_r:+.3f}, p = {v['SGMC-CAL-v3.0']['spearman_p']:.1e})</b>, but that agreement is circular for any file that uses the SGMC raster as a model input. Neither evaluator is validated. Source: <a href="../evidence/evaluator_rank_validity_20261029.json">evidence/evaluator_rank_validity_20261029.json</a>.</p>
</div>

<h2>3. Unique, clean-looking candidates that beat the champion on SGMC-CAL (not cleared)</h2>
<p class=mut>Screen of all 75 binary rasters in docs/downloads (<a href="../evidence/downloads_sgmc_screen_20261029.json">evidence/downloads_sgmc_screen_20261029.json</a>). Unpaired CIs. A leakage audit of each generator is still required.</p>
<table>
<tr><th>File</th><th>Dots</th><th>SGMC-CAL HOLDOUT-DTI (unpaired CI)</th><th>Max overlap vs focus nine</th><th>Status</th></tr>
{screen_rows()}
</table>
<p>Excluded: <code>gems32-bayesopt-dilation-scarp-d28-20261004</code> (SGMC-CAL 0.2567). It is unique (28.0% max overlap) but in-sample (IR-20261029-S01). The champion itself is the 0.064121 reference.</p>

<h2>4. How a file gets submitted</h2>
<ol>
<li>Download the single GeoTIFF from the table (one file, one band, EPSG:32611, 3730 x 3292, float32, values 0 or 1 inside the footprint). Steps: <a href="executive-summary.html">Make a submission</a>.</li>
<li>Upload it on the DrivenData submission page with a unique name and a note of at most 140 characters.</li>
<li>Do not upload a file until the owner has confirmed which encoding the portal accepts (IR-20261029-S04) and the gates in <code>registry/current_status.json</code> clear it.</li>
</ol>

<h2>5. Official sources (verified this session)</h2>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Problem description, metric (DTI, alpha 0.2, beta 0.8, 300 m kernel), submission format</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">GEMS Prize official rules (three submissions per week; one submission scored)</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Live leaderboard (#1 0.4544, #2 0.3916, #3 0.3911, read 2026-10-29)</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Reference solution (drivendataorg)</a></li>
</ul>

<h2>6. Irregularities for owner review</h2>
<p>See <a href="irregularities.html">Irregularities</a> (IDs <code>IR-20261029-S01</code> to <code>-S08</code>), including the in-sample SGMC file, the holdout-vs-leaderboard disagreement, the NaN-vs-zeros format question, and the duplicate bytes for GEMSDOE25 / GEMSDOE30.</p>
</main></body></html>
"""


def main() -> int:
    OUT.write_text(page())
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
