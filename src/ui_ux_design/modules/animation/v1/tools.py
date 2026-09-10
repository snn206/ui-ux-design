"""modules/animation/v1/tools.py — Animation module v1.0.0"""

from __future__ import annotations
import math
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.animation import EasingResult, AnimationDuration

# ── Easing math ───────────────────────────────────────────────────────────────

def _cubic_bezier(x1: float, y1: float, x2: float, y2: float, t: float) -> float:
    """Approximate cubic-bezier value at t using binary search."""
    def bx(t): return 3*t*(1-t)**2*x1 + 3*t**2*(1-t)*x2 + t**3
    def by(t): return 3*t*(1-t)**2*y1 + 3*t**2*(1-t)*y2 + t**3

    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if bx(mid) < t:
            lo = mid
        else:
            hi = mid
    return round(by((lo + hi) / 2), 4)


CURVES = {
    "linear":       (0.0, 0.0, 1.0, 1.0),
    "ease":         (0.25, 0.1, 0.25, 1.0),
    "ease-in":      (0.42, 0.0, 1.0, 1.0),
    "ease-out":     (0.0, 0.0, 0.58, 1.0),
    "ease-in-out":  (0.45, 0.0, 0.55, 1.0),
    # Material Design standard curves
    "standard":     (0.4, 0.0, 0.2, 1.0),
    "decelerate":   (0.0, 0.0, 0.2, 1.0),
    "accelerate":   (0.4, 0.0, 1.0, 1.0),
    # Spring approximation
    "spring":       (0.5, -0.5, 0.1, 1.5),
    "bounce":       (0.36, 0.07, 0.19, 0.97),
}


def compute_easing(
    curve: str,
    t_values: list[float],
    custom_bezier: list[float] | None = None,
) -> dict:
    """
    Compute eased values along a curve.
    t_values: list of 0.0–1.0 input times.
    Returns eased output values + CSS cubic-bezier string.
    """
    if custom_bezier and len(custom_bezier) == 4:
        x1, y1, x2, y2 = custom_bezier
    else:
        x1, y1, x2, y2 = CURVES.get(curve, CURVES["ease-in-out"])

    eased = [_cubic_bezier(x1, y1, x2, y2, max(0.0, min(1.0, t))) for t in t_values]
    css = f"cubic-bezier({x1}, {y1}, {x2}, {y2})"

    durations = {
        "spring": "300–500ms", "bounce": "400–600ms",
        "ease-out": "150–250ms", "ease-in": "100–200ms",
    }
    duration_hint = durations.get(curve, "200–400ms")

    return EasingResult(
        curve=curve,
        eased_values=eased,
        css_value=css,
        duration_suggestion=duration_hint,
    ).model_dump()


DURATION_TABLE = {
    # (element_type, complexity) → (ms, easing)
    ("icon", "micro"):      (100, "ease-out"),
    ("toggle", "micro"):    (150, "ease-in-out"),
    ("button", "micro"):    (120, "ease-out"),
    ("tooltip", "small"):   (200, "ease-out"),
    ("dropdown", "small"):  (220, "ease-in-out"),
    ("snackbar", "small"):  (250, "decelerate"),
    ("drawer", "medium"):   (300, "standard"),
    ("modal", "medium"):    (350, "standard"),
    ("panel", "medium"):    (300, "standard"),
    ("page", "large"):      (500, "ease-in-out"),
    ("3d-flip", "medium"):  (400, "ease-in-out"),
    ("3d-rotate", "large"): (500, "spring"),
}


def suggest_animation_duration(
    element_type: str,
    distance_px: int = 0,
    complexity: str = "small",
) -> dict:
    """Suggest animation duration and easing based on element type."""
    key = (element_type.lower(), complexity.lower())
    if key in DURATION_TABLE:
        ms, easing = DURATION_TABLE[key]
    else:
        # Fallback: scale duration with distance
        base = {"micro": 120, "small": 220, "medium": 350, "large": 500}.get(complexity, 250)
        ms = base + min(distance_px // 4, 200)
        easing = "ease-in-out"

    x1, y1, x2, y2 = CURVES.get(easing, CURVES["ease-in-out"])
    css = (
        f"transition: all {ms}ms cubic-bezier({x1}, {y1}, {x2}, {y2});"
    )
    rationale = (
        f"{element_type.capitalize()} ({complexity}) → {ms}ms with {easing}. "
        f"{'Distance adjusted +%dpx. ' % distance_px if distance_px else ''}"
        f"Follows Material Design motion guidelines."
    )
    return AnimationDuration(
        element_type=element_type,
        duration_ms=ms,
        easing=easing,
        css_transition=css,
        rationale=rationale,
    ).model_dump()


class AnimationModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="animation", version="1.0.0",
            description="Easing curves, spring physics, animation duration guidelines",
            tools=["compute_easing", "suggest_animation_duration"],
        )

    def health_check(self) -> HealthStatus:
        try:
            r = compute_easing("ease-out", [0.0, 0.5, 1.0])
            assert len(r["eased_values"]) == 3
            assert r["eased_values"][0] == 0.0
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(compute_easing)
        server.tool()(suggest_animation_duration)


MODULE_CLASS = AnimationModule
