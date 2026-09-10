"""modules/depth_25d/v1/tools.py — 2.5D Depth module v1.0.0

Covers: elevation shadows, parallax, z-stack.
Note: elevation + z-stack tools are also in layout module — this module
provides richer 2.5D-specific tools and depth-layer mental models.
"""

from __future__ import annotations

from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.modules.layout.v1.tools import (
    calc_elevation_shadow, calc_z_stack, calc_parallax_offset,
)



def suggest_depth_stack(ui_type: str = "web-app") -> dict:
    """
    Return a recommended depth-layer stack for a given UI type.
    Assigns semantic names + z-index values + elevation levels.
    """
    stacks = {
        "web-app": [
            {"name": "background",   "z": 0,   "elevation": 0, "desc": "Page background / wallpaper"},
            {"name": "content",      "z": 10,  "elevation": 0, "desc": "Main scrollable content"},
            {"name": "sticky-header","z": 100, "elevation": 2, "desc": "Sticky navbar / header"},
            {"name": "dropdown",     "z": 200, "elevation": 3, "desc": "Dropdowns, select menus"},
            {"name": "tooltip",      "z": 300, "elevation": 2, "desc": "Hover tooltips"},
            {"name": "modal-overlay","z": 400, "elevation": 0, "desc": "Dark overlay behind modal"},
            {"name": "modal",        "z": 500, "elevation": 4, "desc": "Dialog / modal content"},
            {"name": "toast",        "z": 600, "elevation": 3, "desc": "Notifications, snackbars"},
        ],
        "game-hud": [
            {"name": "world",        "z": 0,   "elevation": 0, "desc": "3D game world"},
            {"name": "hud-bg",       "z": 10,  "elevation": 0, "desc": "HUD background panels"},
            {"name": "hud-content",  "z": 20,  "elevation": 1, "desc": "Health bars, minimap"},
            {"name": "hud-overlay",  "z": 30,  "elevation": 2, "desc": "Damage flash, effects"},
            {"name": "pause-menu",   "z": 50,  "elevation": 4, "desc": "Pause / inventory screen"},
            {"name": "cutscene",     "z": 100, "elevation": 0, "desc": "Full-screen cutscene"},
        ],
        "landing-page": [
            {"name": "background",   "z": 0,   "elevation": 0, "desc": "Hero background"},
            {"name": "parallax-far", "z": 1,   "elevation": 0, "desc": "Far parallax layer (factor 0.2)"},
            {"name": "parallax-mid", "z": 2,   "elevation": 0, "desc": "Mid parallax (factor 0.5)"},
            {"name": "content",      "z": 10,  "elevation": 0, "desc": "Text and CTAs"},
            {"name": "nav",          "z": 100, "elevation": 2, "desc": "Fixed navigation"},
            {"name": "cookie-banner","z": 200, "elevation": 3, "desc": "Cookie / GDPR banner"},
        ],
    }
    stack = stacks.get(ui_type, stacks["web-app"])
    css_vars = "\n".join(
        f"  --z-{item['name']}: {item['z']};" for item in stack
    )
    return {
        "ui_type": ui_type,
        "layers": stack,
        "css_vars": f":root {{\n{css_vars}\n}}",
        "available_types": list(stacks.keys()),
    }


class Depth25DModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="depth_25d", version="1.0.0",
            description="2.5D depth system: elevation shadows, parallax, z-stack, semantic depth layers",
            tools=["calc_elevation_shadow", "calc_z_stack", "calc_parallax_offset",
                   "suggest_depth_stack"],
        )

    def health_check(self) -> HealthStatus:
        try:
            r = calc_elevation_shadow(3)
            assert r["level"] == 3
            s = suggest_depth_stack("web-app")
            assert len(s["layers"]) > 0
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(suggest_depth_stack)



MODULE_CLASS = Depth25DModule
