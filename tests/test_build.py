from __future__ import annotations

from pathlib import Path

from pysitegen.builder import build, load_config

from conftest import assert_success, run_pysitegen, write_file


def write_index(project: Path, body: str) -> Path:
    return write_file(project / "index.py", body)


def test_index_py_builds_by_default_when_site_py_is_absent(tmp_path: Path) -> None:
    write_index(
        tmp_path,
        """
from pysitegen import h1, page

def build():
    return page(h1("Index default"), title="Home")
""",
    )

    result = run_pysitegen(tmp_path, "build")

    assert_success(result)
    html = (tmp_path / "public" / "index.html").read_text(encoding="utf-8")
    assert "Index default" in html


def test_site_static_files_copy_directly_to_public(tmp_path: Path) -> None:
    write_index(
        tmp_path,
        """
from pysitegen import h1, page

def build():
    return page(h1("Static"), title="Static")
""",
    )
    write_file(tmp_path / "static" / "robots.txt", "User-agent: *\nAllow: /\n")
    write_file(tmp_path / "static" / "favicon.png", "not really a png")

    result = run_pysitegen(tmp_path, "build")

    assert_success(result)
    assert (tmp_path / "public" / "robots.txt").read_text(encoding="utf-8") == (
        "User-agent: *\nAllow: /\n"
    )
    assert (tmp_path / "public" / "favicon.png").read_text(encoding="utf-8") == (
        "not really a png"
    )


def test_authored_assets_copy_to_public_assets(tmp_path: Path) -> None:
    write_file(tmp_path / "assets" / "index.css", "body { color: red; }\n")
    write_index(
        tmp_path,
        """
from pathlib import Path

from pysitegen import asset, h1, page

ROOT = Path(__file__).resolve().parent

def build():
    return page(
        h1("Assets"),
        title="Assets",
        assets=[asset(ROOT / "assets" / "index.css", "assets/index.css")],
        stylesheets=["assets/index.css"],
    )
""",
    )

    result = run_pysitegen(tmp_path, "build")

    assert_success(result)
    assert (tmp_path / "public" / "assets" / "index.css").read_text(
        encoding="utf-8"
    ) == "body { color: red; }\n"


def test_default_dark_copies_bundled_css_only_when_used(tmp_path: Path) -> None:
    write_index(
        tmp_path,
        """
from pysitegen import h1, page

def build():
    return page(h1("Plain"), title="Plain")
""",
    )

    plain_result = run_pysitegen(tmp_path, "build")

    assert_success(plain_result)
    assert not (tmp_path / "public" / "assets" / "pysitegen.css").exists()

    write_index(
        tmp_path,
        """
from pysitegen import default_dark, h1, page

def build():
    return page(h1("Themed"), title="Themed", theme=default_dark())
""",
    )

    themed_result = run_pysitegen(tmp_path, "build")

    assert_success(themed_result)
    css_path = tmp_path / "public" / "assets" / "pysitegen.css"
    assert css_path.exists()
    assert "<link rel=\"stylesheet\" href=\"assets/pysitegen.css\">" in (
        tmp_path / "public" / "index.html"
    ).read_text(encoding="utf-8")


def test_spa_copies_bundled_js_only_when_used(tmp_path: Path) -> None:
    write_index(
        tmp_path,
        """
from pysitegen import h1, page

def build():
    return page(h1("Plain"), title="Plain")
""",
    )

    plain_result = run_pysitegen(tmp_path, "build")

    assert_success(plain_result)
    assert not (tmp_path / "public" / "assets" / "pysitegen-spa.js").exists()

    write_index(
        tmp_path,
        """
from pysitegen import h1, page, spa

def build():
    return page(h1("SPA"), title="SPA", behaviors=[spa()])
""",
    )

    spa_result = run_pysitegen(tmp_path, "build")

    assert_success(spa_result)
    js_path = tmp_path / "public" / "assets" / "pysitegen-spa.js"
    assert js_path.exists()
    assert "<script src=\"assets/pysitegen-spa.js\" defer></script>" in (
        tmp_path / "public" / "index.html"
    ).read_text(encoding="utf-8")


def test_site_py_can_define_multiple_pages(tmp_path: Path) -> None:
    write_file(
        tmp_path / "site.py",
        """
SITE = {
    "pages": [
        ("pages/home.py", ""),
        ("pages/about.py", "about"),
    ],
}
""",
    )
    write_file(
        tmp_path / "pages" / "home.py",
        """
from pysitegen import h1, page

def build():
    return page(h1("Home page"), title="Home")
""",
    )
    write_file(
        tmp_path / "pages" / "about.py",
        """
from pysitegen import h1, page

def build():
    return page(h1("About page"), title="About")
""",
    )

    result = run_pysitegen(tmp_path, "build")

    assert_success(result)
    assert "Home page" in (tmp_path / "public" / "index.html").read_text(
        encoding="utf-8"
    )
    assert "About page" in (tmp_path / "public" / "about" / "index.html").read_text(
        encoding="utf-8"
    )


def test_public_directory_is_cleaned_before_rebuild(tmp_path: Path) -> None:
    write_index(
        tmp_path,
        """
from pysitegen import h1, page

def build():
    return page(h1("Clean rebuild"), title="Clean")
""",
    )
    stale_file = tmp_path / "public" / "stale.txt"
    write_file(stale_file, "old")

    config = load_config(tmp_path / "index.py")
    build(config)

    assert (tmp_path / "public" / "index.html").exists()
    assert not stale_file.exists()
