# 🚀 Hướng Dẫn Cài Đặt & Sử Dụng Toàn Diện (Cross-Platform)

Hệ thống Anti-AI-UI hỗ trợ đầy đủ trên **Windows, macOS và Linux**.

---

## 1. Cài đặt Hệ thống (Global / User Environment)

Bạn có thể cài đặt công cụ toàn cục qua `pip`, `uv` hoặc trực tiếp từ Git repository.

### Cách 1: Cài đặt qua uv (Khuyên dùng - Nhanh nhất)
```bash
uv tool install ui-ux-design
# Hoặc cài từ git source:
uv tool install git+https://github.com/snn206/ui-ux-design.git
```

### Cách 2: Cài đặt qua pip
```bash
pip install --user ui-ux-design
# Hoặc từ source repo:
pip install --user git+https://github.com/snn206/ui-ux-design.git
```

### Cách 3: Phát triển Local (Editable mode)
```bash
git clone https://github.com/snn206/ui-ux-design.git
cd ui-ux-design
uv pip install -e ".[dev]"
```

Kiểm tra lệnh CLI đã hoạt động:
```bash
ui-mcp --version
```

---

## 2. Khởi tạo vào Project bất kỳ (`ui-mcp init`)

Khi bắt đầu một project mới hoặc muốn nạp bộ skills vào repo hiện tại:

```bash
cd /path/to/my-project

# Tự động phát hiện IDE/CLI đang dùng và tạo config + copy skills:
ui-mcp init

# Hoặc chỉ định rõ IDE bạn muốn cấu hình:
ui-mcp init --ide cursor,vscode,agy
# Hoặc tạo cấu hình cho tất cả:
ui-mcp init --ide all
```

Lệnh `ui-mcp init` sẽ:
1. Tạo thư mục `.ui-mcp/` chứa:
   - `config.toml`: Cấu hình server
   - `modules.lock`: Quản lý version 9 module MCP
   - `skills.lock`: Quản lý version 10 bộ skills
2. Copy 10 bộ skills vào `.agents/skills/` (bao gồm `ui-prompt-framework`)
3. Tạo self-hosted server tại `.ui-mcp/server/` với đầy đủ models, modules và khả năng tự động nhận diện venv đa nền tảng.
3. Sinh file cấu hình MCP kết nối tự động cho các IDE/CLI được chọn.

---

## 3. Lệnh Chạy & Khởi Động Hệ Thống (Run Commands)

### 3.1. Lệnh chạy MCP Server (Cho Agent / IDE / CLI kết nối)
Lệnh này khởi động MCP Server theo chuẩn stdio transport để AI Agent kết nối và gọi các công cụ thiết kế:

```bash
ui-mcp serve
```
*(Hoặc chạy qua Python module:* `python -m ui_ux_design.mcp_server`*)*

### 3.2. Lệnh chạy Web UI tương tác thử nghiệm (MCP Inspector)
Dùng lệnh này để mở giao diện Web trên trình duyệt, giúp bạn test trực quan từng công cụ trong số 18 tools (tính màu, layout 2D, depth 2.5D, 3D scene, animation...):

```bash
npx @modelcontextprotocol/inspector ui-mcp serve
```
Trình duyệt sẽ mở tại `http://localhost:5173` để bạn nhập thông số và bấm Run thử trực tiếp.

### 3.3. Các lệnh chạy quản lý & kiểm tra nhanh

- **Kiểm tra trạng thái các module MCP:**
  ```bash
  ui-mcp module status
  ```
- **Xem danh sách và phiên bản các skills:**
  ```bash
  ui-mcp skills list
  ```
- **Xem và thử nghiệm Prompt templates:**
  ```bash
  ui-mcp prompt list
  ui-mcp prompt show system_ui
  ```
- **Chạy toàn bộ 17 Test Unit kiểm tra hệ thống:**
  ```bash
  uv run --with pytest pytest tests/
  ```

---

## 4. Kết Nối IDEs & CLIs (Quy Chuẩn Đa Nền Tảng)

Hệ thống hỗ trợ tự động cấu hình cho hơn 20 IDE và CLI phổ biến, đảm bảo chạy đúng trên cả **Windows, macOS và Linux**:

### 4.1. Quy chuẩn Path Đa Nền Tảng:
- **Cursor / VS Code / Windsurf / Trae**: Hỗ trợ mở rộng biến workspace. `ui-mcp init` sẽ sinh:
  - Windows: `"command": "${workspaceFolder}/.venv/Scripts/python.exe"` (hoặc `"python"`)
  - Linux/macOS: `"command": "${workspaceFolder}/.venv/bin/python"` (hoặc `"python3"`)
  - `"args": ["${workspaceFolder}/.ui-mcp/server/server.py"]`
- **Antigravity IDE (`.agents/mcp_config.json`)**: Antigravity không parse biến `${workspaceFolder}`, do đó sử dụng đường dẫn tương đối từ workspace root:
  - Windows: `"command": "python"`
  - Linux/macOS: `"command": "python3"`
  - `"args": [".ui-mcp/server/server.py"]`
- **Tự động hook Virtualenv**: Khi `server.py` được khởi động, nó tự động kiểm tra xem project có `.venv` hay không (`.venv\Scripts\python.exe` trên Windows, `.venv/bin/python` trên POSIX). Nếu có, server sẽ tự động re-exec vào môi trường ảo của project để nạp đầy đủ dependencies.

### 4.2. Danh sách IDEs & CLIs hỗ trợ:
- **Cursor**: Tự động sinh `.cursor/mcp.json`
- **VS Code**: Tự động sinh `.vscode/mcp.json` (hỗ trợ stdio transport)
- **Antigravity (AGY)**: Tự động cấu hình `.agents/mcp_config.json`
- **Zed**: Tự động chèn `context_servers` vào `.zed/settings.json`
- **Windsurf**: Tự động tạo `.windsurf/mcp_config.json`
- **Trae**: Tự động tạo `.trae/mcp_config.json`
- **Continue.dev**: Tự động tạo `.continue/config.yaml`
- **Kiro / Minimax**: Tự động cấu hình file mcp json tương ứng
- **Neovim (Avante / CodeCompanion)**: In snippet cấu hình Lua vào terminal.
- **Claude Code**: Sinh snippet `.ui-mcp/claude_snippet.json`
- **Gemini CLI**: Hướng dẫn thêm server vào `settings.json`
- **Codex**: Tự động sinh `.ui-mcp/codex_snippet.json`
- **OpenCode**: Tự động sinh `.opencode/config.json`
- **Kilo**: Tự động sinh `.kilo/mcp.json`
- **Warp Terminal**: Tự động sinh `.ui-mcp/warp_snippet.json`
- **Codebuff / Freebuff**: Tự động cấu hình `.codebuff/mcp.json` / `.freebuff/mcp.json`
- **Grok / Mistral / Pi**: Hướng dẫn cấu hình manual khi kết nối stdio.

### 3.4. Quản lý & Chuyển đổi Version từ GitHub Store (`ui-mcp version`)
Kho version chính thức được lưu trữ trực tiếp trên GitHub: `https://github.com/snn206/ui-ux-design`. Bạn có thể duyệt, tải về cache máy và đổi version của toàn bộ hệ thống skills & modules chỉ bằng một lệnh:

```bash
# Xem trạng thái phiên bản dự án hiện tại và so sánh với GitHub:
ui-mcp version status

# Duyệt danh sách các phiên bản có sẵn trên GitHub (v1.0.0, v1.1.0, v1.2.0...):
ui-mcp version list

# Chuyển sang một phiên bản cụ thể (tự động tải từ GitHub releases và áp dụng):
ui-mcp version switch v1.0.0

# Chuyển sang bản phát hành mới nhất:
ui-mcp version switch latest

# Chuyển sang dùng mã nguồn phát triển cục bộ:
ui-mcp version switch local

# Tải trước gói release về local cache máy (~/.config/ui-ux-design):
ui-mcp version pull v1.1.0

# Quay lại phiên bản trước đó bất kỳ lúc nào:
ui-mcp version rollback
```

---

## 4. Quản lý Rollback Modules & Skills Cục Bộ

### Quản lý Module MCP:
```bash
# Kiểm tra trạng thái các module:
ui-mcp module status

# Danh sách version của một module:
ui-mcp module list color

# Rollback module về version trước nếu gặp lỗi:
ui-mcp module rollback color

# Pin module tại một version nhất định:
ui-mcp module pin color 1.0.0
```

### Quản lý Skills & Rollback Skills:
```bash
# Xem danh sách skills đã cài và phiên bản active:
ui-mcp skills list

# Tải và cập nhật một skill cụ thể:
ui-mcp skills install ui-fundamentals --version 1.1.0

# Rollback skill về phiên bản cũ:
ui-mcp skills rollback ui-fundamentals

# Kiểm tra tính toàn vẹn (SHA256 checksum):
ui-mcp skills verify
```

---

## 5. Nạp Prompt Templates (Layer 3)

Agent hoặc lập trình viên có thể truy xuất các prompt mẫu đã được chuẩn hóa:

```bash
# Xem danh sách prompt:
ui-mcp prompt list

# Đọc nội dung 1 prompt:
ui-mcp prompt show system_ui

# Ghép (compose) nhiều prompt lại với nhau:
ui-mcp prompt compose system_ui 2d_layout review_checklist --platform web --framework react
```
