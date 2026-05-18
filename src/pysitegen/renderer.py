from __future__ import annotations

import shutil
from pathlib import Path

from .components import Document


def render_site(document: Document, out_dir: str | Path) -> Path:
    target_dir = Path(out_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    html_path = target_dir / "index.html"
    html_path.write_text(document.render(), encoding="utf-8")

    for asset in document.assets:
        asset_target = target_dir / asset.target
        asset_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset.source, asset_target)

    return html_path
