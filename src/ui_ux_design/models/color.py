"""models/color.py — Color data models."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal


class ColorToken(BaseModel):
    hex: str
    hsl: str
    name: str
    role: Literal["primary", "secondary", "accent", "neutral", "surface", "custom"] = "custom"


class Palette(BaseModel):
    colors: list[ColorToken]
    css_vars: str
    preview_ascii: str
    scheme: str


class ContrastResult(BaseModel):
    fg: str
    bg: str
    ratio: float
    AA_normal: bool   # >= 4.5
    AA_large: bool    # >= 3.0
    AAA_normal: bool  # >= 7.0
    grade: Literal["AAA", "AA", "AA-large", "FAIL"]
    recommendation: str


class GradientResult(BaseModel):
    css: str
    contrast_safe: bool
    type: str
    angle: int


class DarkTokenResult(BaseModel):
    dark_tokens: dict[str, str]
    strategy: str
