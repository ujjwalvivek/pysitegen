from __future__ import annotations

from pathlib import Path

from conftest import assert_failure, assert_success, run_pysitegen, write_file


def test_init_creates_starter_project_files(tmp_path: Path) -> None:
    project = tmp_path / "my-site"

    result = run_pysitegen(tmp_path, "init", "my-site")

    assert_success(result)
    expected_files = [
        "index.py",
        "assets/index.css",
        "content/docs/.gitkeep",
        "static/favicon.png",
        "static/robots.txt",
        ".gitignore",
        "README.md",
    ]
    for relative_path in expected_files:
        assert (project / relative_path).exists(), relative_path


def test_init_refuses_to_overwrite_existing_files(tmp_path: Path) -> None:
    project = tmp_path / "my-site"
    write_file(project / "index.py", "# existing\n")

    result = run_pysitegen(tmp_path, "init", "my-site")

    assert_failure(result, "Refusing to overwrite existing file")
    assert (project / "index.py").read_text(encoding="utf-8") == "# existing\n"
