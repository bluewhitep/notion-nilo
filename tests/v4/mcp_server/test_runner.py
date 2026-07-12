import sys

from nilo.core.config_constants import SUPPORTED_TRANSPORTS
from nilo.mcp_server.runner import parse_args
from nilo.runtime.server_process import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TRANSPORT


def test_runner_defaults_follow_runtime_contract(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["nilo.mcp_server.runner"])

    args = parse_args()

    assert args.transport == DEFAULT_TRANSPORT == "streamable-http"
    assert args.host == DEFAULT_HOST
    assert args.port == DEFAULT_PORT


def test_runner_accepts_each_core_supported_transport(monkeypatch) -> None:
    parsed: list[str] = []
    for transport in SUPPORTED_TRANSPORTS:
        monkeypatch.setattr(
            sys,
            "argv",
            ["nilo.mcp_server.runner", "--transport", transport],
        )
        parsed.append(parse_args().transport)

    assert tuple(parsed) == SUPPORTED_TRANSPORTS
