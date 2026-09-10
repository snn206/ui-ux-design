---
name: ui-mcp-tools
description: >
  Hướng dẫn khi nào gọi tool MCP nào và cách đọc kết quả.
  Đây là skill meta — reference map cho tất cả 18 tools.
  Activate khi cần biết tool nào để dùng cho task cụ thể.
---

# UI MCP Tools — Reference Map

## Quy tắc sử dụng

> **Luôn gọi MCP tool thay vì tự tính hoặc guess.**
> Tool trả về kết quả có cấu trúc, đã validated — không cần self-verify.

---

## Tools theo task

### Cần màu sắc?
```
generate_color_palette(base_color, scheme, steps)
  base_color: "#6C63FF" hoặc "hsl(240,60%,55%)"
  scheme: "complementary"|"triadic"|"analogous"|"monochromatic"
  → {colors: [{hex, hsl, name, role}], css_vars, preview_ascii}

check_wcag_contrast(fg, bg)
  → {ratio, AA_normal, AA_large, AAA_normal, grade, recommendation}

generate_dark_tokens(light_tokens)
  → {dark_tokens: {name: hex}, strategy}

generate_gradient(colors, angle=135, type="linear")
  → {css, contrast_safe}
```

### Cần layout / spacing?
```
calc_grid(container_px, columns, gutter_px, margin_px)
  → {column_width, css, breakpoints}

calc_spacing_scale(base=8)
  → {scale: {xs:4, sm:8, ...}, css_vars}

preview_ascii_grid(columns, gutter)
  → ASCII art string

analyze_layout({elements: [{x,y,w,h,type}]})
  → {alignment_score, spacing_consistency, issues, suggestions}
```

### Cần depth / shadow / parallax?
```
calc_elevation_shadow(level)   # level 0-5
  → {css_box_shadow, blur, spread, opacity, y_offset}

calc_z_stack(["bg","nav","modal","toast"])
  → {z_indices: {bg:0, nav:100, modal:500}, css_vars}

calc_parallax_offset(scroll_y, layers)
  → {offsets: {far:40px, mid:100px}, css_transforms}

suggest_depth_stack("web-app"|"game-hud"|"landing-page")
  → full semantic z-stack
```

### Cần 3D?
```
validate_scene_graph({camera, lights, objects})
  → {valid, score, issues, suggestions}

calc_perspective_fov(fov=60, aspect=1.778)
  → {perspective_css, threejs_snippet, css_3d_snippet}

suggest_pbr_material("metal"|"plastic"|"glass"|"wood"|...)
  → {roughness, metalness, color_suggestion, threejs_snippet}
```

### Cần animation?
```
compute_easing("spring"|"ease-out"|..., t_values=[0,0.5,1])
  → {eased_values, css_value: "cubic-bezier(...)", duration_suggestion}

suggest_animation_duration("modal", distance_px=0, complexity="medium")
  → {duration_ms, easing, css_transition, rationale}
```

### Cần typography?
```
calc_type_scale(base=16, ratio=1.25, style="modern")
  → {scale, css_vars, line_heights, letter_spacings, font_pair_suggestion}

suggest_font_pair("geometric"|"editorial"|"modern"|...)
  → {heading, body, google_fonts_url, css_snippet}
```

### Cần review UI?
```
review_ui_quality(
  description="...",
  colors=["#6C63FF", "#FF6584"],
  fonts=[16, 24, 32],
  spacing_values=[8, 16, 24]
)
  → {score, grade, issues: [{type, severity, description, fix}], summary}
```

---

## Thứ tự gọi tool cho task mới

```
1. generate_color_palette        → có màu
2. check_wcag_contrast           → verify contrast
3. calc_type_scale               → có typography
4. calc_spacing_scale            → có spacing
5. [optional] calc_grid          → có layout grid
6. [optional] calc_elevation_shadow → có shadows
7. [optional] suggest_animation_duration → có motion
8. review_ui_quality             → self-review cuối
```
