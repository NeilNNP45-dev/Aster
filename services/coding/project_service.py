from typing import List, Optional

from database.repositories.coding_repository import CodingRepository
from database.models import CodingProject, CodingSession


class ProjectService:
    """High-level project operations."""

    def __init__(self, repo: Optional[CodingRepository] = None):
        self._repo = repo or CodingRepository()

    def add_project(self, project: CodingProject) -> CodingProject:
        return self._repo.add_project(project)

    def update_project(self, project: CodingProject) -> bool:
        return self._repo.update_project(project)

    def list_projects(self) -> List[CodingProject]:
        return self._repo.list_projects()

    def get_project_total_time(self, project_id: int) -> int:
        sessions = self._repo.get_sessions_by_project(project_id)
        return sum(s.duration_minutes for s in sessions)
