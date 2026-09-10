"""tests/test_quality.py — Unit tests for Quality module."""

import pytest
from ui_ux_design.modules.quality.v1.tools import review_ui_quality


def test_review_ui_quality_clean():
    # A clean design adhering to tokens
    result = review_ui_quality(
        description="Clean dashboard layout",
        colors=["#0F172A", "#3B82F6", "#F8FAFC"],
        fonts=["12px", "14px", "16px", "24px"],
        spacing_values=[8, 16, 24, 32],
        no_shadows=False,
    )
    assert result["score"] >= 80
    assert result["grade"] in ["A", "B"]
    assert len(result["issues"]) == 0


def test_review_ui_quality_detects_smells():
    # Generic grey + inconsistent spacing
    result = review_ui_quality(
        description="Messy UI",
        colors=["#f0f0f0", "#cccccc"],
        fonts=["13px", "17px", "23px"],
        spacing_values=[7, 13, 21],
        no_shadows=True,
    )
    assert result["score"] < 70
    issue_types = [i["type"] for i in result["issues"]]
    assert "generic-grey" in issue_types
    assert "inconsistent-spacing" in issue_types
