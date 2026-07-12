import json
from pathlib import Path

import pytest

from nilo.mcp_server import process_manager as compatibility_process_manager
from nilo.runtime import server_process as process_manager


class FakeProcess:
    pid = 4321
    returncode = None

    def poll(self):
        return None


class FakeCompletedProcess:
    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode


def test_mcp_process_manager_reexports_runtime_contract() -> None:
    assert compatibility_process_manager.ServerRuntimeState is process_manager.ServerRuntimeState
    assert compatibility_process_manager.start_background_server is process_manager.start_background_server
    assert compatibility_process_manager.run_foreground_stdio_server is process_manager.run_foreground_stdio_server


def test_foreground_stdio_server_inherits_process_streams(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return FakeCompletedProcess()

    monkeypatch.setattr(process_manager.subprocess, "run", fake_run)

    process_manager.run_foreground_stdio_server()

    assert "nilo.mcp_server.runner" in captured["command"]
    assert captured["command"][captured["command"].index("--transport") + 1] == "stdio"
    assert captured["kwargs"] == {"check": False}


def test_foreground_stdio_server_wraps_nonzero_exit(monkeypatch) -> None:
    monkeypatch.setattr(
        process_manager.subprocess,
        "run",
        lambda command, **kwargs: FakeCompletedProcess(returncode=3),
    )

    with pytest.raises(process_manager.ServerProcessError, match="exited with code 3"):
        process_manager.run_foreground_stdio_server()


def test_start_background_server_writes_state(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return FakeProcess()

    monkeypatch.setenv("NOTION_MCP_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr(process_manager.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(process_manager, "is_pid_running", lambda pid: False)
    monkeypatch.setattr(process_manager.time, "sleep", lambda seconds: None)

    state = process_manager.start_background_server(host="127.0.0.1", port=8123)

    state_file = tmp_path / "server.state.json"
    raw = json.loads(state_file.read_text(encoding="utf-8"))
    assert state.pid == 4321
    assert raw["url"] == "http://127.0.0.1:8123/mcp"
    assert raw["transport"] == "streamable-http"
    assert "nilo.mcp_server.runner" in captured["command"]
    assert captured["kwargs"]["start_new_session"] is True


def test_stop_background_server_marks_state_stopped(monkeypatch, tmp_path: Path) -> None:
    killed: list[tuple[int, int]] = []
    state = process_manager.ServerRuntimeState(
        pid=4321,
        host="127.0.0.1",
        port=8123,
        transport="streamable-http",
        url="http://127.0.0.1:8123/mcp",
        state_file=str(tmp_path / "server.state.json"),
        log_file=str(tmp_path / "server.log"),
        started_at="2026-06-09T00:00:00Z",
        command=["python", "-m", "nilo.mcp_server.runner"],
    )
    process_manager.write_json_atomic(tmp_path / "server.state.json", state.to_dict())
    monkeypatch.setenv("NOTION_MCP_RUNTIME_DIR", str(tmp_path))
    calls = {"count": 0}

    def fake_is_pid_running(pid):
        calls["count"] += 1
        return calls["count"] == 1

    monkeypatch.setattr(process_manager, "is_pid_running", fake_is_pid_running)
    monkeypatch.setattr(process_manager, "wait_for_exit", lambda pid, timeout_seconds: True)
    monkeypatch.setattr(process_manager.os, "kill", lambda pid, sig: killed.append((pid, sig)))

    status = process_manager.stop_background_server()

    assert killed
    assert status["running"] is False
    stored = json.loads((tmp_path / "server.state.json").read_text(encoding="utf-8"))
    assert stored["status"] == "stopped"
    assert stored["stopped_at"] is not None


def test_stop_background_server_wraps_permission_error(monkeypatch, tmp_path: Path) -> None:
    state = process_manager.ServerRuntimeState(
        pid=4321,
        host="127.0.0.1",
        port=8123,
        transport="streamable-http",
        url="http://127.0.0.1:8123/mcp",
        state_file=str(tmp_path / "server.state.json"),
        log_file=str(tmp_path / "server.log"),
        started_at="2026-06-09T00:00:00Z",
        command=["python", "-m", "nilo.mcp_server.runner"],
    )
    process_manager.write_json_atomic(tmp_path / "server.state.json", state.to_dict())
    monkeypatch.setenv("NOTION_MCP_RUNTIME_DIR", str(tmp_path))
    monkeypatch.setattr(process_manager, "is_pid_running", lambda pid: True)
    monkeypatch.setattr(process_manager.os, "kill", lambda pid, sig: (_ for _ in ()).throw(PermissionError()))

    with pytest.raises(process_manager.ServerProcessError, match="Permission denied"):
        process_manager.stop_background_server()
