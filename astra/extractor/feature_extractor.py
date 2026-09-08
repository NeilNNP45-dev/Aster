"""Feature Extraction Engine for Astra ML v1.

Extracts privacy-first, anti-leakage daily feature vectors and targets
from Aster's local SQLite database into CSV/JSON dataset files.
"""

import csv
import json
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from database.connection import DatabaseConnection
from astra.config import (
    DEFAULT_CSV_PATH,
    DEFAULT_METADATA_PATH,
    MIN_HISTORY_DAYS,
    TARGET_COLUMN,
    FEATURE_COLUMNS,
    ALL_DATASET_COLUMNS,
)
from astra.extractor.privacy import PrivacyFilter


class FeatureExtractor:
    """Extracts daily time-series feature vectors from Aster SQLite database."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self.db = db_conn or DatabaseConnection()

    def close(self):
        """Close database connection if owned."""
        if hasattr(self, "db") and self.db is not None:
            self.db.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """Safely parse YYYY-MM-DD or YYYY-MM-DD HH:MM:SS string to a date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    def get_database_date_range(self) -> Tuple[Optional[date], Optional[date]]:
        """Find the earliest and latest recorded dates across all domain tables in Aster."""
        queries = [
            "SELECT MIN(substr(completed_at, 1, 10)) AS min_d, MAX(substr(completed_at, 1, 10)) AS max_d FROM pomodoro_sessions",
            "SELECT MIN(substr(start_at, 1, 10)) AS min_d, MAX(substr(start_at, 1, 10)) AS max_d FROM coding_sessions",
            "SELECT MIN(substr(attendance_date, 1, 10)) AS min_d, MAX(substr(attendance_date, 1, 10)) AS max_d FROM attendance_logs",
            "SELECT MIN(substr(created_at, 1, 10)) AS min_d, MAX(substr(created_at, 1, 10)) AS max_d FROM tasks",
            "SELECT MIN(substr(performed_at, 1, 10)) AS min_d, MAX(substr(performed_at, 1, 10)) AS max_d FROM fitness_workouts",
            "SELECT MIN(substr(created_at, 1, 10)) AS min_d, MAX(substr(created_at, 1, 10)) AS max_d FROM assignments",
        ]

        min_dates = []
        max_dates = []

        with self.db.get_cursor() as cursor:
            for q in queries:
                try:
                    cursor.execute(q)
                    row = cursor.fetchone()
                    if row:
                        if row["min_d"]:
                            d_min = self._parse_date(row["min_d"])
                            if d_min:
                                min_dates.append(d_min)
                        if row["max_d"]:
                            d_max = self._parse_date(row["max_d"])
                            if d_max:
                                max_dates.append(d_max)
                except Exception:
                    continue

        if not min_dates or not max_dates:
            return None, None

        return min(min_dates), max(max_dates)

    def extract_daily_grid(self) -> List[Dict[str, Any]]:
        """Construct continuous daily time-series grid with targets and features."""
        min_date, max_date = self.get_database_date_range()
        if not min_date or not max_date:
            return []

        # Load raw events into memory structures for fast grid processing
        with self.db.get_cursor() as cursor:
            # 1. Pomodoro sessions by date
            cursor.execute(
                "SELECT substr(completed_at, 1, 10) AS log_date, SUM(duration_minutes) AS mins "
                "FROM pomodoro_sessions WHERE session_type = 'Work' GROUP BY log_date"
            )
            pomo_by_date = {row["log_date"]: (row["mins"] or 0) for row in cursor.fetchall()}

            # 2. Coding sessions by date
            cursor.execute(
                "SELECT substr(start_at, 1, 10) AS log_date, SUM(duration_minutes) AS mins "
                "FROM coding_sessions WHERE session_type = 'Coding' GROUP BY log_date"
            )
            coding_by_date = {row["log_date"]: (row["mins"] or 0) for row in cursor.fetchall()}

            # 3. Workouts by date
            cursor.execute(
                "SELECT substr(performed_at, 1, 10) AS log_date, SUM(duration_minutes) AS mins, COUNT(*) AS cnt "
                "FROM fitness_workouts GROUP BY log_date"
            )
            workouts_by_date = {}
            for row in cursor.fetchall():
                workouts_by_date[row["log_date"]] = {
                    "mins": row["mins"] or 0,
                    "cnt": row["cnt"] or 0,
                }

            # 4. Attendance logs
            cursor.execute(
                "SELECT substr(attendance_date, 1, 10) AS log_date, status FROM attendance_logs"
            )
            attendance_by_date = {}
            for row in cursor.fetchall():
                d = row["log_date"]
                if d not in attendance_by_date:
                    attendance_by_date[d] = []
                attendance_by_date[d].append(row["status"])

            # 5. Timetable entries by day of week (Monday, Tuesday, etc.)
            cursor.execute(
                "SELECT day_of_week, start_time, end_time FROM timetable_entries WHERE recurring = 1"
            )
            timetable_by_dow = {}
            for row in cursor.fetchall():
                dow = row["day_of_week"]
                if dow not in timetable_by_dow:
                    timetable_by_dow[dow] = 0.0
                try:
                    s_h, s_m = map(int, row["start_time"].split(":"))
                    e_h, e_m = map(int, row["end_time"].split(":"))
                    dur = (e_h * 60 + e_m - (s_h * 60 + s_m)) / 60.0
                    timetable_by_dow[dow] += max(0.0, dur)
                except Exception:
                    pass

            # 6. Assignments (with due dates and creation dates)
            cursor.execute(
                "SELECT substr(created_at, 1, 10) AS created_d, substr(due_date, 1, 10) AS due_d, status FROM assignments"
            )
            assignments_raw = cursor.fetchall()

            # 7. Exams (with scheduled dates and creation dates)
            cursor.execute(
                "SELECT substr(created_at, 1, 10) AS created_d, substr(scheduled_at, 1, 10) AS sched_d FROM exams"
            )
            exams_raw = cursor.fetchall()

            # 8. Tasks (created dates and priorities)
            cursor.execute(
                "SELECT substr(created_at, 1, 10) AS created_d, priority, is_completed FROM tasks"
            )
            tasks_raw = cursor.fetchall()

            # 9. Daily Goals total streaks (snapshot query — kept for CSV export only)
            # NOTE: active_habit_streaks_total is intentionally EXCLUDED from FEATURE_COLUMNS.
            # This query reads the current SUM(streak_count) and would apply the same value to
            # every row in the training grid, contaminating historical rows with future streak state.
            # See config.py FEATURE_COLUMNS docstring for the full rationale.
            cursor.execute("SELECT SUM(streak_count) AS total_streaks FROM daily_goals")
            row = cursor.fetchone()
            current_streaks = (row["total_streaks"] or 0) if row else 0

        # Build daily time series grid
        records = []
        curr = min_date
        dow_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        while curr <= max_date:
            curr_str = curr.strftime("%Y-%m-%d")
            history_days = (curr - min_date).days

            # --- Primary Target (Day t) ---
            target_pomo = pomo_by_date.get(curr_str, 0)
            target_coding = coding_by_date.get(curr_str, 0)
            target_total_focus = target_pomo + target_coding

            # --- Temporal Context (Day t) ---
            dow_idx = curr.weekday()  # 0=Monday, 6=Sunday
            is_weekend = 1 if dow_idx in (5, 6) else 0
            day_of_month = curr.day

            # --- Historical Focus (< t: [curr - N, curr - 1]) ---
            def get_focus_on_day(target_d: date) -> Tuple[int, int]:
                d_s = target_d.strftime("%Y-%m-%d")
                return pomo_by_date.get(d_s, 0), coding_by_date.get(d_s, 0)

            focus_t_1 = sum(get_focus_on_day(curr - timedelta(days=1)))
            focus_t_2 = sum(get_focus_on_day(curr - timedelta(days=2)))

            # Rolling 7-day focus averages (< t)
            focus_7d_total = 0
            pomo_7d_total = 0
            coding_7d_total = 0
            for i in range(1, 8):
                p_m, c_m = get_focus_on_day(curr - timedelta(days=i))
                pomo_7d_total += p_m
                coding_7d_total += c_m
                focus_7d_total += (p_m + c_m)

            focus_7d_avg = round(focus_7d_total / 7.0, 2)
            pomo_7d_avg = round(pomo_7d_total / 7.0, 2)
            coding_7d_avg = round(coding_7d_total / 7.0, 2)

            # Rolling 14-day focus average (< t)
            focus_14d_total = 0
            for i in range(1, 15):
                p_m, c_m = get_focus_on_day(curr - timedelta(days=i))
                focus_14d_total += (p_m + c_m)
            focus_14d_avg = round(focus_14d_total / 14.0, 2)

            # --- Known Schedule Horizon (>= t) ---
            dow_name = dow_names[dow_idx]
            scheduled_class_hours = timetable_by_dow.get(dow_name, 0.0)

            # Pending assignments due in [curr, curr + 2] known as of t-1
            pending_assign_3d = 0
            for a in assignments_raw:
                if a["due_d"]:
                    due_dt = self._parse_date(a["due_d"])
                    created_dt = self._parse_date(a["created_d"])
                    if due_dt and created_dt and created_dt < curr:
                        if curr <= due_dt <= (curr + timedelta(days=2)) and a["status"] != "Completed":
                            pending_assign_3d += 1

            # Exams due in [curr, curr + 6] known as of t-1
            exams_7d = 0
            for e in exams_raw:
                if e["sched_d"]:
                    sched_dt = self._parse_date(e["sched_d"])
                    created_dt = self._parse_date(e["created_d"])
                    if sched_dt and created_dt and created_dt < curr:
                        if curr <= sched_dt <= (curr + timedelta(days=6)):
                            exams_7d += 1

            # --- Academic History (< t: [curr - 14, curr - 1]) ---
            attended_cnt = 0
            total_class_logs = 0
            for i in range(1, 15):
                d_s = (curr - timedelta(days=i)).strftime("%Y-%m-%d")
                logs = attendance_by_date.get(d_s, [])
                for st in logs:
                    total_class_logs += 1
                    if st in ("Present", "Late"):
                        attended_cnt += 1

            attendance_rate_14d = (
                round((attended_cnt / total_class_logs) * 100.0, 1)
                if total_class_logs > 0
                else 100.0
            )

            # --- Productivity History (< t) ---
            tasks_created_7d = 0
            high_pri_pending = 0
            for t_item in tasks_raw:
                c_dt = self._parse_date(t_item["created_d"])
                if c_dt:
                    if (curr - timedelta(days=7)) <= c_dt < curr:
                        tasks_created_7d += 1
                    if c_dt < curr and t_item["priority"] == "High" and t_item["is_completed"] == 0:
                        high_pri_pending += 1

            # --- Fitness History (< t) ---
            workout_mins_7d = 0
            workouts_cnt_7d = 0
            last_workout_date = None

            for i in range(1, 365):
                check_d = curr - timedelta(days=i)
                d_s = check_d.strftime("%Y-%m-%d")
                w_info = workouts_by_date.get(d_s)
                if w_info:
                    if not last_workout_date:
                        last_workout_date = check_d
                    if i <= 7:
                        workout_mins_7d += w_info["mins"]
                        workouts_cnt_7d += w_info["cnt"]

            # Sentinel -1 means "no workout has ever been logged before this day".
            # The training pipeline must impute this (e.g. clip to a max value or use a
            # separate binary indicator feature) before fitting any model.
            days_since_workout = (curr - last_workout_date).days if last_workout_date else -1

            row_data = {
                "date": curr_str,
                "history_days_available": history_days,
                "target_day_of_week": dow_idx,
                "target_is_weekend": is_weekend,
                "target_day_of_month": day_of_month,
                "focus_mins_t_minus_1": float(focus_t_1),
                "focus_mins_t_minus_2": float(focus_t_2),
                "focus_mins_7d_avg": focus_7d_avg,
                "focus_mins_14d_avg": focus_14d_avg,
                "pomo_mins_7d_avg": pomo_7d_avg,
                "coding_mins_7d_avg": coding_7d_avg,
                "scheduled_class_hours_target_day": float(scheduled_class_hours),
                "pending_assignments_due_next_3d": pending_assign_3d,
                "exams_due_next_7d": exams_7d,
                "attendance_rate_14d": attendance_rate_14d,
                "active_habit_streaks_total": current_streaks,
                "tasks_created_last_7d": tasks_created_7d,
                "high_priority_pending_tasks": high_pri_pending,
                "workout_mins_7d_total": float(workout_mins_7d),
                "workouts_count_7d": workouts_cnt_7d,
                "days_since_last_workout": days_since_workout,
                TARGET_COLUMN: int(target_total_focus),
            }

            # Enforce privacy filtering
            sanitized_row = PrivacyFilter.sanitize_record(row_data)
            records.append(sanitized_row)

            curr += timedelta(days=1)

        return records

    def export_dataset(
        self,
        csv_path: Optional[Path] = None,
        metadata_path: Optional[Path] = None,
        filter_min_history: bool = True,
    ) -> Tuple[Path, Path, int]:
        """Extract dataset and write to CSV and JSON metadata files.
        
        Args:
            csv_path: Target CSV output path.
            metadata_path: Target metadata JSON output path.
            filter_min_history: If True, excludes rows with history_days_available < MIN_HISTORY_DAYS from final CSV.

        Returns:
            Tuple of (csv_path, metadata_path, exported_row_count)
        """
        records = self.extract_daily_grid()

        c_path = Path(csv_path) if csv_path else DEFAULT_CSV_PATH
        m_path = Path(metadata_path) if metadata_path else DEFAULT_METADATA_PATH

        c_path.parent.mkdir(parents=True, exist_ok=True)
        m_path.parent.mkdir(parents=True, exist_ok=True)

        # Validate column schema privacy
        PrivacyFilter.validate_dataset_schema(ALL_DATASET_COLUMNS)

        # Filter rows for training if requested
        if filter_min_history:
            export_rows = [r for r in records if r.get("history_days_available", 0) >= MIN_HISTORY_DAYS]
        else:
            export_rows = records

        # Write CSV
        with open(c_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=ALL_DATASET_COLUMNS)
            writer.writeheader()
            for r in export_rows:
                writer.writerow(r)

        # Write Metadata JSON
        metadata = {
            "dataset_name": "Astra Daily Focus Prediction Dataset",
            "version": "1.0.0",
            "target_column": TARGET_COLUMN,
            "feature_columns": FEATURE_COLUMNS,
            "total_extracted_days": len(records),
            "qualified_training_days": len(export_rows),
            "min_history_days_threshold": MIN_HISTORY_DAYS,
            "privacy_guarantee": "Strict (No text fields, note bodies, or PII)",
            "temporal_policy": "Strict anti-leakage (< t for behavioral history)",
            "generated_at": datetime.now().isoformat(),
        }

        with open(m_path, mode="w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return c_path, m_path, len(export_rows)
