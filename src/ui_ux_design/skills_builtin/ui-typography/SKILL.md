---
name: ui-typography
description: >
  Typographic system: modular type scale, line height, letter spacing,
  font pairing, readability rules. Activate khi task có text/typography.
  MCP tools: calc_type_scale, suggest_font_pair.
---

# UI Typography System

## Modular Type Scale

```
size = base × ratio^n

Base: 16px (1rem) — browser default, accessibility baseline
```

| Scale Name | Ratio | Dùng khi |
|-----------|-------|---------|
| Minor Second | 1.067 | Dense data tables |
| Major Second | 1.125 | Dashboard, admin |
| Minor Third | 1.200 | General app |
| **Major Third** | **1.250** | **Default — landing page** |
| Perfect Fourth | 1.333 | Headline-heavy editorial |

---

## Type Scale (Major Third, base 16px)

| Token | Size | Line Height | Use |
|-------|------|-------------|-----|
| `2xs` | 10px | 1.6 | Timestamp, label |
| `xs` | 13px | 1.6 | Caption, helper |
| `sm` | 16px | 1.6 | Body text |
| `base` | 16px | 1.6 | Body default |
| `lg` | 20px | 1.35 | Lead text |
| `xl` | 25px | 1.35 | H3 |
| `2xl` | 31px | 1.2 | H2 |
| `3xl` | 39px | 1.1 | H1 |
| `4xl` | 49px | 1.1 | Hero headline |

---

## Line Height Rules

- **Heading** (>24px): line-height 1.1–1.2
- **Body** (14–20px): line-height 1.5–1.7
- **Caption** (<14px): line-height 1.4

---

## Readability

- **Measure (line length):** 45–75 characters (600–800px at 16px)
- **Contrast:** body text phải pass WCAG AA (≥4.5:1)
- **Minimum size:** 12px (14px recommended for mobile)

---

## Font Pairing Styles

| Style | Heading | Body |
|-------|---------|------|
| `modern` | Inter | Inter |
| `geometric` | Outfit | DM Sans |
| `editorial` | Playfair Display | Source Serif 4 |
| `technical` | JetBrains Mono | IBM Plex Sans |
| `elegant` | Cormorant Garamond | Lato |

---

## Anti-patterns

- ❌ System default fonts (Arial, Times) cho sản phẩm thương mại
- ❌ Font size tùy tiện: 13px, 17px, 22px
- ❌ Line height 1.0 — không thể đọc
- ❌ ALL CAPS cho body text >3 words
- ❌ >3 font families trong 1 design

---

## MCP Tools

```
calc_type_scale(16, 1.25, style="modern")
  → {scale, css_vars, line_heights, font_pair_suggestion}

suggest_font_pair("geometric")
  → {heading, body, google_fonts_url, css_snippet}
```
