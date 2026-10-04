#!/usr/bin/env python3
"""Generate the GitHub Pages site from the registry JSON (no manual edits, always current)."""
import html
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import feed as FEED  # noqa: E402

DOCS = ROOT / "docs"
NAV = [("index.html", "Home"), ("executive-summary.html", "Submit in 5 minutes"),
       ("research.html", "Research &amp; method"), ("hypotheses.html", "Hypotheses"),
       ("leaderboard.html", "Leaderboard"), ("sources.html", "Sources"),
       ("irregularities.html", "Irregularities")]


def esc(x):
    return html.escape(str(x))


def page(title, body, active=""):
    nav = " ".join(f'<a href="{h}"{" class=mut" if h!=active else ""}>{t}</a>' for h, t in NAV)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><link rel=stylesheet href=assets/site.css></head><body>
<header><div class=wrap><h1>{esc(title)}</h1><nav>{nav}</nav></div></header>
<main class=wrap>{body}</main>
<footer><div class=wrap>GEMSDOE32 &middot; generated {time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime())} from <code>registry/</code> + <code>evidence/</code> &middot;
scores marked <em>claim</em> are owner-reported, not organizer receipts; the public leaderboard rows are read from the official page.
<a href="https://github.com/buffedlizard55-lab/GEMSDOE32">repository</a></div></footer></body></html>"""


def load(p, default=None):
    try:
        return json.loads((ROOT / p).read_text())
    except Exception:
        return default


def build():
    f = FEED.build(ROOT)
    sub = load("registry/submission_build.json")
    hold = load("evidence/holdout_run1.json")
    hyp = load("registry/hypotheses.json", {"hypotheses": []})["hypotheses"]
    irr = load("registry/irregularities.json", {"items": []})["items"]
    prereg = load("registry/preregistration.json", {})
    checks = {}
    if sub and sub.get("files", {}).get("nan"):
        name = Path(sub["files"]["nan"]["path"]).name
        checks = load(f"docs/downloads/checks-{name}.json", {}) or {}
    lb = f.get("leaderboard", [])

    # ---------------------------------------------------------------- index / executive summary
    dl_name = Path(sub["files"]["nan"]["path"]).name if sub and sub.get("files") else None
    if dl_name:
        c = checks
        dl = f"""<div class=dl><h2 style="margin-top:0">1 &middot; Download the submission GeoTIFF</h2>
<p><a class=btn href="downloads/{esc(dl_name)}">&#11015; {esc(dl_name)}</a>
<a class=btn href="downloads/{esc(dl_name.replace('.tif','.zip'))}">&#11015; .zip</a></p>
<p class=mut>single-band float32 GeoTIFF &middot; EPSG:32611 &middot; 100 m &middot; 3730&times;3292 &middot;
{c.get('positive_px','?')} predicted pixels &middot; every footprint pixel finite in [0,&nbsp;1] &middot;
outside the footprint NaN &middot; sha256 <code>{esc(str(c.get('sha256',''))[:16])}&hellip;</code></p>
<p><b>Note to paste in DrivenData's <em>Note (optional)</em> field:</b><br>
<code>GEMSDOE32 cover-r1 | greedy max-expected-coverage emission of the H19-5 field, mass-matched to the best shipped file | NOT a verified score | sha {esc(str(c.get('sha256',''))[:12])}</code></p>
<p class=mut>Format fallback (same predictions, zeros outside the footprint):
<a href="downloads/{esc(dl_name.replace('.tif','-zeros.tif'))}">zeros variant</a> &middot;
<a href="downloads/checks-{esc(dl_name)}.json">format receipt</a> &middot;
<a href="executive-summary.html">step-by-step upload instructions</a></p>
<p class=warn><b>Read this before you spend a slot.</b> This file is <em>format-validated</em> and its
emission rule was <em>validated on a spatially blocked holdout</em> against the current best comparable rule
(see below). It is not organizer-scored, the leaderboard score of its field is an owner report, and the
weekly budget is three submissions with a single file counting for both prize rounds.</p></div>"""
    else:
        dl = ('<div class=dl><h2 style="margin-top:0">Submission GeoTIFF</h2><p class=mut>The build has not '
              'been run in this checkout yet: <code>python3 scripts/fetch_data.py &amp;&amp; '
              'python3 scripts/build_features.py &amp;&amp; python3 scripts/build_submission.py</code>.</p></div>')

    hold_tbl = ""
    if hold:
        s = hold["summary"]
        rows = "".join(f"<tr><td>{esc(a)}</td><td>{v:.4f}</td><td>{s['arms_mean_n_px'].get(a,0):.0f}</td></tr>"
                       for a, v in sorted(s["arms_mean"].items(), key=lambda kv: -kv[1]))
        contrast = "".join(f"<tr><td>{esc(k)}</td><td>{v['mean']:+.4f}</td><td>{v['folds_positive']}/{v['n_folds']}</td></tr>"
                           for k, v in s.items() if isinstance(v, dict) and "mean" in v)
        hold_tbl = f"""<h3>Blocked holdout, emission-arm ladder ({esc(hold.get('preregistration',{}).get('id',''))})</h3>
<table><tr><th>arm</th><th>mean proxy DTI</th><th>mean emitted px</th></tr>{rows}</table>
<table><tr><th>contrast</th><th>mean paired &Delta;</th><th>folds positive</th></tr>{contrast}</table>
<p class=mut>Proxy = the visible catalogue hidden inside each block (hide-and-recover); it is
<em>not</em> the competition's hidden new-fault set. Preregistered before the run:
<code>{esc(json.dumps(prereg, indent=0)[:600])}</code></p>"""
    else:
        hold_tbl = '<p class=mut>Holdout run not present in this checkout (see <code>scripts/run_holdout.py</code>).</p>'

    lb_rows = "".join(f"<tr><td>{r['rank']}</td><td>{esc(r['participant'])}</td><td>{r['score']:.4f}</td>"
                      f"<td>{r.get('submissions','')}</td></tr>" for r in lb[:17])
    index = page("GEMSDOE32 — an auditable fault-discovery system for the DOE GEMS Prize", f"""
{dl}
<div class=grid>
<div class=card><h3>What this system is</h3>
<ul>
<li>A <b>verified implementation of the official metric</b> plus its algebra: the credit bar
<code>k &gt; 0.2&middot;DTI</code> (0.052 at the group's best 0.26, 0.065 at the leaderboard #1 0.3262).</li>
<li>A <b>spatially blocked holdout harness</b> that scores emission rules with the official
metric on hidden catalogue blocks, preregistered before every run.</li>
<li>A <b>Bayesian-optimisation slot gate</b> (<code>src/gems32/bo.py</code>): GP surrogate,
expected improvement, explicit slot cost, and a drift report when live scores stop matching the
proxy.</li>
<li>A <b>live feed</b> of official sources and the public leaderboard ({f['source_count']} sources,
leaderboard last read {esc(str(f['leaderboard_observed_utc']))}).</li>
</ul></div>
<div class=card><h3>Where we stand (honest)</h3>
<ul>
<li>Public leaderboard #1 is <b>{lb[0]['score'] if lb else '?'}</b> ({esc(lb[0]['participant']) if lb else '?'}), observed {esc(str(f['leaderboard_observed_utc']))}.</li>
<li>The group's best owner-reported score is <b>0.2600</b> (a dotted H19-5 emission; the row it is
attributed to is unverified — <a href="irregularities.html">IR-32-SCORE-01</a>).</li>
<li>Nothing in this repository has been scored. The download above is a <em>candidate</em>.</li>
</ul></div>
</div>
{hold_tbl}
<h2>The one-page case</h2>
<blockquote>The metric is a <em>contract</em>: a false negative costs 4&times; a false positive
(&alpha;=0.2, &beta;=0.8 on the official page), and 300 m of distance decay means an approximate
line is still paid for. The system's job is therefore to place the <em>thinnest possible</em>
prediction where the expected credit per unit mass exceeds <code>0.2&middot;DTI</code> — and to
spend one of the three weekly slots only when a surrogate says the expected improvement justifies
the cost. Full derivation: <a href="research.html">Research &amp; method</a>.</blockquote>
<h2>Feed</h2>
<div class=card><b>Checklist before a slot</b>
<ol><li>Does the candidate beat the incumbent on the <em>same-run</em> blocked holdout? (see the ladder above)</li>
<li>Is the expected improvement over the incumbent larger than the slot cost? (<code>bo.slot_gate</code>)</li>
<li>Is the file format-validated by an independent re-read? (<code>checks-&hellip;.json</code>)</li>
<li>Is the note field filled and the two-round consequence understood? (<a href="executive-summary.html">instructions</a>)</li></ol>
</div>""", "index.html")

    # ---------------------------------------------------------------- executive summary
    exe = page("Submit in five minutes", f"""
<div class=card><h2 style="margin-top:0">1. Download</h2>
<p><a href="downloads/{esc(dl_name or '')}">{esc(dl_name or 'the GeoTIFF')}</a>
(or the <a href="downloads/{esc((dl_name or '').replace('.tif','-zeros.tif'))}">zeros variant</a>).
The <code>.zip</code> beside it contains the same single GeoTIFF for portals that prefer one file.</p></div>
<div class=card><h2 style="margin-top:0">2. Verify (30 seconds)</h2>
<pre>python3 - &lt;&lt;'EOF'
import rasterio, numpy as np, hashlib
p = "{esc(dl_name or 'file.tif')}"
print(hashlib.sha256(open(p,'rb').read()).hexdigest())
with rasterio.open(p) as s:
    a = s.read(1); print(s.crs, s.width, s.height, s.transform, s.dtypes, s.nodata)
inside = np.isfinite(a)
print("finite", inside.sum(), "min", np.nanmin(a), "max", np.nanmax(a))
assert np.nanmin(a) &gt;= 0 and np.nanmax(a) &lt;= 1
EOF</pre>
<p class=mut>Expected: EPSG:32611, 3292&times;3730, 100 m, float32, values in [0,&nbsp;1] wherever finite.
The repository's own receipt is <a href="downloads/checks-{esc(dl_name or '')}.json">here</a>.</p></div>
<div class=card><h2 style="margin-top:0">3. Upload</h2>
<ol><li>Open the competition's <b>Submit</b> page (link on the <a href="sources.html">sources</a> page).</li>
<li>Choose the <code>.tif</code> (or the <code>.zip</code>) as <em>File to submit</em>.</li>
<li>Paste the note from the <a href="index.html">home page</a> box into <em>Note (optional)</em>.</li>
<li>Submit. Remember: <b>three scored submissions per week</b>, and you must later choose <b>one</b>
file that is scored in <em>both</em> prize rounds.</li></ol></div>
<div class=card><h2 style="margin-top:0">4. Why the previous file was rejected with
&ldquo;Predicted values must be in range [0,&nbsp;1]&rdquo;</h2>
<p>The competition requires &ldquo;values between 0 and 1&rdquo; for a single-band float32 raster.
A file that carries <b>NaN inside the data footprint</b> fails every range test, and a file that
writes a value outside the footprint but inside the raster can fail it too. The exact validator is
not public, so this is the data-supported explanation, not a quote from DrivenData
(<a href="irregularities.html">IR-32-VERIFY-01</a>). Both variants shipped here are built so that
<b>every pixel inside the footprint is finite and in [0,&nbsp;1]</b>, and the receipt proves it by
independent re-read.</p></div>
<div class=card><h2 style="margin-top:0">5. The two-round trap (read this once)</h2>
<p>Your chosen file is scored first against a <em>fixed private set of faults the experts mapped
before the competition</em> (top five &rarr; $10k each), and then re-scored against an
<em>expanded</em> label set that includes faults the panel verifies from everyone's submissions
(top five &rarr; $15k&hellip;$100k). A prediction that is a real fault missing from both catalogues
can therefore be <em>worth more in round 2 than round 1</em>, and the metric's own weights
(&alpha;=0.2) price that option cheaply.</p></div>""", "executive-summary.html")

    # ---------------------------------------------------------------- research
    research = page("Research &amp; method", f"""
<div class=card><h2 style="margin-top:0">The metric, verbatim, and what it implies</h2>
<p>From the official problem description: <code>k(d)=max(1-d/300m,0)</code>,
<code>TPw = &sum;_g max_x p(x)k(d(x,g))</code>, <code>FPw = &sum;_x p(x)[1-max_g k]</code>,
<code>FNw = &sum;_g [1-max_x p k]</code>, <code>DTI = TPw/(TPw + 0.2&middot;FPw + 0.8&middot;FNw + &epsilon;)</code>.
The published worked example (TPw=3.00, FPw=1.89, FNw=2.00 &rarr; 0.60) is reproduced by
<code>tests/test_metric.py</code>.</p>
<p><b>Identity 1 (norm).</b> <code>FNw = |G| - TPw</code> exactly, so
<code>DTI = T / (0.2(T + S - M) + 0.8K)</code> with S the total prediction mass and M the mass whose
kernel weight toward the nearest truth pixel is subtracted. Verified to 1e&minus;12 against the
published form on random rasters.</p>
<p><b>Identity 2 (the credit bar).</b> Adding one unit of prediction mass changes the denominator
by exactly 0.2, so <code>dDTI &gt; 0 &hArr; k &gt; 0.2&middot;DTI</code>. At the group's best (0.26)
the bar is <b>0.052</b>; at the leaderboard #1 (0.3262) it is <b>0.065</b>. The group's own
independently measured &ldquo;live rate&rdquo; of credit per added dot is 0.0548 — the analytic bar
and the empirical one agree to a few percent, which is the strongest single piece of evidence that
the group's best file sits exactly at its own optimum.</p>
<p><b>Consequence.</b> Emission is a knapsack: rank pixels by expected new credit, stop at the bar.
The packing objective is the metric's own true-positive term, so the objective and the score are
the same object (submodular &rarr; greedy is within 1&minus;1/e). What the field <em>is</em> matters
more than the packing: a ribbon costs 0.2 per surplus pixel, a centreline costs nothing.</p></div>
<div class=card><h2 style="margin-top:0">The two-round objective: a discovery option</h2>
<p>One file is scored twice. Writing the objective as <code>DTI_1 + &rho;&middot;DTI_2</code>, the
emission bar becomes <code>0.2&middot;DTI/(1+&rho;)</code> for a candidate whose pixels have a
plausible path to being <em>verified</em> as a new fault, because round 2 pays for them and round 1
only charges the (cheap) false-positive mass. The prize pools ($50k initial vs $250k final) argue
for &rho;&nbsp;&gt;&nbsp;1; conservative reading &rho;=1 is what the code defaults to. This arm
(<code>A3</code>) is measured in the holdout ladder, but its real value cannot be measured on a
catalogue-derived proxy — it is a strategy argument from the published rules, and it is labelled as
such.</p></div>
<div class=card><h2 style="margin-top:0">What the previous 30+ sessions established (and why this one is different)</h2>
<ul>
<li>The group built a large, careful experiment registry (H16&hellip;H59 across
<a href="https://github.com/buffedlizard55-lab/GEMSDOE28">GEMSDOE28</a>,
<a href="https://github.com/buffedlizard55-lab/GEMSDOE29">GEMSDOE29</a>,
<a href="https://github.com/buffedlizard55-lab/GEMSDOE30">GEMSDOE30</a>): 2<sup>5-1</sup> factorial
(catalogue geometry +0.0610, DEM curvature/scarp +0.0253 dominant; potential-field gradients,
strain/seismicity and thermal families inert), packing ladders, Euler depth licences, drainage,
slip-tendency and catalogue-difference arms. Almost every promotion decision ends in a veto by a
secondary proxy, and the strongest artifact family remains an emission of the H19-5 surface.</li>
<li><b>The leak they found and this repository excludes:</b> a &ldquo;distance to catalogue&rdquo;
feature gives a detector AUC of exactly 1.0 on the visible labels and transfers nothing
off-catalogue.</li>
<li><b>What was missing:</b> an <em>acquisition function</em>. Their gates are fixed thresholds
evaluated on cheap proxies; there is no model of the live score as an expensive, noisy observation
and no explicit cost for spending a slot. <code>src/gems32/bo.py</code> adds exactly that, logs every
holdout evaluation as training data for it, and reports surrogate-vs-live residuals as holdout
drift.</li>
</ul></div>
<div class=card><h2 style="margin-top:0">Data provenance</h2>
<p>All rasters are fetched from hash-pinned owner mirrors through the GitHub API
(<code>registry/data_manifest.json</code>, verified again on every fetch; 6/7 files match, the
seventh — <code>sample_submission.tif</code> — is pinned by a digest computed here). They are
<b>not</b> organizer-authenticated bytes: see <a href="irregularities.html">IR-32-DATA-01</a>.</p></div>""", "research.html")

    # ---------------------------------------------------------------- hypotheses
    hrows = "".join(f"""<tr><td>{h['rank']}</td><td><b>{esc(h['id'])}</b><br>{esc(h['title'])}</td>
<td>{esc(', '.join(h['layers']))}</td><td>{esc(h['signature'])}</td><td>{esc(h['why_off_catalogue'])}</td>
<td>{esc(h['differs_from_repo'])}</td><td>{esc(h['expected_dti'])}</td><td>{esc(h['cost'])}</td>
<td>{esc(h['data_status'])}</td><td>{esc(h['status'])}</td></tr>""" for h in hyp)
    hypotheses = page("Candidate geological hypotheses (ranked)", f"""
<p class=mut>Ranked by expected DTI improvement per unit of implementation cost. Every row states the
layers, the physical signature, why it should catch a fault the USGS/INGENIOUS catalogue lacks, and
how it differs from the group's registered work (H16&hellip;H59). Nothing here is claimed as a
result unless the <em>status</em> column says it was measured.</p>
<table><tr><th>rank</th><th>hypothesis</th><th>layers</th><th>signature</th><th>why off-catalogue</th>
<th>difference from prior work</th><th>expected DTI</th><th>cost</th><th>data status</th><th>status</th></tr>
{hrows}</table>
<h2>How a hypothesis earns a slot here</h2>
<ol><li>registered with its layers, signature, novelty and data source;</li>
<li>preregistered in <code>registry/preregistration.json</code> before any fit;</li>
<li>measured on the blocked holdout against the incumbent <em>at matched emitted mass</em>;</li>
<li>passed to <code>bo.slot_gate</code>, which also prices the slot and the two-round objective;</li>
<li>only then can it become the file in the download box — and the file itself still has to pass the
independent format re-read.</li></ol>""", "hypotheses.html")

    # ---------------------------------------------------------------- leaderboard
    gap = ""
    if lb:
        top = lb[0]["score"]
        gap = f"""<p>The bar set by the current leader is <b>{top:.4f}</b>. Read through the credit
rule, that is <code>0.2&middot;DTI = {0.2*top:.4f}</code> of credit per unit of emitted mass: every
pixel added must buy at least that much expected true-positive credit, or it lowers the score. The
group's measured credit rate on its best file is 0.0548, i.e. <b>{(0.0548/(0.2*top)-1)*100:+.0f}%</b>
against that bar — enough to explain why thinning (which removes redundant mass) bought easy points
and why further density sweeps on the same field cannot.</p>"""
    leaderboard = page("Leaderboard and the size of the gap", f"""
<h2>Public leaderboard as observed</h2>
<p class=mut>Read from the official page on {esc(str(f['leaderboard_observed_utc']))};
{"stored as verified." if f['leaderboard_verified'] else "not stored as verified."}
This repository does not scrape the score page on a schedule from a logged-out client; the feed
workflow reads the one public HTML page once per day and stores the row verbatim in
<code>registry/leaderboard_history.jsonl</code>.</p>
<table><tr><th>rank</th><th>participant</th><th>public DTI</th><th>submissions</th></tr>{lb_rows}</table>
{gap}
<h2>Our own claims, kept separate</h2>
<p class=mut>The group's ledger (owner-reported, unverified): H19-5 solid 0.1922; its d1.5 dotting
0.2477; its d2.8 dotting 0.2600 (the file this repository re-emits); 26GEMSDOE detector-product
emission 0.1223. None of these has an organizer receipt linking those bytes to that row
(<a href="irregularities.html">IR-32-SCORE-01</a>).</p>
<h2>What the proxy can and cannot say</h2>
<p>A catalogue hide-and-recover proxy cannot reward a prediction that is <em>off</em> the catalogue
by construction, and the group's SGMC secondary proxy ranks its worst artifacts highest. This is why
the slot gate prices the <em>information</em> a submission buys rather than pretending a local
number settles it.</p>""", "leaderboard.html")

    # ---------------------------------------------------------------- sources + irregularities
    srows = "".join(f"""<tr><td>{esc(s['id'])}</td><td><a href="{esc(s['url'])}">{esc(s['title'])}</a></td>
<td>{esc(s['role'])}</td><td>{esc(s['status'])}</td></tr>""" for s in f["sources"])
    health = load("docs/data/source_health.json")
    hh = ""
    if health:
        hrows2 = "".join(f"<tr><td>{esc(r['id'])}</td><td>{esc(str(r.get('http_status')))}</td><td>{esc(str(r.get('error','')))[:60]}</td></tr>"
                         for r in health["results"])
        hh = f"<h3>Last probe ({esc(str(health['checked_utc']))})</h3><table><tr><th>id</th><th>HTTP</th><th>note</th></tr>{hrows2}</table>"
    sources_page = page("Sources (official, link-checked)", f"""
<p class=mut>Every scientific or data claim on this site should be traceable to a row here.
&ldquo;listed&rdquo; means the source is official and public but was not fetched from this sandbox
(egress here is limited to github.com); the feed workflow probes them from CI and writes the status.</p>
<table><tr><th>id</th><th>source</th><th>role</th><th>status</th></tr>{srows}</table>{hh}""", "sources.html")

    irows = "".join(f"<tr><td><b>{esc(i['id'])}</b></td><td>{esc(i['severity'])}</td><td>{esc(i['statement'])}</td>"
                    f"<td>{esc(i['mitigation'])}</td></tr>" for i in irr)
    irregularities = page("Irregularities and flags for review", f"""
<p class=mut>Anything that could mislead a reader is listed here rather than buried in a footnote.</p>
<table><tr><th>id</th><th>severity</th><th>statement</th><th>mitigation</th></tr>{irows}</table>""",
                          "irregularities.html")

    for name, content in [("index.html", index), ("executive-summary.html", exe), ("research.html", research),
                          ("hypotheses.html", hypotheses), ("leaderboard.html", leaderboard),
                          ("sources.html", sources_page), ("irregularities.html", irregularities)]:
        (DOCS / name).write_text(content)
    return {"pages": [n for n, _ in NAV], "feed": f}


if __name__ == "__main__":
    out = build()
    print(json.dumps({"pages": out["pages"], "sources": out["feed"]["source_count"],
                      "leaderboard_rows": len(out["feed"]["leaderboard"])}, indent=1))
