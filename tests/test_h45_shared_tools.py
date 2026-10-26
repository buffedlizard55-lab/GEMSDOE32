"""Regression tests for the shared-tool changes made in the H45-1 session (no competition data needed)."""

import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems32 import spcp  # noqa: E402


def test_sarpu_propensity_keyword_is_backward_compatible():
    sig = inspect.signature(spcp.fit_predict_sarpu_spcp)
    assert "return_propensity" in sig.parameters
    assert sig.parameters["return_propensity"].default is False


def test_registry_manifest_entries_have_pins():
    man = json.loads((ROOT / "registry" / "focus_registry_manifest.json").read_text())
    ok = [r for r in man["rasters"] if r.get("status") == "ok"]
    assert len(ok) == man["n_rasters"] == len(man["rasters"]) == 304
    for r in ok:
        assert len(r["sha256"]) == 64 and r["ref"] and r["local"].startswith(".cache/registry/")


def test_restore_pinned_registry_module_imports():
    import restore_pinned_registry as rpr  # noqa: E402

    assert callable(rpr._fetch) and callable(rpr.main)
