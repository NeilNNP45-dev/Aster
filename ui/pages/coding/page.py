from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget, QButtonGroup, QPushButton

from database.connection import DatabaseConnection
from database.repositories.coding_repository import CodingRepository
from services.coding.project_service import ProjectService
from services.coding.goals_service import GoalsService
from services.coding.coding_timer_service import CodingTimerService
from services.coding.github_service import GitHubService
from ui.pages.coding.projects_widget import ProjectsWidget
from ui.pages.coding.coding_timer_widget import CodingTimerWidget
from ui.pages.coding.coding_goals_widget import CodingGoalsWidget
from ui.pages.coding.github_widget import GitHubWidget


class CodingPage(QWidget):
    _TABS = ["⏱  Timer", "📁  Projects", "🎯  Goals", "🔗  GitHub"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CodingPage")

        # construct services for this page
        self._db = DatabaseConnection()
        self._repo = CodingRepository(db_conn=self._db)
        self._project_service = ProjectService(repo=self._repo)
        self._goals_service = GoalsService(repo=self._repo)
        self._timer_service = CodingTimerService(repo=self._repo)
        self._github_service = GitHubService(repo=self._repo)

        self._services = {
            "repo": self._repo,
            "project_service": self._project_service,
            "goals_service": self._goals_service,
            "timer_service": self._timer_service,
            "github_service": self._github_service,
        }

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Coding — Timer, Projects, Goals, GitHub")
        header.setProperty("class", "page-header")
        layout.addWidget(header)

        subtitle = QLabel("Integrated coding timer, project tracker, goals, and GitHub sync")
        subtitle.setProperty("class", "page-subtitle")
        layout.addWidget(subtitle)

        # Pill tabs (simple)
        self._buttons = QButtonGroup(self)
        for i, label in enumerate(self._TABS):
            btn = QPushButton(label)
            btn.setProperty("class", "pill-tab")
            btn.setCheckable(True)
            if i == 0:
                btn.setChecked(True)
            self._buttons.addButton(btn, i)
            layout.addWidget(btn)

        # Stacked
        self._stack = QStackedWidget()
        self._timer_widget = CodingTimerWidget(self._services)
        self._projects_widget = ProjectsWidget(self._services)
        self._goals_widget = CodingGoalsWidget(self._services)
        self._github_widget = GitHubWidget(self._services)
        self._stack.addWidget(self._timer_widget)
        self._stack.addWidget(self._projects_widget)
        self._stack.addWidget(self._goals_widget)
        self._stack.addWidget(self._github_widget)
        layout.addWidget(self._stack)

        # connect using idClicked which provides the integer index
        self._buttons.idClicked.connect(self._stack.setCurrentIndex)
        self._stack.currentChanged.connect(self._on_tab_changed)
        self._projects_widget.project_added.connect(self._on_project_added)

    def _on_tab_changed(self, index: int):
        self._timer_widget.refresh_projects()
        self._projects_widget.refresh()
        self._goals_widget.refresh()
        self._github_widget.refresh()

    def _on_project_added(self):
        self._timer_widget.refresh_projects()
        self._github_widget.refresh()
