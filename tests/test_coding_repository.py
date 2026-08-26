import unittest

from database.connection import DatabaseConnection
from database.repositories.coding_repository import CodingRepository
from database.models import CodingProject, CodingSession, CodingGoal


class TestCodingRepository(unittest.TestCase):

    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.repo = CodingRepository(db_conn=self.conn)

    def tearDown(self):
        if hasattr(self, "conn") and self.conn is not None:
            self.conn.close()


    def test_project_and_session_and_goal_crud(self):
        # Create project
        proj = CodingProject(name="Test Project", repo_path="/tmp/p", language="Python")
        proj = self.repo.add_project(proj)
        self.assertIsNotNone(proj.id)

        projects = self.repo.list_projects()
        self.assertTrue(any(p.id == proj.id for p in projects))

        # Add goal
        goal = CodingGoal(title="Write tests", project_id=proj.id)
        goal = self.repo.add_goal(goal)
        self.assertIsNotNone(goal.id)

        goals = self.repo.get_goals_by_project(proj.id)
        self.assertTrue(any(g.id == goal.id for g in goals))

        # Toggle goal completion
        changed = self.repo.toggle_goal_completion(goal.id)
        self.assertTrue(changed)
        goals = self.repo.get_goals_by_project(proj.id)
        toggled = next((g for g in goals if g.id == goal.id), None)
        self.assertIsNotNone(toggled)

        # Add session
        session = CodingSession(project_id=proj.id, start_at="2026-01-01T12:00:00", end_at="2026-01-01T12:30:00", duration_minutes=30)
        session = self.repo.log_session(session)
        self.assertIsNotNone(session.id)

        sessions = self.repo.get_sessions_by_project(proj.id)
        self.assertTrue(any(s.id == session.id for s in sessions))


if __name__ == "__main__":
    unittest.main()
