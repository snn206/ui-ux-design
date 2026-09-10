"""tests/test_color.py — Unit tests for Color module."""

from ui_ux_design.modules.color.v1.tools import (
    generate_color_palette,
    check_wcag_contrast,
    generate_dark_tokens,
    generate_gradient,
)


def test_generate_color_palette():
    palette = generate_color_palette(base_color="#3b82f6", scheme="triadic", steps=3)
    assert "colors" in palette
    assert len(palette["colors"]) == 3
    assert "css_vars" in palette
    assert "--color-" in palette["css_vars"]
    assert palette["scheme"] == "triadic"


def test_check_wcag_contrast():
    # White on black should have maximum contrast (~21)
    res = check_wcag_contrast(fg="#FFFFFF", bg="#000000")
    assert res["ratio"] >= 20.0
    assert res["AA_normal"] is True
    assert res["AAA_normal"] is True
    assert res["grade"] == "AAA"

    # Same colors should fail
    res_fail = check_wcag_contrast(fg="#777777", bg="#777777")
    assert res_fail["ratio"] == 1.0
    assert res_fail["AA_normal"] is False
    assert res_fail["grade"] == "FAIL"


def test_generate_dark_tokens():
    light = {
        "primary": "#3b82f6",
        "surface": "#ffffff",
        "text": "#111827",
    }
    tokens = generate_dark_tokens(light_tokens=light)
    assert "dark_tokens" in tokens
    assert "strategy" in tokens
    assert "surface" in tokens["dark_tokens"]
    # Inverted white surface should be dark
    assert tokens["dark_tokens"]["surface"].lower() == "#000000"


def test_generate_gradient():
    grad = generate_gradient(colors=["#3b82f6", "#9333ea"], angle=90)
    assert "linear-gradient" in grad["css"]
    assert "90deg" in grad["css"]
