# 🧠 Anti-AI-UI Skills System — Architecture & Developer Guide

## 1. Tổng quan hệ thống
Anti-AI-UI Skills System là một hệ thống 3 tầng (3-Layer Architecture) được thiết kế nhằm chuẩn hóa, tối ưu hóa thẩm mỹ và tư duy thiết kế giao diện cho các AI Coding Agents (Claude, Gemini, Cursor, Antigravity, VS Code, Zed, Codex...).

```
┌─────────────────────────────────────────────────────────────────┐
│                    TẦNG 1: SKILLS KNOWLEDGE                     │
│  9 bộ skills chuẩn hóa (.agents/skills/*):                       │
│  - ui-fundamentals, ui-2d-layout, ui-25d-depth, ui-3d-scene     │
│  - ui-color-system, ui-animation, ui-typography, ui-anti-patterns│
│  - ui-mcp-tools                                                 │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Agent đọc hiểu quy chuẩn
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TẦNG 2: MCP TOOL SERVER                      │
│  Server MCP (stdio transport) cung cấp 18 công cụ tính toán:     │
│  - generate_palette, check_contrast, dark_tokens                │
│  - calc_grid, calc_spacing_scale, analyze_layout                │
│  - calc_elevation_shadow, calc_z_stack, calc_parallax_offset    │
│  - compute_easing, suggest_animation_duration                   │
│  - calc_type_scale, suggest_font_pair                           │
│  - calc_perspective_fov, validate_scene_graph                   │
│  - review_ui_quality                                            │
│                                                                 │
│  Module Registry + modules.lock: hỗ trợ versioning & rollback!  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ Agent nạp context & prompt
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TẦNG 3: PROMPT TEMPLATES                     │
│  PromptLoader + 7 Prompt Templates (prompts/*.md):              │
│  - system_ui, 2d_layout, 25d_depth, 3d_scene, color_palette,    │
│    animation_motion, review_checklist                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Kho Version GitHub & Quản trị Version Tập Trung (`ui-mcp version`)

### 2.1. Kiến trúc Kho Version GitHub (GitHub Version Store)
Hệ thống lấy GitHub Repository (`snn206/ui-ux-design`) làm nguồn phát hành version chính thức (**Single Source of Truth**):

1. **Chỉ mục Version (`versions.json`)**:
   - Được cập nhật liên tục trên branch `main` của GitHub.
   - Chứa danh sách các release tag (`v1.0.0`, `v1.1.0`, `v1.2.0`...), thông tin tương thích, changelog và đường link tải gói assets.
2. **Local Cache (`~/.config/ui-ux-design/skills_cache/`)**:
   - Khi người dùng chọn tải hoặc chuyển đổi version (`ui-mcp version switch <tag>` hoặc `pull`), hệ thống sẽ tải gói nén từ GitHub Releases về cache máy tính.
   - Nhờ đó, các lần chuyển đổi version sau diễn ra tức thì (0ms network latency), hoàn toàn ngoại tuyến (offline-ready).
3. **Chuyển đổi version một bước (`ui-mcp version switch`)**:
   - `ui-mcp version switch v1.0.0`: Tải và áp dụng bản release v1.0.0 từ GitHub.
   - `ui-mcp version switch latest`: Luôn bám sát bản ổn định mới nhất từ GitHub.
   - `ui-mcp version switch local`: Dùng trực tiếp bộ skills từ mã nguồn gói cài đặt hiện tại.
   - `ui-mcp version rollback`: Tự động quay lại bản trước đó trong lịch sử lock.

### 2.2. Quản lý Độc Lập từng Module & Skills

#### Module Rollback & Pinning
Mỗi module MCP (`color`, `layout`, `typography`, `animation`, `depth_25d`, `scene_3d`, `quality`) được ghi nhận trong `.ui-mcp/modules.lock`.
- Xem trạng thái modules: `ui-mcp module status`
- Rollback module khi lỗi: `ui-mcp module rollback <module_name> [version]`
- Pin version cố định: `ui-mcp module pin <module_name> <version>`

#### Skills Lock & Checksum Verification
Kỹ năng (Skills) được quản lý qua `.ui-mcp/skills.lock`:
- Xem danh sách: `ui-mcp skills list`
- Cài đặt version mong muốn: `ui-mcp skills install <skill_name> --version <ver>`
- Rollback từng skill: `ui-mcp skills rollback <skill_name> [version]`
- Kiểm tra toàn vẹn (SHA256): `ui-mcp skills verify`


---

## 3. Cấu trúc thư mục dự án (Project Self-Hosted Architecture)

```
my-project/
├── .ui-mcp/
│   ├── config.toml           # Cấu hình runtime MCP server
│   ├── modules.lock          # Quản lý version active của 7 MCP modules
│   ├── skills.lock           # Quản lý version active của 9 Skills
│   └── server/               # ◄─── MCP SERVER TỰ HOST CỦA DỰ ÁN
│       ├── server.py         # Entrypoint chạy MCP Server qua stdio
│       ├── module_registry.py# Module registry cục bộ của project
│       ├── module_base.py    # Module base interface
│       ├── models/           # Pydantic schemas cục bộ
│       └── modules/          # 7 Modules tính toán chuyên sâu (color, layout, ...)
├── .agents/skills/           # Các thư mục skills cho AI Agent nạp context
│   ├── ui-fundamentals/
│   ├── ui-color-system/
│   └── ...
└── .cursor/mcp.json (hoặc .agents/mcp_config.json, .vscode, .zed, ...) 
    # Cấu hình IDE trỏ trực tiếp: python .ui-mcp/server/server.py
```

