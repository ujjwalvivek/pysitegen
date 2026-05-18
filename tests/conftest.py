from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"


def write_file(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def run_pysitegen(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(SRC_ROOT)
        if not existing_pythonpath
        else os.pathsep.join([str(SRC_ROOT), existing_pythonpath])
    )

    return subprocess.run(
        [sys.executable, "-m", "pysitegen.builder", *args],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, result.stderr


def assert_failure(result: subprocess.CompletedProcess[str], message: str) -> None:
    assert result.returncode != 0
    assert "pysitegen: error:" in result.stderr
    assert message in result.stderr
