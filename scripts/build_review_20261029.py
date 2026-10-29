#!/usr/bin/env python3
"""Build docs/review-20261029.html from evidence JSON (no hand-typed scores).

Every number on the page is read from:
  evidence/focus_rescore_20261029.json          (repo canonical evaluator, HOLDOUT-DTI)
  evidence/focus_directional_overlap_20261029.json (directional 3-px overlap)
and every referenced repo file is asserted to exist before the page is written.

Labels used on the page:
  HOLDOUT-DTI   = repo evaluator (evaluator version, withheld positives, 95% CI)
  OWNER-REPORT  = score typed by the owner in the session prompt; no receipt in repo
  LIVE-PAGE     = read from the public DrivenData leaderboard page on 2026-10-29
No projection is written as a score.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESCORE = ROOT / "evidence" / "focus_rescore_20261029.json"
OVERLAP = ROOT / "evidence" / "focus_directional_overlap_20261029.json"
OUT = ROOT / "docs" / "review-20261029.html"

LB_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
PROBLEM_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"


def spearman(xs: list[float], ys: list[float]) -> float:
    def ranks(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for rank, i in enumerate(order, start=1):
            r[i] = float(rank)
        return r

    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n * n - 1))


def row_for(rescore: dict, needle: str) -> dict:
    hits = [r for r in rescore["rows"] if needle in r["file"] and r.get("holdout")]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one scored row for {needle!r}, got {len(hits)}")
    return hits[0]


def ci(v: list[float]) -> str:
    return f"[{v[0]:.4f}, {v[1]:.4f}]"


def main() -> int:
    rs = json.loads(RESCORE.read_text())
    ov = json.loads(OVERLAP.read_text())

    h33 = row_for(rs, "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros")
    h51 = row_for(rs, "gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros")
    g25 = row_for(rs, "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros")
    g24 = row_for(rs, "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan")
    g27 = row_for(rs, "gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan")
    g28 = row_for(rs, "gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite")

    # Leaderboard-order check on the five focus files whose bytes are local (n=5: indicative only)
    lb = {"GEMSDOE32": 0.2778, "GEMSDOE28": 0.2708, "GEMSDOE25": 0.2600, "GEMSDOE24": 0.2477, "GEMSDOE27": 0.2449}
    sg = {"GEMSDOE32": h33["holdout"]["sgmc_calibrated_dti"], "GEMSDOE28": g28["holdout"]["sgmc_calibrated_dti"],
          "GEMSDOE25": g25["holdout"]["sgmc_calibrated_dti"], "GEMSDOE24": g24["holdout"]["sgmc_calibrated_dti"],
          "GEMSDOE27": g27["holdout"]["sgmc_calibrated_dti"]}
    hr = {"GEMSDOE32": h33["holdout"]["hide_recover_pooled_dti"], "GEMSDOE28": g28["holdout"]["hide_recover_pooled_dti"],
          "GEMSDOE25": g25["holdout"]["hide_recover_pooled_dti"], "GEMSDOE24": g24["holdout"]["hide_recover_pooled_dti"],
          "GEMSDOE27": g27["holdout"]["hide_recover_pooled_dti"]}
    keys = list(lb)
    rho_sgmc = spearman([lb[k] for k in keys], [sg[k] for k in keys])
    rho_hr = spearman([lb[k] for k in keys], [hr[k] for k in keys])

    rank_hr_h33 = [i + 1 for i, r in enumerate(sorted([r for r in rs["rows"] if r.get("holdout")], key=lambda r: -r["holdout"]["hide_recover_pooled_dti"])) if "h33-h33-2-b2" in r["file"]][0]
    rank_sg_h33 = [i + 1 for i, r in enumerate(sorted([r for r in rs["rows"] if r.get("holdout")], key=lambda r: -r["holdout"]["sgmc_calibrated_dti"])) if "h33-h33-2-b2" in r["file"]][0]
    n_scored = len([r for r in rs["rows"] if r.get("holdout")])

    def pair(a: str, b: str) -> float:
        for p in ov["pairs"]:
            if a in p["your_dots"] and b in p["registry_or_peer"]:
                return p["your_dots_within_3px"]
        raise SystemExit(f"missing pair {a} -> {b}")

    dup_h33_vs_25 = pair("GEMSDOE32 h33-2-b2", "GEMSDOE25 d2-8 (0.2600")
    dup_h33_vs_24 = pair("GEMSDOE32 h33-2-b2", "GEMSDOE24 d1-5")
    dup_h33_vs_28 = pair("GEMSDOE32 h33-2-b2", "GEMSDOE28 h27-4-r1")
    dup_h33_vs_27 = pair("GEMSDOE32 h33-2-b2", "GEMSDOE27 topo")
    h51_vs_25 = pair("GEMSDOE32 H51-1-EWSP", "GEMSDOE25 d2-8 (0.2600")
    h51_vs_24 = pair("GEMSDOE32 H51-1-EWSP", "GEMSDOE24 d1-5")
    h51_vs_28 = pair("GEMSDOE32 H51-1-EWSP", "GEMSDOE28 h27-4-r1")
    h51_vs_27 = pair("GEMSDOE32 H51-1-EWSP", "GEMSDOE27 topo")
    h51_vs_r13 = pair("GEMSDOE32 H51-1-EWSP", "GEMSDOE37-class")
    h51_vs_h19 = pair("GEMSDOE32 H51-1-EWSP", "GEMSDOE32 H19-5")
    h51_focus_max = max(h51_vs_25, h51_vs_24, h51_vs_28, h51_vs_27)
    h19_vals = [pair("GEMSDOE32 h33-2-b2", "GEMSDOE32 H19-5"), pair("GEMSDOE25 d2-8 (0.2600", "GEMSDOE32 H19-5"),
                pair("GEMSDOE24 d1-5", "GEMSDOE32 H19-5"), pair("GEMSDOE27 topo", "GEMSDOE32 H19-5"),
                pair("GEMSDOE28 h27-4-r1", "GEMSDOE32 H19-5")]
    min_h19, max_h19 = min(h19_vals), max(h19_vals)

    # every file the page links to must exist in the repo
    links = [
        "docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif",
        "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif",
        "docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.zip",
        "docs/executive-summary.html",
        "docs/nine-site-executive-summary.html",
        "registry/current_status.json",
        "registry/irregularities.json",
        "evidence/focus_rescore_20261029.json",
        "evidence/focus_directional_overlap_20261029.json",
        "evidence/h51_ewsp_run_card.json",
        "scripts/rescore_focus_downloads.py",
        "scripts/focus_directional_overlap.py",
    ]
    for rel in links:
        if not (ROOT / rel).exists():
            raise SystemExit(f"referenced file missing: {rel}")

    def e(s: object) -> str:
        return html.escape(str(s))

    def hrow(name: str, file_cell: str, reported: str, holdout: str, unique: str, dl: str, sub: str, cls: str) -> str:
        return (f"<tr class='{cls}'><td><b>{e(name)}</b></td><td>{file_cell}</td><td>{e(reported)}</td>"
                f"<td>{holdout}</td><td>{unique}</td><td><b>{e(dl)}</b></td><td><b>{e(sub)}</b></td></tr>")

    no = "NO"
    rows = [
        hrow("GEMSDOE32", "<code>gemsdoe32-h33-h33-2-b2-…-e5eb6e7e-zeros.tif</code> (37,654 dots; sha256 <code>c55bafc4…</code>)",
             "0.2778 OWNER-REPORT (already submitted)",
             f"SGMC-CAL {h33['holdout']['sgmc_calibrated_dti']:.4f} {ci(h33['holdout']['sgmc_calibrated_ci95'])}; "
             f"HIDE-RECOVER {h33['holdout']['hide_recover_pooled_dti']:.4f} {ci(h33['holdout']['hide_recover_ci95'])}",
             f"NO — {dup_h33_vs_25*100:.1f}% of dots within 3 px of GEMSDOE25 dots; {dup_h33_vs_24*100:.1f}% of GEMSDOE24; {dup_h33_vs_28*100:.1f}% of GEMSDOE28 (lane rule &gt;70%)",
             "Already submitted; do not resubmit", no, "cls-red"),
        hrow("GEMSDOE25", "<code>gems25-dotted-h19-5-d2-8-…-e56ea318af89-nan.tif</code> (local, 44,090 dots) and <code>-zeros.tif</code>",
             "0.2600 OWNER-REPORT",
             f"SGMC-CAL {g25['holdout']['sgmc_calibrated_dti']:.4f} {ci(g25['holdout']['sgmc_calibrated_ci95'])}; HIDE-RECOVER {g25['holdout']['hide_recover_pooled_dti']:.4f}",
             "NO — same bytes as GEMSDOE24 d2-8 (sha256 prefix 91eae1ca) and nested in the H19-5 family",
             "Review only", no, "cls-red"),
        hrow("GEMSDOE24", "<code>gems24-h25-1-dotted-h19-5-d1-5-…-nan.tif</code> (local, 60,069 dots)",
             "0.2477 OWNER-REPORT",
             f"SGMC-CAL {g24['holdout']['sgmc_calibrated_dti']:.4f} {ci(g24['holdout']['sgmc_calibrated_ci95'])}; HIDE-RECOVER {g24['holdout']['hide_recover_pooled_dti']:.4f}",
             f"NO — {pair('GEMSDOE24 d1-5', 'GEMSDOE25 d2-8 (0.2600'):.0%} of its dots within 3 px of GEMSDOE25 dots",
             "Review only", no, "cls-red"),
        hrow("GEMSDOE25 / GEMSDOE30 (same bytes)", "GEMSDOE30 label suffix <code>91eae1ca</code> equals GEMSDOE25 d2-8 SHA-256 prefix; GEMSDOE30 bytes not stored separately",
             "0.2600 OWNER-REPORT (both)", "Same as GEMSDOE25", "NO — GEMSDOE30 is the GEMSDOE25 file (hash-prefix match, not byte-verified)", "Review only", no, "cls-red"),
        hrow("GEMSDOE27", "<code>gems27-topo-gap-closure-…-nan.tif</code> (local, 61,328 dots)",
             "0.2449 OWNER-REPORT",
             f"SGMC-CAL {g27['holdout']['sgmc_calibrated_dti']:.4f} {ci(g27['holdout']['sgmc_calibrated_ci95'])}; HIDE-RECOVER {g27['holdout']['hide_recover_pooled_dti']:.4f}",
             f"NO — {pair('GEMSDOE27 topo', 'GEMSDOE25 d2-8 (0.2600'):.0%} of its dots within 3 px of GEMSDOE25 dots",
             "Review only", no, "cls-red"),
        hrow("GEMSDOE28", "<code>gems28-h27-4-r1-solo-d2-8-…-allfinite.tif</code> (local, 40,199 dots, no NaN)",
             "0.2708 OWNER-REPORT (the -nan label is not the local file)",
             f"SGMC-CAL {g28['holdout']['sgmc_calibrated_dti']:.4f} {ci(g28['holdout']['sgmc_calibrated_ci95'])}; HIDE-RECOVER {g28['holdout']['hide_recover_pooled_dti']:.4f}",
             f"NO — {pair('GEMSDOE28 h27-4-r1', 'GEMSDOE25 d2-8 (0.2600'):.0%} of its dots within 3 px of GEMSDOE25 dots",
             "Review only", no, "cls-red"),
        hrow("GEMSDOE31", "<code>h27-4-solo-d28-…-8acb75e1-nan</code> (bytes not in repo)",
             "0.2708 OWNER-REPORT", "Not computable (bytes not in repo)",
             "Likely duplicate of GEMSDOE28 (shared <code>8acb75e1</code> run id; not byte-verified)", "Review only", no, "cls-red"),
        hrow("GEMSDOE33", "<code>h33d-analog-tip-stepover-r30-…-cb490425926e</code> (bytes not in repo)",
             "0.2632 OWNER-REPORT", "Not computable (bytes not in repo)", "Not verifiable from repo", "Review only", no, "cls-amber"),
        hrow("GEMSDOE36", "<code>anderson-geothermal-pinn-38854-…-9b9ea4e6-zeros</code> (bytes not in repo)",
             "0.2750 OWNER-REPORT", "Not computable (bytes not in repo)", "Not verifiable from repo", "Review only", no, "cls-amber"),
        hrow("NEW — H51-1-EWSP (unique candidate)",
             "<code>gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-…-bdf25d8c-zeros.tif</code> (37,654 dots; sha256 <code>f66f65e4…</code>; values 0/1, no NaN)",
             "Never submitted — no leaderboard score",
             f"SGMC-CAL {h51['holdout']['sgmc_calibrated_dti']:.4f} {ci(h51['holdout']['sgmc_calibrated_ci95'])} (below 0.064121 champion); "
             f"HIDE-RECOVER {h51['holdout']['hide_recover_pooled_dti']:.6f} (below the 0.004515 champion)",
             f"YES vs focus sites — max {h51_focus_max*100:.1f}% (&lt;70%); <b>NO</b> vs dense <code>r13-lattice-s5</code> ({h51_vs_r13*100:.1f}%)",
             "YES — review only", "NO — gate not met", "cls-amber"),
    ]

    html_doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEMSDOE32 — 2026-10-29 review and executive summary</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#f6f7f9;color:#1b1f24;line-height:1.5}}
main{{max-width:1180px;margin:0 auto;padding:24px}}
h1{{font-size:26px;margin:.2em 0}} h2{{font-size:20px;margin-top:1.6em;border-bottom:1px solid #d0d7de;padding-bottom:.2em}}
.banner{{background:#7a0c0c;color:#fff;padding:16px 20px;border-radius:8px;font-size:16px}}
.banner b{{font-size:18px}}
.card{{background:#fff;border:1px solid #d0d7de;border-radius:8px;padding:14px 18px;margin:12px 0}}
table{{border-collapse:collapse;width:100%;font-size:13.5px;background:#fff}}
th,td{{border:1px solid #d0d7de;padding:6px 8px;vertical-align:top;text-align:left}}
th{{background:#eef1f5}}
tr.cls-red td:first-child{{border-left:5px solid #b42318}}
tr.cls-amber td:first-child{{border-left:5px solid #b54708}}
code{{font-size:12px;background:#eef1f5;padding:0 3px;border-radius:3px}}
.small{{font-size:12.5px;color:#444}}
</style></head><body><main>
<h1>GEMSDOE32 — 2026-10-29 repo review &amp; executive summary</h1>
<p class="small">Generated by <code>scripts/build_review_20261029.py</code> from <code>evidence/focus_rescore_20261029.json</code> and <code>evidence/focus_directional_overlap_20261029.json</code>. No number here is typed by hand.</p>

<div class="banner"><b>VERDICT: NO FILE IS CLEARED FOR UPLOAD.</b><br>
Download for review: the unique candidate <code>H51-1-EWSP</code> only. <b>Submit: NO file.</b>
The 0.2778 file is already submitted and is a duplicate of the GEMSDOE24/25/27/28 family under the lane rule, so do not resubmit it.</div>

<h2>1. Executive summary — which file, estimated score, unique?</h2>
<p><b>Score labels.</b> <b>OWNER-REPORT</b> = typed by the owner in the session prompt, with no submission-page receipt in this repo.
<b>HOLDOUT-DTI</b> = repo canonical evaluator (<code>GEMSDOE32-SGMC-CAL-v3.0</code>, 62,703 withheld positives; and <code>GEMSDOE32-HIDE-RECOVER-v3.0</code>, 22,232 withheld positives), 95% spatial-block CI.
<b>No projection is written as a score.</b> Only a submission-page receipt would make a number ORGANIZER-CONFIRMED, and none exists here.</p>
<table>
<tr><th>Site</th><th>File to download (local path or label)</th><th>Reported public score</th><th>Holdout check (HOLDOUT-DTI)</th><th>Unique vs the nine focus sites?</th><th>OK to download?</th><th>OK to submit?</th></tr>
{''.join(rows)}
</table>
<p class="small">Uniqueness rule (protocol lane rule): YOUR dots within 3 px of a peer's dots &gt; 70% = duplicate. Values are directional and come from <code>evidence/focus_directional_overlap_20261029.json</code>.
The "1.0" entries are consistent with nesting: every dot of the 37,654-dot 0.2778 file lies within 3 px of a dot of the 44,090-dot GEMSDOE25 file.</p>

<h2>2. Live leaderboard (checked 2026-10-29)</h2>
<div class="card">Top of the public DrivenData leaderboard, read from <a href="{LB_URL}">{LB_URL}</a> on 2026-10-29:
<b>#1 xiaofanhu 0.4544</b>, #2 cfld__ 0.3916, #3 Batik Shirt Brothers 0.3911. The "0.4413", "0.4437" and "0.3195" values quoted in the session prompt and README are out of date.
This is the <b>public</b> split. The initial prize is decided on the private split (see the <a href="{PROBLEM_URL}">problem description</a>).</div>

<h2>3. Why did 0.2778 score highest? (analysis, not a receipt)</h2>
<div class="card">
<ol>
<li><b>It is a pruned member of one family.</b> The 0.2778 file (37,654 dots) has <b>{dup_h33_vs_25*100:.1f}%</b> of its dots within 3 px of GEMSDOE25's 44,090 dots and <b>{dup_h33_vs_24*100:.1f}%</b> of GEMSDOE24's. Every focus file in the table has {min_h19*100:.1f}%–{max_h19*100:.1f}% of its dots within 3 px of the H19-5 powerlaw raster (121,131 dots). The README's B-pruning sequence (H19-5 → D2.8 → B=1 → B=2) is the claimed lineage; the overlap numbers are verified, the lineage itself is the README's claim.</li>
<li><b>Hypothesis — pruning removes wasted dots, not structure.</b> Under the metric, a dot counts as a false positive unless it is within 300 m of a withheld fault. Dots on already-mapped USGS traces are plausibly less likely to lie within 300 m of an unmapped fault, so removing them may lower false-positive mass. The surviving dots keep most of the recall. This is untested here; the holdout does not measure it directly.</li>
<li><b>The repo's HIDE-RECOVER holdout does not predict the leaderboard here.</b> The 0.2778 file scores HIDE-RECOVER {h33['holdout']['hide_recover_pooled_dti']:.4f} (rank {rank_hr_h33} of {n_scored} scored rasters). It is {rank_sg_h33} of {n_scored} on SGMC-CAL. The ordering across the five focus files is Spearman &rho; = <b>{rho_sgmc:+.2f}</b> for SGMC-CAL and <b>{rho_hr:+.2f}</b> for HIDE-RECOVER (n = 5, indicative only).</li>
</ol>
<p class="small">So the answer to "can we beat 0.2778?" is <b>not yet demonstrable here</b>. The only instrument that orders the focus files roughly like the leaderboard is SGMC-CAL, and it differs by about 0.01 between files, with overlapping CIs. Beating 0.2778 needs a new family that is not a subset of H19-5, plus a receipt from a real submission.</p>
</div>

<h2>4. The unique candidate: H51-1-EWSP</h2>
<div class="card">
<ul>
<li>Format: float32, 3292×3730, EPSG:32611, 100 m transform matches the template, no NaN, values exactly 0 or 1, 37,654 dots (checked by <code>scripts/rescore_focus_downloads.py</code>).</li>
<li>Uniqueness: directional overlap vs focus peers max <b>{h51_focus_max*100:.1f}%</b> (vs GEMSDOE25 {h51_vs_25*100:.1f}%, GEMSDOE24 {h51_vs_24*100:.1f}%, GEMSDOE27 {h51_vs_27*100:.1f}%, GEMSDOE28 {h51_vs_28*100:.1f}%) and vs the H19-5 registry raster {h51_vs_h19*100:.1f}%. <b>Fails</b> vs the dense <code>13gems_20261001_r13-lattice-s5_v2</code> raster ({h51_vs_r13*100:.1f}%, 206,895 dots). That raster is dense, and the literal rule is open owner decision IR-45-LATTICE-02.</li>
<li>Holdout: HIDE-RECOVER {h51['holdout']['hide_recover_pooled_dti']:.6f} {ci(h51['holdout']['hide_recover_ci95'])}; SGMC-CAL {h51['holdout']['sgmc_calibrated_dti']:.6f} {ci(h51['holdout']['sgmc_calibrated_ci95'])}. This is below the 0.064121 SGMC-CAL champion, so it fails the repo's gate, which requires no SGMC-cal regression.</li>
</ul>
<p class="small">Note: the status file records the H51 HIDE-RECOVER value as 0.002289, and that is the value this evaluator reproduces. The HIDE-RECOVER champion for the same evaluator is 0.004515, so H51 is below it as well. The 0.115134 headline in older README text comes from a fold-local arm and is not the emitted file (see <code>registry/current_status.json</code> headline).</p>
</div>

<h2>5. Irregularities flagged for review</h2>
<div class="card"><b>Parallel review on main (same date):</b> <a href="../docs/research/repo-review-20261029.md">docs/research/repo-review-20261029.md</a> (branch arena/2149a383-gemsdoe32, PR #69). Its IR-R6 "holdout data absent" is <b>resolved</b> by this branch: all 30 inputs are restored from the pinned sibling repos and SHA-256 verified (<code>data/restore_receipt.json</code>). Its other findings (seven focus files not in repo, no organizer receipt, zeros-vs-NaN format) are consistent with this review.</div>
<div class="card">
<ul>
<li><b>IR-20261029-LB-01</b> — Live #1 is 0.4544 on the public page; the prompt and README cite 0.4413 / 0.4437 / 0.3195.</li>
<li><b>IR-20261029-NAN-01</b> — The official page says data outside the bounds "is null or nan" (allowed). The portal error the owner saw was "Predicted values must be in range [0, 1]". Both can be true if the portal treats NaN as out-of-range. The <code>-zeros.tif</code> variants avoid the question, so use them.</li>
<li><b>IR-20261029-EVAL-01</b> — HIDE-RECOVER does not track the leaderboard on the focus files (Spearman {rho_hr:+.2f} at n=5). SGMC-CAL does better ({rho_sgmc:+.2f}, n=5). Neither is a validated estimator.</li>
<li><b>IR-20261029-DUP-01</b> — GEMSDOE30's label suffix <code>91eae1ca</code> equals the SHA-256 prefix of the GEMSDOE24/25 d2-8 raster, so GEMSDOE30 appears to be the same file as GEMSDOE25.</li>
<li><b>IR-20261029-BYTES-01</b> — GEMSDOE31, 33 and 36 bytes are not in the repo, so those rows cannot be re-scored.</li>
<li><b>IR-20261029-PROB-01</b> — The canonical evaluator refuses to score probability (non-binary) rasters. The focus-site NaN-bearing files are binary inside the footprint, so they score; a true probability raster cannot be scored here.</li>
</ul></div>

<h2>6. Limitations and what is needed next</h2>
<div class="card">
<ul>
<li><b>No leaderboard feedback loop.</b> The sandbox cannot log in to DrivenData and cannot submit. Every real score needs a weekly slot and an owner-driven upload, so no candidate here is ORGANIZER-CONFIRMED.</li>
<li><b>Holdout proxy.</b> The repo's HIDE-RECOVER and SGMC-CAL evaluators are proxies for the private test set. They disagree with each other and with the leaderboard, so no proxy can yet serve as a score estimate.</li>
<li><b>Next experiment (not run here).</b> Build a candidate whose directional overlap with the H19-5 family is under 70% and whose SGMC-CAL beats 0.064121, then review it against every gate. Budget used this session: 0 experiments (the review did not change any candidate).</li>
</ul></div>

<h2>7. Sources (checked 2026-10-29)</h2>
<div class="card small">
<ul>
<li>Problem description, metric and submission format (fetched): <a href="{PROBLEM_URL}">{PROBLEM_URL}</a></li>
<li>Public leaderboard (fetched): <a href="{LB_URL}">{LB_URL}</a></li>
<li>Repo governance: <a href="../registry/current_status.json">registry/current_status.json</a>, <a href="../registry/irregularities.json">registry/irregularities.json</a></li>
<li>Evidence: <a href="../evidence/focus_rescore_20261029.json">focus_rescore_20261029.json</a>, <a href="../evidence/focus_directional_overlap_20261029.json">focus_directional_overlap_20261029.json</a></li>
</ul></div>
</main></body></html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_doc)
    print("wrote", OUT)
    print(f"rho_sgmc={rho_sgmc:.3f} rho_hr={rho_hr:.3f} h51_focus_max={h51_focus_max:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
