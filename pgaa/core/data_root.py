"""Resolve the root of the frozen external platform data.

The expansion registries were built against an external volume that is not part
of the submission archive. The root is therefore configurable: set
``PGAA_DATA_ROOT`` to a local copy of that tree, or pass an explicit
``root=``/``usb_root=`` argument to the registry functions.

``LEGACY_USB_ROOT`` is kept only as a last-resort fallback so existing local
workflows keep working. It is not expected to exist for a reader of the
submission archive; see ``docs/DATA_ROOT_PROVENANCE.md`` for how to obtain the
upstream data.
"""
from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "PGAA_DATA_ROOT"
LEGACY_USB_ROOT = Path("/Volumes/MOVESPEED")


def data_root(subpath: str = "") -> Path:
    """Return the external-data root, honoring the ``PGAA_DATA_ROOT`` override."""
    override = os.environ.get(ENV_VAR)
    root = Path(override) if override else LEGACY_USB_ROOT
    return root / subpath if subpath else root
