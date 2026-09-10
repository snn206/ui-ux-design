"""
tests/test_self_hosted_server.py — Tests for project self-hosted MCP server.
"""

from pathlib import Path
from click.testing import CliRunner

from ui_ux_design.cli.init_cmd import _copy_mcp_server, _server_block, _detect_python
from ui_ux_design.cli.main import main


def test_copy_mcp_server(tmp_path: Path):
    proj = tmp_path / "test_project"
    proj.mkdir()

    _copy_mcp_server(proj, force=True)

    server_dir = proj / ".ui-mcp" / "server"
    assert server_dir.exists()
    assert (server_dir / "server.py").exists()
    assert (server_dir / "module_base.py").exists()
    assert (server_dir / "module_registry.py").exists()
    assert (server_dir / "models").is_dir()
    assert (server_dir / "modules").is_dir()
    assert (server_dir / "modules" / "color" / "v1" / "tools.py").exists()


def test_server_block_points_to_project_server(tmp_path: Path):
    proj = tmp_path / "test_project"
    block_var = _server_block(proj, var=True)
    assert block_var["args"] == ["${workspaceFolder}/.ui-mcp/server/server.py"]
    assert block_var["cwd"] == "${workspaceFolder}"

    block_no_var = _server_block(proj, var=False)
    assert block_no_var["args"] == [str(proj / ".ui-mcp/server/server.py")]
    assert block_no_var["cwd"] == str(proj)


def test_detect_python_with_venv(tmp_path: Path):
    proj = tmp_path / "venv_project"
    venv_bin = proj / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "python").touch()

    detected = _detect_python(proj)
    assert detected == "${workspaceFolder}/.venv/bin/python"


def test_init_command_creates_self_hosted_server(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--ide", "agy,cursor", "--force"])
    assert result.exit_code == 0
    assert "Self-hosted MCP server" in result.output
    assert (tmp_path / ".ui-mcp" / "server" / "server.py").exists()
    assert (tmp_path / ".agents" / "mcp_config.json").exists()
    assert (tmp_path / ".cursor" / "mcp.json").exists()
