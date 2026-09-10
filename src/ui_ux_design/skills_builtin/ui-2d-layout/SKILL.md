---
name: ui-2d-layout
description: >
  Kiến trúc layout 2D: box model, flexbox, CSS Grid, spacing scale,
  responsive breakpoints. Activate khi thiết kế layout web/desktop.
  MCP tools: calc_grid, calc_spacing_scale, preview_ascii_grid, analyze_layout.
---

# UI 2D Layout

## Mental Model: Layout Stack

```
Page (max-width: 1440px, centered)
  └── Grid (12 columns, 24px gutter, 80px margin)
       └── Cell (span N columns)
            └── Component (flex/block, box model)
                 └── Content (text, images, icons)
```

---

## Box Model (BẮT BUỘC nhớ)

```
┌─────────────────────────────┐  ← margin (bên ngoài, transparent)
│  ┌───────────────────────┐  │  ← border
│  │  ┌─────────────────┐  │  │  ← padding (bên trong, có background)
│  │  │    CONTENT      │  │  │
│  │  └─────────────────┘  │  │
│  └───────────────────────┘  │
└─────────────────────────────┘
```

> **Luôn dùng `box-sizing: border-box`** — width bao gồm padding + border.

---

## Flexbox Mental Model

```
flex-direction: row    → main axis = horizontal →
flex-direction: column → main axis = vertical   ↓

justify-content = phân bố theo MAIN AXIS
align-items     = căn chỉnh theo CROSS AXIS
```

| Property | Values thường dùng |
|----------|-------------------|
| `justify-content` | `flex-start`, `center`, `space-between`, `space-around` |
| `align-items` | `stretch` (default), `center`, `flex-start`, `flex-end` |
| `flex-wrap` | `wrap` (responsive), `nowrap` |
| `gap` | Thay thế margin, dùng với 8px scale |

---

## CSS Grid Mental Model

```css
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);  /* 12 equal columns */
  gap: 24px;                               /* gutter */
  padding: 0 80px;                         /* margin */
}

.hero { grid-column: 1 / -1; }            /* full width */
.sidebar { grid-column: 1 / 4; }          /* 3 columns */
.content { grid-column: 4 / 13; }         /* 9 columns */
```

---

## Responsive Breakpoints

| Name | Width | Columns | Gutter | Margin |
|------|-------|---------|--------|--------|
| Mobile | 375px | 4 | 12px | 16px |
| Tablet | 768px | 6 | 16px | 24px |
| Desktop | 1024px | 12 | 20px | 40px |
| Wide | 1440px | 12 | 24px | 80px |

---

## MCP Tools

```
calc_grid(1440, 12, 24, 80)    → column width, CSS
calc_spacing_scale(8)          → 4,8,12,16,24,32,48,64px
preview_ascii_grid(12, 24, 80) → ASCII preview
analyze_layout({elements})     → alignment score
```
