from typer.testing import CliRunner

from notion_mcp.cli import app


runner = CliRunner()


def test_root_help_describes_direct_commands() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "init" in result.stdout
    assert "Initialize project-local .notion_mcp context" in result.stdout
    assert "status" in result.stdout
    assert "Show global configuration and capability status" in result.stdout
    assert "server" in result.stdout
    assert "Manage the local MCP server" in result.stdout
    assert "set-token" not in result.stdout
    assert "set-user" not in result.stdout
    assert "Show legacy global configuration" not in result.stdout
    assert "Run the legacy FastAPI REST server" not in result.stdout


def test_project_and_config_help_describe_dynamic_subcommands() -> None:
    project_result = runner.invoke(app, ["project", "--help"])
    config_global_result = runner.invoke(app, ["config", "global", "--help"])
    config_local_result = runner.invoke(app, ["config", "local", "--help"])

    assert project_result.exit_code == 0
    assert "Create .notion_mcp project context" in project_result.stdout
    assert "Show project-local context status" in project_result.stdout
    assert "Print resolved project root" in project_result.stdout

    assert config_global_result.exit_code == 0
    assert "Set a global configuration value" in config_global_result.stdout
    assert "Get a global configuration value" in config_global_result.stdout
    assert "Unset a nullable global configuration value" in config_global_result.stdout
    assert "List global configuration values" in config_global_result.stdout

    assert config_local_result.exit_code == 0
    assert "Create .notion_mcp project context" in config_local_result.stdout
    assert "Show project-local context status" in config_local_result.stdout
    assert "Print resolved project root" in config_local_result.stdout
