#!/usr/bin/env python3
"""Re-read shipped bytes and publish a bounded nine-site review; never promotes."""
import hashlib
import html
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from gems32.byte_audit import inspect_saved_raster


def main():
    status = json.loads((ROOT / 'registry/current_status.json').read_text())
    old = json.loads((ROOT / 'evidence/focus_site_winner_overlap_20261026.json').read_text())
    newest = status['newest_unique']
    artifact = ROOT / newest['file']
    sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
    measured = inspect_saved_raster(artifact)
    card = {
        'hypothesis': 'Audit existing H48-FBGR artifact; no newly assigned method lane in this request.',
        'mechanism': 'Saved-byte verification and nine-site evidence review; no model experiment.',
        'non_fault_mimic': 'Lithologic contacts and radiometric acquisition seams can mimic FBGR targets.',
        'holdout': {'status': 'NOT_RERUN', 'reason': 'No new lane assigned; feature caches absent in checkout.',
                    'historical_evidence': newest['run_card'],
                    'leaderboard_estimate': None},
        'correlation_overlap_vs_registry': {
            'status': 'NOT_RERUN', 'historical_evidence': newest['run_card'],
            'literal_registry_passed': False,
            'warning': 'Do not substitute discrete-only uniqueness for the all-registry rule.'},
        'raster_sha256': sha,
        'hash_matches_registry': sha == newest['sha256'],
        'validator_output': measured,
        'submission_name': newest['submission_name'],
        'note': 'Existing H48 artifact re-audited; no new lane, no new score estimate, no upload authorization.',
        'verdict': 'negative', 'ok_to_submit': False,
        'experiments_used': 0, 'weekly_slots_used': 0,
    }
    rows = []
    for winner in old['historical_winners']:
        repo, ref, path = winner['repo'], winner['head'], winner['file']
        url = f'https://github.com/buffedlizard55-lab/{repo}/blob/{ref}/{path}?raw=true'
        rows.append(f'<tr><td>{repo}</td><td><a href="{html.escape(url)}">{html.escape(Path(path).name)}</a></td>'
                    f'<td>{winner["owner_reported_leaderboard_score"]:.4f} OWNER-REPORT; unconfirmed</td>'
                    '<td>Unavailable</td><td>No: spatial duplicate family</td><td>DO NOT RESUBMIT</td></tr>')
    text = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Nine-site executive review · GEMSDOE32</title><link rel="stylesheet" href="assets/site.css">
<body><main class="wrap"><h1>Nine-site executive review — 2026-10-27</h1>
<p><a href="index.html">Home</a> · <a href="executive-summary.html">Submission instructions</a> ·
<a href="research/review-and-next-hypotheses-20261027.md">Review, hypotheses and limitations</a></p>
<section class="card" style="border:3px solid #b91c1c"><h2>DO NOT SUBMIT</h2>
<p>No new submission has passed all requested gates. No weekly slots were used. The existing H48 file is
available for research only; format validity does not establish scientific superiority or uniqueness.</p>
'''
    text += f'<p><a class="btn" href="{html.escape(newest["file"].removeprefix("docs/"))}">Download existing H48 TIF — AUDIT ONLY</a></p></section>'
    text += '''<h2>Best historical file at each requested site</h2><p>These are historical winners from pinned repository evidence, not newly validated recommendations.
No submission-page receipt establishes ORGANIZER-CONFIRMED scores. Consequently none of the owner-reported
numbers is treated as an estimated score or a confirmed score. Download links identify pinned bytes, not live repository heads.</p>
<div style="overflow:auto"><table><thead><tr><th>Site</th><th>Historical file (research download)</th><th>Reported result</th>
<th>Estimated future score</th><th>Unique under requested spatial rule?</th><th>Decision</th></tr></thead><tbody>'''
    text += ''.join(rows) + '</tbody></table></div>'
    text += '''<h2>Why did H33-B2 report the highest result?</h2><p>The saved evidence supports a spacing/budget explanation:
H33 prunes the H19-5 family into a sparse, buffered dot set, avoiding redundant nearby predictions while retaining
coverage under the distance-tolerant metric. That is a plausible mechanism, not a demonstrated causal explanation of hidden labels.
The reported result of 0.2778 does not imply that new fault physics was discovered. Repackaging, renaming or adding
noise to this file is not a new scientific submission.</p><p>There is no defensible leaderboard-score estimate for a new candidate.
The prompt supplies conflicting leaderboard maxima (0.3195 and 0.4413); neither was freshly authenticated here.
Holdout results cannot be converted into a leaderboard score without calibrated out-of-sample evidence.</p>
<h2>Fresh automated saved-byte check</h2><p>This audit checks all cells, so its finite/range check is stronger than
an inside-footprint-only check. Grid matching is against documented historical constants, NOT a newly authenticated
organizer template. Catalogue exclusion and registry overlap were NOT rerun.</p>'''
    text += '<pre style="overflow:auto">' + html.escape(json.dumps(measured, indent=2)) + '</pre>'
    text += '<p>SHA-256: <code>' + sha + '</code></p>'
    text += '''<h2>Evidence and official review links</h2><ul>
<li><a href="../evidence/focus_site_winner_overlap_20261026.json">Historical nine-site overlap evidence (not rerun)</a></li>
<li><a href="../evidence/review_audit_20261027.json">This review run card</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution/tree/aebe92f7c8a990f0e3443451b7a825d9afd6336b">Official reference repository (commit fetched this session)</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">Official competition data (not fetched this session)</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Official leaderboard (not fetched this session)</a></li>
</ul><h2>What happens next?</h2><p>Establish an explicit method lane, restore the hash-pinned cached stack, and resolve the literal
registry-lattice stop without silently exempting a raster. Test each feature alone, then compare a fold-local candidate
against the best candidate on the same evaluator with paired spatial confidence intervals. Stop on duplication.
Only a fully passing candidate may enter the separate weekly-slot selector.</p></main></body></html>'''
    (ROOT / 'docs/nine-site-review.html').write_text(text)
    (ROOT / 'evidence/review_audit_20261027.json').write_text(json.dumps(card, indent=2) + '\n')
    print(json.dumps({'byte_check_passed': measured['strict_primary_passed'], 'sha256': sha, 'ok_to_submit': False}))


if __name__ == '__main__':
    main()
