---
name: ui-3d-scene
description: >
  Kiến trúc 3D scene: scene graph, camera setup, lighting model (3-point),
  PBR materials, Three.js/Babylon.js/Pygame patterns.
  Activate khi task liên quan đến 3D WebGL, game UI, hay CSS 3D transform.
---

# UI 3D Scene Architecture

## Scene Graph Mental Model

```
Scene (World)
  ├── Camera
  │     PerspectiveCamera(fov=60, aspect=16/9, near=0.1, far=1000)
  ├── Lights
  │     ├── AmbientLight(color=0xffffff, intensity=0.3)    ← fill shadows
  │     ├── DirectionalLight(intensity=1.0, pos=[5,10,5])  ← key light
  │     └── PointLight(intensity=0.5, decay=2, dist=50)   ← rim/accent
  └── Group
        ├── Mesh(BoxGeometry, MeshStandardMaterial)
        └── Mesh(SphereGeometry, MeshStandardMaterial)
```

---

## Camera Setup

| Property | Recommended | Notes |
|----------|-------------|-------|
| FOV | 45°–75° | 60° = natural. <45° = telephoto. >75° = fisheye |
| Aspect | `window.innerWidth/Height` | Update on resize |
| Near | 0.1 | Too small → z-fighting |
| Far | 1000 | Too large → precision loss |

**Tool:** `calc_perspective_fov(60, 1.778)` → Three.js camera snippet

---

## 3-Point Lighting (BẮT BUỘC cho scene đẹp)

```
Key Light   → nhìn từ góc 45° trên, mạnh nhất (intensity 1.0)
Fill Light  → phía đối diện Key, mềm hơn (intensity 0.5)
Rim Light   → phía sau đối tượng, tách khỏi background (intensity 0.3)
```

---

## PBR Materials

| Surface | Roughness | Metalness | Notes |
|---------|-----------|-----------|-------|
| Plastic | 0.6 | 0.0 | Matte finish |
| Metal | 0.2 | 1.0 | Reflective |
| Glass | 0.0 | 0.0 | Transparent |
| Rubber | 0.9 | 0.0 | Very matte |
| Ceramic | 0.3 | 0.0 | Slight gloss |
| Wood | 0.8 | 0.0 | Use texture |
| Gold | 0.1 | 1.0 | Warm metal |

**Tool:** `suggest_pbr_material("metal")` → roughness, metalness, Three.js snippet

---

## CSS 3D (Web-based)

```css
.flip-card-inner {
  transform-style: preserve-3d;
  transition: transform 400ms ease-in-out;
}
.flip-card:hover .flip-card-inner { transform: rotateY(180deg); }
.flip-card-back { transform: rotateY(180deg); backface-visibility: hidden; }
```

**Tool:** `calc_perspective_fov(60)` → `perspective: 800px;` CSS

---

## MCP Tools

```
validate_scene_graph(scene)        → issues + score
calc_perspective_fov(60, 1.778)    → Three.js camera
suggest_pbr_material("ceramic")    → PBR params + snippets
```
