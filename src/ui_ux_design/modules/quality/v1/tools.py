"""modules/quality/v1/tools.py — Quality / Anti-pattern module v1.0.0"""

from __future__ import annotations
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.scene import QualityReview

# ── Anti-pattern smell catalog ────────────────────────────────────────────────

SMELLS = [
    {
        "id": "generic-grey",
        "severity": "warning",
        "name": "Generic Grey",
        "desc": "Overuse of generic grey tones (#f0f0f0, #e0e0e0, #ccc) with no HSL system",
        "fix": "Build an HSL tonal palette. Use tool: generate_color_palette",
        "check": lambda colors, **kw: any(c.lower() in {"#f0f0f0","#e0e0e0","#cccccc","#ccc","#ddd","#eee"} for c in colors) if colors else False,
    },
    {
        "id": "rainbow-hell",
        "severity": "critical",
        "name": "Rainbow Hell",
        "desc": "More than 4 distinct hues used in a single screen",
        "fix": "Apply 60-30-10 rule: one dominant hue, one secondary, one accent",
        "check": lambda colors, **kw: len(set(_hue_bucket(c) for c in colors if c.startswith("#"))) > 4 if colors else False,
    },
    {
        "id": "font-chaos",
        "severity": "warning",
        "name": "Font Size Chaos",
        "desc": "Font sizes not following a modular scale",
        "fix": "Use calc_type_scale to generate a consistent type scale",
        "check": lambda fonts, **kw: _has_arbitrary_sizes(fonts) if fonts else False,
    },
    {
        "id": "inconsistent-spacing",
        "severity": "warning",
        "name": "Inconsistent Spacing",
        "desc": "Spacing values not on 8px grid",
        "fix": "Use calc_spacing_scale and stick to multiples of 8",
        "check": lambda spacing, **kw: any(v % 8 != 0 for v in spacing if isinstance(v, int) and v > 0) if spacing else False,
    },
    {
        "id": "no-depth",
        "severity": "info",
        "name": "Flat / No Depth",
        "desc": "No shadows or elevation — UI feels flat and lifeless",
        "fix": "Add subtle elevation using calc_elevation_shadow levels 1–2 for cards",
        "check": lambda **kw: kw.get("no_shadows", False),
    },
    {
        "id": "over-animation",
        "severity": "info",
        "name": "Over-Animation",
        "desc": "Every element animates — reduces focus and performance",
        "fix": "Only animate with purpose: state changes, feedback, onboarding",
        "check": lambda **kw: False,  # heuristic — needs user declaration
    },
]


def _hue_bucket(hex_color: str) -> int:
    """Quantize hue to nearest 30° bucket."""
    try:
        import colorsys
        h = hex_color.lstrip("#")
        if len(h) == 3: h = "".join(c*2 for c in h)
        r, g, b = int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255
        hue, _, _ = colorsys.rgb_to_hls(r, g, b)
        return int(hue * 360 / 30)
    except Exception:
        return 0


def _has_arbitrary_sizes(font_sizes: list) -> bool:
    """Check if font sizes follow any known scale."""
    known_scale_values = {10,11,12,13,14,16,18,20,24,28,32,36,40,48,56,64,72,80,96}
    for s in font_sizes:
        try:
            val = int(str(s).replace("px","").replace("rem","").split(".")[0])
            if val > 0 and val not in known_scale_values:
                return True
        except Exception:
            pass
    return False


def review_ui_quality(
    description: str = "",
    colors: list[str] | None = None,
    fonts: list[str] | None = None,
    spacing_values: list[int] | None = None,
    no_shadows: bool = False,
) -> dict:
    """
    Score a UI design against known anti-patterns.
    Returns score (0-100), grade, issues, and summary.
    """
    colors = colors or []
    fonts = fonts or []
    spacing_values = spacing_values or []

    found_issues = []
    passed = []

    for smell in SMELLS:
        try:
            triggered = smell["check"](
                colors=colors, fonts=fonts,
                spacing=spacing_values, no_shadows=no_shadows,
            )
        except Exception:
            triggered = False

        if triggered:
            found_issues.append({
                "type": smell["id"],
                "severity": smell["severity"],
                "description": smell["desc"],
                "fix": smell["fix"],
            })
        else:
            passed.append(smell["name"])

    deductions = {"critical": 20, "warning": 10, "info": 5}
    score = 100 - sum(deductions.get(i["severity"], 5) for i in found_issues)
    score = max(0, score)

    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

    if score >= 90:
        summary = "🎉 Excellent UI quality — minimal issues detected."
    elif score >= 75:
        summary = "✓ Good UI — minor improvements available."
    elif score >= 60:
        summary = "⚠ Average — several anti-patterns need attention."
    else:
        summary = "✗ Poor UI quality — significant issues detected. Please review."

    return QualityReview(
        score=score, grade=grade,
        issues=found_issues,
        summary=summary,
        passed_checks=passed,
    ).model_dump()


class QualityModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="quality", version="1.0.0",
            description="UI quality scoring and anti-pattern detection (AI UI smell catalog)",
            tools=["review_ui_quality"],
        )

    def health_check(self) -> HealthStatus:
        try:
            r = review_ui_quality(colors=["#ffffff", "#000000"])
            assert "score" in r
            assert 0 <= r["score"] <= 100
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(review_ui_quality)


MODULE_CLASS = QualityModule
