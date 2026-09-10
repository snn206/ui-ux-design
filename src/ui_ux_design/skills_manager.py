"""skills_manager.py — SkillsManager: download, deploy, rollback, verify skills."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from ui_ux_design.platform import (
    USER_CACHE_DIR, USER_INDEX_CACHE, SKILLS_BUILTIN_DIR,
    PROJECT_SKILLS_DIR, PROJECT_SKILLS_LOCK, SKILLS_INDEX_URL,
)


class SkillsManager:
    """
    Manages the full lifecycle of versioned skills:
    - Download from registry → local cache
    - Deploy from cache → project .agents/skills/
    - Rollback to any cached version
    - Offline fallback to skills_builtin
    """

    def __init__(
        self,
        skills_lock: Path | None = None,
        skills_dir: Path | None = None,
        cache_dir: Path | None = None,
    ) -> None:
        self._lock_path = skills_lock or PROJECT_SKILLS_LOCK
        self._skills_dir = skills_dir or PROJECT_SKILLS_DIR
        self._cache_dir = cache_dir or USER_CACHE_DIR

    # ── Public API ────────────────────────────────────────────────────────────

    def list_skills(self, offline: bool = False) -> dict[str, dict]:
        lock = self._read_lock()
        active = dict(lock.get("active", {}))

        # Also discover any skills in _skills_dir or skills_builtin
        if self._skills_dir.exists():
            for d in self._skills_dir.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists() and d.name not in active:
                    active[d.name] = "1.0.0"

        from ui_ux_design.platform import SKILLS_BUILTIN_DIR
        if SKILLS_BUILTIN_DIR.exists():
            for d in SKILLS_BUILTIN_DIR.iterdir():
                if d.is_dir() and (d / "SKILL.md").exists() and d.name not in active:
                    active[d.name] = "1.0.0"

        index = {} if offline else self._load_index_cached()

        result = {}
        for name, ver in sorted(active.items()):
            cached = self._cached_versions(name)
            latest = index.get("skills", {}).get(name, {}).get("latest", ver)
            update_avail = latest != ver and not offline
            missing = not (self._skills_dir / name).exists()
            result[name] = {
                "active": ver,
                "latest": latest,
                "cached": cached,
                "update_available": update_avail,
                "missing": missing,
            }
        return result


    def status(self, skill: str) -> dict:
        lock = self._read_lock()
        active = lock.get("active", {}).get(skill, "—")
        cached = self._cached_versions(skill)
        index = self._load_index_cached()
        skill_index = index.get("skills", {}).get(skill, {})
        latest = skill_index.get("latest", active)
        versions = skill_index.get("versions", {})
        changelog = versions.get(active, {}).get("changelog", "")
        return {"active": active, "latest": latest, "cached": cached, "changelog": changelog}

    def install(self, skill: str, version: str = "latest") -> str:
        if version == "latest":
            index = self.fetch_index()
            version = index.get("skills", {}).get(skill, {}).get("latest", "1.0.0")

        cached_path = self._cache_path(skill, version)
        if not cached_path.exists():
            self._download(skill, version)

        self._deploy(skill, version)
        lock = self._read_lock()
        lock.setdefault("active", {})[skill] = version
        history = lock.setdefault("history", {}).setdefault(skill, [])
        if version not in history:
            history.append(version)
        self._write_lock(lock)
        return version

    def rollback(self, skill: str, to_version: str | None = None) -> str:
        lock = self._read_lock()
        history: list[str] = lock.get("history", {}).get(skill, [])
        current = lock.get("active", {}).get(skill)

        if to_version is None:
            if len(history) < 2:
                raise ValueError(f"No previous version for skill '{skill}'")
            idx = history.index(current) if current in history else len(history)
            to_version = history[idx - 1]

        if to_version not in history:
            raise ValueError(f"Version '{to_version}' not in history for '{skill}'")

        cached_path = self._cache_path(skill, to_version)
        if not cached_path.exists():
            self._download(skill, to_version)

        self._deploy(skill, to_version)
        lock.setdefault("active", {})[skill] = to_version
        self._write_lock(lock)
        return to_version

    def update(self, skill: str | None = None, confirm_breaking: bool = True) -> dict[str, str]:
        index = self.fetch_index()
        lock = self._read_lock()
        targets = {skill: lock["active"].get(skill)} if skill else lock.get("active", {})
        results = {}
        for name, current_ver in targets.items():
            latest = index.get("skills", {}).get(name, {}).get("latest", current_ver)
            if latest == current_ver:
                continue
            # Check breaking change
            is_breaking = _is_major_bump(current_ver, latest)
            if is_breaking and confirm_breaking:
                import click
                click.confirm(f"Breaking change: {name} {current_ver}→{latest}. Continue?", abort=True)
            results[name] = self.install(name, latest)
        return results

    def verify(self) -> dict[str, bool]:
        lock = self._read_lock()
        checksums = lock.get("checksums", {})
        results = {}
        for name, version in lock.get("active", {}).items():
            key = f"{name}-{version}"
            expected = checksums.get(key)
            if not expected:
                results[name] = True  # no checksum recorded → skip
                continue
            skill_path = self._skills_dir / name / "SKILL.md"
            if not skill_path.exists():
                results[name] = False
                continue
            actual = hashlib.sha256(skill_path.read_bytes()).hexdigest()
            results[name] = f"sha256:{actual}" == expected
        return results

    def fetch_index(self) -> dict:
        """Download skills-index.json from registry. Cache locally for 24h."""
        import time
        cache = USER_INDEX_CACHE
        cache_age = (time.time() - cache.stat().st_mtime) if cache.exists() else float("inf")
        if cache.exists() and cache_age < 86400:
            return json.loads(cache.read_text(encoding="utf-8"))
        try:
            import httpx
            resp = httpx.get(SKILLS_INDEX_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception:
            if cache.exists():
                return json.loads(cache.read_text(encoding="utf-8"))
            return {}

    def list_cache(self) -> dict[str, dict]:
        result = {}
        if not self._cache_dir.exists():
            return result
        for skill_dir in self._cache_dir.iterdir():
            if skill_dir.is_dir():
                versions = [v.name for v in skill_dir.iterdir() if v.is_dir()]
                size = sum(f.stat().st_size for f in skill_dir.rglob("*") if f.is_file())
                result[skill_dir.name] = {"versions": versions, "size": f"{size//1024}KB"}
        return result

    def clear_cache(self, keep_active: bool = True) -> int:
        lock = self._read_lock()
        active = lock.get("active", {})
        freed = 0
        for skill_dir in self._cache_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            active_ver = active.get(skill_dir.name)
            for ver_dir in skill_dir.iterdir():
                if ver_dir.is_dir():
                    if keep_active and ver_dir.name == active_ver:
                        continue
                    shutil.rmtree(ver_dir)
                    freed += 1
        return freed

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load_index_cached(self) -> dict:
        if USER_INDEX_CACHE.exists():
            return json.loads(USER_INDEX_CACHE.read_text(encoding="utf-8"))
        return {}

    def _cache_path(self, skill: str, version: str) -> Path:
        return self._cache_dir / skill / version

    def _cached_versions(self, skill: str) -> list[str]:
        d = self._cache_dir / skill
        if not d.exists():
            return []
        return sorted(v.name for v in d.iterdir() if v.is_dir())

    def _download(self, skill: str, version: str) -> Path:
        """Download skill zip from registry, verify SHA256, extract to cache."""
        index = self._load_index_cached() or self.fetch_index()
        versions = index.get("skills", {}).get(skill, {}).get("versions", {})
        info = versions.get(version)

        dest = self._cache_path(skill, version)

        if info:
            import httpx, zipfile, io
            resp = httpx.get(info["url"], timeout=30, follow_redirects=True)
            resp.raise_for_status()
            data = resp.content
            # Verify checksum
            if info.get("sha256"):
                actual = "sha256:" + hashlib.sha256(data).hexdigest()
                if actual != info["sha256"]:
                    raise ValueError(f"Checksum mismatch for {skill}@{version}")
            dest.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(dest)
        else:
            # Fallback to builtin
            builtin = SKILLS_BUILTIN_DIR / skill
            if builtin.exists():
                shutil.copytree(builtin, dest, dirs_exist_ok=True)
            else:
                raise FileNotFoundError(
                    f"Skill '{skill}@{version}' not found in registry or builtin."
                )
        return dest

    def _deploy(self, skill: str, version: str) -> None:
        """Copy cached skill into the project's .agents/skills/ directory."""
        src = self._cache_path(skill, version)
        if not src.exists():
            raise FileNotFoundError(f"Cache miss: {skill}@{version}. Run install first.")
        dest = self._skills_dir / skill
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)

    def _read_lock(self) -> dict:
        if self._lock_path.exists():
            with open(self._lock_path, "rb") as f:
                return tomllib.load(f)
        return {"active": {}, "history": {}}

    def _write_lock(self, data: dict) -> None:
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        for section, values in data.items():
            lines.append(f"\n[{section}]")
            if isinstance(values, dict):
                for k, v in values.items():
                    lines.append(f"{k} = {repr(v)}")
        self._lock_path.write_text("\n".join(lines), encoding="utf-8")


def _is_major_bump(current: str, new: str) -> bool:
    try:
        cur_major = int(current.split(".")[0])
        new_major = int(new.split(".")[0])
        return new_major > cur_major
    except Exception:
        return False
