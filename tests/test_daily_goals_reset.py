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
        """Verify yesterday's completion resets for today but can continue the streak."""
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
        """Verify reopening after several missed days resets the stale streak."""
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
        self.assertEqual(fetched[0].streak_count, 0)
        self.assertEqual(fetched[0].last_completed_at, past_str)

    def test_consecutive_days_continue_streak(self):
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        goal = DailyGoal(title="Read", streak_count=4, last_completed_at=yesterday_str)
        self.prod_repo.add_daily_goal(goal)

        fetched = self.prod_repo.get_daily_goals()
        self.assertFalse(fetched[0].is_completed)
        self.prod_repo.toggle_goal_completion(fetched[0].id)
        self.assertEqual(self.prod_repo.get_daily_goals()[0].streak_count, 5)

    def test_missing_one_day_does_not_increment_old_streak(self):
        two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        goal = DailyGoal(title="Exercise", streak_count=8, last_completed_at=two_days_ago)
        self.prod_repo.add_daily_goal(goal)

        fetched = self.prod_repo.get_daily_goals()
        self.assertEqual(fetched[0].streak_count, 0)
        self.prod_repo.toggle_goal_completion(fetched[0].id)
        self.assertEqual(self.prod_repo.get_daily_goals()[0].streak_count, 1)

    def test_unchecking_today_resets_completion_without_advancing_streak(self):
        goal = DailyGoal(title="Water", streak_count=2)
        self.prod_repo.add_daily_goal(goal)
        self.prod_repo.toggle_goal_completion(goal.id)
        self.assertTrue(self.prod_repo.get_daily_goals()[0].is_completed)
        self.prod_repo.toggle_goal_completion(goal.id)
        fetched = self.prod_repo.get_daily_goals()[0]
        self.assertFalse(fetched.is_completed)
        self.assertEqual(fetched.streak_count, 2)

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
