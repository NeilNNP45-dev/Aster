from typing import List, Optional

from database.repositories.coding_repository import CodingRepository
from database.models import CodingGoal


class GoalsService:
    """Business logic for coding goals (habit-like)."""

    def __init__(self, repo: Optional[CodingRepository] = None):
        self._repo = repo or CodingRepository()

    def add_goal(self, goal: CodingGoal) -> CodingGoal:
        return self._repo.add_goal(goal)

    def list_goals(self, project_id: Optional[int] = None) -> List[CodingGoal]:
        return self._repo.get_goals_by_project(project_id)

    def toggle_goal(self, goal_id: int) -> bool:
        return self._repo.toggle_goal_completion(goal_id)
