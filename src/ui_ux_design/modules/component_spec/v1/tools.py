"""modules/component_spec/v1/tools.py — Component Spec module v1.0.0

Tools for generating precise CSS/JS token specifications for UI components.
Bridges the gap between design intent and exact implementation — prevents AI from
guessing component values (padding, spring, radius, etc.).
"""

from __future__ import annotations
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.component import (
    ButtonSpec, CardSpec, HeroSpec, LoaderSpec, ComponentSpecResult,
)

# ── Spring → CSS mapping ──────────────────────────────────────────────────────

SPRING_PRESETS: dict[str, tuple[str, int]] = {
    # name → (cubic-bezier, duration_ms)
    "snappy-hover":   ("cubic-bezier(.2,.8,.2,1)",   350),   # {tension:320, friction:18}
    "smooth-reveal":  ("cubic-bezier(.22,1,.36,1)",  700),   # {tension:210, friction:26}
    "modal-enter":    ("cubic-bezier(.34,1.56,.64,1)", 600), # {tension:260, friction:30} — slight overshoot
    "card-hover":     ("cubic-bezier(.25,1,.5,1)",   500),   # {tension:260, friction:22}
    "service-fill":   ("cubic-bezier(.3,.7,.3,1)",   400),   # {tension:240, friction:26}
    "link-lift":      ("cubic-bezier(.2,.8,.2,1)",   300),   # {tension:320, friction:22}
    "logo-scale":     ("cubic-bezier(.2,.8,.2,1)",   350),   # {tension:320, friction:18}
    "nav-stagger":    ("cubic-bezier(.4,0,.2,1)",    500),   # standard material
    "loader-exit":    ("cubic-bezier(.22,1,.36,1)",  700),   # same as reveal
    "carousel-swap":  ("cubic-bezier(.25,1,.5,1)",   500),   # {tension:300, friction:28}
}

# ── Shared token values (Studio-grade design system defaults) ──────────────────

DEFAULT_TOKENS: dict[str, str] = {
    "--bg": "#ffffff",
    "--fg": "#111111",
    "--ink": "#0a0a0a",
    "--muted": "#8d8d8d",
    "--subtle": "#b6b6b6",
    "--line": "#e6e5e2",
    "--surface": "#f1f0ee",
    "--surface-2": "#e3e2df",
    "--accent": "#b15f2c",
    "--accent-from": "#cf8047",
    "--accent-to": "#97501f",
    "--radius-pill": "9999px",
    "--radius-card": "2rem",
    "--radius-card-sm": "1.25rem",
    "--radius-control": "0.875rem",
    "--shell": "88rem",
    "--watermark": "13rem",
}

ADAPTIVE_GRID_CSS = (
    "@media (max-width:1920px){ html{ font-size:0.833333vw } }\n"
    "@media (max-width:1440px){ html{ font-size:1.111111vw } }\n"
    "@media (max-width:1024px){ html{ font-size:1.5625vw } }\n"
    "@media (max-width:640px){  html{ font-size:4.444444vw } }"
)


# ── Tool implementations ──────────────────────────────────────────────────────

def spec_button(
    variant: str = "dark",
    size: str = "md",
    with_arrow: bool = True,
    arrow_direction: str = "right",
) -> dict:
    """
    Generate complete CSS token specification for a PillButton component.

    Args:
        variant: "dark" | "light" | "outline"
        size: "sm" | "md" | "lg"
        with_arrow: Whether to include the arrow badge
        arrow_direction: "right" | "up-right"

    Returns:
        ButtonSpec with full CSS, spring config, and usage example.
    """
    variant = variant.lower()
    size = size.lower()

    # Size scale
    size_map = {
        "sm":  {"font_size": "0.75rem",  "font_weight": "500"},
        "md":  {"font_size": "0.875rem", "font_weight": "500"},
        "lg":  {"font_size": "1rem",     "font_weight": "600"},
    }
    sz = size_map.get(size, size_map["md"])

    # Padding: with_arrow has special structure
    if with_arrow:
        padding = "0.375rem 0.375rem 0.375rem 1.5rem"  # py-1.5 pl-6 pr-1.5
    else:
        padding = {"sm": "0.625rem 1.25rem", "md": "0.875rem 1.75rem", "lg": "1rem 2rem"}.get(size, "0.875rem 1.75rem")

    # Variant styles
    variant_map = {
        "dark":    {"background": "#0a0a0a", "color": "#ffffff", "badge_bg": "#ffffff", "badge_color": "#0a0a0a", "border": "none"},
        "light":   {"background": "#f1f0ee", "color": "#111111", "badge_bg": "#0a0a0a", "badge_color": "#ffffff", "border": "none"},
        "outline": {"background": "transparent", "color": "#111111", "badge_bg": "#0a0a0a", "badge_color": "#ffffff", "border": "1px solid #e6e5e2"},
    }
    v = variant_map.get(variant, variant_map["dark"])

    spring, duration_ms = SPRING_PRESETS["snappy-hover"]
    arrow_icon = "ArrowUpRight" if arrow_direction == "up-right" else "ArrowRight"
    arrow_transform = "translate(2px,-2px)" if arrow_direction == "up-right" else "translate(3px,0)"

    css = f""".pill-btn {{
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  border-radius: 9999px;
  padding: {padding};
  font-size: {sz['font_size']};
  font-weight: {sz['font_weight']};
  background: {v['background']};
  color: {v['color']};
  border: {v.get('border', 'none')};
  transition: transform {duration_ms}ms {spring};
  cursor: pointer;
}}
.pill-btn:hover {{ transform: scale(1.04); }}
.pill-btn__badge {{
  width: 2.25rem;
  height: 2.25rem;
  display: grid;
  place-items: center;
  border-radius: 9999px;
  background: {v['badge_bg']};
  color: {v['badge_color']};
  font-size: 1rem;
  transition: transform {duration_ms}ms {spring};
}}
.pill-btn:hover .pill-btn__badge {{ transform: {arrow_transform}; }}"""

    usage = (
        f'<button class="pill-btn" type="button">\n'
        f'  <span>Let\'s Talk</span>\n'
        f'  <span class="pill-btn__badge">{arrow_icon} SVG</span>\n'
        f'</button>'
    )

    spec = ButtonSpec(
        variant=variant,
        size=size,
        with_arrow=with_arrow,
        arrow_direction=arrow_direction,
        css=css,
        hover_spring=spring,
        hover_duration_ms=duration_ms,
        padding=padding,
        border_radius="9999px",
        font_size=sz["font_size"],
        font_weight=sz["font_weight"],
        background=v["background"],
        color=v["color"],
        badge_bg=v.get("badge_bg"),
        badge_color=v.get("badge_color"),
    )

    return ComponentSpecResult(
        component_type="button",
        spec=spec.model_dump(),
        css_tokens={
            "--btn-bg": v["background"],
            "--btn-color": v["color"],
            "--btn-radius": "9999px",
            "--btn-padding": padding,
            "--btn-hover-spring": f"{spring} {duration_ms}ms",
        },
        usage_example=usage,
    ).model_dump()


def spec_card(
    type: str = "portfolio",
    background: str = "#0a0a0a",
    radius: str = "2rem",
) -> dict:
    """
    Generate complete CSS token specification for a Card component.

    Args:
        type: "portfolio" | "feature" | "stat" | "hero" | "service"
        background: CSS background color or value
        radius: Border radius (e.g. "2rem", "1.25rem")

    Returns:
        CardSpec with hover animation, shadows, and usage example.
    """
    type = type.lower()

    # Type-specific defaults
    type_map = {
        "portfolio": {
            "padding": "1.5rem",
            "padding_sm": "2rem",
            "min_height": "22rem",
            "min_height_sm": "26rem",
            "hover_transform": "translateY(-8px) scale(1.012)",
            "spring": "card-hover",
            "box_shadow": "0 1px 0 0 rgba(255,255,255,.05) inset",  # ring effect
            "color": "#ffffff",
            "overflow": "hidden",
        },
        "feature": {
            "padding": "1.5rem",
            "padding_sm": "2rem",
            "min_height": "14rem",
            "hover_transform": "translateY(-4px)",
            "spring": "card-hover",
            "box_shadow": "0 4px 24px rgba(0,0,0,.06)",
            "color": "#111111",
            "overflow": "hidden",
        },
        "stat": {
            "padding": "3rem 1.5rem",
            "padding_sm": "4rem 2rem",
            "min_height": "auto",
            "hover_transform": "none",
            "spring": "smooth-reveal",
            "box_shadow": "none",
            "color": "#ffffff",
            "overflow": "visible",
        },
        "hero": {
            "padding": "0.5rem",
            "padding_sm": "0.5rem",
            "min_height": "auto",
            "hover_transform": "none",
            "spring": "smooth-reveal",
            "box_shadow": "0 2px 16px rgba(0,0,0,.08)",
            "color": "#111111",
            "overflow": "hidden",
        },
    }
    t = type_map.get(type, type_map["portfolio"])
    spring_name = t["spring"]
    spring_curve, spring_ms = SPRING_PRESETS.get(spring_name, SPRING_PRESETS["card-hover"])

    is_dark = background in ("#0a0a0a", "#111111", "#1a1a1a")

    css = f""".card-{type} {{
  position: relative;
  min-height: {t['min_height']};
  overflow: {t['overflow']};
  border-radius: {radius};
  background: {background};
  padding: {t['padding']};
  color: {t['color']};
  box-shadow: {t['box_shadow']};
  transition: transform {spring_ms}ms {spring_curve};
  cursor: pointer;
}}
@media (min-width: 640px) {{
  .card-{type} {{
    min-height: {t.get('min_height_sm', t['min_height'])};
    padding: {t.get('padding_sm', t['padding'])};
  }}
}}
.card-{type}:hover {{
  transform: {t['hover_transform']};
}}"""

    usage = (
        f'<article class="card-{type}" role="article">\n'
        f'  <!-- Card content -->\n'
        f'</article>'
    )

    spec = CardSpec(
        type=type,
        background=background,
        padding=t["padding"],
        border_radius=radius,
        min_height=t["min_height"],
        box_shadow=t["box_shadow"],
        hover_transform=t["hover_transform"],
        hover_spring=spring_curve,
        hover_duration_ms=spring_ms,
        css=css,
    )

    return ComponentSpecResult(
        component_type="card",
        spec=spec.model_dump(),
        css_tokens={
            "--card-bg": background,
            "--card-radius": radius,
            "--card-padding": t["padding"],
            "--card-hover": t["hover_transform"],
            "--card-spring": f"{spring_curve} {spring_ms}ms",
        },
        usage_example=usage,
    ).model_dump()


def spec_hero(
    layout: str = "fullbleed",
    has_canvas_effect: bool = True,
    has_watermark: bool = True,
    brand_name: str = "BRAND",
) -> dict:
    """
    Generate Hero section specification including canvas effect, watermark, and grid.

    Args:
        layout: "fullbleed" | "split" | "centered"
        has_canvas_effect: Whether to include the liquid canvas brush reveal effect
        has_watermark: Whether to include an oversized brand watermark
        brand_name: Text for the watermark (uppercase)

    Returns:
        HeroSpec with CSS, canvas params, and adaptive grid.
    """
    layout = layout.lower()

    grid_css = ""
    if layout == "fullbleed":
        grid_css = (
            ".hero-content {\n"
            "  position: relative;\n"
            "  z-index: 20;\n"
            "  display: flex;\n"
            "  flex-direction: column;\n"
            "  gap: 2rem;\n"
            "  padding: 7rem 1.25rem 5rem;\n"
            "}\n"
            "@media (min-width: 640px) { .hero-content { padding-inline: 2rem; } }\n"
            "@media (min-width: 1024px) {\n"
            "  .hero-content {\n"
            "    display: grid;\n"
            "    min-height: 100lvh;\n"
            "    grid-template-columns: repeat(12, 1fr);\n"
            "    gap: 2.5rem;\n"
            "    padding: 9rem 2rem 7rem;\n"
            "  }\n"
            "  .hero-left { grid-column: span 7; }\n"
            "  .hero-right { grid-column: span 5; }\n"
            "}"
        )
    elif layout == "split":
        grid_css = (
            ".hero-content {\n"
            "  display: grid;\n"
            "  grid-template-columns: 1fr;\n"
            "  gap: 3rem;\n"
            "  padding: 6rem 1.25rem 4rem;\n"
            "}\n"
            "@media (min-width: 1024px) {\n"
            "  .hero-content { grid-template-columns: 1fr 1fr; }\n"
            "}"
        )
    else:  # centered
        grid_css = (
            ".hero-content {\n"
            "  display: flex;\n"
            "  flex-direction: column;\n"
            "  align-items: center;\n"
            "  text-align: center;\n"
            "  gap: 2rem;\n"
            "  padding: 8rem 1.25rem 6rem;\n"
            "}"
        )

    canvas_snippet = ""
    if has_canvas_effect:
        canvas_snippet = (
            "// LiquidReveal Canvas Effect\n"
            "const brushRadius = 143;  // CSS px\n"
            "const decay = 0.016;      // per-frame alpha reduction\n"
            "const dpr = Math.min(devicePixelRatio, 2);\n"
            "// canvas = full-bleed absolute, pointer-events: none\n"
            "// Use offscreen canvas for cover image (source-in masking)\n"
            "// Brush gradient: addColorStop(0, rgba(255,255,255,1)), addColorStop(0.55, rgba(255,255,255,0.82)), addColorStop(1, rgba(255,255,255,0))\n"
            "// Idle > 120 frames → clearRect (full hard reset)\n"
            "// prefers-reduced-motion → skip canvas entirely\n"
        )

    watermark_css = ""
    if has_watermark:
        watermark_css = (
            f".hero-watermark {{\n"
            f"  pointer-events: none;\n"
            f"  position: absolute;\n"
            f"  inset-inline: 0;\n"
            f"  bottom: 7rem;\n"
            f"  z-index: 1;\n"
            f"  text-align: center;\n"
            f"  user-select: none;\n"
            f"  font-weight: 700;\n"
            f"  line-height: 1;\n"
            f"  font-size: 13rem;  /* var(--watermark) */\n"
            f"  color: rgba(255,255,255,0.4);\n"
            f"}}\n"
            f"/* Reveal: opacity 0→0.4, translateY(20px→0), delay 300ms */\n"
        )

    css = (
        ".hero {\n"
        "  position: relative;\n"
        "  isolation: isolate;\n"
        "  overflow: hidden;\n"
        "  border-radius: 0 0 2rem 2rem;\n"
        "  background: #c9c9c9;  /* hero-to token */\n"
        "}\n"
        ".hero-bg {\n"
        "  position: absolute;\n"
        "  inset: 0;\n"
        "  z-index: 0;\n"
        "}\n"
        ".hero-bg img {\n"
        "  object-fit: cover;\n"
        "  position: absolute;\n"
        "  inset: 0;\n"
        "  width: 100%;\n"
        "  height: 100%;\n"
        "}\n"
        ".hero-vignette {\n"
        "  position: absolute;\n"
        "  inset: 0;\n"
        "  z-index: 1;\n"
        "  pointer-events: none;\n"
        "  background: linear-gradient(to bottom, rgba(255,255,255,.35), transparent, rgba(255,255,255,.35));\n"
        "}\n"
        + (watermark_css or "")
        + grid_css
    )

    spec = HeroSpec(
        layout=layout,
        has_canvas_effect=has_canvas_effect,
        has_watermark=has_watermark,
        has_loader_gate=True,
        background="#c9c9c9",
        canvas_brush_radius=143 if has_canvas_effect else None,
        canvas_decay=0.016 if has_canvas_effect else None,
        watermark_text=brand_name.upper() if has_watermark else None,
        watermark_font_size="13rem" if has_watermark else None,
        watermark_color="rgba(255,255,255,0.4)" if has_watermark else None,
        adaptive_grid_css=ADAPTIVE_GRID_CSS,
        css=css,
    )

    return ComponentSpecResult(
        component_type="hero",
        spec=spec.model_dump(),
        css_tokens={
            "--hero-bg": "#c9c9c9",
            "--hero-watermark-size": "13rem",
            "--hero-watermark-color": "rgba(255,255,255,0.4)",
            "--hero-radius": "0 0 2rem 2rem",
        },
        usage_example=(
            '<section id="home" class="hero">\n'
            '  <div class="hero-bg">\n'
            '    <img src="hero/after.jpg" alt="" aria-hidden="true" />\n'
            '    <canvas aria-hidden="true"></canvas>  <!-- canvas effect -->\n'
            '  </div>\n'
            '  <div class="hero-vignette" aria-hidden="true"></div>\n'
            + (f'  <p class="hero-watermark" aria-hidden="true">{brand_name.upper()}</p>\n' if has_watermark else "")
            + '  <div class="shell hero-content">\n'
            '    <!-- hero columns -->\n'
            '  </div>\n'
            '</section>'
        ),
    ).model_dump()


def spec_loader(
    style: str = "branded",
    duration_ms: int = 1300,
    background: str = "#0a0a0a",
    accent: str = "#cf8047",
    brand_name: str = "Studio",
    tagline: str = "Bold ideas, shipped with quiet precision.",
) -> dict:
    """
    Generate specification for a branded page loader component.

    Args:
        style: "branded" | "minimal" | "progress-only"
        duration_ms: How long the 0→100 count takes (default 1300ms)
        background: Loader background color
        accent: Progress bar and logo accent color
        brand_name: Brand name to display
        tagline: Tagline text below brand name

    Returns:
        LoaderSpec with CSS and JS snippet.
    """
    style = style.lower()
    spring_curve, spring_ms = SPRING_PRESETS["loader-exit"]

    css = f""".page-loader {{
  position: fixed;
  inset: 0;
  z-index: 120;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  background: {background};
  color: #fff;
  border-radius: 0 0 2rem 2rem;  /* rounded bottom */
}}
.page-loader__brand {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #fff;
}}
.page-loader__brand .logo {{ color: {accent}; font-size: 1.875rem; }}
.page-loader__tagline {{
  max-width: 24ch;
  font-size: 0.875rem;
  color: rgba(255,255,255,.55);
  text-align: center;
}}
.page-loader__progress {{
  width: min(22rem, 72vw);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}}
.page-loader__track {{
  height: 1px;
  background: rgba(255,255,255,.15);
  border-radius: 9999px;
}}
.page-loader__fill {{
  height: 100%;
  background: {accent};
  border-radius: 9999px;
  width: 0%;
  transition: width 0.1s ease-out;
}}
.page-loader__meta {{
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(255,255,255,.45);
}}
.page-loader__counter {{
  font-variant-numeric: tabular-nums;
  color: rgba(255,255,255,.8);
}}
/* Exit animation */
.page-loader.exiting {{
  transform: translateY(-100%);
  transition: transform {spring_ms}ms {spring_curve};
}}
.page-loader.exiting .page-loader__brand,
.page-loader.exiting .page-loader__tagline {{
  opacity: 0;
  transform: translateY(-12px);
  transition: opacity 0.3s ease-out, transform 0.3s ease-out;
}}"""

    js_snippet = f"""// Page Loader — Branded counter
const FILL_MS = {duration_ms};
const loader = document.querySelector('.page-loader');
const fill = loader.querySelector('.page-loader__fill');
const counter = loader.querySelector('.page-loader__counter');

function easeInOutCubic(t) {{
  return t < .5 ? 4*t*t*t : 1-((-2*t+2)**3)/2;
}}

let start = null;
function animateLoader(ts) {{
  if (!start) start = ts;
  const t = Math.min((ts - start) / FILL_MS, 1);
  const progress = Math.round(easeInOutCubic(t) * 100);
  fill.style.width = progress + '%';
  counter.textContent = String(progress).padStart(3, '0');
  if (t < 1) {{
    requestAnimationFrame(animateLoader);
  }} else {{
    // Exit
    loader.classList.add('exiting');
    setTimeout(() => {{
      loader.remove();
      startScroll();
      ready = true;  // gate flag for hero reveals
      playHeroReveals();
    }}, {spring_ms});
  }}
}}
stopScroll();
requestAnimationFrame(animateLoader);"""

    spec = LoaderSpec(
        style=style,
        fill_ms=duration_ms,
        background=background,
        foreground="#ffffff",
        accent=accent,
        has_counter=True,
        counter_padding=3,
        exit_transform="translateY(-100%)",
        exit_spring=spring_curve,
        exit_duration_ms=spring_ms,
        css=css,
        js_snippet=js_snippet,
    )

    return ComponentSpecResult(
        component_type="loader",
        spec=spec.model_dump(),
        css_tokens={
            "--loader-bg": background,
            "--loader-accent": accent,
            "--loader-z": "120",
            "--loader-exit-spring": f"{spring_curve} {spring_ms}ms",
        },
        usage_example=(
            '<div class="page-loader" role="status" aria-label="Loading">\n'
            '  <div class="page-loader__brand">\n'
            '    <span class="logo"><!-- LogoMark SVG --></span>\n'
            f'    <span>{brand_name}</span>\n'
            '  </div>\n'
            f'  <p class="page-loader__tagline">{tagline}</p>\n'
            '  <div class="page-loader__progress">\n'
            '    <div class="page-loader__track"><div class="page-loader__fill"></div></div>\n'
            '    <div class="page-loader__meta">\n'
            '      <span>Loading</span>\n'
            '      <span class="page-loader__counter">000</span>\n'
            '    </div>\n'
            '  </div>\n'
            '</div>'
        ),
    ).model_dump()


# ── Module class ──────────────────────────────────────────────────────────────

class ComponentSpecModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="component_spec",
            version="1.0.0",
            description=(
                "Generate precise CSS/JS token specs for UI components. "
                "Prevents AI from guessing padding, spring configs, radii, colors. "
                "Tools: spec_button, spec_card, spec_hero, spec_loader."
            ),
            tools=["spec_button", "spec_card", "spec_hero", "spec_loader"],
        )

    def health_check(self) -> HealthStatus:
        try:
            btn = spec_button("dark", "md", True, "right")
            assert "spec" in btn and "css_tokens" in btn

            card = spec_card("portfolio", "#0a0a0a", "2rem")
            assert "spec" in card

            hero = spec_hero("fullbleed", True, True, "TEST")
            assert "spec" in hero

            loader = spec_loader("branded", 1300)
            assert "js_snippet" in loader["spec"]

            return HealthStatus(healthy=True, message="OK — component_spec v1 ready")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(spec_button)
        server.tool()(spec_card)
        server.tool()(spec_hero)
        server.tool()(spec_loader)


MODULE_CLASS = ComponentSpecModule
