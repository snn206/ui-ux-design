<!-- prompts/animation_motion.md -->
# Motion Design & Animation Specification Prompt

## Quy tắc thời lượng (Duration Guidelines)
- Micro-interactions (hover, click, toggle, check): `100ms - 200ms`
- Component transitions (dropdowns, tooltips, accordion): `200ms - 300ms`
- Page transitions & Dialog overlays: `300ms - 450ms`
- Tuyệt đối không dùng duration > 500ms cho các tương tác lặp lại thường xuyên.

## Cubic Bezier Curves (Easing Standards)
- **Standard / Move**: `cubic-bezier(0.4, 0.0, 0.2, 1)` (vật thể di chuyển từ A đến B trong màn hình).
- **Decelerate / Enter**: `cubic-bezier(0.0, 0.0, 0.2, 1)` (modal/toast bay vào màn hình).
- **Accelerate / Exit**: `cubic-bezier(0.4, 0.0, 1, 1)` (modal/toast biến mất khỏi màn hình).
- **Spring / Bounce**: `cubic-bezier(0.34, 1.56, 0.64, 1)` (chỉ dùng cho micro-feedbacks, badge pop).

## Accessibility
- Bắt buộc hỗ trợ `@media (prefers-reduced-motion: reduce)`:
  tắt transforms bay nhảy, chuyển về `opacity` mờ dần hoặc tức thì.
