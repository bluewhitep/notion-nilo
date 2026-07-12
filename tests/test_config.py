import json
import uuid
from pathlib import Path

import pytest

import nilo.config as legacy_config
from nilo.config import (
    get_config_path,
    load_config,
    save_config,
    set_token,
    set_user,
)
from nilo.models import Config
from nilo.core.config import CoreConfig


def test_save_and_load_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """保存后能正确读取配置。"""
    cfg_file = tmp_path / "config.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))

    user_id = str(uuid.uuid4())
    cfg = Config(notion_token="test-token", user_id=user_id)
    save_config(cfg)

    loaded = load_config()
    assert loaded.notion_token == "test-token"
    assert loaded.user_id == user_id


def test_set_token_and_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """调用 set_token 与 set_user 能正确修改配置文件。"""
    cfg_file = tmp_path / "config.json"
    monkeypatch.setenv("NOTION_MCP_CONFIG", str(cfg_file))

    # 初始写入 token
    set_token("abc")
    cfg = load_config()
    assert cfg.notion_token == "abc"
    assert cfg.user_id is None

    # 更新用户
    user_id = str(uuid.uuid4())
    set_user(user_id)
    cfg2 = load_config()
    assert cfg2.notion_token == "abc"
    assert cfg2.user_id == user_id


def test_legacy_config_symbol_is_core_config() -> None:
    assert Config is CoreConfig


def test_legacy_load_config_uses_global_core_loader(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = CoreConfig(notion_token="global-token")
    calls: list[Path | None] = []

    def fake_load_global_core_config(path: Path | None = None) -> CoreConfig:
        calls.append(path)
        return expected

    monkeypatch.setattr(
        legacy_config,
        "load_global_core_config",
        fake_load_global_core_config,
    )

    assert legacy_config.load_config() is expected
    assert calls == [None]
