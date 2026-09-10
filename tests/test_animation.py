"""tests/test_animation.py — Unit tests for Animation module."""

from ui_ux_design.modules.animation.v1.tools import (
    compute_easing,
    suggest_animation_duration,
)


def test_compute_easing():
    easing = compute_easing(curve="standard", t_values=[0.0, 0.5, 1.0])
    assert "cubic-bezier" in easing["css_value"]
    assert "eased_values" in easing
    assert len(easing["eased_values"]) == 3
    assert easing["eased_values"][0] == 0.0
    assert easing["eased_values"][2] == 1.0


def test_suggest_duration():
    res_button = suggest_animation_duration(element_type="button", complexity="micro")
    assert res_button["duration_ms"] <= 200
    assert res_button["easing"] == "ease-out"

    res_modal = suggest_animation_duration(element_type="modal", complexity="medium")
    assert 200 <= res_modal["duration_ms"] <= 450
    assert res_modal["easing"] == "standard"
