from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from database.models import DailyGoal
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.productivity_repository import ProductivityRepository
from database.repositories.coding_repository import CodingRepository


@dataclass
class HomeSummary:
    active_tasks_count: int = 0
    completed_habits_count: int = 0
    total_habits_count: int = 0
    today_focus_minutes: int = 0
    active_projects_count: int = 0
    today_habits: List[DailyGoal] = field(default_factory=list)


class HomeService:
    """Service orchestrating Home Dashboard data aggregations."""

    def __init__(
        self,
        analytics_repo: Optional[AnalyticsRepository] = None,
        productivity_repo: Optional[ProductivityRepository] = None,
        coding_repo: Optional[CodingRepository] = None,
    ):
        self._analytics_repo = analytics_repo or AnalyticsRepository()
        self._productivity_repo = productivity_repo or ProductivityRepository()
        self._coding_repo = coding_repo or CodingRepository()

    def get_home_summary(self) -> HomeSummary:
        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Reuse AnalyticsRepository aggregation for domain metrics (focus minutes, projects)
        domain_summary = self._analytics_repo.get_domain_summary(today_str, today_str)

        # 2. Query ProductivityRepository for pending tasks count
        all_tasks = self._productivity_repo.get_all_tasks()
        active_tasks = sum(1 for t in all_tasks if not t.is_completed)

        # 3. Retrieve daily habits (which executes repository-level stale goal reset automatically)
        habits = self._productivity_repo.get_daily_goals()

        return HomeSummary(
            active_tasks_count=active_tasks,
            completed_habits_count=sum(1 for h in habits if h.is_completed),
            total_habits_count=len(habits),
            today_focus_minutes=domain_summary.total_focus_minutes,
            active_projects_count=domain_summary.active_projects,
            today_habits=habits,
        )

    def toggle_habit_completion(self, goal_id: int) -> bool:
        return self._productivity_repo.toggle_goal_completion(goal_id)

    def close(self):
        if hasattr(self, "_analytics_repo") and self._analytics_repo:
            self._analytics_repo.close()
        if hasattr(self, "_productivity_repo") and self._productivity_repo:
            self._productivity_repo.close()
        if hasattr(self, "_coding_repo") and self._coding_repo:
            self._coding_repo.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass
