"""modules/scene_3d/v1/tools.py — 3D Scene module v1.0.0"""

from __future__ import annotations
import math
from typing import Any

from ui_ux_design.module_base import MCPModule, ModuleInfo, HealthStatus
from ui_ux_design.models.scene import PBRMaterial, PerspectiveResult, SceneValidation

# ── PBR Surface presets ───────────────────────────────────────────────────────

PBR_PRESETS: dict[str, dict] = {
    "plastic":   {"roughness": 0.6, "metalness": 0.0, "color": "#E8E8F0", "notes": "Matte plastic, slight sheen"},
    "metal":     {"roughness": 0.2, "metalness": 1.0, "color": "#B8C0CC", "notes": "Reflective metal"},
    "brushed-metal": {"roughness": 0.5, "metalness": 1.0, "color": "#A0A8B0", "notes": "Brushed aluminium"},
    "glass":     {"roughness": 0.0, "metalness": 0.0, "color": "#C8E6FF", "notes": "Transparent — set opacity < 0.3"},
    "rubber":    {"roughness": 0.9, "metalness": 0.0, "color": "#333333", "notes": "Very matte, absorbs light"},
    "ceramic":   {"roughness": 0.3, "metalness": 0.0, "color": "#F5F0EB", "notes": "Slight gloss, white-ish"},
    "wood":      {"roughness": 0.8, "metalness": 0.0, "color": "#A0522D", "notes": "Use texture map for grain"},
    "concrete":  {"roughness": 0.95, "metalness": 0.0, "color": "#9E9E9E", "notes": "Very rough, cold grey"},
    "gold":      {"roughness": 0.1, "metalness": 1.0, "color": "#FFD700", "notes": "Highly reflective warm metal"},
    "fabric":    {"roughness": 1.0, "metalness": 0.0, "color": "#6B5B95", "notes": "No reflection, soft surface"},
}


def suggest_pbr_material(surface_type: str) -> dict:
    """Return PBR parameters for a given surface type."""
    preset = PBR_PRESETS.get(surface_type.lower(), PBR_PRESETS["plastic"])
    r, m = preset["roughness"], preset["metalness"]

    threejs = (
        f"new THREE.MeshStandardMaterial({{\n"
        f"  color: '{preset['color']}',\n"
        f"  roughness: {r},\n"
        f"  metalness: {m},\n"
        f"}});"
    )
    babylonjs = (
        f"mat.roughness = {r};\n"
        f"mat.metallic = {m};\n"
        f"mat.albedoColor = BABYLON.Color3.FromHexString('{preset['color']}');"
    )
    available = list(PBR_PRESETS.keys())
    return PBRMaterial(
        surface_type=surface_type,
        roughness=r,
        metalness=m,
        color_suggestion=preset["color"],
        threejs_snippet=threejs,
        babylonjs_snippet=babylonjs,
        notes=f"{preset['notes']}. Available: {', '.join(available)}",
    ).model_dump()


def calc_perspective_fov(
    fov_deg: float = 60.0,
    aspect_ratio: float = 1.7778,  # 16:9
    near: float = 0.1,
    far: float = 1000.0,
) -> dict:
    """Calculate perspective projection parameters for CSS and Three.js."""
    fov_rad = math.radians(fov_deg)
    # CSS perspective distance that approximates the FOV
    perspective_px = round(1 / math.tan(fov_rad / 2) * 500)

    threejs = (
        f"const camera = new THREE.PerspectiveCamera(\n"
        f"  {fov_deg},        // fov\n"
        f"  {aspect_ratio:.4f}, // aspect (window.innerWidth/Height)\n"
        f"  {near},           // near\n"
        f"  {far}             // far\n"
        f");"
    )
    css_3d = (
        f"/* Apply to parent container */\n"
        f"perspective: {perspective_px}px;\n"
        f"perspective-origin: center center;\n"
        f"\n/* Apply to 3D element */\n"
        f"transform-style: preserve-3d;\n"
        f"backface-visibility: hidden;"
    )
    return PerspectiveResult(
        fov_deg=fov_deg,
        aspect_ratio=aspect_ratio,
        perspective_css=f"perspective: {perspective_px}px;",
        projection_info={
            "near": near, "far": far,
            "fov_rad": round(fov_rad, 4),
            "perspective_px": perspective_px,
        },
        threejs_snippet=threejs,
        css_3d_snippet=css_3d,
    ).model_dump()


def validate_scene_graph(scene: dict) -> dict:
    """
    Validate a 3D scene graph structure.
    scene: {camera: {...}, lights: [...], objects: [...]}
    """
    issues: list[str] = []
    suggestions: list[str] = []
    score = 100

    camera = scene.get("camera", {})
    lights = scene.get("lights", [])
    objects = scene.get("objects", [])

    has_camera = bool(camera)
    light_count = len(lights)
    object_count = len(objects)

    # Camera checks
    if not has_camera:
        issues.append("No camera defined — scene will not render")
        suggestions.append("Add a PerspectiveCamera (FOV 60°, aspect 16:9)")
        score -= 30
    else:
        fov = camera.get("fov", 0)
        if fov < 30 or fov > 90:
            issues.append(f"Camera FOV={fov}° is unusual. Recommended: 45–75°")
            score -= 10

    # Light checks
    if light_count == 0:
        issues.append("No lights — scene will be completely dark (unless emissive materials)")
        suggestions.append("Add AmbientLight(0.3) + DirectionalLight(1.0) at minimum")
        score -= 25
    elif light_count == 1:
        suggestions.append("Consider 3-point lighting: Key(1.0) + Fill(0.5) + Rim(0.3)")
    else:
        light_types = [l.get("type", "") for l in lights]
        if "AmbientLight" not in light_types and "ambient" not in light_types:
            suggestions.append("No ambient light — add low-intensity AmbientLight to soften shadows")

    # Object checks
    if object_count == 0:
        issues.append("No objects in scene")
        score -= 20
    else:
        # Check for missing materials
        no_mat = [o.get("name", f"obj{i}") for i, o in enumerate(objects) if not o.get("material")]
        if no_mat:
            issues.append(f"Objects without material: {no_mat[:3]}")
            suggestions.append("Assign MeshStandardMaterial (PBR) to all objects")
            score -= 5 * min(len(no_mat), 4)

    return SceneValidation(
        valid=len([i for i in issues if "will not render" in i or "dark" in i]) == 0,
        score=max(score, 0),
        issues=issues,
        suggestions=suggestions,
        light_count=light_count,
        has_camera=has_camera,
        object_count=object_count,
    ).model_dump()


class Scene3DModule(MCPModule):

    @property
    def info(self) -> ModuleInfo:
        return ModuleInfo(
            name="scene_3d", version="1.0.0",
            description="3D scene validation, PBR material suggestions, perspective/FOV calculator",
            tools=["suggest_pbr_material", "calc_perspective_fov", "validate_scene_graph"],
        )

    def health_check(self) -> HealthStatus:
        try:
            r = suggest_pbr_material("metal")
            assert r["metalness"] == 1.0
            p = calc_perspective_fov(60)
            assert "perspective" in p["perspective_css"]
            return HealthStatus(healthy=True, message="OK")
        except Exception as e:
            return HealthStatus(healthy=False, message=str(e))

    def register_tools(self, server: Any) -> None:
        server.tool()(suggest_pbr_material)
        server.tool()(calc_perspective_fov)
        server.tool()(validate_scene_graph)


MODULE_CLASS = Scene3DModule
