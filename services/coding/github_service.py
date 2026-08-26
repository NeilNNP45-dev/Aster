import json
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from database.repositories.coding_repository import CodingRepository


class GitHubService:
    """Minimal GitHub integration for fetching repo metadata.

    Note: Tokens must not be stored in DB. Use OS keyring or Settings.
    """

    API_BASE = "https://api.github.com/repos/"

    def __init__(self, repo: Optional[CodingRepository] = None):
        self._repo = repo or CodingRepository()

    def _normalize_full_name(self, full_name: str) -> Optional[str]:
        value = full_name.strip()
        if value.startswith("git@github.com:"):
            value = value[len("git@github.com:"):]
        elif value.startswith("ssh://git@github.com/"):
            value = value[len("ssh://git@github.com/"):]
        elif value.startswith("git://github.com/"):
            value = value[len("git://github.com/"):]
        elif value.startswith("https://") or value.startswith("http://"):
            value = value.replace("https://", "").replace("http://", "")
        if value.startswith("www."):
            value = value[4:]
        if value.startswith("github.com/"):
            value = value[len("github.com/"):]
        value = value.rstrip("/")
        if value.endswith(".git"):
            value = value[: -len(".git")]
        if "/" in value and len(value.split("/")) == 2:
            return value
        return None

    MAX_RESPONSE_SIZE = 1024 * 1024  # 1 MB maximum response limit

    def fetch_repo_metadata(self, full_name: str, token: Optional[str] = None) -> Optional[dict]:
        normalized = self._normalize_full_name(full_name)
        if not normalized:
            return None
        url = self.API_BASE + normalized
        headers = {"User-Agent": "Aster-App"}
        if token:
            headers["Authorization"] = f"token {token}"

        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=10) as resp:
                content_type = resp.headers.get("Content-Type", "").lower()
                if "json" not in content_type:
                    return None

                chunks = []
                bytes_read = 0
                chunk_size = 8192
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    bytes_read += len(chunk)
                    if bytes_read > self.MAX_RESPONSE_SIZE:
                        return None
                    chunks.append(chunk)

                data = b"".join(chunks)
                parsed = json.loads(data.decode("utf-8"))
                if isinstance(parsed, dict):
                    return parsed
                return None
        except (HTTPError, URLError, json.JSONDecodeError, UnicodeDecodeError, TimeoutError, OSError, ValueError):
            return None

    def sync_project_metadata(self, project_id: int, full_name: str, token: Optional[str] = None) -> bool:
        meta = self.fetch_repo_metadata(full_name, token)
        if not meta:
            return False
        # Update project with core fields
        project = self._repo.list_projects()
        # find project
        target = next((p for p in project if p.id == project_id), None)
        if not target:
            return False
        target.github_full_name = full_name
        target.github_html_url = meta.get("html_url")
        target.description = meta.get("description") or target.description
        target.language = meta.get("language") or target.language
        return self._repo.update_project(target)
