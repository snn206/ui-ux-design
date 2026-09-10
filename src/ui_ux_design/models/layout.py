"""models/layout.py — Layout data models."""

from __future__ import annotations
from pydantic import BaseModel
from typing import Any


class GridSpec(BaseModel):
    column_width: float
    total_gutter: int
    css: str
    breakpoints: dict[str, Any]


class SpacingScale(BaseModel):
    scale: dict[str, int]   # {xs:4, sm:8, md:16, ...}
    css_vars: str


class LayoutAnalysis(BaseModel):
    alignment_score: float     # 0-100
    spacing_consistency: float # 0-100
    issues: list[str]
    suggestions: list[str]


class ElevationLevel(BaseModel):
    level: int                 # 0-5
    css_box_shadow: str
    blur: int
    spread: int
    opacity: float
    y_offset: int


class ZStack(BaseModel):
    z_indices: dict[str, int]
    css_vars: str


class ParallaxResult(BaseModel):
    offsets: dict[str, float]  # {layer_name: translateY_px}
    css_transforms: dict[str, str]
