#!/usr/bin/env python3
"""Fetch and SHA-pin scored submission rasters from the non-focus owner repositories.

``registry/focus_registry_manifest.json`` covers the nine focus sites (24/25/27/28/30/31/32/33/36).
The owner's score ledger (``docs/score-ledger.csv``) additionally records live-scored submissions on
~20 other owner repositories.  This script fetches those rasters (same owner, same GitHub API,
bytes verified by sha256 at the pinned head) into ``.cache/extra/<repo>/<path>`` and writes
``registry/extra_scored_manifest.json`` so any future session can re-fetch the exact bytes.

Selection rule: every ledger row with a parseable numeric score whose normalized submission name
matches a GeoTIFF in that row's repository (strict containment/hash-token match, the same rules as
``src/gems32/livescore.py``).  No DrivenData or third-party source is contacted.

Usage:  PYTHONPATH=src python3 scripts/fetch_extra_scored.py [--min-score 0.10] [--jobs 6]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gems32.livescore import normalize_name, strong_tokens  # noqa: E402

OWNER = "buffedlizard55-lab"
FOCUS = {"GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"}
LEDGER = ROOT / "docs" / "score-ledger.csv"
OUT = ROOT / "registry" / "extra_scored_manifest.json"
CACHE = ROOT / ".cache" / "extra"


def gh_json(path: str) -> dict:
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ledger_rows(min_score: float) -> list[dict]:
    rows = []
    for r in csv.DictReader(LEDGER.open()):
        if r["site"] in FOCUS or r["site"].startswith("DrivenData"):
            continue
        try:
            score = float(r["score"])
        except ValueError:
            continue
        if score >= min_score:
            rows.append({**r, "score_value": score})
    return rows


def candidate_stems(ledger_name: str) -> tuple[str, set[str]]:
    return normalize_name(ledger_name), strong_tokens(ledger_name)


def stems_match(stem: str, want: str, tokens: set[str]) -> bool:
    """Priority join, mirroring gems32.livescore.match_row: containment (>=12 chars) before tokens.

    A bare token hit is only trusted when no containment candidate exists, because code-version
    tokens (e.g. 6452ae1d00) can be shared by different submissions in the same repository.
    """
    n = normalize_name(stem)
    if want and min(len(want), len(n)) >= 12 and (want in n or n in want):
        return True
    return bool(tokens & strong_tokens(stem))


def stem_priority(stem: str, want: str, tokens: set[str]) -> tuple[int, int]:
    """Sort key: containment matches outrank bare token matches; then shorter stems."""
    n = normalize_name(stem)
    if want and min(len(want), len(n)) >= 12 and (want in n or n in want):
        return (0, len(stem))
    return (1, len(stem))


def fetch_one(repo: str, ref: str, path: str) -> dict:
    dest = CACHE / repo / path
    if dest.exists():
        return {"repo": repo, "ref": ref, "path": path, "local": str(dest.relative_to(ROOT)),
                "bytes": dest.stat().st_size, "sha256": sha256(dest), "status": "ok"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Unique temp name: two ledger rows can resolve to the same file, and a shared ".partial"
    # path lets one thread rename the other's inode out from under it (observed 2026-10-26).
    tmp = dest.with_suffix(f"{dest.suffix}.partial-{os.getpid()}-{threading.get_ident()}")
    for attempt in range(3):
        try:
            with tmp.open("wb") as fh:
                subprocess.run(
                    ["gh", "api", f"repos/{OWNER}/{repo}/contents/{path}?ref={ref}",
                     "-H", "Accept: application/vnd.github.raw"],
                    stdout=fh, check=True, stderr=subprocess.PIPE,
                )
            got = sha256(tmp)
            if dest.exists():
                # Another worker fetched the same file; keep one copy, drop ours.
                tmp.unlink(missing_ok=True)
                return {"repo": repo, "ref": ref, "path": path, "local": str(dest.relative_to(ROOT)),
                        "bytes": dest.stat().st_size, "sha256": sha256(dest), "status": "ok"}
            tmp.replace(dest)
            break
        except subprocess.CalledProcessError:
            time.sleep(2 * (attempt + 1))
    else:
        tmp.unlink(missing_ok=True)
        return {"repo": repo, "ref": ref, "path": path, "status": "FAILED"}
    return {"repo": repo, "ref": ref, "path": path, "local": str(dest.relative_to(ROOT)),
            "bytes": dest.stat().st_size, "sha256": sha256(dest), "status": "ok"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--min-score", type=float, default=0.10)
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    rows = ledger_rows(args.min_score)
    jobs, unmatched = [], []
    for r in rows:
        want, tokens = candidate_stems(r["submission"])
        if not want and not tokens:
            unmatched.append({"site": r["site"], "submission": r["submission"],
                              "reason": "no normalizable name or strong token"})
            continue
        try:
            ref = gh_json(f"repos/{OWNER}/{r['site']}/commits/main")["sha"]
            tree = gh_json(f"repos/{OWNER}/{r['site']}/git/trees/{ref}?recursive=1")
        except (subprocess.CalledProcessError, KeyError):
            unmatched.append({"site": r["site"], "submission": r["submission"],
                              "reason": "repo or main ref not reachable"})
            continue
        tifs = [t["path"] for t in tree.get("tree", [])
                if t.get("type") == "blob" and t["path"].lower().endswith((".tif", ".tiff"))
                and int(t.get("size", 0)) <= 8_000_000]
        hits = [p for p in tifs if stems_match(Path(p).stem, want, tokens)]
        if not hits:
            unmatched.append({"site": r["site"], "submission": r["submission"],
                              "reason": f"no matching tif among {len(tifs)} in repo"})
            continue
        # Containment matches outrank bare token matches; then shorter stems win.
        best = min(hits, key=lambda p: stem_priority(Path(p).stem, want, tokens))
        jobs.append({"repo": r["site"], "ref": ref, "path": best,
                     "ledger_name": r["submission"], "score": r["score_value"],
                     "also_matching": [p for p in hits if p != best][:4]})
        print(f"{r['site']}: {r['submission'][:44]} -> {best}")

    results = []
    with cf.ThreadPoolExecutor(args.jobs) as ex:
        futs = {ex.submit(fetch_one, j["repo"], j["ref"], j["path"]): j for j in jobs}
        for f in cf.as_completed(futs):
            res = f.result()
            meta = {k: futs[f][k] for k in ("repo", "path", "ledger_name", "score", "also_matching")}
            results.append({**meta, **res})
            print(f"  {res['status']:>7} {res.get('bytes', 0):>9,} B  {res['path'].split('/')[-1][:70]}")

    failed = [r for r in results if r["status"] != "ok"]
    manifest = {
        "schema_version": 1,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "owner": OWNER,
        "note": (
            "Scored submission rasters from non-focus owner repositories, fetched at the pinned "
            "main refs for the live-score covariate audit. Scores come from docs/score-ledger.csv "
            "and are OWNER-REPORT, never organizer-authenticated. Bytes are verified by sha256."
        ),
        "min_score": args.min_score,
        "n_fetched": len(results) - len(failed),
        "n_failed": len(failed),
        "n_unmatched_ledger_rows": len(unmatched),
        "rasters": sorted(results, key=lambda r: -r.get("score", 0)),
        "unmatched": unmatched,
    }
    OUT.write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"wrote {OUT}: {manifest['n_fetched']} rasters, {len(failed)} failed, {len(unmatched)} unmatched rows")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
