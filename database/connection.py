import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional


class DatabaseConnection:
    """SQLite Database Connection Manager for Aster."""

    DEFAULT_DB_FILENAME = "aster.db"

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            base_dir = Path(__file__).parent
            self.db_path = str(base_dir / self.DEFAULT_DB_FILENAME)
        else:
            self.db_path = db_path

        # Use a shared connection per DatabaseConnection instance to avoid creating
        # transient sqlite3.Connection objects during import-time operations.
        self._shared_conn: Optional[sqlite3.Connection] = None
        try:
            self._shared_conn = sqlite3.connect(self.db_path if self.db_path != ":memory:" else ":memory:", check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row
            self._shared_conn.execute("PRAGMA foreign_keys = ON;")
            # For file-backed DBs prefer WAL for concurrency
            if self.db_path != ":memory:":
                self._shared_conn.execute("PRAGMA journal_mode = WAL;")
        except Exception:
            # fallback: leave _shared_conn as None
            self._shared_conn = None

        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create or return a configured sqlite3 connection."""
        if self._shared_conn is not None:
            return self._shared_conn

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        return conn

    def _init_db(self):
        """Initialize SQLite database schema from schema.sql."""
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Database schema file not found at: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            # if this is not the shared in-memory connection, close it to avoid leaks
            if self._shared_conn is None:
                try:
                    conn.close()
                except Exception:
                    pass

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager yielding a database cursor with auto-commit/rollback handling."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            if self._shared_conn is None:
                conn.close()

    def close(self):
        """Close shared connection if active."""
        if self._shared_conn is not None:
            self._shared_conn.close()
            self._shared_conn = None
