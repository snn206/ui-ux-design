"""
tests/test_new_modules.py — Tests for prompt_engine, component_spec, and quality v2.
"""

from __future__ import annotations
import pytest

from ui_ux_design.modules.prompt_engine.v1.tools import (
    generate_ui_prompt, validate_ui_prompt, suggest_prompt_sections, audit_page_structure
)
from ui_ux_design.modules.component_spec.v1.tools import (
    spec_button, spec_card, spec_hero, spec_loader
)
from ui_ux_design.modules.quality.v2.tools import review_ui_quality


def test_generate_and_validate_prompt():
    prompt = generate_ui_prompt(
        page_type="landing",
        intent="SaaS Analytics landing page with dark mode, fluid typography and spring reveals",
    )
    assert "sections" in prompt
    assert len(prompt["sections"]) == 11
    assert prompt["estimated_complexity"] in {"moderate", "complex"}
    assert "calc_type_scale" in prompt["mcp_tools_required"]

    validation = validate_ui_prompt(prompt)
    assert validation["score"] > 70
    assert validation["ready_to_code"] is True


def test_suggest_and_audit_sections():
    sug = suggest_prompt_sections("ecommerce")
    assert sug["critical_count"] >= 5
    section_ids = [s["id"] for s in sug["sections"]]
    assert "content" in section_ids

    audit = audit_page_structure(["header", "hero", "about", "footer"], "landing")
    assert audit["score"] < 100
    assert "loader" in audit["sections_missing"]


def test_component_spec():
    btn = spec_button("dark", "md", with_arrow=True, arrow_direction="right")
    assert "--btn-bg" in btn["css_tokens"]
    assert btn["css_tokens"]["--btn-bg"] == "#0a0a0a"

    card = spec_card("portfolio", "#0a0a0a", "2rem")
    assert card["spec"]["hover_transform"] == "translateY(-8px) scale(1.012)"

    hero = spec_hero("fullbleed", has_canvas_effect=True, has_watermark=True, brand_name="STUDIO")
    assert hero["spec"]["watermark_text"] == "STUDIO"
    assert hero["spec"]["has_canvas_effect"] is True

    loader = spec_loader("branded", 1300, "#0a0a0a", "#cf8047", "Studio")
    assert loader["spec"]["fill_ms"] == 1300
    assert loader["spec"]["has_counter"] is True


def test_quality_v2_new_smells():
    res = review_ui_quality(
        colors=["#ffffff", "#111111", "#ff5500"],
        fonts=[16, 24, 32],
        spacing_values=[8, 16, 24],
        css_snippets=["transition: all 0.3s ease;"],
        loader_missing=True,
        no_adaptive_grid=True,
    )
    assert res["score"] < 100
    issue_types = [i["type"] for i in res["issues"]]
    assert "loader-missing" in issue_types
    assert "no-adaptive-grid" in issue_types
