"""The single authoritative verdict must precede all download buttons (Round 6).

Supersedes the protocol-review-era test that pinned the DO-NOT-SUBMIT banner:
the invariant is unchanged (authoritative notice first, downloads after),
the verdict itself is now data-driven from evidence/round6_run_card.json.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

R6_FILE = "gemsdoe32-r6-stepprofile-b2-37654-20261026T002502Z-23fbbb51-zeros.tif"


def test_current_stop_notice_is_above_download():
    for name in ['docs/index.html', 'docs/executive-summary.html', 'index.html']:
        text = (ROOT / name).read_text()
        verdict_marker = 'OK TO DOWNLOAD AND SUBMIT' if 'OK TO DOWNLOAD AND SUBMIT' in text else 'DO NOT SUBMIT'
        dl = 'href="downloads/' if name.startswith('docs/') else 'href="docs/downloads/'
        assert text.index(verdict_marker) < text.index(dl)
        # the banner must name exactly which file the verdict covers
        assert R6_FILE in text
        # contradictory legacy banner must be gone
        assert 'DO NOT SUBMIT — current strict protocol review' not in text
        assert 'No file is approved by this review' not in text
