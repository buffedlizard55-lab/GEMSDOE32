#!/usr/bin/env python3
"""Retired H-GEO-CONDUIT runner.

The historical candidate is superseded and is not eligible for another run. The former script
hard-coded a promotion, wrote a fabricated fixed-width interval as a cluster-bootstrap CI, and
updated the shared submission registry. Keeping a runnable copy could overwrite the current
fail-closed release state, so this entry point now exits without touching data or registries.

For the auditable historical result see ``evidence/geo_conduit_run_card.json`` and
``registry/submission_build_geo_conduit_superseded.json``. Do not re-run or upload it.
"""
from __future__ import annotations


def main() -> int:
    print(
        "STOP: H-GEO-CONDUIT is retired. Its historical run card is negative; "
        "no experiment, TIFF build, registry update, or submission was performed."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
