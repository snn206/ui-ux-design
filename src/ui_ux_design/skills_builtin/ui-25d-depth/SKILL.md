---
name: ui-25d-depth
description: >
  Kỹ thuật 2.5D: elevation shadows, parallax layers, z-index stacking,
  CSS perspective. Activate khi cần depth, shadows, parallax, layered UI.
  MCP tools: calc_elevation_shadow, calc_z_stack, calc_parallax_offset, suggest_depth_stack.
---

# UI 2.5D Depth System

## Mental Model: Layer Stack

```
z-stack (back → front):

  Layer 0  Background (fixed, no shadow)
  Layer 1  Content plane (normal flow)
  Layer 2  Sticky header        ↑ elevation-2
  Layer 3  Dropdowns, menus     ↑ elevation-3
  Layer 4  Modal overlay (dim)
  Layer 5  Modal content        ↑ elevation-4
  Layer 6  Toasts, alerts       ↑ elevation-3
```

---

## Elevation System (6 levels)

| Level | Use case | Shadow |
|-------|---------|--------|
| 0 | Flat surface, page bg | none |
| 1 | Subtle raised (chip, tag) | `0 1px 3px rgba(0,0,0,0.12)` |
| 2 | Card, panel | `0 2px 8px rgba(0,0,0,0.15)` |
| 3 | Dropdown, popup | `0 4px 16px rgba(0,0,0,0.18)` |
| 4 | Modal, dialog | `0 8px 24px rgba(0,0,0,0.20)` |
| 5 | Bottom sheet, drawer | `0 16px 48px rgba(0,0,0,0.24)` |

**Tool:** `calc_elevation_shadow(level)` → CSS box-shadow

---

## Parallax Layers

```
depth_factor = 0.0 → stationary (background)
depth_factor = 0.2 → slow scroll (far objects)
depth_factor = 0.5 → medium scroll (mid ground)
depth_factor = 1.0 → normal scroll speed
```

**Tool:** `calc_parallax_offset(scroll_y, layers)`

---

## CSS 3D Perspective

```css
/* Parent container */
.scene {
  perspective: 1000px;
  perspective-origin: center center;
}

/* 3D child */
.card-3d {
  transform-style: preserve-3d;
  backface-visibility: hidden;
  transition: transform 400ms ease-in-out;
}
.card-3d:hover { transform: rotateY(180deg); }
```

---

## MCP Tools

```
calc_elevation_shadow(3)          → dropdown shadow CSS
calc_z_stack(["bg","nav","modal"]) → {bg:0, nav:100, modal:500}
calc_parallax_offset(200, layers) → {far: 40px, mid: 100px}
suggest_depth_stack("web-app")    → full z-index system
```
