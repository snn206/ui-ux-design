"""
cli/prompt_cmd.py — ui-mcp prompt {list,load,compose,show}
"""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich import box

from ui_ux_design.prompts import prompt_loader

console = Console()


@click.group(name="prompt")
def prompt_group() -> None:
    """Manage and inspect UI design prompt templates."""
    pass


@prompt_group.command(name="list")
def list_prompts() -> None:
    """List all available prompt templates."""
    templates = prompt_loader.list_templates()
    if not templates:
        console.print("[yellow]No prompt templates found.[/yellow]")
        return

    table = Table(title="Available UI Prompt Templates", box=box.ROUNDED)
    table.add_column("Template Name", style="bold cyan")
    table.add_column("Source Path", style="dim")

    for name in templates:
        try:
            path = prompt_loader.resolve_path(name)
            table.add_row(name, str(path))
        except FileNotFoundError:
            table.add_row(name, "unknown")

    console.print(table)


@prompt_group.command(name="show")
@click.argument("name")
def show_prompt(name: str) -> None:
    """Render prompt template with Rich Markdown formatting."""
    try:
        content = prompt_loader.load(name)
        console.print(Markdown(content))
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")


@prompt_group.command(name="load")
@click.argument("name")
@click.option("--output", "-o", type=click.Path(), default=None, help="Save prompt output to file")
def load_prompt(name: str, output: str | None) -> None:
    """Print raw prompt content (ideal for piping or AI injection)."""
    try:
        content = prompt_loader.load(name)
        if output:
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
            console.print(f"[green]✓[/green] Saved prompt to {out_path}")
        else:
            click.echo(content)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")


@prompt_group.command(name="compose")
@click.argument("names", nargs=-1, required=True)
@click.option("--platform", default="web", help="Target platform (web, mobile, desktop)")
@click.option("--framework", default="vanilla", help="UI framework (vanilla, react, vue, flutter)")
@click.option("--output", "-o", type=click.Path(), default=None, help="Save composed prompt to file")
def compose_prompt(names: tuple[str, ...], platform: str, framework: str, output: str | None) -> None:
    """Compose multiple templates into one unified system prompt."""
    try:
        composed = prompt_loader.compose(*names)
        composed = prompt_loader.with_context(composed, platform=platform, framework=framework)
        if output:
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(composed, encoding="utf-8")
            console.print(f"[green]✓[/green] Saved composed prompt to {out_path}")
        else:
            click.echo(composed)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
