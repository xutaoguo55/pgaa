"""Deterministic figure saving.

matplotlib's PDF backend writes the wall-clock time into ``/CreationDate`` by
default, so rendering the same data twice yields different bytes. That makes
byte-level comparisons between the archived software zip and the working tree
report spurious drift, and it defeats any reproducibility check that hashes
rendered figures. Stripping the field keeps PDF output a pure function of the
plotted data.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# Passing None for a metadata key removes it from the emitted PDF.
DETERMINISTIC_PDF_METADATA: dict[str, Any] = {"CreationDate": None}


def save_figure(fig: Any, path: str | Path, **kwargs: Any) -> Path:
    """Save ``fig`` to ``path``, making PDF output reproducible."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".pdf":
        metadata = dict(kwargs.pop("metadata", None) or {})
        metadata.update(DETERMINISTIC_PDF_METADATA)
        kwargs["metadata"] = metadata
    fig.savefig(path, **kwargs)
    return path
