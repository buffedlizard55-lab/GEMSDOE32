"""The current prohibition must precede all archived promotion claims."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_current_stop_notice_is_above_download():
    for name in ['docs/index.html', 'docs/executive-summary.html', 'index.html']:
        text = (ROOT / name).read_text()
        assert text.index('DO NOT SUBMIT — current strict protocol review') < text.index('href="downloads/' if name.startswith('docs/') else 'href="docs/downloads/')
        assert 'No file is approved by this review' in text
        assert 'protocol-audit.json' in text
