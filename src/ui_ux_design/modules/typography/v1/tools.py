"""modules/typography/v1/tools.py — Typography module v1.0.0"""

from __future__ import annotations
import math
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.animation import TypeScale

FONT_PAIRS = {
    "editorial":   {"heading": "Playfair Display", "body": "Source Serif 4"},
    "modern":      {"heading": "Inter",             "body": "Inter"},
    "geometric":   {"heading": "Outfit",            "body": "DM Sans"},
    "humanist":    {"heading": "Nunito",            "body": "Nunito Sans"},
    "technical":   {"heading": "JetBrains Mono",    "body": "IBM Plex Sans"},
    "elegant":     {"heading": "Cormorant Garamond","body": "Lato"},
}

EXPONENT_NAMES = {
    -3: "3xs",
    -2: "2xs",
    -1: "xs",
    0: "base",
    1: "lg",
    2: "xl",
    3: "2xl",
    4: "3xl",
    5: "4xl",
}


def calc_type_scale(
    base_px: int = 16,
    ratio: float = 1.25,
    steps: list[int] | None = None,
    style: str = "modern",
) -> dict:
    """
    Calculate a modular type scale.
    steps: list of exponents relative to base (e.g. [-2,-1,0,1,2,3,4])
    """
    if steps is None:
        steps = [-2, -1, 0, 1, 2, 3, 4]

    scale: dict[str, int] = {}
    for exp in steps:
        size = round(base_px * (ratio ** exp))
        name = EXPONENT_NAMES.get(exp, f"step-{exp}")
        scale[name] = max(size, 10)


    # Line heights: larger text needs tighter leading
    line_heights: dict[str, float] = {}
    for name, size in scale.items():
        if size >= 48:
            lh = 1.1
        elif size >= 32:
            lh = 1.2
        elif size >= 20:
            lh = 1.35
        else:
            lh = 1.6
        line_heights[name] = lh

    # Letter spacing: large headings benefit from tighter tracking
    letter_spacings: dict[str, str] = {}
    for name, size in scale.items():
        if size >= 48:
            ls = "-0.03em"
        elif size >= 32:
            ls = "-0.02em"
        elif size >= 20:
            ls = "-0.01em"
        else:
            ls = "0em"
        letter_spacings[name] = ls

    css_vars = ":root {\n" + "\n".join(
        f"  --text-{k}: {v}px;" for k, v in scale.items()
    ) + "\n}"
    pair = FONT_PAIRS.get(style, FONT_PAIRS["modern"])

    return TypeScale(
        scale=scale,
        css_vars=css_vars,
        line_heights=line_heights,
        letter_spacings=letter_spacings,
        font_pair_suggestion=pair,
    ).model_dump()


def suggest_font_pair(style: str = "modern") -> dict:
    """Suggest a Google Fonts pair based on design style."""
    pair = FONT_PAIRS.get(style, FONT_PAIRS["modern"])
    import_url = (
        f"https://fonts.googleapis.com/css2?"
        f"family={pair['heading'].replace(' ', '+')}:wght@400;600;700"
        f"&family={pair['body'].replace(' ', '+')}:wght@400;500"
        f"&display=swap"
    )
    css = (
        f"font-family: '{pair['heading']}', sans-serif; /* headings */\n"
        f"font-family: '{pair['body']}', sans-serif;    /* body */"
    )
    return {
        "style": style,
        "heading_font": pair["heading"],
        "body_font": pair["body"],
        "google_fonts_url": import_url,
        "css_snippet": css,
        "available_styles": list(FONT_PAIRS.keys()),
    }


class TypographyModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="typography", version="1.0.0",
            description="Modular type scale, line heights, letter spacing, font pair suggestions",
            tools=["calc_type_scale", "suggest_font_pair"],
        )

    def health_check(self) -> HealthStatus:
        try:
            r = calc_type_scale(16, 1.25)
            assert "base" in r["scale"]
            assert r["scale"]["base"] == 16
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(calc_type_scale)
        server.tool()(suggest_font_pair)


MODULE_CLASS = TypographyModule
