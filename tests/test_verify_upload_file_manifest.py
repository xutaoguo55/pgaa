from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


HEADER = "file\trole\tupload\taction\tnotes\n"

MANIFEST_BODY = (
    "MANUSCRIPT.pdf\tmain_manuscript\tyes\tupload\tok\n"
    "SUPPLEMENTARY.pdf\tsupplementary_material\tyes\tupload\tok\n"
    "PGAA_supplementary_code.zip\tsupplementary_software\tyes\tupload\tok\n"
    "COVER_LETTER_BIOINFORMATICS.md\tcover_letter\tyes\tcopy_to_portal\tok\n"
)


def _setup(tmp_path: Path, monkeypatch, body: str):
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_upload_file_manifest.py"
    mod = _load_module("verify_upload_file_manifest_under_test", script)

    manifest = tmp_path / "UPLOAD_FILE_MANIFEST.tsv"
    manifest.write_text(HEADER + body, encoding="utf-8")
    for name in ["MANUSCRIPT.pdf", "SUPPLEMENTARY.pdf", "COVER_LETTER_BIOINFORMATICS.md"]:
        (tmp_path / name).write_text("ok\n", encoding="utf-8")
    supp_zip = tmp_path / "PGAA_supplementary_code.zip"

    monkeypatch.setattr(mod, "ROOT", tmp_path)
    monkeypatch.setattr(mod, "MANIFEST", manifest)
    monkeypatch.setattr(mod, "SUPP_CODE", supp_zip)
    return mod, supp_zip


def test_reports_bad_supplementary_zip(tmp_path: Path, monkeypatch, capsys) -> None:
    mod, supp_zip = _setup(tmp_path, monkeypatch, MANIFEST_BODY)
    supp_zip.write_bytes(b"not a zip archive")

    with pytest.raises(SystemExit) as excinfo:
        mod.main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "UPLOAD FILE MANIFEST CHECK FAILED" in captured.out
    assert "Bad supplementary software zip: PGAA_supplementary_code.zip" in captured.out


def test_reports_missing_required_upload_file(tmp_path: Path, monkeypatch, capsys) -> None:
    body = MANIFEST_BODY.replace(
        "COVER_LETTER_BIOINFORMATICS.md\tcover_letter\tyes\tcopy_to_portal\tok\n", ""
    )
    mod, supp_zip = _setup(tmp_path, monkeypatch, body)
    supp_zip.write_bytes(b"not a zip archive")

    with pytest.raises(SystemExit) as excinfo:
        mod.main()

    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert (
        "Required Bioinformatics upload file missing from manifest: COVER_LETTER_BIOINFORMATICS.md"
        in captured.out
    )


def test_passes_on_consistent_manifest(tmp_path: Path, monkeypatch, capsys) -> None:
    mod, supp_zip = _setup(tmp_path, monkeypatch, MANIFEST_BODY)
    supp_zip.write_bytes(b"not a zip archive")

    # A readable zip with no forbidden entries is what a clean package looks like.
    import zipfile

    with zipfile.ZipFile(supp_zip, "w") as zf:
        zf.writestr("pgaa_supplementary/README.md", "ok\n")

    mod.main()
    captured = capsys.readouterr()
    assert "UPLOAD FILE MANIFEST CHECK PASSED" in captured.out
