"""
module_base.py — Abstract base class for all MCP modules.

Every module must:
  1. Implement the `info` property (returns ModuleInfo)
  2. Implement `register_tools(server)` — registers MCP tools
  3. Implement `health_check()` — self-validates at startup
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModuleInfo:
    name: str              # e.g. "color"
    version: str           # semver e.g. "2.1.0"
    description: str
    tools: list[str]       # tool names this module exposes
    author: str = "core"
    deprecated: bool = False
    min_python: str = "3.11"
    requires: list[str] = field(default_factory=list)  # other module deps


@dataclass
class HealthStatus:
    healthy: bool
    message: str
    details: dict[str, Any] | None = None


class MCPModule(ABC):
    """Abstract base class that every module must implement."""

    @property
    @abstractmethod
    def info(self) -> ModuleInfo: ...

    @abstractmethod
    def register_tools(self, server: Any) -> None:
        """Register all MCP tools from this module into the server."""
        ...

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """
        Self-validate: run a minimal smoke test.
        Called at server startup. FAIL triggers auto-rollback.
        """
        ...

    def on_load(self) -> None:
        """Hook: called once after the module is successfully loaded."""

    def on_unload(self) -> None:
        """Hook: called before the module is unloaded or rolled back."""

    def __repr__(self) -> str:
        return f"<Module {self.info.name} v{self.info.version}>"
