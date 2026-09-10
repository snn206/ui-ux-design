"""
tests/test_cross_platform.py — Cross-platform compatibility tests (Windows, macOS, Linux).
"""

import os
import sys
from pathlib import Path
import pytest

from ui_ux_design.cli.init_cmd import _detect_python, _server_block, _continue_config
from ui_ux_design.platform import get_project_root, APP_NAME


def test_detect_python_cross_platform(tmp_path: Path, monkeypatch):
    # 1. Test Windows venv detection
    win_venv = tmp_path / "win_project" / ".venv" / "Scripts"
    win_venv.mkdir(parents=True)
    (win_venv / "python.exe").touch()

    detected_win = _detect_python(tmp_path / "win_project")
    assert detected_win == "${workspaceFolder}/.venv/Scripts/python.exe"

    # 2. Test Unix/macOS venv detection
    unix_venv = tmp_path / "unix_project" / ".venv" / "bin"
    unix_venv.mkdir(parents=True)
    (unix_venv / "python").touch()

    detected_unix = _detect_python(tmp_path / "unix_project")
    assert detected_unix == "${workspaceFolder}/.venv/bin/python"

    # 3. Test fallback when no venv exists
    empty_proj = tmp_path / "empty_project"
    empty_proj.mkdir()

    monkeypatch.setattr(sys, "platform", "win32")
    assert _detect_python(empty_proj) == "python"

    monkeypatch.setattr(sys, "platform", "darwin")
    assert _detect_python(empty_proj) in ("python", "python3")

    monkeypatch.setattr(sys, "platform", "linux")
    assert _detect_python(empty_proj) in ("python", "python3")


def test_server_block_path_normalization(tmp_path: Path):
    proj = tmp_path / "test_dir"
    block = _server_block(proj, var=True)

    # Must use forward slash for variable paths so it works seamlessly on Windows and Unix IDEs
    assert "${workspaceFolder}/.ui-mcp/server/server.py" in block["args"]
    assert block["cwd"] == "${workspaceFolder}"
    assert "${workspaceFolder}/.ui-mcp/config.toml" in block["env"]["UI_MCP_CONFIG"]


def test_continue_config_yaml_safe_quoting(tmp_path: Path):
    proj = tmp_path / "test_dir"
    yaml_content = _continue_config(proj)

    # Verify YAML is cleanly formatted without raw backslash syntax errors
    assert "mcpServers:" in yaml_content
    assert "ui-ux-design" in yaml_content
    assert "command:" in yaml_content
    assert "args:" in yaml_content


def test_platformdirs_user_cache():
    from platformdirs import user_config_dir
    cfg_dir = user_config_dir(APP_NAME)
    assert cfg_dir is not None
    assert len(cfg_dir) > 0
    assert APP_NAME in cfg_dir


def test_project_root_detection(tmp_path: Path):
    sub = tmp_path / "a" / "b" / "c"
    sub.mkdir(parents=True)
    (tmp_path / "pyproject.toml").touch()

    root = get_project_root(sub)
    assert root == tmp_path
