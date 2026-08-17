from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QComboBox,
)
from services.analytics.analytics_service import AnalyticsService


class OverviewWidget(QWidget):
    """Overview sub-view displaying multi-domain summary metrics."""

    PERIOD_MAP = {
        "This Week (Mon-Sun)": "this_week",
        "Last Week": "last_week",
        "This Month": "this_month",
        "Last 30 Days": "last_30_days",
    }

    def __init__(self, service: AnalyticsService, parent=None):
        super().__init__(parent)
        self.service = service
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Top Controls Row
        ctrl_row = QHBoxLayout()
        filter_label = QLabel("Time Period:")
        filter_label.setProperty("class", "card-description")

        self.period_combo = QComboBox()
        self.period_combo.setProperty("class", "form-combo")
        self.period_combo.addItems(list(self.PERIOD_MAP.keys()))
        self.period_combo.currentTextChanged.connect(self.refresh)

        ctrl_row.addWidget(filter_label)
        ctrl_row.addWidget(self.period_combo)
        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Stat Cards Grid (2x2)
        grid = QGridLayout()
        grid.setSpacing(14)

        # Card 1: Focus Time
        self.focus_card, self.focus_num, self.focus_label, self.focus_trend = self._create_stat_card("⏱️ Total Focus Time")
        # Card 2: Tasks & Productivity
        self.tasks_card, self.tasks_num, self.tasks_label, self.tasks_trend = self._create_stat_card("✅ Task Completion")
        # Card 3: College Attendance
        self.college_card, self.college_num, self.college_label, self.college_trend = self._create_stat_card("🎓 Attendance Rate")
        # Card 4: Fitness & Health
        self.fitness_card, self.fitness_num, self.fitness_label, self.fitness_trend = self._create_stat_card("💪 Fitness Workouts")

        grid.addWidget(self.focus_card, 0, 0)
        grid.addWidget(self.tasks_card, 0, 1)
        grid.addWidget(self.college_card, 1, 0)
        grid.addWidget(self.fitness_card, 1, 1)

        layout.addLayout(grid)

        # Domain Breakdown Cards Row
        breakdown_row = QHBoxLayout()
        breakdown_row.setSpacing(14)

        # Left Detail: Productivity & Habits
        self.prod_detail_card = QFrame()
        self.prod_detail_card.setProperty("class", "card")
        prod_l = QVBoxLayout(self.prod_detail_card)
        prod_t = QLabel("Productivity & Habit Streaks")
        prod_t.setProperty("class", "card-title")
        self.prod_desc = QLabel("Loading...")
        self.prod_desc.setProperty("class", "card-description")
        prod_l.addWidget(prod_t)
        prod_l.addWidget(self.prod_desc)

        # Right Detail: Coding & Projects
        self.coding_detail_card = QFrame()
        self.coding_detail_card.setProperty("class", "card")
        coding_l = QVBoxLayout(self.coding_detail_card)
        coding_t = QLabel("Coding & Software Projects")
        coding_t.setProperty("class", "card-title")
        self.coding_desc = QLabel("Loading...")
        self.coding_desc.setProperty("class", "card-description")
        coding_l.addWidget(coding_t)
        coding_l.addWidget(self.coding_desc)

        breakdown_row.addWidget(self.prod_detail_card, 1)
        breakdown_row.addWidget(self.coding_detail_card, 1)

        layout.addLayout(breakdown_row)
        layout.addStretch()

        self.refresh()

    def _create_stat_card(self, title_text: str):
        card = QFrame()
        card.setProperty("class", "stat-card")
        l = QVBoxLayout(card)
        l.setContentsMargins(16, 16, 16, 16)
        l.setSpacing(6)

        t_lbl = QLabel(title_text)
        t_lbl.setProperty("class", "stat-label")

        val_lbl = QLabel("0")
        val_lbl.setProperty("class", "stat-number")

        sub_lbl = QLabel("")
        sub_lbl.setProperty("class", "card-description")

        trend_lbl = QLabel("")
        trend_lbl.setProperty("class", "stat-badge-up")
        trend_lbl.hide()

        top_h = QHBoxLayout()
        top_h.addWidget(t_lbl)
        top_h.addStretch()
        top_h.addWidget(trend_lbl)

        l.addLayout(top_h)
        l.addWidget(val_lbl)
        l.addWidget(sub_lbl)

        return card, val_lbl, sub_lbl, trend_lbl

    def refresh(self):
        period_key = self.PERIOD_MAP.get(self.period_combo.currentText(), "this_week")
        overview = self.service.get_overview(period_key)
        summary = overview.summary

        if not summary:
            return

        # Update Card 1: Focus Time
        self.focus_num.setText(f"{overview.total_focus_hours} hrs")
        self.focus_label.setText(
            f"Pomodoro: {round((summary.total_focus_minutes - summary.coding_minutes) / 60.0, 1)} hrs | Coding: {round(summary.coding_minutes / 60.0, 1)} hrs"
        )

        # Update Card 2: Tasks
        self.tasks_num.setText(f"{overview.task_completion_rate}%")
        self.tasks_label.setText(f"{summary.tasks_completed} of {summary.tasks_total} tasks completed")

        # Update Card 3: Attendance
        self.college_num.setText(f"{overview.attendance_rate}%")
        self.college_label.setText(f"{summary.classes_attended} of {summary.classes_total} classes attended")

        # Update Card 4: Fitness
        self.fitness_num.setText(f"{summary.workouts_completed} workouts")
        self.fitness_label.setText(f"{summary.workout_minutes} mins total | {summary.calories_burned} kcal burned")

        # Update Week-over-Week trend badge if viewing this_week
        if period_key == "this_week":
            comp = self.service.get_week_over_week_comparison()
            f_change = comp["focus_change_pct"]
            if f_change > 0:
                self.focus_trend.setText(f"+{f_change}% vs last wk")
                self.focus_trend.setProperty("class", "stat-badge-up")
                self.focus_trend.show()
            elif f_change < 0:
                self.focus_trend.setText(f"{f_change}% vs last wk")
                self.focus_trend.setProperty("class", "stat-badge-down")
                self.focus_trend.show()
            else:
                self.focus_trend.hide()
        else:
            self.focus_trend.hide()

        # Update Detail Cards
        self.prod_desc.setText(
            f"• Daily Habits Active: {summary.goals_completed} / {summary.goals_total}\n"
            f"• Total Active Habit Streaks: {summary.active_streaks} days\n"
            f"• Task Completion Rate: {overview.task_completion_rate}%"
        )

        self.coding_desc.setText(
            f"• Coding Focus Time: {round(summary.coding_minutes / 60.0, 1)} hours\n"
            f"• Active Software Projects: {summary.active_projects}\n"
            f"• Integrated GitHub Repositories"
        )
