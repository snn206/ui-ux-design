"""
tests/test_version_manager.py — Unit tests for GitHubVersionHub, VersionManager, and CLI.
"""

import json
from pathlib import Path
import pytest
from click.testing import CliRunner

from ui_ux_design.platform import USER_CACHE_DIR
from ui_ux_design.version_hub import GitHubVersionHub
from ui_ux_design.version_manager import VersionManager
from ui_ux_design.cli.main import main


@pytest.fixture
def mock_catalog(tmp_path: Path) -> Path:
    cat_file = tmp_path / "mock_versions.json"
    data = {
        "schema_version": "1.0",
        "repository": "snn206/ui-ux-design",
        "latest_release": "v1.0.0",
        "releases": {
            "v1.0.0": {
                "tag": "v1.0.0",
                "version": "1.0.0",
                "date": "2026-03-01",
                "type": "stable",
                "name": "Foundation Release",
                "description": "Bản phát hành chuẩn",
                "changelog": ["Init"],
            },
            "v1.1.0": {
                "tag": "v1.1.0",
                "version": "1.1.0",
                "date": "2026-06-15",
                "type": "feature",
                "name": "Enhanced Release",
                "description": "Nâng cấp tokens",
                "changelog": ["Enhancement"],
            },
        },
        "skills": {
            "ui-fundamentals": {"versions": ["1.0.0", "1.1.0"]}
        },
    }
    cat_file.write_text(json.dumps(data), encoding="utf-8")
    return cat_file


@pytest.fixture
def sample_project(tmp_path: Path):
    proj = tmp_path / "my_proj"
    proj.mkdir()
    ui_mcp = proj / ".ui-mcp"
    ui_mcp.mkdir()
    skills_dir = proj / ".agents" / "skills"
    skills_dir.mkdir(parents=True)

    skills_lock = ui_mcp / "skills.lock"
    skills_lock.write_text(
        '[active]\nui-fundamentals = "1.0.0"\n'
        '[history]\nui-fundamentals = ["1.0.0"]\n'
        '[release]\ncurrent = "v1.0.0"\nhistory = ["v1.0.0"]\n',
        encoding="utf-8",
    )

    modules_lock = ui_mcp / "modules.lock"
    modules_lock.write_text(
        '[active]\ncolor = "1.0.0"\n',
        encoding="utf-8",
    )

    # create a sample skill
    sk = skills_dir / "ui-fundamentals"
    sk.mkdir()
    (sk / "SKILL.md").write_text("# Fundamentals v1.0.0", encoding="utf-8")

    return {
        "root": proj,
        "skills_lock": skills_lock,
        "modules_lock": modules_lock,
        "skills_dir": skills_dir,
    }


def test_hub_fetch_catalog(tmp_path: Path, mock_catalog: Path):
    hub = GitHubVersionHub(
        cache_dir=tmp_path / "cache",
        versions_cache=mock_catalog,
        versions_url="http://invalid-url-should-use-cache.example",
    )
    cat = hub.fetch_catalog()
    assert cat["latest_release"] == "v1.0.0"
    assert "v1.1.0" in cat["releases"]


def test_hub_list_releases(tmp_path: Path, mock_catalog: Path):
    hub = GitHubVersionHub(
        cache_dir=tmp_path / "cache",
        versions_cache=mock_catalog,
        versions_url="http://invalid-url.example",
    )
    releases = hub.list_releases()
    assert len(releases) == 2
    tags = [r["tag"] for r in releases]
    assert "v1.0.0" in tags
    assert "v1.1.0" in tags


def test_hub_download_fallback(tmp_path: Path, mock_catalog: Path):
    cache_dir = tmp_path / "cache"
    hub = GitHubVersionHub(
        cache_dir=cache_dir,
        versions_cache=mock_catalog,
        versions_url="http://invalid-url.example",
    )
    # Should populate via fallback when download fails
    dest = hub.download_version("v1.0.0")
    assert dest.exists()
    assert dest.is_dir()
    assert (dest / "ui-fundamentals").exists()


def test_version_manager_status(sample_project, tmp_path: Path, mock_catalog: Path):
    hub = GitHubVersionHub(
        cache_dir=tmp_path / "cache",
        versions_cache=mock_catalog,
    )
    vm = VersionManager(
        project_root=sample_project["root"],
        skills_lock=sample_project["skills_lock"],
        modules_lock=sample_project["modules_lock"],
        skills_dir=sample_project["skills_dir"],
        hub=hub,
    )
    status = vm.get_status()
    assert status["active_release"] == "v1.0.0"
    assert status["latest_release"] == "v1.0.0"
    assert status["is_latest"] is True
    assert "ui-fundamentals" in status["active_skills"]


def test_version_manager_switch_local(sample_project, tmp_path: Path, mock_catalog: Path):
    hub = GitHubVersionHub(
        cache_dir=tmp_path / "cache",
        versions_cache=mock_catalog,
    )
    vm = VersionManager(
        project_root=sample_project["root"],
        skills_lock=sample_project["skills_lock"],
        modules_lock=sample_project["modules_lock"],
        skills_dir=sample_project["skills_dir"],
        hub=hub,
    )
    res = vm.switch("local")
    assert res["success"] is True
    assert res["version"] == "local"

    status = vm.get_status()
    assert status["active_release"] == "local"


def test_version_manager_switch_and_rollback(sample_project, tmp_path: Path, mock_catalog: Path):
    hub = GitHubVersionHub(
        cache_dir=tmp_path / "cache",
        versions_cache=mock_catalog,
    )
    vm = VersionManager(
        project_root=sample_project["root"],
        skills_lock=sample_project["skills_lock"],
        modules_lock=sample_project["modules_lock"],
        skills_dir=sample_project["skills_dir"],
        hub=hub,
    )
    # Switch to v1.1.0
    res = vm.switch("v1.1.0")
    assert res["success"] is True
    status = vm.get_status()
    assert status["active_release"] == "v1.1.0"

    # Rollback to previous (v1.0.0)
    rolled = vm.rollback()
    assert rolled == "v1.0.0"
    status2 = vm.get_status()
    assert status2["active_release"] == "v1.0.0"


def test_cli_version_commands():
    runner = CliRunner()

    # 1. Test 'ui-mcp version status'
    res_status = runner.invoke(main, ["version", "status"])
    assert res_status.exit_code == 0
    assert "Anti-AI-UI Version Status" in res_status.output

    # 2. Test 'ui-mcp version list'
    res_list = runner.invoke(main, ["version", "list"])
    assert res_list.exit_code == 0
    assert "Kho Version Hệ Thống" in res_list.output
    assert "v1.0.0" in res_list.output

    # 3. Test 'ui-mcp version switch local'
    res_switch = runner.invoke(main, ["version", "switch", "local"])
    assert res_switch.exit_code == 0
    assert "Đã chuyển đổi thành công" in res_switch.output
