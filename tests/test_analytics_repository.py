import unittest
from datetime import datetime
from database.connection import DatabaseConnection
from database.models import (
    Task,
    DailyGoal,
    PomodoroSession,
    CodingSession,
    WorkoutEntry,
    WeightEntry,
)
from database.repositories.productivity_repository import ProductivityRepository
from database.repositories.coding_repository import CodingRepository
from database.repositories.analytics_repository import AnalyticsRepository


class TestAnalyticsRepository(unittest.TestCase):

    def setUp(self):
        self.db = DatabaseConnection(db_path=":memory:")
        self.prod_repo = ProductivityRepository(db_conn=self.db)
        self.coding_repo = CodingRepository(db_conn=self.db)
        self.analytics_repo = AnalyticsRepository(db_conn=self.db)

    def tearDown(self):
        if hasattr(self, "db"):
            self.db.close()

    def test_week_bounds(self):
        """Verify Monday to Sunday week bounds calculation."""
        # Wednesday June 10, 2026 -> Monday June 8 to Sunday June 14
        dt = datetime(2026, 6, 10)
        monday, sunday = AnalyticsRepository.get_week_bounds(dt)
        self.assertEqual(monday, "2026-06-08")
        self.assertEqual(sunday, "2026-06-14")

    def test_month_bounds(self):
        """Verify month bounds calculation."""
        dt = datetime(2026, 6, 10)
        first, last = AnalyticsRepository.get_month_bounds(dt)
        self.assertEqual(first, "2026-06-01")
        self.assertEqual(last, "2026-06-30")

    def test_analytics_aggregation(self):
        """Verify multi-domain metrics aggregation across tasks, pomodoros, coding, and workouts."""
        today_str = datetime.now().strftime("%Y-%m-%d")

        # Add tasks
        t1 = Task(title="Task 1", is_completed=True)
        t2 = Task(title="Task 2", is_completed=False)
        self.prod_repo.add_task(t1)
        self.prod_repo.add_task(t2)

        # Add pomodoro session
        pomo = PomodoroSession(duration_minutes=25, session_type="Work")
        self.prod_repo.log_pomodoro_session(pomo)

        # Add coding session
        cs = CodingSession(start_at=f"{today_str} 10:00:00", duration_minutes=45, session_type="Coding")
        self.coding_repo.log_session(cs)

        # Add workout & weight directly
        with self.db.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO fitness_workouts (title, workout_type, duration_minutes, calories, performed_at) VALUES (?, ?, ?, ?, ?)",
                ("Morning Run", "Cardio", 30, 250, f"{today_str} 07:00:00"),
            )
            cursor.execute(
                "INSERT INTO fitness_weights (weight_kg, recorded_at) VALUES (?, ?)",
                (72.5, f"{today_str} 08:00:00"),
            )

        # Query summary
        summary = self.analytics_repo.get_domain_summary(today_str, today_str)

        self.assertEqual(summary.tasks_total, 2)
        self.assertEqual(summary.tasks_completed, 1)
        self.assertEqual(summary.total_focus_minutes, 70)  # 25 + 45
        self.assertEqual(summary.coding_minutes, 45)
        self.assertEqual(summary.workouts_completed, 1)
        self.assertEqual(summary.workout_minutes, 30)
        self.assertEqual(summary.calories_burned, 250)
        self.assertEqual(summary.latest_weight_kg, 72.5)

    def test_daily_focus_breakdown(self):
        """Verify daily focus minutes breakdown."""
        today_str = datetime.now().strftime("%Y-%m-%d")

        pomo = PomodoroSession(duration_minutes=50, session_type="Work")
        self.prod_repo.log_pomodoro_session(pomo)

        breakdown = self.analytics_repo.get_daily_focus_breakdown(today_str, today_str)
        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0].date_str, today_str)
        self.assertEqual(breakdown[0].pomodoro_minutes, 50)
        self.assertEqual(breakdown[0].total_minutes, 50)


if __name__ == "__main__":
    unittest.main()
