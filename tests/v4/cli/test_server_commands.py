import json
from pathlib import Path

from typer.testing import CliRunner

from nilo.cli import app
from nilo.cli.commands import server as server_commands
from nilo.runtime.server_process import ServerRuntimeState


runner = CliRunner()


def test_server_stdio_uses_runtime_without_cli_to_mcp_import(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        server_commands,
        "run_foreground_stdio_server",
        lambda: calls.append("stdio"),
    )

    result = runner.invoke(app, ["server", "stdio"])

    assert result.exit_code == 0
    assert calls == ["stdio"]
    source = Path(server_commands.__file__).read_text(encoding="utf-8")
    assert "nilo.mcp_server" not in source


def test_server_run_passes_host_port_and_prints_json(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_start_background_server(**kwargs):
        captured.update(kwargs)
        return ServerRuntimeState(
            pid=123,
            host=str(kwargs["host"]),
            port=int(kwargs["port"]),
            transport=str(kwargs["transport"]),
            url="http://127.0.0.1:8123/mcp",
            state_file="/tmp/server.state.json",
            log_file="/tmp/server.log",
            started_at="2026-06-09T00:00:00Z",
            command=["python", "-m", "nilo.mcp_server.runner"],
        )

    monkeypatch.setattr(server_commands, "start_background_server", fake_start_background_server)

    result = runner.invoke(app, ["server", "run", "--host", "127.0.0.1", "--port", "8123", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["server"]["pid"] == 123
    assert payload["server"]["url"] == "http://127.0.0.1:8123/mcp"
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8123


def test_server_status_stop_remove_and_logs_use_manager(monkeypatch) -> None:
    monkeypatch.setattr(
        server_commands,
        "get_server_status",
        lambda: {
            "running": True,
            "status": "running",
            "pid": 123,
            "transport": "streamable-http",
            "url": "http://127.0.0.1:8000/mcp",
            "state_file": "/tmp/server.state.json",
            "log_file": "/tmp/server.log",
        },
    )
    monkeypatch.setattr(
        server_commands,
        "stop_background_server",
        lambda timeout_seconds, force: {
            "running": False,
            "status": "stopped",
            "pid": 123,
            "state_file": "/tmp/server.state.json",
        },
    )
    monkeypatch.setattr(
        server_commands,
        "remove_server_state",
        lambda keep_log, force: {
            "running": False,
            "status": "removed",
            "removed": ["/tmp/server.state.json", "/tmp/server.log"],
        },
    )
    monkeypatch.setattr(
        server_commands,
        "read_server_logs",
        lambda tail: {"log_file": "/tmp/server.log", "tail": tail, "lines": ["a", "b"], "text": "a\nb"},
    )

    status = runner.invoke(app, ["serve", "status", "--json"])
    stop = runner.invoke(app, ["server", "stop", "--json"])
    remove = runner.invoke(app, ["server", "remove", "--json"])
    logs = runner.invoke(app, ["server", "logs", "--tail", "2", "--json"])

    assert status.exit_code == 0
    assert json.loads(status.stdout)["server"]["running"] is True
    assert stop.exit_code == 0
    assert json.loads(stop.stdout)["server"]["status"] == "stopped"
    assert remove.exit_code == 0
    assert json.loads(remove.stdout)["server"]["status"] == "removed"
    assert logs.exit_code == 0
    assert json.loads(logs.stdout)["logs"]["lines"] == ["a", "b"]


def test_old_mcp_serve_command_is_removed_from_public_cli() -> None:
    root = runner.invoke(app, ["--help"])
    old_mcp = runner.invoke(app, ["mcp", "serve", "--help"])
    old_run = runner.invoke(app, ["run", "--help"])

    assert root.exit_code == 0
    assert " mcp " not in root.stdout
    assert "Run the legacy FastAPI REST server" not in root.stdout
    assert old_mcp.exit_code != 0
    assert old_run.exit_code != 0
