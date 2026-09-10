---
name: ui-prompt-framework
description: >
  Framework tư duy 11-section cho mọi task thiết kế UI từ đầu.
  Activate khi nhận prompt tạo mới page, section, hoặc component phức tạp.
  Bao gồm: section priority map, Lumora case study, MCP tool mapping.
---

# UI Prompt Framework — 11-Section Thinking System

## Khi nào kích hoạt

Activate skill này khi:
- Tạo mới một trang (page) hoặc section UI từ đầu
- Nhận yêu cầu "build a landing page", "recreate this site", "design a dashboard"
- Cần cấu trúc lại design intent trước khi viết code

> **Không cần** activate khi chỉ sửa nhỏ (tweak color, fix spacing, v.v.)

---

## Mental Framework: 11 Sections

Mọi UI đều có thể được mô tả đầy đủ qua 11 nhóm. Không nhất thiết phải điền hết — chỉ cần điền những sections **phù hợp với trang đó**.

```
1. Objective      → Why / What / How (mục tiêu thiết kế)
2. Container      → Shell, sizing, positioning
3. Layout         → Grid, flex, responsive
4. Content        → Exact text, headings, CTAs
5. Components     → UI building blocks
6. Styling        → Tokens, typography, colors
7. Assets         → Images, fonts, icons, video
8. Interaction    → Click, hover, scroll, animation
9. Responsive     → Breakpoints, mobile adaptation
10. Validation    → Completion checklist
11. Source        → Ground truth / authoritative reference
```

---

## Priority Map theo loại trang

### Landing Page (như Lumora)
| Section | Priority | Notes |
|---------|----------|-------|
| 1. Objective | 🔴 CRITICAL | Phải rõ: studio? SaaS? Portfolio? |
| 2. Container | 🟡 HIGH | Shell max-width, rem grid |
| 3. Layout | 🔴 CRITICAL | Desktop 12-col, mobile stack |
| 4. Content | 🔴 CRITICAL | Exact copy — không hallucinate text |
| 5. Components | 🔴 CRITICAL | Hero, Loader, NavMenu, Modal |
| 6. Styling | 🔴 CRITICAL | Color tokens, typography scale |
| 7. Assets | 🟡 HIGH | Hero images, fonts CDN |
| 8. Interaction | 🔴 CRITICAL | Canvas effect, spring animations, scroll |
| 9. Responsive | 🟡 HIGH | sm/md/lg breakpoints |
| 10. Validation | 🟢 MEDIUM | Self-check trước khi ship |
| 11. Source | 🟢 MEDIUM | Nếu recreating, link exact source |

### Dashboard / App
| Section | Priority |
|---------|----------|
| 1. Objective | 🔴 CRITICAL |
| 3. Layout | 🔴 CRITICAL (sidebar vs topbar) |
| 5. Components | 🔴 CRITICAL (table, chart, filter) |
| 8. Interaction | 🟡 HIGH (state management, loading) |
| 9. Responsive | 🟡 HIGH |

### Component Library
| Section | Priority |
|---------|----------|
| 5. Components | 🔴 CRITICAL |
| 6. Styling | 🔴 CRITICAL (tokens, variants) |
| 8. Interaction | 🔴 CRITICAL (all states) |
| 10. Validation | 🟡 HIGH |

---

## Section 1 — Objective (Không bao giờ skip)

Trước khi code, phải trả lời:

```
1.1 Mục tiêu: "Tái tạo landing page Lumora studio"
1.2 Product: "Single page — lumora.studio"
1.3 Design intent: "Premium dark/light palette, signature canvas effect"
1.4 Scope: "Full page: Loader → Hero → About → Portfolio → Footer"
1.5 Output: "Single index.html, self-contained"
1.6 Tech: "Vanilla HTML/CSS/JS"
1.7 Libraries: "Lenis (CDN importmap only)"
1.8 Constraints: "No build step, no framework, no placeholder images"
1.9 Global: "prefers-reduced-motion support, WCAG AA"
```

---

## Section 8 — Interaction (Lumora-level)

Đây là section phân biệt AI UI với premium UI. Phải có:

### 8.1 Global State Model
```js
// PHẢI có:
let scrollEnabled = true;
function stopScroll() { lenis.stop(); /* overflow:hidden on html */ }
function startScroll() { lenis.start(); /* remove overflow */ }
```

### 8.10 Smooth Scroll
```js
// PHẢI dùng Lenis, không dùng CSS scroll-behavior
const lenis = new Lenis({ smoothWheel: true });
function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
requestAnimationFrame(raf);
```

### 8.11 Animation — Spring Physics (KHÔNG dùng ease)
```
// ❌ AI default:
transition: all 0.3s ease;

// ✅ Spring-like:
transition: all 0.7s cubic-bezier(0.22, 1, 0.36, 1);  /* {tension:210, friction:26} */
transition: all 0.35s cubic-bezier(0.2, 0.8, 0.2, 1); /* hovers snappy {320,18} */
```

### 8.12 Spring Config → CSS Mapping
| React-spring config | CSS cubic-bezier | Duration |
|--------------------|------------------|----------|
| {tension:210, friction:26} | cubic-bezier(.22,1,.36,1) | 0.7s |
| {tension:200, friction:24} | cubic-bezier(.16,1,.3,1) | 0.8s |
| {tension:320, friction:18} | cubic-bezier(.2,.8,.2,1) | 0.35s (hovers) |
| {tension:260, friction:30} | cubic-bezier(.34,1.56,.64,1) | 0.6s (modal) |
| {tension:300, friction:28} | cubic-bezier(.25,1,.5,1) | 0.5s (carousel) |

### 8.13 Reveal (Scroll-triggered)
```js
// IntersectionObserver pattern — PHẢI có
const observer = new IntersectionObserver((entries) => {
  entries.forEach(el => {
    if (el.isIntersecting) {
      el.target.classList.add('revealed');
      observer.unobserve(el.target); // once mode
    }
  });
}, { threshold: 0.1 });
```

Line reveal CSS:
```css
.line-wrapper { overflow: hidden; }
.line-inner { transform: translateY(100%); opacity: 0; transition: transform 0.9s cubic-bezier(.215,.61,.355,1), opacity 0.9s; }
.revealed .line-inner { transform: translateY(0); opacity: 1; }
/* Per-line stagger via nth-child delay */
.line-inner:nth-child(2) { transition-delay: 120ms; }
.line-inner:nth-child(3) { transition-delay: 240ms; }
```

### 8.14 Loader (Branded, không phải spinner)
```
PHẢI có: full-screen branded loader với:
- Logo + tagline
- Progress counter 000→100 (zero-padded, tabular-nums)
- easeInOutCubic counting over FILL_MS=1300ms
- Exit: slide up transform translateY(-100%) cubic-bezier(.22,1,.36,1) ~0.7s
- Gate: chỉ sau khi loader exit xong thì play hero reveals (ready flag)
```

### 8.18 Canvas Effect (Hero signature)
```
Lumora pattern: liquid reveal cursor trail
- brushRadius: 143px (CSS px)
- decay: 0.016 per frame (destination-out fade)
- dpr: min(devicePixelRatio, 2)
- Dùng offscreen canvas cho cover image (source-in masking)
- prefers-reduced-motion → skip canvas entirely
- Idle > 120 frames → clearRect (hard reset)
```

### 8.21 Modal
```
PHẢI có khi có modal:
- stopScroll() khi mở
- startScroll() khi đóng
- Escape key listener
- Backdrop click to close
- stopPropagation trên panel
```

---

## Section 5 — Components (DOM Order MATTERS)

**Luôn ghi rõ DOM order:**
```
PageLoader (z:120) → Header (z:50, fixed) → main {
  Hero (section)
  About (section)
  CreateBand (section)
  Portfolio (section)
  Services (section)
  Stats (section)
} → Footer → NavMenu (overlay z:115) → RequestModal (overlay z:110)
```

**Shared Component Recipes phải define trước:**
- PillButton: variants (dark/light/outline) + arrow variants (right/up-right)
- Eyebrow: tone (dark/light) + dot
- TagChip: tone + border
- AnimatedLink: translateX spring hover

---

## Section 6 — Styling (Token-first, không hardcode)

### 6.2 Design Tokens (LUÔN dùng CSS variables)
```css
:root {
  /* Colors — từ generate_color_palette */
  --bg: #ffffff;
  --fg: #111111;
  --ink: #0a0a0a;        /* black cards */
  --muted: #8d8d8d;
  --accent: #b15f2c;     /* burnt orange */

  /* Radii — fixed tokens */
  --radius-pill: 9999px;
  --radius-card: 2rem;
  --radius-card-sm: 1.25rem;
  --radius-control: 0.875rem;

  /* Container */
  --shell: 88rem;        /* max-width */
  --watermark: 13rem;    /* font-size */
}
```

### 6.3 Adaptive Grid (CRITICAL — bake in, không skip)
```css
/* rem-based: tất cả sizes dùng rem */
@media (max-width: 1920px) { html { font-size: 0.833333vw } }
@media (max-width: 1440px) { html { font-size: 1.111111vw } }
@media (max-width: 1024px) { html { font-size: 1.5625vw } }
@media (max-width: 640px)  { html { font-size: 4.444444vw } }
```

```js
/* Scale-up JS (bắt buộc trên >1920px) */
function applyAdaptiveGrid() {
  const FONT_BASE = 16, baseWidth = 1920, coef = 0.6666;
  const w = window.innerWidth;
  const widthReduction = ((baseWidth - w) / baseWidth) * 100;
  const size = FONT_BASE - (FONT_BASE * (widthReduction * coef)) / 100;
  if (size > FONT_BASE) document.documentElement.style.fontSize = size + 'px';
  else document.documentElement.style.removeProperty('font-size');
}
applyAdaptiveGrid(); addEventListener('resize', applyAdaptiveGrid);
```

---

## MCP Tools Mapping theo Section

| Section | Tool cần gọi | Khi nào |
|---------|-------------|---------|
| 6.2 Color tokens | `generate_color_palette` | Trước khi code bất kỳ màu nào |
| 6.2 Contrast | `check_wcag_contrast` | Mọi text/background pair |
| 6.3 Typography | `calc_type_scale` | Trước khi set font-size |
| 6.5 Spacing | `calc_spacing_scale` | Trước khi set padding/margin |
| 6.10 Shadow | `calc_elevation_shadow` | Card, modal, dropdown |
| 6.15 Z-index | `calc_z_stack` | Loader/modal/header/overlay |
| 8.11 Animation | `compute_easing` | Mọi animation curve |
| 8.11 Duration | `suggest_animation_duration` | Modal, drawer, page transition |
| **NEW** Sections | `generate_ui_prompt` | Để sinh structured prompt 11 sections |
| **NEW** Validate | `validate_ui_prompt` | Check prompt completeness |
| **NEW** Components | `spec_button`, `spec_card`, `spec_hero` | Sinh component CSS tokens |
| Cuối cùng | `review_ui_quality` | Self-review bắt buộc |

---

## Lumora Case Study — Section Mapping

Đây là ví dụ thực tế từ Lumora landing page:

```
Section 1: Landing page studio — Onest font — Lenis only — single HTML
Section 2: body#fff / loader#0a0a0a / hero#c9c9c9 / footer#0a0a0a
Section 3: 12-col grid lg, stack sm — shell max-width 88rem
Section 4: "Bold ideas, shipped with quiet precision" / "LUMORA" watermark
Section 5: PageLoader → Header → Hero → About → CreateBand → Portfolio → Services → Stats → Footer → NavMenu → RequestModal
Section 6: --bg:#fff --fg:#111 --ink:#0a0a0a --accent:#b15f2c — Onest 400/500/600/700
Section 7: hero/after.jpg (base LCP), hero/before.jpg (brush-reveal) — Google Fonts CDN
Section 8: Lenis + spring cubic-bezier + canvas liquid reveal + count-up + clock
Section 9: sm:640 md:768 lg:1024 — mobile stack — touch disables hover springs
Section 10: WCAG AA, prefers-reduced-motion, semantic HTML, aria-label
```

---

## Anti-Rules (Không bao giờ làm)

- ❌ `transition: all 0.3s ease` cho hover — dùng spring cubic-bezier
- ❌ Hardcode hex mà không qua `generate_color_palette`
- ❌ Bỏ qua adaptive grid — mọi landing page phải có rem-based scaling
- ❌ Hero chỉ có static image — phải có interactive element (canvas, parallax, etc.)
- ❌ Loader là spinner đơn giản — phải branded với counter
- ❌ Modal không lock scroll — phải có `stopScroll()` / `startScroll()`
- ❌ Font-size random px — phải từ `calc_type_scale`
- ❌ Spacing random — phải 8px grid từ `calc_spacing_scale`
- ❌ `z-index: 9999` — phải từ `calc_z_stack`
- ❌ Placeholder text "Lorem ipsum" — dùng real copy hoặc ghi rõ [PLACEHOLDER]
