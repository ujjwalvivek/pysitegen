from __future__ import annotations

from pathlib import Path

from conftest import assert_success, run_pysitegen, write_file

from pysitegen import visual_canvas, visual_scene


def test_visual_scene_normalizes_layer_specs() -> None:
    scene = visual_scene(
        "background",
        ("grid", {"spacing": 120, "opacity": 0.25}),
    )

    assert scene == [
        {"primitive": "background", "options": {}},
        {"primitive": "grid", "options": {"spacing": 120, "opacity": 0.25}},
    ]


def test_visual_canvas_renders_scene_data() -> None:
    node = visual_canvas(
        visual_scene(("grid", {"spacing": 80})),
        id="hero-canvas",
        fps=30,
        class_="hero-visual",
    )

    html = node.render()

    assert html.startswith('<canvas id="hero-canvas"')
    assert "data-pysitegen-canvas" in html
    assert "data-fps=\"12\"" in html
    assert (
        "data-scene=\"[{&quot;primitive&quot;:&quot;grid&quot;,"
        "&quot;options&quot;:{&quot;spacing&quot;:80}}]\""
    ) in html
    assert "class=\"hero-visual\"" in html


def test_canvas_background_loads_cdn_runtime_only_when_used(tmp_path: Path) -> None:
    write_file(
        tmp_path / "index.py",
        """
from pysitegen import h1, page

def build():
    return page(h1("Plain"), title="Plain")
""",
    )

    plain_result = run_pysitegen(tmp_path, "build")

    assert_success(plain_result)
    assert not (tmp_path / "public" / "assets" / "pysitegen-canvas.js").exists()
    plain_html = (tmp_path / "public" / "index.html").read_text(encoding="utf-8")
    assert "cdn.ujjwalvivek.com/scripts/substrate" not in plain_html

    write_file(
        tmp_path / "index.py",
        """
from pysitegen import canvas_background, h1, page, visual_canvas, visual_scene

def build():
    scene = visual_scene(
        "background",
        ("grid", {"spacing": 96}),
        ("nodes", {"count": 16}),
    )
    return page(
        visual_canvas(scene, id="hero-canvas", fps=0, class_="hero-visual"),
        h1("Visual"),
        title="Visual",
        behaviors=[canvas_background()],
    )
""",
    )

    visual_result = run_pysitegen(tmp_path, "build")

    assert_success(visual_result)
    html = (tmp_path / "public" / "index.html").read_text(encoding="utf-8")

    assert not (tmp_path / "public" / "assets" / "pysitegen-canvas.js").exists()
    assert "data-pysitegen-canvas" in html
    assert "data-fps=\"0\"" in html
    assert "import { compose, primitives } from" in html
    assert "https://cdn.ujjwalvivek.com/scripts/substrate/latest/main.js" in html
