from typing import List, Optional
from database.connection import DatabaseConnection
from database.models import Task, DailyGoal, Note, PomodoroSession


class ProductivityRepository:
    """Repository handling all CRUD database operations for Productivity entities."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self.db = db_conn or DatabaseConnection()

    def close(self):
        if hasattr(self, "db") and self.db is not None:
            self.db.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


    # ==================== TASKS (To-Do List) ====================

    def add_task(self, task: Task) -> Task:
        """Insert a new task into database."""
        query = """
            INSERT INTO tasks (title, description, priority, category, due_date, is_completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.category,
                    task.due_date,
                    1 if task.is_completed else 0,
                ),
            )
            task.id = cursor.lastrowid
            
            # Fetch generated timestamp
            cursor.execute("SELECT created_at FROM tasks WHERE id = ?", (task.id,))
            row = cursor.fetchone()
            if row:
                task.created_at = row["created_at"]
        return task

    def get_all_tasks(self, category: Optional[str] = None) -> List[Task]:
        """Retrieve all tasks, optionally filtered by category."""
        if category:
            query = "SELECT * FROM tasks WHERE category = ? ORDER BY is_completed ASC, id DESC"
            params = (category,)
        else:
            query = "SELECT * FROM tasks ORDER BY is_completed ASC, id DESC"
            params = ()

        tasks = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                tasks.append(
                    Task(
                        id=row["id"],
                        title=row["title"],
                        description=row["description"],
                        priority=row["priority"],
                        category=row["category"],
                        due_date=row["due_date"],
                        is_completed=bool(row["is_completed"]),
                        created_at=row["created_at"],
                    )
                )
        return tasks

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Fetch a single task by ID."""
        query = "SELECT * FROM tasks WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (task_id,))
            row = cursor.fetchone()
            if row:
                return Task(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    priority=row["priority"],
                    category=row["category"],
                    due_date=row["due_date"],
                    is_completed=bool(row["is_completed"]),
                    created_at=row["created_at"],
                )
        return None

    def update_task(self, task: Task) -> bool:
        """Update an existing task."""
        if task.id is None:
            return False
        query = """
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, category = ?, due_date = ?, is_completed = ?
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.category,
                    task.due_date,
                    1 if task.is_completed else 0,
                    task.id,
                ),
            )
            return cursor.rowcount > 0

    def toggle_task_completion(self, task_id: int) -> bool:
        """Toggle task completion state."""
        query = "UPDATE tasks SET is_completed = CASE WHEN is_completed = 1 THEN 0 ELSE 1 END WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (task_id,))
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        query = "DELETE FROM tasks WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (task_id,))
            return cursor.rowcount > 0

    # ==================== DAILY GOALS (Habits) ====================

    def add_daily_goal(self, goal: DailyGoal) -> DailyGoal:
        """Insert a new daily goal."""
        query = """
            INSERT INTO daily_goals (title, category, is_completed, reset_daily, streak_count, last_completed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    goal.title,
                    goal.category,
                    1 if goal.is_completed else 0,
                    1 if goal.reset_daily else 0,
                    goal.streak_count,
                    goal.last_completed_at,
                ),
            )
            goal.id = cursor.lastrowid
        return goal

    def get_daily_goals(self) -> List[DailyGoal]:
        """Retrieve all daily goals."""
        query = "SELECT * FROM daily_goals ORDER BY id ASC"
        goals = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                goals.append(
                    DailyGoal(
                        id=row["id"],
                        title=row["title"],
                        category=row["category"],
                        is_completed=bool(row["is_completed"]),
                        reset_daily=bool(row["reset_daily"]),
                        streak_count=row["streak_count"],
                        last_completed_at=row["last_completed_at"],
                    )
                )
        return goals

    def toggle_goal_completion(self, goal_id: int) -> bool:
        """Toggle goal completion and update streak."""
        query = """
            UPDATE daily_goals
            SET is_completed = CASE WHEN is_completed = 1 THEN 0 ELSE 1 END,
                streak_count = CASE WHEN is_completed = 0 THEN streak_count + 1 ELSE max(0, streak_count - 1) END,
                last_completed_at = CASE WHEN is_completed = 0 THEN datetime('now', 'localtime') ELSE last_completed_at END
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (goal_id,))
            return cursor.rowcount > 0

    def delete_daily_goal(self, goal_id: int) -> bool:
        """Delete a daily goal by ID."""
        query = "DELETE FROM daily_goals WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (goal_id,))
            return cursor.rowcount > 0

    # ==================== NOTES ====================

    def add_note(self, note: Note) -> Note:
        """Insert a new note."""
        query = "INSERT INTO notes (title, content, category) VALUES (?, ?, ?)"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (note.title, note.content, note.category))
            note.id = cursor.lastrowid
            
            cursor.execute("SELECT created_at, updated_at FROM notes WHERE id = ?", (note.id,))
            row = cursor.fetchone()
            if row:
                note.created_at = row["created_at"]
                note.updated_at = row["updated_at"]
        return note

    def get_all_notes(self) -> List[Note]:
        """Retrieve all notes sorted by updated_at descending."""
        query = "SELECT * FROM notes ORDER BY updated_at DESC"
        notes = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                notes.append(
                    Note(
                        id=row["id"],
                        title=row["title"],
                        content=row["content"],
                        category=row["category"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return notes

    def get_note_by_id(self, note_id: int) -> Optional[Note]:
        """Fetch a single note by ID."""
        query = "SELECT * FROM notes WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (note_id,))
            row = cursor.fetchone()
            if row:
                return Note(
                    id=row["id"],
                    title=row["title"],
                    content=row["content"],
                    category=row["category"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
        return None

    def update_note(self, note: Note) -> bool:
        """Update note title, content, and category."""
        if note.id is None:
            return False
        query = """
            UPDATE notes
            SET title = ?, content = ?, category = ?, updated_at = datetime('now', 'localtime')
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (note.title, note.content, note.category, note.id))
            return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        """Delete a note by ID."""
        query = "DELETE FROM notes WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (note_id,))
            return cursor.rowcount > 0

    # ==================== POMODORO SESSIONS ====================

    def log_pomodoro_session(self, session: PomodoroSession) -> PomodoroSession:
        """Log a completed Pomodoro focus session."""
        query = "INSERT INTO pomodoro_sessions (duration_minutes, session_type) VALUES (?, ?)"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (session.duration_minutes, session.session_type))
            session.id = cursor.lastrowid
            
            cursor.execute("SELECT completed_at FROM pomodoro_sessions WHERE id = ?", (session.id,))
            row = cursor.fetchone()
            if row:
                session.completed_at = row["completed_at"]
        return session

    def get_recent_pomodoro_sessions(self, limit: int = 20) -> List[PomodoroSession]:
        """Retrieve recent completed pomodoro sessions."""
        query = "SELECT * FROM pomodoro_sessions ORDER BY id DESC LIMIT ?"
        sessions = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (limit,))
            for row in cursor.fetchall():
                sessions.append(
                    PomodoroSession(
                        id=row["id"],
                        duration_minutes=row["duration_minutes"],
                        session_type=row["session_type"],
                        completed_at=row["completed_at"],
                    )
                )
        return sessions
