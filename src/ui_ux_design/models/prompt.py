"""models/prompt.py — Pydantic models for prompt_engine module."""

from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class PromptSection(BaseModel):
    id: str                    # e.g. "objective", "container", "layout"
    label: str                 # Human-readable: "1. Objective"
    priority: str              # "critical" | "high" | "medium" | "low" | "skip"
    filled: bool = False       # Whether user provided data for this section
    content: dict[str, Any] = {}   # Section-specific content


class UIPromptSpec(BaseModel):
    page_type: str             # "landing" | "dashboard" | "portfolio" | "saas" | "ecommerce"
    intent: str                # Brief description of design intent
    sections: list[PromptSection]
    mcp_tools_required: list[str]   # Tools AI must call before coding
    anti_patterns_to_avoid: list[str]
    estimated_complexity: str  # "simple" | "medium" | "complex" | "premium"


class PromptValidationIssue(BaseModel):
    section_id: str
    severity: str              # "error" | "warning" | "info"
    message: str
    fix: str


class PromptValidationResult(BaseModel):
    score: int                 # 0-100
    grade: str                 # "A" | "B" | "C" | "D" | "F"
    is_valid: bool
    issues: list[PromptValidationIssue]
    missing_critical: list[str]
    summary: str
    ready_to_code: bool        # True if score >= 70 and no critical errors


class PageStructureAudit(BaseModel):
    score: int
    grade: str
    sections_present: list[str]
    sections_missing: list[str]
    sections_recommended: list[str]
    issues: list[dict[str, str]]
    summary: str
