"""models/scene.py — 3D scene data models."""

from __future__ import annotations
from pydantic import BaseModel
from typing import Literal, Any


class PBRMaterial(BaseModel):
    surface_type: str
    roughness: float
    metalness: float
    color_suggestion: str
    threejs_snippet: str
    babylonjs_snippet: str
    notes: str


class PerspectiveResult(BaseModel):
    fov_deg: float
    aspect_ratio: float
    perspective_css: str        # "perspective: 800px"
    projection_info: dict[str, Any]
    threejs_snippet: str
    css_3d_snippet: str


class SceneValidation(BaseModel):
    valid: bool
    score: int                  # 0-100
    issues: list[str]
    suggestions: list[str]
    light_count: int
    has_camera: bool
    object_count: int


class QualityReview(BaseModel):
    score: int                  # 0-100
    grade: Literal["A", "B", "C", "D", "F"]
    issues: list[dict[str, str]]  # [{type, severity, description, fix}]
    summary: str
    passed_checks: list[str]
