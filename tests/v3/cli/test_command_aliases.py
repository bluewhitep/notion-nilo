# File: tests/v3/cli/test_command_aliases.py
# Format: UTF-8
# =============================
# File Description:
# Validate explicit short aliases for the public CLI command tree.
# TAG: test, cli, aliases
# =============================

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pytest
from typer.testing import CliRunner
from typer.main import get_command

from nilo.cli import app
from nilo.cli.aliases import CLI_ALIASES, CommandPath

runner = CliRunner()

SCOPED_PUBLIC_PATHS: set[CommandPath] = {
    ("init",),
    ("version",),
    ("config",),
    ("pwd",),
    ("auth",),
    ("auth", "validate"),
    ("auth", "whoami"),
    ("page",),
    ("page", "attach"),
    ("page", "status"),
    ("page", "refresh"),
    ("page", "detach"),
    ("page", "blocks"),
    ("page", "retrieve"),
    ("page", "create"),
    ("page", "update"),
    ("page", "trash"),
    ("block",),
    ("block", "children"),
    ("block", "append"),
    ("block", "insert-after"),
    ("block", "update"),
    ("block", "trash"),
    ("database",),
    ("database", "attach"),
    ("database", "status"),
    ("database", "refresh"),
    ("database", "detach"),
    ("database", "retrieve"),
    ("database", "sources"),
    ("database", "create"),
    ("database", "update"),
    ("database", "rename"),
    ("database", "query"),
    ("database", "page"),
    ("database", "page", "create"),
    ("database", "property"),
    ("database", "property", "rename"),
    ("data-source",),
    ("data-source", "retrieve"),
    ("data-source", "query"),
    ("data-source", "create"),
    ("data-source", "update"),
    ("data-source", "templates"),
    ("data-source", "property"),
    ("data-source", "property", "rename"),
    ("data-source", "page"),
    ("data-source", "page", "create"),
    ("user",),
    ("user", "me"),
    ("user", "list"),
    ("user", "retrieve"),
    ("comment",),
    ("comment", "list"),
    ("comment", "create"),
    ("comment", "reply"),
    ("view",),
    ("view", "retrieve"),
    ("view", "list"),
    ("view", "query"),
    ("view", "create"),
    ("view", "update"),
    ("file-upload",),
    ("file-upload", "retrieve"),
    ("file-upload", "list"),
    ("file-upload", "create"),
    ("file-upload", "send"),
    ("file-upload", "complete"),
    ("search",),
    ("search", "query"),
    ("custom-emoji",),
    ("custom-emoji", "list"),
    ("custom-emoji", "retrieve"),
    ("raw-api",),
    ("raw-api", "operations"),
    ("raw-api", "invoke"),
    ("server",),
    ("server", "run"),
    ("server", "stdio"),
    ("server", "status"),
    ("server", "stop"),
    ("server", "remove"),
    ("server", "logs"),
}


# --------------------------------
# Function Description:
# Converts every canonical segment with a registered prefix into its alias.
# Inputs/Outputs:
# Input canonical command path; returns the fully aliased invocation path.
# Usage:
# fully_aliased(("database", "page", "create"))
# --------------------------------
def fully_aliased(path: CommandPath) -> list[str]:
    return [CLI_ALIASES.get(path[:index], path[index - 1]) for index in range(1, len(path) + 1)]


# --------------------------------
# Function Description:
# Enumerates the visible canonical CLI command tree using Click's public group contract.
# Inputs/Outputs:
# No input; returns every visible root, group, and leaf command path.
# Usage:
# visible_command_paths()
# --------------------------------
def visible_command_paths() -> set[CommandPath]:
    paths: set[CommandPath] = set()

    def walk(group: Any, parent: CommandPath = ()) -> None:
        for name, command in group.commands.items():
            if command.hidden:
                continue
            path = (*parent, name)
            paths.add(path)
            if hasattr(command, "commands"):
                walk(command, path)

    root = get_command(app)
    assert hasattr(root, "commands")
    walk(root)
    return paths


# --------------------------------
# Function Description:
# Verifies the scoped public command inventory has an explicit alias entry.
# Inputs/Outputs:
# No input; assertion-only test.
# Usage:
# pytest tests/v3/cli/test_command_aliases.py
# --------------------------------
def test_scoped_public_commands_have_explicit_aliases() -> None:
    assert visible_command_paths() == SCOPED_PUBLIC_PATHS
    assert SCOPED_PUBLIC_PATHS == set(CLI_ALIASES)


# --------------------------------
# Function Description:
# Verifies aliases are ASCII letters, at most six characters, and unique among siblings.
# Inputs/Outputs:
# No input; assertion-only test.
# Usage:
# pytest tests/v3/cli/test_command_aliases.py
# --------------------------------
def test_aliases_are_short_letters_and_unique_per_parent() -> None:
    aliases_by_parent: dict[CommandPath, list[str]] = defaultdict(list)
    canonical_by_parent: dict[CommandPath, set[str]] = defaultdict(set)
    for path in CLI_ALIASES:
        canonical_by_parent[path[:-1]].add(path[-1])
    for path, alias in CLI_ALIASES.items():
        assert alias.isascii() and alias.isalpha()
        assert len(alias) <= 6
        assert alias not in canonical_by_parent[path[:-1]]
        aliases_by_parent[path[:-1]].append(alias)
    for aliases in aliases_by_parent.values():
        assert len(aliases) == len(set(aliases))


# --------------------------------
# Function Description:
# Verifies each alias resolves under its canonical parent without running business operations.
# Inputs/Outputs:
# Input parametrized command path; invokes help and asserts successful parsing.
# Usage:
# pytest tests/v3/cli/test_command_aliases.py
# --------------------------------
@pytest.mark.parametrize("path", sorted(CLI_ALIASES))
def test_each_alias_resolves_under_canonical_parent(path: CommandPath) -> None:
    result = runner.invoke(app, [*path[:-1], CLI_ALIASES[path], "--help"])
    assert result.exit_code == 0, f"alias failed for {' '.join(path)}: {result.stdout}"


# --------------------------------
# Function Description:
# Verifies complete command paths remain parseable when every registered segment uses its alias.
# Inputs/Outputs:
# Input parametrized command path; invokes help and asserts successful parsing.
# Usage:
# pytest tests/v3/cli/test_command_aliases.py
# --------------------------------
@pytest.mark.parametrize("path", sorted(CLI_ALIASES))
def test_fully_aliased_command_paths_resolve(path: CommandPath) -> None:
    result = runner.invoke(app, [*fully_aliased(path), "--help"])
    assert result.exit_code == 0, f"fully aliased path failed for {' '.join(path)}: {result.stdout}"
