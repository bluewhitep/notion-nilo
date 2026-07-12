# File: tests/v2/cli/test_json_usage_errors.py
# Format: UTF-8
# =============================
# File Description:
# Validate stable JSON envelopes for CLI parsing and payload errors.
# TAG: test, cli, json, errors, function-calling
# =============================

from __future__ import annotations

import json
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from nilo.cli import app
from nilo.cli.errors import JsonErrorGroup
from nilo.cli.formatting import exit_with_error
from nilo.core.errors import CoreError

runner = CliRunner()


# --------------------------------
# Function Description:
# Parses and validates the common one-line JSON usage-error envelope.
# Inputs/Outputs:
# Input CLI result; returns decoded payload after structural assertions.
# Usage:
# payload = assert_json_error(result)
# --------------------------------
def assert_json_error(result: object) -> dict[str, object]:
    exit_code = getattr(result, "exit_code")
    stdout = getattr(result, "stdout")
    assert exit_code != 0
    assert stdout.endswith("\n")
    assert len(stdout.splitlines()) == 1
    payload = json.loads(stdout)
    assert payload["ok"] is False
    assert set(payload["error"]) == {"type", "code", "message", "details"}
    assert payload["error"]["type"] == "CliUsageError"
    assert payload["error"]["details"]["exit_code"] == exit_code
    return payload


# --------------------------------
# Function Description:
# Verifies --json selects structured errors when placed at root, group, or leaf level.
# Inputs/Outputs:
# Input parametrized CLI arguments; assertion-only test.
# Usage:
# pytest tests/v2/cli/test_json_usage_errors.py
# --------------------------------
@pytest.mark.parametrize(
    ("args", "expected_code"),
    [
        (["--json", "page", "update"], "cli_unknown_option"),
        (["page", "--json", "update"], "cli_unknown_option"),
        (["page", "update", "--json"], "cli_missing_parameter"),
    ],
)
def test_json_flag_at_any_level_selects_json_usage_errors(args: list[str], expected_code: str) -> None:
    payload = assert_json_error(runner.invoke(app, args))
    assert payload["error"]["code"] == expected_code


# --------------------------------
# Function Description:
# Verifies invalid JSON payloads use the stable invalid-parameter envelope through aliases.
# Inputs/Outputs:
# No input; assertion-only test that performs a dry-run parse and no Notion call.
# Usage:
# pytest tests/v2/cli/test_json_usage_errors.py
# --------------------------------
def test_invalid_json_payload_is_a_structured_error_through_aliases() -> None:
    result = runner.invoke(
        app,
        ["blk", "add", "block-1", "--payload", "not-json", "--dry-run", "--json"],
    )
    payload = assert_json_error(result)
    assert payload["error"]["code"] == "cli_invalid_parameter"
    assert payload["error"]["message"] == "Invalid value: payload must be valid JSON"


# --------------------------------
# Function Description:
# Verifies non-JSON invocations retain the existing human-readable Rich usage output.
# Inputs/Outputs:
# No input; assertion-only test.
# Usage:
# pytest tests/v2/cli/test_json_usage_errors.py
# --------------------------------
def test_non_json_usage_error_keeps_human_output() -> None:
    result = runner.invoke(app, ["page", "update"])
    assert result.exit_code == 2
    assert result.stdout == ""
    assert result.stderr.startswith("Usage:")
    assert "Missing argument 'PAGE_ID'." in result.stderr
    with pytest.raises(json.JSONDecodeError):
        json.loads(result.stderr)


# --------------------------------
# Function Description:
# Verifies an already-rendered Core JSON error preserves typer.Exit(1) without a traceback.
# Inputs/Outputs:
# No input; invokes an isolated callback and asserts the existing Core error envelope and exit code.
# Usage:
# pytest tests/v2/cli/test_json_usage_errors.py
# --------------------------------
def test_json_core_error_exit_preserves_code_without_traceback() -> None:
    error_app = typer.Typer(cls=JsonErrorGroup)

    # Keeps the isolated Typer application in group mode so its custom root class owns error handling.
    @error_app.callback()
    def root() -> None:
        return None

    # Emits the normal Core error envelope before using the existing typer.Exit path.
    @error_app.command(name="fail")
    def fail(json_output: bool = typer.Option(False, "--json")) -> None:
        exit_with_error(CoreError("expected failure", code="expected_failure"), json_output=json_output)

    result = runner.invoke(error_app, ["fail", "--json"])

    assert result.exit_code == 1
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) == 1
    assert "Traceback" not in result.stdout
    assert json.loads(result.stdout) == {
        "ok": False,
        "error": {
            "type": "CoreError",
            "code": "expected_failure",
            "message": "expected failure",
            "details": {},
        },
    }


# --------------------------------
# Function Description:
# Verifies an unhandled Core configuration failure is normalized by the root JSON contract.
# Inputs/Outputs:
# Uses malformed global JSON; asserts one structured line and no traceback.
# Usage:
# pytest tests/v2/cli/test_json_usage_errors.py -k malformed_global
# --------------------------------
def test_malformed_global_config_is_a_structured_json_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text('{"default_transport":"sse"}', encoding="utf-8")
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(config_file))

    result = runner.invoke(app, ["config", "--global", "--show", "--json"])

    assert result.exit_code == 1
    assert result.stderr == ""
    assert len(result.stdout.splitlines()) == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "ConfigValidationError"
    assert payload["error"]["code"] == "config_validation_failed"
    assert "Traceback" not in result.stdout
