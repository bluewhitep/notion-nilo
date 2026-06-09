from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def test_uv_isolated_install_exposes_cli_help(tmp_path: Path) -> None:
    """The local package must expose the notion-mcp CLI in an isolated uv run."""
    uv = shutil.which("uv")
    assert uv is not None, "uv is required for isolated install validation"

    repo_root = Path(__file__).resolve().parents[3]
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
            "notion-mcp",
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
    assert "notion-mcp" in combined_output or "Notion MCP" in combined_output
    assert "init" in combined_output
    assert "server" in combined_output
