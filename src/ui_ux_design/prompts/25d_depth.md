<!-- prompts/25d_depth.md -->
# 2.5D Depth, Elevation & Stacking Prompt

## Nguyên tắc phân tầng (Layering & Depth)
Giao diện có chiều sâu 2.5D giúp người dùng hiểu rõ ngữ cảnh tương tác và độ quan trọng của các thành phần giao diện.

## Thang Elevation chuẩn (Shadow Tokens)
- **Level 0 (Flat)**: Background canvas, borders mờ `box-shadow: none`.
- **Level 1 (Card/Surface)**: Card nghỉ, buttons phụ:
  `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);`
- **Level 2 (Hover/Active)**: Card hover, dropdown menu:
  `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);`
- **Level 3 (Modal/Dialog)**: Dialogs, popovers nổi bật:
  `box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.15), 0 4px 6px -4px rgba(0, 0, 0, 0.1);`
- **Level 4 (Toasts/Overlay)**: Toasts, notification banners:
  `box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.1);`

## Z-Index Stacking Context
- Base: `0 - 10`
- Sticky Header/Nav: `100`
- Dropdown/Popover: `500`
- Modal Overlay: `1000`
- Modal Dialog: `1010`
- Toast/Notification: `2000`
- Tooltip: `3000`
