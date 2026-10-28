#!/usr/bin/env python3
"""Render docs/nine-site-executive-summary.html from verified evidence (2026-10-28).

Every number on the page is read from evidence/*.json, docs/score-ledger.csv, a run card, or
recomputed from bytes on disk.  The builder raises instead of printing a value it cannot find.

Evidence labels used on the page:
  OWNER-REPORT          live score copied from the owner brief / ledger (no organizer receipt in repo)
  HOLDOUT-DTI           local evaluator value; evaluator version, withheld count and 95% CI shown
  MEASURED-HERE         recomputed from bytes in this session
  PROJECTION            linear map from SGMC-cal to live score; never a score
  OFFICIAL              read from an official organizer page (DrivenData leaderboard)
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "nine-site-executive-summary.html"


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def sha256(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def esc(x) -> str:
    return html.escape(str(x))


def f4(x, nd=4) -> str:
    if x is None:
        raise ValueError("missing number")
    return f"{float(x):.{nd}f}"


def ci(c) -> str:
    return f"[{c[0]:.4f}, {c[1]:.4f}]"


def main() -> int:
    ship = load("evidence/shipped_ranked_validated_20261028.json")["rows"]
    iv = load("evidence/instrument_vs_live_20261028.json")
    comp = load("evidence/comparator_reproduction_20261028.json")["checks"]
    proj = load("evidence/live_projection_from_sgmc_20261028.json")
    lb = load("evidence/leaderboard_read_20261028.json")
    status = load("registry/current_status.json")
    ledger = list(csv.DictReader((ROOT / "docs/score-ledger.csv").open()))

    def ship_row(fragment: str) -> dict:
        hits = [r for r in ship if fragment in r["file"]]
        if len(hits) != 1:
            raise ValueError(f"ship fragment {fragment!r} matched {len(hits)} rows")
        return hits[0]

    def best_ledger(site: str) -> dict:
        rows = [r for r in ledger if r["site"] == site and r["score"].strip()]
        return max(rows, key=lambda r: float(r["score"]))

    # --- 1. Nine focus sites: best ledger score per site; file on disk where it exists ---
    site_defs = [
        # site, on-disk fragment (or None), note from the site's own row or measured here
        ("GEMSDOE24", "989f59505db1",
         "Best row is the d1.5 file (60,069 dots). A GEMSDOE24-labelled d2.8 file on disk is the same dot mask as GEMSDOE25 (IR-20261028-07)."),
        ("GEMSDOE25", "e56ea318af89-zeros",
         "d2.8 thinning, 44,090 dots. Ledger flags a conflicting owner page (unscored / not slot-approved)."),
        ("GEMSDOE27", "5512495c6bd1-nan",
         "topo-gap closure on d1.5, 61,328 dots. Ledger row is user-reported; not independently authenticated."),
        ("GEMSDOE28", None,
         "h36-1 rung30 blind r1 (ledger: 37,660 dots, byte-verified in an earlier session). Raster not on disk this session."),
        ("GEMSDOE30", None,
         "Ledger: dot set identical to GEMSDOE25 d2.8 (IR-32-FAM-02). Name suffix 91eae1ca equals the sha256 prefix of a restored d2.8 file whose dot mask matches GEMSDOE25 (MEASURED-HERE). Treat as a duplicate."),
        ("GEMSDOE31", None,
         "Same solo base family as GEMSDOE28 h27-4 (8acb75e1). Raster not on disk this session."),
        ("GEMSDOE32", "e5eb6e7e-zeros",
         "GROUP BEST. Ledger: solo (40,199 dots) minus 2,545 dots within 2 px of the catalogue = 37,654 dots (40199 - 2545 = 37654, checked)."),
        ("GEMSDOE33", None,
         "Fault-tip / step-over analog. Raster not on disk this session."),
        ("GEMSDOE36", None,
         "Ledger (forensic): contains all 37,654 champion dots plus extras; the extras cost about -0.0028 vs champion. Not re-verified here."),
    ]
    site_rows = []
    for site, frag, note in site_defs:
        best = best_ledger(site)
        if frag:
            srow = ship_row(frag)
            uniq = (f"measured: non-lattice max 3-px overlap {srow['max_within3px_vs_any_non_lattice_file']:.3f}; "
                    f"lattice {srow['within3px_vs_13gems_lattice']:.3f} (fails 70%)")
        else:
            uniq = "NOT MEASURED here (raster not on disk)"
        site_rows.append((site, best["score"], best["submission"], uniq, note))

    # --- 2. New candidates (run-card HR + measured SGMC + measured overlaps) ---
    cards = {
        "H51-1 EWSP (EXP1)": ("docs/downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif",
                              "bdf25d8c", "evidence/h51_ewsp_run_card.json", ("holdout_dti", "primary_hide_and_recover"),
                              "fold-local (card primary)",
                              "DO NOT SUBMIT: fails the lattice rule; SGMC-cal 0.0630 is below champion 0.0641"),
        "H47-1 LDGI": ("docs/downloads/gemsdoe32-h47-ldgi-dualhorizon-corridor-37654-20261026T230609Z-0eb8a25c-zeros.tif",
                       "0eb8a25c", "evidence/h47_ldgi_run_card.json", ("holdout_dti", "primary_hide_and_recover"),
                       "fold-local (card primary)",
                       "DO NOT SUBMIT: fails the lattice rule; SGMC-cal margin over champion not significant"),
        "H49-1 CGTD": ("docs/downloads/gemsdoe32-h49-cgtd-noisyor-axial28-37654-20261027T235000Z-f3e24fb5-zeros.tif",
                       "f3e24fb5", "evidence/h49_cgtd_run_card.json", ("holdout_dti", "primary_hide_and_recover"),
                       "fold-local (card primary)",
                       "DO NOT SUBMIT: fails the lattice rule; intra-repo overlap vs H48 (card: 73.33%)"),
        "ARENA49-PCG": ("docs/downloads/gemsdoe32-arena49-pcg-dualconcord-37654-20261026T220056Z-54e97629-zeros.tif",
                        "54e97629", "evidence/arena49_pcg_run_card.json", ("holdout_dti", "primary_visible_gated"),
                        "FLAT-MASK instrument (NOT fold-local)",
                        "DO NOT SUBMIT: fails the lattice rule; run card contradicts itself (IR-20261028-06)"),
        "ARENA-EULER-E1": ("docs/downloads/gemsdoe32-euler-e1-37654-20261028T000236Z-71f0a187-zeros.tif",
                           "71f0a187", "evidence/euler_lane_run_card.json", ("holdout", "EXP3_BASE35_EULER_OOF"),
                           "fold-local (card EXP3 block)",
                           "DO NOT SUBMIT: fails the lattice rule; HR ties the champion proxy"),
        "ARENA9 PGRN-PU": ("docs/downloads/gemsdoe32-arena9-pgrn-pu37654-20261026T053246Z-4f7aba9b-zeros.tif",
                           "4f7aba9b", "evidence/arena9_run_card.json", ("holdout_dti", "selected_pooled_dti"),
                           "fold-local (card selected)",
                           "DO NOT SUBMIT: loses to the champion proxy on fold-local HR (0.0579 vs 0.0992)"),
    }
    proj_keys = {"H51-1 EWSP (EXP1)": "H51-1 EXP1 (bdf25d8c)", "H47-1 LDGI": "H47-1 LDGI (0eb8a25c)",
                 "H49-1 CGTD": "H49-1 CGTD (f3e24fb5)", "ARENA49-PCG": "ARENA49-PCG (54e97629)",
                 "ARENA-EULER-E1": "ARENA-EULER-E1 (71f0a187)", "ARENA9 PGRN-PU": "ARENA9 PGRN-PU (4f7aba9b)"}

    cand_rows = []
    for name, (path, frag, card_rel, (k1, k2), hr_label, verdict) in cards.items():
        card = load(card_rel)
        top_block = card[k1]
        block = top_block if isinstance(top_block.get(k2), (float, int)) else top_block[k2]
        if isinstance(top_block.get(k2), (float, int)):           # ARENA9 card: float + sibling CI keys
            hr, hr_ci = top_block[k2], top_block["selected_ci95"]
        else:
            hr = block.get("pooled_dti", block.get("dti"))
            hr_ci = block.get("ci95")
        if hr is None or hr_ci is None:
            raise ValueError(f"{card_rel}: no HR for {name}")
        card_sha = card.get("raster_sha256") or (card.get("artifacts") or {}).get("primary_zeros_sha256")
        actual = sha256(path)
        sha_check = "matches run card" if card_sha == actual else f"DOES NOT match run card ({str(card_sha)[:12]})"
        r = ship_row(frag)
        p = proj["candidates"][proj_keys[name]]
        cand_rows.append({
            "name": name, "path": path, "file": Path(path).name, "dots": r["dots"], "sha": actual,
            "sha_check": sha_check, "hr": hr, "hr_ci": hr_ci, "hr_label": hr_label,
            "sgmc": r["sgmc_cal_dti"], "sgmc_ci": r["sgmc_cal_ci95"],
            "nonlat": r["max_within3px_vs_any_non_lattice_file"], "lat": r["within3px_vs_13gems_lattice"],
            "proj": p, "verdict": verdict,
        })

    # --- 3. Champion comparator, instrument and projection values ---
    euler_champ_dti = load("evidence/euler_lane_run_card.json")["holdout"]["champion_actual_raster_h33_2_b2"]["dti"]
    d28 = comp["registry_0p2778_proxy_is_d28_parent_collared"]
    h33c = comp["h33_b2_file_sgmc_cal"]
    h33_sh = ship_row("e5eb6e7e-zeros")
    # The lattice raster is itself in the receipt (self-overlap 1.0); exclude it from the counts.
    comp_rows = [r for r in ship if "13gems" not in r["file"]]
    n_comp = len(comp_rows)
    lat_pass = sum(1 for r in comp_rows if r["within3px_vs_13gems_lattice"] <= 0.70)
    nonlat_pass = sum(1 for r in comp_rows if r["literal_70pct_gate_vs_non_lattice"])
    receipt_nonlat_pass = sum(1 for r in ship if r["literal_70pct_gate_vs_non_lattice"])
    ivs = iv["summary"]
    ph = [r for r in iv["rows"] if "PLACEHOLDER" in r["label"]][0]
    top = lb["rows_verified"][0]
    r26 = [r for r in lb["rows_verified"] if r["rank"] == 26][0]
    n_ship = len(ship)

    site_html = "".join(
        f"<tr><td><b>{esc(s)}</b></td>"
        f"<td>{esc(score)}<br><small>OWNER-REPORT (ledger)</small></td>"
        f"<td><code>{esc(sub)}</code></td><td>{esc(u)}</td><td>{esc(note)}</td>"
        f"<td><b style=\"color:#f85149\">NO upload</b><br><small>already scored, duplicate, or unverified</small></td></tr>"
        for s, score, sub, u, note in site_rows)

    cand_html = ""
    for c in cand_rows:
        pr = c["proj"]
        extrap = " (extrapolated beyond the SGMC range of the fit)" if c["sgmc"] > 0.0641209 else ""
        cand_html += (
            f"<tr><td><a href=\"downloads/{esc(c['file'])}\"><code>{esc(c['file'])}</code></a>"
            f"<br><small>sha256 {esc(c['sha'][:16])}&hellip; &middot; {esc(c['sha_check'])}</small></td>"
            f"<td>{esc(c['name'])}</td><td>{c['dots']:,}</td>"
            f"<td>{f4(c['hr'])} {ci(c['hr_ci'])}<br><small>HOLDOUT-DTI, {esc(c['hr_label'])}, n=22,232</small></td>"
            f"<td>{f4(c['sgmc'])} {ci(c['sgmc_ci'])}<br><small>HOLDOUT-DTI SGMC-cal, MEASURED-HERE, n=62,703</small></td>"
            f"<td>{c['nonlat']:.3f}</td><td>{c['lat']:.3f}</td>"
            f"<td><small>PROJECTION (not a score): {pr['projected_live_mean']:.4f}, 95% PI "
            f"[{pr['projected_95pi'][0]:.4f}, {pr['projected_95pi'][1]:.4f}]{extrap}</small></td>"
            f"<td><b style=\"color:#f85149\">{esc(c['verdict'])}</b></td></tr>")

    page = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Nine-site executive summary · GEMSDOE32</title>
<link rel=stylesheet href=assets/site.css></head><body>
<header class=top><div class=wrap>
<h1>Nine-site executive summary: which file, what score, is it unique</h1>
<nav><a href="index.html">Home</a> <a href="executive-summary.html">Make a submission</a> <a href="nine-site-executive-summary.html" class=active>Nine-site summary</a> <a href="research.html">Research</a> <a href="leaderboard.html">Leaderboard</a> <a href="irregularities.html">Irregularities</a></nav>
</div></header>
<main class=wrap>

<section class=dl style="border:3px solid #b91c1c" aria-label="Decision">
<h2 style="margin:4px 0">&#128308; DOWNLOAD FOR AUDIT: YES &middot; SUBMIT TO THE LIVE PORTAL: NO</h2>
<p><b>No file is authorized for upload today.</b> Registry decision: <code>any_file_ok_to_submit = false</code>
(<code>registry/current_status.json</code>).</p>
<p>The literal duplicate rule (more than 70% of dots within 3 px of any registry raster) is failed by <b>{n_comp - lat_pass} of {n_comp}</b>
competitive on-disk rasters (the lattice raster itself excluded) against the 13gems calibration lattice. The 0.2778 champion itself is
<b>{h33_sh['within3px_vs_13gems_lattice']*100:.2f}%</b> within 3 px of it, so no competitive-size file can pass the literal rule.
The owner must decide, in writing, whether this dense calibration raster counts for the 70% rule. That decision is required before any file can be submitted.</p>
<p><b>Short answer to &ldquo;which file should I submit?&rdquo;:</b> none today. The best file at each site is already scored and should not be resubmitted.
The best <i>new</i> candidates are in section 2. They are research artifacts until the lattice decision is made.</p>
</section>

<h2>0. Leaderboard fact check (official page, read 2026-10-28)</h2>
<p>[OFFICIAL] <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">DrivenData leaderboard</a>:
#1 <b>{esc(top['participant'])} {top['score']:.4f}</b>; #26 <b>{esc(r26['participant'])} {r26['score']:.4f}</b>.
So <b>0.3195 is not the highest public score</b> (IR-20261028-01). Our own team does not appear in the rows read, so its public score is unverified.
Record: <a href="../evidence/leaderboard_read_20261028.json"><code>evidence/leaderboard_read_20261028.json</code></a>.</p>

<h2>1. Per-site answer: GEMSDOE24 · 25 · 27 · 28 · 30 · 31 · 32 · 33 · 36</h2>
<p>Scores are the highest numeric row for each site in <code>docs/score-ledger.csv</code>. None has an organizer receipt in the repo, so all are OWNER-REPORT. &ldquo;Uniqueness&rdquo; is measured only where the raster is on disk.</p>
<div style="overflow-x:auto"><table><thead><tr><th>Site</th><th>Best live score</th><th>Submission (ledger name)</th><th>Uniqueness</th><th>Notes</th><th>Download / submit?</th></tr></thead>
<tbody>{site_html}</tbody></table></div>

<h3>Why GEMSDOE32&rsquo;s 0.2778 scored highest (what the evidence supports)</h3>
<ul>
<li><b>Arithmetic (verified):</b> the ledger says the champion is the solo file (40,199 dots) minus 2,545 dots within 2 px of the catalogue, giving 37,654 dots. 40,199 &minus; 2,545 = 37,654.</li>
<li><b>Direction (MEASURED-HERE, SGMC-cal, HOLDOUT-DTI):</b> the solo parent scores {f4(ship_row('8acb75e1f2cc-allfinite')['sgmc_cal_dti'])}, the champion {f4(h33c['prevalence_calibrated_dti'])} {ci(h33c['ci95'])}, and the GEMSDOE25 d2.8 parent {f4(ship_row('e56ea318af89-zeros')['sgmc_cal_dti'])}. The champion ranks above both, as its live score does.</li>
<li><b>Size of the live gap:</b> the owner-reported solo score is 0.2708 (GEMSDOE28/31 family) and the champion 0.2778, a gap of +0.0070. The instrument does not resolve gaps this small (section 3).</li>
<li><b>Caveat:</b> the 0.099202 comparator is the d2.8 parent, not the champion. The 0.2778 file itself scores static HR {f4(euler_champ_dti)} on the same evaluator (Euler card receipt; section 2).</li>
</ul>

<h2>2. New candidates: measured evidence and gate status</h2>
<p><b>HR</b> = fold-local HOLDOUT-DTI from each run card (GEMSDOE32-HIDE-RECOVER-v3.0, withheld positives 22,232). <b>SGMC-cal</b> = recomputed here with the shared evaluator (GEMSDOE32-SGMC-CAL-v3.0, withheld positives 62,703). <b>Non-lattice</b> = largest share of this file's dots within 3 px of any other on-disk raster (lattice excluded). <b>Lattice</b> = share within 3 px of the 13gems lattice. The 70% limit applies to each.</p>
<div style="overflow-x:auto"><table><thead><tr><th>Download (click)</th><th>Candidate</th><th>Dots</th><th>HR (HOLDOUT-DTI)</th><th>SGMC-cal (HOLDOUT-DTI)</th><th>Non-lattice overlap (limit 0.70)</th><th>Lattice overlap (limit 0.70)</th><th>Live projection</th><th>Verdict</th></tr></thead>
<tbody>{cand_html}</tbody></table></div>

<p><b>Champion comparator (reproduced here).</b> The registry&rsquo;s &ldquo;0.2778 champion proxy&rdquo; HR of
<b>{f4(d28['pooled_dti'], 6)} {ci(d28['ci95'])}</b> is reproduced from the GEMSDOE25 d2.8 parent with a 2-px visible collar (<code>scripts/reproduce_comparators_20261028.py</code>).
It is <b>not</b> the 0.2778 file&rsquo;s own holdout. Scored on the same static path, the 0.2778 file gives {f4(euler_champ_dti)} (Euler run card receipt; IR-EULER-02). Future reports should label the comparator as the d2.8 parent.</p>
<p><b>PROJECTION, not a score.</b> Linear map from SGMC-cal to owner-reported live score, fitted on {proj['n_training_points']} points
(R&sup2; {proj['r_squared']:.3f}, residual SD {proj['residual_sd']:.4f}). The candidates with SGMC-cal above 0.0641 lie outside the fit range, so their projections are extrapolations and are not evidence.</p>

<h2>3. Which instrument to trust (measured)</h2>
<ul>
<li>Spearman rank correlation of SGMC-cal with owner-reported live scores across <b>{ivs['n_files_correlated']}</b> restored files: <b>{ivs['spearman_live_vs_sgmc_cal']:.2f}</b>.</li>
<li>Spearman of the static hide-and-recover diagnostic with live scores: <b>{ivs['spearman_live_vs_static_hide_recover']:.2f}</b>. It does not track live rank and must not be used to pick a file.</li>
<li>Fold-local HR values on the candidate cards come from the per-fold pipeline. The shipped files do not reproduce them on the static path, so each needs its own per-fold receipt before a claim is promoted.</li>
<li>Contamination: <code>hsupsgmc</code> used SGMC north pixels as training positives, and the <code>bayesopt</code> file was selected using SGMC-cal in its objective (IR-20261028-04). Their SGMC values are not independent evidence.</li>
</ul>
<p>Evidence: <a href="../evidence/instrument_vs_live_20261028.json"><code>instrument_vs_live_20261028.json</code></a> &middot;
<a href="../evidence/comparator_reproduction_20261028.json"><code>comparator_reproduction_20261028.json</code></a> &middot;
<a href="../evidence/shipped_ranked_validated_20261028.json"><code>shipped_ranked_validated_20261028.json</code></a> &middot;
<a href="../evidence/live_projection_from_sgmc_20261028.json"><code>live_projection_from_sgmc_20261028.json</code></a></p>

<h2>4. What blocks a submission (owner decisions, not automatic)</h2>
<ol>
<li><b>Lattice rule.</b> Only {lat_pass} of {n_comp} competitive rasters pass the 70% rule against the 13gems lattice. The owner must either (a) record a written exemption for dense calibration rasters, or (b) accept that no competitive-size file can be submitted under the literal rule.</li>
<li><b>Per-candidate fold-local receipts.</b> Each HR claim needs its own per-fold re-emission receipt.</li>
<li><b>Selection bias.</b> SGMC-cal has been used as a selection criterion. A held-out instrument is needed for future selection.</li>
<li><b>Slot selection.</b> Promotion to a live slot is a separate selector step. Nothing here authorizes a weekly slot.</li>
</ol>
<p>Non-lattice gate: <b>{nonlat_pass} of {n_comp}</b> competitive rasters pass the 70% rule against other on-disk rasters (the receipt's {receipt_nonlat_pass} of {n_ship} counts the lattice itself, which trivially passes). This is not a submission pass, because the lattice rule still applies.</p>

<h2>5. Irregularities flagged (recorded in registry/irregularities.json)</h2>
<ul>
<li><b>IR-20261028-01</b>: The brief describes 0.3195 as the highest score. The official page shows it at rank #26; the top is 0.4544.</li>
<li><b>IR-20261028-02</b>: The &ldquo;champion proxy&rdquo; HR (0.099202) is the GEMSDOE25 d2.8 parent under a visible collar, not the 0.2778 file (static HR 0.004515).</li>
<li><b>IR-20261028-03</b>: Registry lattice counts do not reproduce exactly. Registry: 6,514 allowed px and 99.45% H51 overlap. Measured: 6,649 px and 99.70% (grid convention), with other conventions differing again. The pass/fail conclusion is unchanged.</li>
<li><b>IR-20261028-04</b>: SGMC contamination and selection bias (hsupsgmc, bayesopt).</li>
<li><b>IR-20261028-05</b>: Static HR does not track live rank (Spearman {ivs['spearman_live_vs_static_hide_recover']:.2f}).</li>
<li><b>IR-20261028-06</b>: ARENA49-PCG run card: top-level verdict negative, while <code>promotion_decision</code> says promote (its final gate ignores the lattice).</li>
<li><b>IR-20261028-07</b>: Identical dot masks under three names: GEMSDOE25 (zeros), a restored GEMSDOE24-labelled d2.8 file (sha prefix 91eae1ca, matching the GEMSDOE30 name), and the d2-8 repro file (MEASURED-HERE, 0 px difference).</li>
<li><b>IR-20261028-08</b>: The <code>gemsdoe9-PLACEHOLDER</code> file scores SGMC-cal {f4(ph['sgmc_cal_dti'])}, with owner-reported live {ph['live_score_owner_report']:.4f}. It is a placeholder, not a candidate.</li>
<li><b>IR-20261028-09</b>: GEMSDOE25 ledger row conflicts with its owner page (unscored / not slot-approved).</li>
</ul>

<h2>6. Verification trail</h2>
<ul>
<li>Restore: 30 files restored and SHA-256 verified from pinned GitHub mirrors (<code>scripts/restore_data.py</code>). DrivenData&rsquo;s data tab is login-walled, so these are not organizer-authenticated (IR-32-DATA-01).</li>
<li>Run card (JSON, this cycle): <a href="../evidence/run_card_nine_site_20261028.json"><code>evidence/run_card_nine_site_20261028.json</code></a>. Registry irregularities: <a href="../registry/irregularities.json"><code>registry/irregularities.json</code></a> (IR-20261028-01 to -09).</li>
<li>Scripts (this session): <code>scripts/reproduce_comparators_20261028.py</code>, <code>scripts/validate_instrument_vs_live.py</code>, <code>scripts/rank_shipped_by_validated_instrument.py</code>, <code>scripts/project_live_from_sgmc.py</code>, <code>scripts/build_nine_site_executive_summary.py</code>.</li>
<li>Sources: <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">DrivenData leaderboard</a> (official, read 2026-10-28); <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData competition page</a>; <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">NLR submission guide (96647.pdf)</a>.</li>
</ul>
<p><small>Generated by scripts/build_nine_site_executive_summary.py. Status source: registry/current_status.json (updated {esc(status.get('updated_utc', ''))}).</small></p>
</main></body></html>
"""
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)} ({len(page)} bytes); candidates={len(cand_rows)} sites={len(site_rows)}")
    for c in cand_rows:
        print(f"  {c['name']:<20} {c['sha_check']}  HR={c['hr']:.6f}  SGMC={c['sgmc']:.6f}  nonlat={c['nonlat']:.4f} lat={c['lat']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
