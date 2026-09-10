---
name: ui-anti-patterns
description: >
  Nhận biết và tránh UI xấu, rác, AI-generated generic.
  Catalog 10 "AI UI Smell" phổ biến nhất với cách fix cụ thể.
  Activate khi review bất kỳ UI nào — kể cả UI do chính AI sinh ra.
---

# UI Anti-Patterns — Chống UI Bẩn/Rác/AI

## Khi nào kích hoạt
- Trước khi xuất code UI bất kỳ
- Khi review UI của người khác
- Sau khi sinh UI — self-review bắt buộc

---

## AI UI Smell Catalog

### 1. 🚫 Generic Grey
**Dấu hiệu:** `#f0f0f0`, `#e0e0e0`, `#ccc`, `#ddd`, `#eee` tràn lan
**Tại sao xấu:** Không có personality, nhạt nhẽo, không memorable
**Fix:** Dùng HSL tonal palette. Tool: `generate_color_palette`

---

### 2. 🌈 Rainbow Hell
**Dấu hiệu:** >4 màu khác hue trong 1 màn hình
**Tại sao xấu:** Mắt không biết tập trung vào đâu, chaotic
**Fix:** 60-30-10 rule: 1 dominant, 1 secondary, 1 accent

---

### 3. 📝 Text Wall
**Dấu hiệu:** Block text lớn, không padding, không line breaks, font size giống nhau
**Tại sao xấu:** Unreadable, user bỏ đọc ngay
**Fix:** Type scale + line height 1.6 + max-width 65ch + section spacing

---

### 4. 🏝️ Orphaned Element
**Dấu hiệu:** Button, icon, text nổi một mình không có visual connection
**Tại sao xấu:** Vi phạm Proximity law, confusing UX
**Fix:** Grouping với padding, border-radius, hoặc container

---

### 5. 🌑 Shadow Abuse
**Dấu hiệu:** `box-shadow` trên mọi element với blur quá lớn
**Tại sao xấu:** Looks cheap, overdesigned, visual noise
**Fix:** Chỉ dùng elevation 1-2 cho card, elevation 3-4 cho modal. Tool: `calc_elevation_shadow`

---

### 6. 🔤 Font Chaos
**Dấu hiệu:** >3 font-size khác nhau không theo scale, size random (13px, 17px, 22px)
**Tại sao xấu:** Không có hierarchy, amateur
**Fix:** Modular type scale. Tool: `calc_type_scale`

---

### 7. 😴 Flat Boring
**Dấu hiệu:** Hoàn toàn flat, không shadow, không gradient, không depth, monochrome grey
**Tại sao xấu:** Lifeless, không engaging, looks like wireframe
**Fix:** Subtle elevation level 1, gentle gradient overlay, slight surface tint

---

### 8. 💫 Over-Animation
**Dấu hiệu:** Mọi thứ đều animate, hover effects khắp nơi, animation dài >600ms
**Tại sao xấu:** Distract user, performance issue, accessibility problem
**Fix:** Animate với purpose: state changes, feedback, onboarding only

---

### 9. 📐 Inconsistent Spacing
**Dấu hiệu:** Spacing random: 7px, 13px, 22px, 37px
**Tại sao xấu:** Looks amateurish, no visual rhythm
**Fix:** 8px grid system. Tool: `calc_spacing_scale`

---

### 10. 👁️ Low Contrast
**Dấu hiệu:** Grey text trên white, light blue on white, anything < 3:1
**Tại sao xấu:** Unreadable, fails accessibility, illegal in many contexts
**Fix:** Tool: `check_wcag_contrast` — must pass AA (4.5:1 for normal text)

---

## Pre-submit Checklist

Trước khi xuất code UI, tự hỏi:

- [ ] Màu có qua `generate_color_palette` không?
- [ ] Contrast có qua `check_wcag_contrast` không?
- [ ] Spacing có theo 8px grid không?
- [ ] Font size có theo type scale không?
- [ ] Animation có easing và duration phù hợp không?
- [ ] Elevation chỉ dùng 0-5 levels không?
- [ ] Đã gọi `review_ui_quality` chưa?

---

## MCP Tools

| Task | Tool |
|------|------|
| Review tổng thể | `review_ui_quality(description, colors, fonts, spacing_values)` |
| Check contrast | `check_wcag_contrast(fg, bg)` |
