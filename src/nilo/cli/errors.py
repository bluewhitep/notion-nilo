# File: src/nilo/cli/errors.py
# Format: UTF-8
# =============================
# File Description:
# Stable JSON rendering for Click and Typer command-line usage errors.
# TAG: cli, errors, json, function-calling
# =============================

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from typing import Any, Protocol, cast

import click
import typer
from typer.core import TyperGroup

from nilo.core.errors import CoreError


class UsageErrorLike(Protocol):
    exit_code: int

    def format_message(self) -> str: ...


# --------------------------------
# Function Description:
# Detects whether a CLI invocation requested structured JSON output at any command level.
# Inputs/Outputs:
# Input raw CLI arguments; returns True when an exact --json flag is present.
# Usage:
# wants_json(["page", "retrieve", "--json"])
# --------------------------------
def wants_json(args: Sequence[str]) -> bool:
    return "--json" in args


# --------------------------------
# Function Description:
# Maps Click usage exception types to stable public CLI error codes.
# Inputs/Outputs:
# Input ClickException; returns a stable snake_case error code.
# Usage:
# usage_error_code(typer.BadParameter("invalid value"))
# --------------------------------
def usage_error_code(error: UsageErrorLike) -> str:
    if isinstance(error, click.MissingParameter):
        return "cli_missing_parameter"
    if isinstance(error, typer.BadParameter):
        if type(error) is typer.BadParameter:
            return "cli_invalid_parameter"
        return "cli_missing_parameter"
    if isinstance(error, click.BadParameter):
        return "cli_invalid_parameter"
    if isinstance(error, click.NoSuchOption) or hasattr(error, "option_name"):
        return "cli_unknown_option"
    return "cli_usage_error"


# --------------------------------
# Function Description:
# Builds the stable single-line JSON envelope for a Click usage error.
# Inputs/Outputs:
# Input ClickException; returns a JSON-serializable error dictionary.
# Usage:
# usage_error_payload(typer.BadParameter("invalid value"))
# --------------------------------
def usage_error_payload(error: UsageErrorLike) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {
            "type": "CliUsageError",
            "code": usage_error_code(error),
            "message": error.format_message(),
            "details": {"exit_code": error.exit_code},
        },
    }


# --------------------------------
# Function Description:
# Emits a Click usage error as one compact JSON line on standard output.
# Inputs/Outputs:
# Input ClickException; writes one line and returns None.
# Usage:
# echo_usage_error(typer.BadParameter("invalid value"))
# --------------------------------
def echo_usage_error(error: UsageErrorLike) -> None:
    typer.echo(json.dumps(usage_error_payload(error), ensure_ascii=False, separators=(",", ":")))


# --------------------------------
# Function Description:
# Emits an unhandled Core error as one compact JSON line for Function Calling.
# Inputs/Outputs:
# Input CoreError; writes the shared error envelope and returns None.
# Usage:
# echo_core_error(CoreError("failed"))
# --------------------------------
def echo_core_error(error: CoreError) -> None:
    payload = {"ok": False, "error": error.to_dict()}
    typer.echo(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


# --------------------------------
# Function Description:
# Recognizes official Click exceptions and Typer-compatible usage errors without private imports.
# Inputs/Outputs:
# Input arbitrary exception; returns True only for objects exposing the Click usage-error contract.
# Usage:
# is_usage_error(typer.BadParameter("invalid value"))
# --------------------------------
def is_usage_error(error: BaseException) -> bool:
    if isinstance(error, (click.ClickException, typer.BadParameter)):
        return True
    return isinstance(getattr(error, "exit_code", None), int) and callable(
        getattr(error, "format_message", None)
    )


class JsonErrorGroup(TyperGroup):
    # --------------------------------
    # Function Description:
    # Runs Typer normally, but converts propagated usage errors to JSON when --json is present.
    # Inputs/Outputs:
    # Input standard Click main arguments; returns callback results or exits with the original error code.
    # Usage:
    # typer.Typer(cls=JsonErrorGroup)
    # --------------------------------
    def main(
        self,
        args: Sequence[str] | None = None,
        prog_name: str | None = None,
        complete_var: str | None = None,
        standalone_mode: bool = True,
        windows_expand_args: bool = True,
        **extra: Any,
    ) -> Any:
        resolved_args = list(sys.argv[1:] if args is None else args)
        if not wants_json(resolved_args):
            return super().main(
                args=resolved_args,
                prog_name=prog_name,
                complete_var=complete_var,
                standalone_mode=standalone_mode,
                windows_expand_args=windows_expand_args,
                **extra,
            )
        try:
            result = super().main(
                args=resolved_args,
                prog_name=prog_name,
                complete_var=complete_var,
                standalone_mode=False,
                windows_expand_args=windows_expand_args,
                **extra,
            )
        except Exception as error:
            if isinstance(error, CoreError):
                echo_core_error(error)
                if standalone_mode:
                    raise SystemExit(1) from error
                raise
            if not is_usage_error(error):
                raise
            usage_error = cast(UsageErrorLike, error)
            echo_usage_error(usage_error)
            if standalone_mode:
                raise SystemExit(usage_error.exit_code) from error
            raise
        if standalone_mode and isinstance(result, int) and result != 0:
            raise SystemExit(result)
        return result
