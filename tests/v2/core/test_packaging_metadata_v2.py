from __future__ import annotations

import os
import shutil
import subprocess
import tomllib
from pathlib import Path


def test_uv_installed_package_imports_outside_repo_cwd(tmp_path: Path) -> None:
    """Installed package import must not rely on the repository root on sys.path."""
    uv = shutil.which("uv")
    assert uv is not None, "uv is required for packaging validation"

    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "pyproject.toml").open("rb") as pyproject_file:
        expected_version = tomllib.load(pyproject_file)["project"]["version"]
    run_cwd = tmp_path / "outside-repo"
    run_cwd.mkdir()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")

    result = subprocess.run(
        [
            uv,
            "run",
            "--no-project",
            "--with",
            str(repo_root),
            "python",
            "-c",
            "import nilo; print(nilo.__version__)",
        ],
        cwd=run_cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == expected_version
