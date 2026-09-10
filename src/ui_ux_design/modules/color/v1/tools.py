"""modules/color/v1/tools.py — Color module v1.0.0"""

from __future__ import annotations
import colorsys
import math
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.color import (
    ColorToken, Palette, ContrastResult, GradientResult, DarkTokenResult,
)

# ── Pure math helpers ─────────────────────────────────────────────────────────

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def _rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)

def _hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return round(r*255), round(g*255), round(b*255)

def _relative_luminance(r: int, g: int, b: int) -> float:
    def linearize(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)

def _contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = _relative_luminance(*_hex_to_rgb(hex1))
    l2 = _relative_luminance(*_hex_to_rgb(hex2))
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)

def _hue_rotate(hex_color: str, degrees: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    h, s, l = _rgb_to_hsl(r, g, b)
    new_h = (h + degrees) % 360
    nr, ng, nb = _hsl_to_rgb(new_h, s, l)
    return _rgb_to_hex(nr, ng, nb)

def _make_token(hex_color: str, name: str, role: str = "custom") -> ColorToken:
    r, g, b = _hex_to_rgb(hex_color)
    h, s, l = _rgb_to_hsl(r, g, b)
    return ColorToken(hex=hex_color, hsl=f"hsl({h},{s}%,{l}%)", name=name, role=role)

def _ascii_swatch(colors: list[str]) -> str:
    swatches = "  ".join(f"[{c}]" for c in colors)
    return f"▌{swatches}▐"


# ── Tool implementations ──────────────────────────────────────────────────────

def generate_color_palette(base_color: str, scheme: str, steps: int = 5) -> dict:
    """Generate a harmonious HSL-based color palette."""
    base_color = base_color.strip()
    if base_color.startswith("hsl"):
        # Parse hsl(h, s%, l%)
        parts = base_color.replace("hsl(", "").replace(")", "").split(",")
        h, s, l = float(parts[0]), float(parts[1].replace("%","")), float(parts[2].replace("%",""))
        r, g, b = _hsl_to_rgb(h, s, l)
        base_hex = _rgb_to_hex(r, g, b)
    else:
        base_hex = base_color

    scheme_offsets = {
        "monochromatic": [0],
        "complementary": [0, 180],
        "analogous": [0, 30, -30],
        "triadic": [0, 120, 240],
        "split-complementary": [0, 150, 210],
    }
    offsets = scheme_offsets.get(scheme, [0])
    hues = [_hue_rotate(base_hex, off) for off in offsets]

    roles = ["primary", "secondary", "accent", "neutral", "surface"]
    tokens: list[ColorToken] = []
    for i, color in enumerate(hues[:steps]):
        role = roles[i] if i < len(roles) else "custom"
        tokens.append(_make_token(color, f"{scheme}-{i+1}", role))

    css_vars = "\n".join(f"  --color-{t.name}: {t.hex};" for t in tokens)
    palette = Palette(
        colors=tokens,
        css_vars=f":root {{\n{css_vars}\n}}",
        preview_ascii=_ascii_swatch([t.hex for t in tokens]),
        scheme=scheme,
    )
    return palette.model_dump()


def check_wcag_contrast(fg: str, bg: str) -> dict:
    """Check WCAG contrast ratio between two colors."""
    ratio = _contrast_ratio(fg.strip(), bg.strip())
    aa_normal = ratio >= 4.5
    aa_large = ratio >= 3.0
    aaa_normal = ratio >= 7.0

    if aaa_normal:
        grade, rec = "AAA", "Excellent — passes all WCAG levels."
    elif aa_normal:
        grade, rec = "AA", "Good — passes AA for normal text."
    elif aa_large:
        grade, rec = "AA-large", "Marginal — only passes AA for large text (18px+)."
    else:
        grade, rec = "FAIL", f"Insufficient contrast ({ratio}:1). Need ≥4.5 for AA."

    return ContrastResult(
        fg=fg, bg=bg, ratio=ratio,
        AA_normal=aa_normal, AA_large=aa_large, AAA_normal=aaa_normal,
        grade=grade, recommendation=rec,
    ).model_dump()


def generate_dark_tokens(light_tokens: dict[str, str]) -> dict:
    """Convert light-mode hex tokens into dark-mode equivalents."""
    dark = {}
    for name, hex_color in light_tokens.items():
        r, g, b = _hex_to_rgb(hex_color)
        h, s, l = _rgb_to_hsl(r, g, b)
        # Invert lightness: light bg → dark bg, dark text → light text
        new_l = 100 - l
        nr, ng, nb = _hsl_to_rgb(h, s, new_l)
        dark[name] = _rgb_to_hex(nr, ng, nb)
    return DarkTokenResult(
        dark_tokens=dark,
        strategy="Lightness inversion (L → 100-L) in HSL space. Review manually for brand colors.",
    ).model_dump()


def generate_gradient(colors: list[str], angle: int = 135, type: str = "linear") -> dict:
    """Generate a CSS gradient with contrast safety check."""
    if len(colors) < 2:
        colors = colors + ["#ffffff"]
    stops = ", ".join(c.strip() for c in colors[:3])
    if type == "linear":
        css = f"background: linear-gradient({angle}deg, {stops});"
    elif type == "radial":
        css = f"background: radial-gradient(circle, {stops});"
    else:
        css = f"background: conic-gradient(from {angle}deg, {stops});"
    safe = _contrast_ratio(colors[0], colors[-1]) >= 1.5
    return GradientResult(css=css, contrast_safe=safe, type=type, angle=angle).model_dump()


# ── Module class ──────────────────────────────────────────────────────────────

class ColorModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="color", version="1.0.0",
            description="Palette generation, WCAG contrast, dark mode tokens, gradients",
            tools=["generate_color_palette", "check_wcag_contrast",
                   "generate_dark_tokens", "generate_gradient"],
        )

    def health_check(self) -> HealthStatus:
        try:
            result = generate_color_palette("#6C63FF", "complementary", 2)
            assert len(result["colors"]) == 2
            cr = check_wcag_contrast("#ffffff", "#000000")
            assert cr["ratio"] > 20
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(generate_color_palette)
        server.tool()(check_wcag_contrast)
        server.tool()(generate_dark_tokens)
        server.tool()(generate_gradient)


MODULE_CLASS = ColorModule
