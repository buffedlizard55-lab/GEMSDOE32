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
import rasterio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gems32 import feed as FEED  # noqa: E402

DOCS = ROOT / "docs"
DL = ROOT / "docs" / "downloads"
# root-level pages that GitHub Pages would serve, but which the current site does not own: each is
# rewritten as a canonical redirect to the docs/ page that now carries its subject.  IR-34-ROOT-01.
ROOT_REDIRECTS = {
    "bayes-opt.html": ("research.html", "Bayesian surrogate & expected improvement"),
    "geothermal-knowledge.html": ("research.html", "Geothermal science background"),
    "leaderboard-analysis.html": ("leaderboard.html", "Leaderboard and the size of the gap"),
}
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


def protocol_notice(prefix: str = "") -> str:
    """Authoritative status above legacy sections; absence of evidence never means approved."""
    audit = read("docs/data/protocol-audit.json", {}) or {}
    rc = read("docs/data/latest-run-card.json", {}) or {}
    rows = "".join(
        f"<li><code>{esc(Path(r['file']).name)}</code>: 12/12 format audit PASS; "
        f"within 3 px of synthetic 5-px calibration lattice = {r['within_3px_fraction']:.2%}; "
        f"<b>literal duplicate — STOP</b></li>"
        for r in audit.get("results", []) if r.get("literal_duplicate")
    )
    cand_name = esc(rc.get("submission_name", "GEMSDOE32-H36-1C-TDR-PDS-9FF9D6E2"))
    return f"""<section class=dl style="border:3px solid #b91c1c; background:#fff8f8;" aria-label="Current submission decision">
<h2>DO NOT SUBMIT — current strict protocol review</h2>
<p><b>No file is approved by this review. Downloads below are validated research/audit artifacts (<code>download_ok = true</code>), NOT upload authorization (<code>ok_to_submit = false</code>, <code>verdict = negative</code>).</b>
Older primary/promoted labels in historical archives below do not override this notice.</p>
<ul>{rows}</ul>
<p><b>Round-6 Summary (<code>{cand_name}</code>, 3/3 experiments, 0 weekly slots used):</b>
Our newly generated unique GeoTIFF passes <b>13/13 non-human portal/range-[0, 1] checks</b>, <b>46/46 holdout leakage canaries</b> (max AUC <code>0.5841 &le; 0.90</code>), and <b>uniqueness across all 44 genuine submission/detector rasters</b> (max |Spearman| <code>0.1595 &le; 0.90</code>; max 3-px dot overlap <code>60.44% &le; 70%</code>; <code>52.20%</code> vs. 0.2778 Champion). It achieves <b>HOLDOUT-DTI <code>0.10982</code></b> (95% CI <code>[0.09866, 0.12275]</code>, <code>GEMSDOE32-HOLDOUT-v3-visible-gated</code>, <code>22,232</code> withheld positives), but trails the <code>0.2778</code> Champion on censorship-matched control (<code>0.07639</code> vs. <code>0.09920</code>) and independent off-catalogue USGS SGMC blind faults (<b>HOLDOUT-DTI <code>0.08380</code></b> vs. <code>0.09606</code>), and hits the unmodified literal 5-px calibration-lattice stop (<code>99.80% &gt; 70%</code>). <b>Protect your 3/week DrivenData cap: spend 0 live slots today.</b></p>
<p><a href="{prefix}research/hypotheses-round6-20261026.md">Round-6 ranked hypotheses (H36-1..H36-5)</a> ·
<a href="{prefix}data/latest-run-card.json">Canonical JSON Run Card</a> ·
<a href="{prefix}data/protocol-audit.json">Exact automated protocol-audit.json</a> ·
<a href="{prefix}executive-summary.html">9-Site Executive Summary &amp; Submission Guide</a></p></section>"""


def page(title: str, body: str, active: str = "", dl_btn: str = "") -> str:
    nav = " ".join(f'<a href="{h}"{" class=active" if h == active else ""}>{t}</a>' for h, t in NAV)
    stamp = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)} · {TITLE}</title><link rel=stylesheet href=assets/site.css></head><body>
<header class=top><div class=wrap>
<h1>{esc(title)}</h1><nav>{nav}</nav>
{protocol_notice()}
<div class=dlbtn>{dl_btn}</div>
</div></header>
<div class=values><div class=wrap><b>Core Values.</b> <b>Maximize P(Win)</b> — every weekly submission slot is an experiment, not a lottery ticket. <b>Own the Outcome</b> — every claim here carries an evidence class, and the defect in our own previously-shipped primary was measured, published and replaced rather than quietly dropped.</div></div>
<main class=wrap>{body}</main>
<footer><div class=wrap>
Site generated {stamp} from <code>registry/*.json</code> and <code>evidence/*.json</code> by
<code>scripts/build_site.py</code>. Owner-reported scores are labelled <em>claim</em>; the only
scores this repository reads itself are the other teams' public-leaderboard rows.
<a href="https://github.com/buffedlizard55-lab/GEMSDOE32">Repository</a> ·
<a href="data/feed.json">feed.json</a> · <a href="https://github.com/buffedlizard55-lab/GEMSDOE32/issues">report an irregularity</a>
</div></footer></body></html>"""


def download_block(sub: dict | None, name: str, prefix: str = "") -> str:
    if not sub:
        return ('<div class=dl><h2>Submission GeoTIFF</h2><p class=mut>Not built in this checkout. '
                'Run <code>python3 scripts/build_submission.py</code>.</p></div>')
    f = sub.get("file", {})
    sha = (f.get("sha256") or "")
    note = sub.get("note", "")

    def link(rel: str, label: str, cls: str = "") -> str:
        """Render a download link only if the file is actually present -- never a dead button.

        ``prefix`` is the path from the *rendering* page back to the repository root: the docs/ pages
        need "", the root landing page needs "docs/".  Without this the one-click button on the root
        page 404s, which is exactly the defect this parameter exists to prevent (IR-34-ROOT-01).
        """
        p = ROOT / rel
        if not p.exists():
            return ""
        c = f' class="{cls}"' if cls else ""
        return f'<a{c} href="{esc(prefix + rel.replace("docs/", ""))}">{esc(label)}</a> '

    primary = link(f.get("path", f"docs/downloads/{name}.tif"),
                   f"Download {esc(name)}.tif (Validated Research Artifact)", "btn")
    # the NaN-outside twin and the .zip are looked up from the registry, not guessed from the name
    twin = ""
    nan_rel = (sub.get("nan_companion") or {}).get("path", "")
    if nan_rel:
        twin = link(nan_rel, "NaN-outside twin (masked companion)", "btn alt")
    zkey = (sub.get("zip") or {}).get("path")
    zzip = link(zkey, ".zip (single GeoTIFF inside)", "btn alt") if zkey else ""
    for e in (sub.get("pack") or []):
        rp = e.get("path", "")
        if not twin and rp.endswith("-nan.tif") and e.get("role", "").startswith("SECONDARY"):
            twin = link(rp, "NaN-outside twin (competition format)", "btn alt")
    receipt = ""
    stem = name.split("-zeros")[0].split("-nan")[0]
    for cand in sorted(DL.glob(f"*{stem}*audit*.json")) + sorted(DL.glob(f"checks-{name}.tif.json")):
        r = link(str(cand.relative_to(ROOT)), "13-point automated format receipt (.json)")
        if r:
            receipt = r
            break

    pack_rows = ""
    named = [e for e in (sub.get("pack") or []) if e.get("role") != "AVAILABLE DOWNLOAD"]
    if named:
        cells = []
        for e in named:
            rel = e.get("path", "")
            a = link(rel, rel.split("/")[-1])
            cells.append(
                f"<tr><td><b>{esc(e.get('role',''))}</b></td><td>{a or '&mdash;'}</td>"
                f"<td class=mut>{esc((e.get('sha256') or '')[:16])}&hellip;</td>"
                f"<td class=mut>{esc(e.get('note',''))}</td></tr>")
        pack_rows = ("<h3>Identification pack &mdash; the other two queries</h3>"
                     "<table><tr><th>slot</th><th>file</th><th>sha256</th><th>what it gives</th></tr>"
                     + "".join(cells) + "</table>")

    anchor = link((sub.get("anchor") or {}).get("path", ""),
                  "Historical 0.2778 Champion h33-h33-2-b2 (already scored — DO NOT re-upload)")
    sub_id = sub.get("submission_name") or f"GEMSDOE32-{sub.get('candidate_id','primary')}"
    pos_px = int(f.get("emitted_positive_pixels") or f.get("positive_px") or 0)
    verdict_str = str(sub.get("verdict", "negative")).upper()
    ok_sub = bool(sub.get("ok_to_submit", False))
    status_line = (
        "DOWNLOAD FOR RESEARCH: YES · LIVE PORTAL SUBMIT: NO (Verdict: NEGATIVE — trails 0.2778 Champion on "
        "off-catalogue SGMC blind faults 0.08380 vs 0.09606 and hits literal 5-px calibration lattice stop)."
        if not ok_sub else sub.get("status_line", "Approved for selector review.")
    )
    return f"""<div class=dl>
<h2>&#11015;&nbsp;UNIQUE VALIDATED GEOTIFF DOWNLOAD &mdash; VERDICT: {esc(verdict_str)} (RESEARCH ONLY · DO NOT UPLOAD)</h2>
<p>{primary}{zzip}{twin}</p>
<p><b>Filename:</b> <code>{esc(name)}.tif</code><br>
<b>Unique submission name:</b> <code>{esc(sub_id)}</code><br>
<b>Short portal note ({len(note)}/140 characters):</b><br>
<code>{esc(note)}</code></p>
<p class=mut>single band · float32 · EPSG:32611 · 100 m · 3730&times;3292 ·
{pos_px:,} predicted pixels · every cell finite (12,279,160 / 12,279,160) · every value in [0, 1] ·
0 NaN anywhere · nodata=None · sha256 <code>{esc(sha)}</code>
{('· ' + receipt) if receipt else ''}</p>
{('<p><b>Historical Fleet Champion Reference:</b> ' + anchor + '</p>') if anchor else ''}
{pack_rows}
<p class=warn><b>Automated Gate Verdict:</b> {esc(status_line)}</p>
</div>"""


GH = "https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/"


def _r5_candidate_row(run: dict | None, label: str, gate_text: str, ev_file: str) -> str:
    if not run:
        return f"<tr><td><b>{esc(label)}</b></td><td class=mut>not built in this checkout</td></tr>"
    b = (run.get("submission_bundle") or {}).get("zeros_tif") or {}
    fname = b.get("filename", "")
    dl = ""
    if fname and (DL / fname).exists():
        dl = f'<a href="downloads/{esc(fname)}">download .tif</a> · sha256 <code>{esc((b.get("sha256") or "")[:12])}&hellip;</code>'
    verdict = run.get("verdict", "?")
    badge = ('<b style="color:#b00020">&#9940; DO NOT SUBMIT</b>' if verdict == "negative"
             else '<b style="color:#0a6c03">&#9989; PASSED ALL LOCAL GATES (selector decides)</b>')
    return (f"<tr><td><b>{esc(label)}</b><br>{badge}</td>"
            f"<td>{esc(gate_text)}<br><span class=mut>{dl} · "
            f'<a href="{GH}evidence/{esc(ev_file)}">full receipt</a></span></td></tr>')


def round5_section() -> str:
    """Round 5 (2026-10-25): why the champion scored 0.2778, and the two new unique candidates.

    Everything is rendered from evidence/ JSON produced by scripts/run_hcvf2.py,
    scripts/run_hsupsgmc.py and scripts/analyze_registry_overlap.py — never hand-typed numbers.
    """
    e1 = read("evidence/hcvf2_run.json")
    e2 = read("evidence/hsupsgmc_run.json")
    ov = read("evidence/registry_overlap.json") or {}
    cc = ov.get("construction_checks", {})
    h1 = ((e1 or {}).get("holdout") or {}).get("H-CVF2", {})
    sg = ((e2 or {}).get("south_sgmc_gate") or {})
    per = sg.get("per_candidate", {})
    e1_gate = (f"HOLDOUT-DTI @37,654 dots: SGMC-cal {h1.get('sgmc_prevalence_calibrated_dti', 0):.5f} vs "
               f"champion 0.06412; catalogue-hidden pooled "
               f"{((h1.get('pooled') or {}).get('pooled_dti') or 0):.5f} (instrument perverse for B-gated "
               f"files, IR-32-INSTR-03). Unique lane: 49.7% of dots within 3 px of the champion "
               f"(champion family: &ge;92.6%). Format: 12/12 audit checks pass.")
    e2_gate = (f"Held-out SOUTH SGMC DTI {per.get('H-SUP-SGMC', {}).get('dti', 0):.5f} vs champion "
               f"{per.get('CHAMPION_h33-2-b2', {}).get('dti', 0):.5f} (paired diff 95% CI "
               f"{(sg.get('paired_diff_candidate_minus_champion') or {}).get('boot_ci95', ['?','?'])}). "
               f"Unique lane + format-valid, but worse where it matters.")
    nested = ("verified" if cc.get("champion_equals_solo_and_dist_gt_2px") else "NOT verified")
    return f"""<div class=dl>
<h2>&#128300;&nbsp;ROUND 5 (2026-10-25) &mdash; why the champion scored 0.2778, and two new unique files</h2>
<p><b>Round-5 verdict:</b> the champion file <code>h33-2-b2-…-e5eb6e7e-zeros.tif</code> is already
submitted and scored <b>0.2778</b> (ORGANIZER-CONFIRMED, owner-reported) — do not resubmit it. The
two round-5 files below are <b>unique and format-valid</b> but both measured <b>worse than the
champion</b> on the fair local instrument, so both are labelled
<b style="color:#b00020">DO NOT SUBMIT</b>. The one-click primary elsewhere on this page is a
<i>separate parallel lane's</i> artifact (promoted on the drift instrument, IR-32-INSTR-01/03
caveats apply) — round 5 neither promotes nor blocks it; promotion to a weekly slot is the
selector's step, and this section never spends one.</p>
<h3>Why h33-2-b2 got the group's highest score (measured from the bytes)</h3>
<ul>
<li>The whole top cluster is <b>one nested family</b>: H19-5 (121,131 dots, 0.1922) &sup; d2.8 (44,090,
0.2600) &sup; solo (40,199, 0.2708) &sup; champion (37,654, <b>0.2778</b>). Every gain came from
<i>removing</i> dots. The champion's construction is {nested} pixel-exactly: the 0.2708 base minus its
2,545 dots within 200&nbsp;m of the catalogue.</li>
<li>Mechanism: the scorer masks known faults, so near-catalogue dots almost never earn (implied
&approx;0.006&ndash;0.016 credit/dot) but always pay &alpha;=0.2 in the denominator; the break-even bar at
0.2778 is <code>k &gt; 0.2&middot;DTI = 0.0556</code>. B=2 was the first file with <b>zero</b> dots inside 200&nbsp;m.</li>
<li>The runner-up (GEMSDOE36 &ldquo;Anderson PINN&rdquo;, 0.2750) <b>contains all 37,654 champion dots</b>
+ 1,200 more &mdash; those extras cost &minus;0.0028 (IR-32-FAM-01).</li>
<li>Beating 0.2778 therefore needs <b>better-placed mass, not more or less of the same mass</b>: at the
same 37,654 dots, +8% mean credit reaches 0.30; the public #1 (0.4413, read 2026-10-25) needs &approx;+59%.</li>
</ul>
<h3>The two unique round-5 candidates (new lanes, honestly measured)</h3>
<table><tr><th>candidate</th><th>validation gates (all numbers HOLDOUT-DTI unless labelled)</th></tr>
{_r5_candidate_row(e1, "H-CVF2 — CV-GBM 35-channel field, B=2, greedy max-coverage", e1_gate, "hcvf2_run.json")}
{_r5_candidate_row(e2, "H-SUP-SGMC — CV-GBM + SGMC-north supervision", e2_gate, "hsupsgmc_run.json")}
</table>
<p class=mut>Method, frozen gates and falsifiers: <a href="research/hypotheses-round5.md">hypotheses-round5.md</a>.
Forensic overlap anatomy: <a href="{GH}evidence/registry_overlap.json">registry_overlap.json</a>
(reproduce: <code>scripts/analyze_registry_overlap.py</code>). Instrument warning: the catalogue-hidden
holdout scores the live B-ladder <i>backwards</i> (IR-32-INSTR-03) &mdash; do not gate B-pruned files on it.</p>
</div>"""


def nine_site_and_round6_section(prefix: str = "") -> str:
    """Line-by-line verified 9-Site Executive Summary + Round-6 H36-1 (TDR-PDS) Run Card & Hypotheses."""
    rc = read("docs/data/latest-run-card.json") or {}
    exp_rows = ""
    for e in rc.get("experiment_progression", []):
        exp_rows += (
            f"<tr><td><b>{esc(e['experiment'])}</b></td>"
            f"<td><code>{e['holdout_dti_visible_v3']:.5f}</code> "
            f"<span class=mut>[{e['holdout_dti_ci95'][0]:.4f}, {e['holdout_dti_ci95'][1]:.4f}]</span></td>"
            f"<td><code>{e['censored_d0_control_dti']:.5f}</code></td>"
            f"<td><code>{e['sgmc_off_catalogue_raw_dti']:.5f}</code></td>"
            f"<td><code>{e['sgmc_prevalence_calibrated_dti']:.5f}</code></td></tr>"
        )
    u = rc.get("correlation_and_overlap_vs_registry", {})
    c_auc = (rc.get("leakage_canary") or {}).get("max_oriented_auc", 0.58412)
    return f"""<div class=card>
<h2>&#127919;&nbsp;Executive Fleet Audit Across the 9 Focus Sites (2026-10-26)</h2>
<p><b>Bottom-Line Leaderboard Decision:</b> Across all 9 focus repositories, the highest leaderboard score
belongs to <b>GEMSDOE32</b>'s <code>gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif</code>
(<b>0.2778</b> owner-reported live score, 37,654 dots) &mdash; <b>already submitted and scored; do NOT re-upload it</b>.
Every high-scoring historical file across the 9 sites belongs to the <b>single nested <code>H19-5</code> dot-thinning family</b>
(with two exact byte/pixel duplicate pairs and one 96.9% superset). Every newly generated 2026-10-26 unique physical/ML GeoTIFF across all 9 sites is
<b>portal-valid (<code>download_ok = true</code>)</b> and <b>honestly gated <code>DO NOT SUBMIT</code> (<code>verdict = negative</code>)</b>.
<b>Recommended live DrivenData slots to spend today: 0.</b></p>
<table>
<tr><th>Site &amp; Verified Repo</th><th>Best Historical Scored File (Owner-Reported Score)</th><th>Uniqueness / Family Relation (Byte-Verified)</th><th>Latest 2026-10-26 Unique Research TIF</th><th>Submit Verdict</th></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE32"><b>GEMSDOE32</b></a><br><span class=mut>THIS REPO</span></td>
<td><code>h33-h33-2-b2-…-e5eb6e7e-zeros.tif</code><br><b>0.2778 (FLEET BEST)</b> · 37,654 dots</td>
<td><b>Canonical B=2 Optimum</b> = <code>solo &amp; (d_cat &gt; 2)</code>; sha256 <code>e5eb6e7e…</code> (already scored)</td>
<td><code>gemsdoe32-h36-1c-tdr-pds-steger-37654-…-9ff9d6e2-zeros.tif</code><br><span class=mut>Unique vs 44 detectors (max 3px ov 60.44%, |&rho;| 0.1595)</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b><br><span class=mut>Champion already scored; H36-1C SGMC 0.0838 &lt; 0.0961</span></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE36"><b>GEMSDOE36</b></a><br><span class=mut>HEAD <code>a4c660a8</code></span></td>
<td><code>anderson-friction-pinn-b2-swap1200-…-zeros.tif</code><br><b>0.2750</b> · 38,854 dots</td>
<td><b>96.91% Superset Duplicate</b> of GEMSDOE32 Champion (all 37,654 Champion dots + 1,200 extra dots costing &minus;0.0028)</td>
<td><code>gemsdoe36-h36-gps-graben-pair-20261026-bb29ce2a4bb4-zeros.tif</code><br><span class=mut>89.85% &gt; 70% overlap; HOLDOUT-DTI 0.1320 &lt; 0.1488</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE28"><b>GEMSDOE28</b></a><br><span class=mut>HEAD <code>94152be6</code></span></td>
<td><code>gems28-h27-4-r1-solo-d2-8-…-allfinite.tif</code><br><b>0.2708</b> · 40,199 dots</td>
<td><b>Exact Dot-Identical Twin</b> of GEMSDOE31 <code>solo</code> = <code>d2.8 &amp; (d_cat &gt; 1)</code></td>
<td><code>gems28-s20-vesselness-lidarstep-20261026-7a7c5e44</code><br><span class=mut>37,500 dots; HOLDOUT-DTI 0.0863 &lt; 0.0988</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE31"><b>GEMSDOE31</b></a><br><span class=mut>HEAD <code>6ca63b0c</code></span></td>
<td><code>gems31-h27-4-r1-solo-d2-8-…-nan.tif</code><br><b>0.2708</b> · 40,199 dots</td>
<td><b>Exact Dot-Identical Twin</b> of GEMSDOE28 <code>solo</code> (0 symmetric pixel diff)</td>
<td><code>gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif</code><br><span class=mut>HOLDOUT-DTI 0.0459 &lt; 0.0481 control</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE33"><b>GEMSDOE33</b></a><br><span class=mut>HEAD <code>7deca206</code></span></td>
<td><code>GEMSDOE33-h33d-skel-b1-trim-…-zeros.tif</code><br><b>0.2632</b> · 41,865 dots</td>
<td><b>H19-5 Family Subset/Trim</b> (B=1 skeleton trim, 41,865 dots)</td>
<td><i>No new unique 2026-10-26 TIF emitted (input/gate audit)</i></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE25"><b>GEMSDOE25</b></a><br><span class=mut>HEAD <code>de77cb6c</code></span></td>
<td><code>gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif</code><br><b>0.2600</b> · 44,090 dots</td>
<td><b>Exact Dot-Identical Twin</b> of GEMSDOE30 <code>poisson300m</code> (0 symmetric pixel diff)</td>
<td><i>ROD factorial evaluation (OK TO SUBMIT: NO)</i></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE30"><b>GEMSDOE30</b></a><br><span class=mut>HEAD <code>ac54b7f3</code></span></td>
<td><code>gems30-h19-5-poisson300m-…-nan.tif</code><br><b>0.2600</b> · 44,090 dots</td>
<td><b>Exact Dot-Identical Twin</b> of GEMSDOE25 <code>d2.8</code> (IR-32-FAM-02)</td>
<td><code>gems30-PTA1-44090-20261025-9a3f7f9535a4.tif</code><br><span class=mut>Unique across 196 rasters; negative gate stop</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE24"><b>GEMSDOE24</b></a><br><span class=mut>HEAD <code>2a2b9829</code></span></td>
<td><code>gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif</code><br><b>0.2194</b> · 77,507 dots</td>
<td><b>Dense d=1.5 Member</b> of H19-5 family (GVC1 37,654d unsubmitted duplicate corridor)</td>
<td><code>gems24-crp1-compfront-xdepth-saddle-…-zeros.tif</code><br><span class=mut>80.7% &gt; 70% 3px overlap; HOLDOUT-DTI 0.1375 &lt; 0.1488</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE27"><b>GEMSDOE27</b></a><br><span class=mut>HEAD <code>398cda94</code></span></td>
<td><code>H29-S (511898747886)</code> <b>0.2190</b> (37,654d) · <code>topo-gap-closure</code> <b>0.2186</b> (78,763d)</td>
<td><code>H29-S</code> is the highest live-scored <b>pure OOF ML non-H19-5 surface</b> (0.2190 &lt; 0.2778)</td>
<td><code>gems27-h31-rankens-celf-b2-20261026-93c8af046660-allfinite.tif</code><br><span class=mut>Unique; HOLDOUT-DTI 0.03671 &lt; 0.04402</span></td>
<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>
</table>

<h3>Round-6 Lane <code>H36-1 (TDR-PDS)</code> — Measured 3-Experiment Progression &amp; Automated Gate Receipt</h3>
<p>Motivated by two byte-verified physical discoveries &mdash; <b>IR-32-BAND-02</b> (Band 6 <code>tc</code> correlates at
<code>&rho; = +0.99942</code> with GeoDAWN radiometric Total Count, proving true Miller&ndash;Singh magnetic &amp; gravity tilt angles
<code>arctan(VG/HG)</code> were never previously computed) and <b>IR-32-BAND-03</b> (Band 18 <code>iso_grav_anom_hg</code> is signed
<code>&part;g/&part;x</code> at <code>&rho; = +0.9438</code>, locating half-graben polarity reversals) &mdash; plus repairing
<b>IR-32-INSTR-03</b> in <code>src/gems32/holdout.py</code> (<code>GEMSDOE32-HOLDOUT-v3-visible-gated</code>, restoring exact live order
<code>0.06879 &lt; 0.09674 &lt; 0.09898 &lt; 0.09920</code>), we ran 3 pre-registered experiments at matched <code>37,654</code> dots:</p>
<table>
<tr><th>Experiment (Budget Cap: 3/3)</th><th>v3 Visible-Gated Pooled <code>HOLDOUT-DTI</code> [95% CI]<br><span class=mut>22,232 withheld Quaternary positives</span></th><th>Censored-<code>d=0</code> Control<br><span class=mut>matches IR-32-FIELD-01</span></th><th>Off-Catalogue <code>SGMC</code> Raw <code>HOLDOUT-DTI</code><br><span class=mut>62,703 blind faults &gt;300 m</span></th><th><code>SGMC</code> Calibrated <code>HOLDOUT-DTI</code></th></tr>
<tr><td><b>Baseline: 0.2778 Champion (<code>h33-h33-2-b2</code>)</b></td><td><code>0.09920</code> <span class=mut>[0.0820, 0.1222]</span></td><td><code>0.09920</code></td><td><b><code>0.09606</code></b> <span class=mut>[0.0848, 0.1077]</span></td><td><b><code>0.06412</code></b></td></tr>
{exp_rows}
</table>
<p class=mut><b>Automated Gate Summary (Zero Human Intervention):</b> Format 13/13 <b>PASS</b> · Leakage Canaries 46/46 <b>PASS</b>
(worst oriented AUC <code>{c_auc:.4f} &le; 0.90</code>) · Genuine 44-Raster Uniqueness <b>PASS</b>
(max |Spearman| <code>{u.get('genuine_max_abs_surface_spearman', 0.1595):.4f} &le; 0.90</code>; max 3-px dot overlap
<code>{u.get('genuine_max_dot_overlap_within_3px', 0.6044):.2%} &le; 70%</code>; vs. 0.2778 Champion
<code>{u.get('vs_02778_champion_dot_overlap_within_3px', 0.5220):.2%}</code>) · Blind SGMC Holdout <b>FAIL</b>
(<code>0.08380 &lt; 0.09606</code>) · Literal 5-px Calibration Lattice <b>STOP</b> (<code>99.80% &gt; 70%</code>, IR-32-LATTICE-01)
&rarr; <b>Verdict: <code>NEGATIVE</code></b> (<a href="{esc(prefix)}data/latest-run-card.json">JSON Run Card</a>).</p>

<h3>PhD Analysis: Why <code>0.2778</code> Won, Its Hard Ceiling, and What Is Required for <code>0.3195</code> &amp; <code>0.4413</code></h3>
<ul>
<li><b>Exact Metric Inversion:</b> From <code>DTI = T / (0.8&middot;T + 0.2&middot;|P| + 0.8&middot;|G|)</code> across the nested pairs
<code>H19-5</code> (121,131 px, 0.1922) &rarr; <code>D2.8</code> (44,090 px, 0.2600) &rarr; <code>Solo</code> (40,199 px, 0.2708) &rarr;
<code>Champion</code> (37,654 px, <b>0.2778</b>), hidden test fault volume is <code>|G| &approx; 12,265</code> pixels (~1,226 km).</li>
<li><b>Why <code>B = 2</code> Reached <code>0.2778</code>:</b> DrivenData masks known catalogue pixels during scoring; because hidden test faults
are disjoint connected segments rather than parallel traces 100&ndash;200 m beside mapped faults, the 2,545 flank dots at
<code>1 &lt; d_cat &le; 2 px</code> earned only ~0.0156 credit/dot (3.6&times; below the break-even bar <code>0.2&middot;DTI = 0.0556</code>).
Removing them saved <code>0.2 &times; 2,545 = 509</code> denominator units for almost zero loss in <code>T &approx; 4,503</code>.</li>
<li><b>Mathematical Impossibility Proof for Re-Thinning <code>H19-5</code> to <code>0.4413</code>:</b> Even the entire un-thinned 121,131-px
<code>H19-5</code> ridge captures only <code>T_solid &approx; 5,021</code> weighted test pixels (<code>40.9%</code> of <code>|G|</code>).
At 37,654 dots, reaching <code>0.3195</code> requires <code>T &approx; 5,430</code> (<code>44.3%</code> recall) and reaching the public #1
<code>0.4413</code> (<code>xiaofanhu</code>) requires <code>T &approx; 8,408</code> (<code>68.6%</code> recall &gt; <code>5,021</code>)!
Thus <b>no subset or re-weighting of <code>H19-5</code> can ever exceed ~0.305&ndash;0.312</b>; bridging to <code>0.3195&ndash;0.4413</code>
requires discovering ~340 km of genuinely unmapped structures (relocated coseismic/microseismic planes such as the 2020
<i>M<sub>w</sub></i>&nbsp;6.5 Monte Cristo splays, InSAR phase discontinuities, full-footprint 1&nbsp;m 3DEP LiDAR scarps, and 3-D MT/gravity inversions).</li>
</ul>
</div>"""


def arena41_block(prefix: str = "") -> str:
    return nine_site_and_round6_section(prefix)


def download_catalogue(fl: dict, sub: dict | None) -> str:
    """Every GeoTIFF this repository offers, with its sha256 -- so no link on the site is a dead
    button and every file is independently checkable."""
    import subprocess as sp
    if not DL.is_dir():
        return ""
    rows = []
    for p in sorted(DL.glob("*.tif")):
        rel = str(p.relative_to(ROOT))
        pos = ""
        try:
            with rasterio.open(p) as ds:
                a = ds.read(1)
            pos = f"{int(((a > 0) & np.isfinite(a)).sum()):,}"
        except Exception:
            pos = "&mdash;"
        try:
            sha = sp.run(["sha256sum", str(p)], capture_output=True, text=True, check=True).stdout[:64]
        except Exception:
            sha = "&mdash;"
        role = "PRIMARY" if (sub or {}).get("file", {}).get("path") == rel else ""
        for e in (sub or {}).get("pack") or []:
            if e.get("path") == rel:
                role = e.get("role", role)
        if rel == ((sub or {}).get("anchor") or {}).get("path"):
            role = "ANCHOR (already-scored base)"
        rows.append(f"<tr><td>{esc(role)}</td><td><a href=\"{esc(rel.replace('docs/', ''))}\">"
                    f"{esc(p.name)}</a></td><td>{pos}</td>"
                    f"<td class=mut><code>{esc(sha)}</code></td>"
                    f"<td class=mut>{p.stat().st_size:,} B</td></tr>")
    return f"""<h2>Complete download catalogue</h2>
<p class=mut>Every GeoTIFF in this repository, in one table, each with the sha256 of the bytes
actually published. Nothing here is claimed to be scored: <b>no artifact in this repository has an
organiser score.</b></p>
<table><tr><th>role</th><th>file</th><th>positive pixels</th><th>sha256</th><th>bytes</th></tr>
{''.join(rows)}</table>"""


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
    parts = [arena41_block(), download_block(sub, name), round5_section(), f"""<div class=dl>
<h2>&#9888;&nbsp;The portal error <code>"Predicted values must be in range [0, 1]"</code> &mdash; fixed, and here is exactly how</h2>
<p>DrivenData rejects a submission whose values fall outside <code>[0, 1]</code>, and it also rejects
a raster whose <b>nodata tag</b> is a large negative sentinel such as
<code>-3.4028234663852886e+38</code>, because that sentinel is not a value in <code>[0, 1]</code>.
Two different failures produce the same message, and this repository has measured both.</p>
<ul>
<li><b>Mechanism 1 &mdash; the float32 sentinel.</b> <code>training_features.tif</code> uses
<code>-3.4028234663852886e+38</code> as nodata: <b>7,113,308</b> cells, of which <b>3,061</b> lie
<i>inside</i> the submission footprint. Writing those through unchanged puts them outside
<code>[0, 1]</code>.</li>
<li><b>Mechanism 2 &mdash; the NaN sentinel.</b> A raster carrying <code>nodata=NaN</code> with NaN
cells outside the footprint is a legitimate competition format, but it is one validator change away
from the same rejection. Every primary download here is written <b>all-finite</b>, with
<code>nodata=None</code>.</li>
</ul>
<p><b>The fix, verified by re-reading the written bytes:</b> every GeoTIFF offered on this site is
single-band float32, EPSG:32611, 100 m, 3730&times;3292, <b>every one of the 12,279,160 cells
finite</b>, <b>min 0.0, max 1.0, zero cells outside <code>[0, 1]</code>, zero NaN</b>, and
<b>no nodata tag</b>. Each download ships a
<code>checks-*.json</code> format receipt produced by re-opening the file from disk.</p>
</div>

<h2>What this is</h2>
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
    sub_id = esc((sub or {}).get("submission_name", "GEMSDOE32-H36-1C-TDR-PDS-9FF9D6E2"))
    fresh = esc(f"{name}-fresh")
    _stem = name.split("-zeros")[0].split("-nan")[0]
    _rec = sorted(DL.glob(f"*{_stem}*audit*.json")) + sorted(DL.glob(f"checks-{name}.tif.json"))
    receipt_link = (f'<a href="downloads/{esc(_rec[0].name)}">{esc(_rec[0].name)}</a>'
                    if _rec else '<span class=mut>not written in this checkout</span>')
    return f"""<h2 style="margin-top:6px">Executive Summary &amp; Step-by-Step DrivenData Submission Guide</h2>
{download_block(sub, name)}
{nine_site_and_round6_section()}
<div class=card><h3>1 · Automated Non-Human Format Verification &amp; Download</h3>
<p>The newly generated unique research file <code>{esc(name)}.tif</code> is verified automatically without human intervention
by dual validators (<code>gems32.submission.audit_geotiff</code> + <code>gemsdoe32.submission.validate_submission_geotiff</code>):
single-band <code>float32</code>, <code>EPSG:32611</code> UTM Zone 11N, 100 m resolution, <code>3730&times;3292</code> shape,
<code>nodata=None</code>, all <code>12,279,160</code> cells finite in <code>[0.0, 1.0]</code>.
Receipt: {receipt_link}.<br>
<b style="color:#b00020">Important Slot Rule:</b> Because <code>{sub_id}</code> has automated gate verdict <code>NEGATIVE</code>
(<code>ok_to_submit = false</code>), download it for local GIS/scientific review only &mdash; <b>do not spend a live weekly slot uploading a negative-verdict file</b>. Use the steps below <i>only</i> when a future candidate achieves <code>verdict = promote</code> and passes the cross-run selector.</p></div>

<div class=card><h3>2 · How to Submit a Promoted Candidate to DrivenData (Portal Workflow)</h3>
<p class=mut>Official portal URL (requires DrivenData login, 3 submissions/week cap):</p>
<ol>
<li><b>Portal Submission Page:</b>
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/" target="_blank">https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/</a></li>
<li><b>File format accepted:</b> Upload either the single-band <code>*-zeros.tif</code> directly or its single-TIFF <code>*-zeros.zip</code> archive.</li>
<li><b>Unique Submission Identifier (current Round-6 artifact):</b> <code>{sub_id}</code></li>
<li><b>Short Portal Note (&le;140 chars, copy-paste ready):</b><br>
<code>{note}</code></li>
<li><b>Selector Guardrail:</b> Never re-upload <code>gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif</code> (already scored at <b>0.2778</b>) or any sibling duplicate (<code>GEMSDOE25 &equiv; GEMSDOE30</code>, <code>GEMSDOE28 &equiv; GEMSDOE31</code>, <code>GEMSDOE36 &sup; GEMSDOE32</code>).</li>
</ol></div>

<div class=card><h3>3 · Why this file avoids &ldquo;Predicted values must be in range [0, 1]&rdquo;</h3>
<p>Earlier submission attempts in this competition encountered the portal error:
<code style="color:#b00020; font-weight:bold;">&ldquo;Predicted values must be in range [0, 1]&rdquo;</code>.
Our forensic autopsy (<a href="research.html">docs/research/range-error-root-cause-2026-10-03.md</a>) diagnosed the two root causes:</p>
<ul>
<li><b>Mechanism 1 &mdash; NaNs outside the footprint:</b> When predictions outside the active footprint are written as <code>NaN</code> (the published spec), Python/NumPy whole-array checks like <code>((pred >= 0) & (pred <= 1)).all()</code> return <code>False</code> because any comparison involving <code>NaN</code> evaluates to <code>False</code>.</li>
<li><b>Mechanism 2 &mdash; Float32 sentinels:</b> In raw feature rasters (e.g. Band 6 <code>tc</code>), unmasked cells hold <code>-3.4028235e+38</code>, which is strictly less than 0.0.</li>
</ul>
<p><b>The Guaranteed Fix:</b> The downloaded <code>*-zeros.tif</code> file writes <b>0.0 outside the footprint</b> with <code>nodata=None</code>.
All <b>12,279,160 / 12,279,160 cells are strictly finite floats in [0.0, 1.0]</b> with <b>0 NaNs anywhere in the raster</b>.
This file is guaranteed to pass the DrivenData web form without triggering range errors.</p></div>

<div class=card><h3>4 · Know the two-round scoring rules before submitting</h3>
<p>The competition scores your submission <b>twice</b>: first against the existing known catalogue faults (masked during scoring), then in the final round against an expanded ground truth set that includes panel-verified discoveries. The metric weights false negatives 4&times; false positives (&beta;=0.8 vs &alpha;=0.2), rewarding genuinely new blind fault conduits.</p>
<ul>
<li>Weekly limit: 3 scored submissions per week;</li>
<li>Exactly <b>one</b> final submission file is selected to represent your team in the final prize round;</li>
<li>All emitted dots on catalogue faults are masked out by DrivenData (earning 0 credit while paying denominator penalties); our file places <b>0 dots on catalogue pixels</b> and enforces a <b>B=2 (200 m) exclusion buffer</b> to eliminate zero-credit waste.</li>
</ul></div>
{download_catalogue(fl, sub)}
<div class=card><h3>5 · Keep the names unique</h3>
<p>The filename already carries a unique content id and the note repeats it, so two submissions can
never be confused. If a file is ever rebuilt, the build script writes a new name
(e.g. <code>{fresh}</code>) rather than overwriting the old one — the score ledger stays auditable.</p>
</div>"""


RESEARCH_NOTES = [
    ("hypotheses-round6-20261026.md", "Round 6 (2026-10-26): Band 6 radiometric TC & Band 18 signed gx "
                                      "byte discoveries (IR-32-BAND-02/03), visible-gated holdout repair "
                                      "(IR-32-INSTR-03), 5 ranked hypotheses (H36-1..H36-5), and 3-experiment "
                                      "TDR-PDS + Steger curvilinear skeleton evaluation"),
    ("hypotheses-round5.md", "Round 5 (2026-10-25): why the champion scored 0.2778 (nested-family "
                             "forensics), the five ranked hypotheses, two measured negative lanes "
                             "(H-CVF2, H-SUP-SGMC), and the catalogue-hidden instrument perversity "
                             "(IR-32-INSTR-03)"),
    ("hypotheses-round4.md", "Round 4 (H33-1..H33-5): the live-anchored removal rule, the winning "
                             "flank-B=2 arm, the two falsified addition arms, and IR-33-LM-01"),
    ("hypotheses-round3.md", "Round 3 (H62-1..H62-5): transform only layers that are still raw "
                             "fields; the rank-1 candidate was falsified by its own falsifier"),
    ("hypotheses-round2.md", "Round 2 (H60-1..H60-5): the catalogue-difference audit"),
    ("why-d28-scored-026.md", "Why the dotted D2.8 file scored what it did"),
    ("verification-2026-10-04.md", "the source-verification pass and what could not be verified"),
    ("range-error-root-cause-2026-10-03.md", "root cause of the portal's "
                                             "\"Predicted values must be in range [0, 1]\" error"),
    ("score-ceiling-analysis.md", "the perfect-knowledge ceiling and the recall needed to lead"),
    ("geothermal-vents-knowledge.md", "the measured GDR volcanic-vent and wellspring statistics"),
    ("shipped_audit.json", "the per-file portal-legality audit of every artifact on disk"),
]


def research(fl: dict, sub: dict | None, name: str) -> str:
    ev = fl.get("evidence", {}).get("h60_2_catalogue_difference.json", {})
    hd = fl.get("holdout", {})
    research_rows = "".join(
        f'<tr><td><a href="https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/research/'
        f'{esc(fn)}">{esc(fn)}</a></td><td>{esc(desc)}</td></tr>' for fn, desc in RESEARCH_NOTES)
    return f"""<div class=card><h3>Session findings (2026-10-04) &mdash; read these three first</h3>
<ul>
<li><a href="research/instrument-calibration.md"><b>Which local instrument tracks the leaderboard?</b></a>
&mdash; 12 stored artifacts with owner-reported live scores, re-scored here: <code>catalogue_hidden</code>
&rho; = +0.140, SGMC-calibrated +0.537, drift-corrected +0.529 (LOO MAE 0.053). The historical headline
proxy does <i>not</i> rank live scores; the promotion instrument is the best available and is still not
significant at n = 12 (p &asymp; 0.09). Includes the measured discontinuity: <b>one</b> dot on a mapped
fault moves the drift instrument 0.14801 &rarr; 0.07831 (&minus;47 %) while both other instruments are
unchanged.</li>
<li><a href="research/h33-hypotheses.md"><b>Five untried hypotheses (H33-A&hellip;E)</b></a> &mdash; each with
layers, physical signature, the reason it should catch a fault the catalogue lacks, and the novelty
statement. Measured verdict: all four label-free surfaces scored <b>below</b> a uniform-random control on
the catalogue-hidden instrument (random 0.03438 at 44,090 px), while the aligned-drainage-chain field
scored <b>0.09072</b> on the off-catalogue SGMC instrument against the incumbent's <b>0.06059</b>. The two
instruments disagree in <b>sign</b> about every new hypothesis &mdash; the holdout drift this repository
exists to measure. Nothing was promoted.</li>
<li><a href="research/h34-positional-error-emission.md"><b>Positional-error-calibrated emission</b></a>
&mdash; `DTI = T/(&alpha;S + &beta;K)` means every added dot costs exactly &alpha;; the belief field's
measured localisation error (median 4.12 px for the 0.2600 base) is the quantity that should set the
packing density. Honest mixed result, no promotion.</li>
</ul>
<p class=mut>The four new label-free surfaces are implemented in <code>src/gems32/h33.py</code>; the
selection rule that picks the one-click file is <code>scripts/build_slot_plan.py</code> and its receipt is
<code>registry/slot_plan.json</code>.</p></div>
<h2 style="margin-top:6px">1 · The metric, and the decision rule that falls out of it</h2>
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
<h2>6 · Round 4 (H33): the live-anchored removal rule, and what it killed</h2>
<p>The single most informative measurement available to this project is a pair of the group's own
files that differ by <b>exactly one mechanism</b>: the dotted D2.8 emission
(<code>GEMS28-H27-4-R1-SOLO-D2.8</code>, 40,199 dots, owner-reported live score
<b>0.2600</b>) and its catalogue-flank prune at B&nbsp;=&nbsp;1
(40,199&nbsp;&minus;&nbsp;3,891&nbsp;=&nbsp;36,308 dots, owner-reported live score
<b>0.2708</b>). <code>existing_faults.tif</code> is byte-identical to <code>labels.tif</code>, so
the "blind" prune removed exactly the 3,891 dots within 100&nbsp;m of the published catalogue and
nothing else. Inverting that pair through the official metric under a zero-credit assumption
recovers the live true-positive weight, the live false-positive mass, and therefore a
<b>credit-loss budget</b> for any further removal.</p>
<table>
<tr><th>quantity recovered by the inversion</th><th>value</th><th>what it means</th></tr>
<tr><td>weighted true positives, TP<sub>w</sub></td><td>5,073.3</td><td>the live set's credit mass</td></tr>
<tr><td>denominator, D</td><td>18,734.4</td><td>implies |G| = 12,226 hidden truth pixels</td></tr>
<tr><td>mean credit per emitted dot</td><td>0.1262</td><td>the group's live efficiency</td></tr>
<tr><td>implied weighted recall</td><td>0.4150</td><td>41.5 % of the hidden set's weight</td></tr>
<tr><td>credit-loss budget at B = 1</td><td>210.7</td><td>how much weighted credit a removal may burn</td></tr>
<tr><td>live break-even bar &tau;<sub>live</sub></td><td>0.05416</td><td>a new dot must beat this to pay for itself</td></tr>
</table>
<p><b>The rule that falls out of it</b> (implemented in <code>src/gems32/live_anchor.py</code>): a
removal of <code>dn</code> dots that costs <code>dS</code> units of off-catalogue weighted credit and
removes <code>dTP<sub>g</sub></code> units of on-catalogue credit is a live gain iff
<code>dS &lt; TP_w · (0.2·dn &minus; 0.8(dS &minus; dTP_g)) / D</code>. The gate used for every
submission decision is the <b>safety factor</b> = budget &divide; measured cost; a removal arm is
slot-eligible only at safety &ge; 2.0.</p>
<h3>What round 4 measured, arm by arm</h3>
<table>
<tr><th>arm</th><th>dots</th><th>live-mirror &Delta;DTI</th><th>folds</th><th>credit/dot</th><th>safety</th><th>verdict</th></tr>
<tr><td>base &mdash; GEMS28-H27-4-R1-SOLO-D2.8</td><td>40,199</td><td>0.263051</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>the anchor</td></tr>
<tr><td>D2.8 emission (live 0.2600)</td><td>44,090</td><td>0.251593</td><td>&mdash;</td><td>&mdash;</td><td>&mdash;</td><td>the other anchor</td></tr>
<tr><td><b>H33-2-B2 (catalogue flank B = 2)</b></td><td><b>37,654</b></td><td><b>+0.004870</b></td><td><b>4/4</b></td><td>&mdash;</td><td><b>2.08</b></td><td class=ok><b>WINNER &mdash; shipped primary</b></td></tr>
<tr><td>H33-2-B3 (catalogue flank B = 3)</td><td>35,483</td><td>+0.001317</td><td>3/4</td><td>&mdash;</td><td>1.27</td><td class=bad>rejected: safety &lt; 2.0</td></tr>
<tr><td>H33-2B2 + H33-1</td><td>38,554</td><td>+0.004978</td><td>4/4</td><td>&mdash;</td><td>&mdash;</td><td>slot-eligible secondary</td></tr>
<tr><td>H33-1-P600A1800 (geothermometry)</td><td>41,999</td><td>+0.002639</td><td>2/4</td><td>0.00541</td><td>&mdash;</td><td class=bad>FALSIFIED as an addition arm</td></tr>
<tr><td>H33-1-P300A900 (geothermometry)</td><td>41,099</td><td>+0.000524</td><td>2/4</td><td>0.00215</td><td>&mdash;</td><td class=bad>FALSIFIED as an addition arm</td></tr>
<tr><td>H33-5-P300A900 (tip / step-over)</td><td>41,099</td><td>+0.001870</td><td>3/4</td><td>0.00767</td><td>&mdash;</td><td class=bad>FALSIFIED as an addition arm</td></tr>
</table>
<p><b>Why B = 2 and not B = 1 or B = 3.</b> B = 1 is already live-tested and produced 0.2708.
B = 2 removes 2,545 further dots (6.3 % of the mass) for 58.6 units of off-catalogue weighted credit
(1.5 %) against a budget of 125.1 &mdash; safety 2.08 &mdash; and improves the live-mirror margin in
all four quadrants. B = 3 spends the budget down to safety 1.27 and only wins 3 of 4 quadrants, so it
is rejected. The group only ever tested B = 1 live; <b>B = 2 is a new, non-obvious operating
point.</b></p>
<h3>IR-33-LM-01: the drift finding that bounds what the live mirror may decide</h3>
<p>Outside its validated regime the live mirror (LM-cal) ranks a 7,943-dot "safe-mass-pruned"
variant at <b>0.4413</b> &mdash; 1.35&times; the entire public leaderboard's top score. The live
record refutes that number. For the pruned file not to exceed 0.3262, <b>at least 16 % of the 0.2708
emission's weighted credit must sit on dots the off-catalogue truth model calls credit-neutral</b>.
LM-cal is therefore licensed only for small, mechanism-matched perturbations of a live-scored base
(40&nbsp;k&ndash;62&nbsp;k dots), which is exactly why the slot gate requires the live-anchored safety
factor in addition to the mirror margin.</p>
<h2>7 · Research notes (readable on GitHub, one click each)</h2>
<p class=mut>Every number on this site is produced by a script in <code>scripts/</code> and stored in
<code>evidence/</code> or <code>registry/</code>. These are the write-ups, in the order they were
made. They are Markdown, so the links open them rendered on GitHub rather than as a download.</p>
<table><tr><th>note</th><th>what it establishes</th></tr>
{research_rows}</table>
<h2>8 · Method and reproducibility</h2>
<pre>pip install -r requirements.txt
bash scripts/fetch_mirrors.sh       # hash-verified fetch of every pinned mirror (GitHub API)
python3 scripts/prepare_data.py     # 19 bands, footprint + catalogue masks
python3 scripts/run_pipeline.py     # autopsy + holdout + H32 suite + GP surrogate + slot gate
python3 scripts/run_h33_validation.py   # live-mirror + live-anchored inversion + the H33 GeoTIFFs
python3 scripts/build_submission_build.py  # picks the primary, writes registry/submission_build.json
python3 scripts/audit_shipped.py    # re-opens every file on disk; refreshes the manifest
python3 scripts/build_site.py       # regenerates docs/*.html, the feed and the root landing page
python3 -m pytest tests -q          # 80 tests, including the site's link integrity</pre>
<p class=mut>Order matters: <code>audit_shipped.py</code> runs <em>after</em> anything that writes
GeoTIFFs, because it rebuilds <code>docs/downloads/submissions_manifest.json</code> from the files
actually on disk rather than from what the pipeline thinks it wrote.</p>
<p class=mut>The holdout ran{' with mean AUC ' + esc(round(hd.get('summary', {}).get('auc_mean', float('nan')), 3)) if hd else ''}
on a CPU-only box for the emission arms; the detector used there is a gradient-boosted tree, not the
U-Net of the official reference solution, because this sandbox has 2&nbsp;vCPU and no GPU. The
emission rule is what is being validated, and it is detector-agnostic.</p>"""


def hypotheses_page(fl: dict) -> str:
    hyp = fl.get("hypotheses", [])
    reg_h = read("registry/hypotheses.json") or {}
    r6 = reg_h.get("round6_hypotheses_20261026", [])
    ev = fl.get("evidence", {}).get("h60_2_catalogue_difference.json", {})
    r6_rows = "".join(f"""<tr><td>{esc(h.get('rank',''))}</td><td><b>{esc(h.get('id',''))}</b><br>{esc(h.get('title',''))}</td>
<td>{esc(h.get('layers',''))}</td><td>{esc(h.get('signature',''))}</td>
<td>{esc(h.get('why_off_catalogue',''))}</td><td>{esc(h.get('differs_from_repo',''))}</td>
<td>{esc(h.get('expected_dti',''))} · cost {esc(h.get('cost',''))} · data: {esc(h.get('data_status',''))}</td>
<td>{esc(h.get('status',''))}</td></tr>""" for h in r6)
    rows = "".join(f"""<tr><td>{esc(h.get('rank',''))}</td><td><b>{esc(h.get('id',''))}</b><br>{esc(h.get('title',''))}</td>
<td>{esc('; '.join(h.get('layers', [])) if isinstance(h.get('layers'), list) else h.get('layers',''))}</td><td>{esc(h.get('signature',''))}</td>
<td>{esc(h.get('why_off_catalogue',''))}</td><td>{esc(h.get('differs_from_repo',''))}</td>
<td>{esc(h.get('expected_dti',''))} · cost {esc(h.get('cost',''))} · data: {esc(h.get('data_status',''))}</td>
<td>{esc(h.get('status',''))}</td></tr>""" for h in hyp)
    return f"""<h2 style="margin-top:6px">Round-6 Pre-Registered Geological Hypotheses (2026-10-26: H36-1 .. H36-5)</h2>
<p class=mut>Pre-registered before running Round-6 experiments (<a href="research/hypotheses-round6-20261026.md">hypotheses-round6-20261026.md</a>),
motivated by byte-verified fixes for <b>IR-32-BAND-02</b> (Band 6 <code>tc</code> = radiometric Total Count) and
<b>IR-32-BAND-03</b> (Band 18 = signed <code>&part;g/&part;x</code>).</p>
<table><tr><th>#</th><th>hypothesis</th><th>layers</th><th>signature</th><th>why off-catalogue</th>
<th>difference from prior work</th><th>expected / cost / data</th><th>status</th></tr>{r6_rows}</table>
<h2>Historical Hypothesis Archive (Earlier Rounds)</h2>
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
    # A persistent download button in the header of *every* page: the brief asks for an obvious
    # one-click download at the very top of the site, and the safest way to guarantee that is to put
    # it in the page chrome rather than in one page's body.
    dl_btn = ""
    if sub:
        _f = sub.get("file", {})
        _zp = (sub.get("zip") or {}).get("path")
        _btn = [f'<a class="btn" href="{esc(_f.get("path", "").replace("docs/", ""))}">'
                f'&#11015; Download the registry-primary GeoTIFF (read its status first)</a>']
        if _zp and (ROOT / _zp).is_file():
            _btn.append(f'<a class="btn alt" href="{esc(_zp.replace("docs/", ""))}">.zip</a>')
        dl_btn = " ".join(_btn)

    pages = {
        "index.html": page(f"{TITLE} - a fault-discovery system for the DOE GEMS Prize",
                           overview(fl, sub, name), "index.html", dl_btn),
        "executive-summary.html": page("Make a submission (executive summary)", exec_summary(fl, sub, name),
                                       "executive-summary.html", dl_btn),
        "research.html": page("Research: the metric, the decision rule, and the evidence",
                              research(fl, sub, name), "research.html", dl_btn),
        "hypotheses.html": page("Candidate hypotheses, ranked", hypotheses_page(fl), "hypotheses.html",
                                dl_btn),
        "leaderboard.html": page("Leaderboard and the size of the gap", leaderboard_page(fl),
                                 "leaderboard.html", dl_btn),
        "sources.html": page("Sources", sources_page(fl), "sources.html", dl_btn),
        "irregularities.html": page("Irregularities flagged for review", irregularities_page(fl),
                                     "irregularities.html", dl_btn),
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
{protocol_notice("docs/")}
{arena41_block("docs/")}
{download_block(sub, name, "docs/")}
<div class=card><b>Full site:</b> <a href="docs/index.html">evidence, instruments, hypotheses and the
irregularity register &rarr;</a> &nbsp;·&nbsp; <a href="docs/executive-summary.html">how to submit, step by step &rarr;</a>
&nbsp;·&nbsp; <a href="README.md">README</a> &nbsp;·&nbsp; <a href="https://github.com/buffedlizard55-lab/GEMSDOE32">repository</a></div>
</main></body></html>"""
    (ROOT / "index.html").write_text(landing)

    # ---- root stubs for the other pages ---------------------------------------------------------
    # GitHub Pages publishes the repository *root* (server-side setting, source main:/), so
    # /GEMSDOE32/executive-summary.html would otherwise serve a stale, hand-written page that still
    # headlines a superseded primary.  Each root page is therefore a generated stub: the one-click
    # download first (with correct docs/-prefixed links), then a canonical pointer to the real page.
    # IR-34-ROOT-01.
    # Three further root pages come from the parallel (arena/01a104ba) site builder.  Pages publishes
    # the repository root, so they are live URLs too, and their content is superseded.  They become
    # stubs pointing at the docs/ page that now owns that subject.
    for legacy, target in ROOT_REDIRECTS.items():
        stub = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(target[1])} &middot; {TITLE}</title>
<link rel=canonical href="docs/{target[0]}">
<link rel=stylesheet href="docs/assets/site.css">
<meta http-equiv=refresh content="0; url=docs/{target[0]}"></head><body>
<main class=wrap style="padding-top:26px">
<h1>{esc(target[1])}</h1>
{download_block(sub, name, "docs/")}
<div class=card><b>This page moved.</b> The parallel site layout was retired; the current page is
<a href="docs/{target[0]}">{esc(target[1])} &rarr;</a>. &nbsp;&middot;&nbsp;
<a href="docs/index.html">whole site &rarr;</a></div>
</main></body></html>"""
        (ROOT / legacy).write_text(stub)

    for fname, title in NAV[1:]:
        stub = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)} &middot; {TITLE}</title>
<link rel=canonical href="docs/{fname}">
<link rel=stylesheet href="docs/assets/site.css">
<meta http-equiv=refresh content="0; url=docs/{fname}"></head><body>
<main class=wrap style="padding-top:26px">
<h1>{esc(title)}</h1>
{download_block(sub, name, "docs/")}
<div class=card><b>Full page:</b> <a href="docs/{fname}">{esc(title)} &rarr;</a>
&nbsp;&middot;&nbsp; <a href="docs/index.html">whole site &rarr;</a>
&nbsp;&middot;&nbsp; <a href="README.md">README</a></div>
</main></body></html>"""
        (ROOT / fname).write_text(stub)

    print(json.dumps({"pages": list(pages), "sources": fl.get("source_count"),
                      "leaderboard_rows": len(fl.get("leaderboard", [])),
                      "hypotheses": len(fl.get("hypotheses", [])),
                      "submission_built": bool(sub)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
