"""modules/layout/v1/tools.py — Layout module v1.0.0"""

from __future__ import annotations
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.layout import (
    GridSpec, SpacingScale, LayoutAnalysis, ElevationLevel, ZStack, ParallaxResult,
)

# ── Tool implementations ──────────────────────────────────────────────────────

def calc_grid(container_px: int, columns: int, gutter_px: int, margin_px: int) -> dict:
    """Calculate CSS grid system parameters."""
    usable = container_px - (2 * margin_px)
    total_gutter = gutter_px * (columns - 1)
    col_width = (usable - total_gutter) / columns
    css = (
        f"display: grid;\n"
        f"grid-template-columns: repeat({columns}, {col_width:.1f}px);\n"
        f"gap: {gutter_px}px;\n"
        f"padding: 0 {margin_px}px;"
    )
    # Responsive breakpoints (scale down columns)
    breakpoints = {
        "1440": {"columns": columns, "gutter": gutter_px},
        "1024": {"columns": max(columns // 2, 6), "gutter": max(gutter_px - 8, 16)},
        "768":  {"columns": 6, "gutter": 16},
        "375":  {"columns": 4, "gutter": 12},
    }
    return GridSpec(
        column_width=round(col_width, 2),
        total_gutter=total_gutter,
        css=css,
        breakpoints=breakpoints,
    ).model_dump()


def calc_spacing_scale(base: int = 8, steps: list[float] | None = None) -> dict:
    """Generate an 8-point spacing scale."""
    if steps is None:
        steps = [0.5, 1, 1.5, 2, 3, 4, 6, 8, 12]
    names = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]
    scale = {names[i]: round(base * s) for i, s in enumerate(steps) if i < len(names)}
    css_vars = ":root {\n" + "\n".join(f"  --space-{k}: {v}px;" for k, v in scale.items()) + "\n}"
    return SpacingScale(scale=scale, css_vars=css_vars).model_dump()


def preview_ascii_grid(columns: int, gutter: int, width: int = 80) -> str:
    """Render an ASCII art grid preview."""
    col_w = max((width - (gutter * (columns - 1))) // columns, 3)
    col_str = "█" * col_w
    gap_str = "·" * gutter
    row = gap_str.join([col_str] * columns)
    header = f"Grid: {columns} cols, {gutter}px gutter, ~{col_w}px/col"
    ruler = "─" * width
    return f"{header}\n{ruler}\n{row}\n{ruler}"


def analyze_layout(layout_json: dict) -> dict:
    """Analyze a layout for alignment, spacing consistency, and common issues."""
    elements = layout_json.get("elements", [])
    if not elements:
        return LayoutAnalysis(
            alignment_score=0, spacing_consistency=0,
            issues=["No elements provided"],
            suggestions=["Describe layout elements with {x, y, w, h, type}"],
        ).model_dump()

    # Check alignment: how many elements share x or right edge
    xs = [e.get("x", 0) for e in elements]
    unique_xs = len(set(xs))
    alignment_score = max(0, 100 - (unique_xs / len(xs)) * 100 * 0.5)

    # Check spacing consistency: all gaps multiples of 8?
    heights = sorted(set(e.get("h", 0) for e in elements))
    bad_spacings = [h for h in heights if h % 8 != 0 and h > 0]
    spacing_score = 100 - (len(bad_spacings) / max(len(heights), 1)) * 100

    issues, suggestions = [], []
    if bad_spacings:
        issues.append(f"Non-8px heights found: {bad_spacings[:3]}")
        suggestions.append("Use 8px grid: all heights/margins should be multiples of 8")
    if unique_xs > len(xs) / 2:
        issues.append("Elements have many different X positions — poor alignment")
        suggestions.append("Align elements to grid columns for visual consistency")

    return LayoutAnalysis(
        alignment_score=round(alignment_score, 1),
        spacing_consistency=round(spacing_score, 1),
        issues=issues,
        suggestions=suggestions,
    ).model_dump()


def calc_elevation_shadow(level: int) -> dict:
    """Return CSS box-shadow for an elevation level (0–5)."""
    level = max(0, min(5, level))
    configs = [
        (0, 0, 0, 0.0, 0),     # 0: no shadow
        (0, 1, 3, 0.12, 1),    # 1: subtle
        (0, 2, 8, 0.15, 2),    # 2: card
        (0, 4, 16, 0.18, 4),   # 3: dropdown
        (0, 8, 24, 0.20, 8),   # 4: modal
        (0, 16, 48, 0.24, 16), # 5: drawer
    ]
    x, y, blur, opacity, spread = configs[level]
    shadow = f"{x}px {y}px {blur}px {spread}px rgba(0,0,0,{opacity})"
    return ElevationLevel(
        level=level, css_box_shadow=shadow,
        blur=blur, spread=spread, opacity=opacity, y_offset=y,
    ).model_dump()


def calc_z_stack(layers: list[str]) -> dict:
    """Assign z-index values to a list of layers (back→front)."""
    base = 0
    step = 10
    z_indices = {layer: base + i * step for i, layer in enumerate(layers)}
    css_vars = ":root {\n" + "\n".join(
        f"  --z-{layer.replace(' ', '-')}: {z};" for layer, z in z_indices.items()
    ) + "\n}"
    return ZStack(z_indices=z_indices, css_vars=css_vars).model_dump()


def calc_parallax_offset(scroll_y: float, layers: list[dict]) -> dict:
    """
    Calculate parallax translateY for each layer.
    Each layer: {name: str, depth_factor: 0.0–1.0}
    depth_factor=0 → no movement, depth_factor=1 → full scroll speed.
    """
    offsets: dict[str, float] = {}
    transforms: dict[str, str] = {}
    for layer in layers:
        name = layer.get("name", "layer")
        factor = float(layer.get("depth_factor", 0.5))
        offset = round(scroll_y * factor, 2)
        offsets[name] = offset
        transforms[name] = f"transform: translateY({offset}px);"
    return ParallaxResult(offsets=offsets, css_transforms=transforms).model_dump()


# ── Module class ──────────────────────────────────────────────────────────────

class LayoutModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="layout", version="1.0.0",
            description="Grid calculator, spacing scale, layout analysis, elevation, z-stack, parallax",
            tools=["calc_grid", "calc_spacing_scale", "preview_ascii_grid",
                   "analyze_layout", "calc_elevation_shadow", "calc_z_stack",
                   "calc_parallax_offset"],
        )

    def health_check(self) -> HealthStatus:
        try:
            g = calc_grid(1440, 12, 24, 80)
            assert g["column_width"] > 0
            s = calc_spacing_scale()
            assert "sm" in s["scale"]
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        for fn in [calc_grid, calc_spacing_scale, preview_ascii_grid,
                   analyze_layout, calc_elevation_shadow, calc_z_stack,
                   calc_parallax_offset]:
            server.tool()(fn)


MODULE_CLASS = LayoutModule
