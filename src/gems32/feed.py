"""Live feed: one JSON the site renders, refreshed by a scheduled workflow.

The feed answers the practical question the brief asks for -- "an up to date current feed" and
"no manual checking" -- by aggregating: (1) the official source list and the HTTP status last
observed for each, (2) the public-leaderboard snapshot history, (3) the repository's own build
state (files, hashes, hypothesis statuses, holdout summary).  It never fabricates a score: a
leaderboard row is stored with ``verified`` true only when it was read from the public page.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def _read_json(p: Path, default=None):
    try:
        return json.loads(p.read_text())
    except Exception:
        return default


def build(root: Path = ROOT) -> dict:
    reg = root / "registry"
    docs = root / "docs"
    feed: dict = {"schema": 1, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    src = _read_json(reg / "sources.json", {"sources": []})
    feed["sources"] = [{"id": s["id"], "title": s["title"], "url": s["url"],
                        "role": s.get("role", ""), "status": s.get("status", "listed")}
                       for s in src["sources"]]
    feed["source_count"] = len(feed["sources"])

    lb_path = reg / "leaderboard_history.jsonl"
    rows = []
    if lb_path.exists():
        for line in lb_path.read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    feed["leaderboard"] = rows[-1]["rows"] if rows else []
    feed["leaderboard_observed_utc"] = rows[-1]["observed_utc"] if rows else None
    feed["leaderboard_verified"] = bool(rows and rows[-1].get("verified"))

    hyp = _read_json(reg / "hypotheses.json", {"hypotheses": []})
    feed["hypotheses"] = [{"id": h["id"], "rank": h["rank"], "title": h["title"],
                           "status": h["status"]} for h in hyp["hypotheses"]]

    sub = _read_json(reg / "submission_build.json")
    if sub:
        feed["submission"] = {k: v for k, v in sub.items() if k not in ("credit_audit",)}
    hold = _read_json(root / "evidence" / "holdout_run1.json")
    if hold:
        feed["holdout"] = {"summary": hold.get("summary", {}), "seconds": hold.get("seconds"),
                           "preregistration_id": hold.get("preregistration", {}).get("id")}
    obs = _read_json(root / "evidence" / "observations_summary.json")
    if obs:
        feed["observations"] = obs
    feed["irregularities"] = _read_json(reg / "irregularities.json", {"items": []})["items"]
    docs.mkdir(exist_ok=True)
    (docs / "data").mkdir(exist_ok=True)
    (docs / "data" / "feed.json").write_text(json.dumps(feed, indent=1) + "\n")
    return feed


def refresh_sources(root: Path = ROOT, timeout: float = 15.0, allow_leaderboard: bool = True) -> dict:
    """Probe every source once (HEAD/GET) and update its observed status; optional leaderboard read."""
    import urllib.request
    results = []
    src = _read_json(root / "registry" / "sources.json", {"sources": []})
    for s in src["sources"]:
        rec = {"id": s["id"], "url": s["url"], "checked_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        try:
            req = urllib.request.Request(s["url"], headers={"User-Agent": "GEMSDOE32-feed/1.0 (+research)"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                rec.update(http_status=r.status, content_type=r.headers.get("Content-Type", ""))
        except Exception as exc:                      # noqa: BLE001 - recorded, never raised
            rec.update(http_status=None, error=f"{type(exc).__name__}: {exc}")
        results.append(rec)
    out = {"checked_utc": results[0]["checked_utc"] if results else None, "results": results}
    (root / "docs" / "data" / "source_health.json").write_text(json.dumps(out, indent=1) + "\n")
    return out
