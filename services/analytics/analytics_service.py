from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal

from database.repositories.analytics_repository import AnalyticsRepository
from database.models import (
    AnalyticsOverview,
    FocusTimeStats,
    ReportSummary,
    DomainSummary,
)


class AnalyticsService(QObject):
    """Business logic service for Aster Analytics & Reports."""

    data_refreshed = Signal()

    def __init__(self, repo: Optional[AnalyticsRepository] = None, parent=None):
        super().__init__(parent)
        self.repo = repo or AnalyticsRepository()

    def resolve_date_range(self, period: str) -> tuple[str, str]:
        """Resolve period keyword ('this_week', 'last_week', 'this_month', 'last_30_days') to (start_date, end_date)."""
        now = datetime.now()

        if period == "last_week":
            prev_week_dt = now - timedelta(days=7)
            return AnalyticsRepository.get_week_bounds(prev_week_dt)
        elif period == "this_month":
            return AnalyticsRepository.get_month_bounds(now)
        elif period == "last_30_days":
            start_dt = now - timedelta(days=29)
            return start_dt.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")
        else:  # 'this_week' default (Monday to Sunday)
            return AnalyticsRepository.get_week_bounds(now)

    def get_overview(self, period: str = "this_week") -> AnalyticsOverview:
        """Fetch AnalyticsOverview for requested period."""
        start_date, end_date = self.resolve_date_range(period)
        return self.repo.get_analytics_overview(start_date, end_date)

    def get_daily_focus(self, period: str = "this_week") -> List[FocusTimeStats]:
        """Fetch daily focus breakdown for requested period."""
        start_date, end_date = self.resolve_date_range(period)
        return self.repo.get_daily_focus_breakdown(start_date, end_date)

    def get_week_over_week_comparison(self) -> Dict[str, Any]:
        """Compare current week (Mon-Sun) against previous week (Mon-Sun)."""
        this_start, this_end = self.resolve_date_range("this_week")
        last_start, last_end = self.resolve_date_range("last_week")

        curr_sum = self.repo.get_domain_summary(this_start, this_end)
        prev_sum = self.repo.get_domain_summary(last_start, last_end)

        def calc_pct_change(curr: float, prev: float) -> float:
            if prev == 0:
                return 100.0 if curr > 0 else 0.0
            return round(((curr - prev) / prev) * 100.0, 1)

        focus_change = calc_pct_change(curr_sum.total_focus_minutes, prev_sum.total_focus_minutes)
        tasks_change = calc_pct_change(curr_sum.tasks_completed, prev_sum.tasks_completed)
        workouts_change = calc_pct_change(curr_sum.workouts_completed, prev_sum.workouts_completed)

        return {
            "focus_change_pct": focus_change,
            "focus_trend": "up" if focus_change > 0 else ("down" if focus_change < 0 else "steady"),
            "tasks_change_pct": tasks_change,
            "tasks_trend": "up" if tasks_change > 0 else ("down" if tasks_change < 0 else "steady"),
            "workouts_change_pct": workouts_change,
            "workouts_trend": "up" if workouts_change > 0 else ("down" if workouts_change < 0 else "steady"),
            "curr_focus_hours": round(curr_sum.total_focus_minutes / 60.0, 1),
            "prev_focus_hours": round(prev_sum.total_focus_minutes / 60.0, 1),
        }

    def generate_report(self, report_type: str = "Weekly") -> ReportSummary:
        """Generate structured human-readable report."""
        period = "this_week" if report_type == "Weekly" else "this_month"
        start_date, end_date = self.resolve_date_range(period)
        overview = self.repo.get_analytics_overview(start_date, end_date)
        summary = overview.summary or DomainSummary()

        label = f"Week of {start_date} to {end_date}" if report_type == "Weekly" else f"Month of {start_date[:7]}"

        highlights = []
        if summary.total_focus_minutes > 0:
            hrs = round(summary.total_focus_minutes / 60.0, 1)
            highlights.append(f"⏱️ Logged {hrs} hours of focus time across Pomodoro & Coding sessions.")

        if summary.tasks_completed > 0:
            highlights.append(f"✅ Completed {summary.tasks_completed} tasks with an overall completion rate of {overview.task_completion_rate}%.")

        if summary.active_streaks > 0:
            highlights.append(f"🔥 Maintained {summary.active_streaks} total habit streak days.")

        if summary.workouts_completed > 0:
            highlights.append(f"💪 Completed {summary.workouts_completed} workouts logging {summary.workout_minutes} mins and {summary.calories_burned} kcal.")

        if not highlights:
            highlights.append("🌱 No activity recorded yet for this period. Start completing tasks or focus sessions!")

        prod_text = (
            f"Tasks Completed: {summary.tasks_completed} / {summary.tasks_total}\n"
            f"Habits & Goals Active: {summary.goals_completed} / {summary.goals_total}\n"
            f"Active Habit Streaks: {summary.active_streaks} days\n"
            f"Pomodoro Focus Time: {round((summary.total_focus_minutes - summary.coding_minutes) / 60.0, 1)} hrs"
        )

        college_text = (
            f"Classes Attended: {summary.classes_attended} / {summary.classes_total} ({overview.attendance_rate}%)\n"
            f"Assignments Completed: {summary.assignments_completed} / {summary.assignments_total}"
        )

        coding_text = (
            f"Coding Focus Time: {round(summary.coding_minutes / 60.0, 1)} hrs\n"
            f"Active Projects Tracked: {summary.active_projects}"
        )

        fitness_text = (
            f"Workouts Completed: {summary.workouts_completed}\n"
            f"Total Workout Time: {summary.workout_minutes} mins\n"
            f"Estimated Calories Burned: {summary.calories_burned} kcal\n"
            f"Latest Weight Record: {f'{summary.latest_weight_kg} kg' if summary.latest_weight_kg else 'No entry'}"
        )

        gen_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return ReportSummary(
            report_type=report_type,
            period_label=label,
            start_date=start_date,
            end_date=end_date,
            summary_text=f"Aster {report_type} Performance Summary ({start_date} to {end_date})",
            highlights=highlights,
            productivity_notes=prod_text,
            college_notes=college_text,
            coding_notes=coding_text,
            fitness_notes=fitness_text,
            generated_at=gen_at,
        )
