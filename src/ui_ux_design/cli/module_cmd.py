"""cli/module_cmd.py — ui-mcp module {list,rollback,status,reload,pin}"""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


@click.group(name="module")
def module_group() -> None:
    """Manage MCP module versions (list, rollback, status, reload, pin)."""


@module_group.command("list")
def module_list() -> None:
    """List all modules with their version and status."""
    from ui_ux_design.module_registry import ModuleRegistry
    registry = ModuleRegistry()
    registry.load_all()
    statuses = registry.status()

    table = Table(box=box.ROUNDED, title="MCP Modules", title_style="bold cyan")
    table.add_column("Module", style="cyan")
    table.add_column("Version", style="white")
    table.add_column("Status")
    table.add_column("Tools", justify="right")
    table.add_column("Message", style="dim")

    for name, s in statuses.items():
        status_icon = "✓" if s.healthy else ("⚠ SKIPPED" if s.skipped else "✗")
        status_style = "green" if s.healthy else "red"
        table.add_row(
            name, s.version,
            f"[{status_style}]{status_icon}[/{status_style}]",
            str(len(s.tools)),
            s.health_message[:60],
        )
    console.print(table)


@module_group.command("rollback")
@click.argument("module_name")
@click.option("--to", "to_version", default=None, help="Target version (default: previous)")
def module_rollback(module_name: str, to_version: str | None) -> None:
    """Roll back a module to its previous (or specified) version."""
    from ui_ux_design.module_registry import ModuleRegistry
    registry = ModuleRegistry()
    try:
        rolled = registry.rollback(module_name, to_version)
        console.print(f"[green]✓[/green] Module [cyan]{module_name}[/cyan] rolled back to [bold]{rolled}[/bold]")
    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise SystemExit(1)


@module_group.command("status")
@click.argument("module_name", required=False)
@click.pass_context
def module_status(ctx: click.Context, module_name: str | None = None) -> None:
    """Show detailed status of a single module (or all modules if omitted)."""
    if not module_name:
        ctx.invoke(module_list)
        return
    from ui_ux_design.module_registry import ModuleRegistry
    registry = ModuleRegistry()
    registry.load_all()
    statuses = registry.status()
    s = statuses.get(module_name)
    if not s:
        console.print(f"[red]Module '{module_name}' not found.[/red]")
        raise SystemExit(1)

    console.print(f"\n[bold cyan]{module_name}[/bold cyan]")
    console.print(f"  Version : {s.version}")
    console.print(f"  Status  : {'[green]healthy[/green]' if s.healthy else '[red]unhealthy[/red]'}")
    console.print(f"  Tools   : {', '.join(s.tools) or '(none)'}")
    console.print(f"  Message : {s.health_message}\n")


@module_group.command("reload")
@click.argument("module_name")
def module_reload(module_name: str) -> None:
    """Hot-reload a module without restarting the server (dev mode)."""
    from ui_ux_design.module_registry import ModuleRegistry
    registry = ModuleRegistry()
    health = registry.hot_reload(module_name)
    if health.healthy:
        console.print(f"[green]✓[/green] Module [cyan]{module_name}[/cyan] reloaded.")
    else:
        console.print(f"[red]✗[/red] Reload failed: {health.message}")


@module_group.command("pin")
@click.argument("module_spec")  # format: "color@1.0.0"
def module_pin(module_spec: str) -> None:
    """Pin a module to a specific version (e.g. color@1.0.0)."""
    if "@" not in module_spec:
        console.print("[red]Format: ui-mcp module pin <name>@<version>[/red]")
        raise SystemExit(1)
    name, version = module_spec.split("@", 1)
    from ui_ux_design.module_registry import ModuleRegistry
    registry = ModuleRegistry()
    registry.pin(name, version)
    console.print(f"[green]✓[/green] Module [cyan]{name}[/cyan] pinned to [bold]{version}[/bold]")
