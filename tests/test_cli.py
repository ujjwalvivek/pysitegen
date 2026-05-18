from __future__ import annotations

from pathlib import Path

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
