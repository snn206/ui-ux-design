---
name: ui-color-system
description: >
  Hệ thống màu sắc chuyên nghiệp: HSL model, palette generation,
  WCAG contrast, dark mode tokens, gradient design.
  Activate khi bất kỳ task nào liên quan đến màu sắc.
---

# UI Color System

## Khi nào kích hoạt
Mọi task có màu sắc — dù chỉ chọn 1 màu nền.

---

## HSL Model (Dùng thay vì RGB/HEX)

```
HSL(Hue 0-360°, Saturation 0-100%, Lightness 0-100%)
```

- **Hue** = màu gốc (0=đỏ, 120=xanh lá, 240=xanh dương)
- **Saturation** = độ đậm (0%=xám, 100%=sống động)
- **Lightness** = độ sáng (0%=đen, 50%=cân bằng, 100%=trắng)

> **Tại sao HSL?** Dễ tính toán harmony, dễ tạo tonal scale, dễ dark mode.

---

## Color Schemes

| Scheme | Cách tính | Dùng khi |
|--------|-----------|---------|
| **Monochromatic** | 1 hue, nhiều lightness | Minimal, elegant |
| **Complementary** | H + 180° | High contrast, call-to-action |
| **Analogous** | H ±30° | Harmonious, nature-inspired |
| **Triadic** | H + 120° + 240° | Vibrant, playful |
| **Split-comp** | H + 150° + 210° | Balanced contrast |

---

## 60-30-10 Rule (BẮT BUỘC)

```
60% → Dominant color (background, large surfaces)
30% → Secondary color (cards, sidebars)
10% → Accent color (buttons, highlights, CTA)
```

---

## WCAG Contrast Requirements

| Loại text | Minimum ratio |
|-----------|--------------|
| Normal text (<18px) | **4.5:1** (AA) |
| Large text (≥18px bold / ≥24px) | **3.0:1** (AA) |
| UI components, icons | **3.0:1** (AA) |
| Enhanced (AAA) | **7.0:1** |

**Luôn gọi `check_wcag_contrast` trước khi dùng bất kỳ cặp màu nào.**

---

## Dark Mode Strategy

> **KHÔNG đảo màu đơn thuần** (light → dark = invert). Phải rebuild token.

```
Light mode: background=#FFFFFF, text=#1A1A2E
Dark mode:  background=#0F0F1A, text=#E8E8F0
                                  ↑ KHÔNG phải #FFFFFF
```

Gọi tool `generate_dark_tokens` để sinh dark mode tự động.

---

## Gradient Rules

- ✅ 2-3 màu tối đa
- ✅ Góc: 135° (xuống phải) hoặc 45° (lên phải)
- ✅ Màu trong gradient phải cùng hue family hoặc analogous
- ❌ Không dùng rainbow gradient (>3 hues)
- ❌ Không gradient text trừ khi hero element

---

## MCP Tools

| Task | Tool |
|------|------|
| Tạo palette | `generate_color_palette(base, scheme)` |
| Kiểm tra contrast | `check_wcag_contrast(fg, bg)` |
| Sinh dark mode | `generate_dark_tokens(light_tokens)` |
| Tạo gradient | `generate_gradient(colors, angle)` |
