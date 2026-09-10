---
name: ui-animation
description: >
  Motion design: Disney 12 principles, easing curves, spring physics,
  duration guidelines, CSS vs JS animation decision.
  Activate khi task có animation, transition, hay motion.
  MCP tools: compute_easing, suggest_animation_duration.
---

# UI Animation & Motion Design

## Disney 12 Principles → UI

| Principle | UI Application |
|-----------|---------------|
| **Ease In/Out** | Tất cả transitions — KHÔNG dùng linear |
| **Anticipation** | Hover state chuẩn bị cho action |
| **Staging** | Entrance animations: element quan trọng animate trước |
| **Squash & Stretch** | Button press scale (0.95 on press) |
| **Secondary Action** | Loading spinner trong button |
| **Timing** | Duration theo khoảng cách di chuyển |

---

## Duration Guidelines (BẮT BUỘC)

| Loại | Duration | Easing | Ví dụ |
|------|----------|--------|-------|
| Micro | 100–150ms | ease-out | Icon swap, toggle |
| Small | 150–250ms | ease-in-out | Tooltip, dropdown |
| Medium | 250–400ms | Material standard | Modal, drawer |
| Large | 400–600ms | spring | Page transition |
| 3D | 300–500ms | ease-in-out | Card flip, rotate |

---

## Easing Curves

```
ease-out    → Bắt đầu nhanh, kết thúc chậm (element enters screen)
ease-in     → Bắt đầu chậm, kết thúc nhanh (element leaves screen)
ease-in-out → Cân bằng (element moves within screen)
spring      → Overshoot một chút (natural, alive feeling)
linear      → ❌ Chỉ dùng cho loading bars
```

**Material Design Standard:** `cubic-bezier(0.4, 0, 0.2, 1)`

---

## CSS vs JS Animation

| Khi nào | Dùng gì |
|---------|---------|
| Simple transitions (opacity, transform) | CSS transition |
| Keyframe animations | CSS @keyframes |
| Physics / spring / complex sequence | GSAP / anime.js |
| 3D scene animations | Three.js AnimationMixer |
| SVG path animations | Lottie / GSAP SVG |

---

## Anti-patterns

- ❌ `transition: all` — thay bằng property cụ thể
- ❌ `linear` easing — thiếu tự nhiên
- ❌ Duration > 600ms — quá chậm, user frustrated
- ❌ Animate width/height — dùng `transform: scaleX/Y` thay
- ❌ Mọi element đều animate — purposeful motion only

---

## MCP Tools

```
compute_easing("spring", [0, 0.25, 0.5, 0.75, 1.0])
  → eased values + cubic-bezier CSS

suggest_animation_duration("modal", distance_px=0, complexity="medium")
  → {duration_ms: 350, easing: "standard", css_transition: "..."}
```
