"""modules/prompt_engine/v1/tools.py — Prompt Engine module v1.0.0

Tools for generating and validating UI design prompts using the 11-section framework.
Helps AI think structurally before coding, preventing hallucinated design decisions.
"""

from __future__ import annotations
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.prompt import (
    PromptSection, UIPromptSpec, PromptValidationIssue,
    PromptValidationResult, PageStructureAudit,
)

# ── Section definitions ───────────────────────────────────────────────────────

ALL_SECTIONS = [
    {"id": "objective",    "label": "1. Objective",    "number": 1},
    {"id": "container",    "label": "2. Container",    "number": 2},
    {"id": "layout",       "label": "3. Layout",       "number": 3},
    {"id": "content",      "label": "4. Content",      "number": 4},
    {"id": "components",   "label": "5. Components",   "number": 5},
    {"id": "styling",      "label": "6. Styling",      "number": 6},
    {"id": "assets",       "label": "7. Assets",       "number": 7},
    {"id": "interaction",  "label": "8. Interaction",  "number": 8},
    {"id": "responsive",   "label": "9. Responsive",   "number": 9},
    {"id": "validation",   "label": "10. Validation",  "number": 10},
    {"id": "source",       "label": "11. Source",      "number": 11},
]

# Priority per page type
PAGE_TYPE_PRIORITIES: dict[str, dict[str, str]] = {
    "landing": {
        "objective": "critical",
        "container": "high",
        "layout": "critical",
        "content": "critical",
        "components": "critical",
        "styling": "critical",
        "assets": "high",
        "interaction": "critical",
        "responsive": "high",
        "validation": "medium",
        "source": "medium",
    },
    "dashboard": {
        "objective": "critical",
        "container": "medium",
        "layout": "critical",
        "content": "high",
        "components": "critical",
        "styling": "high",
        "assets": "medium",
        "interaction": "high",
        "responsive": "high",
        "validation": "medium",
        "source": "low",
    },
    "portfolio": {
        "objective": "critical",
        "container": "high",
        "layout": "critical",
        "content": "critical",
        "components": "critical",
        "styling": "critical",
        "assets": "critical",
        "interaction": "high",
        "responsive": "high",
        "validation": "medium",
        "source": "medium",
    },
    "saas": {
        "objective": "critical",
        "container": "high",
        "layout": "critical",
        "content": "critical",
        "components": "critical",
        "styling": "critical",
        "assets": "high",
        "interaction": "critical",
        "responsive": "critical",
        "validation": "high",
        "source": "low",
    },
    "ecommerce": {
        "objective": "critical",
        "container": "high",
        "layout": "critical",
        "content": "critical",
        "components": "critical",
        "styling": "high",
        "assets": "critical",
        "interaction": "critical",
        "responsive": "critical",
        "validation": "high",
        "source": "medium",
    },
    "component": {
        "objective": "high",
        "container": "low",
        "layout": "medium",
        "content": "medium",
        "components": "critical",
        "styling": "critical",
        "assets": "low",
        "interaction": "critical",
        "responsive": "medium",
        "validation": "high",
        "source": "medium",
    },
}

MCP_TOOLS_BY_SECTION: dict[str, list[str]] = {
    "styling": ["generate_color_palette", "check_wcag_contrast", "calc_type_scale", "calc_spacing_scale"],
    "layout": ["calc_grid", "calc_spacing_scale"],
    "components": ["calc_elevation_shadow", "calc_z_stack", "spec_button", "spec_card"],
    "interaction": ["compute_easing", "suggest_animation_duration"],
    "validation": ["review_ui_quality", "audit_page_structure"],
}

ANTI_PATTERNS_BY_TYPE: dict[str, list[str]] = {
    "landing": [
        "no-adaptive-grid", "static-hero", "generic-loader",
        "missing-spring-physics", "no-brand-watermark",
        "generic-grey", "font-chaos", "inconsistent-spacing",
    ],
    "dashboard": [
        "inconsistent-spacing", "font-chaos", "low-contrast",
        "shadow-abuse", "over-animation",
    ],
    "portfolio": [
        "no-adaptive-grid", "static-hero", "no-brand-watermark",
        "generic-grey", "inconsistent-spacing",
    ],
    "saas": [
        "generic-grey", "font-chaos", "inconsistent-spacing",
        "no-adaptive-grid", "missing-spring-physics",
    ],
}

# ── Default content templates by page type ────────────────────────────────────

LANDING_DEFAULTS: dict[str, Any] = {
    "objective": {
        "tech": "Vanilla HTML/CSS/JS",
        "output": "Single self-contained index.html",
        "libraries": "Lenis smooth-scroll (CDN importmap)",
        "constraints": ["No build step", "No framework", "No placeholder images", "prefers-reduced-motion support"],
        "global": ["WCAG AA contrast", "Semantic HTML", "Keyboard accessible"],
    },
    "container": {
        "shell_max_width": "88rem",
        "centering": "margin-inline: auto",
        "horizontal_padding": {"default": "1.25rem", "sm": "2rem"},
        "adaptive_grid": True,
        "font_base": "16px (vw-scaled)",
    },
    "layout": {
        "desktop": "12-column grid (lg: 1024px+)",
        "tablet": "2-column where applicable (md: 768px+)",
        "mobile": "Single column stack (< 640px)",
        "breakpoints": {"sm": "640px", "md": "768px", "lg": "1024px"},
        "page_shell": ".shell { max-width: 88rem; margin-inline: auto; }",
    },
    "components": {
        "dom_order": [
            "PageLoader (z:120, position:fixed)",
            "Header (z:50, position:absolute/fixed)",
            "main > [sections...]",
            "Footer",
            "NavMenu overlay (z:115, position:fixed)",
            "RequestModal overlay (z:110, position:fixed)",
        ],
        "shared_recipes": [
            "PillButton (dark/light/outline variants + arrow)",
            "Eyebrow (dark/light tone + dot)",
            "TagChip (inline-flex, pill border)",
            "AnimatedLink (translateX spring hover)",
        ],
    },
    "styling": {
        "font_family": "System or Google Fonts — must specify",
        "font_weights": [400, 500, 600, 700],
        "adaptive_grid_css": (
            "@media (max-width:1920px){ html{ font-size:0.833333vw } }\n"
            "@media (max-width:1440px){ html{ font-size:1.111111vw } }\n"
            "@media (max-width:1024px){ html{ font-size:1.5625vw } }\n"
            "@media (max-width:640px){  html{ font-size:4.444444vw } }"
        ),
        "css_reset": (
            "*{ box-sizing:border-box; margin:0; padding:0 }\n"
            "html{ -webkit-font-smoothing:antialiased }\n"
            "body{ overflow-x:hidden }\n"
            "a{ color:inherit; text-decoration:none }\n"
            "button{ font:inherit; color:inherit; background:none; border:none; cursor:pointer }\n"
            "ul{ list-style:none }\n"
            "img{ display:block }\n"
            "@media (prefers-reduced-motion: reduce){ *{ animation:none !important; transition:none !important } }"
        ),
        "scroll_lock_model": (
            "let scrollEnabled = true;\n"
            "function stopScroll() { lenis.stop(); document.documentElement.style.cssText += 'position:relative;overflow:hidden;height:100%'; }\n"
            "function startScroll() { lenis.start(); document.documentElement.style.removeProperty('position'); document.documentElement.style.removeProperty('overflow'); document.documentElement.style.removeProperty('height'); }"
        ),
    },
    "interaction": {
        "smooth_scroll_lib": "Lenis v1.3.23",
        "smooth_scroll_init": (
            "import Lenis from 'lenis';\n"
            "window.scrollTo(0, 0);\n"
            "const lenis = new Lenis({ smoothWheel: true });\n"
            "function raf(t){ lenis.raf(t); requestAnimationFrame(raf); }\n"
            "requestAnimationFrame(raf);"
        ),
        "spring_hover_snappy": "cubic-bezier(.2,.8,.2,1) 350ms   /* {tension:320, friction:18} */",
        "spring_reveal": "cubic-bezier(.22,1,.36,1) 700ms         /* {tension:210, friction:26} */",
        "spring_modal": "cubic-bezier(.34,1.56,.64,1) 600ms       /* {tension:260, friction:30} */",
        "loader_fill_ms": 1300,
        "loader_easing": "easeInOutCubic",
        "canvas_brush_radius": 143,
        "canvas_decay": 0.016,
    },
}


# ── Tool implementations ──────────────────────────────────────────────────────

def generate_ui_prompt(
    page_type: str = "landing",
    intent: str = "A premium design studio landing page",
    sections: list[str] | None = None,
) -> dict:
    """
    Generate a structured 11-section UI design prompt.

    Args:
        page_type: Type of page ("landing", "dashboard", "portfolio", "saas", "ecommerce", "component")
        intent: Brief description of the design intent / brand
        sections: Optional list of section IDs to include (default: all relevant for page_type)

    Returns:
        UIPromptSpec with sections populated with smart defaults and MCP tool requirements.
    """
    page_type = page_type.lower().strip()
    if page_type not in PAGE_TYPE_PRIORITIES:
        page_type = "landing"

    priorities = PAGE_TYPE_PRIORITIES[page_type]
    sections_filter = set(sections) if sections else None

    prompt_sections: list[PromptSection] = []
    for s in ALL_SECTIONS:
        sid = s["id"]
        if sections_filter and sid not in sections_filter:
            continue

        priority = priorities.get(sid, "low")
        # Skip sections explicitly low priority unless explicitly requested
        if priority == "skip":
            continue

        # Pull defaults for this section and page type
        content: dict[str, Any] = {}
        if page_type == "landing" and sid in LANDING_DEFAULTS:
            content = dict(LANDING_DEFAULTS[sid])

        prompt_sections.append(PromptSection(
            id=sid,
            label=s["label"],
            priority=priority,
            filled=bool(content),
            content=content,
        ))

    # Determine required MCP tools
    mcp_tools: list[str] = []
    for sid, tools in MCP_TOOLS_BY_SECTION.items():
        if any(ps.id == sid for ps in prompt_sections):
            mcp_tools.extend(t for t in tools if t not in mcp_tools)

    # Anti-patterns to avoid
    anti_patterns = ANTI_PATTERNS_BY_TYPE.get(page_type, [
        "generic-grey", "font-chaos", "inconsistent-spacing", "low-contrast",
    ])

    # Estimate complexity
    critical_count = sum(1 for ps in prompt_sections if ps.priority == "critical")
    complexity = "premium" if critical_count >= 7 else "complex" if critical_count >= 5 else "medium"

    spec = UIPromptSpec(
        page_type=page_type,
        intent=intent,
        sections=prompt_sections,
        mcp_tools_required=mcp_tools,
        anti_patterns_to_avoid=anti_patterns,
        estimated_complexity=complexity,
    )
    return spec.model_dump()


def validate_ui_prompt(prompt_dict: dict) -> dict:
    """
    Validate a UI design prompt for completeness and quality.

    Checks whether critical sections are filled, identifies missing required information,
    and returns a score + actionable issues.

    Args:
        prompt_dict: A dict matching UIPromptSpec structure (from generate_ui_prompt or manual)

    Returns:
        PromptValidationResult with score, grade, issues, and ready_to_code flag.
    """
    issues: list[PromptValidationIssue] = []
    missing_critical: list[str] = []

    # Extract page_type and sections
    page_type = prompt_dict.get("page_type", "landing")
    intent = str(prompt_dict.get("intent", "")).strip()
    sections_data = prompt_dict.get("sections", [])

    # Build a lookup of provided sections
    section_map: dict[str, dict] = {}
    for s in sections_data:
        sid = s.get("id", "")
        section_map[sid] = s

    priorities = PAGE_TYPE_PRIORITIES.get(page_type, PAGE_TYPE_PRIORITIES["landing"])

    # Check 1: Intent is not empty or too vague
    if not intent or len(intent) < 10:
        issues.append(PromptValidationIssue(
            section_id="objective",
            severity="error",
            message="Intent / design description is missing or too vague (< 10 chars)",
            fix="Provide a clear description: e.g. 'Fintech dashboard with dark mode, high contrast data tables and subtle elevation'",
        ))

    # Check 2: Critical sections must be present and ideally filled
    for sid, priority in priorities.items():
        if priority != "critical":
            continue
        if sid not in section_map:
            missing_critical.append(sid)
            issues.append(PromptValidationIssue(
                section_id=sid,
                severity="error",
                message=f"Critical section '{sid}' is completely missing from prompt",
                fix=f"Add section '{sid}' with relevant data before coding. Run generate_ui_prompt() to get defaults.",
            ))
        else:
            s = section_map[sid]
            if not s.get("filled") and not s.get("content"):
                issues.append(PromptValidationIssue(
                    section_id=sid,
                    severity="warning",
                    message=f"Critical section '{sid}' exists but has no content/data",
                    fix=f"Fill in '{sid}' with specific values. Don't leave it empty — AI will hallucinate.",
                ))

    # Check 3: Styling section must include color tokens check
    if "styling" in section_map:
        styling = section_map["styling"].get("content", {})
        if not styling.get("color_tokens") and not styling.get("colors"):
            issues.append(PromptValidationIssue(
                section_id="styling",
                severity="warning",
                message="No color tokens defined — AI will likely hallucinate generic grey palette",
                fix="Call generate_color_palette() first and add tokens to styling.color_tokens",
            ))

    # Check 4: Interaction section — check for spring config mention
    if page_type in ("landing", "portfolio", "saas"):
        if "interaction" not in section_map:
            issues.append(PromptValidationIssue(
                section_id="interaction",
                severity="warning",
                message="No interaction section — landing pages need spring animations and scroll behavior",
                fix="Add interaction section with: smooth_scroll, spring configs, loader spec, reveal animations",
            ))
        else:
            interaction = section_map["interaction"].get("content", {})
            if not interaction.get("smooth_scroll_lib") and not interaction.get("smooth_scroll"):
                issues.append(PromptValidationIssue(
                    section_id="interaction",
                    severity="info",
                    message="No smooth scroll library specified — default browser scroll will feel generic",
                    fix="Add Lenis: smooth_scroll_lib='Lenis' and the RAF loop initialization",
                ))

    # Check 5: Assets — hero needs images mapped
    if page_type in ("landing", "portfolio"):
        if "assets" not in section_map:
            issues.append(PromptValidationIssue(
                section_id="assets",
                severity="info",
                message="No assets section — hero images will be placeholder or missing",
                fix="Define hero image sources (CDN URLs or local paths) in the assets section",
            ))

    # Compute score
    deductions = {"error": 15, "warning": 7, "info": 3}
    score = 100 - sum(deductions.get(i.severity, 5) for i in issues)
    score = max(0, score)

    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

    if score >= 90:
        summary = "✅ Prompt is comprehensive — AI has enough spec to produce premium UI."
    elif score >= 75:
        summary = "✓ Good prompt — minor gaps, AI may make small assumptions."
    elif score >= 60:
        summary = "⚠ Incomplete prompt — AI will likely hallucinate in several sections."
    else:
        summary = "✗ Insufficient prompt — will produce generic AI UI. Fill critical sections first."

    return PromptValidationResult(
        score=score,
        grade=grade,
        is_valid=score >= 60,
        issues=issues,
        missing_critical=missing_critical,
        summary=summary,
        ready_to_code=score >= 70 and not missing_critical,
    ).model_dump()


def suggest_prompt_sections(page_type: str) -> dict:
    """
    Suggest which of the 11 sections to fill for a given page type,
    with brief explanation of what each section should contain.

    Args:
        page_type: "landing" | "dashboard" | "portfolio" | "saas" | "ecommerce" | "component"

    Returns:
        Dict with section priorities, what to fill, and MCP tools for each.
    """
    page_type = page_type.lower().strip()
    priorities = PAGE_TYPE_PRIORITIES.get(page_type, PAGE_TYPE_PRIORITIES["landing"])

    section_guidance: dict[str, str] = {
        "objective": "Design goal, tech stack, libraries, constraints, global rules (WCAG, motion)",
        "container": "Shell max-width, rem vs px strategy, adaptive grid media queries, overflow handling",
        "layout": "Grid system (12-col?), flex vs grid, responsive breakpoints, section order",
        "content": "Exact copy for all visible text — headings, CTAs, labels, navigation items",
        "components": "Component inventory, DOM order, shared recipes (buttons, cards, eyebrow)",
        "styling": "Color tokens (hex palette), typography scale, spacing scale, CSS variables",
        "assets": "Image URLs or local paths, font CDN links, SVG icons inline/external",
        "interaction": "Scroll lib, spring configs, reveal animations, loader, canvas/hover effects",
        "responsive": "Mobile layout changes, element visibility, typography scaling per breakpoint",
        "validation": "Pre-ship checklist: contrast, accessibility, anti-pattern review",
        "source": "Link to authoritative reference (Figma, live site, screenshots)",
    }

    result = []
    for s in ALL_SECTIONS:
        sid = s["id"]
        priority = priorities.get(sid, "low")
        tools = MCP_TOOLS_BY_SECTION.get(sid, [])
        result.append({
            "id": sid,
            "label": s["label"],
            "priority": priority,
            "what_to_fill": section_guidance.get(sid, ""),
            "mcp_tools": tools,
            "required": priority == "critical",
        })

    return {
        "page_type": page_type,
        "sections": result,
        "critical_count": sum(1 for r in result if r["priority"] == "critical"),
        "tip": (
            f"For a {page_type} page, fill all CRITICAL sections before coding. "
            "Skip LOW priority sections unless you have specific requirements."
        ),
    }


def audit_page_structure(
    sections_present: list[str],
    page_type: str = "landing",
) -> dict:
    """
    Audit whether a page has all recommended UI sections for its type.

    Used to verify a completed page has the right structural elements
    (e.g., a landing page must have: Loader, Header, Hero, About, CTA, Footer).

    Args:
        sections_present: List of section/component names present in the page
        page_type: "landing" | "dashboard" | "portfolio" | "saas" | "ecommerce"

    Returns:
        PageStructureAudit with score and missing sections.
    """
    # Required sections per page type
    REQUIRED_SECTIONS: dict[str, list[str]] = {
        "landing": ["loader", "header", "hero", "about", "footer"],
        "portfolio": ["header", "hero", "work", "footer"],
        "saas": ["header", "hero", "features", "pricing", "footer"],
        "dashboard": ["header", "sidebar", "main-content"],
        "ecommerce": ["header", "hero", "products", "cart", "footer"],
    }
    RECOMMENDED_SECTIONS: dict[str, list[str]] = {
        "landing": ["nav-menu", "request-modal", "services", "stats", "portfolio", "cta"],
        "portfolio": ["case-studies", "about", "contact"],
        "saas": ["testimonials", "cta", "about", "blog"],
        "dashboard": ["stats", "notifications", "search"],
        "ecommerce": ["filters", "wishlist", "search", "checkout"],
    }

    page_type = page_type.lower().strip()
    required = REQUIRED_SECTIONS.get(page_type, REQUIRED_SECTIONS["landing"])
    recommended = RECOMMENDED_SECTIONS.get(page_type, [])

    # Normalize: lowercase, strip
    present_normalized = {s.lower().strip() for s in sections_present}

    issues: list[dict[str, str]] = []
    sections_missing: list[str] = []
    sections_recommended_missing: list[str] = []

    for req in required:
        if not any(req in p or p in req for p in present_normalized):
            sections_missing.append(req)
            issues.append({
                "type": "missing-required",
                "severity": "critical",
                "section": req,
                "fix": f"Add a '{req}' section/component to the page. It's required for {page_type} pages.",
            })

    for rec in recommended:
        if not any(rec in p or p in rec for p in present_normalized):
            sections_recommended_missing.append(rec)
            issues.append({
                "type": "missing-recommended",
                "severity": "warning",
                "section": rec,
                "fix": f"Consider adding a '{rec}' section to improve user experience.",
            })

    # Score: critical missing = -20 each, warning = -5 each
    score = 100
    score -= len(sections_missing) * 20
    score -= len(sections_recommended_missing) * 5
    score = max(0, score)

    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

    if not sections_missing:
        summary = f"✅ All required sections present for {page_type} page. Score: {score}/100."
    else:
        summary = f"⚠ Missing {len(sections_missing)} required section(s): {', '.join(sections_missing)}."

    return PageStructureAudit(
        score=score,
        grade=grade,
        sections_present=list(sections_present),
        sections_missing=sections_missing,
        sections_recommended=sections_recommended_missing,
        issues=issues,
        summary=summary,
    ).model_dump()


# ── Module class ──────────────────────────────────────────────────────────────

class PromptEngineModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="prompt_engine",
            version="1.0.0",
            description=(
                "11-section UI prompt generator and validator. "
                "Helps AI think structurally before coding — prevents hallucinated design decisions."
            ),
            tools=["generate_ui_prompt", "validate_ui_prompt", "suggest_prompt_sections", "audit_page_structure"],
        )

    def health_check(self) -> HealthStatus:
        try:
            # Test generate
            result = generate_ui_prompt("landing", "Test studio", None)
            assert "sections" in result
            assert len(result["sections"]) > 5
            # Test validate
            val = validate_ui_prompt(result)
            assert "score" in val
            assert 0 <= val["score"] <= 100
            # Test audit
            audit = audit_page_structure(["loader", "header", "hero", "footer"], "landing")
            assert "score" in audit
            return HealthStatus(healthy=True, message="OK — prompt_engine v1 ready")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(generate_ui_prompt)
        server.tool()(validate_ui_prompt)
        server.tool()(suggest_prompt_sections)
        server.tool()(audit_page_structure)


MODULE_CLASS = PromptEngineModule
