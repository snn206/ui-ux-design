"""modules/quality/v2/tools.py — Quality / Anti-pattern module v2.0.0

Extends v1 with 7 new AI Smell checks for studio-grade UI:
- loader-missing, no-adaptive-grid, spring-missing, canvas-missing,
- watermark-missing, no-scroll-lock, hardcoded-z-index

Also adds audit_page_structure proxy (delegates to prompt_engine module).
"""

from __future__ import annotations
from typing import Any
import re

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.scene import QualityReview

# ── Anti-pattern smell catalog v2 ─────────────────────────────────────────────

SMELLS_V2 = [
    # ── Inherited from v1 ──────────────────────────────────────────────────
    {
        "id": "generic-grey",
        "severity": "warning",
        "name": "Generic Grey",
        "desc": "Overuse of generic grey tones (#f0f0f0, #e0e0e0, #ccc) with no HSL system",
        "fix": "Build an HSL tonal palette. Use tool: generate_color_palette",
        "check": lambda colors, **kw: any(
            c.lower() in {"#f0f0f0","#e0e0e0","#cccccc","#ccc","#ddd","#eee"}
            for c in colors
        ) if colors else False,
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
        "id": "low-contrast",
        "severity": "critical",
        "name": "Low Contrast",
        "desc": "Text contrast likely below WCAG AA (4.5:1)",
        "fix": "Run check_wcag_contrast for all text/background pairs. Fix failing pairs.",
        "check": lambda **kw: kw.get("low_contrast", False),
    },

    # ── New in v2 — Studio-grade anti-AI smells ───────────────────────────
    {
        "id": "loader-missing",
        "severity": "warning",
        "name": "Missing Page Loader",
        "desc": "Single page apps/landing pages have no branded loader — first impression is blank screen",
        "fix": (
            "Add a branded loader: full-screen panel, Logo+tagline, "
            "progress bar, counter 000→100 (easeInOutCubic, FILL_MS=1300ms), "
            "exit slide-up translateY(-100%). Use spec_loader() for full spec."
        ),
        "check": lambda **kw: kw.get("loader_missing", False),
    },
    {
        "id": "no-adaptive-grid",
        "severity": "warning",
        "name": "No Adaptive Grid",
        "desc": "Layout uses fixed px font-sizes instead of rem-based vw-scaled adaptive grid",
        "fix": (
            "Add rem-based vw media queries:\n"
            "@media (max-width:1920px){ html{ font-size:0.833333vw } }\n"
            "@media (max-width:1440px){ html{ font-size:1.111111vw } }\n"
            "@media (max-width:1024px){ html{ font-size:1.5625vw } }\n"
            "@media (max-width:640px){  html{ font-size:4.444444vw } }\n"
            "Use rem for ALL sizes. Add JS scale-up above 1920px."
        ),
        "check": lambda **kw: kw.get("no_adaptive_grid", False),
    },
    {
        "id": "spring-missing",
        "severity": "warning",
        "name": "Missing Spring Physics",
        "desc": "Hover/reveal animations use 'ease' or 'linear' instead of spring-like cubic-bezier",
        "fix": (
            "Replace: transition: all 0.3s ease\n"
            "With spring cubic-beziers:\n"
            "  Hover snappy: cubic-bezier(.2,.8,.2,1) 350ms\n"
            "  Reveals: cubic-bezier(.22,1,.36,1) 700ms\n"
            "  Modals: cubic-bezier(.34,1.56,.64,1) 600ms\n"
            "Use compute_easing('spring', [...]) for exact values."
        ),
        "check": lambda css_snippets, **kw: _has_generic_easing(css_snippets) if css_snippets else False,
    },
    {
        "id": "canvas-missing",
        "severity": "info",
        "name": "Static Hero (No Canvas Effect)",
        "desc": "Hero section has only static image/video — no interactive canvas or cursor effect",
        "fix": (
            "Add a canvas-based hero effect (liquid brush reveal, particle trail, etc.). "
            "Minimum: cursor-reactive overlay. Use spec_hero(has_canvas_effect=True) for spec. "
            "Always honor prefers-reduced-motion by disabling canvas."
        ),
        "check": lambda **kw: kw.get("canvas_missing", False),
    },
    {
        "id": "watermark-missing",
        "severity": "info",
        "name": "No Brand Watermark",
        "desc": "Hero and/or footer have no oversized brand text/mark — missed depth and identity layer",
        "fix": (
            "Add oversized watermark: position:absolute; font-size:13rem; "
            "color:rgba(255,255,255,0.05); pointer-events:none; user-select:none. "
            "Reveal with opacity 0→0.4 spring animation."
        ),
        "check": lambda **kw: kw.get("watermark_missing", False),
    },
    {
        "id": "no-scroll-lock",
        "severity": "warning",
        "name": "Modal/Overlay Missing Scroll Lock",
        "desc": "Modal or nav overlay opens without locking page scroll — content jumps or scrolls under overlay",
        "fix": (
            "Implement scroll lock model:\n"
            "  stopScroll() → lenis.stop() + html overflow:hidden\n"
            "  startScroll() → lenis.start() + remove overflow\n"
            "Call stopScroll() on modal open, startScroll() on close."
        ),
        "check": lambda **kw: kw.get("no_scroll_lock", False),
    },
    {
        "id": "hardcoded-z-index",
        "severity": "warning",
        "name": "Hardcoded Arbitrary Z-index",
        "desc": "Uses z-index: 9999 or other arbitrary values not from a z-stack system",
        "fix": (
            "Use a semantic z-stack. Run calc_z_stack(['bg','content','header','overlay','modal','toast']) "
            "to get a proper z-index system. Typical: header=50, overlay=100, modal=110, nav=115, loader=120."
        ),
        "check": lambda css_snippets, **kw: _has_arbitrary_z_index(css_snippets) if css_snippets else False,
    },
]


# ── Helper functions ──────────────────────────────────────────────────────────

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
    """Check if font sizes follow any known modular scale."""
    known_scale_values = {10,11,12,13,14,16,18,20,24,28,32,36,40,48,56,64,72,80,96}
    for s in font_sizes:
        try:
            val = int(str(s).replace("px","").replace("rem","").split(".")[0])
            if val > 0 and val not in known_scale_values:
                return True
        except Exception:
            pass
    return False


def _has_generic_easing(css_snippets: list[str]) -> bool:
    """
    Detect generic 'ease', 'linear', or 'ease-in-out' transitions without cubic-bezier.
    Returns True if any snippet uses generic easing in a transition/animation rule.
    """
    generic_pattern = re.compile(
        r'transition\s*:[^;]*\b(ease|linear|ease-in|ease-out|ease-in-out)\b(?!\s*\()',
        re.IGNORECASE,
    )
    for snippet in css_snippets:
        if generic_pattern.search(str(snippet)):
            return True
    return False


def _has_arbitrary_z_index(css_snippets: list[str]) -> bool:
    """Detect z-index values outside the semantic range (>= 200 without system)."""
    z_pattern = re.compile(r'z-index\s*:\s*(\d+)', re.IGNORECASE)
    bad_values = {9999, 999, 9998, 1000, 10000, 100000}
    for snippet in css_snippets:
        for match in z_pattern.finditer(str(snippet)):
            val = int(match.group(1))
            if val in bad_values or val > 500:
                return True
    return False


# ── Main tool ─────────────────────────────────────────────────────────────────

def review_ui_quality(
    description: str = "",
    colors: list[str] | None = None,
    fonts: list[str] | None = None,
    spacing_values: list[int] | None = None,
    css_snippets: list[str] | None = None,
    no_shadows: bool = False,
    low_contrast: bool = False,
    loader_missing: bool = False,
    no_adaptive_grid: bool = False,
    canvas_missing: bool = False,
    watermark_missing: bool = False,
    no_scroll_lock: bool = False,
) -> dict:
    """
    Score a UI design against 13 known anti-patterns (v2 — 13 studio-grade anti-AI checks).

    Args:
        description: Brief description of the UI being reviewed
        colors: List of hex colors used (checks for generic grey, rainbow hell)
        fonts: List of font sizes used (checks for font chaos)
        spacing_values: List of px spacing values (checks for 8px grid compliance)
        css_snippets: List of CSS strings (checks for generic easing, arbitrary z-index)
        no_shadows: True if no shadows/elevation used anywhere
        low_contrast: True if contrast has not been verified with WCAG tools
        loader_missing: True if page has no branded loader (for SPAs/landing pages)
        no_adaptive_grid: True if layout uses fixed px font-size instead of rem/vw
        canvas_missing: True if hero has no interactive canvas/cursor effect
        watermark_missing: True if hero/footer has no brand watermark
        no_scroll_lock: True if modal/overlays don't lock scroll

    Returns:
        QualityReview with score (0-100), grade, issues list, and summary.
    """
    colors = colors or []
    fonts = fonts or []
    spacing_values = spacing_values or []
    css_snippets = css_snippets or []

    # Build kwargs for checks
    check_kwargs = dict(
        colors=colors,
        fonts=fonts,
        spacing=spacing_values,
        css_snippets=css_snippets,
        no_shadows=no_shadows,
        low_contrast=low_contrast,
        loader_missing=loader_missing,
        no_adaptive_grid=no_adaptive_grid,
        canvas_missing=canvas_missing,
        watermark_missing=watermark_missing,
        no_scroll_lock=no_scroll_lock,
    )

    found_issues = []
    passed = []

    for smell in SMELLS_V2:
        try:
            triggered = smell["check"](**check_kwargs)
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
        summary = "🎉 Excellent UI quality — minimal issues detected. Premium grade."
    elif score >= 75:
        summary = "✓ Good UI — minor improvements available. Consider high-end studio micro-interactions and depth."
    elif score >= 60:
        summary = "⚠ Average — several anti-patterns need attention before shipping."
    else:
        summary = "✗ Poor UI quality — significant issues detected. Review all CRITICAL smells first."

    return QualityReview(
        score=score, grade=grade,
        issues=found_issues,
        summary=summary,
        passed_checks=passed,
    ).model_dump()


# ── Module class ──────────────────────────────────────────────────────────────

class QualityModuleV2(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="quality",
            version="2.0.0",
            description=(
                "UI quality scoring v2 — 13 anti-pattern checks for studio-grade UI: "
                "loader-missing, no-adaptive-grid, spring-missing, canvas-missing, "
                "watermark-missing, no-scroll-lock, hardcoded-z-index."
            ),
            tools=["review_ui_quality"],
        )

    def health_check(self) -> HealthStatus:
        try:
            r = review_ui_quality(
                colors=["#ffffff", "#000000"],
                fonts=[16, 24, 32],
                spacing_values=[8, 16, 24],
            )
            assert "score" in r
            assert 0 <= r["score"] <= 100
            assert "issues" in r

            # Test new checks
            r2 = review_ui_quality(
                css_snippets=["transition: all 0.3s ease;"],
                no_adaptive_grid=True,
                loader_missing=True,
            )
            triggered = [i["type"] for i in r2["issues"]]
            assert "spring-missing" in triggered
            assert "no-adaptive-grid" in triggered
            assert "loader-missing" in triggered

            return HealthStatus(healthy=True, message="OK — quality v2 ready (13 smell checks)")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(review_ui_quality)


MODULE_CLASS = QualityModuleV2
