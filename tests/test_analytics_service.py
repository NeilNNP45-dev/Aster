import unittest
from datetime import datetime
from database.connection import DatabaseConnection
from database.models import Task, PomodoroSession
from database.repositories.productivity_repository import ProductivityRepository
from database.repositories.analytics_repository import AnalyticsRepository
from services.analytics.analytics_service import AnalyticsService


class TestAnalyticsService(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseConnection(db_path=":memory:")
        self.prod_repo = ProductivityRepository(db_conn=self.db)
        self.analytics_repo = AnalyticsRepository(db_conn=self.db)
        self.service = AnalyticsService(repo=self.analytics_repo)

    def tearDown(self):
        if hasattr(self, "db"):
            self.db.close()

    def test_date_range_resolution(self):
        """Verify period resolutions."""
        start_w, end_w = self.service.resolve_date_range("this_week")
        self.assertIsNotNone(start_w)
        self.assertIsNotNone(end_w)

        start_m, end_m = self.service.resolve_date_range("this_month")
        self.assertTrue(start_m.endswith("-01"))

    def test_report_generation(self):
        """Verify report summary generation."""
        # Add sample data
        self.prod_repo.add_task(Task(title="Finish Report", is_completed=True))
        self.prod_repo.log_pomodoro_session(PomodoroSession(duration_minutes=50, session_type="Work"))

        report = self.service.generate_report(report_type="Weekly")
        self.assertEqual(report.report_type, "Weekly")
        self.assertTrue(len(report.highlights) > 0)
        self.assertIn("Tasks Completed", report.productivity_notes)

    def test_week_over_week_comparison(self):
        """Verify comparison structure."""
        comp = self.service.get_week_over_week_comparison()
        self.assertIn("focus_change_pct", comp)
        self.assertIn("focus_trend", comp)
        self.assertIn("tasks_change_pct", comp)


if __name__ == "__main__":
    unittest.main()
