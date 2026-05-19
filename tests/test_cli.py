from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pysitegen.builder as builder

from conftest import assert_failure, assert_success, run_pysitegen, write_file


def test_compile_succeeds_and_removes_pycache(tmp_path: Path) -> None:
    write_file(
        tmp_path / "index.py",
        """
from pysitegen import h1, page

def build():
    return page(h1("Compile"), title="Compile")
""",
    )

    result = run_pysitegen(tmp_path, "compile")

    assert_success(result)
    assert "Compiled" in result.stdout
    assert not list(tmp_path.rglob("__pycache__"))


def test_version_works(tmp_path: Path) -> None:
    result = run_pysitegen(tmp_path, "--version")

    assert_success(result)
    assert "0.1.0" in result.stdout


def test_serve_help_mentions_no_reload(tmp_path: Path) -> None:
    result = run_pysitegen(tmp_path, "serve", "--help")

    assert_success(result)
    assert "--no-reload" in result.stdout


def test_live_reload_script_injects_before_body() -> None:
    html = "<!doctype html><html><body><h1>Hello</h1></body></html>"

    inject_live_reload = cast(Any, getattr(builder, "inject_live_reload"))

    result = inject_live_reload(html)

    assert 'new EventSource("/__pysitegen/reload")' in result
    assert result.index("EventSource") < result.index("</body>")


def test_watch_snapshot_ignores_public_output(tmp_path: Path) -> None:
    write_file(tmp_path / "index.py", "def build():\n    pass\n")
    write_file(tmp_path / "assets" / "index.css", "body {}\n")
    write_file(tmp_path / "public" / "index.html", "<h1>Generated</h1>\n")

    snapshot_project = cast(Any, getattr(builder, "snapshot_project"))

    snapshot = snapshot_project(tmp_path, tmp_path / "public")

    assert tmp_path / "index.py" in snapshot
    assert tmp_path / "assets" / "index.css" in snapshot
    assert tmp_path / "public" / "index.html" not in snapshot


def test_missing_site_py_and_index_py_gives_useful_error(tmp_path: Path) -> None:
    result = run_pysitegen(tmp_path, "build")

    assert_failure(result, "No site.py or index.py found")
    assert "pysitegen init ." in result.stderr


def test_malformed_site_gives_useful_error(tmp_path: Path) -> None:
    write_file(tmp_path / "site.py", "SITE = []\n")

    result = run_pysitegen(tmp_path, "build")

    assert_failure(result, "must define SITE as a dict or build()")


def test_missing_page_file_gives_useful_error(tmp_path: Path) -> None:
    write_file(
        tmp_path / "site.py",
        """
SITE = {"pages": [("pages/missing.py", "")]}
""",
    )

    result = run_pysitegen(tmp_path, "build")

    assert_failure(result, "Configured page does not exist")
    assert "pages/missing.py" in result.stderr


def test_page_without_build_gives_useful_error(tmp_path: Path) -> None:
    write_file(
        tmp_path / "site.py",
        """
SITE = {"pages": [("pages/empty.py", "")]}
""",
    )
    write_file(tmp_path / "pages" / "empty.py", "TITLE = 'No build here'\n")

    result = run_pysitegen(tmp_path, "build")

    assert_failure(result, "must define build()")


def test_build_returning_non_document_gives_useful_error(tmp_path: Path) -> None:
    write_file(
        tmp_path / "index.py",
        """
def build():
    return "not a document"
""",
    )

    result = run_pysitegen(tmp_path, "build")

    assert_failure(result, "build() must return pysitegen.Document")
