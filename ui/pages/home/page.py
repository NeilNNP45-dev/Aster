from datetime import datetime
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy,
)

from services.home.home_service import HomeService, HomeSummary


class HomeMetricCard(QFrame):
    """Card displaying a single summary metric."""

    def __init__(self, title: str, value: str, icon: str = "📊", parent=None):
        super().__init__(parent)
        self.setProperty("class", "metric-card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._build(title, value, icon)

    def _build(self, title: str, value: str, icon: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 18px;")
        top_row.addWidget(icon_lbl)
        top_row.addStretch()
        layout.addLayout(top_row)

        self.num_lbl = QLabel(value)
        self.num_lbl.setProperty("class", "metric-number")

        label_lbl = QLabel(title)
        label_lbl.setProperty("class", "metric-label")

        layout.addWidget(self.num_lbl)
        layout.addWidget(label_lbl)

    def update_value(self, value: str):
        self.num_lbl.setText(value)


class HomeHabitItem(QFrame):
    """Lightweight preview row for a daily habit with check toggle."""

    def __init__(self, goal_id: int, title: str, is_completed: bool, streak: int, on_toggle: Callable[[int], None], parent=None):
        super().__init__(parent)
        self.setProperty("class", "task-item")
        self._goal_id = goal_id
        self._on_toggle = on_toggle

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        check_btn = QPushButton("✓" if is_completed else "")
        check_btn.setFixedSize(22, 22)
        check_btn.setProperty("class", "task-check-btn" + (" completed" if is_completed else ""))
        check_btn.clicked.connect(lambda: self._on_toggle(self._goal_id))

        title_lbl = QLabel(title)
        title_lbl.setProperty("class", "task-title")
        if is_completed:
            title_lbl.setStyleSheet("text-decoration: line-through; color: #6B7280;")

        streak_lbl = QLabel(f"🔥 {streak}")
        streak_lbl.setProperty("class", "task-due")

        layout.addWidget(check_btn)
        layout.addWidget(title_lbl, 1)
        layout.addWidget(streak_lbl)


class HomePage(QWidget):
    """Dynamic, workflow-centric Home Dashboard Page."""

    def __init__(self, on_navigate: Optional[Callable[[int], None]] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")
        self._on_navigate = on_navigate
        self._home_service = HomeService()

        self._init_ui()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def _get_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning ☀️"
        elif hour < 18:
            return "Good Afternoon 👋"
        else:
            return "Good Evening 🌙"

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 28, 28, 28)
        root_layout.setSpacing(20)

        # ── Header ───────────────────────────────────────────────────────────
        self._header_title = QLabel(self._get_greeting())
        self._header_title.setProperty("class", "page-header")

        now_str = datetime.now().strftime("%A, %B %d, %Y")
        self._header_subtitle = QLabel(f"{now_str} — Your unified workspace summary")
        self._header_subtitle.setProperty("class", "page-subtitle")

        root_layout.addWidget(self._header_title)
        root_layout.addWidget(self._header_subtitle)

        # ── Live Metrics Grid Row ────────────────────────────────────────────
        metrics_row = QHBoxLayout()
        metrics_row.setSpacing(14)

        self._card_tasks = HomeMetricCard("Pending Tasks", "0", icon="✅")
        self._card_habits = HomeMetricCard("Habits Today", "0 / 0", icon="🎯")
        self._card_focus = HomeMetricCard("Today's Focus", "0 mins", icon="⏱️")
        self._card_projects = HomeMetricCard("Active Projects", "0", icon="💻")

        metrics_row.addWidget(self._card_tasks)
        metrics_row.addWidget(self._card_habits)
        metrics_row.addWidget(self._card_focus)
        metrics_row.addWidget(self._card_projects)

        root_layout.addLayout(metrics_row)

        # ── Main Two-Column Body ─────────────────────────────────────────────
        body_layout = QHBoxLayout()
        body_layout.setSpacing(20)

        # --- Left Column: Workflows & Habits ---
        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        # Quick Actions Card
        actions_card = QFrame()
        actions_card.setProperty("class", "card")
        actions_layout = QVBoxLayout(actions_card)
        actions_layout.setSpacing(12)

        actions_title = QLabel("Quick Actions")
        actions_title.setProperty("class", "card-title")
        actions_layout.addWidget(actions_title)

        shortcuts_grid = QGridLayout()
        shortcuts_grid.setSpacing(10)

        btn_add_task = QPushButton("✅  Add New Task")
        btn_add_task.setProperty("class", "action-shortcut-btn")
        btn_add_task.clicked.connect(lambda: self._trigger_navigate(1))

        btn_focus = QPushButton("🍅  Start Focus Timer")
        btn_focus.setProperty("class", "action-shortcut-btn")
        btn_focus.clicked.connect(lambda: self._trigger_navigate(1))

        btn_coding = QPushButton("💻  Log Coding Time")
        btn_coding.setProperty("class", "action-shortcut-btn")
        btn_coding.clicked.connect(lambda: self._trigger_navigate(3))

        btn_workout = QPushButton("💪  Log Workout")
        btn_workout.setProperty("class", "action-shortcut-btn")
        btn_workout.clicked.connect(lambda: self._trigger_navigate(4))

        shortcuts_grid.addWidget(btn_add_task, 0, 0)
        shortcuts_grid.addWidget(btn_focus, 0, 1)
        shortcuts_grid.addWidget(btn_coding, 1, 0)
        shortcuts_grid.addWidget(btn_workout, 1, 1)
        actions_layout.addLayout(shortcuts_grid)


        left_col.addWidget(actions_card)

        # Habits Preview Card
        habits_card = QFrame()
        habits_card.setProperty("class", "card")
        habits_layout = QVBoxLayout(habits_card)
        habits_layout.setSpacing(10)

        habits_title = QLabel("Today's Habits Checklist")
        habits_title.setProperty("class", "card-title")
        habits_layout.addWidget(habits_title)

        self._habits_list_container = QWidget()
        self._habits_list_layout = QVBoxLayout(self._habits_list_container)
        self._habits_list_layout.setContentsMargins(0, 0, 0, 0)
        self._habits_list_layout.setSpacing(6)

        habits_layout.addWidget(self._habits_list_container)
        left_col.addWidget(habits_card, 1)

        body_layout.addLayout(left_col, 3)

        # --- Right Column: Status & Recent Updates ---
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        # Recent Updates Card
        updates_card = QFrame()
        updates_card.setProperty("class", "card")
        updates_layout = QVBoxLayout(updates_card)
        updates_layout.setSpacing(10)

        updates_title = QLabel("Recent Updates")
        updates_title.setProperty("class", "card-title")

        badge = QLabel("Version 0.6.0 — Analytics & Suite")
        badge.setProperty("class", "status-badge")

        updates_desc = QLabel(
            "• Analytics & Insights Suite active across all domains\n"
            "• Automatic daily habit resets & streak tracking\n"
            "• Local-first SQLite database architecture\n"
            "• Hardened GitHub integration & input masking"
        )
        updates_desc.setProperty("class", "card-description")
        updates_desc.setWordWrap(True)

        updates_layout.addWidget(updates_title)
        updates_layout.addWidget(badge)
        updates_layout.addWidget(updates_desc)

        right_col.addWidget(updates_card)
        right_col.addStretch()

        body_layout.addLayout(right_col, 2)

        root_layout.addLayout(body_layout, 1)

    def refresh(self):
        """Fetch latest home summary data from HomeService and update UI."""
        self._header_title.setText(self._get_greeting())
        summary: HomeSummary = self._home_service.get_home_summary()

        self._card_tasks.update_value(str(summary.active_tasks_count))
        self._card_habits.update_value(f"{summary.completed_habits_count} / {summary.total_habits_count}")
        self._card_focus.update_value(f"{summary.today_focus_minutes} mins")
        self._card_projects.update_value(str(summary.active_projects_count))

        # Refresh habits preview
        while self._habits_list_layout.count() > 0:
            child = self._habits_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not summary.today_habits:
            empty_lbl = QLabel("No daily habits created yet. Go to Productivity to add one.")
            empty_lbl.setProperty("class", "card-description")
            self._habits_list_layout.addWidget(empty_lbl)
        else:
            for habit in summary.today_habits:
                item = HomeHabitItem(
                    goal_id=habit.id,
                    title=habit.title,
                    is_completed=habit.is_completed,
                    streak=habit.streak_count,
                    on_toggle=self._on_habit_toggle,
                )
                self._habits_list_layout.addWidget(item)

    def _on_habit_toggle(self, goal_id: int):
        self._home_service.toggle_habit_completion(goal_id)
        self.refresh()

    def _trigger_navigate(self, page_index: int):
        if self._on_navigate:
            self._on_navigate(page_index)

    def closeEvent(self, event):
        if hasattr(self, "_home_service") and self._home_service:
            self._home_service.close()
        super().closeEvent(event)
