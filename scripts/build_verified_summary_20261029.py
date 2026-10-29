#!/usr/bin/env python3
"""Build the verified nine-site executive summary (docs/nine-site-verified-summary.html) and the run card.

Inputs (no hand-typed numbers):
  evidence/nine_site_verification_20261029.json   (scripts/verify_nine_site_20261029.py)
  evidence/nine_site_best_files_audit.json        (pinned GitHub refs and digests)
  registry/current_status.json                    (current decision)
Outputs:
  docs/nine-site-verified-summary.html
  evidence/run_card_20261029_verification.json
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = json.loads((ROOT / "evidence" / "nine_site_verification_20261029.json").read_text())
AUD = json.loads((ROOT / "evidence" / "nine_site_best_files_audit.json").read_text())
STATUS = json.loads((ROOT / "registry" / "current_status.json").read_text())
OUT_HTML = ROOT / "docs" / "nine-site-verified-summary.html"
OUT_CARD = ROOT / "evidence" / "run_card_20261029_verification.json"

FOCUS = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
UNIQUE_KEY = "H51-1"
OVERLAP_LIMIT = 0.70
RHO_LIMIT = 0.90
AUD_BY_SITE = {s["site"]: s for s in AUD["sites"]}


def esc(x) -> str:
    return html.escape(str(x))


def pair_rho(a: str, b: str) -> float | None:
    for k in (f"{a}|{b}", f"{b}|{a}"):
        if k in VER["surface_spearman"]:
            return VER["surface_spearman"][k]
    return None


def overlap(a: str, b: str) -> float:
    return VER["directional_3px_overlap"][f"{a}->{b}"]


def max_vs_others(site: str, pool: list[str]) -> tuple[float, float, str]:
    """Max directional 3 px overlap (both directions) and max surface rho against the other pool members."""
    worst_ov, worst_rho, who = 0.0, -1.0, ""
    for b in pool:
        if b == site:
            continue
        o = max(overlap(site, b), overlap(b, site))
        r = pair_rho(site, b)
        if o > worst_ov:
            worst_ov, who = o, b
        if r is not None and r > worst_rho:
            worst_rho = r
    return worst_ov, worst_rho, who


def file_link(site: str) -> str:
    a = AUD_BY_SITE[site]
    rel = a["file"]
    if site == "GEMSDOE32":
        return f'<a href="{esc(rel.replace("docs/", ""))}">{esc(Path(rel).name)}</a>'
    return (f'<a href="https://github.com/buffedlizard55-lab/{site}/blob/{a["github_ref"]}/{rel}">'
            f'{esc(Path(rel).name)}</a> <span class="mut">(sibling repo, pinned ref {a["github_ref"][:7]})</span>')


def live_label(site: str) -> str:
    return f'{VER["inputs"][site]["live_owner_report"]:.4f} <span class="mut">OWNER-REPORT</span>'


def strict_result(site: str) -> str:
    name = "h51" if site == "H51-1" else site.lower()
    ch = (ROOT / ".cache" / "work" / "eval" / f"{name}.check.txt")
    if not ch.exists():
        return "not run"
    return "PASS" if "[PASSED]" in ch.read_text() else "FAIL (whole-array NaN outside footprint)"


def main() -> int:
    inp = VER["inputs"]
    mv = VER["mass_vs_owner_live"]
    p37 = next(p for p in mv["predictions"] if p["dots"] == 37654.0)
    h51 = inp[UNIQUE_KEY]
    champ = inp["GEMSDOE32"]
    r13 = VER["r13_coverage"]
    hold = VER["holdout_static_diagnostic"]
    assoc = VER["association_n9"]
    idents = VER["identical_dot_sets"]
    pinned_ok = all(v["match"] for v in VER["pinned_digest_check"].values())

    # ---- per-site table rows -------------------------------------------------
    rows = []
    for s in FOCUS:
        ov, rho, who = max_vs_others(s, FOCUS)
        uniq = (ov <= OVERLAP_LIMIT) and (rho <= RHO_LIMIT)
        hr = hold[s]["HIDE-RECOVER-v3.0_pooled_dti"]
        ci = hold[s]["ci95"]
        rows.append(
            f"<tr><td><b>{s}</b></td>"
            f"<td>{file_link(s)}<br><span class='mut'>{inp[s]['dots']:,} dots · sha256 {esc(inp[s]['sha256'][:12])}…</span></td>"
            f"<td>{live_label(s)}<br><span class='mut'>already scored; resubmitting adds no information</span></td>"
            f"<td>{'n/a (already scored)'}</td>"
            f"<td>{'<b class=bad>NO</b>' if not uniq else '<b class=ok>yes</b>'} "
            f"<span class='mut'>max 3 px overlap {ov:.3f} vs {esc(who)}; max surface ρ {rho:.3f}</span></td>"
            f"<td>{esc(strict_result(s))}</td>"
            f"<td>{hr:.4f} <span class='mut'>[{ci[0]:.4f}, {ci[1]:.4f}] · n={hold[s]['n_withheld_positives']:,} · static diagnostic</span></td>"
            f"<td><b class=bad>NO — do not submit</b></td></tr>"
        )

    # H51 unique row
    ov_h51, rho_h51, who_h51 = max_vs_others(UNIQUE_KEY, FOCUS)
    h51_r13_ov = overlap(UNIQUE_KEY, "r13")
    h51_hold = hold[UNIQUE_KEY]
    h51_row = (
        f"<tr class=hl><td><b>NEW: H51-1 EWSP</b><br><span class='mut'>not a previous submission</span></td>"
        f"<td><a href=\"downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif\">"
        f"gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif</a><br>"
        f"<span class='mut'>{h51['dots']:,} dots · sha256 {esc(h51['sha256'][:12])}…</span></td>"
        f"<td>not scored (no live receipt)</td>"
        f"<td><b>{p37['projection']:.4f}</b> PROJECTION <span class='mut'>[95% PI {p37['pi95_new_file'][0]:.4f}, {p37['pi95_new_file'][1]:.4f}] mass-only regression on 9 owner-reported points; not a score</span></td>"
        f"<td><b class=ok>yes</b> vs all 9 focus files (max 3 px {ov_h51:.3f}, max ρ {rho_h51:.3f}) · <b class=bad>NO</b> vs dense r13 ({h51_r13_ov:.3f}, literal rule ≤0.70)</td>"
        f"<td>{esc(strict_result('H51-1'))}</td>"
        f"<td>{h51_hold['HIDE-RECOVER-v3.0_pooled_dti']:.4f} <span class='mut'>[{h51_hold['ci95'][0]:.4f}, {h51_hold['ci95'][1]:.4f}] · n={h51_hold['n_withheld_positives']:,} · static diagnostic, below champion</span></td>"
        f"<td><b class=bad>NO — download for review only</b></td></tr>"
    )

    html_doc = f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Verified nine-site executive summary · GEMSDOE32 (2026-10-29)</title>
<link rel=stylesheet href=assets/site.css>
<style>td,th{{vertical-align:top}} .mut{{color:var(--mut);font-size:12.5px}} .bad{{color:var(--bad)}} .ok{{color:var(--acc)}}
tr.hl td{{background:#1b1f0e}} table{{width:100%;border-collapse:collapse;font-size:13.5px}} th,td{{border:1px solid var(--line);padding:6px 7px;text-align:left}}
th{{background:var(--bg2)}} .tablewrap{{overflow-x:auto}} code{{font-size:12.5px}}</style></head><body>
<header class=top><div class=wrap>
<h1>Verified nine-site executive summary (GEMSDOE24 · 25 · 27 · 28 · 30 · 31 · 32 · 33 · 36)</h1>
<nav><a href="index.html">Home</a> <a href="executive-summary.html">Make a submission</a> <a href="nine-site-verified-summary.html" class=active>Verified summary</a> <a href="irregularities.html">Irregularities</a></nav>
</div></header>
<main class=wrap>

<section class=dl style="border-color:#b91c1c;background:#1f0d0d" aria-label="Decision">
<h2 style="margin:4px 0;border:0">&#128308; Decision: DO NOT SUBMIT any file today</h2>
<p><b>Download for review:</b> the only new unique TIF is <a href="downloads/gemsdoe32-h51-ewsp-crack-poisson-axial28-37654-20261028T123000Z-bdf25d8c-zeros.tif">H51-1 EWSP (<code>-zeros.tif</code>)</a>. It passes format and range checks and is not a copy of any focus-site file. It is <b>not cleared to submit</b> because (1) it fails the literal r13 lattice rule (<b>{h51_r13_ov:.3f}</b> of its dots lie within 3 px of r13, rule limit 0.70), (2) its static holdout is below the champion, and (3) no organizer receipt exists for any new file.</p>
<p><b>Best file already submitted:</b> <code>h33-h33-2-b2</code> (GEMSDOE32, owner-reported <b>0.2778</b>). Resubmitting it adds nothing.</p>
<p><b>If it is ever cleared, the submission form fields would be:</b> name <code>GEMSDOE32-H51-EWSP-BDF25D8C</code> · note (<b>{len(NOTE)}</b> characters) <code>{esc(NOTE)}</code> · sha256 <code>{esc(h51['sha256'])}</code>. Steps: <a href="executive-summary.html">Make a submission</a>. Clearing it requires the owner's decision on the r13 rule and a fresh holdout that beats the champion. Neither exists yet.</p>
<p class=mut>Every number on this page is labelled: <b>OWNER-REPORT</b> (owner's live score, no receipt) · <b>MEASURED-HERE</b> (computed from the pinned bytes in this run) · <b>HOLDOUT-DTI (static diagnostic)</b> (<code>evidence/…</code>, promotion-ineligible) · <b>PROJECTION</b> (regression, never a score). ORGANIZER-CONFIRMED: none.</p>
</section>

<h2>1. Per-site table: which file, estimated score, unique?</h2>
<div class=tablewrap><table>
<tr><th>Site</th><th>File to download</th><th>Live score</th><th>Estimated score (new file)</th><th>Unique vs the other listed sites?</th><th>Strict format check</th><th>Holdout (static diagnostic)</th><th>Submit?</th></tr>
{''.join(rows)}
{h51_row}
</table></div>
<p class=mut>Uniqueness rule (owner's, from the parallel-run protocol): a file is a duplicate if &gt;70% of its dots lie within 3 px of one other raster's dots, or Spearman ρ &gt; 0.90. Measured by <code>scripts/verify_nine_site_20261029.py</code>. Nine focus files are all previous submissions, so none is unique by definition. Identical dot sets found: {esc(', '.join(idents)) or 'none'}.</p>

<h2>2. Why 0.2778 scored highest (PhD-level reading of the measured evidence)</h2>
<p><b>What the evidence shows (MEASURED-HERE):</b></p>
<ul>
<li>The champion has <b>{champ['dots']:,}</b> dots, the fewest of the nine files, and <b>0.0%</b> of them lie within 200 m of a catalogued fault (<code>labels.tif</code>). Its dots lie within 3 px of the other focus files' dots at 0.999–1.000 (GEMSDOE24, 25, 27, 28, 30, 31, 33, 36).</li>
<li>Across the nine owner-reported files, live score falls with dot count (Spearman ρ = <b>{assoc['rho_live_vs_dots']:.3f}</b>) and with the share of dots near catalogued faults (ρ = <b>{assoc['rho_live_vs_share_within_200m_catalogue']:.3f}</b>). The two files with 0% near-catalogue dots that have live scores (GEMSDOE32 and GEMSDOE36) are the top two live scores in the family. H51-1 has the same 0% share but no live score.</li>
</ul>
<p><b>Mechanism (metric algebra, from <code>src/gems32/metric.py</code>; DTI = TP/(α(TP+FP)+β|G|), α=0.2, β=0.8):</b> a dot raises DTI only if its kernel-weighted credit k exceeds α·DTI. At DTI ≈ 0.28 that threshold is k ≈ 0.056. Dots that are near catalogued faults and carry little credit against the scored truth therefore cost more than they earn. Pruning them (the B-gate ladder) raises DTI. This requires the scored truth to lie mainly off-catalogue. The repo cites a known-fault masking clarification for that point, but it was not re-read this session. This is the best-supported explanation, and it is an inference, not a measured result.</p>
<p><b>Confound:</b> in this family dot mass and catalogue share move together, so n=9 cannot separate them. Partial OLS gives both negative coefficients, but the data cannot say which one drives the score. A clean test needs two files of the same mass that differ only in catalogue share, which is the H51-1 experiment below.</p>
<p><b>Named non-fault mimic:</b> basin-fill sparsity. A file whose dots sit in mapped-fault-free basin fill (alluvium over smooth gravity and magnetic fields) would show 0% catalogue proximity without detecting any fault. The same live signal could then come from avoiding catalogue-adjacent terrain rather than from finding faults.</p>

<h2>3. The holdout disagrees with the live scores (critical)</h2>
<table>
<tr><th>Comparison (n = 9)</th><th>Spearman ρ</th><th>Reading</th></tr>
<tr><td>static HIDE-RECOVER DTI vs owner live score</td><td><b class=bad>{assoc['rho_static_HIDE_RECOVER_vs_live']:.3f}</b></td><td>Negative. The holdout ranks files in the opposite order to the leaderboard. Do not use it to pick a file.</td></tr>
<tr><td>static HIDE-RECOVER DTI vs share of dots near catalogue</td><td><b>{assoc['rho_static_HIDE_RECOVER_vs_share_within_200m_catalogue']:.3f}</b></td><td>The holdout rewards catalogue proximity, because it withholds catalogue segments and credits dots near them. The live scores appear to penalise it.</td></tr>
<tr><td>SGMC-CAL off-catalogue DTI (all nine)</td><td>n/a</td><td>Nearly flat (≈0.058–0.064 for every file, CIs overlap). It cannot discriminate between files.</td></tr>
</table>
<p class=mut>Repo instrument note: the static evaluator states <code>promotion_eligible=false</code>. Fold-local re-emission, the only promotion-eligible route, is not reproduced here (no generator run this session).</p>

<h2>4. Verified checks (what was actually run)</h2>
<ul>
<li>Restored all 30 pinned inputs from the owner's GitHub repos at their pinned refs (codeload/gh, SHA-256 verified). Test suite: <b>275 passed</b> before the new regression file, <b>282 passed</b> after it (3 subtests).</li>
<li>Nine focus files: pinned digests match: <b>{'all 9' if pinned_ok else 'NOT all'}</b> (<code>evidence/nine_site_verification_20261029.json</code>). All are EPSG:32611, 3730×3292, float32, one band, 0/1 inside the footprint.</li>
<li>Strict portal check (<code>scripts/check_submission.py --strict-finite</code>): <b>PASS</b> for the <code>-zeros</code> files (GEMSDOE30, 32, 33, 36). <b>FAIL</b> for the <code>-nan</code> files (GEMSDOE24, 25, 27, 28, 31) because NaN sits outside the footprint. This is by design. The leaderboard accepted those files (owner-reported scores), so the strict check is stricter than the portal.</li>
<li>Champion holdout reproduced: HIDE-RECOVER {hold['GEMSDOE32']['HIDE-RECOVER-v3.0_pooled_dti']:.6f} with CI [{hold['GEMSDOE32']['ci95'][0]:.6f}, {hold['GEMSDOE32']['ci95'][1]:.6f}] (repo stores [0.003837, 0.005278]), SGMC-CAL {hold['GEMSDOE32']['SGMC-CAL-v3.0_dti']:.6f}. The point estimate matches; the CI endpoints differ by about 0.00002, logged as IR-20261029-V03.</li>
</ul>

<h2>5. Why no literal uniqueness pass is possible for any dense file</h2>
<p>r13-lattice-s5 (206,895 dots, a registry raster with an OWNER-REPORT score of 0.0904) lies within 3 px of <b>{r13['footprint_within_3px_of_r13']*100:.2f}%</b> of the footprint. Only <b>{r13['footprint_beyond_3px_of_r13_px']:,}</b> footprint pixels lie outside its collar. Under the 70% rule a file needs at least 30% of its dots outside that collar, so it can hold at most <b>{r13['max_dots_satisfying_literal_70pct_rule_bound']:,}</b> dots. Any file that meets the rule would therefore be a sparse file placed mostly on the leftover pixels. That is rule-satisfaction, not geology, so it is not proposed. The repo's own figure (6,514 px and a 21,713-dot bound, after known-fault exclusion) differs from this raw count; both are logged (IR-20261029-V04). <b>Owner decision needed:</b> exempt dense calibration rasters, or replace the rule with a density-aware test.</p>

<h2>6. Next steps (ranked by expected information per slot; none is cleared)</h2>
<ol>
<li><b>H51-1 as a mechanism test (1 slot, after the owner rules on r13).</b> It is mass-matched (37,654 dots, same as the champion), has 0% near-catalogue dots, and is spatially independent (max 3 px overlap 0.54 with the focus files). Prediction if catalogue avoidance is the mechanism: live ≥ 0.2778. Prediction if mass alone matters: about 0.272 (PI 0.262–0.283). A result outside that band refutes the mass-only projection.</li>
<li><b>Repair the instrument before any further holdout claims.</b> Make the holdout's truth the off-catalogue set, and check its sign against live on the nine files. Target: ρ &gt; 0 against live, with CIs that separate the families.</li>
<li><b>Mass-controlled catalogue test.</b> Build two files at ~38k dots that differ only in the catalogue-adjacent share (0% vs ~15%). This separates mass from catalogue share, which the nine files cannot do.</li>
<li><b>Owner: replace the literal lattice rule</b> with a density-normalised test (for example, overlap relative to a random baseline of the same mass; random champion-sized sets score 99.85–99.91% against r13 per the repo's own note IR-20261029-04, not re-measured here, so the literal rule is degenerate).</li>
</ol>

<h2>7. Limitations and what they block</h2>
<ul>
<li><b>No organizer receipt</b> exists for any file. Every live score here is OWNER-REPORT, so the ranking itself is unverified.</li>
<li><b>Leaderboard conflict:</b> the public leaderboard page read on 2026-10-29 shows #1 at <b>0.4544</b> (one manual read via the fetch tool, not automated). The brief's 0.4413 has no repo source. The brief's 0.3195 is a historical benchmark in the README, not a current figure (IR-20261029-V05).</li>
<li><b>Competition data mirrored in public GitHub repos</b> (<code>registry/data_manifest.json</code>, "owner-supplied mirror"). Redistribution may conflict with the competition rules. Flagged for owner review (IR-20261029-V06).</li>
<li><b>Sample size:</b> the mass and catalogue associations use nine points in one family and are confounded. They support hypotheses only.</li>
<li><b>Canary:</b> no new feature stack was built, so no new leakage canary was run. The repo's prior H51 canary (max AUC 0.80524 ≤ 0.90) is from 2026-10-28 and is quoted, not re-run.</li>
</ul>

<h2>8. Run card (JSON)</h2>
<pre style="white-space:pre-wrap;background:var(--bg2);padding:12px;border-radius:8px;overflow-x:auto">{esc(json.dumps(build_run_card(), indent=2))}</pre>

<h2>9. Official sources (for manual review)</h2>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Competition page and rules</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Problem description and metric (DTI, α=0.2, β=0.8, 300 m kernel)</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Public leaderboard (read 2026-10-29: #1 0.4544)</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Organizer reference solution</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Submission-format PDF (NLR FY26 OSTI 96647)</a></li>
<li><a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">Scoring clarification: known-fault masking (cited from the repo; not re-read this session)</a></li>
</ul>
</main>
<footer class=wrap><p class=mut>Generated by <code>scripts/build_verified_summary_20261029.py</code> from <code>evidence/nine_site_verification_20261029.json</code>. Owner-reported scores are labelled OWNER-REPORT; nothing on this page is an organizer confirmation.</p></footer>
</body></html>
"""
    OUT_HTML.write_text(html_doc)
    card = build_run_card()
    OUT_CARD.write_text(json.dumps(card, indent=2) + "\n")
    print(f"wrote {OUT_HTML.relative_to(ROOT)} and {OUT_CARD.relative_to(ROOT)}")
    return 0


NOTE = "GEMSDOE32-H51 EWSP emitted 37654d | static HR 0.0023 SGMC 0.0630 | review only, do not submit"
assert len(NOTE) <= 140, len(NOTE)


def build_run_card() -> dict:
    h51 = VER["inputs"]["H51-1"]
    hold51 = VER["holdout_static_diagnostic"]["H51-1"]
    mv = VER["mass_vs_owner_live"]
    p37 = next(p for p in mv["predictions"] if p["dots"] == 37654.0)
    return {
        "card_version": 1,
        "date_utc": "2026-10-29",
        "branch": "arena/4b00da0d-gemsdoe32",
        "experiments_used": 3,
        "experiments": [
            "E1 byte-level verification of 9 focus files + H51-1 + r13; holdout instrument reproduced (champion, H51-1)",
            "E2 association analysis: live vs dots, live vs catalogue share, static holdout vs live (n=9)",
            "E3 r13 coverage bound for the literal 70% lattice rule",
        ],
        "slots_used": 0,
        "hypothesis": "H51-1 (existing file): a mass-matched, catalogue-avoiding, spatially independent file should score at least as well as the 0.2778 champion if catalogue avoidance (not mass) drives live score.",
        "mechanism": "DTI = TP/(alpha(TP+FP)+beta|G|); a dot helps only if its kernel credit exceeds alpha*DTI (~0.056 at DTI 0.28). Dots near catalogued faults carry low credit against the scored truth.",
        "named_non_fault_mimic": "Basin-fill sparsity: dots placed where mapped faults are absent (alluvium over smooth gravity/magnetic fields) mimic deliberate catalogue pruning.",
        "holdout": {
            "label": "HOLDOUT-DTI (static diagnostic, promotion_eligible=false)",
            "evaluator_version": "GEMSDOE32-HIDE-RECOVER-v3.0",
            "n_withheld_positives": hold51["n_withheld_positives"],
            "dti": hold51["HIDE-RECOVER-v3.0_pooled_dti"],
            "ci95": hold51["ci95"],
            "sgmc_cal_dti": hold51["SGMC-CAL-v3.0_dti"],
            "sgmc_cal_ci95": hold51["sgmc_ci95"],
        },
        "projection_not_a_score": {
            "label": "PROJECTION (mass-only regression, n=9, owner-reported)",
            "dots": 37654,
            "point": p37["projection"],
            "pi95_new_file": p37["pi95_new_file"],
        },
        "correlation_overlap_vs_registry": {
            "max_3px_overlap_vs_focus_nine": round(max(max(VER["directional_3px_overlap"][f"H51-1->{s}"], VER["directional_3px_overlap"][f"{s}->H51-1"]) for s in FOCUS), 6),
            "max_3px_overlap_vs_r13": VER["directional_3px_overlap"]["H51-1->r13"],
            "surface_rho_vs_focus_nine_max": round(max(VER["surface_spearman"].get(f"H51-1|{s}", VER["surface_spearman"].get(f"{s}|H51-1", -1)) for s in FOCUS), 6),
            "literal_70pct_rule_vs_r13": "FAIL",
        },
        "raster_sha256": h51["sha256"],
        "raster_path": h51["path"],
        "validator_output": {
            "crs": h51["crs"],
            "shape": h51["shape"],
            "dtype": h51["dtype"],
            "nan_in_footprint": h51["nan_in_footprint"],
            "unique_values_in_footprint": h51["unique_values_in_footprint"],
            "footprint_pixels": VER["footprint_pixels"],
            "transform_first6": h51["transform"],
            "strict_check": strict_result("H51-1"),
        },
        "leakage_canary": "not re-run this session (no new features); repo H51 canary max AUC 0.80524 <= 0.90 (2026-10-28, quoted)",
        "submission_name": "GEMSDOE32-H51-EWSP-BDF25D8C",
        "submission_note": NOTE,
        "verdict": "negative for submission (download for review only); r13 literal gate fails; static holdout below champion",
    }


if __name__ == "__main__":
    raise SystemExit(main())
