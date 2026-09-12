from __future__ import annotations

from pathlib import Path

import scripts.verify_manuscript_consistency as vmc


def test_check_zip_builder_reports_bad_zip(tmp_path: Path, monkeypatch) -> None:
    builder = tmp_path / "scripts/build_submission_zip.py"
    builder.parent.mkdir(parents=True, exist_ok=True)
    builder.write_text(
        '"""builder stub for test."""\n',
        encoding="utf-8",
    )

    zpath = tmp_path / "PGAA_supplementary_code.zip"
    zpath.write_bytes(b"not a zip archive")

    monkeypatch.setattr(vmc, "ROOT", tmp_path)

    errors = vmc.check_zip_builder()

    assert any("Bad zip archive" in err for err in errors)
