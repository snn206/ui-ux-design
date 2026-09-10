"""
version_manager.py — Unified Version Management Engine.

Provides high-level operations to:
- Inspect project version status
- Browse the GitHub version store
- Pull releases from GitHub into local cache
- Switch project version (bundle, individual skill, or local source)
- Rollback to previous version
"""

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ui_ux_design.platform import (
    GITHUB_REPO,
    PROJECT_ROOT,
    PROJECT_SKILLS_DIR,
    PROJECT_SKILLS_LOCK,
    PROJECT_MODULES_LOCK,
    SKILLS_BUILTIN_DIR,
    USER_CACHE_DIR,
)
from ui_ux_design.version_hub import GitHubVersionHub

logger = logging.getLogger(__name__)


class VersionManager:
    """
    Unified manager orchestrating:
    - GitHub Version Store (remote releases, downloads)
    - Local User Cache (~/.config/ui-ux-design/skills_cache/)
    - Project Active State (.agents/skills/, .ui-mcp/skills.lock)
    """

    def __init__(
        self,
        project_root: Path | None = None,
        skills_lock: Path | None = None,
        modules_lock: Path | None = None,
        skills_dir: Path | None = None,
        hub: GitHubVersionHub | None = None,
    ) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.skills_lock = skills_lock or PROJECT_SKILLS_LOCK
        self.modules_lock = modules_lock or PROJECT_MODULES_LOCK
        self.skills_dir = skills_dir or PROJECT_SKILLS_DIR
        self.hub = hub or GitHubVersionHub()

    # ── Status & Discovery ─────────────────────────────────────────────────────

    def get_status(self) -> dict[str, Any]:
        """
        Return the overall version status for the project:
        - active release
        - active skills & modules
        - latest version on GitHub
        - cached versions
        """
        skills_lock_data = self._read_toml(self.skills_lock)
        modules_lock_data = self._read_toml(self.modules_lock)

        active_release = skills_lock_data.get("release", {}).get("current")
        active_skills = skills_lock_data.get("active", {})
        active_modules = modules_lock_data.get("active", {})

        # If release is not explicitly named, infer from first skill version
        if not active_release and active_skills:
            first_ver = next(iter(active_skills.values()), "1.0.0")
            active_release = f"v{first_ver}" if not first_ver.startswith("v") else first_ver
        elif not active_release:
            active_release = "uninitialized"

        catalog = self.hub.fetch_catalog()
        latest_release = catalog.get("latest_release", "v1.0.0")
        cached_versions = self.hub.list_cached_versions()

        return {
            "project_root": str(self.project_root),
            "repository": GITHUB_REPO,
            "active_release": active_release,
            "latest_release": latest_release,
            "is_latest": (active_release == latest_release or active_release.lstrip("v") == latest_release.lstrip("v")),
            "cached_versions": cached_versions,
            "active_skills": active_skills,
            "active_modules": active_modules,
            "skills_count": len(active_skills),
            "cache_dir": str(self.hub.cache_dir),
        }

    def list_catalog(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        List all available releases from GitHub Store + Local Source.
        Each item has status: ACTIVE, CACHED, or AVAILABLE (GitHub).
        """
        releases = self.hub.list_releases(force_refresh=force_refresh)
        current_status = self.get_status()
        active_rel = current_status["active_release"]

        results = []

        # 1. Local Source entry
        is_local_active = (active_rel == "local")
        results.append({
            "tag": "local",
            "version": "local/dev",
            "name": "Mã nguồn hiện tại (Current Source)",
            "date": "HEAD",
            "type": "dev",
            "source": "Local Source",
            "description": "Bộ kỹ năng tích hợp sẵn trong mã nguồn gói cài đặt hiện tại.",
            "is_active": is_local_active,
            "is_cached": True,
            "changelog": ["Trực tiếp từ thư mục mã nguồn skills_builtin/"],
        })

        # 2. GitHub Releases
        for r in releases:
            tag = r["tag"]
            ver = r.get("version", tag.lstrip("v"))
            is_active = (active_rel == tag or active_rel == ver or active_rel.lstrip("v") == ver)
            item = dict(r)
            item["source"] = "GitHub Store"
            item["is_active"] = is_active
            results.append(item)

        return results

    # ── Version Operations ─────────────────────────────────────────────────────

    def pull(self, version_or_tag: str) -> Path:
        """
        Download a version package from GitHub into local cache.
        Does not apply it to the project yet.
        """
        if version_or_tag.lower() == "latest":
            catalog = self.hub.fetch_catalog()
            version_or_tag = catalog.get("latest_release", "v1.0.0")

        if version_or_tag.lower() == "local":
            raise ValueError("Phiên bản 'local' đã có sẵn trong mã nguồn máy, không cần pull.")

        return self.hub.download_version(version_or_tag)

    def switch(self, target: str, force: bool = False) -> dict[str, Any]:
        """
        Switch the project to a specific version:
        - "latest": Fetches and switches to latest release on GitHub
        - "local": Switches to skills bundled directly in the package source
        - "v1.0.0", "1.1.0", etc.: Downloads from GitHub if needed, deploys to .agents/skills/
        """
        target = target.strip()

        # Resolve 'latest'
        if target.lower() == "latest":
            catalog = self.hub.fetch_catalog()
            target = catalog.get("latest_release", "v1.0.0")

        # Handle 'local'
        if target.lower() == "local":
            return self._switch_to_local()

        # Handle GitHub version release
        tag = self.hub._normalize_tag(target)
        ver_number = tag.lstrip("v")

        # 1. Download/ensure cache
        cached_dir = self.hub.download_version(tag, force_download=force)

        # 2. Deploy from cache into project .agents/skills/
        deployed_skills = self._deploy_skills_from_dir(cached_dir)

        # 3. Update skills.lock
        self._update_skills_lock(deployed_skills, release_tag=tag, version_str=ver_number)

        # 4. Update modules.lock active versions if needed
        self._update_modules_lock(version_str=ver_number)

        logger.info("Switched project to version %s (%d skills updated)", tag, len(deployed_skills))
        return {
            "success": True,
            "version": tag,
            "source": "GitHub Store",
            "skills_deployed": deployed_skills,
            "message": f"Đã chuyển đổi thành công sang phiên bản {tag} từ GitHub Store.",
        }

    def rollback(self, skill_name: str | None = None) -> str:
        """
        Roll back to the previous version in history.
        If skill_name is None, rolls back the release bundle.
        """
        lock_data = self._read_toml(self.skills_lock)

        if skill_name:
            # Single skill rollback
            history = lock_data.get("history", {}).get(skill_name, [])
            current = lock_data.get("active", {}).get(skill_name)
            if len(history) < 2:
                raise ValueError(f"Không có phiên bản trước đó trong lịch sử cho skill '{skill_name}'.")
            idx = history.index(current) if current in history else len(history)
            to_ver = history[idx - 1]
            return self.switch_single_skill(skill_name, to_ver)

        # Bundle rollback
        rel_history = lock_data.get("release", {}).get("history", [])
        current_rel = lock_data.get("release", {}).get("current")

        if len(rel_history) < 2:
            raise ValueError("Không có phiên bản trước đó trong lịch sử dự án để rollback.")

        idx = rel_history.index(current_rel) if current_rel in rel_history else len(rel_history)
        to_rel = rel_history[idx - 1]

        self.switch(to_rel)
        return to_rel

    def switch_single_skill(self, skill_name: str, version: str) -> str:
        """Switch an individual skill to a specific version."""
        cached_dir = self.hub.get_cached_path(version)
        if not cached_dir:
            cached_dir = self.hub.download_version(version)

        src_skill = cached_dir / skill_name
        if not src_skill.exists():
            # Check builtin
            src_skill = SKILLS_BUILTIN_DIR / skill_name
            if not src_skill.exists():
                raise FileNotFoundError(f"Không tìm thấy skill '{skill_name}' ở version {version}.")

        dest_skill = self.skills_dir / skill_name
        dest_skill.parent.mkdir(parents=True, exist_ok=True)
        if dest_skill.exists():
            shutil.rmtree(dest_skill)
        shutil.copytree(src_skill, dest_skill)

        # Update lock
        lock_data = self._read_toml(self.skills_lock)
        lock_data.setdefault("active", {})[skill_name] = version
        hist = lock_data.setdefault("history", {}).setdefault(skill_name, [])
        if version not in hist:
            hist.append(version)
        self._write_toml(self.skills_lock, lock_data)

        return version

    # ── Internal Deployment Helpers ───────────────────────────────────────────

    def _switch_to_local(self) -> dict[str, Any]:
        """Deploy directly from packaged source code."""
        source = SKILLS_BUILTIN_DIR
        if not source.exists() or not any(source.iterdir()):
            source = PROJECT_ROOT / ".agents" / "skills"

        deployed = []
        if source.exists() and any(source.iterdir()):
            for skill_dir in source.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    dest = self.skills_dir / skill_dir.name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(skill_dir, dest)
                    deployed.append(skill_dir.name)

        # Update lock
        lock_data = self._read_toml(self.skills_lock)
        for s in deployed:
            lock_data.setdefault("active", {})[s] = "local"
            hist = lock_data.setdefault("history", {}).setdefault(s, [])
            if "local" not in hist:
                hist.append("local")

        rel_sec = lock_data.setdefault("release", {})
        rel_sec["current"] = "local"
        hist_rel = rel_sec.setdefault("history", [])
        if "local" not in hist_rel:
            hist_rel.append("local")

        self._write_toml(self.skills_lock, lock_data)

        return {
            "success": True,
            "version": "local",
            "source": "Local Source",
            "skills_deployed": deployed,
            "message": "Đã chuyển đổi thành công sang phiên bản từ mã nguồn hiện tại.",
        }

    def _deploy_skills_from_dir(self, source_dir: Path) -> list[str]:
        """Deploy skill directories from source_dir into project's .agents/skills/."""
        deployed = []
        # Find all directories that contain SKILL.md
        candidate_dirs = []
        if (source_dir / "SKILL.md").exists():
            candidate_dirs.append(source_dir)
        else:
            for item in source_dir.rglob("SKILL.md"):
                candidate_dirs.append(item.parent)

        for skill_dir in candidate_dirs:
            skill_name = skill_dir.name
            dest_dir = self.skills_dir / skill_name
            dest_dir.parent.mkdir(parents=True, exist_ok=True)
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            shutil.copytree(skill_dir, dest_dir)
            deployed.append(skill_name)

        return sorted(deployed)

    def _update_skills_lock(
        self,
        deployed_skills: list[str],
        release_tag: str,
        version_str: str,
    ) -> None:
        """Update .ui-mcp/skills.lock with active and history."""
        lock_data = self._read_toml(self.skills_lock)
        active = lock_data.setdefault("active", {})
        history = lock_data.setdefault("history", {})

        for skill in deployed_skills:
            active[skill] = version_str
            hist_list = history.setdefault(skill, [])
            if version_str not in hist_list:
                hist_list.append(version_str)

        # Release section
        rel_sec = lock_data.setdefault("release", {})
        rel_sec["current"] = release_tag
        rel_hist = rel_sec.setdefault("history", [])
        if release_tag not in rel_hist:
            rel_hist.append(release_tag)

        self._write_toml(self.skills_lock, lock_data)

    def _update_modules_lock(self, version_str: str) -> None:
        """Optionally record release version in modules.lock."""
        if not self.modules_lock.exists():
            return
        try:
            mod_data = self._read_toml(self.modules_lock)
            rel_sec = mod_data.setdefault("release", {})
            rel_sec["current"] = version_str
            self._write_toml(self.modules_lock, mod_data)
        except Exception as e:
            logger.debug("Failed updating modules.lock release: %s", e)

    def _read_toml(self, path: Path) -> dict:
        if path.exists():
            try:
                with open(path, "rb") as f:
                    return tomllib.load(f)
            except Exception:
                pass
        return {}

    def _write_toml(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for section, values in data.items():
            lines.append(f"[{section}]")
            if isinstance(values, dict):
                for k, v in values.items():
                    if isinstance(v, list):
                        items_str = ", ".join(f'"{i}"' for i in v)
                        lines.append(f"{k} = [{items_str}]")
                    else:
                        lines.append(f'{k} = "{v}"')
            lines.append("")
        path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
