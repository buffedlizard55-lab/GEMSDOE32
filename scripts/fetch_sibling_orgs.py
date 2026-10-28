#!/usr/bin/env python3
"""Fetch and SHA-256-pin all submission-like GeoTIFFs from sibling-organization repositories.

Covers all 21 sibling repositories named in the 2026-10-27 prompt:
  - kanlerxz87-cyber: KANLERGEMSDOE1, KANLERGEMSDOE2, KANLERGEMSDOE3
  - eugboogieman123-ops: EUGGEMSDOE1, EUGGEMSDOE2, EUGGEMSDOE3
  - wingbangboozle1-lang: WBGGEMSDOE1, WBGGEMSDOE2, WBGGEMSDOE3
  - ginnymcfiner23-ux: GINNYGEMSDOE1, GINNYGEMSDOE2, GINNYGEMSDOE3
  - karagemop466-tech: GEMSDOEkarage1, GEMSDOEkarage2, GEMSDOEkarage3
  - apartanish22-droid: ApartGEMSDOE1, ApartGEMSDOE2, ApartGEMSDOE3
  - sassnarep3-star: GEMSDOESASS1, GEMSDOESASS2, GEMSDOESASS3

Writes cached bytes under `.cache/sibling_orgs/<owner>/<repo>/<path>` (git-ignored) and
records SHA-256 + commit ref metadata in both `.cache/sibling_orgs/manifest.json` and
`registry/sibling_orgs_manifest.json`.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIBLING_REPOS: tuple[tuple[str, str], ...] = (
    ("kanlerxz87-cyber", "KANLERGEMSDOE1"),
    ("kanlerxz87-cyber", "KANLERGEMSDOE2"),
    ("kanlerxz87-cyber", "KANLERGEMSDOE3"),
    ("eugboogieman123-ops", "EUGGEMSDOE1"),
    ("eugboogieman123-ops", "EUGGEMSDOE2"),
    ("eugboogieman123-ops", "EUGGEMSDOE3"),
    ("wingbangboozle1-lang", "WBGGEMSDOE1"),
    ("wingbangboozle1-lang", "WBGGEMSDOE2"),
    ("wingbangboozle1-lang", "WBGGEMSDOE3"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE1"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE2"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE3"),
    ("karagemop466-tech", "GEMSDOEkarage1"),
    ("karagemop466-tech", "GEMSDOEkarage2"),
    ("karagemop466-tech", "GEMSDOEkarage3"),
    ("apartanish22-droid", "ApartGEMSDOE1"),
    ("apartanish22-droid", "ApartGEMSDOE2"),
    ("apartanish22-droid", "ApartGEMSDOE3"),
    ("sassnarep3-star", "GEMSDOESASS1"),
    ("sassnarep3-star", "GEMSDOESASS2"),
    ("sassnarep3-star", "GEMSDOESASS3"),
)
MAX_BYTES = 8_000_000


def gh_json(path: str) -> dict | None:
    res = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return json.loads(res.stdout)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def list_sibling(owner: str, repo: str) -> tuple[str | None, list[dict]]:
    c = gh_json(f"repos/{owner}/{repo}/commits/main") or gh_json(f"repos/{owner}/{repo}/commits/master")
    if not c:
        return None, []
    ref = c["sha"]
    tree = gh_json(f"repos/{owner}/{repo}/git/trees/{ref}?recursive=1")
    if not tree or "tree" not in tree:
        return ref, []
    files = [
        t for t in tree["tree"]
        if t["type"] == "blob"
        and t["path"].lower().endswith((".tif", ".tiff"))
        and not t["path"].startswith("data/")
        and int(t.get("size", 0)) <= MAX_BYTES
    ]
    return ref, files


def fetch_blob(owner: str, repo: str, ref: str, path: str, size: int, cache_dir: Path) -> dict:
    dest = cache_dir / owner / repo / path
    if not (dest.exists() and dest.stat().st_size == size):
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".partial")
        for attempt in range(3):
            try:
                with tmp.open("wb") as fh:
                    subprocess.run(
                        [
                            "gh", "api",
                            f"repos/{owner}/{repo}/contents/{path}?ref={ref}",
                            "-H", "Accept: application/vnd.github.raw",
                        ],
                        stdout=fh,
                        stderr=subprocess.PIPE,
                        check=True,
                    )
                tmp.replace(dest)
                break
            except subprocess.CalledProcessError:
                tmp.unlink(missing_ok=True)
                time.sleep(1.5 * (attempt + 1))
        else:
            return {"owner": owner, "repo": repo, "ref": ref, "path": path, "status": "FAILED"}
    return {
        "owner": owner,
        "repo": repo,
        "ref": ref,
        "path": path,
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "local": str(dest.relative_to(ROOT)),
        "status": "ok",
    }


def main() -> int:
    cache_dir = ROOT / ".cache" / "sibling_orgs"
    cache_dir.mkdir(parents=True, exist_ok=True)
    refs: dict[str, dict] = {}
    jobs = []
    for owner, repo in SIBLING_REPOS:
        ref, files = list_sibling(owner, repo)
        refs[f"{owner}/{repo}"] = {"ref": ref, "n_tif_blobs": len(files)}
        print(f"  {owner}/{repo:18s} ref={(ref or 'NONE')[:10]}  tifs={len(files)}", flush=True)
        if ref:
            for f in files:
                jobs.append((owner, repo, ref, f["path"], int(f["size"])))

    results = []
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(fetch_blob, *j, cache_dir) for j in jobs]
        for fut in cf.as_completed(futs):
            results.append(fut.result())

    results.sort(key=lambda r: (r["owner"], r["repo"], r["path"]))
    ok_rows = [r for r in results if r["status"] == "ok"]
    failed = [r for r in results if r["status"] != "ok"]

    # Legacy list format in `.cache/sibling_orgs/manifest.json` for backward compatibility
    (cache_dir / "manifest.json").write_text(json.dumps(ok_rows, indent=2) + "\n")
    reg_doc = {
        "schema_version": 1,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "n_repos_checked": len(SIBLING_REPOS),
        "n_rasters_ok": len(ok_rows),
        "n_failed": len(failed),
        "repos": refs,
        "rasters": ok_rows,
    }
    (ROOT / "registry" / "sibling_orgs_manifest.json").write_text(json.dumps(reg_doc, indent=2) + "\n")
    print(f"Fetched {len(ok_rows)} sibling-org GeoTIFFs across {len(SIBLING_REPOS)} repos ({len(failed)} failed)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
