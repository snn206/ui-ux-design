<!-- prompts/2d_layout.md -->
# 2D Layout & Grid Specification Prompt

## Ngữ cảnh áp dụng
- Platform: {platform}
- Framework: {framework}
- Mục tiêu: Thiết kế layout 2D responsive, cân đối, theo grid chuẩn.

## Hướng dẫn triển khai
1. **Grid Container**:
   - Sử dụng CSS Grid hoặc Flexbox hiện đại với gutter rõ ràng.
   - Desktop (>= 1200px): 12 columns, max-width 1280px hoặc 1440px, auto-margins.
   - Tablet (768px - 1199px): 8 columns, gutter 16px.
   - Mobile (< 768px): 4 columns, padding 16px.
2. **Spacing Tokens**:
   - Sử dụng CSS variables: `--space-xs: 4px`, `--space-sm: 8px`, `--space-md: 16px`, `--space-lg: 24px`, `--space-xl: 32px`, `--space-2xl: 48px`.
3. **Box Model & Alignment**:
   - `box-sizing: border-box` trên toàn bộ elements.
   - Tránh hardcoded height trên containers chứa text động.
