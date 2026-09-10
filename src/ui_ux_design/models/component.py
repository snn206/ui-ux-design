"""models/component.py — Pydantic models for component_spec module."""

from __future__ import annotations
from pydantic import BaseModel


class ButtonSpec(BaseModel):
    variant: str               # "dark" | "light" | "outline"
    size: str                  # "sm" | "md" | "lg"
    with_arrow: bool
    arrow_direction: str       # "right" | "up-right"
    css: str                   # Complete CSS snippet
    hover_spring: str          # cubic-bezier string for hover
    hover_duration_ms: int
    padding: str
    border_radius: str
    font_size: str
    font_weight: str
    background: str
    color: str
    badge_bg: str | None = None
    badge_color: str | None = None


class CardSpec(BaseModel):
    type: str                  # "portfolio" | "feature" | "stat" | "hero"
    background: str
    padding: str
    border_radius: str
    min_height: str | None = None
    box_shadow: str | None = None
    hover_transform: str       # e.g. "translateY(-8px) scale(1.012)"
    hover_spring: str          # cubic-bezier
    hover_duration_ms: int
    css: str


class HeroSpec(BaseModel):
    layout: str                # "fullbleed" | "split" | "centered"
    has_canvas_effect: bool
    has_watermark: bool
    has_loader_gate: bool
    background: str
    canvas_brush_radius: int | None = None
    canvas_decay: float | None = None
    watermark_text: str | None = None
    watermark_font_size: str | None = None
    watermark_color: str | None = None
    adaptive_grid_css: str
    css: str


class LoaderSpec(BaseModel):
    style: str                 # "branded" | "minimal" | "progress-only"
    fill_ms: int               # Duration for 0→100 count
    background: str
    foreground: str
    accent: str
    has_counter: bool
    counter_padding: int       # digits (e.g. 3 → "000")
    exit_transform: str        # e.g. "translateY(-100%)"
    exit_spring: str
    exit_duration_ms: int
    css: str
    js_snippet: str


class ComponentSpecResult(BaseModel):
    component_type: str
    spec: dict
    css_tokens: dict[str, str]  # CSS variable name → value
    usage_example: str
