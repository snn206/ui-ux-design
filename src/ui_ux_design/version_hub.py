"""
version_hub.py — Client for the official GitHub Version Hub (snn206/ui-ux-design).

Fetches release catalog from GitHub, downloads version packages from GitHub Releases / Tags,
and caches them locally for seamless offline usage and switching.
"""

from __future__ import annotations

import io
import json
import logging
import shutil
import time
import zipfile
from pathlib import Path
from typing import Any

from ui_ux_design.platform import (
    GITHUB_REPO,
    GITHUB_RAW_BASE,
    GITHUB_RELEASES_URL,
    GITHUB_ARCHIVE_URL,
    VERSIONS_INDEX_URL,
    USER_VERSIONS_CACHE,
    VERSIONS_BUNDLED_FILE,
    USER_CACHE_DIR,
    SKILLS_BUILTIN_DIR,
    PROJECT_ROOT,
)

logger = logging.getLogger(__name__)


class GitHubVersionHub:
    """
    Interacts with the GitHub Version Store:
    - Fetches the catalog of available releases (versions.json) from GitHub main branch
    - Downloads release archives from GitHub Releases or GitHub tag archives
    - Manages local cache at ~/.config/ui-ux-design/skills_cache/<version>/
    """

    def __init__(
        self,
        cache_dir: Path | None = None,
        versions_cache: Path | None = None,
        versions_url: str | None = None,
    ) -> None:
        self.cache_dir = cache_dir or USER_CACHE_DIR
        self.versions_cache = versions_cache or USER_VERSIONS_CACHE
        self.versions_url = versions_url or VERSIONS_INDEX_URL

    # ── Catalog Discovery ──────────────────────────────────────────────────────

    def fetch_catalog(self, force_refresh: bool = False) -> dict[str, Any]:
        """
        Fetch versions.json from GitHub with a 24-hour local cache.
        Falls back to local/bundled versions.json if offline.
        """
        if not force_refresh and self.versions_cache.exists():
            try:
                mtime = self.versions_cache.stat().st_mtime
                if (time.time() - mtime) < 86400:  # 24h
                    return json.loads(self.versions_cache.read_text(encoding="utf-8"))
            except Exception as e:
                logger.debug("Failed reading versions cache: %s", e)

        # Attempt to fetch from GitHub
        try:
            import httpx
            resp = httpx.get(self.versions_url, timeout=10, follow_redirects=True)
            if resp.status_code == 200:
                data = resp.json()
                self.versions_cache.parent.mkdir(parents=True, exist_ok=True)
                self.versions_cache.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                return data
        except Exception as e:
            logger.debug("Could not reach GitHub versions index at %s: %s", self.versions_url, e)

        # Fallback 1: Stale cache
        if self.versions_cache.exists():
            try:
                return json.loads(self.versions_cache.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Fallback 2: Project root versions.json
        project_versions = PROJECT_ROOT / "versions.json"
        if project_versions.exists():
            try:
                return json.loads(project_versions.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Fallback 3: Package bundled versions.json
        if VERSIONS_BUNDLED_FILE.exists():
            try:
                return json.loads(VERSIONS_BUNDLED_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Ultimate fallback minimal catalog
        return {
            "schema_version": "1.0",
            "repository": GITHUB_REPO,
            "latest_release": "v1.0.0",
            "releases": {
                "v1.0.0": {
                    "tag": "v1.0.0",
                    "version": "1.0.0",
                    "date": "2026-03-01",
                    "type": "stable",
                    "description": "Foundation Release",
                    "changelog": ["Initial 9 skills and 18 MCP tools"]
                }
            },
            "skills": {}
        }

    def list_releases(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        Return a list of all releases from the GitHub catalog, annotated with cache status.
        """
        catalog = self.fetch_catalog(force_refresh=force_refresh)
        releases_dict = catalog.get("releases", {})
        latest_tag = catalog.get("latest_release", "")

        results = []
        for tag, info in releases_dict.items():
            version_str = info.get("version", tag.lstrip("v"))
            is_cached = self.is_version_cached(tag) or self.is_version_cached(version_str)
            item = dict(info)
            item["tag"] = tag
            item["version"] = version_str
            item["is_latest"] = (tag == latest_tag or version_str == latest_tag.lstrip("v"))
            item["is_cached"] = is_cached
            results.append(item)

        # Sort by tag/version descending
        results.sort(key=lambda r: r.get("date", ""), reverse=True)
        return results

    def is_version_cached(self, version_or_tag: str) -> bool:
        """Check whether a version is already extracted and available in local cache."""
        ver = self._normalize_tag(version_or_tag)
        dir1 = self.cache_dir / ver
        dir2 = self.cache_dir / ver.lstrip("v")
        for d in (dir1, dir2):
            if d.exists() and any(d.iterdir()):
                return True
        return False

    def get_cached_path(self, version_or_tag: str) -> Path | None:
        """Return the path to the cached version directory if it exists."""
        ver = self._normalize_tag(version_or_tag)
        for d in (self.cache_dir / ver, self.cache_dir / ver.lstrip("v")):
            if d.exists() and any(d.iterdir()):
                return d
        return None

    # ── Download & Cache ───────────────────────────────────────────────────────

    def download_version(
        self,
        version_or_tag: str,
        force_download: bool = False,
    ) -> Path:
        """
        Download a specific version package from GitHub and extract it into local cache.
        Returns the Path to the cached version directory.
        """
        ver = self._normalize_tag(version_or_tag)
        cached_path = self.get_cached_path(ver)

        if cached_path and not force_download:
            logger.info("Version %s is already cached at %s", ver, cached_path)
            return cached_path

        dest_dir = self.cache_dir / ver
        dest_dir.mkdir(parents=True, exist_ok=True)

        catalog = self.fetch_catalog()
        releases = catalog.get("releases", {})
        release_info = releases.get(ver) or releases.get(f"v{ver}") or releases.get(ver.lstrip("v")) or {}

        # Candidate URLs to download from
        urls_to_try = []
        if release_info.get("download_url"):
            urls_to_try.append(release_info["download_url"])
        if release_info.get("archive_fallback_url"):
            urls_to_try.append(release_info["archive_fallback_url"])
        urls_to_try.append(f"{GITHUB_ARCHIVE_URL}/{ver}.zip")
        urls_to_try.append(f"{GITHUB_ARCHIVE_URL}/v{ver.lstrip('v')}.zip")

        download_success = False
        import httpx

        for url in urls_to_try:
            try:
                logger.info("Attempting download from GitHub: %s", url)
                resp = httpx.get(url, timeout=30, follow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 100:
                    self._extract_zip_archive(resp.content, dest_dir)
                    download_success = True
                    break
            except Exception as e:
                logger.debug("Failed download from %s: %s", url, e)

        if not download_success:
            # Fallback when offline or release not yet pushed to GitHub Releases
            logger.warning(
                "Could not download %s from GitHub. Falling back to built-in template.",
                ver,
            )
            self._fallback_populate(ver, dest_dir)

        return dest_dir

    def list_cached_versions(self) -> list[str]:
        """Return list of versions currently in local cache."""
        if not self.cache_dir.exists():
            return []
        versions = []
        for d in self.cache_dir.iterdir():
            if d.is_dir() and any(d.iterdir()):
                versions.append(d.name)
        return sorted(versions)

    # ── Internal Helpers ───────────────────────────────────────────────────────

    def _normalize_tag(self, tag: str) -> str:
        tag = tag.strip()
        if not tag.startswith("v") and any(c.isdigit() for c in tag):
            return f"v{tag}"
        return tag

    def _extract_zip_archive(self, zip_bytes: bytes, target_dir: Path) -> None:
        """
        Extract skill folders from a zip file (either a standalone skills zip or a repo archive).
        """
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            namelist = zf.namelist()
            # Check if this is a repo archive (e.g. ui-ux-design-1.0.0/.agents/skills/...)
            skills_prefix = None
            for name in namelist:
                if "/.agents/skills/" in name or name.startswith(".agents/skills/"):
                    idx = name.find(".agents/skills/")
                    skills_prefix = name[:idx + len(".agents/skills/")]
                    break
                elif "/skills_builtin/" in name or name.startswith("skills_builtin/"):
                    idx = name.find("skills_builtin/")
                    skills_prefix = name[:idx + len("skills_builtin/")]
                    break

            if skills_prefix:
                for member in zf.infolist():
                    if member.filename.startswith(skills_prefix) and not member.is_dir():
                        rel_path = member.filename[len(skills_prefix):]
                        dest_file = target_dir / rel_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(member) as src, open(dest_file, "wb") as dst:
                            dst.write(src.read())
            else:
                # Direct skills zip
                zf.extractall(target_dir)

    def _fallback_populate(self, ver: str, target_dir: Path) -> None:
        """
        Offline fallback: populate target_dir using SKILLS_BUILTIN_DIR or local project.
        """
        source = SKILLS_BUILTIN_DIR
        if not source.exists() or not any(source.iterdir()):
            source = PROJECT_ROOT / ".agents" / "skills"

        if source.exists() and any(source.iterdir()):
            for item in source.iterdir():
                if item.is_dir():
                    dest_skill = target_dir / item.name
                    if dest_skill.exists():
                        shutil.rmtree(dest_skill)
                    shutil.copytree(item, dest_skill)

            # Mark version in SKILL.md headers or notes
            tag_name = ver if ver.startswith("v") else f"v{ver}"
            version_badge = f"\n<!-- Version: {tag_name} (from GitHub Catalog) -->\n"
            for skill_dir in target_dir.iterdir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    try:
                        content = skill_md.read_text(encoding="utf-8")
                        if "<!-- Version:" not in content:
                            skill_md.write_text(content + version_badge, encoding="utf-8")
                    except Exception:
                        pass
        else:
            raise RuntimeError(f"Cannot populate version {ver}: no local fallback skills found.")
