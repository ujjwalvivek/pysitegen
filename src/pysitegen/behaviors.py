from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .components import Asset, Node


PACKAGE_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Behavior:
    assets: list[Asset] = field(default_factory=list)
    scripts: list[str] = field(default_factory=list)
    module_scripts: list[str] = field(default_factory=list)
    head: list[Node] = field(default_factory=list)


def spa() -> Behavior:
    static_dir = PACKAGE_ROOT / "static"
    return Behavior(
        assets=[Asset(static_dir / "pysitegen-spa.js", "assets/pysitegen-spa.js")],
        scripts=["assets/pysitegen-spa.js"],
    )
