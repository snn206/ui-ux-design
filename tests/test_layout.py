"""tests/test_layout.py — Unit tests for Layout module."""

from ui_ux_design.modules.layout.v1.tools import (
    calc_grid,
    calc_spacing_scale,
    calc_elevation_shadow,
    analyze_layout,
)


def test_calc_grid():
    grid = calc_grid(container_px=1280, columns=12, gutter_px=16, margin_px=24)
    assert grid["column_width"] > 0
    assert grid["total_gutter"] == 16 * 11
    assert "grid-template-columns" in grid["css"]
    assert "1440" in grid["breakpoints"]


def test_calc_spacing_scale():
    scale = calc_spacing_scale(base=8)
    assert "scale" in scale
    assert "css_vars" in scale
    assert scale["scale"]["md"] == 12  # base 8 * 1.5
    assert "--space-md: 12px;" in scale["css_vars"]


def test_calc_elevation_shadow():
    shadow0 = calc_elevation_shadow(0)
    assert shadow0["css_box_shadow"] == "0px 0px 0px 0px rgba(0,0,0,0.0)"

    shadow2 = calc_elevation_shadow(2)
    assert "rgba" in shadow2["css_box_shadow"]
    assert shadow2["level"] == 2


def test_analyze_layout():
    # Detect off-grid elements
    layout_data = {
        "elements": [
            {"type": "card", "x": 0, "y": 0, "w": 200, "h": 13},
            {"type": "button", "x": 50, "y": 20, "w": 100, "h": 27},
            {"type": "text", "x": 120, "y": 60, "w": 150, "h": 32},
        ]
    }
    analysis = analyze_layout(layout_json=layout_data)
    assert "issues" in analysis
    assert len(analysis["issues"]) > 0
    assert any("Non-8px heights" in iss for iss in analysis["issues"])
