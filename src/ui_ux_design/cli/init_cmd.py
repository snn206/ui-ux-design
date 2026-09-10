"""
cli/init_cmd.py — ui-mcp init

Copies skills and IDE configs into the current project.
Detects installed IDEs/CLIs automatically.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import click
from rich.console import Console

console = Console()

ALL_IDES = [
    "agy", "cursor", "vscode", "kiro", "trae",
    "windsurf", "zed", "continue", "minimax", "neovim",
]
ALL_CLIS = [
    "claude", "gemini", "codex", "opencode", "kilo",
    "warp", "codebuff", "freebuff", "grok", "mistral", "pi",
]

# ── Config templates (MCP server block shared across IDEs) ─────────────────────

def _detect_python(project_root: Path, var: bool = True) -> str:
    """Detect python executable for the project, preferring local venv across Win/Mac/Linux."""
    venv_python = project_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return "${workspaceFolder}/.venv/bin/python" if var else str(venv_python.resolve())
    venv_win = project_root / ".venv" / "Scripts" / "python.exe"
    if venv_win.exists():
        return "${workspaceFolder}/.venv/Scripts/python.exe" if var else str(venv_win.resolve())
    if not var:
        return sys.executable
    if sys.platform == "win32":
        return "python"
    if shutil.which("python3") and not shutil.which("python"):
        return "python3"
    return "python"



def _server_block(project_root: Path, var: bool = True) -> dict:
    """Return the MCP server config dict pointing to project's self-hosted server."""
    root_path = project_root.resolve() if not var else project_root
    cwd = "${workspaceFolder}" if var else str(root_path)
    cfg_path = "${workspaceFolder}/.ui-mcp/config.toml" if var else str(root_path / ".ui-mcp/config.toml")
    py_cmd = _detect_python(project_root, var=var)
    server_script = "${workspaceFolder}/.ui-mcp/server/server.py" if var else str(root_path / ".ui-mcp/server/server.py")
    return {
        "command": py_cmd,
        "args": [server_script],
        "cwd": cwd,
        "env": {"UI_MCP_CONFIG": cfg_path},
    }


def _mcp_servers_json(project_root: Path, var: bool = True) -> dict:
    return {"mcpServers": {"ui-ux-design": _server_block(project_root, var)}}

def _mcp_servers_json_vscode(project_root: Path) -> dict:
    block = _server_block(project_root, var=True)
    block["type"] = "stdio"
    return {"servers": {"ui-ux-design": block}}


def _zed_config(project_root: Path) -> str:
    block = _server_block(project_root, var=False)
    return json.dumps({
        "context_servers": {
            "ui-ux-design": {
                "command": {"path": block["command"], "args": block["args"]}
            }
        }
    }, indent=2)


def _continue_config(project_root: Path) -> str:
    b = _server_block(project_root, var=False)
    cmd = json.dumps(b['command'])
    args = json.dumps(b['args'])
    cfg = json.dumps(b['env']['UI_MCP_CONFIG'])
    return (
        f"mcpServers:\n"
        f"  - name: ui-ux-design\n"
        f"    command: {cmd}\n"
        f"    args: {args}\n"
        f"    env:\n"
        f"      UI_MCP_CONFIG: {cfg}\n"
    )



def _neovim_guide(project_root: Path) -> str:
    b = _server_block(project_root, var=False)
    return (
        f"-- Add to ~/.config/nvim/init.lua (avante.nvim or codecompanion):\n"
        f"require('avante').setup({{\n"
        f"  mcp = {{\n"
        f"    servers = {{\n"
        f"      ['ui-ux-design'] = {{\n"
        f"        cmd = {{ '{b['command']}', {', '.join(repr(a) for a in b['args'])} }},\n"
        f"      }}\n"
        f"    }}\n"
        f"  }}\n"
        f"}})\n"
    )


def _gemini_guide(project_root: Path) -> str:
    b = _server_block(project_root, var=False)
    return (
        f"# Add to ~/.gemini/settings.json:\n"
        + json.dumps({"mcpServers": {"ui-ux-design": b}}, indent=2)
    )


def _manual_guide(tool: str):
    def _guide(project_root: Path) -> str:
        b = _server_block(project_root, var=False)
        return (
            f"# {tool} does not natively support MCP.\n"
            f"# Run the server manually and pipe its output:\n"
            f"# {b['command']} {' '.join(b['args'])}\n"
        )
    return _guide


IDE_CONFIG_MAP = {
    "agy":      (".agents/mcp_config.json",        lambda r: json.dumps(_mcp_servers_json(r, var=False), indent=2)),
    "cursor":   (".cursor/mcp.json",               lambda r: json.dumps(_mcp_servers_json(r, var=True), indent=2)),
    "vscode":   (".vscode/mcp.json",               lambda r: json.dumps(_mcp_servers_json_vscode(r), indent=2)),
    "kiro":     (".kiro/mcp.json",                  lambda r: json.dumps(_mcp_servers_json(r), indent=2)),
    "trae":     (".trae/mcp_config.json",           lambda r: json.dumps(_mcp_servers_json(r), indent=2)),
    "windsurf": (".windsurf/mcp_config.json",       lambda r: json.dumps(_mcp_servers_json(r), indent=2)),
    "zed":      (".zed/settings.json",              _zed_config),
    "continue": (".continue/config.yaml",           _continue_config),
    "minimax":  (".minimax/mcp.json",               lambda r: json.dumps(_mcp_servers_json(r), indent=2)),
    "neovim":   (None,                              _neovim_guide),
    # CLIs
    "claude":   (".ui-mcp/claude_snippet.json",     lambda r: json.dumps(_mcp_servers_json(r, var=False), indent=2)),
    "gemini":   (None,                              _gemini_guide),
    "codex":    (".ui-mcp/codex_snippet.json",      lambda r: json.dumps({"mcp_servers": {"ui-ux-design": _server_block(r, False)}}, indent=2)),
    "opencode": (".opencode/config.json",           lambda r: json.dumps({"mcp": {"servers": {"ui-ux-design": _server_block(r, False)}}}, indent=2)),
    "kilo":     (".kilo/mcp.json",                  lambda r: json.dumps(_mcp_servers_json(r, False), indent=2)),
    "warp":     (".ui-mcp/warp_snippet.json",       lambda r: json.dumps({"servers": [{"name": "ui-ux-design", **_server_block(r, False)}]}, indent=2)),
    "codebuff": (".codebuff/mcp.json",              lambda r: json.dumps(_mcp_servers_json(r, False), indent=2)),
    "freebuff": (".freebuff/mcp.json",              lambda r: json.dumps(_mcp_servers_json(r, False), indent=2)),
    "grok":     (None,                              _manual_guide("Grok")),
    "mistral":  (None,                              _manual_guide("Mistral")),
    "pi":       (None,                              _manual_guide("Pi")),
}


# ── Detection logic ────────────────────────────────────────────────────────────


def detect_tools(project_root: Path) -> list[str]:
    detected = []
    dir_signals = {
        "agy": ".agents", "cursor": ".cursor", "vscode": ".vscode",
        "kiro": ".kiro", "trae": ".trae", "windsurf": ".windsurf",
        "zed": ".zed", "continue": ".continue", "minimax": ".minimax",
        "opencode": ".opencode", "kilo": ".kilo", "codebuff": ".codebuff",
        "freebuff": ".freebuff",
    }
    for tool, dirname in dir_signals.items():
        if (project_root / dirname).exists():
            detected.append(tool)

    cli_signals = {
        "claude": "claude", "gemini": "gemini", "codex": "codex",
        "warp": "warp", "grok": "grok", "mistral": "mistral", "kilo": "kilo",
    }
    for tool, cmd in cli_signals.items():
        if tool not in detected and shutil.which(cmd):
            detected.append(tool)

    env_signals = {
        "agy": ["AGY_HOME", "ANTIGRAVITY_HOME"],
        "gemini": ["GEMINI_API_KEY"],
        "warp": ["WARP_SESSION", "WARP_THEME"],
    }
    for tool, envs in env_signals.items():
        if tool not in detected and any(os.environ.get(e) for e in envs):
            detected.append(tool)

    return detected


# ── Init command ───────────────────────────────────────────────────────────────

@click.command()
@click.option("--ide", default=None, help="IDE(s) to configure: cursor,vscode,agy,... or 'all'")
@click.option("--no-skills", is_flag=True, help="Skip copying skills")
@click.option("--force", is_flag=True, help="Overwrite existing configs")
@click.option("--minimal", is_flag=True, help="Only create .ui-mcp/config.toml")
def init_cmd(ide: str | None, no_skills: bool, force: bool, minimal: bool) -> None:
    """
    Initialize ui-mcp in the current project.

    Copies skills, creates IDE configs, and sets up modules.lock.
    """
    project_root = Path.cwd()
    ui_mcp_dir = project_root / ".ui-mcp"
    ui_mcp_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold cyan]ui-mcp init[/bold cyan] → {project_root}\n")

    # 1. Create config.toml
    _write_config(project_root, force)

    # 2. Create modules.lock
    _write_modules_lock(project_root, force)

    # 3. Create skills.lock
    _write_skills_lock(project_root, force)

    if minimal:
        console.print("[green]✓[/green] Minimal init done (.ui-mcp/config.toml)")
        return

    # 4. Copy self-hosted MCP server files into .ui-mcp/server/
    _copy_mcp_server(project_root, force)

    # 5. Copy skills
    if not no_skills:
        _copy_skills(project_root, force)

    # 6. IDE configs
    tools = _resolve_ides(ide, project_root)
    for tool in tools:
        _write_ide_config(tool, project_root, force)

    console.print(f"\n[bold green]✓ ui-mcp initialized successfully with self-hosted MCP server![/bold green]")
    console.print(f"  Server    : {project_root / '.ui-mcp/server/server.py'}")
    console.print(f"  Skills    : {project_root / '.agents/skills/'}")
    console.print(f"  Config    : {project_root / '.ui-mcp/config.toml'}")
    console.print(f"\nRun the project MCP server:")
    console.print(f"  [bold cyan]python .ui-mcp/server/server.py[/bold cyan]")
    console.print(f"  (or [cyan]ui-mcp serve[/cyan])\n")



def _resolve_ides(ide_arg: str | None, project_root: Path) -> list[str]:
    if ide_arg == "all":
        return ALL_IDES + ALL_CLIS
    if ide_arg:
        return [t.strip() for t in ide_arg.split(",")]
    detected = detect_tools(project_root)
    if detected:
        console.print(f"[dim]Auto-detected: {', '.join(detected)}[/dim]")
        return detected
    # Fallback: ask user
    console.print("[yellow]No IDE detected. Please select:[/yellow]")
    choices = ALL_IDES + ALL_CLIS
    try:
        from rich.prompt import Prompt
        selected_str = Prompt.ask(
            f"Tools ({', '.join(choices)})", default="agy,cursor,vscode"
        )
        return [t.strip() for t in selected_str.split(",")]
    except Exception:
        return ["agy"]


def _write_config(project_root: Path, force: bool) -> None:
    config_path = project_root / ".ui-mcp" / "config.toml"
    if config_path.exists() and not force:
        console.print(f"  [dim]skip[/dim] {config_path.name} (already exists, use --force to overwrite)")
        return
    config_path.write_text(
        f'[project]\nname = "{project_root.name}"\nui_mcp_version = "0.1.0"\n\n'
        f'[server]\nlog_level = "info"\nauto_reload = true\n\n'
        f'[modules]\nenabled = ["color","layout","typography","animation","depth_25d","scene_3d","quality"]\n',
        encoding="utf-8",
    )
    console.print(f"  [green]✓[/green] {config_path.relative_to(project_root)}")


def _write_modules_lock(project_root: Path, force: bool) -> None:
    lock_path = project_root / ".ui-mcp" / "modules.lock"
    if lock_path.exists() and not force:
        return
    lock_path.write_text(
        '[active]\ncolor = "1.0.0"\nlayout = "1.0.0"\ntypography = "1.0.0"\n'
        'animation = "1.0.0"\ndepth_25d = "1.0.0"\nscene_3d = "1.0.0"\nquality = "1.0.0"\n\n'
        '[history]\ncolor = ["1.0.0"]\nlayout = ["1.0.0"]\ntypography = ["1.0.0"]\n'
        'animation = ["1.0.0"]\ndepth_25d = ["1.0.0"]\nscene_3d = ["1.0.0"]\nquality = ["1.0.0"]\n',
        encoding="utf-8",
    )
    console.print(f"  [green]✓[/green] .ui-mcp/modules.lock")


def _write_skills_lock(project_root: Path, force: bool) -> None:
    lock_path = project_root / ".ui-mcp" / "skills.lock"
    if lock_path.exists() and not force:
        return
    skills = [
        "ui-fundamentals", "ui-2d-layout", "ui-25d-depth", "ui-3d-scene",
        "ui-color-system", "ui-animation", "ui-typography", "ui-anti-patterns",
        "ui-mcp-tools",
    ]
    active = "\n".join(f'{s} = "1.0.0"' for s in skills)
    history = "\n".join(f'{s} = ["1.0.0"]' for s in skills)
    lock_path.write_text(
        f'[active]\n{active}\n\n[history]\n{history}\n\n'
        f'[registry]\nurl = "https://github.com/snn206/ui-ux-design/releases/download"\nfallback = "builtin"\n',
        encoding="utf-8",
    )
    console.print(f"  [green]✓[/green] .ui-mcp/skills.lock")


def _copy_mcp_server(project_root: Path, force: bool) -> None:
    from ui_ux_design.platform import PACKAGE_DIR
    server_dir = project_root / ".ui-mcp" / "server"
    if server_dir.exists() and not force:
        console.print(f"  [dim]skip[/dim] .ui-mcp/server/ (already exists, use --force to overwrite)")
        return

    server_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy server.py from template
    template_server = PACKAGE_DIR / "server_template" / "server.py"
    if template_server.exists():
        shutil.copy2(template_server, server_dir / "server.py")
    else:
        shutil.copy2(PACKAGE_DIR / "mcp_server.py", server_dir / "server.py")

    # 2. Copy core registry and base
    if (PACKAGE_DIR / "module_base.py").exists():
        shutil.copy2(PACKAGE_DIR / "module_base.py", server_dir / "module_base.py")
    if (PACKAGE_DIR / "module_registry.py").exists():
        shutil.copy2(PACKAGE_DIR / "module_registry.py", server_dir / "module_registry.py")

    # 3. Copy models/ and modules/
    if (PACKAGE_DIR / "models").exists():
        shutil.copytree(PACKAGE_DIR / "models", server_dir / "models", dirs_exist_ok=True)
    if (PACKAGE_DIR / "modules").exists():
        shutil.copytree(PACKAGE_DIR / "modules", server_dir / "modules", dirs_exist_ok=True)

    # 4. Create empty __init__.py
    (server_dir / "__init__.py").touch()

    console.print(f"  [green]✓[/green] .ui-mcp/server/ (Self-hosted MCP server: server.py, 7 modules, models)")


def _copy_skills(project_root: Path, force: bool) -> None:

    from ui_ux_design.platform import SKILLS_BUILTIN_DIR
    skills_dir = project_root / ".agents" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    if not SKILLS_BUILTIN_DIR.exists():
        console.print(f"  [yellow]⚠[/yellow] skills_builtin not found — skills will be downloaded on first use")
        return

    copied = 0
    for skill_dir in SKILLS_BUILTIN_DIR.iterdir():
        if skill_dir.is_dir():
            dest = skills_dir / skill_dir.name
            if dest.exists() and not force:
                continue
            shutil.copytree(skill_dir, dest, dirs_exist_ok=True)
            copied += 1
    console.print(f"  [green]✓[/green] Skills copied to .agents/skills/ ({copied} skills)")


def _write_ide_config(tool: str, project_root: Path, force: bool) -> None:
    if tool not in IDE_CONFIG_MAP:
        console.print(f"  [yellow]⚠[/yellow] Unknown tool: {tool}")
        return

    rel_path, content_fn = IDE_CONFIG_MAP[tool]
    content = content_fn(project_root)

    if rel_path is None:
        # Print guide to console
        console.print(f"\n  [cyan]{tool}[/cyan] — manual setup:")
        for line in content.strip().splitlines():
            console.print(f"    {line}")
        return

    out_path = project_root / rel_path
    if out_path.exists() and not force:
        console.print(f"  [dim]skip[/dim] {rel_path} (exists)")
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # For Zed: merge into existing settings.json
    if tool == "zed" and out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            new = json.loads(content)
            existing.update(new)
            content = json.dumps(existing, indent=2)
        except Exception:
            pass

    out_path.write_text(content, encoding="utf-8")
    console.print(f"  [green]✓[/green] {rel_path}")
