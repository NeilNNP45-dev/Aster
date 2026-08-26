from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from database.connection import DatabaseConnection
from database.models import (
    DomainSummary,
    FocusTimeStats,
    AnalyticsOverview,
)


class AnalyticsRepository:
    """Repository handling read-only queries and aggregation for Analytics across all domains."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self.db = db_conn or DatabaseConnection()

    def close(self):
        if hasattr(self, "db") and self.db is not None:
            self.db.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


    @staticmethod
    def get_week_bounds(dt: Optional[datetime] = None) -> Tuple[str, str]:
        """Return ISO week bounds (Monday to Sunday) for the given date in YYYY-MM-DD format."""
        if dt is None:
            dt = datetime.now()
        start_of_week = dt - timedelta(days=dt.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)    # Sunday
        return start_of_week.strftime("%Y-%m-%d"), end_of_week.strftime("%Y-%m-%d")

    @staticmethod
    def get_month_bounds(dt: Optional[datetime] = None) -> Tuple[str, str]:
        """Return month bounds (1st to last day of month) for the given date in YYYY-MM-DD format."""
        if dt is None:
            dt = datetime.now()
        first_day = dt.replace(day=1)
        if dt.month == 12:
            next_month = dt.replace(year=dt.year + 1, month=1, day=1)
        else:
            next_month = dt.replace(month=dt.month + 1, day=1)
        last_day = next_month - timedelta(days=1)
        return first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")

    def get_domain_summary(self, start_date: str, end_date: str) -> DomainSummary:
        """Aggregate summary metrics across Productivity, College, Coding, and Fitness."""
        start_ts = f"{start_date} 00:00:00"
        end_ts = f"{end_date} 23:59:59"

        summary = DomainSummary()

        with self.db.get_cursor() as cursor:
            # --- 1. Productivity: Tasks ---
            cursor.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) AS completed FROM tasks WHERE created_at <= ?",
                (end_ts,),
            )
            row = cursor.fetchone()
            if row:
                summary.tasks_total = row["total"] or 0
                summary.tasks_completed = row["completed"] or 0

            # --- 2. Productivity: Daily Goals & Streaks ---
            cursor.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) AS completed, SUM(streak_count) AS streaks FROM daily_goals"
            )
            row = cursor.fetchone()
            if row:
                summary.goals_total = row["total"] or 0
                summary.goals_completed = row["completed"] or 0
                summary.active_streaks = row["streaks"] or 0

            # --- 3. Productivity: Pomodoro Sessions ---
            cursor.execute(
                "SELECT SUM(duration_minutes) AS total_min FROM pomodoro_sessions WHERE session_type = 'Work' AND completed_at >= ? AND completed_at <= ?",
                (start_ts, end_ts),
            )
            row = cursor.fetchone()
            pomo_min = (row["total_min"] or 0) if row else 0

            # --- 4. College: Course Attendance & Assignments ---
            cursor.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN status IN ('Present', 'Late') THEN 1 ELSE 0 END) AS attended FROM attendance_logs WHERE attendance_date >= ? AND attendance_date <= ?",
                (start_date, end_date),
            )
            row = cursor.fetchone()
            if row:
                summary.classes_total = row["total"] or 0
                summary.classes_attended = row["attended"] or 0

            cursor.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed FROM assignments WHERE created_at <= ?",
                (end_ts,),
            )
            row = cursor.fetchone()
            if row:
                summary.assignments_total = row["total"] or 0
                summary.assignments_completed = row["completed"] or 0

            # --- 5. Coding: Timer Sessions & Active Projects ---
            cursor.execute(
                "SELECT SUM(duration_minutes) AS total_min FROM coding_sessions WHERE session_type = 'Coding' AND start_at >= ? AND start_at <= ?",
                (start_ts, end_ts),
            )
            row = cursor.fetchone()
            coding_min = (row["total_min"] or 0) if row else 0
            summary.coding_minutes = coding_min

            cursor.execute("SELECT COUNT(*) AS active_count FROM coding_projects WHERE is_active = 1")
            row = cursor.fetchone()
            summary.active_projects = (row["active_count"] or 0) if row else 0

            # Total focus time combines Pomodoro focus + Coding timer focus
            summary.total_focus_minutes = pomo_min + coding_min

            # --- 6. Fitness: Workouts & Weight ---
            cursor.execute(
                "SELECT COUNT(*) AS total_workouts, SUM(duration_minutes) AS total_dur, SUM(calories) AS total_cal FROM fitness_workouts WHERE performed_at >= ? AND performed_at <= ?",
                (start_ts, end_ts),
            )
            row = cursor.fetchone()
            if row:
                summary.workouts_completed = row["total_workouts"] or 0
                summary.workout_minutes = row["total_dur"] or 0
                summary.calories_burned = row["total_cal"] or 0

            cursor.execute("SELECT weight_kg FROM fitness_weights ORDER BY recorded_at DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                summary.latest_weight_kg = row["weight_kg"]

        return summary

    def get_daily_focus_breakdown(self, start_date: str, end_date: str) -> List[FocusTimeStats]:
        """Return daily focus minutes (Pomodoro + Coding) for each day in range [start_date, end_date]."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        daily_map = {}
        curr = start_dt
        while curr <= end_dt:
            d_str = curr.strftime("%Y-%m-%d")
            daily_map[d_str] = FocusTimeStats(date_str=d_str)
            curr += timedelta(days=1)

        start_ts = f"{start_date} 00:00:00"
        end_ts = f"{end_date} 23:59:59"

        with self.db.get_cursor() as cursor:
            # Pomodoro minutes by day
            cursor.execute(
                """
                SELECT substr(completed_at, 1, 10) AS log_date, SUM(duration_minutes) AS mins
                FROM pomodoro_sessions
                WHERE session_type = 'Work' AND completed_at >= ? AND completed_at <= ?
                GROUP BY log_date
                """,
                (start_ts, end_ts),
            )
            for row in cursor.fetchall():
                d = row["log_date"]
                if d in daily_map:
                    daily_map[d].pomodoro_minutes = row["mins"] or 0

            # Coding minutes by day
            cursor.execute(
                """
                SELECT substr(start_at, 1, 10) AS log_date, SUM(duration_minutes) AS mins
                FROM coding_sessions
                WHERE session_type = 'Coding' AND start_at >= ? AND start_at <= ?
                GROUP BY log_date
                """,
                (start_ts, end_ts),
            )
            for row in cursor.fetchall():
                d = row["log_date"]
                if d in daily_map:
                    daily_map[d].coding_minutes = row["mins"] or 0

        result = []
        for d_str in sorted(daily_map.keys()):
            stat = daily_map[d_str]
            stat.total_minutes = stat.pomodoro_minutes + stat.coding_minutes
            result.append(stat)

        return result

    def get_analytics_overview(self, start_date: str, end_date: str) -> AnalyticsOverview:
        """Construct full AnalyticsOverview for a given date range."""
        summary = self.get_domain_summary(start_date, end_date)

        focus_hours = round(summary.total_focus_minutes / 60.0, 1)

        task_rate = 0.0
        if summary.tasks_total > 0:
            task_rate = round((summary.tasks_completed / summary.tasks_total) * 100.0, 1)

        attendance_rate = 0.0
        if summary.classes_total > 0:
            attendance_rate = round((summary.classes_attended / summary.classes_total) * 100.0, 1)

        return AnalyticsOverview(
            start_date=start_date,
            end_date=end_date,
            total_focus_hours=focus_hours,
            task_completion_rate=task_rate,
            attendance_rate=attendance_rate,
            summary=summary,
        )
