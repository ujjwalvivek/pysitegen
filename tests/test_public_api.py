from __future__ import annotations

import pysitegen


def test_root_package_exports_authoring_api_only() -> None:
    assert "page" in pysitegen.__all__
    assert "tag" in pysitegen.__all__
    assert "asset" in pysitegen.__all__
    assert "default_dark" in pysitegen.__all__
    assert "spa" in pysitegen.__all__
    assert "markdown_file" in pysitegen.__all__

    assert "build" not in pysitegen.__all__
    assert "load_config" not in pysitegen.__all__
    assert "serve" not in pysitegen.__all__
    assert "render_site" not in pysitegen.__all__
    assert "SiteConfig" not in pysitegen.__all__
    assert "RawHtml" not in pysitegen.__all__
