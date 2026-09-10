"""cli/skills_cmd.py — ui-mcp skills {list,install,update,rollback,cache,verify}"""

from __future__ import annotations
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


@click.group(name="skills")
def skills_group() -> None:
    """Manage skill versions (independent of source code version)."""


@skills_group.command("list")
@click.option("--offline", is_flag=True, help="Only show locally cached skills")
def skills_list(offline: bool) -> None:
    """List all skills with active version and update availability."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    statuses = manager.list_skills(offline=offline)

    table = Table(box=box.ROUNDED, title="Skills", title_style="bold magenta")
    table.add_column("Skill", style="magenta")
    table.add_column("Active", style="white")
    table.add_column("Latest")
    table.add_column("Cached versions", style="dim")
    table.add_column("Status")

    for name, s in statuses.items():
        update_avail = s.get("update_available", False)
        status = "[yellow]↑ update[/yellow]" if update_avail else "[green]✓ up-to-date[/green]"
        if s.get("missing"):
            status = "[red]✗ missing[/red]"
        table.add_row(
            name,
            s.get("active", "—"),
            s.get("latest", "—"),
            ", ".join(s.get("cached", [])),
            status,
        )
    console.print(table)


@skills_group.command("status")
@click.argument("skill_name")
def skills_status(skill_name: str) -> None:
    """Show detailed status for a single skill."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    s = manager.status(skill_name)
    console.print(f"\n[bold magenta]{skill_name}[/bold magenta]")
    console.print(f"  Active   : {s.get('active', '—')}")
    console.print(f"  Latest   : {s.get('latest', '—')}")
    console.print(f"  Cached   : {', '.join(s.get('cached', []))}")
    if s.get("changelog"):
        console.print(f"  Changelog: {s['changelog']}")
    console.print()


@skills_group.command("install")
@click.argument("skill_spec")   # "ui-color-system" or "ui-color-system@1.2.0"
def skills_install(skill_spec: str) -> None:
    """Install a skill (latest or specific version). Example: ui-3d-scene@1.5.0"""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    if "@" in skill_spec:
        name, version = skill_spec.split("@", 1)
    else:
        name, version = skill_spec, "latest"

    with console.status(f"Installing {name}@{version}..."):
        try:
            installed = manager.install(name, version)
            console.print(f"[green]✓[/green] Installed [magenta]{name}[/magenta] v[bold]{installed}[/bold]")
        except Exception as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            raise SystemExit(1)


@skills_group.command("update")
@click.argument("skill_name", required=False)
@click.option("--all", "update_all", is_flag=True, help="Update all skills")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation for breaking changes")
def skills_update(skill_name: str | None, update_all: bool, yes: bool) -> None:
    """Update a skill (or all) to the latest version."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()

    targets = None if update_all else ([skill_name] if skill_name else None)
    if not targets and not update_all:
        console.print("[yellow]Specify a skill name or use --all[/yellow]")
        raise SystemExit(1)

    results = manager.update(skill_name, confirm_breaking=not yes)
    for name, new_ver in results.items():
        console.print(f"[green]✓[/green] [magenta]{name}[/magenta] → v[bold]{new_ver}[/bold]")


@skills_group.command("rollback")
@click.argument("skill_name")
@click.option("--to", "to_version", default=None, help="Target version")
def skills_rollback(skill_name: str, to_version: str | None) -> None:
    """Roll back a skill to its previous (or specified) version."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    try:
        rolled = manager.rollback(skill_name, to_version)
        console.print(
            f"[green]✓[/green] Skill [magenta]{skill_name}[/magenta] rolled back to [bold]{rolled}[/bold]"
        )
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise SystemExit(1)


@click.group(name="cache")
def cache_group() -> None:
    """Manage skills cache."""


@cache_group.command("list")
def cache_list() -> None:
    """List all versions in the local skills cache."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    cache = manager.list_cache()
    table = Table(box=box.SIMPLE, title="Skills Cache")
    table.add_column("Skill")
    table.add_column("Cached Versions")
    table.add_column("Size")
    for name, info in cache.items():
        table.add_row(name, ", ".join(info["versions"]), info.get("size", "?"))
    console.print(table)


@cache_group.command("clear")
@click.option("--keep-active", is_flag=True, default=True, help="Keep active versions")
@click.confirmation_option(prompt="Clear old cached skill versions?")
def cache_clear(keep_active: bool) -> None:
    """Remove old cached skill versions to free up space."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    freed = manager.clear_cache(keep_active=keep_active)
    console.print(f"[green]✓[/green] Freed {freed} cached versions.")


@cache_group.command("path")
def cache_path() -> None:
    """Print the skills cache directory path."""
    from ui_ux_design.platform import USER_CACHE_DIR
    console.print(str(USER_CACHE_DIR))


skills_group.add_command(cache_group, name="cache")


@skills_group.command("verify")
def skills_verify() -> None:
    """Verify SHA256 checksums of all active skills."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    results = manager.verify()
    all_ok = True
    for name, ok in results.items():
        icon = "[green]✓[/green]" if ok else "[red]✗ TAMPERED[/red]"
        console.print(f"  {icon} {name}")
        if not ok:
            all_ok = False
    if not all_ok:
        console.print("[red]\nSome skills failed verification. Re-install them.[/red]")
        raise SystemExit(1)
    else:
        console.print("[green]\nAll skills verified.[/green]")


@skills_group.command("fetch-index")
def fetch_index() -> None:
    """Refresh the skills registry index from remote."""
    from ui_ux_design.skills_manager import SkillsManager
    manager = SkillsManager()
    with console.status("Fetching index..."):
        index = manager.fetch_index()
    count = len(index.get("skills", {}))
    console.print(f"[green]✓[/green] Index refreshed: {count} skills available.")
