"""
mcp_server.py — MCP Server entry point.

Loads all modules from modules.lock (auto-rollback on health_check failure),
then runs the MCP server via stdio transport.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server.fastmcp import FastMCP as MCPServer

from ui_ux_design.module_registry import ModuleRegistry
from ui_ux_design.platform import PROJECT_MODULES_LOCK

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s [%(name)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("ui-mcp")


def create_server(lock_path: Path | None = None) -> MCPServer:
    """Build the MCP server with all healthy modules registered."""
    server = MCPServer("ui-ux-design")
    registry = ModuleRegistry(lock_path=lock_path)

    # Load all modules — unhealthy ones auto-rollback or are skipped
    modules = registry.load_all(server)

    total_tools = sum(len(m.info.tools) for m in modules.values())
    logger.info(
        "ui-mcp server ready: %d modules, %d tools", len(modules), total_tools
    )

    for name, status in registry.status().items():
        if status.skipped:
            logger.warning("  ⚠ %s: SKIPPED (%s)", name, status.health_message)
        else:
            logger.info("  ✓ %s v%s: %s tools", name, status.version, len(status.tools))

    return server


async def _run() -> None:
    lock_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    server = create_server(lock_path)
    if hasattr(server, "run_stdio_async"):
        await server.run_stdio_async()
    else:
        await server.run(transport="stdio")


def serve() -> None:
    """Entry point: start MCP server on stdio."""
    asyncio.run(_run())


if __name__ == "__main__":
    serve()
