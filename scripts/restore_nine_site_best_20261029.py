#!/usr/bin/env python3
"""Restore the on-disk-missing nine-site best rasters at their pinned refs (2026-10-29).

Why: the nine-site uniqueness and holdout audits need the exact bytes of each site's best
submission. Five of them were absent from the cache (GEMSDOE28/30/31/33/36). They are fetched
from the public GitHub repositories at the commit pinned in registry/focus_registry_manifest.json
and accepted only if the SHA-256 of the fetched bytes equals the pinned digest. Nothing is
relaxed: a mismatch aborts with exit code 2.

Uses `gh api` (GitHub only; no DrivenData access). Writes into .cache/registry/ (git-ignored).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "focus_registry_manifest.json"

# (repo, path inside repo) for the nine-site best files that are not on disk.
TARGETS = [
    ("GEMSDOE28", "docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif"),
    ("GEMSDOE30", "docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif"),
    ("GEMSDOE31", "docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif"),
    ("GEMSDOE33", "docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif"),
    ("GEMSDOE36", "docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif"),
]


NINE = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
        "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    all_focus = "--all-focus" in sys.argv[1:]
    rows = json.loads(MANIFEST.read_text())["rasters"]
    targets = TARGETS
    if all_focus:
        # Every pinned focus-repository raster (204 rows, nine sites): the uniqueness registry.
        targets = [(r["repo"], r["path"]) for r in rows if r["repo"] in NINE]
    status = []
    for repo, path in targets:
        row = next((r for r in rows if r["repo"] == repo and r["path"] == path), None)
        if row is None:
            print(f"MISSING-IN-MANIFEST {repo} {path}", file=sys.stderr)
            return 2
        dest = ROOT / row["local"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not (dest.exists() and sha256(dest) == row["sha256"]):
            tmp = dest.with_suffix(dest.suffix + ".partial")
            with tmp.open("wb") as out:
                subprocess.run(
                    ["gh", "api", f"repos/buffedlizard55-lab/{repo}/contents/{path}?ref={row['ref']}",
                     "-H", "Accept: application/vnd.github.raw"],
                    stdout=out, stderr=subprocess.PIPE, check=True,
                )
            got = sha256(tmp)
            if got != row["sha256"]:
                tmp.unlink(missing_ok=True)
                print(f"SHA-MISMATCH {repo} {path}: got {got} want {row['sha256']}", file=sys.stderr)
                return 2
            tmp.replace(dest)
        status.append({"repo": repo, "path": path, "ref": row["ref"], "sha256": row["sha256"],
                       "bytes": dest.stat().st_size, "local": str(dest.relative_to(ROOT))})
        if not all_focus:
            print(f"OK {repo} {dest.stat().st_size:>9} {row['sha256'][:16]} {path}")
    out = ROOT / ".cache" / "registry" / ("nine_site_all_restore_20261029.json" if all_focus else "nine_site_best_restore_20261029.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(status, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
