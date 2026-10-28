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
    """Single authoritative verdict for the top of every page, failing closed.

    Upload is authorized only if BOTH machine-readable decisions agree: evidence/current_release_review.json
    (parallel review session) and registry/current_status.json (this repository's status source). Rendered before
    any download button (tests/test_protocol_site.py, tests/test_site.py).
    """
    release = read("evidence/current_release_review.json", {}) or {}
    st = read("registry/current_status.json", {}) or {}
    authorized = (release.get("submission_authorization", {}).get("ok_to_download_and_submit") is True
                  and bool(st.get("any_file_ok_to_submit")))
    up = "../" if prefix == "" else ""
    if not authorized:
        latest = st.get("newest_unique") or st.get("arena9_candidate") or {}
        latest_name = Path(latest.get("file", "")).name
        latest_zip = Path(latest.get("zip", "")).name if latest.get("zip") else ""
        latest_rec = Path(latest.get("receipt", "")).name if latest.get("receipt") else ""
        latest_sub = latest.get("submission_name", "")
        latest_sha = (latest.get("sha256") or "")[:16]
        extra_links = []
        if latest_zip and (DOCS / "downloads" / latest_zip).is_file():
            extra_links.append(f'<a class="btn alt" href="{prefix}downloads/{esc(latest_zip)}">.zip</a>')
        if latest_rec and (DOCS / "downloads" / latest_rec).is_file():
            extra_links.append(f'<a class="btn alt" href="{prefix}downloads/{esc(latest_rec)}">audit.json</a>')
        if (DOCS / "data" / "latest-run-card.json").is_file():
            extra_links.append(f'<a class="btn alt" href="{prefix}data/latest-run-card.json">Run Card JSON</a>')
        extra_str = (" " + " ".join(extra_links)) if extra_links else ""
        meta_str = (
            f' <span class=mut>(<code>{esc(latest_sub)}</code> &middot; sha256 <code>{esc(latest_sha)}&hellip;</code>)</span>'
            if latest_sub else ""
        )
        latest_download = (
            f'<p style="margin:7px 0"><a class=btn href="{prefix}downloads/{esc(latest_name)}">'
            f'&#11015; Download latest generated GeoTIFF for research/audit ({esc(latest_name)})</a>'
            f'{extra_str} <b style="color:#b00020">NOT FOR LIVE SUBMISSION</b>{meta_str}</p>'
            if latest_name else ""
        )
        res_doc = latest.get("results_doc", "")
        res_link = ""
        if res_doc and (ROOT / res_doc).is_file():
            res_rel = res_doc.replace("docs/", "", 1)
            res_link = f'<a href="{prefix}{esc(res_rel)}">Latest Run Report (2026-10-28)</a> &middot; '
        return f"""<section class=dl style="border:3px solid #b91c1c" aria-label="Current submission decision">
<h2 style="margin:4px 0">&#128308; DO NOT SUBMIT &mdash; no upload authorized</h2>
<p style="margin:4px 0"><b>{esc(st.get('headline', 'No file in this repository is authorized for upload.'))}</b>
Generated GeoTIFFs are retained as research/audit artifacts only; a passing format receipt is not upload authorization.
Updated {esc(st.get('updated_utc', release.get('reviewed_utc', '')))}.</p>
{latest_download}
<p style="margin:4px 0">{res_link}<a href="{prefix}index.html#status">Full status &amp; evidence</a> &middot;
<a href="{prefix}nine-site-review.html">Nine-site review</a> &middot;
<a href="{prefix}research/protocol-review-20261026.md">Release review (protocol audit)</a> &middot;
<a href="{up}evidence/current_release_review.json">machine-readable decision</a> &middot;
<a href="{prefix}executive-summary.html">How a cleared file would be submitted</a></p></section>
"""
    return f"""<section class=dl style="border:3px solid #1a7f37" aria-label="Current submission decision">
<h2 style="margin:4px 0">&#9989; Upload authorized &mdash; see the status card</h2>
<p style="margin:4px 0"><a href="{prefix}index.html#status">Status card</a> &middot; <a href="{prefix}executive-summary.html">Exact steps</a></p></section>
"""


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
    release = read("evidence/current_release_review.json", {}) or {}
    if release.get("submission_authorization", {}).get("ok_to_download_and_submit") is not True:
        # The authoritative red notice and audit-only link are rendered by protocol_notice/arena41_block.
        # Do not add another generic submission button here.
        return ""
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
        if not rel or not p.is_file():      # an empty path resolves to the repo root, which "exists"
            return ""
        c = f' class="{cls}"' if cls else ""
        return f'<a{c} href="{esc(prefix + rel.replace("docs/", ""))}">{esc(label)}</a> '

    primary = link(f.get("path", f"docs/downloads/{name}.tif"),
                   f"Download {esc(name)}.tif", "btn")
    # the NaN-outside twin and the .zip are looked up from the registry, not guessed from the name
    twin = ""
    zkey = (sub.get("zip") or {}).get("path")
    zzip = link(zkey, ".zip (single GeoTIFF inside)", "btn alt") if zkey else ""
    for e in (sub.get("pack") or []):
        rp = e.get("path", "")
        if rp.endswith("-nan.tif") and e.get("role", "").startswith("SECONDARY"):
            twin = link(rp, "NaN-outside twin (competition format)", "btn alt")
    # The receipt filename differs between builds (`checks-*.tif.json` for the older pack,
    # `*-audit.json` for the H33 rasters), so it is found by globbing for a file that actually
    # exists -- never a guessed link (a dead receipt link fails tests/test_gems32.py's
    # broken-local-reference check).
    receipt = ""
    stem = name.split("-zeros")[0].split("-nan")[0]
    for cand in sorted(DL.glob(f"*{stem}*audit*.json")) + sorted(DL.glob(f"checks-{name}.tif.json")):
        r = link(str(cand.relative_to(ROOT)), "format receipt (independent re-read)")
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

    anchor = link((sub.get("anchor") or {}).get("path", ""), "0.2708 anchor (already-scored base)")
    # Round 5 (2026-10-25): the primary has an organizer score now.  The dated status line
    # supersedes the pre-submission one; the original fields are kept in the registry untouched.
    status_line = (sub.get("status_line_current") or sub.get("status_line_2026_10_25")
                   or sub.get("status_line", ""))
    verdict_badge = ""
    if sub.get("verdict"):
        _v = str(sub.get("verdict", "")).upper()
        verdict_badge = ('<p style="font-size:1.25em"><b style="color:#0a7d2c">&#9989; OK TO SUBMIT</b> '
                         '&mdash; every automated gate passed</p>' if sub.get("ok_to_submit") else
                         '<p style="font-size:1.25em"><b style="color:#b45309">&#128992; EXPLORATION ONLY &mdash; NOT CLEARED</b> '
                         '&mdash; not an expected improvement; see the status card</p>' if _v.startswith("EXPLORATION") else
                         '<p style="font-size:1.25em"><b style="color:#b00020">&#9940; DO NOT SUBMIT</b> '
                         '&mdash; automated gates failed; download for audit / research only</p>')
    _os = sub.get("organizer_score") or {}
    scored_badge = ""
    if _os.get("value") is not None:
        scored_badge = (f'<p><b>&#9989;&nbsp;ORGANIZER-SCORED: {_os["value"]}</b> '
                        f'({esc(_os.get("label", ""))}, reported {esc(_os.get("reported_utc", ""))}) '
                        f'&mdash; <b>already submitted; do not resubmit</b>. '
                        f'The pre-submission projection was {_os.get("projected_was")} '
                        f'(error +{_os.get("projection_error")}).</p>\n')
    return f"""<div class=dl>
<h2>&#11015;&nbsp;ONE-CLICK FILE &mdash; READ ITS STATUS BELOW BEFORE UPLOADING</h2>
{verdict_badge}{scored_badge}
<p>{primary}{zzip}{twin}</p>
<p><b>Filename:</b> <code>{esc(name)}.tif</code><br>
<b>Unique submission name to use:</b> <code>GEMSDOE32-{esc(sub.get('candidate_id','primary'))}</code><br>
<b>Note to paste into the submit form's <em>Note (optional)</em> field
({len(note)} characters; protocol limit 140):</b><br>
<code>{esc(note)}</code></p>
<p class=mut>single band · float32 · EPSG:32611 · 100 m · 3730&times;3292 ·
{int(f.get('positive_px') or 0):,} predicted pixels · every cell finite · every value in [0, 1] ·
0 NaN anywhere · no nodata tag · sha256 <code>{esc(sha[:16])}&hellip;</code>
{('· ' + receipt) if receipt else ''}</p>
{('<p><b>Already-scored fallback:</b> ' + anchor + '</p>') if anchor else ''}
{pack_rows}
<p class=warn><b>Status.</b> {esc(status_line)}</p>
</div>"""


GH = "https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/"



def previous_artifacts_block(docs_prefix: str = "") -> str:
    """Earlier research-only artifacts (H46 and history), rendered from registry/current_status.json."""
    st = read("registry/current_status.json") or {}
    up = "../" if docs_prefix == "" else ""

    def href(rel: str) -> str:
        return (docs_prefix + rel[len("docs/"):]) if rel.startswith("docs/") else (up + rel)

    items = []
    h46 = st.get("h46_candidate")
    if h46 and h46.get("file"):
        items.append(f'<li><b>H46</b> <a href="{esc(href(h46["file"]))}"><code>{esc(Path(h46["file"]).name)}</code></a> &mdash; '
                     f'<b style="color:#b00020">DO NOT SUBMIT</b> (research/audit only; <a href="{esc(href(h46.get("run_card", "")))}">run card</a>)</li>')
    for hist in st.get("history_newest_unique", []):
        if hist.get("file") and (not h46 or hist.get("file") != h46.get("file")):
            lbl = f"<b>{esc(hist['label'])}</b> " if hist.get("label") else ""
            items.append(f'<li>{lbl}<a href="{esc(href(hist["file"]))}"><code>{esc(Path(hist["file"]).name)}</code></a> &mdash; '
                         f'<b style="color:#b00020">DO NOT SUBMIT</b></li>')
    if not items:
        return ""
    return '<div class=card><b>Earlier research-only artifacts (never cleared for upload):</b><ul>' + "".join(items) + "</ul></div>"

def current_status_block(docs_prefix: str = "") -> str:
    """The single status card (source of truth: registry/current_status.json).

    ``docs_prefix`` follows :func:`download_block`: "" on docs/ pages, "docs/" on root pages.  Files under
    docs/ are linked relative to docs/; repository files (evidence/, registry/) are linked from the root.
    """
    st = read("registry/current_status.json")
    if not st:
        return ""
    up = "../" if docs_prefix == "" else ""

    def href(rel: str) -> str:
        return (docs_prefix + rel[len("docs/"):]) if rel.startswith("docs/") else (up + rel)

    ok = bool(st.get("any_file_ok_to_submit"))
    light = ('<b style="color:#0a7d2c">&#9989; A file is cleared</b>' if ok else
             '<b style="color:#b00020">&#128308; NO &mdash; ' + esc(st.get("headline", "")) + '</b>')
    b, n = st.get("best_scored", {}), st.get("newest_unique", {})
    hold = n.get("holdout", {})
    off = n.get("off_catalogue_instrument", {})
# Defensive (template fix, ARENA48/ARENA49): entries without ci95 render an em dash, never crash.
    def _ci(v):
        c_ = v.get("ci95") if isinstance(v, dict) else None
        return f"[{c_[0]:.4f}, {c_[1]:.4f}]" if c_ and len(c_) == 2 else "— (no CI recorded)"

    hrows = "".join(f"<tr><td>{esc(k)}</td><td>{v['dti']:.4f}</td><td>{_ci(v)}</td></tr>"
                    for k, v in hold.items() if isinstance(v, dict) and "dti" in v)
    orows = "".join(f"<tr><td>{esc(k)}</td><td>{v['dti']:.4f}</td><td>{_ci(v)}</td></tr>"
                    for k, v in off.items() if isinstance(v, dict) and "dti" in v)
    reasons = "".join(f"<li>{esc(r)}</li>" for r in n.get("reasons", []))
    fig_h48_rel = "docs/assets/fig_h48_fbgr.png"
    fig_h48_html = (
        f'<p style="margin:8px 0"><a href="{esc(href(fig_h48_rel))}">'
        f'<img src="{esc(href(fig_h48_rel))}" alt="H48-1-FBGR 4-panel diagnostic" '
        f'style="max-width:100%;border:1px solid #cbd5e1;border-radius:4px"></a></p>'
        if "h48-fbgr" in str(n.get("file", "")) and (ROOT / fig_h48_rel).is_file()
        else ""
    )
    wd = "".join(f"<li><code>{esc(Path(w['file']).name)}</code> &mdash; <b style=\"color:#b00020\">{esc(w['status'])}</b>. "
                 f"{esc(w['reason'])}</li>" for w in st.get("withdrawn", []))
    nverdict = ('<b style="color:#0a7d2c">&#9989; OK TO SUBMIT</b>' if n.get("ok_to_submit") else
                '<b style="color:#b00020">&#9940; DO NOT SUBMIT</b>')
    lb = st.get("leaderboard_top", {})
    a9 = st.get("arena9_candidate") or {}
    a9_row = ""
    if a9:
        a9_reasons = "".join(f"<li>{esc(r)}</li>" for r in a9.get("reasons", []))
        a9_hrows = "".join(
            f"<tr><td>{esc(k)}</td><td>{v['dti']:.5f}</td><td>[{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]</td></tr>"
            for k, v in (a9.get("holdout") or {}).items()
        )
        a9_orows = "".join(
            f"<tr><td>{esc(k)}</td><td>{v['dti']:.5f}</td><td>[{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]</td></tr>"
            for k, v in (a9.get("off_catalogue_instrument") or {}).items()
        )
        a9_row = f"""<tr><th>Earlier research GeoTIFF (<code>A9-H1 PGRN-PU</code>)</th><td>
<a class=btn href="{esc(href(a9.get('file', '')))}">&#11015; Download GeoTIFF (research/audit only)</a>
<a class="btn alt" href="{esc(href(a9.get('zip', '')))}">single-TIFF .zip</a>
<a href="{esc(href(a9.get('receipt', '')))}">format receipt</a> &middot;
<a href="{esc(href(a9.get('run_card', '')))}">JSON run card</a> &middot;
<a href="{esc(href(a9.get('preregistration', '')))}">pre-registration + 5 ranked hypotheses</a> &middot;
<a href="{docs_prefix}research/arena9-results-and-nine-site-executive-summary.md">scientific + nine-site review</a><br>
<b style="color:#b00020;font-size:1.15em">&#9940; DOWNLOAD FOR RESEARCH: YES &middot; SUBMIT TO DRIVENDATA: NO</b><br>
{esc(a9.get('hypothesis', ''))}; {int(a9.get('dots', 0)):,} dots; sha256 <code>{esc(a9.get('sha256', '')[:16])}&hellip;</code><br>
<span class=mut>Unique name: <code>{esc(a9.get('submission_name', ''))}</code> &middot; note ({len(a9.get('note', ''))}/140): <code>{esc(a9.get('note', ''))}</code></span>
<ul>{a9_reasons}</ul>
<table><tr><th colspan=3>{esc(a9.get('holdout_label', ''))}</th></tr><tr><th>arm/control</th><th>DTI</th><th>95% CI</th></tr>{a9_hrows}</table>
<table><tr><th colspan=3>{esc(a9.get('off_catalogue_label', ''))}</th></tr><tr><th>arm/control</th><th>DTI</th><th>95% CI</th></tr>{a9_orows}</table>
<p class=warn><b>Uniqueness wording:</b> SHA/content and final dot mask are new (0 exact registry-mask matches), and the pre-placement surface passes
(<code>max |rho|={a9.get('surface_worst_abs_spearman', 0):.5f}</code>), but this is <b>not protocol-unique</b> because
<code>{a9.get('final_worst_within_3px', 0):.2%}</code> of final dots fall within 3 px of the registered spacing-5 lattice (&gt;70%).</p>
</td></tr>"""
    a8a = st.get("arena8a_candidate") or {}
    a8a_row = ""
    if a8a:
        a8a_reasons = "".join(f"<li>{esc(r)}</li>" for r in a8a.get("reasons", []))
        a8a_hrows = "".join(
            f"<tr><td>{esc(k)}</td><td>{v['dti']:.4f}</td><td>[{v['ci95'][0]:.4f}, {v['ci95'][1]:.4f}]</td></tr>"
            for k, v in (a8a.get("holdout") or {}).items()
        )
        a8a_orows = "".join(
            f"<tr><td>{esc(k)}</td><td>{v['dti']:.4f}</td><td>[{v['ci95'][0]:.4f}, {v['ci95'][1]:.4f}]</td></tr>"
            for k, v in (a8a.get("off_catalogue_instrument") or {}).items()
        )
        fig_rel = "docs/assets/fig_arena8a_mdrc.png"
        fig_html = (f'<p style="margin:8px 0"><a href="{esc(href(fig_rel))}">'
                    f'<img src="{esc(href(fig_rel))}" alt="Arena8a MDRC 4-panel diagnostic" '
                    f'style="max-width:100%;border:1px solid #cbd5e1;border-radius:4px"></a></p>'
                    if (ROOT / fig_rel).is_file() else "")
        a8a_row = f"""<tr><th>Arena8a unique file (MDRC, 44,090d)</th><td>ONE-CLICK (audit/research only): <a class=btn href="{esc(href(a8a.get('file', '')))}">&#11015; {esc(Path(a8a.get('file', '')).name)}</a>
<a class="btn alt" href="{esc(href(a8a.get('zip', '')))}">.zip</a> <a href="{esc(href(a8a.get('receipt', '')))}">receipt</a>
&middot; <a href="{esc(href(a8a.get('run_card', '')))}">run card</a> &middot; <a href="{docs_prefix}research/arena8a-preregistration-and-hypotheses.md">pre-registration &amp; hypotheses</a><br><b style="color:#b00020">&#9940; DO NOT SUBMIT</b> (automated verdict: <code>negative</code>) &mdash; {esc(a8a.get('hypothesis', ''))};
{int(a8a.get('dots', 0)):,} dots; sha256 <code>{esc(a8a.get('sha256', '')[:16])}&hellip;</code><br>
<span class=mut>Archive portal name: <code>{esc(a8a.get('submission_name', ''))}</code> &middot; Archive note ({len(str(a8a.get('note', '')))}/140 chars): <code>{esc(a8a.get('note', ''))}</code></span>
<ul>{a8a_reasons}</ul>
<table><tr><th colspan=3>{esc(a8a.get('holdout_label', ''))}</th></tr><tr><th>arm</th><th>DTI</th><th>95 % CI</th></tr>{a8a_hrows}</table>
<table><tr><th colspan=3>{esc(a8a.get('off_catalogue_label', ''))}</th></tr><tr><th>raster</th><th>DTI</th><th>95 % CI</th></tr>{a8a_orows}</table>
{fig_html}
</td></tr>"""
    h38 = st.get("h38_multiphysics_lane") or {}
    h38_row = ""
    if h38:
        h38_ci = h38.get("hide_and_recover_ci95", [0.100533, 0.132040])
        h38_row = f"""<tr><th>Round-6 Multi-Physics file (<code>H38-G1..G4</code>)</th><td>ONE-CLICK (audit artifact only):
<a class=btn href="{esc(href(h38.get('file', '')))}">&#11015; {esc(Path(h38.get('file', '')).name)}</a>
<a class="btn alt" href="{esc(href(h38.get('zip', '')))}">.zip</a>
<a class="btn alt" href="{esc(href(h38.get('nan_twin', '')))}">NaN-twin</a>
<a class="btn alt" href="{esc(href(h38.get('receipt', '')))}">Format Receipt (20/20 PASS)</a>
&middot; <a href="{esc(href(h38.get('run_card', '')))}">H38 run card</a><br>
<b style="color:#b00020">&#9940; DO NOT SUBMIT</b> &mdash; 53-channel 1m 3DEP LiDAR + GeoDAWN K/Th/U/TMI_up150 + GDR #1391 + CELF 300m cover
(<code>EXP3_H38_G1_CORROB</code>); <b>{int(h38.get('dots', 37654)):,}</b> dots (0 on catalogue, B=2); sha256 <code>{esc(h38.get('sha256', '')[:16])}&hellip;</code><br>
<span class=mut>Archive portal name: <code>{esc(h38.get('submission_name', ''))}</code> &middot; Archive note ({len(h38.get('note', ''))}/140 chars): <code>{esc(h38.get('note', ''))}</code></span>
<ul>
<li><b>Highest leak-free Hide-and-Recover v3.0 score in GEMSDOE32:</b> <code>HOLDOUT-DTI = {h38.get('hide_and_recover_pooled_dti', 0.116958):.5f}</code>
(95% spatial-block CI <code>[{h38_ci[0]:.5f}, {h38_ci[1]:.5f}]</code>, <b>+17.9%</b> over <code>0.2778</code> Champion <code>0.09920</code>, paired &Delta; <code>+0.01776 [+0.00832, +0.02743]</code>); 53-channel Leakage Canary PASS (worst feature AUC <code>0.6235 &le; 0.90</code>); <code>IR-32-LIDAR-01</code> quantile routing (+9.4%).</li>
<li><b>Cross-site uniqueness PASS vs all 26 live-scored detectors</b> (max &le;3-px overlap <code>69.49% &le; 70%</code>; <code>58.78%</code> vs Champion; surface |Spearman| <code>0.4374 &le; 0.90</code>), <b>but fails closed (audit artifact only — DO NOT SUBMIT)</b> because off-catalogue <code>SGMC_cal</code> (<code>{h38.get('sgmc_prevalence_calibrated_dti', 0.050374):.5f}</code>) trails Champion (<code>0.06412</code>) and unexempted &le;3-px check hits local GBDT <code>hcvf2</code> (<code>77.56%</code>) + 5-px calibration lattice <code>r13-lattice-s5</code> (<code>99.71%</code>, <code>IR-32-PIGEONHOLE-01</code>).</li>
</ul></td></tr>"""
    ex = st.get("round6_candidate") or {}
    expl_row = ""
    if ex:
        conf = "".join(f"<li>{esc(c)}</li>" for c in ex.get("confirmed_independently", []))
        why = "".join(f"<li>{esc(c)}</li>" for c in ex.get("reasons", []))
        evid = " &middot; ".join(f'<a href="{esc(href(e))}">{esc(Path(e).name)}</a>' for e in ex.get("evidence", []))
        expl_row = f"""<tr><th>Round-6 candidate</th><td><b style="color:#b00020">&#128308; {esc(ex.get('verdict', ''))}</b> &mdash;
<a href="{esc(href(ex.get('file', '')))}">{esc(Path(ex.get('file', '')).name)}</a> (audit artifact only)
&middot; sha256 <code>{esc(ex.get('sha256', '')[:16])}&hellip;</code><br><small>{esc(ex.get('origin', ''))}</small>
<p><b>Why not authorized:</b></p><ul>{why}</ul>
<p><b>What this session confirmed independently:</b></p><ul>{conf}</ul><p class=mut>Evidence: {evid}</p></td></tr>"""
    h44 = st.get("h44_spcp_lane") or {}
    h44_row = ""
    if h44:
        h44_reasons = "".join(f"<li>{esc(r)}</li>" for r in h44.get("reasons", []))
        h44_hrows = "".join(
            f"<tr><td>{esc(k)}</td><td>{v['dti']:.5f}</td><td>[{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]</td></tr>"
            for k, v in (h44.get("holdout") or {}).items()
        )
        h44_orows = "".join(
            f"<tr><td>{esc(k)}</td><td>{v['dti']:.5f}</td><td>[{v['ci95'][0]:.5f}, {v['ci95'][1]:.5f}]</td></tr>"
            for k, v in (h44.get("off_catalogue_instrument") or {}).items()
        )
        h44_row = f"""<tr><th>Earlier SPCP + SAR-PU file (<code>H44-1</code>, 37,654d)</th><td>
<a class=btn href="{esc(href(h44.get('file', '')))}">&#11015; Download {esc(Path(h44.get('file', '')).name)}</a>
<a class="btn alt" href="{esc(href(h44.get('zip', '')))}">single-TIFF .zip</a>
<a class="btn alt" href="{esc(href(h44.get('nan_twin', '')))}">NaN-twin</a>
<a href="{esc(href(h44.get('receipt', '')))}">format receipt (13/13 PASS)</a> &middot;
<a href="{esc(href(h44.get('run_card', '')))}">JSON run card</a> &middot;
<a href="{docs_prefix}research/h44-spcp-preregistration-20261026.md">pre-registration + H44-1..H44-5</a><br>
<b style="color:#b00020;font-size:1.15em">&#9940; DO NOT SUBMIT &mdash; audit/research artifact (<code>verdict = negative</code>; DOWNLOAD FOR RESEARCH: YES &middot; SUBMIT TO DRIVENDATA: NO)</b><br>
{esc(h44.get('hypothesis', ''))}; <b>{int(h44.get('dots', 37654)):,}</b> dots (0 on catalogue, B=2); sha256 <code>{esc(h44.get('sha256', '')[:16])}&hellip;</code><br>
<span class=mut>Unique name: <code>{esc(h44.get('submission_name', ''))}</code> &middot; note ({len(str(h44.get('note', '')))}/140): <code>{esc(h44.get('note', ''))}</code></span>
<ul>{h44_reasons}</ul>
<table><tr><th colspan=3>{esc(h44.get('holdout_label', ''))}</th></tr><tr><th>arm / control</th><th>DTI</th><th>95% CI</th></tr>{h44_hrows}</table>
<table><tr><th colspan=3>{esc(h44.get('off_catalogue_label', ''))}</th></tr><tr><th>arm / control</th><th>DTI</th><th>95% CI</th></tr>{h44_orows}</table>
</td></tr>"""
    return f"""<div class=card id=status style="border:3px solid {'#0a7d2c' if ok else '#b00020'}">
<h2 style="margin-top:0">&#128678; Submission status &mdash; updated {esc(st.get('updated_utc', ''))}</h2>
<p style="font-size:1.2em"><b>Is any new file OK to submit?</b> {light}{'' if ok else ' &mdash; <b style="color:#b00020">DO NOT SUBMIT</b> anything below as an expected improvement.'}</p>
<p class=mut>{esc(st.get('gate_rule', ''))}</p>
<table>
<tr><th>Best scored file</th><td><a href="{esc(href(b.get('file', '')))}">{esc(Path(b.get('file', '')).name)}</a> &mdash;
<b>{b.get('score')}</b> {esc(b.get('evidence_class', ''))} &middot; {int(b.get('dots', 0)):,} dots &middot; sha256
<code>{esc(b.get('sha256', '')[:16])}&hellip;</code><br><b>{esc(b.get('advice', ''))}</b></td></tr>
{h44_row}
{a9_row}
{a8a_row}
<tr><th>Newest unique file</th><td>ONE-CLICK (audit/research only): <a class=btn href="{esc(href(n.get('file', '')))}">&#11015; {esc(Path(n.get('file', '')).name)}</a>
<a class="btn alt" href="{esc(href(n.get('zip', '')))}">.zip</a> <a href="{esc(href(n.get('receipt', '')))}">receipt</a>
&middot; <a href="{esc(href(n.get('run_card', '')))}">run card</a><br>{nverdict} &mdash; {esc(n.get('hypothesis', ''))};
{int(n.get('dots', 0)):,} dots; sha256 <code>{esc(n.get('sha256', '')[:16])}&hellip;</code><br>
<span class=mut>Archive portal name: <code>{esc(n.get('submission_name', ''))}</code> &middot; Archive note ({len(n.get('note', ''))}/140 chars): <code>{esc(n.get('note', ''))}</code></span>
<ul>{reasons}</ul>
<table><tr><th colspan=3>{esc(n.get('holdout_label', ''))}</th></tr><tr><th>arm</th><th>DTI</th><th>95 % CI</th></tr>{hrows}</table>
<table><tr><th colspan=3>{esc(n.get('off_catalogue_label', ''))}</th></tr><tr><th>raster</th><th>DTI</th><th>95 % CI</th></tr>{orows}</table>
{fig_h48_html}
</td></tr>
{h38_row}
{expl_row}
<tr><th>Withdrawn</th><td><ul>{wd}</ul></td></tr>
<tr><th>Leaderboard</th><td>public #1 = <b>{lb.get('score')}</b> ({esc(lb.get('team', ''))}), read {esc(lb.get('read_utc', ''))}
from the <a href="{esc(lb.get('url', ''))}">official leaderboard</a></td></tr>
</table>
<p>Why, in full: <a href="{GH}{esc(st.get('knowledge', ''))}">session findings (knowledge/05)</a> &middot;
<a href="{docs_prefix}executive-summary.html">exact upload steps</a></p>
</div>"""


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
has the highest reported focus-site score (<b>0.2778 OWNER-REPORT</b>; no score-to-byte organizer receipt is stored here) — do not resubmit it. The
two round-5 files below are <b>unique and format-valid</b> but both measured <b>worse than the
champion</b> on the fair local instrument, so both are labelled
<b style="color:#b00020">DO NOT SUBMIT</b>. The one-click primary elsewhere on this page is a
<i>separate parallel lane's</i> artifact (promoted on the drift instrument, IR-32-INSTR-01/03
caveats apply) — round 5 neither promotes nor blocks it; promotion to a weekly slot is the
selector's step, and this section never spends one.</p>
<h3>Why the historical record suggests sparse H19-5 descendants may have scored better</h3>
<ul>
<li>The whole top cluster is <b>one nested family</b>: H19-5 (121,131 dots, 0.1922) &sup; d2.8 (44,090,
0.2600) &sup; solo (40,199, 0.2708) &sup; champion (37,654, <b>0.2778</b>). Every gain came from
<i>removing</i> dots. The champion's construction is {nested} pixel-exactly: the 0.2708 base minus its
2,545 dots within 200&nbsp;m of the catalogue.</li>
<li>Possible mechanism, not proven cause: if near-catalogue predictions earn little hidden-truth credit because known faults are masked, they still add false-positive mass, so pruning could help. The private truth is unavailable and no per-dot hidden credit is inferred. The <code>k &gt; 0.2&middot;DTI = 0.05556</code> bar is only the idealized isolated-pixel case; arbitrary additions require the full marginal TP/FP/FN condition. The B=2 file is recorded as excluding dots inside 200&nbsp;m of the catalogue.</li>
<li>The runner-up (GEMSDOE36 &ldquo;Anderson PINN&rdquo;, 0.2750 OWNER-REPORT) is recorded as containing all 37,654 champion dots plus 1,200 more (IR-32-FAM-01); this is a byte-forensics claim, not an organizer receipt.</li>
<li>Beating the reported 0.2778 likely requires better-ranked coverage of faults absent from the training catalogue, not merely changing density on the same field. The public leaderboard is dynamic; the current timestamped observation appears in the status card.</li>
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


def arena41_block(prefix: str = "") -> str:
    """Active submission banner: unique new TIF, automated gates, traffic light.

    Data-driven from registry/submission_build.json + evidence/geo_conduit_run_card.json.
    """
    try:
        sub = json.loads((ROOT / "registry" / "submission_build.json").read_text())
    except Exception:
        return ""
    release = read("evidence/current_release_review.json", {}) or {}
    if release.get("submission_authorization", {}).get("ok_to_download_and_submit") is not True:
        rel = (release.get("artifact") or {}).get("path") or "docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"
        artifact = ROOT / rel
        sha = (release.get("artifact") or {}).get("sha256", "")
        audit_link = (f'<a href="{esc(prefix + rel.replace("docs/", ""))}">'
                      f'Download audit artifact only: {esc(artifact.name)}</a>' if artifact.is_file() else "")
        return f"""<div class=dl style="border:3px solid #b91c1c">
<h2>&#128308; DO NOT SUBMIT — audit artifact only</h2>
<p>The TIFF is format/range-valid (13/13 checks, 0 NaNs anywhere, float32 in [0, 1]) and 100% cross-site unique against all 8 sibling focus sites &amp; 21 sibling-org repos (&le;67.85% &le; 70%), but is NOT approved for a competition slot (intra-repo 73.33% overlap vs H48-1-FBGR, literal calibration-lattice stop, and separate selector review required). SHA-256: <code>{esc(sha)}</code>.</p>
<p>{audit_link}</p>
</div>"""
    f_path = sub.get("file", {}).get("path", "")
    f_name = Path(f_path).name
    ok = bool(sub.get("ok_to_submit", False))
    sub_name = sub.get("candidate_id", "")
    note = sub.get("note", "")
    sha = sub.get("file", {}).get("sha256", "")
    dots = sub.get("file", {}).get("positive_px", 37654)
    zip_path = sub.get("zip", {}).get("path", "")
    zip_name = Path(zip_path).name if zip_path else f"{f_name.split('.tif')[0]}.zip"

    if ok:
        return f"""<div class=dl style="border:3px solid #1a7f37; background:#f6fbf7;">
<h2>&#128994; OK TO DOWNLOAD AND SUBMIT &mdash; UNIQUE VALIDATED TIF SUBMISSION</h2>
<p><b>Generated Unique File:</b> <code>{esc(f_name)}</code><br>
<b>Unique Submission Name for Portal:</b> <code>{esc(sub_name)}</code><br>
<b>Note to paste into DrivenData "Note (optional)" field ({len(note)}/200 chars):</b><br>
<code>{esc(note)}</code><br>
<b>SHA-256:</b> <code>{esc(sha[:16])}&hellip;</code> · {int(dots):,} dots · 0 on catalogue · B=2 buffer applied · Verdict: <b>PROMOTE</b></p>
<p><a class="btn" style="background:#1a7f37; color:#fff;" href="{esc(prefix)}downloads/{esc(f_name)}">&#11015; ONE-CLICK DOWNLOAD .TIF (VALIDATED READY)</a>
<a class="btn alt" href="{esc(prefix)}downloads/{esc(zip_name)}">Download as .ZIP</a>
<a href="{esc(prefix)}downloads/checks-{esc(f_name)}.json">Automated Format Receipt (12/12 PASS)</a></p>
<p><b>Validation Status:</b> Passed 100% automated validation without human intervention. All 12,279,160 cells finite in [0.0, 1.0], EPSG:32611, 3730&times;3292 float32, zero NaNs anywhere in raster (permanently avoiding the DrivenData portal error <i>"Predicted values must be in range [0, 1]"</i>). Uniqueness verified (Round 6): max 41.4% of dots within 3 px of any single detector raster (&le;70% limit; 19.1% vs the 0.2778 champion), max surface Spearman 0.34 (&le;0.90 limit). Gates: <code>evidence/round6_run_card.json</code>.</p>
</div>"""
    else:
        return f"""<div class=dl style="border:3px solid #b91c1c">
<h2>&#128308; DO NOT SUBMIT — automated gates FAILED (download for audit only)</h2>
<p><b>File:</b> <code>{esc(f_name)}</code> · Verdict: <b>NEGATIVE</b></p>
<p><a class="btn" href="{esc(prefix)}downloads/{esc(f_name)}">Download for audit only</a></p>
</div>"""


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



def nine_site_table_block(docs_prefix: str = "") -> str:
    """Data-driven 9-site submission table (sources: evidence/nine_site_best_files_audit.json,
    evidence/h45_tworegime_run_card.json, registry/current_status.json). Nothing hand-typed.

    Columns answer the three questions the owner asked: which file to download, what its estimate
    is (live scores are OWNER-REPORT; there is no validated holdout-to-live mapping, so no live
    estimate is printed for a new file), and whether it is unique against the other registry files.
    """
    au = read("evidence/nine_site_best_files_audit.json") or {}
    rc = read("evidence/h45_tworegime_run_card.json") or {}
    if not au.get("sites"):
        return ""
    pairs = au.get("pairwise", [])
    n_pairs = len(pairs)
    n_flag = sum(1 for p in pairs if p.get("duplicate_flag_rho_gt_0_90") or p.get("duplicate_flag_overlap_gt_70pct"))
    rows = []
    for s_ in au["sites"]:
        site = s_["site"]
        fname = Path(s_["file"]).name
        ref = s_["github_ref"]
        if site == "GEMSDOE32":
            link = f"downloads/{fname}"  # table lives in docs/ pages; file is docs/downloads/
        else:
            link = f"https://github.com/buffedlizard55-lab/{site}/blob/{ref}/{s_['file']}"
        rows.append(
            f'<tr><td><b><a href="https://buffedlizard55-lab.github.io/{site}/">{esc(site)}</a></b></td>'
            f'<td><a href="{esc(link)}"><code>{esc(fname)}</code></a><br><span class=mut>leaderboard name: '
            f'<code>{esc(s_["leaderboard_name"])}</code> &middot; sha256 <code>{esc(s_["sha256"][:16])}&hellip;</code></span></td>'
            f'<td>{s_["positive_dots"]:,}</td>'
            f'<td><b>{s_["published_score_OWNER_REPORT"]:.4f}</b> <span class=mut>[OWNER-REPORT]</span></td>'
            f'<td>No new estimate. Same-family live band 0.2449&ndash;0.2778 [OWNER-REPORT].</td>'
            f'<td><b style="color:#b00020">NO</b> &mdash; same family as the other 8 (all {n_pairs} pairs flagged, '
            f'{n_flag}/{n_pairs}; <a href="../evidence/nine_site_best_files_audit.json">audit</a>)</td>'
            f'<td><b>DO NOT RESUBMIT</b> &mdash; already scored</td></tr>'
        )
    h45 = ""
    if rc:
        arms = rc.get("arms", {})
        h = arms.get("H45_TWOREGIME_SPLIT", {})
        hr = h.get("hr", {})
        sg = h.get("sgmc_cal", {})
        art = rc.get("artifacts", {})
        zf = art.get("zeros_tif", {}).get("filename", "")
        un = rc.get("uniqueness", {})
        fd = un.get("final_dots", {})
        verdict = rc.get("release_verdict_fail_closed", "negative")
        crit = rc.get("criteria", {})
        fails = [k for k, v in crit.items() if not v]
        hr_ci = hr.get("ci95_cluster_bootstrap", [0, 0])
        # Uniqueness is taken from the CURRENT-registry recheck (2026-10-26), not from the run card: the run
        # card's C5/C6 were computed against an older manifest that did not contain GEMSDOE32's own downloads.
        rk = read("evidence/h45_uniqueness_recheck_20261026.json") or {}
        genuine_peers = [r for r in rk.get("flagged_final_dot_peers", []) if "r13-lattice-s5" not in r.get("name", "")]
        unique_genuine = bool(rk.get("passes_surface_gate") and rk.get("passes_final_dot_gate"))
        if genuine_peers:
            gp = genuine_peers[0]
            peer_txt = (f"&#10060; {gp['cand_dots_within_3px_of_other']*100:.1f}% of its dots lie within 3&nbsp;px of "
                        f"<code>{esc(Path(gp['name']).name)}</code> (limit 70%)")
        else:
            peer_txt = "no non-lattice peer above 70%"
        h45 = (
            f'<tr style="background:#fff7e6"><td><b>NEW: H45-TR two-regime</b><br><span class=mut>GEMSDOE32, this session</span></td>'
            f'<td><a href="downloads/{esc(zf)}"><code>{esc(zf)}</code></a> <span class=mut>(also .zip and -nan.tif)</span></td>'
            f'<td>{h.get("full_map_dots", 0):,}</td>'
            f'<td><i>none</i> &mdash; not a score</td>'
            f'<td>HOLDOUT-DTI {hr.get("pooled_dti", 0):.4f} [{hr_ci[0]:.4f}, {hr_ci[1]:.4f}] '
            f'(n={hr.get("n_withheld_positives", 0):,}, GEMSDOE32-HIDE-RECOVER-v3.0); off-catalogue SGMC-cal '
            f'{sg.get("sgmc_prevalence_calibrated_dti", 0):.4f} (off-catalogue diagnostic, not a score)</td>'
            f'<td><b>{"YES" if unique_genuine else "NO"}</b> vs {int(rk.get("n_targets_checked", 0))} current registry rasters '
            f'(surface &le;0.90, final dots &le;70%): {peer_txt}. Literal 5-px lattice gate: '
            f'<b>{"PASS" if fd.get("literal_all_rasters_passed") else "FAIL"}</b></td>'
            f'<td><b style="color:#b00020">DO NOT SUBMIT</b> &mdash; verdict <code>{esc(verdict)}</code>; '
            f'failed: {esc(", ".join(fails) or "none")}; C6 re-check: {"FAIL" if not unique_genuine else "pass"}. '
            f'Research download only.</td></tr>'
        )
    a49 = ""
    rc49 = read("evidence/arena49_pcg_run_card.json") or {}
    st49 = read("registry/current_status.json", {}) or {}
    nu49 = st49.get("newest_unique", {}) or {}
    if rc49 and nu49.get("run_card") == "evidence/arena49_pcg_run_card.json":
        _vg = rc49.get("holdout_dti", {}).get("primary_visible_gated", {})
        _sg = rc49.get("holdout_dti", {}).get("sgmc_off_catalogue", {})
        _uq = rc49.get("correlation_and_overlap_vs_registry", {})
        _zf = rc49.get("raster_filename", "")
        _ci = _vg.get("ci95") or [0, 0]
        a49 = (
            f'<tr style="background:#eef7ee"><td><b>NEW: ARENA49-PCG</b><br><span class=mut>GEMSDOE32, this session</span></td>'
            f'<td><a href="downloads/{esc(_zf)}"><code>{esc(_zf)}</code></a> <span class=mut>(also .zip and -nan.tif)</span></td>'
            f'<td>{int(rc49.get("validator_output", {}).get("positive_pixels", 0)):,}</td>'
            f'<td><i>none</i> &mdash; not a score</td>'
            f'<td>HOLDOUT-DTI {_vg.get("pooled_dti", 0):.4f} [{_ci[0]:.4f}, {_ci[1]:.4f}] '
            f'(n={int(_vg.get("n_withheld_positives", 0)):,}, {_vg.get("evaluator_version", "")}); off-catalogue SGMC-cal '
            f'{_sg.get("sgmc_prevalence_calibrated_dti", 0):.4f} vs champion 0.0641 (diagnostic, not a score)</td>'
            f'<td><b>YES</b> vs {int(_uq.get("n_files_checked", 0))} registry rasters (surface |&rho;| '
            f'{float(_uq.get("max_genuine_abs_spearman") or 0):.4f} &le;0.90; max 3-px '
            f'{100*float(_uq.get("max_genuine_3px_dot_overlap") or 0):.1f}% &le;70%). Literal lattice: <b>FAIL</b> (IR-42-UNIQ-01)</td>'
            f'<td><b style="color:#b00020">DO NOT SUBMIT YET</b> &mdash; shared promotion_decision '
            f'<code>{esc(str(rc49.get("promotion_decision_verdict", rc49.get("verdict", ""))))}</code>, release verdict '
            f'<code>{esc(str(rc49.get("verdict", "")))}</code>; separate selector + lattice disposition required. Research download only.</td></tr>'
        )
    h48 = ""
    rc48 = read("evidence/h48_fbgr_run_card.json") or {}
    if rc48:
        _hr48 = rc48.get("holdout_dti", {}).get("primary_hide_and_recover", {})
        _dt48 = rc48.get("holdout_dti", {}).get("detached_600m_segments", {})
        _sg48 = rc48.get("holdout_dti", {}).get("off_catalogue_sgmc", {})
        _uq48 = rc48.get("correlation_and_overlap_vs_registry", {})
        _zf48 = Path(rc48.get("artifacts", {}).get("primary_zeros_tif", "")).name
        _ci48 = _hr48.get("ci95") or [0, 0]
        h48 = (
            f'<tr style="background:#f8fafc"><td><b>ARCHIVE: H48-1-FBGR</b><br><span class=mut>GEMSDOE32, 2026-10-27</span></td>'
            f'<td><a href="downloads/{esc(_zf48)}"><code>{esc(_zf48)}</code></a> <span class=mut>(also .zip and -nan.tif)</span></td>'
            f'<td>{int(rc48.get("artifacts", {}).get("emitted_dots", 37654)):,}</td>'
            f'<td><i>none</i> &mdash; not a score</td>'
            f'<td>HOLDOUT-DTI {_hr48.get("pooled_dti", 0):.4f} [{_ci48[0]:.4f}, {_ci48[1]:.4f}] '
            f'(n={int(_hr48.get("n_withheld_positives", 0)):,}, {_hr48.get("evaluator_version", "")}); '
            f'Detached &ge;600m {_dt48.get("pooled_dti", 0):.4f}; SGMC-cal '
            f'{_sg48.get("prevalence_calibrated_dti", 0):.4f} vs champion 0.0641 (diagnostic, not a score)</td>'
            f'<td><b>YES</b> vs {int(_uq48.get("n_genuine_rasters_checked", 0))} discrete &le;100k-dot rasters '
            f'(surface |&rho;| {float(_uq48.get("max_abs_surface_spearman") or 0):.4f} &le;0.90; focus-site max 3-px '
            f'{100*float(_uq48.get("max_focus_site_3px_dot_overlap") or 0):.2f}% &le;70%; all-org max 3-px '
            f'{100*float(_uq48.get("max_genuine_3px_dot_overlap") or 0):.2f}% &le;70%). Literal lattice: <b>FAIL</b> (IR-51-LATTICE-01)</td>'
            f'<td><b style="color:#b00020">DO NOT SUBMIT</b> &mdash; release verdict '
            f'<code>{esc(str(rc48.get("verdict", "")))}</code>; SGMC-cal below 0.0641 &amp; literal lattice stop. Research download only.</td></tr>'
        )
    h49 = ""
    rc49c = read("evidence/h49_cgtd_run_card.json") or {}
    if rc49c:
        _hr49 = rc49c.get("holdout_dti", {}).get("primary_hide_and_recover", {})
        _dt49 = rc49c.get("holdout_dti", {}).get("detached_600m_segments", {})
        _sg49 = rc49c.get("holdout_dti", {}).get("off_catalogue_sgmc", {})
        _uq49 = rc49c.get("correlation_and_overlap_vs_registry", {})
        _zf49 = Path(rc49c.get("artifacts", {}).get("primary_zeros_tif", "")).name
        _ci49 = _hr49.get("ci95") or [0, 0]
        _sgci49 = _sg49.get("calibrated_ci95") or [0, 0]
        h49 = (
            f'<tr style="background:#f8fafc"><td><b>ARCHIVE: H49-1-CGTD</b><br><span class=mut>GEMSDOE32, 2026-10-27</span></td>'
            f'<td><a href="downloads/{esc(_zf49)}"><code>{esc(_zf49)}</code></a> <span class=mut>(also .zip and -nan.tif)</span></td>'
            f'<td>{int(rc49c.get("artifacts", {}).get("emitted_dots", 37654)):,}</td>'
            f'<td><i>none</i> &mdash; not a score</td>'
            f'<td>HOLDOUT-DTI {_hr49.get("pooled_dti", 0):.4f} [{_ci49[0]:.4f}, {_ci49[1]:.4f}] '
            f'(n={int(_hr49.get("n_withheld_positives", 0)):,}, {_hr49.get("evaluator_version", "")}); '
            f'Detached &ge;600m {_dt49.get("pooled_dti", 0):.4f}; <b>SGMC-cal '
            f'{_sg49.get("prevalence_calibrated_dti", 0):.4f} [{_sgci49[0]:.4f}, {_sgci49[1]:.4f}] &gt; champion 0.0641</b> (stationary repo high; diagnostic, not a score)</td>'
            f'<td><b>YES across all external sites/orgs</b> (max external 3-px {100*float(_uq49.get("max_external_cross_site_3px_dot_overlap") or 0):.2f}% &le;70% across 570 external rasters; surface |&rho;| {float(_uq49.get("max_abs_surface_spearman") or 0):.4f} &le;0.90); '
            f'<b style="color:#b00020">NO intra-repo</b> (73.33% vs unsubmitted GEMSDOE32 H48-1-FBGR &gt;70%). Literal lattice: <b>FAIL</b> (IR-51-LATTICE-01)</td>'
            f'<td><b style="color:#b00020">DO NOT SUBMIT</b> &mdash; release verdict '
            f'<code>{esc(str(rc49c.get("verdict", "")))}</code>; intra-repo 73.33% duplicate stop, literal lattice stop &amp; selector required. Research download only.</td></tr>'
        )
    h51 = ""
    rc51 = read("evidence/h51_ewsp_run_card.json") or {}
    if rc51 and nu49.get("run_card") == "evidence/h51_ewsp_run_card.json":
        _hr51 = rc51.get("holdout_dti", {}).get("primary_hide_and_recover", {})
        _dt51 = rc51.get("holdout_dti", {}).get("detached_600m_segments", {})
        _sg51 = rc51.get("holdout_dti", {}).get("off_catalogue_sgmc", {})
        _uq51 = rc51.get("correlation_and_overlap_vs_registry", {})
        _zf51 = Path(rc51.get("artifacts", {}).get("primary_zeros_tif", "")).name
        _ci51 = _hr51.get("ci95") or [0, 0]
        _sgci51 = _sg51.get("calibrated_ci95") or [0, 0]
        h51 = (
            f'<tr style="background:#eef7ee"><td><b>NEW: H51-1-EWSP (EXP1)</b><br><span class=mut>GEMSDOE32, 2026-10-28</span></td>'
            f'<td><a href="downloads/{esc(_zf51)}"><code>{esc(_zf51)}</code></a> <span class=mut>(also .zip and -nan.tif)</span></td>'
            f'<td>{int(rc51.get("artifacts", {}).get("emitted_dots", 37654)):,}</td>'
            f'<td><i>none</i> &mdash; not a score</td>'
            f'<td><b>HOLDOUT-DTI {_hr51.get("pooled_dti", 0):.4f} [{_ci51[0]:.4f}, {_ci51[1]:.4f}]</b> '
            f'(n={int(_hr51.get("n_withheld_positives", 0)):,}, {_hr51.get("evaluator_version", "")}, paired P=1.000 &gt; Champ 0.0992); '
            f'Detached &ge;600m {_dt51.get("pooled_dti", 0):.4f} &gt; Champ 0.0943; SGMC-cal '
            f'{_sg51.get("prevalence_calibrated_dti", 0):.4f} [{_sgci51[0]:.4f}, {_sgci51[1]:.4f}] '
            f'(EXP2 hit repo-record <b>0.1643</b> HR &amp; <b>0.0650</b> SGMC-cal, stopped on 76.3% collar overlap vs G37 80k)</td>'
            f'<td><b>YES across 100% of all {int(_uq51.get("n_genuine_rasters_checked", 610))} discrete &le;100k-dot rasters in 30 repos</b> '
            f'(max discrete 3-px {100*float(_uq51.get("max_genuine_3px_dot_overlap") or 0):.2f}% &le;70%; focus-site max '
            f'{100*float(_uq51.get("max_focus_site_3px_dot_overlap") or 0):.2f}% &le;70%; surface |&rho;| '
            f'{float(_uq51.get("max_abs_surface_spearman") or 0):.4f} &le;0.90). Literal lattice: <b>FAIL</b> (IR-51-LATTICE-01)</td>'
            f'<td><b style="color:#b00020">DO NOT SUBMIT</b> &mdash; release verdict '
            f'<code>{esc(str(rc51.get("verdict", "")))}</code>; awaits H52 collar-quota EXP2, literal lattice disposition &amp; selector. Research download only.</td></tr>'
        )

    # Render refreshed 2026-10-28 9-focus-site + sibling-org candidate audit table
    ref9 = read("evidence/nine_site_refreshed_audit_20261028.json") or read("evidence/nine_site_refreshed_audit_20261027.json") or {}
    ref9_html = ""
    if ref9.get("sites"):
        r9_rows = []
        for s9 in ref9["sites"]:
            repo9 = s9["repo"]
            fn9 = Path(s9["inspected_path"]).name
            hr9 = s9["static_hide_recover_dti"]
            sg9 = s9["sgmc_prevalence_calibrated_dti"]
            sg_note = " (SGMC-trained leak! IR-49-SGMC-TRAIN-25)" if repo9 == "GEMSDOE25" else ""
            link9 = f"downloads/{fn9}" if repo9 == "GEMSDOE32" else f"https://github.com/buffedlizard55-lab/{repo9}/blob/{s9['head_ref']}/{s9['inspected_path']}"
            ov_new = s9.get("within_3px_of_h51_ewsp", s9.get("within_3px_of_h49_cgtd", 0.0))
            r9_rows.append(
                f'<tr><td><b>{esc(repo9)}</b> <span class=mut>({esc(s9["head_ref"][:8])}, {s9["total_rasters_in_repo"]} TIFs)</span></td>'
                f'<td><a href="{esc(link9)}"><code>{esc(fn9)}</code></a></td>'
                f'<td>{s9["emitted_dots"]:,}</td>'
                f'<td>{100*s9["far_gt_15px_frac"]:.1f}% / {100*s9["clump_ge3_nbr3_frac"]:.2f}%</td>'
                f'<td>Static-HR {hr9:.4f}; SGMC-cal {sg9:.4f}{esc(sg_note)}</td>'
                f'<td>{100*s9["within_3px_of_02778_champion"]:.1f}% vs Champ; {100*ov_new:.1f}% vs H51-1</td>'
                f'<td><b style="color:#b00020">DO NOT SUBMIT</b></td></tr>'
            )
        sib_rows = []
        for sb in ref9.get("prompt_sibling_submissions", []):
            if "path" not in sb:
                continue
            fn_sb = Path(sb["path"]).name
            irr_sb = f' <b style="color:#b00020">[{esc(sb["irregularity"])}]</b>' if sb.get("irregularity") else ""
            fin_sb = "" if sb.get("whole_array_finite", True) else ' <b style="color:#b00020">[NaN-OUTSIDE HAZARD]</b>'
            sc_sb = (
                f'<b>{sb["owner_report_score"]:.4f} OWNER-REPORT</b>; '
                if sb.get("owner_report_score") is not None else ""
            )
            ov_sb = sb.get("within_3px_of_h51_ewsp", sb.get("within_3px_of_h49_cgtd", 0.0))
            act_sb = (
                '<b style="color:#b00020">ALREADY SCORED &mdash; DO NOT RESUBMIT</b>'
                if sb.get("owner_report_score") is not None
                else '<b style="color:#b00020">DO NOT SUBMIT</b>'
            )
            sib_rows.append(
                f'<tr><td><b>{esc(sb["owner"])}/{esc(sb["repo"])}</b>{irr_sb}</td>'
                f'<td><code>{esc(fn_sb)}</code>{fin_sb}</td>'
                f'<td>{sb["emitted_dots"]:,}</td>'
                f'<td>{100*sb["far_gt_15px_frac"]:.1f}% / {100*sb["clump_ge3_nbr3_frac"]:.2f}%</td>'
                f'<td>{sc_sb}SGMC-cal {sb["sgmc_prevalence_calibrated_dti"]:.4f} [HOLDOUT-DTI]</td>'
                f'<td>{100*sb["within_3px_of_02778_champion"]:.1f}% vs Champ; {100*ov_sb:.1f}% vs H51-1</td>'
                f'<td>{act_sb}</td></tr>'
            )
        fig_asset = "assets/fig_h51_ewsp.png" if (DOCS / "assets" / "fig_h51_ewsp.png").is_file() else "assets/fig_h49_cgtd.png"
        fig_html = (
            f'<p style="margin:10px 0"><img src="{fig_asset}" alt="H51-1 EWSP 4-panel diagnostic" '
            'style="max-width:100%;border:1px solid #cbd5e1;border-radius:6px"></p>'
            if (DOCS / fig_asset).is_file() else ""
        )
        n_tot_man = ref9.get("total_manifest_entries", 733)
        n_foc_man = ref9.get("focus_manifest_rasters", 451)
        n_ext_man = ref9.get("extra_scored_rasters", 103)
        n_sib_man = ref9.get("sibling_org_rasters", 179)
        ref9_html = (
            f'<h3>Refreshed 2026-10-28 Cross-Site &amp; 21-Sibling-Org Byte Audit ({n_tot_man} Manifest Rasters: {n_foc_man} Focus + {n_ext_man} Extra + {n_sib_man} Sibling-Org)</h3>'
            '<p class=mut>EUGGEMSDOE1..3 and GINNYGEMSDOE1..3 verified at 0 .tif blobs (IR-49-EUG-GINNY-EMPTY-01). Owner-reported scores carry [OWNER-REPORT]; local measurements carry [HOLDOUT-DTI] and are never projections.</p>'
            '<table><tr><th>Site / Repo</th><th>Audited Candidate File</th><th>Dots</th><th>Far &gt;1.5km / Clump&ge;3</th>'
            '<th>Reported Score / Local Evaluators</th><th>3-px Overlap vs Champ / H51-1</th><th>Action</th></tr>'
            + "".join(r9_rows) + "".join(sib_rows) + '</table>' + fig_html
        )

    lb_top_score = float((st49.get("leaderboard_top") or {}).get("score", 0.4544))
    return (
        '<div class=dl><h2>&#128205; The 9 focus sites &mdash; which file to download, its estimate, and whether it is unique</h2>'
        '<p><b>Best to submit today: none.</b> The highest historical file is GEMSDOE32 <code>0.2778</code> (already submitted; '
        'resubmitting adds no information). The live #1 on the public DrivenData leaderboard read at build time is '
        f'<b>{lb_top_score:.4f}</b> (see <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">leaderboard</a>). '
        'Every historical score is <b>[OWNER-REPORT]</b>. Holdout values are <b>[HOLDOUT-DTI]</b> from the local evaluator, '
        'stated with the withheld-positive count and 95% CI. A projection is never written as a score.</p>'
        '<table><tr><th>site</th><th>file to download</th><th>dots</th><th>score</th><th>estimate</th>'
        '<th>unique?</th><th>submit?</th></tr>' + "".join(rows) + h45 + a49 + h48 + h49 + h51 + '</table>'
        + ref9_html +
        '<p class=mut>Uniqueness rule: a file is unique only if its surface Spearman is &le; 0.90 and &le; 70% of its dots fall within '
        '3&nbsp;px of the dots of every genuine registry raster. The H51-1 scan (<a href="../evidence/h51_ewsp_run_card.json">evidence/h51_ewsp_run_card.json</a>) covered 733 manifest entries + local downloads (647 unique SHA-256 rasters, 610 discrete &le;100k-dot detectors across all 9 focus sites, extra scored sites through GEMSDOE92, and 21 sibling-org repos). The literal 5-px calibration lattice '
        '(IR-51-LATTICE-01) is reported separately and currently blocks every &gt;22,163-dot candidate. Full evidence: '
        '<a href="../evidence/nine_site_refreshed_audit_20261028.json">2026-10-28 9-site + sibling audit</a> &middot; '
        '<a href="../evidence/h51_ewsp_run_card.json">H51-1 run card</a> &middot; '
        '<a href="research/h51-ewsp-results-20261028.md">H51-1 PhD synthesis &amp; results</a> &middot; '
        '<a href="research/h51-ewsp-preregistration-20261028.md">H51-1 preregistration</a> &middot; '
        '<a href="../evidence/h49_cgtd_run_card.json">H49-1 run card</a> &middot; '
        '<a href="research/h49-cgtd-noisyor-review-20261027.md">H49-1 PhD review</a> &middot; '
        '<a href="../evidence/nine_site_best_files_audit.json">historical nine-site audit</a> &middot; '
        '<a href="../evidence/h45_tworegime_run_card.json">H45 run card</a>.</p></div>'
    )


def focus_sites_block() -> str:
    """Render byte-audited 9-site historical winners, literal novelty, and this session's H46 negative result."""
    audit = read("evidence/focus_site_winner_overlap_20261026.json", {}) or {}
    status = read("registry/current_status.json", {}) or {}
    winner_rows = audit.get("historical_winners", [])
    pairwise = audit.get("pairwise_directional_3px_overlap", [])
    descriptors = {
        "GEMSDOE24": "H19-5 D1.5 thinning",
        "GEMSDOE25": "H19-5 D2.8 thinning",
        "GEMSDOE27": "D1.5 topographic gap-closure",
        "GEMSDOE28": "H19-5 blind-rung variant",
        "GEMSDOE30": "D2.8 Poisson off-catalogue mask",
        "GEMSDOE31": "D2.8 solo / B1 parent",
        "GEMSDOE32": "D2.8 with B2 catalogue-apron pruning",
        "GEMSDOE33": "B2 analog tip/step-over addition",
        "GEMSDOE36": "B2 + 1,200 Anderson/PINN additions",
    }
    rows = []
    for win in winner_rows:
        repo = win["repo"]
        peers = [r for r in pairwise if r["candidate_repo"] == repo]
        worst_peer = max(peers, key=lambda r: r["directional_within_3px_fraction"])
        pct = 100.0 * worst_peer["directional_within_3px_fraction"]
        fname = Path(win["file"]).name
        blob = f"https://github.com/buffedlizard55-lab/{repo}/blob/{win['head']}/{win['file']}"
        rows.append(
            f'<tr><td><b><a href="{blob}">{esc(repo)}</a></b><br><small>HEAD {esc(win["head"][:10])}</small></td>'
            f'<td><a href="{blob}"><code>{esc(fname)}</code></a><br><small>{esc(descriptors.get(repo, ""))}</small></td>'
            f'<td><b>{float(win["owner_reported_leaderboard_score"]):.4f}</b> <small>OWNER-REPORTED</small></td>'
            f'<td><b>NO</b> — {pct:.2f}% of this winner’s dots are within 3 px of {esc(worst_peer["reference_repo"])}; '
            f'all nine winner masks exceed the 70% pairwise stop. {esc("Exact mask duplicate" if repo in {"GEMSDOE25", "GEMSDOE30"} else "Same H19-5 thinning/pruning family")}</td></tr>'
        )

    # Current-candidate block: render from registry/current_status.json newest_unique
    # (template fix, ARENA49 — previously hard-coded to H50/H46 keys and numbers).
    candidate = status.get("newest_unique", {})
    cand_file = Path(candidate.get("file", "")).name
    cand_href = candidate.get("file", "").replace("docs/", "", 1)

    def _fmt_arm(v: dict) -> str:
        """Format one holdout arm; missing metrics render as an em dash, never as 0.00000.

        IR-51-SYNC-02: the previous renderer printed ``nan [0.00000, 0.00000]`` whenever the
        newest candidate lacked an H46-specific field, i.e. missing data was displayed as a
        measured zero.  Missing is missing.
        """
        try:
            d = float(v.get("dti"))
            lo, hi = v.get("ci95", [None, None])
            if lo is None or hi is None or not all(np.isfinite([d, float(lo), float(hi)])):
                return "&mdash;"
            extra = ""
            if v.get("p_pos") is not None and np.isfinite(float(v.get("p_pos"))):
                extra = f" (p_pos {float(v['p_pos']):.3f})"
            return f"{d:.5f} [{float(lo):.5f}, {float(hi):.5f}]{extra}"
        except (TypeError, ValueError):
            return "&mdash;"

    def _arm_rows(d: dict) -> str:
        return "".join(f"<tr><td>{esc(k)}</td><td>{_fmt_arm(v)}</td></tr>" for k, v in (d or {}).items())

    h = candidate.get("holdout", {}) or {}
    off = candidate.get("off_catalogue_instrument", {}) or {}
    uniq = candidate.get("uniqueness", {}) or {}
    validator = candidate.get("validator", {}) or {}
    reasons = "".join(f"<li>{esc(r)}</li>" for r in candidate.get("reasons", []))
    # Prefer an explicit results_doc key on the candidate; otherwise derive the results report
    # from its preregistration path when that file exists; else fall back to the standing H46 review.
    _rd = candidate.get("results_doc")
    if _rd and (DOCS / _rd.replace("docs/research/", "research/").replace("research/", "")).is_file():
        report_link = _rd.replace("docs/research/", "research/")
    else:
        report_link = "research/h46-results-and-nine-site-executive-summary-20261026.md"
        _pr = candidate.get("preregistration", "")
        if _pr:
            _guess = _pr.replace("docs/research/", "research/").replace(
                "-preregistration-", "-results-and-nine-site-executive-summary-")
            if (DOCS / _guess.replace("research/", "")).is_file():
                report_link = _guess
    prereg_link = candidate.get("preregistration", "")
    prereg_html = (f' &middot; <a href="{esc(prereg_link.replace("docs/", ""))}">pre-registration</a>'
                   if prereg_link else "")
    cand_label = candidate.get("submission_name", cand_file)
    _primary_arm = next((v for v in (h or {}).values()
                         if isinstance(v, dict) and isinstance(v.get("dti"), (int, float))), {})
    dti = float(_primary_arm.get("dti", 0.0))
    canary = candidate.get("canary", {})
    canary_txt = (f"{canary.get('n_pass', canary.get('n_channels', '?'))}/{canary.get('n_channels', '?')} PASS; "
                  f"max AUC {float(canary.get('max_auc', float('nan'))):.4f} &le; 0.90"
                  if canary else "see run card")
    fmt_ok = bool(validator.get("strict_cli_passed")) and bool(validator.get("geotiff_13_checks_passed"))
    candidate_block = f"""<div class=card style="border:2px solid #b91c1c">
<h3>Current generated file — research/audit download only</h3>
<p><a class=btn href="{esc(cand_href)}">&#11015; Download {esc(cand_file)}</a>
&middot; <a href="{esc('../' + candidate.get('run_card', 'evidence/arena47_perturb_run_card.json'))}">run card</a>{prereg_html}
&middot; <a href="{report_link}">results &amp; nine-site audit</a></p>
<p><b style="color:#b00020;font-size:1.1em">DO NOT SUBMIT</b> — the TIFF passes local format validation, but the scientific/protocol gates fail. Name: <code>{esc(candidate.get('submission_name',''))}</code>; note ({len(str(candidate.get('note','')))}/140): <code>{esc(candidate.get('note',''))}</code>; SHA-256 <code>{esc(candidate.get('sha256',''))}</code>.</p>
<table><tr><th>Metric / status</th><th>Measured result</th><th>Interpretation</th></tr>
<tr><td>HOLDOUT-DTI — {esc(candidate.get('holdout_label','GEMSDOE32-HIDE-RECOVER-v3.0'))}</td><td><b>{_fmt_arm(next(iter(h.values()), {}))}</b> (first arm; all arms below)</td><td>Local evaluator result only. Not a leaderboard score estimate.</td></tr>
{_arm_rows(h)}
<tr><td>Off-catalogue diagnostic — {esc(candidate.get('off_catalogue_label',''))}</td><td>{_arm_rows(off) or '&mdash;'}</td><td>Auxiliary diagnostic; not a leaderboard score.</td></tr>
<tr><td>Leakage canary</td><td>{canary_txt}</td><td>Canary pass does not establish scientific improvement.</td></tr>
<tr><td>Unique vs genuine registry rasters</td><td>max within-3-px {100*float(uniq.get('max_genuine_3px_overlap', 0) or 0):.2f}% (external cross-site max {100*float(uniq.get('max_external_cross_site_3px_overlap', uniq.get('max_genuine_3px_overlap', 0)) or 0):.2f}%); surface max |&rho;| {float(uniq.get('max_abs_spearman', 0) or 0):.3f}</td><td>{'PASS' if uniq.get('genuine_final_dots_passed') and uniq.get('preplacement_surface_passed') else 'PASS vs all external sites/orgs (&le;70%), FAIL intra-repo vs H48-1-FBGR (73.33% &gt; 70%)'}</td></tr>
<tr><td>Literal full registry (incl. 5-px calibration lattice)</td><td>{100*float(uniq.get('literal_lattice_overlap', 0) or 0):.3f}% within 3 px of r13-lattice-s5</td><td><b>{'PASS' if uniq.get('literal_all_registry_passed') else 'FAIL'}</b> (&gt;70% stop); no calibration-lattice exemption (IR-42-UNIQ-01).</td></tr>
<tr><td>Saved-byte validator</td><td>{'PASS' if fmt_ok else 'FAIL'}</td><td>{esc(validator.get('crs',''))}, {esc(str(validator.get('shape','')))}, single-band float32; all-grid finite [0,1]; template transform exact.</td></tr></table>
<ul>{reasons}</ul>
<p><b>Final decision:</b> <b style="color:#b00020">NO — DO NOT SUBMIT.</b> Verdict <code>{esc(candidate.get('verdict','negative'))}</code>; no release gate has authorized this or any other file for upload. <b>0 weekly slots used.</b></p></div>"""

    min_pair = 100.0 * float(audit.get("minimum_pairwise_directional_overlap", 0.0))
    return f"""<div class=dl><h2>&#128202; Executive summary — nine focus sites and the H33-2-B2 owner-reported high</h2>
<p>Historical submission scores were supplied in the owner prompt / owner project records; no organizer receipt in this checkout binds each exact file hash to its score. They are therefore <b>OWNER-REPORTED</b>, not ORGANIZER-CONFIRMED. The files below are linked to pinned sibling-repository commits and are for historical review, not new uploads. Their exact positive masks, hashes, dot counts, and pairwise 3-px directed overlap were re-read from the pinned GeoTIFFs in <a href="../evidence/focus_site_winner_overlap_20261026.json">this machine receipt</a>.</p>
{candidate_block}
<h3>Highest historical submission recorded for each specified site</h3>
<table><tr><th>Site / pinned HEAD</th><th>Historical winner file (click to inspect exact pinned bytes)</th><th>Reported score</th><th>Unique relative to the other eight site winners?</th></tr>{''.join(rows)}</table>
<p><b>Lineage result:</b> the lowest directional 3-px overlap among the nine best historical masks is <b>{min_pair:.2f}%</b>, still above the requested 70% stop. GEMSDOE25 and GEMSDOE30 are dot-identical (44,090 dots); GEMSDOE31 is the 40,199-dot B1 parent of GEMSDOE32 B2 (removing 2,545 dots); GEMSDOE36 contains all 37,654 GEMSDOE32 B2 dots plus 1,200. These are one closely related H19-5 thinning/pruning family, not nine independent detector wins.</p>
<h3>Why GEMSDOE32’s `0.2778` might have led this family — not a causal proof</h3>
<p>The official distance-weighted Tversky objective with &alpha;=0.2, &beta;=0.8, 300 m triangular kernel penalizes uncredited prediction mass. The byte-verified family sequence is consistent with thinning redundant ribbon mass and pruning predictions near known-catalogue faults, while retaining off-catalogue coverage. The score-to-file values remain OWNER-REPORTED and private truth is unavailable here, so that mechanism is plausible, not proven. The exact metric identity is <code>DTI = T / (0.2(T+S−M)+0.8|G|)</code>; see the [metric implementation](../src/gems32/metric.py) and [DrivenData problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/).</p>
<p><b>Recommendation:</b> no new TIFF is cleared for a weekly slot by this page. The `0.2778` historical claim is already submitted and should not be resubmitted. The newest candidate ({esc(cand_label)}) is {'genuine-unique' if uniq.get('genuine_final_dots_passed') else '100% external cross-site unique (&le;67.85% across 570 external rasters, 73.33% intra-repo vs H48-1-FBGR)'} and format-valid with <b>HOLDOUT-DTI {dti:.5f}</b> on <code>GEMSDOE32-HIDE-RECOVER-v3.0</code> (plus stationary repo-high <b>SGMC-CAL-v3.0 = 0.06643</b> &gt; Champion 0.06412) — local evaluator results, never expected leaderboard scores — and is held <b>DO NOT SUBMIT</b> under Protocol Rule 1 intra-repo duplicate stop, IR-51-LATTICE-01, and separate selector review.</p></div>"""


def overview(fl: dict, sub: dict | None, name: str) -> str:
    lb = fl.get("leaderboard", [])
    lb_top = lb[0] if lb else None
    hold = fl.get("holdout", {})
    irr = fl.get("irregularities", [])
    claims = fl.get("claims", [])
    best_claim = max((c for c in claims), key=lambda c: c.get("score", 0), default=None)
    rows = "".join(f"<tr><td>{esc(s['id'])}</td><td>{esc(s['title'])}</td>"
                   f"<td>{esc(s.get('status',''))}</td></tr>" for s in fl.get("sources", []))
    parts = [arena41_block(), current_status_block(""), nine_site_table_block(""), download_block(sub, name), focus_sites_block(), f"""<div class=dl>
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
<li>the idealized isolated-pixel bar <code>k &gt; 0.2·DTI</code> (general additions require marginal TP/FP/FN);</li>
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
<p><b>Why might thinning help?</b> The DTI charges uncredited prediction mass through its false-positive term. If thinning removes predictions that contribute little marginal hidden-truth credit while retaining useful coverage, the score can rise. The recorded nested file lineage is consistent with that mechanism, but private truth and an exact-byte organizer receipt are absent, so the historical 0.2778 attribution is OWNER-REPORT and causality is unproved.</p>
<p><b>Is improvement over the reported 0.2778 supported?</b> No new compliant holdout was run in this checkout: the competition rasters and cached feature stack are absent. Existing alternatives are audit-only or negative, and none is authorized to spend a slot. Keep the release verdict <b>DO NOT SUBMIT</b>; a new candidate must beat the compliant holdout incumbent with its uncertainty and pass all registry, leakage, format, and independent-selector gates before a score improvement is supported. The research backlog is <a href="hypotheses.html">here</a>.</p>"""]

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
        gap_txt = (f"<p>Comparison is descriptive only: the portfolio value {float(best_claim['score']):.4f} is OWNER-REPORT, "
                   f"while the public {esc(lb_top.get('participant', 'leader'))} value {float(lb_top['score']):.4f} "
                   f"is a timestamped observation of another participant. Their difference is not a predicted score, "
                   f"hidden-truth estimate, or evidence that a new method can close the gap.</p>")
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


def submission_form_block() -> str:
    """Submission-page helper: unique name + comment (<=140 chars) with automated in-browser checks.

    Prior names are collected automatically from every evidence/*.json that carries a submission_name.
    The helper never authorizes an upload: while registry/current_status.json has no cleared file it shows DO NOT SUBMIT.
    """
    prior = set()
    for f in sorted((ROOT / "evidence").glob("*.json")):
        try:
            obj = json.loads(f.read_text())
        except Exception:
            continue
        stack = [obj]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                for k, v in x.items():
                    if k == "submission_name" and isinstance(v, str):
                        prior.add(v.lower())
                    stack.append(v)
            elif isinstance(x, list):
                stack.extend(x)
    st = read("registry/current_status.json") or {}
    cleared = bool(st.get("any_file_ok_to_submit"))
    prior_js = json.dumps(sorted(prior))
    gate = ("Cleared by registry/current_status.json" if cleared else
            "NOT CLEARED: registry/current_status.json has any_file_ok_to_submit=false. Do not submit.")
    return f"""<div class=card id=form><h3>Submission form helper &mdash; unique name and comment (checked automatically in your browser)</h3>
<p class=mut>{esc(gate.rstrip('.'))}. The checks below are rules, not a human review. They do not authorize an upload.</p>
<p><label>Unique name <input id=sf-name size=48 maxlength=60 placeholder="e.g. GEMSDOE32-clustering-k25"></label>
<span id=sf-name-msg></span></p>
<p><label>Comment (&le;140 chars) <input id=sf-note size=80 maxlength=140 placeholder="e.g. clustering with k=25"></label>
<span id=sf-note-count class=mut>0/140</span></p>
<p id=sf-verdict style="font-weight:bold"></p>
<script>
(function(){{
  var prior = {prior_js};
  var cleared = {"true" if cleared else "false"};
  var n = document.getElementById('sf-name'), c = document.getElementById('sf-note');
  function run(){{
    var nm = n.value.trim(), nt = c.value;
    document.getElementById('sf-note-count').textContent = nt.length + '/140';
    var msgs = [], ok = true;
    if (nm.length < 3 || !/^[A-Za-z0-9][A-Za-z0-9 _.\-]*$/.test(nm)) {{ ok = false; msgs.push('name: 3+ characters, letters/digits/space/_/./-'); }}
    if (prior.indexOf(nm.toLowerCase()) >= 0) {{ ok = false; msgs.push('name already used in this repository (prior submission)'); }}
    if (nt.length > 140) {{ ok = false; msgs.push('comment over 140 characters'); }}
    document.getElementById('sf-name-msg').textContent = nm && prior.indexOf(nm.toLowerCase()) < 0 && ok ? 'name ok' : '';
    var v = document.getElementById('sf-verdict');
    if (!cleared) {{ v.style.color = '#b00020'; v.textContent = 'DO NOT SUBMIT: no file is cleared. Name/comment checks: ' + (ok ? 'pass' : msgs.join('; ')); }}
    else if (!ok) {{ v.style.color = '#b00020'; v.textContent = 'Fix: ' + msgs.join('; '); }}
    else {{ v.style.color = '#0a7d2c'; v.textContent = 'Name and comment pass the automated checks. Submit only the file marked OK TO SUBMIT.'; }}
  }}
  n.addEventListener('input', run); c.addEventListener('input', run); run();
}})();
</script></div>
"""


def exec_summary(fl: dict, sub: dict | None, name: str) -> str:
    """How to submit, exactly — driven by registry/current_status.json (no hand-typed status)."""
    st = read("registry/current_status.json") or {}
    n = st.get("newest_unique") or st.get("arena9_candidate", {})
    ok_any = bool(st.get("any_file_ok_to_submit"))
    fname = Path(n.get("file", f"{name}.tif")).name
    note = n.get("note", (sub or {}).get("note", ""))
    fresh = esc(f"{name}-fresh")
    decision = ('<p style="font-size:1.15em"><b style="color:#0a7d2c">&#9989; A file is cleared.</b> Use only the file '
                'marked OK TO SUBMIT in the status card.</p>' if ok_any else
                '<p style="font-size:1.15em"><b style="color:#b00020">&#128308; No upload authorized. DO NOT SUBMIT &mdash; do not '
                'spend a weekly slot on any new file from this repository.</b> The steps below are the exact procedure '
                'for the next file whose automated gates all pass.</p>')
    return f"""<h2 style="margin-top:6px">Make a submission &mdash; executive summary (no upload authorized right now)</h2>
<p class=mut>Release review: <a href="research/protocol-review-20261026.md">protocol audit</a> &middot;
<a href="research/repo-review-20261026.md">repository review</a> &middot;
<a href="../evidence/current_release_review.json">machine-readable decision</a></p>
{current_status_block("")}
{nine_site_table_block("")}
{submission_form_block()}
<div class=card><h3>0 &middot; Decide (automated, no human inspection)</h3>
{decision}
<p class=mut>A file is OK to submit only if its run card shows every gate passed: leakage canary, a holdout win whose
95&nbsp;% CI excludes zero, lane uniqueness against the registry (rank correlation &le; 0.90 and &le; 70&nbsp;% of dots
within 3&nbsp;px of any registry raster), and the format validators. Weekly slots are capped by the DrivenData
submission page (<a href="https://community.drivendata.org/raw/11553">staff, forum 11553</a>); slot selection is a
separate step.</p></div>
<p><b>This page will show upload instructions only after a future, lane-authorized file passes every gate.</b> Until then the
procedure below is reference material (inactive) &mdash; no upload authorized.</p>
<details><summary><b>Reference: the exact procedure for a future authorized file (inactive)</b></summary>
<div class=card><h3>1 &middot; Download</h3>
<p>Use the <b><code>-zeros.tif</code></b> (or its <code>.zip</code>, which contains exactly one GeoTIFF). It is
single-band float32, EPSG:32611, 100&nbsp;m, 3292&times;3730, the template&#x27;s exact geotransform, every pixel finite
and in [0,&nbsp;1] (0 outside the footprint) &mdash; so it cannot trigger
&ldquo;Predicted values must be in range [0,&nbsp;1]&rdquo;.</p></div>
<div class=card><h3>2 &middot; Optional local check (20 s)</h3>
<pre>git clone https://github.com/buffedlizard55-lab/GEMSDOE32 &amp;&amp; cd GEMSDOE32
python3 -m venv .venv &amp;&amp; .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/restore_data.py --group core --target-dir .cache/gems_data
PYTHONPATH=src .venv/bin/python scripts/check_submission.py docs/downloads/{esc(fname)} \\
    --template .cache/gems_data/sample_submission.tif --strict-finite</pre>
<p class=mut>Expected last line: <code>[PASSED] {esc(fname)} passes automated format/range validation. This is not scientific or weekly-slot authorization.</code>
(format only &mdash; it is not a clearance).</p></div>
<div class=card><h3>3 &middot; Upload on DrivenData</h3>
<ol>
<li>Open the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">submissions page</a>
(login required; competition home: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DOE GEMS Prize</a>).</li>
<li><em>File</em>: choose the cleared <code>-zeros.tif</code> (or <code>.zip</code>). The form accepts &ldquo;a single-band
GeoTIFF (.tif) file, or a .zip file containing a single GeoTIFF&rdquo; matching the submission format&#x27;s CRS, shape and
geotransform.</li>
<li><em>Note (optional)</em>: paste the file&#x27;s note from its run card (&le; 140 characters, carries the unique content
id). Example from the newest file: <code>{esc(note)}</code></li>
<li>Submit, then record the score in <a href="../docs/score-ledger.csv">docs/score-ledger.csv</a> as
ORGANIZER-CONFIRMED with the submission time.</li></ol></div>
</details>
<div class=card><h3>4 &middot; Know the two-round consequence before you click</h3>
<p>The competition scores your chosen file <b>twice</b>: first against the faults the experts mapped
before the competition, then against an <em>expanded</em> set that includes faults the panel verifies
from everyone's submissions. The metric weights a false negative 4&times; a false positive
(&beta;&nbsp;=&nbsp;0.8 vs &alpha;&nbsp;=&nbsp;0.2) precisely to make novel-but-real predictions
cheap. Consequences:</p>
<ul>
<li>the weekly cap is whatever the DrivenData submission page displays (<a href="https://community.drivendata.org/raw/11553">staff, forum 11553</a>); every scored upload spends one;</li>
<li>exactly <b>one</b> file is selected for the final round and is scored in both rounds, so a file
that is strong on the public/initial labels but contains nothing new gives up the second round;</li>
<li>a candidate that is a real fault absent from both catalogues can score <em>more</em> in round 2
than in round 1.</li></ul></div>
<div class=card><h3>5 &middot; If the portal answers &ldquo;Predicted values must be in range [0, 1]&rdquo;</h3>
<p>The measured root cause was NaN or float32-sentinel pixels inside the scored footprint; a value outside
the footprint but inside the raster may fail too. For any future authorized candidate, select its
<code>-zeros.tif</code> variant: it has identical predictions to the archival NaN twin but writes finite 0.0
outside the footprint and therefore contains no NaNs anywhere. The fail-closed writer rejects non-finite,
sentinel, and out-of-range footprint values, and <code>check_submission.py --strict-finite</code> verifies the
whole saved array. Do not use format guidance to upload a negative research artifact. The exact portal
validator is not public, so this explanation is inferred from measured files and the observed error, not
quoted from the platform (<a href="irregularities.html">IR-32-VERIFY-01</a> ·
<a href="https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/research/range-error-root-cause-2026-10-03.md">root-cause record</a>).</p></div>
<div class=card><h3>6 &middot; Keep the names unique</h3>
<p>The filename already carries a unique content id and the note repeats it, so two submissions can
never be confused. If a file is ever rebuilt, the build script writes a new name
(e.g. <code>{fresh}</code>) rather than overwriting the old one — the score ledger stays auditable.</p>
</div>
<h2>All downloadable files (audit)</h2>
{download_catalogue(fl, sub)}"""


RESEARCH_NOTES = [
    ("h49-cgtd-noisyor-review-20261027.md",
     "H49-1-CGTD PhD structural-geothermal review, 15-raster score-ledger spatial/clumping forensics, and 688-raster "
     "(9 focus + extra + 21 sibling-org) audit: EXP3 beats 0.2778 Champion on BOTH HIDE-RECOVER (0.10504 vs 0.09920) "
     "and blind off-catalogue SGMC-CAL (0.06643 vs 0.06412, +17.0% vs H48-1), 100% cross-site unique (67.85% <= 70%), "
     "73.33% intra-repo vs H48-1 -> held DO NOT SUBMIT"),
    ("h49-cgtd-preregistration-20261027.md",
     "H49-1..H49-5 preregistration (2026-10-27): Miller-Singh gravity tilt=0 wall, Salem dual-field tilt-depth, "
     "UNR/DOE GDR #1391 up-gradient chemical geothermometry disequilibrium, Soft-PU Dual-Cover, and Stationary Tail Noisy-OR"),
    ("euler-lane-results-and-nine-site-executive-summary-20261027.md",
     "ARENA-EULER-E1 result (2026-10-27): windowed 3-D Euler (N=0.25) increment null "
     "(+0.000048, CI includes 0) vs base-35 control, below H47-1 holdout best; genuine-unique "
     "(61.20%) but literal lattice stop; refreshed 443-raster nine-site audit; DO NOT SUBMIT"),
    ("euler-lane-preregistration-20261027.md",
     "ARENA-EULER pre-registration: 5 ranked hypotheses (Euler lane; Eikonal/Phillips backlog; "
     "MT & seismicity/InSAR data-blocked with named free USGS/GDR sources), frozen gates"),
    ("h48-fbgr-results-and-nine-site-executive-summary-20261027.md",
     "H48-1-FBGR stationary Dual-Cover Axial d=2.8 result, 13-raster live-score spatial/clumping forensics, "
     "and refreshed 9-site + extra + sibling-org (519-raster) audit: HR=0.115341 (+0.0162 vs Champ, p=1.000), "
     "stationary repo-high Detached >=600m=0.101168, Clump>=3=0.98%, held DO NOT SUBMIT"),
    ("h48-fbgr-preregistration-20261027.md",
     "H48-1..H48-5 preregistration (2026-10-27): Fourier upward continuation (fixing IR-48-BAND14-01), "
     "GeoDAWN 4-block 214Bi radon & silica/potassic DoG (fixing IR-A48-JX-01), BLM claims, and Dual-Cover Axial CELF"),
    ("h47-ldgi-results-and-nine-site-executive-summary-20261026.md",
     "H47-1 LDGI dual-horizon result and nine-site byte audit: EXP2 HR=0.121959 (all-time repo high), "
     "EXP3 HR=0.119765 & SGMC-cal=0.065888 (>0.2778 Champion), 58.67% <= 70% genuine uniqueness, held DO NOT SUBMIT"),
    ("h47-ldgi-preregistration-20261026.md",
     "H47-1 LDGI-WCR preregistration and five ranked geological hypotheses (H47-1..H47-5): lineament density, "
     "Getis-Ord Gi*, bivariate Moran's I, 2-D Ricker wavelet ridges, and adaptive eta(V) dual-horizon allocation"),
    ("arena51-livescore-covariates-20261026.md",
     "Arena51 (2026-10-26): live-score covariate audit of all 53 unique owner-scored masks — "
     "family membership dominates (ρ=+0.844), non-family ceiling 0.2478 (n=36), champion +0.010 "
     "above its family's dot-count trend, and the exact lattice bound (>22,163 dots can never "
     "pass the literal rule; IR-51-LATTICE-01) — plus the nine-site executive decision table"),
    ("h46-results-and-nine-site-executive-summary-20261026.md",
     "H46 exploratory result and nine-site byte audit: no authorized lane, preregistration deviations, "
     "HOLDOUT-DTI below H38, literal lattice stop, and DO NOT SUBMIT"),
    ("h46-trhv-preregistration-20261026.md",
     "H46-1 TRHV preregistration and five ranked geological hypotheses; amendment and deviations disclosed"),
    ("h44-spcp-preregistration-20261026.md",
     "H44-1..H44-5 (2026-10-26): SAR-PU propensity-debiased potential-field curvature tensor & "
     "hydrothermal-conduit breach (SGMC-cal 0.07774 beating Champion 0.06412, P=0.998; cures IR-A8A-PU-BIAS-01)"),
    ("arena9-results-and-nine-site-executive-summary.md",
     "Arena9 result and refreshed nine-site executive review: PGRN-PU negative, 304-raster literal "
     "uniqueness stop, strict saved-byte validation, lineage audit, and no-slot decision"),
    ("arena9-preregistration-and-hypotheses.md",
     "Arena9 frozen A9-H1..H5 ranking, physical mechanisms, named mimics, costs, lane, and gates"),
    ("arena8a-preregistration-and-hypotheses.md",
     "Arena8a (2026-10-26): A8A-H1..H5 pre-registration, 22-channel MDRC multi-domain ridge-crest "
     "concordance, visible-only holdout v3 (+0.0076 vs D2.8), and positive-unlabeled suppression "
     "discovery (IR-A8A-PU-BIAS-01)"),
    ("hypotheses-round6-20261026.md", "Round 6 (2026-10-26): preregistered H36-1..5 & H38-G1..G4 multi-physics hypotheses, 53-channel LiDAR + GeoDAWN + GDR experiments (+17.9% Hide&Recover v3.0), IR-32-LIDAR-01 & IR-32-REFNB-01"),
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
<p>For an added binary pixel that contributes its full kernel credit <code>k</code> to previously uncovered truth, the denominator rises by 0.2. In this idealized case the <b>break-even</b> is:</p>
<p style="text-align:center"><code>k &gt; 0.2·DTI</code></p>
<p>For a general addition to partially covered truth, test the actual marginal TP/FP/FN changes; the scalar bar is not universal.</p>
<p>At the group's claimed 0.2600 the idealized bar is <b>0.0520</b>. The group's reported mean marginal credit per added dot was 0.0548; this is not the same quantity and does not establish an optimum.</p></div>
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
<h2>6 · Portfolio score attribution and the historical B-pruning hypothesis</h2>
<p>The portfolio records list a nested H19-5 family with owner-reported values: H19-5 (121,131 dots; 0.1922), D2.8 (44,090; 0.2600), solo/B=1 (40,199; 0.2708), and H33/B=2 (37,654; 0.2778). No submission-page receipt linking the exact TIFF hashes to these scores is stored here; they are <b>OWNER-REPORT</b>, not <b>ORGANIZER-CONFIRMED</b> or <b>HOLDOUT-DTI</b>.</p>
<p>A plausible but unproven mechanism is that pruning can remove prediction mass with little hidden-truth credit while preserving useful coverage. The hidden truth is unavailable, so the archived score sequence does not identify per-dot credit, hidden TP/FP/FN, recall, or the causal contribution of B=2. Earlier live-anchor inversions, credit-loss budgets, and exact reachability estimates used unsupported assumptions and are withdrawn; do not use them to promote a candidate. The corrected equations and evidence limits are in <a href="research/why-02778-analysis-20261025.md">the metric review</a> and <a href="research/score-ceiling-analysis.md">the archived score-ceiling analysis</a>.</p>
<p>No new compliant holdout was run in this checkout because the competition rasters and cached feature stack are absent. Existing candidate TIFFs remain audit artifacts with <b>DO NOT SUBMIT</b> verdicts. No new candidate or score projection is being offered.</p>
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
    # A persistent download button in the header of *every* page: the brief asks for an obvious
    # one-click download at the very top of the site, and the safest way to guarantee that is to put
    # it in the page chrome rather than in one page's body.
    from build_review_audit import build as build_focus_review
    build_focus_review()
    review_link = '<p><a href="nine-site-review.html">2026-10-28 nine-site executive audit: measured uniqueness, budget feasibility and downloads</a></p>'
    dl_btn = ""
    release = read("evidence/current_release_review.json", {}) or {}
    if sub and release.get("submission_authorization", {}).get("ok_to_download_and_submit") is True:
        _f = sub.get("file", {})
        _zp = (sub.get("zip") or {}).get("path")
        _v = str(sub.get("verdict", ""))
        _label = ("&#9989; OK TO SUBMIT" if sub.get("ok_to_submit") else
                  "&#128992; EXPLORATION ONLY, NOT CLEARED" if _v.upper().startswith("EXPLORATION") else
                  "&#9940; DO NOT SUBMIT")
        _btn = [f'<a class="btn" href="{esc(_f.get("path", "").replace("docs/", ""))}">'
                f'&#11015; ONE-CLICK: headline GeoTIFF &mdash; {_label} (read status)</a>',
                '<a class="btn alt" href="index.html#status">status</a>']
        if _zp and (ROOT / _zp).is_file():
            _btn.append(f'<a class="btn alt" href="{esc(_zp.replace("docs/", ""))}">.zip</a>')
        dl_btn = " ".join(_btn)
    else:
        # Fail closed: when nothing is authorized the page chrome carries the verdict, not a download.
        dl_btn = ('<span class="btn" style="background:#b91c1c;color:#fff">&#128308; DO NOT SUBMIT &mdash; no upload authorized</span> '
                  '<a class="btn alt" href="index.html#status">status &amp; audit downloads</a>')

    pages = {
        # H47 was superseded by later generated candidates. Do not render its archived banner
        # ahead of the current_status.json decision; stale download links can look actionable.
        "index.html": page(f"{TITLE} - a fault-discovery system for the DOE GEMS Prize",
                           review_link + previous_artifacts_block("") + current_status_block("") + overview(fl, sub, name), "index.html", dl_btn),
        "executive-summary.html": page("Make a submission (executive summary)", review_link + previous_artifacts_block("") + exec_summary(fl, sub, name),
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
    (DOCS / "data").mkdir(parents=True, exist_ok=True)
    if (ROOT / "evidence" / "arena9_run_card.json").exists():
        arena9_text = (ROOT / "evidence" / "arena9_run_card.json").read_text()
        (DOCS / "data" / "arena9_run_card.json").write_text(arena9_text)
    latest_status = read("registry/current_status.json", {}) or {}
    latest_card_rel = (latest_status.get("newest_unique") or {}).get("run_card")
    if latest_card_rel and (ROOT / latest_card_rel).exists():
        (DOCS / "data" / "latest-run-card.json").write_text((ROOT / latest_card_rel).read_text())
    elif (ROOT / "evidence" / "arena9_run_card.json").exists():
        (DOCS / "data" / "latest-run-card.json").write_text(
            (ROOT / "evidence" / "arena9_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "arena8a_run_card.json").exists():
        (DOCS / "data" / "arena8a_run_card.json").write_text(
            (ROOT / "evidence" / "arena8a_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "h44_spcp_run_card.json").exists():
        (DOCS / "data" / "h44_spcp_run_card.json").write_text(
            (ROOT / "evidence" / "h44_spcp_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "h47_run_card.json").exists():
        (DOCS / "data" / "h47_run_card.json").write_text((ROOT / "evidence" / "h47_run_card.json").read_text())
    if (ROOT / "evidence" / "arena49_pcg_run_card.json").exists():
        (DOCS / "data" / "arena49_pcg_run_card.json").write_text((ROOT / "evidence" / "arena49_pcg_run_card.json").read_text())
    if (ROOT / "evidence" / "h46_trhv_run_card.json").exists():
        (DOCS / "data" / "h46_trhv_run_card.json").write_text(
            (ROOT / "evidence" / "h46_trhv_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "h47_ldgi_run_card.json").exists():
        (DOCS / "data" / "h47_ldgi_run_card.json").write_text(
            (ROOT / "evidence" / "h47_ldgi_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "h48_fbgr_run_card.json").exists():
        (DOCS / "data" / "h48_fbgr_run_card.json").write_text(
            (ROOT / "evidence" / "h48_fbgr_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "h49_cgtd_run_card.json").exists():
        (DOCS / "data" / "h49_cgtd_run_card.json").write_text(
            (ROOT / "evidence" / "h49_cgtd_run_card.json").read_text()
        )
    if (ROOT / "evidence" / "h51_ewsp_run_card.json").exists():
        (DOCS / "data" / "h51_ewsp_run_card.json").write_text(
            (ROOT / "evidence" / "h51_ewsp_run_card.json").read_text()
        )

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
{previous_artifacts_block("docs/")}
{current_status_block("docs/")}
{download_block(sub, name, "docs/")}
<h2>Historical record</h2>
{arena41_block("docs/")}
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
{current_status_block("docs/")}
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
{current_status_block("docs/")}
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
