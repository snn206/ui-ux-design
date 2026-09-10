"""tests/test_registry_and_skills.py — Unit tests for ModuleRegistry, SkillsManager, and PromptLoader."""

import pytest
from pathlib import Path
from ui_ux_design.prompts import PromptLoader
from ui_ux_design.module_registry import ModuleRegistry


def test_prompt_loader_list():
    loader = PromptLoader()
    templates = loader.list_templates()
    assert "system_ui" in templates
    assert "2d_layout" in templates
    assert "review_checklist" in templates


def test_prompt_loader_load():
    loader = PromptLoader()
    content = loader.load("system_ui")
    assert "UI Design System Master Prompt" in content
    assert "8px Spacing Grid" in content


def test_prompt_loader_compose():
    loader = PromptLoader()
    composed = loader.compose("system_ui", "2d_layout")
    assert "UI Design System Master Prompt" in composed
    assert "2D Layout & Grid Specification Prompt" in composed


def test_prompt_loader_with_context():
    loader = PromptLoader()
    res = loader.with_context("2d_layout", platform="iOS", framework="SwiftUI")
    assert "Platform: iOS" in res
    assert "Framework: SwiftUI" in res


def test_module_registry_load(tmp_path: Path):
    lock_file = tmp_path / "modules.lock"
    lock_file.write_text(
        '[active]\ncolor = "1.0.0"\nlayout = "1.0.0"\n'
        '[history]\ncolor = ["1.0.0"]\nlayout = ["1.0.0"]\n',
        encoding="utf-8",
    )
    registry = ModuleRegistry(lock_path=lock_file)
    registry.load_all()
    statuses = registry.status()
    assert "color" in statuses
    assert "layout" in statuses
    assert statuses["color"].version == "1.0.0"
    assert statuses["color"].healthy is True

