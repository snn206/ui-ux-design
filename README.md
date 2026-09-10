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
    <img src="https://img.shields.io/badge/Tests-17%20Passed-brightgreen?style=flat-square" alt="Tests"/>
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-teal?style=flat-square" alt="Platform"/>
  </p>

</div>

---

## 🚀 1. Luồng Hoạt Động & Cài Đặt (Architecture Workflow)

Hệ thống được thiết kế theo mô hình **Global CLI + Project Self-Hosted MCP Server**:

1. **Cài đặt CLI toàn cục (Global Install - Chỉ làm 1 lần)**:
   ```bash
   # Cài đặt qua uv (Khuyên dùng):
   uv tool install --editable .

   # Hoặc cài đặt qua pip:
   pip install --user .
   ```

2. **Vào bất kỳ dự án nào và Khởi tạo Tự Host (Project Self-Hosting)**:
   ```bash
   cd my-project
   ui-mcp init
   ```
   Lệnh `init` sẽ:
   - **Tự host MCP Server trong dự án**: Sao chép mã nguồn server, 9 modules tính toán và models vào `.ui-mcp/server/` của dự án.
   - Sao chép 10 bộ kỹ năng chống AI UI vào `.agents/skills/` (bao gồm `ui-prompt-framework`).
   - Cấu hình IDE (Cursor, VS Code, Antigravity...) kết nối đa nền tảng chuẩn xác.

3. **Cơ Chế Đa Nền Tảng (Windows / macOS / Linux) Của Self-Hosted Server**:
   - **Tự định vị động (Zero-Hardcode)**: Server `.ui-mcp/server/server.py` tự định vị project root qua `Path(__file__)`, không phụ thuộc vào thư mục làm việc (CWD) hay đường dẫn tuyệt đối của máy cá nhân.
   - **Tự động hook Virtualenv (Smart Python Re-exec)**:
     - Trên **Windows**: Tự động phát hiện `.venv\Scripts\python.exe`
     - Trên **Linux/macOS**: Tự động phát hiện `.venv/bin/python`
     - Kể cả khi IDE gọi server bằng lệnh Python mặc định của hệ thống (`python` trên Win hoặc `python3` trên POSIX), `server.py` vẫn tự động chuyển sang môi trường `.venv` nội bộ để nạp đầy đủ dependencies (`mcp`, `pydantic`,...).
   - **Cấu hình IDE tương thích 100%**:
     - *Cursor & VS Code*: Dùng biến `${workspaceFolder}` theo đúng chuẩn OS (`.venv/Scripts/python.exe` trên Windows, `.venv/bin/python` trên POSIX).
     - *Antigravity IDE (`.agents/mcp_config.json`)*: Dùng đường dẫn tương đối (`"command": "python"` trên Win, `"python3"` trên POSIX, `"args": [".ui-mcp/server/server.py"]`) do Antigravity không hỗ trợ biến `${workspaceFolder}`.
     - *Cách chạy đồng nhất*: Có thể dùng lệnh `ui-mcp serve` trên mọi hệ điều hành.

4. **Khởi chạy MCP Server của Dự án**:
   - Khi mở IDE, IDE sẽ tự động kích hoạt MCP Server cục bộ của dự án.
   - Hoặc chạy thủ công trong thư mục dự án:
     ```bash
     # Trên Windows:
     python .ui-mcp/server/server.py
     # Trên Linux / macOS:
     python3 .ui-mcp/server/server.py
     # Hoặc dùng CLI chung:
     ui-mcp serve
     ```


---

## ⚡ 2. Bảng Tổng Hợp Lệnh Chạy (Run Commands Cheat-Sheet)

| Lệnh | Mô tả |
|---|---|
| **`ui-mcp version status`** | **Xem tổng quan version**: trạng thái active, bản mới nhất trên GitHub, cache |
| **`ui-mcp version list`** | **Duyệt Kho Version**: xem các release có sẵn trên GitHub (`v1.0.0`, `v1.1.0`...) |
| **`ui-mcp version switch <tag>`** | **Đổi version tức thì**: tải từ GitHub và kích hoạt (`v1.0.0`, `latest`, `local`) |
| **`ui-mcp version pull <tag>`** | **Tải trước về máy**: lưu trữ bản release vào local cache (~/.config) |
| **`ui-mcp version rollback`** | **Rollback nhanh**: quay lại version trước đó của dự án |
| **`ui-mcp serve`** | **Chạy MCP Server** (kết nối stdio cho IDEs/CLIs như Cursor, VS Code, Claude, Zed, AGY...) |
| **`python -m ui_ux_design.mcp_server`** | Chạy MCP Server trực tiếp qua Python runtime |
| **`npx @modelcontextprotocol/inspector ui-mcp serve`** | **Mở Web UI** (`http://localhost:5173`) để test trực quan 31 MCP tools |
| **`ui-mcp init`** | **Khởi tạo dự án**: tự động phát hiện IDE/OS, copy 10 Skills và tạo file config kết nối |
| **`ui-mcp init --ide cursor,vscode,agy`** | Khởi tạo với cấu hình cụ thể cho Cursor, VS Code, Antigravity |
| **`ui-mcp module status`** | Kiểm tra trạng thái sức khỏe (Health status) và version của 9 Modules |
| **`ui-mcp module rollback <name>`** | Rollback một module về version ổn định trước đó |
| **`ui-mcp skills list`** | Xem danh sách 10 bộ skills và version đang active |
| **`ui-mcp skills rollback <skill>`** | Rollback một skill về version trước đó |
| **`ui-mcp prompt list`** | Liệt kê các prompt templates thiết kế UI có sẵn |
| **`ui-mcp prompt show <name>`** | Hiển thị nội dung hướng dẫn của một prompt template |
| **`ui-mcp prompt compose <p1> <p2>`** | Ghép các prompt theo ngữ cảnh (`--platform`, `--framework`) |
| **`pytest tests/`** | Chạy toàn bộ Test Suite kiểm thử hệ thống |

---

## 🛠️ 3. Hỗ Trợ 20+ IDEs & CLIs

Hệ thống hỗ trợ tự động nhận diện và tạo cấu hình MCP kết nối cho:
- **IDEs**: Cursor, VS Code, Antigravity (AGY), Zed, Windsurf, Trae, Continue.dev, Kiro, Minimax, Neovim.
- **CLIs**: Claude Code, Gemini CLI, Codex, OpenCode, Kilo, Warp Terminal, Codebuff, Freebuff, Grok, Mistral, Pi.

---

## 📚 4. Tài Liệu Chi Tiết

- [docs/install-guide.md](docs/install-guide.md): Hướng dẫn cài đặt cross-platform và chi tiết các lệnh chạy.
- [docs/architecture.md](docs/architecture.md): Thiết kế kiến trúc sâu, cơ chế quản lý version và rollback.

