"""
module_registry.py — Loads, manages, and rolls back MCP modules.

Flow on startup:
  1. Read modules.lock → get active version for each module
  2. Import the versioned module package  (modules/<name>/v<major>/)
  3. Run health_check() → if FAIL, rollback to previous version
  4. Register all healthy modules' tools into the MCP server
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ui_ux_design.module_base import MCPModule, HealthStatus, ModuleInfo
from ui_ux_design.platform import PROJECT_MODULES_LOCK, PACKAGE_DIR

logger = logging.getLogger(__name__)


@dataclass
class ModuleStatus:
    name: str
    version: str
    healthy: bool
    health_message: str
    tools: list[str]
    skipped: bool = False


class ModuleRegistry:
    """
    Central registry that owns the lifecycle of all MCP modules.
    Thread-safe for reads; mutations require explicit CLI calls.
    """

    def __init__(self, lock_path: Path | None = None, modules_dir: Path | None = None) -> None:
        self._lock_path = lock_path or PROJECT_MODULES_LOCK
        self._modules_dir = modules_dir
        self._active: dict[str, MCPModule] = {}
        self._statuses: dict[str, ModuleStatus] = {}


    # ── Public API ────────────────────────────────────────────────────────────

    def load_all(self, server: Any | None = None) -> dict[str, MCPModule]:
        """
        Load every module listed in modules.lock.
        Auto-rollback on health_check failure.
        Returns the dict of healthy loaded modules.
        """
        lock = self._read_lock()
        active_versions: dict[str, str] = lock.get("active", {})
        history: dict[str, list[str]] = lock.get("history", {})
        enabled: list[str] | None = lock.get("modules", {}).get("enabled")

        for name, version in active_versions.items():
            if enabled and name not in enabled:
                logger.info("Module %s is disabled — skipping", name)
                continue
            self._load_module(name, version, history.get(name, []), server)

        return self._active

    def rollback(self, module_name: str, to_version: str | None = None) -> str:
        """
        Roll a module back to `to_version` (or the previous version in history).
        Updates modules.lock.  Returns the version rolled back to.
        """
        lock = self._read_lock()
        history: list[str] = lock.get("history", {}).get(module_name, [])
        current = lock.get("active", {}).get(module_name)

        if to_version is None:
            # Find the version immediately before the current one
            if len(history) < 2:
                raise ValueError(f"No previous version for module '{module_name}'")
            idx = history.index(current) if current in history else len(history)
            to_version = history[idx - 1]

        if to_version not in history:
            raise ValueError(
                f"Version '{to_version}' not in history for module '{module_name}'"
            )

        # Unload current
        if module_name in self._active:
            self._active[module_name].on_unload()
            del self._active[module_name]

        # Update lock file
        lock.setdefault("active", {})[module_name] = to_version
        self._write_lock(lock)

        logger.info("Module %s rolled back: %s → %s", module_name, current, to_version)
        return to_version

    def hot_reload(self, module_name: str) -> HealthStatus:
        """Unload and re-import the currently active version (dev helper)."""
        lock = self._read_lock()
        version = lock.get("active", {}).get(module_name)
        if not version:
            raise ValueError(f"Module '{module_name}' not in modules.lock")

        if module_name in self._active:
            self._active[module_name].on_unload()
            del self._active[module_name]

        # Force reimport
        pkg = f"ui_ux_design.modules.{module_name}.v{version.split('.')[0]}.tools"
        if pkg in sys.modules:
            del sys.modules[pkg]

        history = lock.get("history", {}).get(module_name, [version])
        self._load_module(module_name, version, history)
        status = self._statuses.get(module_name)
        return HealthStatus(
            healthy=status.healthy if status else False,
            message=status.health_message if status else "unknown",
        )

    def pin(self, module_name: str, version: str) -> None:
        """Pin a module to a specific version (prevents auto-upgrade)."""
        lock = self._read_lock()
        lock.setdefault("pinned", {})[module_name] = version
        self._write_lock(lock)
        logger.info("Module %s pinned to %s", module_name, version)

    def status(self) -> dict[str, ModuleStatus]:
        return dict(self._statuses)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load_module(
        self,
        name: str,
        version: str,
        history: list[str],
        server: Any | None = None,
    ) -> None:
        major = version.split(".")[0]
        module = self._import_module(name, major)
        if module is None:
            self._statuses[name] = ModuleStatus(
                name=name, version=version,
                healthy=False, health_message="Import failed",
                tools=[], skipped=True,
            )
            return

        health = module.health_check()
        if health.healthy:
            module.on_load()
            self._active[name] = module
            if server:
                module.register_tools(server)
            self._statuses[name] = ModuleStatus(
                name=name, version=version,
                healthy=True, health_message=health.message,
                tools=module.info.tools,
            )
            logger.info("✓ Module %s v%s loaded (%d tools)", name, version, len(module.info.tools))
        else:
            logger.warning("✗ Module %s v%s health_check FAILED: %s", name, version, health.message)
            self._try_rollback(name, version, history, server)

    def _try_rollback(
        self,
        name: str,
        failed_version: str,
        history: list[str],
        server: Any | None,
    ) -> None:
        """Attempt to load a previous version when health_check fails."""
        candidates = [v for v in reversed(history) if v != failed_version]
        for fallback_version in candidates:
            major = fallback_version.split(".")[0]
            module = self._import_module(name, major)
            if module is None:
                continue
            health = module.health_check()
            if health.healthy:
                module.on_load()
                self._active[name] = module
                if server:
                    module.register_tools(server)
                self._statuses[name] = ModuleStatus(
                    name=name, version=fallback_version,
                    healthy=True,
                    health_message=f"[ROLLBACK from {failed_version}] {health.message}",
                    tools=module.info.tools,
                )
                logger.warning(
                    "⚠ Module %s rolled back automatically: %s → %s",
                    name, failed_version, fallback_version,
                )
                # Update lock
                lock = self._read_lock()
                lock.setdefault("active", {})[name] = fallback_version
                self._write_lock(lock)
                return

        # All versions failed
        self._statuses[name] = ModuleStatus(
            name=name, version=failed_version,
            healthy=False, health_message="All versions failed health_check",
            tools=[], skipped=True,
        )
        logger.error("✗✗ Module %s skipped — all versions unhealthy", name)

    def _import_module(self, name: str, major: str) -> MCPModule | None:
        # 1. Try local modules_dir first if explicitly provided
        if self._modules_dir:
            file_path = self._modules_dir / name / f"v{major}" / "tools.py"
            if file_path.exists():
                try:
                    spec = importlib.util.spec_from_file_location(f"local_{name}_v{major}", file_path)
                    if spec and spec.loader:
                        mod = importlib.util.module_from_spec(spec)
                        sys.modules[spec.name] = mod
                        spec.loader.exec_module(mod)
                        cls = getattr(mod, "MODULE_CLASS", None)
                        if cls is not None:
                            return cls()
                except Exception as e:
                    logger.debug("Failed loading local file module %s: %s", file_path, e)

        # 2. Try standard package import
        pkg = f"ui_ux_design.modules.{name}.v{major}.tools"
        try:
            mod = importlib.import_module(pkg)
            cls = getattr(mod, "MODULE_CLASS", None)
            if cls is not None:
                return cls()
        except Exception as e:
            logger.debug("Failed importing %s: %s", pkg, e)

        # 3. Fallback to relative modules package
        try:
            mod = importlib.import_module(f"modules.{name}.v{major}.tools")
            cls = getattr(mod, "MODULE_CLASS", None)
            if cls is not None:
                return cls()
        except Exception:
            pass

        logger.error("Failed to import module %s v%s", name, major)
        return None



    def _read_lock(self) -> dict:
        if self._lock_path.exists():
            with open(self._lock_path, "rb") as f:
                return tomllib.load(f)
        # Default lock — all modules at v1
        return {
            "active": {
                "color": "1.0.0", "layout": "1.0.0", "typography": "1.0.0",
                "animation": "1.0.0", "depth_25d": "1.0.0",
                "scene_3d": "1.0.0", "quality": "1.0.0",
            },
            "history": {},
        }

    def _write_lock(self, data: dict) -> None:
        import tomllib as _tomllib  # noqa: F401 — just to check we have toml write
        # Use tomli_w if available, else format manually
        try:
            import tomli_w
            self._lock_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._lock_path, "wb") as f:
                tomli_w.dump(data, f)
        except ImportError:
            # Fallback: write TOML manually (simple key=value)
            self._lock_path.parent.mkdir(parents=True, exist_ok=True)
            lines = []
            for section, values in data.items():
                lines.append(f"\n[{section}]")
                if isinstance(values, dict):
                    for k, v in values.items():
                        lines.append(f'{k} = {repr(v)}')
            self._lock_path.write_text("\n".join(lines), encoding="utf-8")
