# File: src/nilo/cli/aliases.py
# Format: UTF-8
# =============================
# File Description:
# Explicit short aliases and public registration helpers for the CLI command tree.
# TAG: cli, aliases, commands
# =============================

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

import typer

CommandPath = tuple[str, ...]

CLI_ALIASES: dict[CommandPath, str] = {
    ("init",): "ini",
    ("version",): "ver",
    ("config",): "cfg",
    ("pwd",): "cwd",
    ("auth",): "au",
    ("auth", "validate"): "check",
    ("auth", "whoami"): "who",
    ("page",): "pg",
    ("page", "attach"): "att",
    ("page", "status"): "stat",
    ("page", "refresh"): "sync",
    ("page", "detach"): "det",
    ("page", "blocks"): "blks",
    ("page", "retrieve"): "get",
    ("page", "create"): "new",
    ("page", "update"): "upd",
    ("page", "trash"): "del",
    ("block",): "blk",
    ("block", "children"): "kids",
    ("block", "append"): "add",
    ("block", "insert-after"): "after",
    ("block", "update"): "upd",
    ("block", "trash"): "del",
    ("database",): "db",
    ("database", "attach"): "att",
    ("database", "status"): "stat",
    ("database", "refresh"): "sync",
    ("database", "detach"): "det",
    ("database", "retrieve"): "get",
    ("database", "sources"): "srcs",
    ("database", "create"): "new",
    ("database", "update"): "upd",
    ("database", "rename"): "ren",
    ("database", "query"): "qry",
    ("database", "page"): "pg",
    ("database", "page", "create"): "new",
    ("database", "property"): "prop",
    ("database", "property", "rename"): "ren",
    ("data-source",): "ds",
    ("data-source", "retrieve"): "get",
    ("data-source", "query"): "qry",
    ("data-source", "create"): "new",
    ("data-source", "update"): "upd",
    ("data-source", "templates"): "tmpl",
    ("data-source", "property"): "prop",
    ("data-source", "property", "rename"): "ren",
    ("data-source", "page"): "pg",
    ("data-source", "page", "create"): "new",
    ("user",): "usr",
    ("user", "me"): "self",
    ("user", "list"): "ls",
    ("user", "retrieve"): "get",
    ("comment",): "cmt",
    ("comment", "list"): "ls",
    ("comment", "create"): "new",
    ("comment", "reply"): "ans",
    ("view",): "vw",
    ("view", "retrieve"): "get",
    ("view", "list"): "ls",
    ("view", "query"): "qry",
    ("view", "create"): "new",
    ("view", "update"): "upd",
    ("file-upload",): "fu",
    ("file-upload", "retrieve"): "get",
    ("file-upload", "list"): "ls",
    ("file-upload", "create"): "new",
    ("file-upload", "send"): "push",
    ("file-upload", "complete"): "done",
    ("search",): "srch",
    ("search", "query"): "qry",
    ("custom-emoji",): "emoji",
    ("custom-emoji", "list"): "ls",
    ("custom-emoji", "retrieve"): "get",
    ("raw-api",): "raw",
    ("raw-api", "operations"): "ops",
    ("raw-api", "invoke"): "call",
    ("server",): "srv",
    ("server", "run"): "start",
    ("server", "stdio"): "pipe",
    ("server", "status"): "stat",
    ("server", "stop"): "halt",
    ("server", "remove"): "rm",
    ("server", "logs"): "tail",
}


# --------------------------------
# Function Description:
# Validates that every configured alias is short, ASCII alphabetic, and unique among siblings.
# Inputs/Outputs:
# Input path-to-alias mapping; raises ValueError for an invalid or ambiguous alias.
# Usage:
# validate_aliases(CLI_ALIASES)
# --------------------------------
def validate_aliases(aliases: dict[CommandPath, str]) -> None:
    canonical_by_parent: dict[CommandPath, set[str]] = defaultdict(set)
    alias_by_parent: dict[CommandPath, set[str]] = defaultdict(set)
    for path in aliases:
        if not path:
            raise ValueError("CLI alias paths cannot be empty")
        canonical_by_parent[path[:-1]].add(path[-1])
    for path, alias in aliases.items():
        parent = path[:-1]
        if not alias.isascii() or not alias.isalpha() or len(alias) > 6:
            raise ValueError(f"Invalid CLI alias for {' '.join(path)}: {alias}")
        if alias in canonical_by_parent[parent] or alias in alias_by_parent[parent]:
            raise ValueError(f"Ambiguous CLI alias under {' '.join(parent) or '<root>'}: {alias}")
        alias_by_parent[parent].add(alias)


# --------------------------------
# Function Description:
# Returns the configured short alias for a canonical command path.
# Inputs/Outputs:
# Input one or more canonical command segments; returns the registered alias string.
# Usage:
# alias_for("page", "retrieve")
# --------------------------------
def alias_for(*path: str) -> str:
    return CLI_ALIASES[tuple(path)]


# --------------------------------
# Function Description:
# Builds a hidden Typer command decorator for a canonical command's explicit alias.
# Inputs/Outputs:
# Input Typer app, canonical path, and public command settings; returns a callback decorator.
# Usage:
# @command_alias(app, "page", "retrieve")
# --------------------------------
def command_alias(
    app: typer.Typer,
    *path: str,
    **command_settings: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    return app.command(name=alias_for(*path), hidden=True, **command_settings)


# --------------------------------
# Function Description:
# Registers a hidden short alias for an existing Typer command group.
# Inputs/Outputs:
# Input parent/child apps and canonical path; mutates the parent command registry.
# Usage:
# add_group_alias(root_app, page_app, "page")
# --------------------------------
def add_group_alias(parent: typer.Typer, child: typer.Typer, *path: str) -> None:
    parent.add_typer(child, name=alias_for(*path), hidden=True)


validate_aliases(CLI_ALIASES)
