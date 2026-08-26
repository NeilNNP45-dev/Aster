import unittest
from datetime import datetime, timedelta

from database.connection import DatabaseConnection
from database.models import DailyGoal, CodingGoal, CodingProject
from database.repositories.productivity_repository import ProductivityRepository
from database.repositories.coding_repository import CodingRepository


class TestDailyGoalsReset(unittest.TestCase):

    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.prod_repo = ProductivityRepository(db_conn=self.conn)
        self.coding_repo = CodingRepository(db_conn=self.conn)

    def tearDown(self):
        if hasattr(self, "conn") and self.conn is not None:
            self.conn.close()

    def test_same_day_preservation(self):
        """Verify daily goals completed today remain completed when fetched."""
        today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        goal = DailyGoal(
            title="Read 10 pages",
            is_completed=True,
            reset_daily=True,
            streak_count=5,
            last_completed_at=today_str,
        )
        self.prod_repo.add_daily_goal(goal)

        fetched = self.prod_repo.get_daily_goals()
        self.assertEqual(len(fetched), 1)
        self.assertTrue(fetched[0].is_completed)
        self.assertEqual(fetched[0].streak_count, 5)
        self.assertEqual(fetched[0].last_completed_at, today_str)

    def test_previous_day_reset(self):
        """Verify daily goals completed yesterday are reset to is_completed=False, preserving streak and timestamp."""
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        goal = DailyGoal(
            title="Workout 30m",
            is_completed=True,
            reset_daily=True,
            streak_count=12,
            last_completed_at=yesterday_str,
        )
        self.prod_repo.add_daily_goal(goal)

        fetched = self.prod_repo.get_daily_goals()
        self.assertEqual(len(fetched), 1)
        self.assertFalse(fetched[0].is_completed)
        self.assertEqual(fetched[0].streak_count, 12)
        self.assertEqual(fetched[0].last_completed_at, yesterday_str)

    def test_multiple_day_shutdown_reset(self):
        """Verify daily goals completed 5 days ago reset to is_completed=False upon launch/fetch."""
        past_str = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")
        goal = DailyGoal(
            title="Drink Water",
            is_completed=True,
            reset_daily=True,
            streak_count=3,
            last_completed_at=past_str,
        )
        self.prod_repo.add_daily_goal(goal)

        fetched = self.prod_repo.get_daily_goals()
        self.assertEqual(len(fetched), 1)
        self.assertFalse(fetched[0].is_completed)
        self.assertEqual(fetched[0].streak_count, 3)
        self.assertEqual(fetched[0].last_completed_at, past_str)

    def test_non_resetting_goals_remain_completed(self):
        """Verify goals with reset_daily=False remain completed even across day boundaries."""
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        goal = DailyGoal(
            title="One-time Milestone",
            is_completed=True,
            reset_daily=False,
            streak_count=1,
            last_completed_at=yesterday_str,
        )
        self.prod_repo.add_daily_goal(goal)

        fetched = self.prod_repo.get_daily_goals()
        self.assertEqual(len(fetched), 1)
        self.assertTrue(fetched[0].is_completed)
        self.assertEqual(fetched[0].streak_count, 1)

    def test_coding_goals_stale_reset(self):
        """Verify coding goals reset behavior across day boundaries."""
        proj = self.coding_repo.add_project(CodingProject(name="Aster"))
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        cg = CodingGoal(
            title="Solve 2 LeetCode",
            project_id=proj.id,
            is_completed=True,
            reset_daily=True,
            streak_count=7,
            last_completed_at=yesterday_str,
        )
        self.coding_repo.add_goal(cg)

        fetched = self.coding_repo.get_goals_by_project(proj.id)
        self.assertEqual(len(fetched), 1)
        self.assertFalse(fetched[0].is_completed)
        self.assertEqual(fetched[0].streak_count, 7)
        self.assertEqual(fetched[0].last_completed_at, yesterday_str)


if __name__ == "__main__":
    unittest.main()
