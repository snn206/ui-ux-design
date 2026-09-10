---
name: ui-fundamentals
description: >
  Kiến thức nền tảng UI/UX bắt buộc. Activate trước mọi task UI.
  Bao gồm: Gestalt laws, CRAP principles, 8px grid, visual hierarchy,
  F/Z pattern, và quy tắc không sinh giá trị tùy tiện.
---

# UI Fundamentals — Kiến thức Nền tảng

## Khi nào kích hoạt
Skill này phải được đọc **trước tất cả tasks UI** — dù là web, desktop, hay 3D.

---

## Mental Model: 4 câu hỏi cần trả lời trước khi viết UI

1. **Cái gì quan trọng nhất?** → Visual hierarchy
2. **Các element liên quan nhau như thế nào?** → Proximity & Grouping
3. **Người dùng mắt sẽ đi theo hướng nào?** → F-pattern / Z-pattern
4. **UI này cảm giác nhất quán không?** → Repetition & Alignment

---

## Gestalt Laws (Luật tri giác)

| Luật | Ý nghĩa | Áp dụng trong UI |
|------|---------|------------------|
| **Proximity** | Elements gần nhau = cùng nhóm | Card group, form fields |
| **Similarity** | Elements giống nhau = cùng loại | Button styles, icon families |
| **Closure** | Não tự điền khoảng trống | Icons, progress indicators |
| **Continuity** | Mắt theo đường thẳng/cong | Navigation flows, carousels |
| **Figure/Ground** | Tách foreground khỏi background | Modal overlays, tooltips |

---

## CRAP Principles

- **C**ontrast — Các element khác nhau phải trông khác nhau rõ ràng
- **R**epetition — Nhất quán: cùng màu, font, style trong suốt
- **A**lignment — Mọi element phải có đường căn, không đặt tùy tiện
- **P**roximity — Nhóm các element liên quan lại, tách biệt không liên quan

---

## 8px Grid System (BẮT BUỘC)

> **Mọi spacing, sizing phải là bội số của 8.**

```
4   8   12  16  24  32  48  64  96  128
```

- ❌ `padding: 13px` — KHÔNG được
- ✅ `padding: 16px` — ĐÚNG
- ❌ `gap: 7px` — KHÔNG được
- ✅ `gap: 8px` — ĐÚNG

**Công cụ:** Dùng MCP tool `calc_spacing_scale` để tạo scale.

---

## Visual Hierarchy

Kích thước, màu sắc, và weight tạo ra thứ bậc:

```
H1  → 32-48px, weight 700, màu đậm
H2  → 24-32px, weight 600
H3  → 20-24px, weight 600
Body → 16px, weight 400, màu hơi nhạt hơn
Caption → 12-14px, weight 400, màu xám
```

---

## Quy tắc KHÔNG được vi phạm

- ❌ **Không tự đặt màu hex** mà chưa qua `generate_color_palette`
- ❌ **Không dùng px spacing tùy tiện** — phải dùng `calc_spacing_scale`
- ❌ **Không đặt font size ngẫu nhiên** — phải dùng `calc_type_scale`
- ❌ **Không sinh animation** mà không có easing curve
- ❌ **Không dùng `z-index: 9999`** tùy tiện — phải dùng `calc_z_stack`

---

## MCP Tools liên quan

| Tình huống | Tool cần gọi |
|-----------|-------------|
| Cần màu | `generate_color_palette` |
| Cần spacing | `calc_spacing_scale` |
| Cần font size | `calc_type_scale` |
| Cần review chất lượng | `review_ui_quality` |
