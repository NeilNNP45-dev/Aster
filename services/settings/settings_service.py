from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from database.connection import DatabaseConnection


@dataclass
class StorageInfo:
    db_filename: str
    db_path: str
    file_size_formatted: str
    journal_mode: str
    privacy_mode: str


@dataclass
class AppSettingsInfo:
    app_name: str = "Aster"
    version: str = "v0.6.0"
    version_title: str = "Analytics & Productivity Suite"
    theme_name: str = "Sleek Dark Theme"
    github_auth_policy: str = "Session-only (Tokens requested on-demand, never saved)"


class SettingsService:
    """Service providing safe application preferences and storage diagnostics for the Settings UI."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self._db = db_conn or DatabaseConnection()

    def get_app_info(self) -> AppSettingsInfo:
        return AppSettingsInfo()

    def get_storage_info(self) -> StorageInfo:
        db_path_obj = Path(self._db.db_path)
        size_bytes = 0
        if db_path_obj.exists():
            try:
                size_bytes = db_path_obj.stat().st_size
            except OSError:
                size_bytes = 0

        if size_bytes < 1024:
            size_fmt = f"{size_bytes} Bytes"
        elif size_bytes < 1024 * 1024:
            size_fmt = f"{size_bytes / 1024:.1f} KB"
        else:
            size_fmt = f"{size_bytes / (1024 * 1024):.2f} MB"

        return StorageInfo(
            db_filename=db_path_obj.name,
            db_path=str(db_path_obj),
            file_size_formatted=size_fmt,
            journal_mode="WAL (Write-Ahead Logging)",
            privacy_mode="100% Local & Private",
        )

    def close(self):
        if hasattr(self, "_db") and self._db:
            self._db.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
