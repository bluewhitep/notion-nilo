from __future__ import annotations

import json
import os
import shutil
import subprocess
import tomllib
from pathlib import Path


def test_uv_isolated_install_exposes_cli_help(tmp_path: Path) -> None:
    """The local package must expose the nilo CLI in an isolated uv run."""
    uv = shutil.which("uv")
    assert uv is not None, "uv is required for isolated install validation"

    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "pyproject.toml").open("rb") as pyproject_file:
        expected_version = tomllib.load(pyproject_file)["project"]["version"]
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
            "nilo",
            "--help",
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    combined_output = result.stdout + result.stderr
    assert "nilo" in combined_output or "Notion MCP" in combined_output
    assert "init" in combined_output
    assert "server" in combined_output

    version_result = subprocess.run(
        [
            uv,
            "run",
            "--no-project",
            "--with",
            str(repo_root),
            "nilo",
            "version",
            "--json",
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        timeout=120,
        check=False,
    )

    assert version_result.returncode == 0, version_result.stderr
    version_payload = json.loads(version_result.stdout)
    assert version_payload["mcp_version"] == expected_version
