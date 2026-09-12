from pathlib import Path

import pytest

from pgaa.core import data_root as data_root_module
from pgaa.core.data_root import ENV_VAR, LEGACY_USB_ROOT, data_root


def test_data_root_falls_back_to_legacy_volume(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_VAR, raising=False)
    assert data_root() == LEGACY_USB_ROOT
    assert data_root("a/b") == LEGACY_USB_ROOT / "a/b"


def test_data_root_honors_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_VAR, "/mnt/copy")
    assert data_root() == Path("/mnt/copy")
    assert data_root("pgaa_cross_platform/v2") == Path("/mnt/copy/pgaa_cross_platform/v2")


def test_registries_use_the_overridden_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_VAR, "/mnt/copy")
    import importlib

    from pgaa.core import expansion_v2, expansion_v3

    importlib.reload(expansion_v2)
    importlib.reload(expansion_v3)
    try:
        assert expansion_v2.DEFAULT_USB_ROOT == Path("/mnt/copy/pgaa_cross_platform/v2")
        assert expansion_v3.DEFAULT_USB_ROOT == Path("/mnt/copy/pgaa_cross_platform")
        assert all(
            str(spec.path).startswith("/mnt/copy/")
            for spec in expansion_v2.frozen_ready_specs()
        )
    finally:
        monkeypatch.delenv(ENV_VAR, raising=False)
        importlib.reload(expansion_v2)
        importlib.reload(expansion_v3)
    assert data_root_module.ENV_VAR == ENV_VAR
