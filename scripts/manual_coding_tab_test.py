from PySide6.QtWidgets import QApplication
import sys
from pathlib import Path

# ensure repo root on sys.path
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ui.pages.coding.page import CodingPage
from database.connection import DatabaseConnection
from database.repositories.coding_repository import CodingRepository
from services.coding.project_service import ProjectService
from services.coding.goals_service import GoalsService
from services.coding.coding_timer_service import CodingTimerService
from services.coding.github_service import GitHubService
from database.models import CodingProject, CodingGoal


def run():
    app = QApplication(sys.argv)
    # create coding page (which creates its own services)
    page = CodingPage()
    services = page._services
    repo = services.get("repo")
    project_service = services.get("project_service")
    goals_service = services.get("goals_service")
    timer_service = services.get("timer_service")
    github_service = services.get("github_service")

    # Add project
    p = project_service.add_project(CodingProject(name="TestProject", repo_path="/tmp", github_full_name="psf/requests"))
    print("Added project", p.id)

    # Add goal
    g = goals_service.add_goal(CodingGoal(title="Solve two problems", reset_daily=False))
    print("Added goal", g.id)

    # Simulate timer: start 3 seconds and invoke ticks
    timer_service.start(duration_seconds=3, project_id=p.id)
    # call _on_tick 3 times
    for _ in range(4):
        timer_service._on_tick()

    sessions = repo.get_sessions_by_project(p.id)
    print("Sessions for project:", len(sessions))

    # GitHub sync (metadata)
    ok = github_service.sync_project_metadata(p.id, "psf/requests", token=None)
    print("GitHub sync ok:", ok)

    print('Manual coding tab scripted test complete')


if __name__ == '__main__':
    run()
