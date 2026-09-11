<div align="center">

  # 🎨 Anti-AI-UI Skills & MCP System (`ui-ux-design`)

  <p align="center">
    <strong>Hệ thống chuẩn hóa tư duy thiết kế UI/UX cho AI Coding Agents — Chống UI rác, hiểu sâu kiến trúc 2D / 2.5D / 3D.</strong>
  </p>

  <!-- Badges -->
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version"/>
    <img src="https://img.shields.io/badge/Package%20Manager-uv-DE5FE9?style=flat-square&logo=astral&logoColor=white" alt="uv"/>
    <img src="https://img.shields.io/badge/MCP-Protocol%20v1.0-blue?style=flat-square" alt="MCP Protocol"/>
    <img src="https://img.shields.io/badge/Tests-37%20Passed-brightgreen?style=flat-square" alt="Tests"/>
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-teal?style=flat-square" alt="Platform"/>
  </p>

</div>

---

## ⚡ Hướng Dẫn Cài Đặt Tuần Tự (Step-by-Step Setup)

Thực hiện theo đúng **5 bước** dưới đây để tích hợp trọn gói hệ thống Anti-AI-UI và MCP Server vào dự án của bạn:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Bước 1     │     │   Bước 2     │     │   Bước 3     │     │   Bước 4     │     │   Bước 5     │
│ Cài đặt CLI  │ ──> │ Khởi tạo vào │ ──> │ Cài gói cho  │ ──> │ Kiểm tra     │ ──> │ Sử dụng cùng │
│   toàn cục   │     │   dự án      │     │    .venv     │     │ hoạt động    │     │   AI Agent   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

### 📌 Bước 1: Cài đặt công cụ CLI `ui-mcp` (Chỉ cần làm 1 lần)

Chọn **MỘT** trong ba cách sau tùy môi trường máy của bạn:

- **Cách 1: Cài qua `uv tool` (Khuyên dùng — Nhanh nhất & cách ly sạch sẽ)**:
  ```bash
  uv tool install git+https://github.com/snn206/ui-ux-design.git
  ```

- **Cách 2: Cài qua `pip`**:
  ```bash
  pip install git+https://github.com/snn206/ui-ux-design.git
  ```

- **Cách 3: Nếu bạn clone mã nguồn repo về máy để đóng góp / chỉnh sửa**:
  ```bash
  git clone https://github.com/snn206/ui-ux-design.git
  cd ui-ux-design
  pip install -e .
  ```

> 💡 **Kiểm tra thành công:** Mở terminal bất kỳ và gõ:
> ```bash
> ui-mcp --version
> ```
> Nếu hiển thị phiên bản `ui-mcp` là bạn đã hoàn tất Bước 1.

---

### 📌 Bước 2: Khởi tạo vào dự án của bạn (`ui-mcp init`)

Mở terminal, chuyển vào thư mục dự án mà bạn muốn AI thiết kế UI:

```bash
cd /duong-dan-toi-du-an-cua-ban
ui-mcp init
```

Lệnh `ui-mcp init` sẽ tự động:
1. ✅ **Tạo Self-Hosted MCP Server**: Sao chép code server và 9 module tính toán vào `.ui-mcp/server/` trong dự án của bạn.
2. ✅ **Cài 10 bộ Kỹ năng Chống AI-UI**: Sao chép 10 skills vào `.agents/skills/` (chuẩn chung cho mọi AI IDE).
3. ✅ **Tự động cấu hình IDE**: Tạo sẵn file cấu hình kết nối đa nền tảng cho Cursor (`.cursor/mcp.json`), VS Code (`.vscode/settings.json`), Antigravity (`.agents/mcp_config.json`), Claude...

---

### 📌 Bước 3: Chuẩn bị môi trường Python cho server dự án

Self-hosted MCP Server chạy cục bộ trong dự án và cần 2 thư viện nền tảng: `mcp` và `pydantic`.

Tại thư mục dự án của bạn, hãy tạo môi trường `.venv` và cài gói:

- **Nếu dùng `uv` (Nhanh nhất)**:
  ```bash
  uv venv
  uv pip install mcp pydantic
  ```

- **Nếu dùng `python` / `pip` truyền thống**:
  - **Trên Windows**:
    ```cmd
    python -m venv .venv
    .venv\Scripts\pip install mcp pydantic
    ```
  - **Trên Linux / macOS**:
    ```bash
    python3 -m venv .venv
    .venv/bin/pip install mcp pydantic
    ```

> *(Nếu dự án của bạn đã có sẵn thư mục `.venv` và đã cài `mcp`, `pydantic`, bạn có thể bỏ qua bước này).*

---

### 📌 Bước 4: Kiểm tra và Khởi chạy thử (Verify)

Kiểm tra xem MCP Server của dự án đã sẵn sàng phục vụ chưa:

```bash
# Cách A: Dùng lệnh CLI có sẵn (chạy được trên mọi hệ điều hành)
ui-mcp serve

# Cách B: Hoặc chạy trực tiếp file server nội bộ của dự án
# Trên Windows:
python .ui-mcp/server/server.py
# Trên Linux / macOS:
python3 .ui-mcp/server/server.py
```

Khi màn hình hiển thị các dòng log sau nghĩa là server đã hoạt động trơn tru:
```text
INFO [module_registry] ✓ Module color v1.0.0 loaded (4 tools)
INFO [module_registry] ✓ Module layout v1.0.0 loaded (7 tools)
INFO [module_registry] ✓ Module typography v1.0.0 loaded (2 tools)
INFO [module_registry] ✓ Module animation v1.0.0 loaded (2 tools)
INFO [module_registry] ✓ Module depth_25d v1.0.0 loaded (4 tools)
INFO [module_registry] ✓ Module scene_3d v1.0.0 loaded (3 tools)
INFO [module_registry] ✓ Module quality v2.0.0 loaded (1 tools)
INFO [module_registry] ✓ Module prompt_engine v1.0.0 loaded (4 tools)
INFO [module_registry] ✓ Module component_spec v1.0.0 loaded (4 tools)
```
*(Bấm `Ctrl + C` để thoát chế độ test).*

---

### 📌 Bước 5: Sử dụng trong IDE & AI Coding Agent

Bây giờ bạn chỉ cần mở hoặc reload IDE (Cursor, VS Code, Antigravity, Claude Code...):
- **31 Công cụ MCP**: AI sẽ tự động gọi các tool tính toán khi cần (ví dụ: `calc_wcag_contrast`, `calc_type_scale`, `calc_grid`, `check_ai_smell`, `generate_ui_prompt`...).
- **10 Bộ Skills**: AI sẽ tự động kích hoạt các file hướng dẫn trong `.agents/skills/` mỗi khi bạn prompt về giao diện, màu sắc, bố cục, typography, hoặc motion.

---

## 📦 Quản Lý & Đổi Phiên Bản (GitHub Version Store)

Kho version được quản lý trực tiếp qua GitHub Releases:

```bash
# 1. Xem trạng thái phiên bản dự án hiện tại
ui-mcp version status

# 2. Duyệt danh sách các phiên bản có sẵn trên GitHub
ui-mcp version list

# 3. Đổi sang một phiên bản cụ thể (tự động tải và áp dụng vào dự án)
ui-mcp version switch v1.0.0

# 4. Cập nhật lên bản mới nhất
ui-mcp version switch latest

# 5. Quay lại phiên bản trước đó bất kỳ lúc nào nếu gặp lỗi
ui-mcp version rollback
```

---

## 🧠 Hệ Thống 10 Kỹ Năng & 9 Modules Tính Toán

### 10 Bộ Kỹ Năng (Anti-AI-UI Skills trong `.agents/skills/`)
1. **`ui-fundamentals`**: Nguyên lý nền tảng (Gestalt, CRAP, 8px grid, visual hierarchy, F/Z pattern).
2. **`ui-anti-patterns`**: Catalog 13 mùi "AI UI Smell" phổ biến nhất và cách khắc phục triệt để.
3. **`ui-prompt-framework`**: Tư duy thiết kế theo khung 11 section linh hoạt (không gò ép, áp dụng theo ngữ cảnh thực tế).
4. **`ui-color-system`**: Hệ thống màu sắc HSL, palette generation, WCAG contrast, dark mode tokens.
5. **`ui-typography`**: Typographic modular scale, line height, letter spacing, font pairing chuẩn xác.
6. **`ui-2d-layout`**: Kiến trúc layout 2D, flexbox, CSS Grid, spacing scale, responsive breakpoints.
7. **`ui-25d-depth`**: Kỹ thuật 2.5D: elevation shadows, parallax layers, z-index stacking, perspective.
8. **`ui-3d-scene`**: Kiến trúc 3D WebGL: Three.js/Babylon.js/Pygame, camera, 3-point lighting, PBR materials.
9. **`ui-animation`**: Motion design: Disney 12 principles, easing curves, spring physics, duration rules.
10. **`ui-mcp-tools`**: Hướng dẫn bản đồ gọi tool MCP cho AI Agent.

### 9 Modules Tính Toán (31 MCP Tools trong `.ui-mcp/server/`)
| Module | Số tool | Chức năng chính |
|---|:---:|---|
| **`color`** | 4 | Tính tỷ lệ tương phản WCAG 2.1, tạo palette HSL, sinh dark mode tokens, sinh gradient CSS |
| **`layout`** | 7 | Chia lưới CSS Grid, tính spacing scale 8px, preview lưới ASCII, phân tích bố cục |
| **`typography`** | 2 | Tính modular type scale theo tỷ lệ (Golden Ratio, Perfect Fourth...), gợi ý cặp font |
| **`animation`** | 2 | Tính cubic-bezier easing curve, gợi ý thời lượng chuyển động theo diện tích |
| **`depth_25d`** | 4 | Sinh chuỗi CSS box-shadow đa lớp, sắp xếp z-index stack, tính parallax offset |
| **`scene_3d`** | 3 | Gợi ý setup camera, 3-point lighting model, cấu hình PBR material |
| **`quality`** | 1 | Quét và phát hiện 13 lỗi AI UI Smell trong CSS/HTML |
| **`prompt_engine`**| 4 | Sinh prompt UI chuẩn 11-section, validate prompt, gợi ý section theo loại trang, audit cấu trúc |
| **`component_spec`**| 4 | Sinh đặc tả kỹ thuật chi tiết chuẩn studio cho Button, Card, Hero Section, Loader |

---

## ⚡ Bảng Tra Cứu Lệnh Nhanh (CLI Cheat-Sheet)

| Lệnh | Phân loại | Mô tả |
|---|---|---|
| **`ui-mcp init`** | Khởi tạo | Khởi tạo self-hosted server, copy 10 skills và cấu hình IDE vào dự án |
| **`ui-mcp serve`** | Chạy Server | Chạy MCP Server stdio kết nối với IDE/Agent |
| **`ui-mcp version status`** | Version | Kiểm tra phiên bản đang chạy và bản mới nhất trên GitHub |
| **`ui-mcp version list`** | Version | Liệt kê các release tag trên GitHub |
| **`ui-mcp version switch <tag>`**| Version | Đổi sang version từ GitHub (`v1.0.0`, `latest`, `local`) |
| **`ui-mcp version rollback`** | Version | Quay lại phiên bản trước đó của dự án |
| **`ui-mcp module status`** | Kiểm tra | Xem trạng thái sức khỏe (Health status) của 9 modules |
| **`ui-mcp skills list`** | Kiểm tra | Xem danh sách 10 skills và trạng thái active |
| **`ui-mcp prompt list`** | Prompts | Xem các mẫu prompt UI chuyên nghiệp có sẵn |
| **`npx @modelcontextprotocol/inspector ui-mcp serve`** | Kiểm thử | Mở giao diện Web UI (`http://localhost:5173`) để test trực quan 31 tools |
| **`pytest tests/`** | Kiểm thử | Chạy 37 bài unit tests tự động của hệ thống |

---

## 🛠️ Hỗ Trợ 20+ IDEs & CLIs

Hệ thống được thiết kế để hoạt động hoàn hảo trên mọi môi trường:
- **IDEs**: Cursor, VS Code, Antigravity (AGY), Windsurf, Trae, Zed, Continue.dev, Neovim...
- **CLIs & Agents**: Claude Code, Gemini CLI, Codex, OpenCode, Warp Terminal, Kilo...
- **Hệ điều hành**: Windows, macOS, Linux (tự động xử lý đường dẫn và Virtualenv).

---

## 📚 Tài Liệu Chi Tiết

- [docs/install-guide.md](docs/install-guide.md): Hướng dẫn cài đặt sâu và xử lý sự cố.
- [docs/architecture.md](docs/architecture.md): Tài liệu kiến trúc hệ thống, cơ chế cách ly và rollback.
