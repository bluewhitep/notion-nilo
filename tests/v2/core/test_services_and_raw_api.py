import ast
import importlib
from pathlib import Path

import pytest

from nilo.core.errors import NotionOperationError
from nilo.core.services.blocks import BlocksService
from nilo.core.services.pages import PagesService
from nilo.core.services.raw_api import RawNotionService, registered_operations

REPO_ROOT = Path(__file__).resolve().parents[3]


class Recorder:
    def __init__(self, name: str) -> None:
        self.name = name
        self.calls: list[tuple[str, dict[str, object]]] = []

    def retrieve(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("retrieve", kwargs))
        return {"method": f"{self.name}.retrieve", "kwargs": kwargs}

    def create(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("create", kwargs))
        return {"method": f"{self.name}.create", "kwargs": kwargs}

    def update(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("update", kwargs))
        return {"method": f"{self.name}.update", "kwargs": kwargs}

    def list(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("list", kwargs))
        return {"results": [], "has_more": False, "next_cursor": None, "kwargs": kwargs}

    def query(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("query", kwargs))
        return {"method": f"{self.name}.query", "kwargs": kwargs}


class ChildrenRecorder(Recorder):
    def list(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("list", kwargs))
        return {"method": f"{self.name}.list", "kwargs": kwargs}

    def append(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("append", kwargs))
        return {"method": f"{self.name}.append", "kwargs": kwargs}


class BlocksRecorder(Recorder):
    def __init__(self) -> None:
        super().__init__("blocks")
        self.children = ChildrenRecorder("blocks.children")


class ViewsWithoutQuery:
    def __init__(self) -> None:
        self.queries = Recorder("views.queries")


class CustomEmojisWithoutRetrieve:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def list(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(("list", kwargs))
        return {
            "results": [{"id": "emoji-1", "name": "smile", "url": "https://example.com/smile.png"}],
            "has_more": False,
            "next_cursor": None,
        }


class FakeClient:
    def __init__(self) -> None:
        self.pages = Recorder("pages")
        self.blocks = BlocksRecorder()
        self.views = ViewsWithoutQuery()
        self.custom_emojis = CustomEmojisWithoutRetrieve()


def test_pages_service_wraps_sdk_operations() -> None:
    client = FakeClient()
    service = PagesService(client)

    assert service.retrieve("page-1")["method"] == "pages.retrieve"
    assert client.pages.calls[-1] == ("retrieve", {"page_id": "page-1"})

    service.create({"parent": {"page_id": "root"}})
    assert client.pages.calls[-1] == ("create", {"parent": {"page_id": "root"}})

    service.update("page-1", {"properties": {}})
    assert client.pages.calls[-1] == (
        "update",
        {"page_id": "page-1", "properties": {}},
    )


def test_blocks_service_uses_position_for_2026_append_contract() -> None:
    client = FakeClient()
    service = BlocksService(client)

    service.append_children(
        "block-1",
        children=[{"type": "paragraph"}],
        position={"type": "end"},
    )

    assert client.blocks.children.calls[-1] == (
        "append",
        {
            "block_id": "block-1",
            "children": [{"type": "paragraph"}],
            "position": {"type": "end"},
        },
    )


def test_service_modules_do_not_import_cli_or_mcp_layers() -> None:
    modules = [
        "blocks",
        "pages",
        "databases",
        "data_sources",
        "users",
        "comments",
        "views",
        "file_uploads",
        "search",
        "custom_emojis",
        "raw_api",
    ]

    for module_name in modules:
        module = importlib.import_module(f"nilo.core.services.{module_name}")
        source = getattr(module, "__file__", "")
        assert "/cli/" not in source
        assert "/mcp_server/" not in source


# --------------------------------
# Function Description:
# Returns absolute modules imported by one Python source file.
# Inputs/Outputs:
# Input source path; returns module names from import and from-import statements.
# Usage:
# imported_modules(Path("src/nilo/core/config.py"))
# --------------------------------
def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


# --------------------------------
# Function Description:
# Enforces one-way Core/Runtime and adapter-layer import boundaries across all source files.
# Inputs/Outputs:
# No input; asserts Core/Runtime never depend on adapters and CLI/MCP never depend on each other.
# Usage:
# pytest tests/v2/core/test_services_and_raw_api.py -k layer_import_boundaries
# --------------------------------
def test_layer_import_boundaries() -> None:
    forbidden_by_layer = {
        "core": ("nilo.cli", "nilo.mcp_server"),
        "runtime": ("nilo.cli", "nilo.mcp_server"),
        "cli": ("nilo.mcp_server",),
        "mcp_server": ("nilo.cli",),
    }

    for layer, forbidden_prefixes in forbidden_by_layer.items():
        for path in sorted((REPO_ROOT / "src" / "nilo" / layer).rglob("*.py")):
            for module in imported_modules(path):
                assert not module.startswith(forbidden_prefixes), (
                    f"{path.relative_to(REPO_ROOT)} imports forbidden layer {module}"
                )


def test_raw_api_invokes_only_registered_operations() -> None:
    client = FakeClient()
    service = RawNotionService(client)

    result = service.invoke("pages.retrieve", {"page_id": "page-1"})

    assert result["method"] == "pages.retrieve"
    assert client.pages.calls[-1] == ("retrieve", {"page_id": "page-1"})
    assert "pages.retrieve" in registered_operations()
    assert "custom_emojis.list" in registered_operations()


def test_raw_api_uses_service_fallbacks_for_sdk_endpoint_gaps() -> None:
    client = FakeClient()
    service = RawNotionService(client)

    emoji = service.invoke("custom_emojis.retrieve", {"custom_emoji_id": "emoji-1"})
    view_query = service.invoke("views.query", {"view_id": "view-1", "page_size": 10})

    assert emoji["name"] == "smile"
    assert client.custom_emojis.calls[-1] == ("list", {"page_size": 100})
    assert view_query["method"] == "views.queries.create"
    assert client.views.queries.calls[-1] == (
        "create",
        {"view_id": "view-1", "page_size": 10},
    )


def test_raw_api_rejects_unregistered_or_private_operations() -> None:
    service = RawNotionService(FakeClient())

    with pytest.raises(NotionOperationError):
        service.invoke("pages.__dict__", {})

    with pytest.raises(NotionOperationError):
        service.invoke("arbitrary.delete_everything", {})
