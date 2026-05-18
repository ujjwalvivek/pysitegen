from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .components import Asset


PACKAGE_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Theme:
    assets: list[Asset]
    stylesheets: list[str]


def default_dark() -> Theme:
    static_dir = PACKAGE_ROOT / "static"
    return Theme(
        assets=[Asset(static_dir / "pysitegen.css", "assets/pysitegen.css")],
        stylesheets=["assets/pysitegen.css"],
    )
