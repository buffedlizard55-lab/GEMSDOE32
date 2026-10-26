#!/usr/bin/env python3
"""Restore the duplicate-gate registry at its PINNED commits, fail-closed on any SHA-256 mismatch.

Why this exists: `scripts/run_h44_spcp.py::scan_full_registry` silently skips any manifest entry
whose local file is missing (`if p.exists()`), so an un-restored cache makes the "289/304 rasters
checked" claim false while the run still reports PASS. This script materialises every
`status == "ok"` entry of `registry/focus_registry_manifest.json` at its pinned `ref`, verifies the
bytes against the pinned `sha256` and `bytes`, and exits non-zero on any mismatch or missing file.

It does NOT re-enumerate the focus repositories (that is `scripts/fetch_focus_registry.py`, which
re-pins the manifest to the current `main`). Pins are never changed here.

Usage:  python scripts/restore_pinned_registry.py [--jobs 6]
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "focus_registry_manifest.json"


def _fetch(entry: dict) -> dict:
    dest = ROOT / entry["local"]
    if dest.exists() and dest.stat().st_size == entry["bytes"]:
        digest = hashlib.sha256(dest.read_bytes()).hexdigest()
        if digest == entry["sha256"]:
            return {"local": entry["local"], "status": "present"}
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    api = f"repos/buffedlizard55-lab/{entry['repo']}/contents/{entry['path']}?ref={entry['ref']}"
    try:
        with tmp.open("wb") as fh:
            subprocess.run(
                ["gh", "api", api, "-H", "Accept: application/vnd.github.raw"],
                stdout=fh,
                check=True,
                stderr=subprocess.PIPE,
            )
        data = tmp.read_bytes()
    except subprocess.CalledProcessError as exc:
        tmp.unlink(missing_ok=True)
        return {"local": entry["local"], "status": "fetch-error", "error": exc.stderr.decode(errors="replace")[:200]}
    finally:
        tmp.unlink(missing_ok=True)
    digest = hashlib.sha256(data).hexdigest()
    if digest != entry["sha256"] or len(data) != entry["bytes"]:
        return {"local": entry["local"], "status": "MISMATCH", "got_sha256": digest, "got_bytes": len(data)}
    dest.write_bytes(data)
    return {"local": entry["local"], "status": "restored"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    man = json.loads(MANIFEST.read_text())
    entries = [r for r in man["rasters"] if r.get("status") == "ok"]
    results: list[dict] = []
    with cf.ThreadPoolExecutor(max_workers=a.jobs) as pool:
        for res in pool.map(_fetch, entries):
            results.append(res)
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(json.dumps({"manifest_ok_entries": len(entries), "counts": counts}, indent=1))
    bad = [r for r in results if r["status"] not in {"present", "restored"}]
    for r in bad[:20]:
        print("FAIL", json.dumps(r), file=sys.stderr)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
