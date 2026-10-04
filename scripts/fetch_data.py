#!/usr/bin/env python3
"""Fetch and hash-verify the hash-pinned competition mirrors (GitHub API only)."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "registry" / "data_manifest.json").read_text())


def gh_raw(repo, ref, path, dest):
    dest = Path(dest)
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() == _sha(dest):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("wb") as fh:
        subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}",
                        "-H", "Accept: application/vnd.github.raw"], stdout=fh, check=True)
    return dest


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default="/tmp/gems32/data")
    a = ap.parse_args()
    dest = Path(a.dest)
    ok, bad = [], []
    for f in MANIFEST["files"]:
        target = dest / f["dest"]
        if "parts" in f:
            chunks = []
            for i, p in enumerate(f["parts"]):
                chunks.append(gh_raw(f["repo"], f["ref"], p, dest / f"part-{i:03d}"))
            with target.open("wb") as out:
                for c in chunks:
                    out.write(c.read_bytes())
        else:
            gh_raw(f["repo"], f["ref"], f["path"], target)
        digest = _sha(target)
        (ok if digest == f["sha256"] else bad).append((f["id"], digest))
        print(("OK   " if digest == f["sha256"] else "FAIL ") + f"{f['id']:26s} {digest[:16]}...")
    print(json.dumps({"verified": len(ok), "failed": len(bad), "dest": str(dest)}))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
