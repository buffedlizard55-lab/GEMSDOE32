#!/usr/bin/env python3
"""Render the fresh, bounded executive review. Offline and deterministic; never promotes."""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = 'evidence/focus_review_20261028.json'
REVIEW = 'research/review-20261028.md'


def esc(value):
    return html.escape(str(value), quote=True)


def build():
    r = json.loads((ROOT / EVIDENCE).read_text())
    current = r['current_artifact']
    status = json.loads((ROOT / 'registry/current_status.json').read_text())
    newest = status['newest_unique']
    artifact_label = newest.get('submission_name') or Path(newest['file']).stem
    # A stale review must never display one candidate's validation on another download.
    fresh = (current['sha256'] == status['newest_unique']['sha256']
             and current['file'] == status['newest_unique']['file']
             and hashlib.sha256((ROOT/current['file']).read_bytes()).hexdigest() == current['sha256'])
    bound = r['budget_feasibility']
    rows, details = [], []
    for w in r['winners']:
        name = Path(w['path']).name
        fmt = 'PASS' if w['validator']['passed'] else 'FAIL: not all cells finite'
        aliases = [p['reference'] for p in r['directional_comparisons']
                   if p['candidate'] == w['repo'] and p['footprint_pixels_identical']]
        unique = ('NO — spatial duplicate family' if not w['unique_among_nine_winners']
                  else 'No duplicate measured among these eight; full registry unchecked')
        if aliases:
            unique += '; same footprint values as ' + ', '.join(aliases)
        rows.append(f'''<tr><th scope="row"><a href="#{esc(w['repo'])}">{esc(w['repo'])}</a></th>
<td><a href="{esc(w['download_url'])}">{esc(name)}</a></td>
<td>{w['unconfirmed_user_claim']:.4f}<br><small>USER-REPORTED / unconfirmed</small></td>
<td>Unavailable</td><td>{esc(unique)}</td><td>{esc(fmt)}</td><td class="bad">DO NOT RESUBMIT</td></tr>''')
        details.append(f'''<section class="card" id="{esc(w['repo'])}"><h3>{esc(w['repo'])} — historical winner review</h3>
<p><strong>{esc(name)}</strong></p><p>Highest reported result for this site in the supplied shortlist:
{w['unconfirmed_user_claim']:.4f} (unconfirmed user claim, not ORGANIZER-CONFIRMED).
No new score estimate is justified. Prediction count: {w['positive_pixels']:,}; positive pixels on known faults: {w['positive_on_catalogue']:,}.
Maximum directional overlap against another winner: {100*w['max_directional_overlap']:.2f}% within 3 pixels.
All comparisons use the complete footprint, not sampled ranks.</p>
<p>Automated decision: <strong class="bad">not unique; do not resubmit</strong>. Strict finite-grid format: {esc(fmt)}.
This is a comparison of named historical files, not a claim that every later artifact on this site was audited.</p>
<p><a href="{esc(w['download_url'])}">Download pinned historical TIF for research</a> ·
<a href="https://github.com/buffedlizard55-lab/{esc(w['repo'])}/tree/{esc(w['ref'])}">Pinned repository source</a></p>
<details><summary>File identity</summary><p>SHA-256: <code>{esc(w['sha256'])}</code><br>
Git blob verified: <code>{esc(w['git_blob_sha'])}</code></p></details></section>''')
    latest_link = (f'<a class="btn alt" href="{esc(current["file"].removeprefix("docs/"))}" download>Download {html.escape(artifact_label)} GeoTIFF — RESEARCH / AUDIT ONLY</a>'
                   if fresh else '<p class="bad">This audit is stale; rerun refresh_focus_review.py before using its artifact link.</p>')
    doc = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nine-site executive review · GEMSDOE32</title><link rel="stylesheet" href="assets/site.css">
<style>.review-table{{overflow-x:auto}} td:nth-child(2){{min-width:240px;overflow-wrap:anywhere}} code{{overflow-wrap:anywhere}} main{{padding-bottom:40px!important}} h1{{margin-top:24px}}</style></head>
<body><main class="wrap"><h1>Nine-site executive review</h1>
<p class="mut">Snapshot: {esc(r['generated_utc'])} · automated byte and spatial audit · no competition slot used</p>
<nav aria-label="Review navigation"><a href="index.html">Home</a><a href="executive-summary.html">Submission guide</a>
<a href="{REVIEW}">Scientific review &amp; next hypotheses</a><a href="../{EVIDENCE}">Full evidence JSON</a></nav>
<section class="dl" style="border-color:var(--bad)"><h2 class="bad">DO NOT SUBMIT</h2>
<p><strong>No new, unique, scientifically validated submission was generated in this review.</strong>
The best historical result in the supplied nine-site shortlist is GEMSDOE32 H33-B2, reported as 0.2778;
there is no organizer receipt authenticating that claim. It is already submitted and fails your spatial-uniqueness rule.</p>
<p>The existing audited artifact passes automated format/range checks against the restored mirror template,
but fails literal uniqueness. It is not a newly generated candidate. No human inspection is needed for this negative decision.</p>
<p>The latest registered candidate is <b>{html.escape(artifact_label)}</b>; it remains a research artifact.</p>
{latest_link}<p>Research download: yes. Competition upload: <strong>no</strong>. Estimated leaderboard score: <strong>unavailable</strong>.</p></section>
<section class="card"><h2>A mathematically impossible dot budget</h2>
<p>The calibration lattice is within 3 pixels of {100*r['lattice_footprint_coverage_within_3px']:.4f}% of the footprint.
After known-fault exclusion, only <strong>{bound['outside_3px_pixels']:,}</strong> allowed pixels are outside its 3-pixel collar.
For N distinct dots to pass the 70% limit, at least 30% must be outside: <code>3N ≤ 10U</code>.</p>
<p>Therefore <strong>N ≤ {bound['max_feasible_distinct_dots']:,}</strong> is a necessary bound for this reference.
The current <strong>{bound['budget']:,}-dot</strong> configuration cannot pass even with perfect placement.
A lower budget is not automatically unique or scientifically useful; all other references still apply.</p>
<p>Measured current-artifact overlap with this lattice: <strong>{100*r['literal_lattice_check']['comparisons'][0]['within_3px_fraction']:.4f}%</strong>.
The shared feasibility check now catches this before a new model experiment. No reference was silently exempted.</p></section>
<h2>What file is best at each site?</h2>
<p>“Best” below means highest <em>user-reported historical result in this request</em>, not an upload recommendation.
No claim has a submission-page receipt; none is ORGANIZER-CONFIRMED. A projection is not a score.
The nine named historical files were freshly fetched at pinned repository heads and verified against Git blob identities.
This is not a complete census of all registry rasters or all later submissions.</p>
<div class="review-table"><table><caption>Historical downloads, claims, estimate availability, uniqueness and automated format checks</caption>
<thead><tr><th>Site</th><th>Historical TIF — research only</th><th>Unconfirmed historical claim</th><th>Estimated future score</th>
<th>Unique?</th><th>Strict format</th><th>Upload decision</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p>GEMSDOE25 and GEMSDOE30 have identical values inside the footprint despite different file hashes.
Renaming, changing compression or converting outside-footprint NaNs to zero does not make a new scientific submission.</p>
<h2>Why might H33-B2 have performed better?</h2>
<p>The audited H33 file is sparse ({next(w['positive_pixels'] for w in r['winners'] if w['repo']=='GEMSDOE32'):,} dots).
The code and historical lineage describe a B=2 catalogue-distance pruning of a related dot family.
Under the requested distance-weighted Tversky metric, removing a redundant prediction can reduce false-positive mass
without reducing the maximum kernel credit at a truth pixel. That can improve DTI. Conversely, removing useful
coverage can lower DTI. Hidden labels are unavailable, so neither the causal contribution of pruning nor a future
improvement over the unconfirmed 0.2778 can be established from the reported results alone.</p>
<p>The target is fault prediction relevant to geothermal exploration, not direct proof of a vent or viable reservoir.
The official reference notebook uses ordinary Tversky <em>training loss</em>; it does not independently verify the
300 m scoring kernel. See the <a href="{REVIEW}">scientific review</a> for evidence boundaries and ranked hypotheses.</p>
<h2>Automated format validation and the range error</h2>
<p>The shared validator checks actual saved bytes for one float32 band, CRS, shape, transform, finite in-footprint
values and whole-array values in [0,1]. The existing audited artifact passes. The template is a hash-pinned owner mirror,
not newly authenticated organizer data. A format pass is necessary but is not a score or uniqueness pass.</p>
<p>Five historical files fail the conservative whole-array finite check because of outside-footprint NaNs.
This does not prove the organizer rejected those historical files. The current writer supplies an all-finite zeros variant.
It now rejects fractional or invalid inputs instead of silently turning every positive probability into a dot.</p>
<details><summary>Existing audited file identity and validation</summary><p>Name: <code>{esc(current['submission_name'])}</code><br>
Note: <code>{esc(current['note'])}</code><br>SHA-256: <code>{esc(current['sha256'])}</code></p>
<pre>{esc(json.dumps(current['validator'], indent=2))}</pre></details>
<h2>How submission works once a candidate passes</h2>
<ol><li>Run the shared feasibility, leakage, fold-local hide-and-recover, full-registry surface/final-dot and saved-byte gates.
A paired spatial confidence interval must favor the candidate over the current best on the same evaluator.</li>
<li>The separate selector checks the authenticated weekly cap and available slots. This review neither chooses a slot nor uploads.</li>
<li>Only after release authorization, download the approved all-finite single-band TIF (or its single-TIF ZIP),
check its displayed SHA-256, and choose it in the competition’s “File to submit” field. Use the approved unique name and note of at most 140 characters.</li>
<li>Save the organizer receipt, submitted file hash and score. Only then label the result ORGANIZER-CONFIRMED.</li></ol>
<p>These are future instructions, not authorization to upload any file currently linked here. The current weekly cap and leaderboard
were not fetched; conflicting historical figures in the request cannot identify today's leader.</p>
<h2>Individual site summaries</h2>{''.join(details)}
<h2>Sources and access boundaries</h2><ul>
<li><a href="../evidence/official/reference-excerpts-20261028.json">Fresh official notebook excerpts and source hash</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b">Official reference solution — fetched via GitHub</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem/metric page — not fetched here</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">Official competition data — not fetched here</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Official leaderboard — not fetched here</a></li>
</ul><p>All nine summaries are published here in GEMSDOE32. Other repositories were read only; their websites were not changed.</p>
</main></body></html>'''
    (ROOT / 'docs/nine-site-review.html').write_text(doc)
    return doc


def main():
    build()
    print('Rendered docs/nine-site-review.html from pinned evidence; upload decision remains negative.')


if __name__ == '__main__':
    main()
