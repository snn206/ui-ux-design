"""cli/main.py — ui-mcp CLI entry point."""

from __future__ import annotations

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(package_name="ui-ux-design")
def main() -> None:
    """
    \b
    ui-mcp — Anti-AI-UI Skills System
    MCP tools + Skills for structured, quality UI generation.

    \b
    Quick start:
      pip install ui-ux-design      # install globally
      cd my-project
      ui-mcp init                   # init project (copies skills, IDE configs)
      ui-mcp serve                  # start MCP server
    """


@main.command()
@click.option("--lock", default=None, help="Path to modules.lock (default: .ui-mcp/modules.lock)")
def serve(lock: str | None) -> None:
    """Start the MCP server (stdio transport). Prioritizes project self-hosted server."""
    import subprocess
    import sys
    from pathlib import Path
    from ui_ux_design.platform import PROJECT_ROOT

    local_server = PROJECT_ROOT / ".ui-mcp" / "server" / "server.py"
    if local_server.exists():
        # Execute project's self-hosted server directly
        args = [sys.executable, str(local_server)]
        if lock:
            args.append(lock)
        try:
            subprocess.run(args)
        except KeyboardInterrupt:
            pass
    else:
        # Fallback to package runner
        from ui_ux_design.mcp_server import serve as _serve
        _serve()



# Attach sub-command groups
from ui_ux_design.cli.init_cmd import init_cmd
from ui_ux_design.cli.module_cmd import module_group
from ui_ux_design.cli.skills_cmd import skills_group
from ui_ux_design.cli.prompt_cmd import prompt_group
from ui_ux_design.cli.version_cmd import version_group

main.add_command(init_cmd, name="init")
main.add_command(module_group, name="module")
main.add_command(skills_group, name="skills")
main.add_command(prompt_group, name="prompt")
main.add_command(version_group, name="version")


