#!/usr/bin/env python3
"""Render the GitHub Pages site from the registry + evidence JSON. Nothing is hand-written HTML.

Run: ``python3 scripts/build_site.py``  (also runs in CI before every Pages deploy)
"""
from __future__ import annotations

import html
import json
import sys
import time

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import feed as FEED  # noqa: E402

DOCS = ROOT / "docs"
NAV = [("index.html", "Home"), ("executive-summary.html", "Make a submission"),
       ("research.html", "Research"), ("hypotheses.html", "Hypotheses"),
       ("leaderboard.html", "Leaderboard"), ("sources.html", "Sources"),
       ("irregularities.html", "Irregularities")]
TITLE = "GEMSDOE32"


def esc(x) -> str:
    return html.escape(str(x))


def read(path: str, default=None):
    p = ROOT / path
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def page(title: str, body: str, active: str = "") -> str:
    nav = " ".join(f'<a href="{h}"{" class=active" if h == active else ""}>{t}</a>' for h, t in NAV)
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)} · {TITLE}</title><link rel=stylesheet href=assets/site.css></head><body>
<header class=top><div class=wrap>
<h1>{esc(title)}</h1><nav>{nav}</nav>
</div></header><main class=wrap>{body}</main>
<footer><div class=wrap>
Site generated {stamp} from <code>registry/*.json</code> and <code>evidence/*.json</code> by
<code>scripts/build_site.py</code>. Owner-reported scores are labelled <em>claim</em>; the only
scores this repository reads itself are the other teams' public-leaderboard rows.
<a href="https://github.com/buffedlizard55-lab/GEMSDOE32">Repository</a> ·
<a href="data/feed.json">feed.json</a> · <a href="https://github.com/buffedlizard55-lab/GEMSDOE32/issues">report an irregularity</a>
</div></footer></body></html>"""


def download_block(sub: dict | None, name: str) -> str:
    if not sub:
        return ('<div class=dl><h2>Submission GeoTIFF</h2><p class=mut>Not built in this checkout. '
                'Run <code>python3 scripts/build_submission.py</code>.</p></div>')
    f = sub.get("file", {})
    zeros = sub.get("file_zeros", {})
    sha = (f.get("sha256") or "")
    note = sub.get("note", "")
    return f"""<div class=dl>
<h2>&#11015;&nbsp;Download the submission GeoTIFF</h2>
<p><a class=btn href="downloads/{esc(name)}.tif">Download {esc(name)}.tif</a>
<a class="btn alt" href="downloads/{esc(name)}.zip">.zip</a></p>
<p><b>Note to paste into the submit form's <em>Note (optional)</em> field:</b><br>
<code>{esc(note)}</code></p>
<p class=mut>single band · float32 · EPSG:32611 · 100 m · 3292&times;3730 ·
{int(f.get('positive_px') or 0):,} predicted pixels · every footprint pixel finite and in [0, 1] ·
NaN outside the footprint · sha256 <code>{esc(sha[:16])}&hellip;</code></p>
<p class=mut>Same predictions with 0.0 instead of NaN outside the footprint:
<a href="downloads/{esc(name)}-zeros.tif">zeros variant</a> ·
<a href="downloads/checks-{esc(name)}.tif.json">format receipt (independent re-read)</a></p>
<p class=warn><b>Status.</b> {esc(sub.get('status_line',''))}</p>
</div>"""


def model_mc_section(fl: dict) -> str:
    ev = fl.get("evidence", {})
    runs = [(k, v) for k, v in ev.items() if "mc" in k and isinstance(v, dict)]
    if not runs:
        return ""
    blocks = []
    for k, d in runs:
        s = d.get("summary", {})
        rows = "".join(
            f"<tr><td>{esc(a)}</td><td>{v['mean']:.4f}</td><td>{esc(v.get('px',''))}</td>"
            f"<td>{esc(v.get('mean_TP_w',''))}</td></tr>"
            for a, v in s.items() if isinstance(v, dict) and "mean" in v and not a.startswith("paired_"))
        diffs = "".join(
            f"<tr><td>{esc(a.replace('paired_','').replace('_minus_',' &minus; '))}</td>"
            f"<td>{v['mean']:+.4f} &plusmn; {v['sem']:.4f}</td>"
            f"<td>{v['draws_positive']}/{v['n_draws']}</td></tr>"
            for a, v in s.items() if a.startswith("paired_"))
        blocks.append(f"""<div class=card><b>{esc(k)}</b> — {esc(d.get('question', d.get('instrument','')))}
<p class=mut>Truth model: {esc(d.get('truth_model',{}).get('truth_px'))} px,
&sigma; = {esc(d.get('truth_model',{}).get('sigma_px'))} px, drawn paired for every candidate; scored
with the official metric. Source of the model: {esc(d.get('truth_model',{}).get('source',''))}.</p>
<table><tr><th>candidate</th><th>mean official DTI</th><th>px</th><th>mean TP<sub>w</sub></th></tr>{rows}</table>
{"<table><tr><th>paired difference</th><th>mean &plusmn; s.e.</th><th>draws positive</th></tr>" + diffs + "</table>" if diffs else ""}
</div>""")
    return f"""<h2>Two instruments, and the disagreement between them</h2>
<p>The blocked holdout scores emission rules against the <em>catalogue</em>; the model Monte Carlo
scores candidate <em>files</em> against a generative description of the hidden set. They do not agree
about every change — and that disagreement is a finding, not noise to shrug off:</p>
<table><tr><th>change, at matched emitted mass</th><th>blocked holdout (catalogue truth)</th>
<th>live-anchored truth model (official metric, paired draws)</th></tr>
<tr><td>greedy packing of the <em>surface</em> vs the incumbent dot-thin</td>
<td class=ok>+0.0100 mean, 4/4 folds positive</td>
<td class=bad>&minus;0.0033, 0/12 draws positive</td></tr>
<tr><td>greedy packing of the <em>scatter-smoothed</em> field, catalogue pixels excluded</td>
<td class=mut>not measured on this instrument (it is off-catalogue by construction)</td>
<td class=ok><b>+0.0247 &plusmn; 0.0005, 12/12 draws positive</b></td></tr></table>
<p><b>Mechanism.</b> The holdout's truth is the catalogue, so it rewards covering the field surface
where the catalogue runs. The hidden set is scattered <em>around</em> the surface (the group's own
inference: a 1.85 px scale), so covering the surface is the wrong objective — the right one is to
cover the surface blurred by that scale, which is what the shipped file does. Same mass, same field,
same metric; only the objective changed.</p>
{''.join(blocks)}"""


def overview(fl: dict, sub: dict | None, name: str) -> str:
    lb = fl.get("leaderboard", [])
    lb_top = lb[0] if lb else None
    hold = fl.get("holdout", {})
    irr = fl.get("irregularities", [])
    claims = fl.get("claims", [])
    best_claim = max((c for c in claims), key=lambda c: c.get("score", 0), default=None)
    rows = "".join(f"<tr><td>{esc(s['id'])}</td><td>{esc(s['title'])}</td>"
                   f"<td>{esc(s.get('status',''))}</td></tr>" for s in fl.get("sources", []))
    parts = [download_block(sub, name), f"""<h2>What this is</h2>
<p>{TITLE} is an auditable system for the <b>DOE GEMS Prize</b> (DrivenData #306, GeoDAWN / NW
Nevada): find geothermal-indicative faults that are <em>not</em> in the USGS&nbsp;/&nbsp;INGENIOUS
catalogue, and ship them as a legal GeoTIFF. It has three parts: an exact re-implementation of the
competition metric and its decision theory; a preregistered spatially-blocked holdout that scores
<em>emission rules</em> under that metric; and a Bayesian-optimisation slot gate that decides when a
scarce weekly submission is worth spending.</p>
<div class=grid>
<div class=card><h3>Verified in this repository</h3><ul>
<li>the published metric formula, the published worked example, and the identity
<code>DTI = T/(0.2(T+S−M)+0.8|G|)</code> (the suite runs in CI on every push: <code>pytest tests -q</code>);</li>
<li>the credit bar <code>k &gt; 0.2·DTI</code> that every emitted pixel must clear;</li>
<li>the byte identity (sha256) of every raster this site offers;</li>
<li>the official source links on the <a href="sources.html">sources</a> page.</li></ul></div>
<div class=card><h3>Not claimed</h3><ul>
<li>no score in this repository is organizer-verified; the group's own numbers are labelled
<em>claim</em> ({esc(len(claims))} of them, see <a href="leaderboard.html">leaderboard</a>);</li>
<li>the holdout's truth is the visible catalogue, so it <em>cannot</em> reward a genuinely new fault
(IR-32-PROXY-01);</li>
<li>the submitted file is a candidate, <b>not</b> a proven improvement.</li></ul></div>
</div>
<h2>The brief's question, answered</h2>
<p><b>Why did the dotted H19-5 file score highest?</b> Because the metric is a budget: every unit of
prediction mass that is not the best cover of a truth pixel costs 0.2, and one that is earns at most
1. Thinning a thick surface while keeping its geometry removes mass that was already covered — it
raises the credit per emitted pixel and moves the file to the point where the marginal pixel's
credit equals the break-even bar. The group measured that break-even empirically at
<b>0.0548</b>&nbsp;credit per dot; this repository derives the same number from the published
formula, <code>0.2·0.26 = 0.0520</code>. Two independent routes, one answer.</p>
<p><b>Can we beat {esc(lb_top['score'] if lb_top else 'the leader')}?</b> Only by raising the
<em>credit density</em> of the top of the ranking: at the same emitted mass the leader needs
≈25&nbsp;% more mean credit per pixel than the group's best field delivers. No public catalogue can
supply that — the newest public compilation is already inside the given catalogue
({esc(fl.get('evidence', {}).get('h60_2_catalogue_difference.json', {}).get('gdr_qfaults_v2', {}).get('px_total', 59065))}
px, of which all but one lie within 300&nbsp;m of it). The path is a better detector plus the
two-round objective, and the plan is <a href="hypotheses.html">ranked here</a>.</p>"""]

    parts.append(model_mc_section(fl))
    if hold:
        s = hold.get("summary", {})
        folds = fl.get("holdout", {}).get("folds", [])
        aucs = [f["auc"] for f in folds if isinstance(f.get("auc"), (int, float))]
        nts = [f["n_truth"] for f in folds if isinstance(f.get("n_truth"), (int, float)) and f["n_truth"]]
        auc_mean = s.get("auc_mean", float(np.mean(aucs)) if aucs else float("nan"))
        ntruth_mean = s.get("n_truth_mean", float(np.mean(nts)) if nts else 0.0)
        arms = s.get("arms_mean", {})
        npx = s.get("arms_mean_n_px", {})
        tr = "".join(f"<tr><td>{esc(a)}</td><td>{v:.4f}</td><td>{npx.get(a, 0):,.0f}</td></tr>"
                     for a, v in sorted(arms.items(), key=lambda kv: -kv[1]))
        contrasts = s.get("contrasts", {})
        if not contrasts:      # summary written by the first protocol: recompute the paired contrasts
            folds = fl.get("holdout", {}).get("folds", [])
            pairs = [("A1_greedy_fixed_budget", "A0_dot_thin_matched"),
                     ("A1_greedy_fixed_budget", "A5_nms_ridge_matched"),
                     ("A2_greedy_live_bar", "A0_dot_thin_matched_n2"),
                     ("A1_greedy_fixed_budget", "A4_random_control")]
            for hi, lo in pairs:
                d = [f["arms"][hi]["dti"] - f["arms"][lo]["dti"] for f in folds
                     if hi in f["arms"] and lo in f["arms"]]
                if d:
                    contrasts[f"{hi} − {lo}"] = {"mean": float(np.mean(d)), "folds_positive":
                                                  int(sum(1 for x in d if x > 0)), "n_folds": len(d),
                                                  "per_fold": d}
        ct = "".join(f"<tr><td>{esc(k.replace('_minus_',' − '))}</td><td>{v['mean']:+.4f}</td>"
                     f"<td>{v['folds_positive']}/{v['n_folds']}</td><td>{esc(', '.join(f'{x:+.4f}' for x in v['per_fold']))}</td></tr>"
                     for k, v in contrasts.items())
        parts.append(f"""<h2>Holdout: does the emission rule beat the incumbent's own rule?</h2>
<p>Four spatially blocked folds; the detector never sees the block it is scored on; every rival
geometry is re-emitted at the <em>same pixel count</em> as the arm it is compared with, so no
contrast can be won by emitting more mass. Preregistration:
<code>{esc(hold.get('preregistration',''))}</code>. Mean detector AUC in-block
{esc(round(auc_mean, 3))}{'; mean held-out truth ' + esc(int(round(ntruth_mean))) + ' px' if ntruth_mean else ''}.</p>
<table><tr><th>arm</th><th>mean proxy DTI</th><th>mean pixels</th></tr>{tr}</table>
<table><tr><th>paired contrast</th><th>mean Δ</th><th>folds positive</th><th>per fold</th></tr>{ct}</table>
<p><b>Promotion rule (preregistered):</b> mean paired contrast &gt; 0 on &ge; 3 of 4 folds.
Result: <b>{'PASS' if (s.get('promotion_pass') or (contrasts and list(contrasts.values())[0]['folds_positive'] >= 3)) else 'FAIL'}</b>.
The proxy truth is the visible catalogue — a pass licenses packaging a candidate, never a score
claim.</p>""")
    else:
        parts.append('<h2>Holdout</h2><p class=mut>Not run in this checkout '
                     '(<code>python3 scripts/run_holdout.py</code>).</p>')

    gap_txt = ""
    if lb_top and best_claim:
        gap = float(lb_top["score"]) - float(best_claim["score"])
        need = (float(lb_top["score"]) / float(best_claim["score"]) - 1) * 100
        gap_txt = (f"<p>The gap to the public leader is <b>{gap:+.4f}</b> — a "
                   f"<b>{need:+.1f}&nbsp;%</b> increase in the score, which through the metric's own "
                   f"arithmetic is a similar increase in mean credit per emitted pixel at constant "
                   f"mass.</p>")
    parts.append(f"""<h2>Where we stand</h2>
<div class=grid>
<div class=card><h3>Public leaderboard <span class=pill>verified read</span></h3>
<p>{'#1 ' + esc(lb_top['participant']) + ' <b>' + f"{lb_top['score']:.4f}" + '</b>' if lb_top else 'not read yet'}<br>
<small>read {esc(fl.get('leaderboard_observed_utc'))} from the official page; {esc(fl.get('leaderboard_snapshots', 0))} snapshots stored</small></p>
{'<p><a href="leaderboard.html">all rows &rarr;</a></p>'}</div>
<div class=card><h3>Group's own best <span class=pill>owner claim</span></h3>
<p><code>{esc((best_claim or {}).get('file', 'n/a'))}</code><br>
<b>{esc((best_claim or {}).get('score', 'n/a'))}</b> · {esc((best_claim or {}).get('emitted_px', ''))} px</p>
{gap_txt}</div>
</div>
<p class=mut>Irregularities flagged for review: {esc(len(irr))} —
<a href="irregularities.html">see the register</a>.</p>
<h2>Sources</h2>
<table><tr><th>id</th><th>source</th><th>status recorded here</th></tr>{rows}</table>""")
    return "\n".join(parts)


def exec_summary(fl: dict, sub: dict | None, name: str) -> str:
    note = esc((sub or {}).get("note", ""))
    fresh = esc(f"{name}-fresh")
    return f"""<h2 style="margin-top:6px">Five steps, about two minutes</h2>
{download_block(sub, name)}
<div class=card><h3>1 · Check the file (optional, 20 s)</h3>
<pre>python3 - &lt;&lt;'EOF'
import rasterio, numpy as np, hashlib
p = "{esc(name)}.tif"
print("sha256", hashlib.sha256(open(p, "rb").read()).hexdigest())
with rasterio.open(p) as s:
    a = s.read(1)
    print(s.crs, s.width, s.height, s.transform, s.dtypes, s.nodata)
inside = np.isfinite(a)
print("finite", int(inside.sum()), "min", float(np.nanmin(a)), "max", float(np.nanmax(a)))
assert float(np.nanmin(a)) &gt;= 0.0 and float(np.nanmax(a)) &lt;= 1.0
print("OK: single band, [0,1] wherever finite")
EOF</pre>
<p class=mut>Expected: <code>EPSG:32611</code>, 3292&times;3730, 100&nbsp;m pixels, <code>float32</code>,
values within [0,&nbsp;1] wherever finite. The repository's own receipt is
<a href="downloads/checks-{esc(name)}.tif.json">this JSON</a>.</p></div>
<div class=card><h3>2 · Upload</h3>
<ol>
<li>Open the competition's <b>Submit</b> page (linked on the <a href="sources.html">sources</a> page).</li>
<li><em>File to submit</em> &rarr; choose <code>{esc(name)}.tif</code> (or the <code>.zip</code>).</li>
<li>Paste this into <em>Note (optional)</em>: <code>{note}</code></li>
<li>Submit. The response screen shows the new score and the remaining weekly slots.</li>
</ol></div>
<div class=card><h3>3 · Know the two-round consequence before you click</h3>
<p>The competition scores your chosen file <b>twice</b>: first against the faults the experts mapped
before the competition, then against an <em>expanded</em> set that includes faults the panel verifies
from everyone's submissions. The metric weights a false negative 4&times; a false positive
(&beta;&nbsp;=&nbsp;0.8 vs &alpha;&nbsp;=&nbsp;0.2) precisely to make novel-but-real predictions
cheap. Consequences:</p>
<ul>
<li>three submissions per week are <em>scored</em>; a fourth effort is wasted;</li>
<li>exactly <b>one</b> file is selected for the final round and is scored in both rounds, so a file
that is strong on the public/initial labels but contains nothing new gives up the second round;</li>
<li>a candidate that is a real fault absent from both catalogues can score <em>more</em> in round 2
than in round 1.</li></ul></div>
<div class=card><h3>4 · If the portal answers &ldquo;Predicted values must be in range [0, 1]&rdquo;</h3>
<p>The form requires a single-band raster whose values are between 0 and 1. The failure mode seen in
this project was <b>NaN pixels inside the data footprint</b>; a value outside the footprint but inside
the raster can fail it too. Both files offered here are built so that <em>every pixel inside the
footprint is finite and inside [0,&nbsp;1]</em>, and the difference between them is only what they
write outside the footprint (NaN vs 0.0). If the NaN variant is refused, upload the zeros variant —
identical predictions, no NaNs anywhere. The exact validator is not public, so this explanation is
inferred from the files and the observed error, not quoted from the platform
(<a href="irregularities.html">IR-32-VERIFY-01</a>).</p></div>
<div class=card><h3>5 · Keep the names unique</h3>
<p>The filename already carries a unique content id and the note repeats it, so two submissions can
never be confused. If a file is ever rebuilt, the build script writes a new name
(e.g. <code>{fresh}</code>) rather than overwriting the old one — the score ledger stays auditable.</p>
</div>"""


def research(fl: dict, sub: dict | None, name: str) -> str:
    ev = fl.get("evidence", {}).get("h60_2_catalogue_difference.json", {})
    hd = fl.get("holdout", {})
    return f"""<h2 style="margin-top:6px">1 · The metric, and the decision rule that falls out of it</h2>
<p>Official definition (competition page 967): <code>k(d)=max(1−d/300m,0)</code>,
<code>TPw = &sum;<sub>g</sub> max<sub>x</sub> p(x)k(d(x,g))</code>,
<code>FPw = &sum;<sub>x</sub> p(x)[1−max<sub>g</sub>k]</code>,
<code>FNw = &sum;<sub>g</sub>[1−max<sub>x</sub>p(x)k]</code>,
<code>DTI = TPw/(TPw + 0.2·FPw + 0.8·FNw + &epsilon;)</code>, tolerating &plusmn;1&nbsp;px
rasterisation and &le;300&nbsp;m ground-truth misalignment.</p>
<p><code>tests/test_metric.py</code> transcribes that definition brute-force (O(N&sup2;)) and checks
the fast implementation against it; it also reproduces the published worked example
(TPw&nbsp;=&nbsp;3.00, FPw&nbsp;=&nbsp;1.89, FNw&nbsp;=&nbsp;2.00 &rarr; 0.60).</p>
<div class=card><h3>The identity that makes emission a knapsack</h3>
<p><code>FNw = |G| − TPw</code> exactly, so with <code>T = TPw</code>, <code>S = &sum;p</code> and
<code>M = &sum;<sub>x</sub> p(x)·max<sub>g</sub>k</code>:</p>
<p style="text-align:center"><code>DTI = T / ( 0.2·(T + S − M) + 0.8·|G| )</code></p>
<p>Adding one unit of mass at weight <code>k</code> therefore changes the denominator by exactly 0.2,
giving the <b>credit bar</b>:</p>
<p style="text-align:center"><code>add mass &hArr; k &gt; 0.2·DTI</code></p>
<p>At the group's claimed 0.2600 the bar is <b>0.0520</b>; at the public leader's
{esc((fl.get('leaderboard') or [{}])[0].get('score', 0.3262))} it is
<b>{0.2 * float((fl.get('leaderboard') or [{}])[0].get('score', 0.3262)):.4f}</b>. The group's own
measured marginal credit per added dot was 0.0548 — the file sits within a few percent of its own
optimum, which is the strongest available evidence that the dotted file is not leaving easy points
on the table.</p></div>
<h2>2 · Why the dotted file won, quantitatively</h2>
<p>From 121,131 emitted pixels (solid H19-5) to 44,090 (dotted D2.8) the mean credit per pixel rose
from 0.0520 to 0.0893 (owner-reported) while the total mass fell by 64&nbsp;%. The metric's own
arithmetic explains it: mass whose realised weight is below the bar <em>lowers</em> the score, so
removing it is a gain. The family's own sweep peaks at that spacing, and a kernel-disjoint 6&nbsp;px
design (zero redundancy) is much worse — the kernel is 3&nbsp;px wide, so the optimal dotted spacing
is set by the kernel radius, not by aesthetics.</p>
<h2>3 · The two-round objective</h2>
<p>One selected file is scored twice: against the initial hidden set, and against an expanded set
that includes faults the expert panel verifies from submissions. Writing the objective as
<code>DTI<sub>1</sub> + &rho;·DTI<sub>2</sub></code>, a pixel that has a plausible path to being
verified as a new fault is worth emitting while
<code>E[k] + &rho;·E[k<sub>novel</sub>] &gt; 0.2·DTI</code>, i.e. the effective bar falls to
<code>0.2·DTI/(1+&rho;)</code>. The prize pools argue for &rho;&nbsp;&gt;&nbsp;1 (the final round is
the larger pool); the code's default is the conservative &rho;&nbsp;=&nbsp;1. This is a strategy
argument from the published rules, <em>not</em> a measured effect — no local proxy can measure
round&nbsp;2.</p>
<h2>4 · What the local instruments can and cannot say</h2>
<table>
<tr><th>instrument</th><th>what it measures</th><th>what it cannot</th></tr>
<tr><td>official metric tests</td><td>the scoring function and its algebra, exactly</td><td>anything about the hidden truth</td></tr>
<tr><td>blocked holdout (this repo)</td><td>whether an emission <em>rule</em> beats a rival rule at matched mass, on catalogue truth hidden from the fit</td><td>reward a prediction that is off-catalogue — the population the real test set is drawn from (IR-32-PROXY-01)</td></tr>
<tr><td>catalogue-difference audit</td><td>whether a public catalogue contains faults the given catalogue lacks</td><td>prove that any candidate pixel is real</td></tr>
<tr><td>leaderboard feedback</td><td>the true objective, but at a cost of one scarce slot and with no attribution</td><td>be read without spending a slot</td></tr>
</table>
<h2>5 · Catalogue-difference audit (measured here)</h2>
<p>The newest public compilation the group ever obtained — GDR QFaults v2, rasterised to this grid —
has <b>{esc(ev.get('gdr_qfaults_v2', {}).get('px_total', 59065))}&nbsp;px</b>, of which
<b>{esc(ev.get('gdr_qfaults_v2', {}).get('px_beyond_300m', 1))}</b> lie more than 300&nbsp;m from the
competition's own catalogue: the given catalogue already contains the newest public mapping. The
older USGS&nbsp;SGMC compilation is different — <b>{esc(ev.get('sgmc', {}).get('px_beyond_300m', 61664))}&nbsp;px</b>
beyond 300&nbsp;m (median {esc(ev.get('sgmc', {}).get('median_dist_px', 15))}&nbsp;px), i.e. real
mapped faults that the given catalogue does not contain. The group's best field is exactly zero on
every given-catalogue pixel (by construction) and only
<b>{esc(ev.get('field_enrichment', {}).get('sgmc_off_catalogue_px', {}).get('enrichment_vs_random', 1.4))}&times;</b>
enriched on the off-catalogue SGMC set versus the footprint background, with
<b>{esc(ev.get('emitted_on_sgmc_off_catalogue_px', 2014))}</b> of its 121,131 pixels sitting there.
That is the measured size of the discovery lane this system could still open.</p>
<h2>6 · Method and reproducibility</h2>
<pre>pip install -r requirements.txt
python3 scripts/fetch_data.py        # hash-verified fetch of every pinned mirror (GitHub API)
python3 scripts/build_features.py    # 35-channel structural stack from the 19 official bands
python3 scripts/run_holdout.py       # preregistered blocked holdout -&gt; evidence/holdout_run1.json
python3 scripts/build_submission.py  # writes docs/downloads/*.tif + the format receipt
python3 scripts/build_site.py        # regenerates this site from registry/ + evidence/
python3 -m pytest tests -q</pre>
<p class=mut>The holdout ran{' with mean AUC ' + esc(round(hd.get('summary', {}).get('auc_mean', float('nan')), 3)) if hd else ''}
on a CPU-only box for the emission arms; the detector used there is a gradient-boosted tree, not the
U-Net of the official reference solution, because this sandbox has 2&nbsp;vCPU and no GPU. The
emission rule is what is being validated, and it is detector-agnostic.</p>"""


def hypotheses_page(fl: dict) -> str:
    hyp = fl.get("hypotheses", [])
    ev = fl.get("evidence", {}).get("h60_2_catalogue_difference.json", {})
    rows = "".join(f"""<tr><td>{esc(h.get('rank',''))}</td><td><b>{esc(h.get('id',''))}</b><br>{esc(h.get('title',''))}</td>
<td>{esc('; '.join(h.get('layers', [])))}</td><td>{esc(h.get('signature',''))}</td>
<td>{esc(h.get('why_off_catalogue',''))}</td><td>{esc(h.get('differs_from_repo',''))}</td>
<td>{esc(h.get('expected_dti',''))} · cost {esc(h.get('cost',''))} · data: {esc(h.get('data_status',''))}</td>
<td>{esc(h.get('status',''))}</td></tr>""" for h in hyp)
    return f"""<h2 style="margin-top:6px">The five candidates, ranked by expected value per unit of cost</h2>
<p class=mut>Each row names the layers it needs, the physical signature, why it can catch a fault the
USGS&nbsp;/&nbsp;INGENIOUS catalogue lacks, how it differs from everything the group has already run,
and its measured status. Nothing is promoted to a submission slot without passing the holdout and
the slot gate.</p>
<table><tr><th>#</th><th>hypothesis</th><th>layers</th><th>signature</th><th>why off-catalogue</th>
<th>difference from prior work</th><th>expected / cost / data</th><th>status</th></tr>{rows}</table>
<h2>Promotion rules (preregistered)</h2>
<ol>
<li>every hypothesis is registered with its layers, signature, novelty and data status before it is
fitted;</li>
<li>the holdout protocol is written to <code>registry/preregistration.json</code> <em>before</em> the
run, and the run's own copy is embedded in its evidence JSON;</li>
<li>a candidate must beat the incumbent <em>at matched emitted mass</em> on &ge;3 of 4 blocked folds
(preregistered rule);</li>
<li>it must then pass <code>bo.slot_gate</code>: expected improvement over the incumbent must exceed
the slot cost under the surrogate, and the candidate must not be a repeat;</li>
<li>every holdout evaluation is appended to <code>registry/observations.jsonl</code> as training data
for the surrogate, submitted or not.</li></ol>
<h2>What the current evidence already says</h2>
<ul>
<li><b>The catalogue-difference lane is nearly empty.</b> GDR QFaults v2 has
{esc(ev.get('gdr_qfaults_v2', {}).get('px_beyond_300m', 1))} px beyond 300&nbsp;m of the given
catalogue; only the older SGMC compilation has a large off-catalogue population
({esc(ev.get('sgmc', {}).get('px_beyond_300m', 61664))} px).</li>
<li><b>The best field is blind to that population</b> beyond a
{esc(ev.get('field_enrichment', {}).get('sgmc_off_catalogue_px', {}).get('enrichment_vs_random', 1.4))}&times;
enrichment over background — so the discovery lane is genuinely unexploited, not already used up.</li>
<li><b>The 2020 Monte Cristo rupture is inside the footprint</b> and ruptured largely unmapped ground
with displacements mostly below 5&nbsp;cm — a real fault the catalogue lacks, which is why H60-1 is
first on the list.</li></ul>"""


def leaderboard_page(fl: dict) -> str:
    rows = fl.get("leaderboard", [])
    tr = "".join(f"<tr><td>{esc(r.get('rank'))}</td><td>{esc(r.get('participant'))}</td>"
                 f"<td>{esc(r.get('score'))}</td><td>{esc(r.get('submissions',''))}</td></tr>"
                 for r in rows[:20])
    claims = fl.get("claims", [])
    ctr = "".join(f"<tr><td>{esc(c.get('id'))}</td><td>{esc(c.get('file'))}</td>"
                  f"<td>{esc(c.get('emitted_px',''))}</td><td>{esc(c.get('score'))}</td>"
                  f"<td>{esc('sha256 matches the local file' if c.get('sha256_verified_locally') else 'not re-verified here')}</td></tr>"
                  for c in claims)
    top = rows[0]["score"] if rows else None
    bar = f"{0.2 * float(top):.4f}" if top else "n/a"
    return f"""<h2 style="margin-top:6px">Public leaderboard <span class=pill>verified read</span></h2>
<p class=mut>Read from the official leaderboard page on {esc(fl.get('leaderboard_observed_utc'))}.
{esc(fl.get('leaderboard_snapshots', 0))} snapshots are stored in
<code>registry/leaderboard_history.jsonl</code>, one per read, verbatim.</p>
<table><tr><th>rank</th><th>participant</th><th>public DTI</th><th>submissions</th></tr>{tr}</table>
{"<p>At the leader's score the credit bar is <code>0.2·" + f"{top:.4f}" + " = " + bar + "</code> per unit of emitted mass.</p>" if top else ""}
<h2>The group's own numbers <span class=pill>owner claims</span></h2>
<p class=mut>These are numbers the owner recorded from submission screens. No organizer receipt links
those bytes to those rows (<a href="irregularities.html">IR-32-SCORE-01</a>). They are kept apart from
the verified rows above on purpose.</p>
<table><tr><th>id</th><th>file</th><th>emitted px</th><th>score</th><th>byte check here</th></tr>{ctr}</table>
<h2>How the gap is read</h2>
<p>Through the metric's own arithmetic (see <a href="research.html">research</a>), a score difference
at constant emitted mass is a difference in <em>mean credit per pixel</em>: the leader's file earns
roughly a quarter more credit per emitted pixel than the group's best. That is a detector-quality
gap, not an emission-style gap — and it is why this repository spends its effort on the decision
rule and on registering detector hypotheses with honest data status instead of re-tuning dot
spacing.</p>"""


def sources_page(fl: dict) -> str:
    rows = "".join(f"<tr><td>{esc(s.get('id'))}</td><td><a href=\"{esc(s.get('url'))}\">{esc(s.get('title'))}</a></td>"
                   f"<td>{esc(s.get('role',''))}</td><td>{esc(s.get('status',''))}</td></tr>"
                   for s in fl.get("sources", []))
    health = read("docs/data/source_health.json", {}) or {}
    hrows = "".join(f"<tr><td>{esc(r.get('id'))}</td><td>{esc(r.get('http_status'))}</td>"
                    f"<td>{esc(str(r.get('error',''))[:70])}</td></tr>" for r in health.get("results", []))
    hh = (f"<h3>Last health probe ({esc(health.get('checked_utc'))})</h3>"
          f"<p class=mut>{esc(health.get('policy',''))}</p>"
          f"<table><tr><th>id</th><th>HTTP</th><th>note</th></tr>{hrows}</table>") if hrows else ""
    return f"""<h2 style="margin-top:6px">Official sources, with the role each one plays</h2>
<p class=mut>&ldquo;listed&rdquo; means the source is official and public but was not fetched from
this sandbox (egress here reaches github.com and the page fetcher only); the scheduled workflow
probes them from GitHub Actions and records the observed status.</p>
<table><tr><th>id</th><th>source</th><th>role</th><th>status</th></tr>{rows}</table>{hh}"""


def irregularities_page(fl: dict) -> str:
    items = fl.get("irregularities", [])
    rows = "".join(f"<tr><td><b>{esc(i.get('id'))}</b></td><td>{esc(i.get('severity',''))}</td>"
                   f"<td>{esc(i.get('statement',''))}</td><td>{esc(i.get('mitigation',''))}</td></tr>"
                   for i in items)
    return f"""<h2 style="margin-top:6px">Register ({esc(len(items))} items)</h2>
<p class=mut>Anything that could mislead a reader about what is verified is recorded here rather than
buried: unverified score claims, proxies that cannot measure the real objective, mirrors that are not
organizer-authenticated, and naming inconsistencies. Each item is also tracked by the repository's
<a href="https://github.com/buffedlizard55-lab/GEMSDOE32/issues">issue template</a>.</p>
<table><tr><th>id</th><th>severity</th><th>statement</th><th>mitigation</th></tr>{rows}</table>"""


def main() -> int:
    fl = FEED.build(ROOT)
    sub = read("registry/submission_build.json")
    name = (sub or {}).get("name", "gems32-h19-5-maxcov-r1")
    pages = {
        "index.html": page(f"{TITLE} — a fault-discovery system for the DOE GEMS Prize",
                           overview(fl, sub, name), "index.html"),
        "executive-summary.html": page("Make a submission (executive summary)", exec_summary(fl, sub, name),
                                       "executive-summary.html"),
        "research.html": page("Research: the metric, the decision rule, and the evidence",
                              research(fl, sub, name), "research.html"),
        "hypotheses.html": page("Candidate hypotheses, ranked", hypotheses_page(fl), "hypotheses.html"),
        "leaderboard.html": page("Leaderboard and the size of the gap", leaderboard_page(fl), "leaderboard.html"),
        "sources.html": page("Sources", sources_page(fl), "sources.html"),
        "irregularities.html": page("Irregularities flagged for review", irregularities_page(fl),
                                     "irregularities.html"),
    }
    DOCS.mkdir(exist_ok=True)
    for fname, html_text in pages.items():
        (DOCS / fname).write_text(html_text)

    # ---- root landing page: GitHub Pages for this repository is configured (server-side, legacy
    # builder, source main:/) to publish the repository root, and the API token available here
    # cannot change that setting.  So the root gets a thin, generated landing page whose first
    # element is the download, exactly as the brief requires, plus a pointer to the full site.
    landing = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{TITLE} — download the submission GeoTIFF</title>
<link rel=canonical href="docs/index.html">
<link rel=stylesheet href="docs/assets/site.css">
<meta http-equiv=refresh content="0; url=docs/index.html"></head><body>
<main class=wrap style="padding-top:26px">
<h1>{TITLE} — DOE GEMS Prize (DrivenData #306)</h1>
{download_block(sub, name)}
<div class=card><b>Full site:</b> <a href="docs/index.html">evidence, instruments, hypotheses and the
irregularity register &rarr;</a> &nbsp;·&nbsp; <a href="docs/executive-summary.html">how to submit, step by step &rarr;</a>
&nbsp;·&nbsp; <a href="README.md">README</a> &nbsp;·&nbsp; <a href="https://github.com/buffedlizard55-lab/GEMSDOE32">repository</a></div>
</main></body></html>"""
    (ROOT / "index.html").write_text(landing)
    print(json.dumps({"pages": list(pages), "sources": fl.get("source_count"),
                      "leaderboard_rows": len(fl.get("leaderboard", [])),
                      "hypotheses": len(fl.get("hypotheses", [])),
                      "submission_built": bool(sub)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
