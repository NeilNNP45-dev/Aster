from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QProgressBar, QSizePolicy,
)

from database.models import DailyGoal
from database.repositories.productivity_repository import ProductivityRepository


class GoalItemWidget(QFrame):
    """A single daily goal row with a check toggle and delete."""

    def __init__(self, goal: DailyGoal, on_toggle, on_delete, parent=None):
        super().__init__(parent)
        self.goal = goal
        self.setProperty("class", "task-item")
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        check_btn = QPushButton("✓" if self.goal.is_completed else "")
        check_btn.setFixedSize(24, 24)
        check_btn.setProperty("class", "task-check-btn" + (" completed" if self.goal.is_completed else ""))
        check_btn.clicked.connect(lambda: self._on_toggle(self.goal.id))

        title_lbl = QLabel(self.goal.title)
        title_lbl.setProperty("class", "task-title")
        if self.goal.is_completed:
            title_lbl.setStyleSheet("text-decoration: line-through; color: #6B7280;")
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        streak_lbl = QLabel(f"🔥 {self.goal.streak_count}")
        streak_lbl.setProperty("class", "task-due")

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(22, 22)
        del_btn.setProperty("class", "task-delete-btn")
        del_btn.clicked.connect(lambda: self._on_delete(self.goal.id))

        layout.addWidget(check_btn)
        layout.addWidget(title_lbl)
        layout.addWidget(streak_lbl)
        layout.addWidget(del_btn)


class GoalsWidget(QWidget):
    """Daily Goals & Habits sub-view."""

    def __init__(self, repo: ProductivityRepository, parent=None):
        super().__init__(parent)
        self._repo = repo
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Header row
        header_row = QHBoxLayout()
        self._progress_lbl = QLabel("0 / 0 completed today")
        self._progress_lbl.setProperty("class", "card-description")
        header_row.addWidget(self._progress_lbl)
        header_row.addStretch()
        self.add_btn = QPushButton("＋  Add Goal")
        self.add_btn.setProperty("class", "primary-btn")
        header_row.addWidget(self.add_btn)
        layout.addLayout(header_row)

        # Progress bar
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(8)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setProperty("class", "habit-progress")
        layout.addWidget(self._progress_bar)

        # Scrollable goals list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._goals_container = QWidget()
        self._goals_layout = QVBoxLayout(self._goals_container)
        self._goals_layout.setContentsMargins(0, 0, 0, 0)
        self._goals_layout.setSpacing(6)
        self._goals_layout.addStretch()
        scroll.setWidget(self._goals_container)
        layout.addWidget(scroll, 1)

    def refresh(self):
        while self._goals_layout.count() > 1:
            item = self._goals_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        goals = self._repo.get_daily_goals()
        completed = sum(1 for g in goals if g.is_completed)
        total = len(goals)
        self._progress_lbl.setText(f"{completed} / {total} completed today")
        self._progress_bar.setMaximum(max(total, 1))
        self._progress_bar.setValue(completed)

        if not goals:
            empty = QLabel("No habits yet. Click '＋ Add Goal' to create one.")
            empty.setProperty("class", "card-description")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._goals_layout.insertWidget(0, empty)
            return

        for goal in goals:
            widget = GoalItemWidget(goal, self._on_toggle, self._on_delete)
            self._goals_layout.insertWidget(self._goals_layout.count() - 1, widget)

    def _on_toggle(self, goal_id: int):
        self._repo.toggle_goal_completion(goal_id)
        self.refresh()

    def _on_delete(self, goal_id: int):
        self._repo.delete_daily_goal(goal_id)
        self.refresh()
