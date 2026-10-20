from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QButtonGroup,
)

from database.connection import DatabaseConnection
from database.repositories.productivity_repository import ProductivityRepository
from ui.pages.productivity.tasks_widget import TasksWidget
from ui.pages.productivity.goals_widget import GoalsWidget
from ui.pages.productivity.notes_widget import NotesWidget
from ui.pages.productivity.pomodoro_widget import PomodoroWidget
from ui.dialogs.task_dialog import TaskDialog
from ui.dialogs.goal_dialog import GoalDialog


class ProductivityPage(QWidget):
    """
    Productivity page featuring four sub-views:
      0 – Tasks (To-Do list)
      1 – Daily Goals & Habits
      2 – Notes
      3 – Pomodoro Focus Timer
    """

    _TABS = ["✅  Tasks", "🎯  Daily Goals", "📝  Notes", "🍅  Pomodoro"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProductivityPage")

        # Shared database + repository
        self._db = DatabaseConnection()
        self._repo = ProductivityRepository(db_conn=self._db)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # ── Page header ──────────────────────────────────────────────────────
        title = QLabel("Productivity")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Manage one-time tasks, repeatable daily goals, notes, and focus sessions")
        subtitle.setProperty("class", "page-subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ── Pill sub-tab navigation ──────────────────────────────────────────
        tab_row = QHBoxLayout()
        tab_row.setSpacing(6)
        self._tab_group = QButtonGroup(self)
        self._tab_group.setExclusive(True)

        for i, label in enumerate(self._TABS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "pill-tab")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._tab_group.addButton(btn, i)
            tab_row.addWidget(btn)

        self._tab_group.button(0).setChecked(True)
        tab_row.addStretch()
        layout.addLayout(tab_row)

        # ── Sub-view stacked widget ──────────────────────────────────────────
        self._stack = QStackedWidget()

        self._tasks_view = TasksWidget(self._repo)
        self._goals_view = GoalsWidget(self._repo)
        self._notes_view = NotesWidget(self._repo)
        self._pomodoro_view = PomodoroWidget(self._repo)

        self._stack.addWidget(self._tasks_view)     # 0
        self._stack.addWidget(self._goals_view)     # 1
        self._stack.addWidget(self._notes_view)     # 2
        self._stack.addWidget(self._pomodoro_view)  # 3

        # Connect tab buttons to stack switching
        self._tab_group.idClicked.connect(self._stack.setCurrentIndex)

        # Connect "Add" buttons to their dialogs
        self._tasks_view.add_btn.clicked.connect(lambda: self._open_task_dialog())
        self._goals_view.add_btn.clicked.connect(lambda: self._open_goal_dialog())
        self._tasks_view.edit_requested.connect(self._open_task_dialog)
        self._goals_view.edit_requested.connect(self._open_goal_dialog)

        layout.addWidget(self._stack, 1)

    # ── Dialog handlers ──────────────────────────────────────────────────────

    def _open_task_dialog(self, task=None):
        dialog = TaskDialog(self, task=task)
        if dialog.exec() == TaskDialog.DialogCode.Accepted:
            updated_task = dialog.get_task()
            if updated_task:
                if task is None:
                    self._repo.add_task(updated_task)
                else:
                    self._repo.update_task(updated_task)
                self._tasks_view.refresh()

    def _open_goal_dialog(self, goal=None):
        dialog = GoalDialog(self, goal=goal)
        if dialog.exec() == GoalDialog.DialogCode.Accepted:
            updated_goal = dialog.get_goal()
            if updated_goal:
                if goal is None:
                    self._repo.add_daily_goal(updated_goal)
                else:
                    self._repo.update_daily_goal(updated_goal)
                self._goals_view.refresh()
