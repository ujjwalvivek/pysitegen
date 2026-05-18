from __future__ import annotations

from pathlib import Path

from .components import Asset


def asset(source: str | Path, target: str) -> Asset:
    return Asset(Path(source), target)
