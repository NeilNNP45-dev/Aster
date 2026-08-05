import unittest

from database.connection import DatabaseConnection
from database.models import CodingProject, CodingSession, CodingGoal
from database.repositories.coding_repository import CodingRepository
from services.coding.project_service import ProjectService
from services.coding.goals_service import GoalsService


class TestCodingServices(unittest.TestCase):
    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.repo = CodingRepository(db_conn=self.conn)
        self.project_service = ProjectService(repo=self.repo)
        self.goals_service = GoalsService(repo=self.repo)

    def test_project_time_total(self):
        proj = CodingProject(name="P1")
        proj = self.project_service.add_project(proj)
        # log two sessions
        s1 = CodingSession(project_id=proj.id, start_at="t1", end_at="t2", duration_minutes=30)
        s2 = CodingSession(project_id=proj.id, start_at="t3", end_at="t4", duration_minutes=20)
        self.repo.log_session(s1)
        self.repo.log_session(s2)
        total = self.project_service.get_project_total_time(proj.id)
        self.assertEqual(total, 50)

    def test_goals_service_toggle(self):
        proj = CodingProject(name="P2")
        proj = self.project_service.add_project(proj)
        goal = CodingGoal(title="Do code", project_id=proj.id)
        goal = self.goals_service.add_goal(goal)
        self.assertFalse(goal.is_completed)
        toggled = self.goals_service.toggle_goal(goal.id)
        self.assertTrue(toggled)


if __name__ == "__main__":
    unittest.main()
