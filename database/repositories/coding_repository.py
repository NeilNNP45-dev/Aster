from typing import List, Optional
from database.connection import DatabaseConnection
from database.models import CodingProject, CodingSession, CodingGoal


class CodingRepository:
    """Repository for Coding domain persistence."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self.db = db_conn or DatabaseConnection()

    # ---------- Projects ----------
    def add_project(self, project: CodingProject) -> CodingProject:
        query = """
            INSERT INTO coding_projects (name, repo_path, github_full_name, github_html_url, description, language, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    project.name,
                    project.repo_path,
                    project.github_full_name,
                    project.github_html_url,
                    project.description,
                    project.language,
                    1 if project.is_active else 0,
                ),
            )
            project.id = cursor.lastrowid
        return project

    def list_projects(self) -> List[CodingProject]:
        query = "SELECT * FROM coding_projects ORDER BY id DESC"
        projects: List[CodingProject] = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                projects.append(
                    CodingProject(
                        id=row["id"],
                        name=row["name"],
                        repo_path=row["repo_path"],
                        github_full_name=row["github_full_name"],
                        github_html_url=row["github_html_url"],
                        description=row["description"],
                        language=row["language"],
                        is_active=bool(row["is_active"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return projects

    def update_project(self, project: CodingProject) -> bool:
        if project.id is None:
            return False
        query = """
            UPDATE coding_projects
            SET name = ?, repo_path = ?, github_full_name = ?, github_html_url = ?, description = ?, language = ?, is_active = ?, updated_at = datetime('now','localtime')
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    project.name,
                    project.repo_path,
                    project.github_full_name,
                    project.github_html_url,
                    project.description,
                    project.language,
                    1 if project.is_active else 0,
                    project.id,
                ),
            )
            return cursor.rowcount > 0

    # ---------- Sessions ----------
    def log_session(self, session: CodingSession) -> CodingSession:
        query = """
            INSERT INTO coding_sessions (project_id, start_at, end_at, duration_minutes, session_type, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    session.project_id,
                    session.start_at,
                    session.end_at,
                    session.duration_minutes,
                    session.session_type,
                    session.notes,
                ),
            )
            session.id = cursor.lastrowid
        return session

    def get_sessions_by_project(self, project_id: Optional[int]) -> List[CodingSession]:
        query = "SELECT * FROM coding_sessions"
        params: tuple = ()
        if project_id is not None:
            query += " WHERE project_id = ?"
            params = (project_id,)
        query += " ORDER BY id DESC"

        sessions: List[CodingSession] = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                sessions.append(
                    CodingSession(
                        id=row["id"],
                        project_id=row["project_id"],
                        start_at=row["start_at"],
                        end_at=row["end_at"],
                        duration_minutes=row["duration_minutes"],
                        session_type=row["session_type"],
                        notes=row["notes"],
                        created_at=row["created_at"],
                    )
                )
        return sessions

    # ---------- Goals ----------
    def add_goal(self, goal: CodingGoal) -> CodingGoal:
        query = "INSERT INTO coding_goals (title, project_id, is_completed, reset_daily, streak_count, last_completed_at) VALUES (?, ?, ?, ?, ?, ?)"
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    goal.title,
                    goal.project_id,
                    1 if goal.is_completed else 0,
                    1 if goal.reset_daily else 0,
                    goal.streak_count,
                    goal.last_completed_at,
                ),
            )
            goal.id = cursor.lastrowid
        return goal

    def get_goals_by_project(self, project_id: Optional[int] = None) -> List[CodingGoal]:
        query = "SELECT * FROM coding_goals"
        params: tuple = ()
        if project_id is not None:
            query += " WHERE project_id = ?"
            params = (project_id,)
        query += " ORDER BY id DESC"

        goals: List[CodingGoal] = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                goals.append(
                    CodingGoal(
                        id=row["id"],
                        title=row["title"],
                        project_id=row["project_id"],
                        is_completed=bool(row["is_completed"]),
                        reset_daily=bool(row["reset_daily"]),
                        streak_count=row["streak_count"],
                        last_completed_at=row["last_completed_at"],
                        created_at=row["created_at"],
                    )
                )
        return goals

    def toggle_goal_completion(self, goal_id: int) -> bool:
        query = """
            UPDATE coding_goals
            SET is_completed = CASE WHEN is_completed = 1 THEN 0 ELSE 1 END,
                streak_count = CASE WHEN is_completed = 0 THEN streak_count + 1 ELSE max(0, streak_count - 1) END,
                last_completed_at = CASE WHEN is_completed = 0 THEN datetime('now', 'localtime') ELSE last_completed_at END
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (goal_id,))
            return cursor.rowcount > 0
