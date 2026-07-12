# N.I.L.O.

[![CI](https://github.com/bluewhitep/notion-nilo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bluewhitep/notion-nilo/actions/workflows/ci.yml) [![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](pyproject.toml) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#status) [![Docs](https://img.shields.io/badge/docs-EN%20%7C%20JP%20%7C%20ZH-blue.svg)](https://bluewhitep.github.io/notion-nilo/)

N.I.L.O. - Notion Interfaces, Locally Operated - provides a local Notion runtime with shared Core/Runtime modules and thin CLI/MCP adapters.

Web docs: [bluewhitep.github.io/notion-nilo](https://bluewhitep.github.io/notion-nilo/)

## Status

- Core owns shared business logic; Runtime owns shared process and execution lifecycle behavior.
- CLI is the git-like human and Function Calling entrypoint, with explicit short aliases and stable `--json` errors.
- MCP tools are the structured Agent/LLM entrypoint and reuse Core/Runtime capabilities.
- Background MCP server lifecycle commands are available through `nilo server ...`.
- Local MCP clients use stdio; URL-based local or remote clients use Streamable HTTP. Legacy SSE is not supported.

Remote deployment guidance, authentication, TLS, and reverse-proxy configuration are deferred; current HTTP examples bind to localhost only.

The project is in alpha. Public APIs, CLI commands, and MCP tool contracts may still change before a stable release.

## Installation

### PyPI release

Install the current release from PyPI:

```bash
uv tool install notion-nilo
nilo --help
```

If you do not use `uv`, install with `pip` instead:

```bash
pip install notion-nilo
nilo --help
```

### GitHub source

Use this method to install directly from the public source repository:

```bash
git clone https://github.com/bluewhitep/notion-nilo.git
cd notion-nilo
uv tool install .
nilo --help
```

## Migration From notion-mcp

The previously published `notion-mcp` PyPI project remains separate and will not be renamed by PyPI. New releases use:

- PyPI package: `notion-nilo`
- Python import package: `nilo`
- CLI command: `nilo`
- GitHub repository: `bluewhitep/notion-nilo`

Existing `.notion_mcp/` project context directories and `NOTION_MCP_*` environment variables are intentionally kept for compatibility in this rename.

## Documentation

Web documentation is deployed with GitHub Pages:

- [Documentation site](https://bluewhitep.github.io/notion-nilo/)

Repository documentation is organized by language. The English tree is the source for content decisions:

- [中文](Docs/ZH/README.md)
- [English](Docs/EN/README.md)
- [日本語](Docs/JP/README.md)

Common English entrypoints:

- [Installation](Docs/EN/User/Installation.md)
- [Configuration](Docs/EN/User/Configuration.md)
- [MCP client setup](Docs/EN/User/MCP_Clients.md)
- [CLI reference](Docs/EN/User/Cli.md)
- [Troubleshooting](Docs/EN/User/Troubleshooting.md)

## Roadmap

- Stabilize the Core/Runtime, CLI, and MCP contracts toward the first stable release.
- Expand remote deployment security guidance before recommending network exposure.
- Keep GitHub source installation available for users who want the latest repository state before a PyPI release.

## Development

```bash
uv run pytest -q -p no:cacheprovider
uv run ruff check .
uv run mypy src
```

Live Notion tests require explicit opt-in and real Notion credentials. Do not commit tokens or local configuration files.

## Security

Report non-sensitive bugs through [GitHub issues](https://github.com/bluewhitep/notion-nilo/issues). For sensitive security reports, follow [SECURITY.md](SECURITY.md).

## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## License

Licensed under the [Apache License 2.0](LICENSE).
