"""
cli/version_cmd.py — ui-mcp version {status,list,switch,pull,rollback,sync,package}

Unified version management CLI connecting to GitHub Version Hub (snn206/ui-ux-design).
"""

from __future__ import annotations

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group(name="version", invoke_without_command=True)
@click.pass_context
def version_group(ctx: click.Context) -> None:
    """Quản lý version và Kho Version GitHub (xem danh mục, tải về, đổi version)."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(version_status)


@version_group.command("status")
def version_status() -> None:
    """Xem tổng quan trạng thái phiên bản của dự án."""
    from ui_ux_design.version_manager import VersionManager
    vm = VersionManager()
    st = vm.get_status()

    active_rel = st["active_release"]
    latest_rel = st["latest_release"]
    is_latest = st["is_latest"]

    status_badge = "[bold green]✓ Mới nhất (Up-to-date)[/bold green]" if is_latest else f"[bold yellow]↑ Có bản mới ({latest_rel})[/bold yellow]"
    cached_str = ", ".join(st["cached_versions"]) or "Chưa có bản nào trong cache"

    info_text = (
        f"[bold cyan]Dự án:[/bold cyan] {st['project_root']}\n"
        f"[bold cyan]Kho GitHub:[/bold cyan] https://github.com/{st['repository']}\n"
        f"[bold cyan]Phiên bản đang dùng (Active):[/bold cyan] [bold magenta]{active_rel}[/bold magenta]  {status_badge}\n"
        f"[bold cyan]Phiên bản mới nhất trên GitHub:[/bold cyan] [bold green]{latest_rel}[/bold green]\n"
        f"[bold cyan]Bản đã lưu trong Cache máy (~/.config):[/bold cyan] {cached_str}\n"
        f"[bold cyan]Số lượng Skills đang nạp:[/bold cyan] {st['skills_count']} skills"
    )

    console.print(
        Panel(
            info_text,
            title="[bold blue]🎨 Anti-AI-UI Version Status[/bold blue]",
            border_style="bright_blue",
            box=box.ROUNDED,
        )
    )

    # Hiển thị bảng chi tiết các skills
    if st["active_skills"]:
        table = Table(box=box.SIMPLE_HEAD, title="Danh sách Skills & Version đang nạp")
        table.add_column("Skill", style="cyan")
        table.add_column("Version", style="white")
        for name, ver in sorted(st["active_skills"].items()):
            table.add_row(name, str(ver))
        console.print(table)


@version_group.command("list")
@click.option("--refresh", is_flag=True, help="Làm mới danh mục từ GitHub")
def version_list(refresh: bool) -> None:
    """Duyệt Kho Version (GitHub Releases & Mã nguồn cục bộ)."""
    from ui_ux_design.version_manager import VersionManager
    vm = VersionManager()

    with console.status("[cyan]Đang đồng bộ Kho Version từ GitHub...[/cyan]"):
        releases = vm.list_catalog(force_refresh=refresh)

    table = Table(
        box=box.ROUNDED,
        title="Kho Version Hệ Thống (GitHub Version Store: snn206/ui-ux-design)",
        title_style="bold magenta",
    )
    table.add_column("Tag / Version", style="bold magenta")
    table.add_column("Trạng thái (Status)", justify="center")
    table.add_column("Loại (Type)")
    table.add_column("Nguồn (Source)")
    table.add_column("Ngày phát hành", style="dim")
    table.add_column("Mô tả tóm tắt")

    for r in releases:
        tag = r["tag"]
        is_active = r.get("is_active", False)
        is_cached = r.get("is_cached", False)

        if is_active:
            status_tag = "[bold green]● ACTIVE[/bold green]"
        elif is_cached:
            status_tag = "[cyan]↓ CACHED[/cyan]"
        else:
            status_tag = "[white]☁ GITHUB[/white]"

        type_color = {
            "stable": "green",
            "feature": "yellow",
            "preview": "magenta",
            "dev": "dim",
        }.get(r.get("type", ""), "white")

        table.add_row(
            tag,
            status_tag,
            f"[{type_color}]{r.get('type', 'release')}[/{type_color}]",
            r.get("source", "GitHub"),
            r.get("date", "—"),
            r.get("description", r.get("name", "—")),
        )

    console.print(table)
    console.print(
        "\n[dim]Gợi ý:[/dim] Chuyển version bằng lệnh [bold cyan]ui-mcp version switch <tag>[/bold cyan] (Ví dụ: [green]ui-mcp version switch v1.0.0[/green] hoặc [green]ui-mcp version switch latest[/green])\n"
    )


@version_group.command("switch")
@click.argument("version_tag")
@click.option("--force", is_flag=True, help="Ép tải lại từ GitHub ngay cả khi đã có trong cache")
def version_switch(version_tag: str, force: bool) -> None:
    """Chuyển đổi version cho dự án (Ví dụ: v1.0.0, latest, local)."""
    from ui_ux_design.version_manager import VersionManager
    vm = VersionManager()

    console.print(f"[cyan]Đang chuyển đổi sang phiên bản:[/cyan] [bold magenta]{version_tag}[/bold magenta]...")

    with console.status("[cyan]Đang tải gói từ GitHub và triển khai skills...[/cyan]"):
        try:
            result = vm.switch(version_tag, force=force)
        except Exception as e:
            console.print(f"[bold red]✗ Lỗi khi chuyển đổi version:[/bold red] {e}")
            raise SystemExit(1)

    console.print(f"[bold green]✓[/bold green] {result['message']}")
    console.print(f"[dim]Số lượng skills đã cập nhật vào .agents/skills/:[/dim] [bold]{len(result['skills_deployed'])}[/bold]")
    for s in result["skills_deployed"]:
        console.print(f"  [green]✓[/green] {s}")


@version_group.command("pull")
@click.argument("version_tag")
def version_pull(version_tag: str) -> None:
    """Tải trước một version từ GitHub về local cache máy tính."""
    from ui_ux_design.version_manager import VersionManager
    vm = VersionManager()

    with console.status(f"[cyan]Đang kéo {version_tag} từ GitHub về local cache...[/cyan]"):
        try:
            dest = vm.pull(version_tag)
            console.print(f"[bold green]✓[/bold green] Đã tải và lưu trữ thành công phiên bản [magenta]{version_tag}[/magenta] tại:")
            console.print(f"  [dim]{dest}[/dim]")
        except Exception as e:
            console.print(f"[bold red]✗ Lỗi khi tải version:[/bold red] {e}")
            raise SystemExit(1)


@version_group.command("rollback")
@click.argument("skill_name", required=False)
def version_rollback(skill_name: str | None) -> None:
    """Quay lại phiên bản trước đó trong lịch sử (toàn dự án hoặc từng skill)."""
    from ui_ux_design.version_manager import VersionManager
    vm = VersionManager()

    try:
        rolled = vm.rollback(skill_name)
        target_name = f"skill '{skill_name}'" if skill_name else "dự án"
        console.print(f"[bold green]✓[/bold green] Đã rollback {target_name} thành công về phiên bản [bold magenta]{rolled}[/bold magenta].")
    except Exception as e:
        console.print(f"[bold red]✗ Lỗi khi rollback:[/bold red] {e}")
        raise SystemExit(1)


@version_group.command("sync")
def version_sync() -> None:
    """Làm mới và đồng bộ danh mục phiên bản từ GitHub."""
    from ui_ux_design.version_hub import GitHubVersionHub
    hub = GitHubVersionHub()

    with console.status("[cyan]Đang kết nối GitHub và làm mới danh mục...[/cyan]"):
        catalog = hub.fetch_catalog(force_refresh=True)

    releases_count = len(catalog.get("releases", {}))
    latest = catalog.get("latest_release", "—")
    console.print(f"[bold green]✓[/bold green] Đã đồng bộ thành công: [bold]{releases_count}[/bold] bản phát hành trên GitHub (Mới nhất: [bold magenta]{latest}[/bold magenta]).")


@version_group.command("package")
@click.argument("tag")
@click.option("--out-dir", default=None, help="Thư mục xuất file zip (mặc định: dist/)")
def version_package(tag: str, out_dir: str | None) -> None:
    """(Dành cho Maintainer) Đóng gói các skills thành file zip để upload lên GitHub Releases."""
    import hashlib
    import zipfile
    from pathlib import Path
    from ui_ux_design.platform import PROJECT_ROOT, SKILLS_BUILTIN_DIR

    norm_tag = tag if tag.startswith("v") else f"v{tag}"
    out_path = Path(out_dir) if out_dir else (PROJECT_ROOT / "dist")
    out_path.mkdir(parents=True, exist_ok=True)

    zip_filename = f"ui-ux-skills-{norm_tag}.zip"
    zip_dest = out_path / zip_filename

    source = SKILLS_BUILTIN_DIR
    if not source.exists() or not any(source.iterdir()):
        source = PROJECT_ROOT / ".agents" / "skills"

    with zipfile.ZipFile(zip_dest, "w", zipfile.ZIP_DEFLATED) as zf:
        for skill_dir in source.iterdir():
            if skill_dir.is_dir():
                for file_path in skill_dir.rglob("*"):
                    if file_path.is_file():
                        rel = file_path.relative_to(source)
                        zf.write(file_path, arcname=str(rel))

    sha256 = hashlib.sha256(zip_dest.read_bytes()).hexdigest()

    console.print(f"[bold green]✓ Đã đóng gói thành công:[/bold green] {zip_dest}")
    console.print(f"[bold cyan]SHA256:[/bold cyan] sha256:{sha256}")
    console.print(f"[bold yellow]Hướng dẫn tạo GitHub Release:[/bold yellow]")
    console.print(f"  1. Tạo tag: git tag -a {norm_tag} -m 'Release {norm_tag}' && git push origin {norm_tag}")
    console.print(f"  2. Đính kèm file '{zip_filename}' vào GitHub Release {norm_tag}")
    console.print(f"  3. Cập nhật mã sha256 trên vào file versions.json trên GitHub")
