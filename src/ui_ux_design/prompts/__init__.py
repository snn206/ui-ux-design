"""
prompts/__init__.py — PromptLoader for UI/UX Design System prompt templates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ui_ux_design.platform import PACKAGE_DIR, get_project_root

PROMPTS_DIR = PACKAGE_DIR / "prompts"


class PromptLoader:
    """Load, compose, and format UI design prompt templates."""

    def __init__(self, custom_dir: Path | str | None = None) -> None:
        self.builtin_dir = PROMPTS_DIR
        project_root = get_project_root()
        self.project_prompts_dir = project_root / ".ui-mcp" / "prompts"
        self.custom_dir = Path(custom_dir) if custom_dir else None

    def list_templates(self) -> list[str]:
        """Return list of available template names (without .md extension)."""
        names = set()
        for d in [self.builtin_dir, self.project_prompts_dir, self.custom_dir]:
            if d and d.exists():
                for f in d.glob("*.md"):
                    names.add(f.stem)
        return sorted(names)

    def resolve_path(self, name: str) -> Path:
        """Find the template file, checking custom -> project -> builtin."""
        filename = f"{name}.md" if not name.endswith(".md") else name
        search_dirs = [self.custom_dir, self.project_prompts_dir, self.builtin_dir]
        for d in search_dirs:
            if d and (d / filename).is_file():
                return d / filename
        raise FileNotFoundError(f"Prompt template '{name}' not found in any search path.")

    def load(self, name: str) -> str:
        """Load single template by name."""
        path = self.resolve_path(name)
        return path.read_text(encoding="utf-8")

    def compose(self, *names: str, separator: str = "\n\n---\n\n") -> str:
        """Compose multiple templates into one cohesive prompt."""
        contents = [self.load(name) for name in names]
        return separator.join(contents)

    def with_context(self, template_or_name: str, **ctx: Any) -> str:
        """
        Inject variables into template.
        If template_or_name is a template name and exists, it is loaded;
        otherwise it is treated as raw template text.
        """
        try:
            text = self.load(template_or_name)
        except (FileNotFoundError, OSError):
            text = template_or_name

        for k, v in ctx.items():
            placeholder = f"{{{k}}}"
            text = text.replace(placeholder, str(v))
        return text


# Default global instance
prompt_loader = PromptLoader()
