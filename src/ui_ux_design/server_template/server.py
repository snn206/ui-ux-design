"""
server.py — Self-Hosted Project MCP Server.

Runs as a standalone MCP server for this workspace:
- Loads local modules from .ui-mcp/server/modules/
- Reads active versions and rollback state from ../modules.lock
- Communicates via standard input/output (stdio) with IDEs/CLIs (Cursor, VS Code, AGY, Claude, etc.)
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

# Setup paths so local server modules and models are prioritized
SERVER_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SERVER_DIR.parent.parent.resolve()

# Auto-switch to project virtualenv if available and not currently active
_venv_dir = PROJECT_ROOT / ".venv"
_venv_py = (
    _venv_dir / "Scripts" / "python.exe"
    if sys.platform == "win32"
    else _venv_dir / "bin" / "python"
)
_in_this_venv = _venv_dir.exists() and Path(sys.prefix).resolve() == _venv_dir.resolve()
if _venv_py.exists() and not _in_this_venv:
    import os
    os.execv(str(_venv_py), [str(_venv_py), *sys.argv])

if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
src_dir = PROJECT_ROOT / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Reconfigure UTF-8 for Windows console / stdio
if sys.platform == "win32":
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8")
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

# Setup module aliasing if ui_ux_design is not installed in the current environment
try:
    import ui_ux_design.module_base
except ImportError:
    import types
    import module_base

    pkg = types.ModuleType("ui_ux_design")
    pkg.__path__ = [str(SERVER_DIR)]
    pkg.module_base = module_base
    sys.modules["ui_ux_design"] = pkg
    sys.modules["ui_ux_design.module_base"] = module_base

    import models
    pkg.models = models
    sys.modules["ui_ux_design.models"] = models

    for model_file in (SERVER_DIR / "models").glob("*.py"):
        if model_file.stem != "__init__":
            import importlib
            m = importlib.import_module(f"models.{model_file.stem}")
            setattr(models, model_file.stem, m)
            sys.modules[f"ui_ux_design.models.{model_file.stem}"] = m

    import module_registry
    pkg.module_registry = module_registry
    sys.modules["ui_ux_design.module_registry"] = module_registry

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from module_registry import ModuleRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("ui-mcp-selfhosted")


def create_server(lock_path: Path | None = None) -> MCPServer:
    """Build the self-hosted MCP server with all healthy local modules registered."""
    server = MCPServer("ui-ux-design")
    actual_lock = lock_path or (SERVER_DIR.parent / "modules.lock")
    modules_path = SERVER_DIR / "modules"

    registry = ModuleRegistry(lock_path=actual_lock, modules_dir=modules_path)

    # Load all modules — unhealthy ones auto-rollback or are skipped
    modules = registry.load_all(server)

    total_tools = sum(len(m.info.tools) for m in modules.values())
    logger.info(
        "Self-hosted project MCP server ready: %d modules, %d tools loaded from %s",
        len(modules), total_tools, SERVER_DIR
    )

    for name, status in registry.status().items():
        if status.skipped:
            logger.warning("  ⚠ %s: SKIPPED (%s)", name, status.health_message)
        else:
            logger.info("  ✓ %s v%s: %s tools", name, status.version, len(status.tools))

    return server


async def _run() -> None:
    lock_path = Path(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].endswith(".lock") else None
    server = create_server(lock_path)
    if hasattr(server, "run_stdio_async"):
        await server.run_stdio_async()
    else:
        await server.run(transport="stdio")


def serve() -> None:
    """Entry point: start MCP server on stdio."""
    try:
        asyncio.run(_run())
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    serve()
