import unittest
from datetime import datetime

from database.connection import DatabaseConnection
from database.models import Task, DailyGoal, CodingProject, PomodoroSession
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.productivity_repository import ProductivityRepository
from database.repositories.coding_repository import CodingRepository
from services.home.home_service import HomeService


class TestHomeService(unittest.TestCase):

    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.analytics_repo = AnalyticsRepository(db_conn=self.conn)
        self.prod_repo = ProductivityRepository(db_conn=self.conn)
        self.coding_repo = CodingRepository(db_conn=self.conn)
        self.service = HomeService(
            analytics_repo=self.analytics_repo,
            productivity_repo=self.prod_repo,
            coding_repo=self.coding_repo,
        )

    def tearDown(self):
        if hasattr(self, "service") and self.service is not None:
            self.service.close()

    def test_get_home_summary(self):
        # 1. Add tasks (1 completed, 2 pending)
        self.prod_repo.add_task(Task(title="Task 1", is_completed=True))
        self.prod_repo.add_task(Task(title="Task 2", is_completed=False))
        self.prod_repo.add_task(Task(title="Task 3", is_completed=False))

        # 2. Add habit
        self.prod_repo.add_daily_goal(DailyGoal(title="Water", is_completed=True))
        self.prod_repo.add_daily_goal(DailyGoal(title="Read", is_completed=False))

        # 3. Add project
        self.coding_repo.add_project(CodingProject(name="Aster", is_active=True))

        # 4. Add Pomodoro work session
        self.prod_repo.log_pomodoro_session(PomodoroSession(duration_minutes=25, session_type="Work"))

        summary = self.service.get_home_summary()

        self.assertEqual(summary.active_tasks_count, 2)
        self.assertEqual(summary.completed_habits_count, 1)
        self.assertEqual(summary.total_habits_count, 2)
        self.assertEqual(summary.today_focus_minutes, 25)
        self.assertEqual(summary.active_projects_count, 1)
        self.assertEqual(len(summary.today_habits), 2)

    def test_toggle_habit_completion(self):
        habit = self.prod_repo.add_daily_goal(DailyGoal(title="Exercise"))
        self.assertFalse(habit.is_completed)

        toggled = self.service.toggle_habit_completion(habit.id)
        self.assertTrue(toggled)

        summary = self.service.get_home_summary()
        self.assertEqual(summary.completed_habits_count, 1)


if __name__ == "__main__":
    unittest.main()
