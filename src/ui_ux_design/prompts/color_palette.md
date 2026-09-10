<!-- prompts/color_palette.md -->
# Color System & Contrast Standards Prompt

## Bảng màu & Tỷ lệ 60-30-10
- **60% Nền tảng (Dominant)**: Background canvas trung tính (Light: `#FAFAFA` hoặc `#F4F5F7`; Dark: `#0D1117` hoặc `#121826`).
- **30% Cấu trúc (Secondary)**: Surfaces, borders, text phụ, card headers.
- **10% Điểm nhấn (Accent/Primary)**: Primary CTA, active states, key badges.

## Tiêu chuẩn tương phản WCAG 2.1
- Text thông thường (< 18px hoặc < 14px bold): Tỷ lệ tương phản tối thiểu **4.5:1** (AA) hoặc **7.0:1** (AAA).
- Text lớn (>= 18px hoặc >= 14px bold): Tỷ lệ tương phản tối thiểu **3.0:1** (AA).
- UI Components & Form borders: Tỷ lệ tương phản tối thiểu **3.0:1** so với background kế cận.

## Dark Mode Mapping Rules
- Không đảo ngược màu một cách ngây thơ (`#000` thành `#FFF`).
- Giảm độ bão hòa (saturation) của màu accent từ 10-20% trong dark mode để tránh hiện tượng rung mắt (chromatic aberration).
- Bề mặt càng cao trong trục Z (elevation) thì màu nền càng sáng nhẹ (Surface tinting).
