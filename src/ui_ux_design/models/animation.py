"""models/animation.py — Animation data models."""

from __future__ import annotations
from pydantic import BaseModel
from typing import Literal


class EasingResult(BaseModel):
    curve: str
    eased_values: list[float]
    css_value: str              # "cubic-bezier(0.4, 0, 0.2, 1)"
    duration_suggestion: str


class AnimationDuration(BaseModel):
    element_type: str
    duration_ms: int
    easing: str
    css_transition: str
    rationale: str


class SpringConfig(BaseModel):
    mass: float
    stiffness: float
    damping: float
    values: list[float]         # sampled spring positions
    css_approximation: str


class TypeScale(BaseModel):
    scale: dict[str, int]       # {xs:13, sm:16, md:20, lg:25, xl:31, "2xl":39}
    css_vars: str
    line_heights: dict[str, float]
    letter_spacings: dict[str, str]
    font_pair_suggestion: dict[str, str]  # {heading: "...", body: "..."}
