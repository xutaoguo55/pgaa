from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest


BUILDER_SOURCE = """
ROOT_FILES = ["README.md"]
ROOT_DIRS = ["pgaa"]
SCRIPT_SUFFIXES = {".py"}
FORBIDDEN_SUBSTRINGS = ["mmd_psm"]
"""


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_zip(path: Path, members: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, text in members.items():
            zf.writestr(f"pgaa_supplementary/{name}", text)


@pytest.fixture()
def gate(tmp_path: Path, monkeypatch):
    """A miniature release tree with a zip that agrees with it."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "build_submission_zip.py").write_text(
        BUILDER_SOURCE, encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("See `pgaa/ok.py`.\n", encoding="utf-8")
    (tmp_path / "pgaa").mkdir()
    (tmp_path / "pgaa" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pgaa" / "ok.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "pgaa" / "mmd_psm.py").write_text("VALUE = 2\n", encoding="utf-8")

    members = {
        "README.md": "See `pgaa/ok.py`.\n",
        "pgaa/__init__.py": "",
        "pgaa/ok.py": "VALUE = 1\n",
        "scripts/build_submission_zip.py": BUILDER_SOURCE,
    }
    zpath = tmp_path / "PGAA_supplementary_code.zip"
    _write_zip(zpath, members)

    module = _load_module(
        "verify_manuscript_consistency_gate_under_test",
        Path(__file__).resolve().parents[1] / "scripts" / "verify_manuscript_consistency.py",
    )
    monkeypatch.setattr(module, "ROOT", tmp_path)
    return module, tmp_path, zpath, members


def test_passes_when_zip_matches_the_documented_tree(gate) -> None:
    module, _, _, _ = gate
    assert module.check_zip_is_self_contained() == []


def test_flags_a_file_the_packager_rules_admit_but_the_zip_lacks(gate) -> None:
    module, root, _, _ = gate
    (root / "pgaa" / "late_addition.py").write_text("VALUE = 3\n", encoding="utf-8")

    errors = module.check_zip_is_self_contained()

    assert any("missing a file its own rules admit: pgaa/late_addition.py" in e for e in errors)


def test_flags_a_documented_path_the_exclusion_rules_drop(gate) -> None:
    module, root, _, _ = gate
    (root / "README.md").write_text(
        "See `pgaa/ok.py` and `pgaa/mmd_psm.py`.\n", encoding="utf-8"
    )

    errors = module.check_zip_is_self_contained()

    assert any("dropped by the zip exclusion rules: pgaa/mmd_psm.py" in e for e in errors)


def test_flags_a_packaged_module_importing_an_excluded_module(gate) -> None:
    module, _, zpath, members = gate
    members = dict(members)
    members["pgaa/ok.py"] = "from pgaa.mmd_psm import VALUE\n"
    _write_zip(zpath, members)

    errors = module.check_zip_is_self_contained()

    assert any(
        "imports a file the zip excludes: pgaa/ok.py -> pgaa.mmd_psm" in e for e in errors
    )
