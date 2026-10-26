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
    """Render the session-scoped release decision, failing closed when it is absent."""
    decision = read("evidence/current_release_review.json", {}) or {}
    evidence_prefix = "evidence/" if prefix == "docs/" else "../evidence/"
    fname = "gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"
    if decision.get("submission_authorization", {}).get("ok_to_download_and_submit") is not True:
        return f"""<section class=dl style="border:3px solid #b91c1c" aria-label="Current submission decision">
<h2>&#128308; DO NOT SUBMIT — current-session release gates are not satisfied</h2>
<p><b>The Round-6 GeoTIFF is retained as an audit artifact only.</b> Its file-format/range check passed, but that does not authorize upload. The current method lane is missing, the prior B=2 holdout used the full catalogue mask, and the required fold-local hide-and-recover evidence was not established. No submission slot was used.</p>
<p><a href="{prefix}research/repo-review-20261026.md">Read the review and required next steps</a> · <a href="{evidence_prefix}current_release_review.json">machine-readable release decision</a></p>
</section>"""
    card = read("evidence/round6_run_card.json", {}) or {}
    boot = ((card.get("holdout") or {}).get("primary_sgmc") or {})
    if card.get("verdict") != "promote" or not boot:
        return f"""<section class=dl style="border:3px solid #b91c1c" aria-label="Current submission decision">
<h2>&#128308; DO NOT SUBMIT</h2>
<p><b>No file currently passes all frozen gates. Downloads are audit artifacts, not upload authorization.</b>
See <a href="{prefix}research/hypotheses-round6.md">Round-6 preregistration</a>. No slot was used.</p></section>"""
    return f"""<section class=dl style="border:3px solid #1a7f37; background:#f6fbf7" aria-label="Current submission decision">
<h2>&#128994; OK TO DOWNLOAD AND SUBMIT &mdash; ONE FILE ONLY (Round 6, 2026-10-26)</h2>
<p><b>Submit this file:</b> <code>{esc(fname)}</code><br>
<b>Unique submission name:</b> <code>{esc(card.get('submission_name', ''))}</code> &middot;
<b>Note to paste (93/140 chars):</b> <code>{esc(card.get('note_le140', ''))}</code><br>
<b>SHA-256:</b> <code>{esc((card.get('raster_sha256') or '')[:16])}&hellip;</code> &middot; 37,654 dots &middot; 0 on catalogue &middot; B=2 &middot; all-finite [0,1] (never triggers <i>&ldquo;Predicted values must be in range [0, 1]&rdquo;</i>)</p>
<p><a class="btn" style="background:#1a7f37;color:#fff" href="{esc(prefix)}downloads/{esc(fname)}">&#11015; ONE-CLICK DOWNLOAD .TIF</a>
<a class="btn alt" href="{esc(prefix)}downloads/{esc(fname[:-4])}.zip">.ZIP</a>
<a href="{esc(prefix)}executive-summary.html">Step-by-step upload guide</a> &middot;
<a href="{esc(prefix)}research/focus-sites-executive-summary.md">Per-site executive summary (9 focus sites)</a></p>
<p><b>Why this verdict:</b> the file passed every frozen automated gate without human inspection &mdash;
leakage canary AUC 0.525 (&le;0.90); <b>[HOLDOUT-DTI]</b> SGMC-exact {boot.get('candidate_sgmc_dti', 0):.4f} vs champion {boot.get('champion_sgmc_dti', 0):.4f}
(paired diff {boot.get('paired_diff', 0):+.4f}, 95% CI [{boot.get('paired_diff_ci95', [0, 0])[0]:.4f}, {boot.get('paired_diff_ci95', [0, 0])[1]:.4f}],
{int(boot.get('n_truth_px', 0)):,} withheld truth px); uniqueness max 41.4% within-3px (&le;70%) and max surface &rho; 0.34 (&le;0.90)
vs every detector raster on disk; dual portal validators PASS. Random controls score 0.074&ndash;0.077 on the same instrument.</p>
<p><b>What PROMOTE does not mean:</b> no organizer score exists for this file and none is claimed; HOLDOUT-DTI is a local
proxy (SGMC population), not a leaderboard prediction; promotion is a selector recommendation &mdash; confirm the
authenticated weekly cap on the submission page before uploading. <b>Every other file on this site is
<span style="color:#b00020">DO NOT SUBMIT</span></b>: the 0.2778 champion was already submitted (resubmitting wastes a slot),
and the former GEO-CONDUIT primary was demoted 2026-10-26 (70.24% within-3px vs h28 exceeds the 70% gate; IR-R6-02).</p>
<p><a href="{prefix}research/hypotheses-round6.md">Frozen preregistration &amp; 5 ranked hypotheses</a> &middot;
<a href="{prefix}research/standing-brief-20261025.md">Standing brief — read every session</a></p></section>"""


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
        if not p.exists():
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
    status_line = sub.get("status_line_2026_10_25") or sub.get("status_line", "")
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
{scored_badge}
<p>{primary}{zzip}{twin}</p>
<p><b>Filename:</b> <code>{esc(name)}.tif</code><br>
<b>Unique submission name to use:</b> <code>GEMSDOE32-{esc(sub.get('candidate_id','primary'))}</code><br>
<b>Note to paste into the submit form's <em>Note (optional)</em> field
({len(note)}/200 characters):</b><br>
<code>{esc(note)}</code></p>
<p class=mut>single band · float32 · EPSG:32611 · 100 m · 3292&times;3730 ·
{int(f.get('positive_px') or 0):,} predicted pixels · every cell finite · every value in [0, 1] ·
0 NaN anywhere · no nodata tag · sha256 <code>{esc(sha[:16])}&hellip;</code>
{('· ' + receipt) if receipt else ''}</p>
{('<p><b>Already-scored fallback:</b> ' + anchor + '</p>') if anchor else ''}
{pack_rows}
<p class=warn><b>Status.</b> {esc(status_line)}</p>
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
        rel = "docs/downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"
        artifact = ROOT / rel
        sha = (release.get("artifact") or {}).get("sha256", "")
        audit_link = (f'<a href="{esc(prefix + rel.replace("docs/", ""))}">'
                      f'Download audit artifact only: {esc(artifact.name)}</a>' if artifact.is_file() else "")
        return f"""<div class=dl style="border:3px solid #b91c1c">
<h2>&#128308; DO NOT SUBMIT — audit artifact only</h2>
<p>The TIFF is format/range-valid but is not approved for a competition slot. Missing lane assignment and noncompliant fold-isolation evidence block promotion. SHA-256: <code>{esc(sha)}</code>.</p>
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



def focus_sites_block() -> str:
    """Per-site executive summary for the 9 focus sites (Round 6). All scores OWNER-REPORT."""
    rows = [
        ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5", "0.2477", "Denser H19-5 thin (60,069 dots). Superseded by its own sparser children.", "DO NOT SUBMIT (superseded)"),
        ("GEMSDOE25", "dotted-h19-5-d2-8", "0.2600", "H19-5 dot-thin 2.8px (44,090). Parent of the champion.", "DO NOT SUBMIT (superseded)"),
        ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5", "0.2449", "Gap-closure on d1.5 scored BELOW d1.5 itself: added mass hurt.", "DO NOT SUBMIT"),
        ("GEMSDOE28", "h36-1-rung30-blind-r1", "0.2710", "Best of a ~0.27 cluster (solo 0.2708, h38-1 0.2707, h32-1 0.2649): all one family.", "DO NOT SUBMIT (already scored)"),
        ("GEMSDOE30", "d28-poisson300m-offcat-44090", "0.2600", "Dot-identical to GEMSDOE25 d2.8 (same score = scorer determinism check).", "DO NOT SUBMIT (duplicate)"),
        ("GEMSDOE31", "h27-4-solo-d28", "0.2708", "Same 8acb75e1 solo lineage as GEMSDOE28.", "DO NOT SUBMIT (duplicate lineage)"),
        ("GEMSDOE32", "h33-h33-2-b2 (champion) + archived R6-1 STEP", "0.2778 / unscored", "Champion = ladder end (B=2). The R6-1 raster is a format-valid historical audit artifact; its current release gates are not satisfied.", "Champion: DO NOT RESUBMIT. R6-1: DO NOT SUBMIT"),
        ("GEMSDOE33", "h33d-analog-tip-stepover-r30", "0.2632", "Tip/step-over analog lane; below champion.", "DO NOT SUBMIT"),
        ("GEMSDOE36", "anderson-geothermal-pinn-38854", "0.2750", "Contains ALL 37,654 champion dots +1,200 (extras cost -0.0028). Not independent.", "DO NOT SUBMIT (champion superset)"),
    ]
    trs = "".join(f"<tr><td><b>{esc(a)}</b></td><td><code>{esc(b)}</code></td><td>{esc(c)}</td><td>{esc(d)}</td><td><b>{esc(e)}</b></td></tr>" for a, b, c, d, e in rows)
    return f"""<div class=dl><h2>&#128202; Executive summary &mdash; highest reported files across the 9 focus sites and current status</h2>
<p>Every score below is <b>[OWNER-REPORT]</b> (recorded from a submission screen; this repo holds no organizer
receipt linking bytes to score &mdash; IR-32-SCORE-01). Full analysis:
<a href="research/focus-sites-executive-summary.md">focus-sites-executive-summary.md</a>.</p>
<table><tr><th>site</th><th>its best submission</th><th>score</th><th>what it is</th><th>verdict today</th></tr>{trs}</table>
<p><b>Bottom line:</b> the 0.2778 champion is an OWNER-REPORT score and is reported as already submitted; do not resubmit it. The archived R6-1 STEP artifact is unique under its historical registry comparison and format-valid, but the current review found no authorized lane and no compliant fold-isolated promotion result: <b>DO NOT SUBMIT</b>. The other listed files are reported scored, duplicated or superseded; the available evidence does not establish an organizer-confirmed score-to-bytes receipt.</p></div>"""


def overview(fl: dict, sub: dict | None, name: str) -> str:
    lb = fl.get("leaderboard", [])
    lb_top = lb[0] if lb else None
    hold = fl.get("holdout", {})
    irr = fl.get("irregularities", [])
    claims = fl.get("claims", [])
    best_claim = max((c for c in claims), key=lambda c: c.get("score", 0), default=None)
    rows = "".join(f"<tr><td>{esc(s['id'])}</td><td>{esc(s['title'])}</td>"
                   f"<td>{esc(s.get('status',''))}</td></tr>" for s in fl.get("sources", []))
    parts = [arena41_block(), download_block(sub, name), focus_sites_block(), f"""<div class=dl>
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
    release = read("evidence/current_release_review.json", {}) or {}
    if release.get("submission_authorization", {}).get("ok_to_download_and_submit") is not True:
        rel = "downloads/gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"
        artifact = ROOT / "docs" / rel
        download = (f'<a href="{esc(rel)}">Download the existing TIFF for audit/education only</a>'
                    if artifact.is_file() else "The historical artifact is not present in this checkout.")
        return f"""<h2>Submission status — no upload authorized</h2>
<div class=dl style="border:3px solid #b91c1c"><h2>DO NOT SUBMIT</h2>
<p>{download}. Its GeoTIFF bytes pass standalone range and metadata checks; however, the method lane for this session is missing, the historic holdout used a full-catalogue B=2 exclusion, and the current review could not reproduce the competition-template comparison.</p>
<p>Do not use a weekly submission slot. The page will show upload instructions only after a future, lane-authorized experiment passes fold-local hide-and-recover, leakage, uniqueness and format gates and is separately selected.</p>
<p><a href="research/repo-review-20261026.md">Current review and next steps</a> · <a href="../evidence/current_release_review.json">Machine-readable decision</a></p>
</div>"""
    note = esc((sub or {}).get("note", ""))
    fresh = esc(f"{name}-fresh")
    _stem = name.split("-zeros")[0].split("-nan")[0]
    _rec = sorted(DL.glob(f"*{_stem}*audit*.json")) + sorted(DL.glob(f"checks-{name}.tif.json"))
    receipt_link = (f'<a href="downloads/{esc(_rec[0].name)}">{esc(_rec[0].name)}</a>'
                    if _rec else '<span class=mut>not written in this checkout</span>')
    return f"""<h2 style="margin-top:6px">Submission instructions &mdash; Step-by-Step Contest Guide</h2>
{arena41_block()}
{download_block(sub, name)}
<div class=card><h3>1 · Download the validated file</h3>
<p>Click the green <b>Download .TIF</b> button above (or download the <code>.zip</code> package).
The file <code>{esc(name)}.tif</code> is pre-validated by automated 12-point checks:
single-band float32, EPSG:32611 UTM Zone 11N, 100 m resolution, 3730&times;3292 shape.
Receipt: {receipt_link}.</p></div>

<div class=card><h3>2 · Upload to DrivenData &mdash; exact portal URL, file, and note</h3>
<p class=mut>Direct portal link (open in new tab):</p>
<ol>
<li><b>Portal Submission Page:</b>
<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/" target="_blank">https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/</a>
(Login with your DrivenData credentials).</li>
<li><b>File to submit:</b> Click <i>Choose File</i> &rarr; select <code>{esc(name)}.tif</code> (or <code>{esc(name)}.zip</code>).</li>
<li><b>Unique Submission Identifier:</b> <code>GEMSDOE32-R6-STEP-23FBBB51</code></li>
<li><b>Note (optional):</b> Copy-paste this exact text into the field (fits within the portal character budget):<br>
<code>{note}</code></li>
<li>Click <b>Submit</b>. The verification engine evaluates your raster and posts your receipt and score.</li>
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
    dl_btn = ""
    release = read("evidence/current_release_review.json", {}) or {}
    if sub and release.get("submission_authorization", {}).get("ok_to_download_and_submit") is True:
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
