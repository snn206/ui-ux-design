"""
platform.py — Cross-platform path utilities.

Provides consistent paths across Windows, macOS, and Linux:
- GLOBAL_DATA_DIR: bundled package data (read-only)
- USER_CACHE_DIR: downloaded skills cache (~/.config/ui-ux-design/)
- PROJECT_ROOT: .ui-mcp/ in current project
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "ui-ux-design"

# ── Package-bundled data (read-only) ─────────────────────────────────────────
# Location of skills_builtin/, templates/ inside the installed package
PACKAGE_DIR = Path(__file__).parent
SKILLS_BUILTIN_DIR = PACKAGE_DIR / "skills_builtin"
TEMPLATES_DIR = PACKAGE_DIR / "templates"

# ── User-level cache (writable, cross-platform) ───────────────────────────────
# Windows : C:\Users\<user>\AppData\Roaming\ui-ux-design
# macOS   : ~/.config/ui-ux-design   (XDG-compliant on Linux too)
# Linux   : ~/.config/ui-ux-design
USER_CONFIG_DIR = Path(user_config_dir(APP_NAME))
USER_CACHE_DIR = USER_CONFIG_DIR / "skills_cache"
USER_INDEX_CACHE = USER_CONFIG_DIR / "skills_index.json"

# ── Project-level (local, per-project) ───────────────────────────────────────
def get_project_root(start: Path | None = None) -> Path:
    """
    Walk up from `start` (default: cwd) to find the project root.
    Heuristic: directory containing .ui-mcp/, .git, pyproject.toml, etc.
    Falls back to cwd if nothing found.
    """
    current = (start or Path.cwd()).resolve()
    markers = {".ui-mcp", ".git", "pyproject.toml", "package.json", ".agents"}
    for directory in [current, *current.parents]:
        if any((directory / m).exists() for m in markers):
            return directory
    return current


PROJECT_ROOT = get_project_root()
PROJECT_CONFIG_DIR = PROJECT_ROOT / ".ui-mcp"
PROJECT_SKILLS_DIR = PROJECT_ROOT / ".agents" / "skills"
PROJECT_MODULES_LOCK = PROJECT_CONFIG_DIR / "modules.lock"
PROJECT_SKILLS_LOCK = PROJECT_CONFIG_DIR / "skills.lock"
PROJECT_CONFIG_FILE = PROJECT_CONFIG_DIR / "config.toml"

# ── Python executable (for spawning subprocesses) ────────────────────────────
PYTHON_EXE = Path(sys.executable)

# ── Skills & Versions GitHub Registry ──────────────────────────────────────────
GITHUB_REPO = os.environ.get("UI_MCP_GITHUB_REPO", "snn206/ui-ux-design")
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
GITHUB_RELEASES_URL = f"https://github.com/{GITHUB_REPO}/releases/download"
GITHUB_ARCHIVE_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/tags"

SKILLS_REGISTRY_URL = (
    os.environ.get("UI_MCP_REGISTRY")
    or GITHUB_RELEASES_URL
)
SKILLS_INDEX_URL = f"{SKILLS_REGISTRY_URL}/skills-index.json"
VERSIONS_INDEX_URL = os.environ.get("UI_MCP_VERSIONS_URL", f"{GITHUB_RAW_BASE}/versions.json")
USER_VERSIONS_CACHE = USER_CONFIG_DIR / "versions_cache.json"
VERSIONS_BUNDLED_FILE = PACKAGE_DIR / "versions.json"

