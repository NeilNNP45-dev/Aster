"""Unit tests for Astra ML v1 Feature Extractor and Privacy Engine."""

import csv
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from database.connection import DatabaseConnection
from database.repositories.productivity_repository import ProductivityRepository
from database.repositories.coding_repository import CodingRepository
from database.models import PomodoroSession, CodingSession, Task, DailyGoal
from astra.config import (
    ALL_DATASET_COLUMNS,
    FEATURE_COLUMNS,
    QUALIFIER_COLUMNS,
    FORBIDDEN_TEXT_FIELDS,
    TARGET_COLUMN,
    MIN_HISTORY_DAYS,
)
from astra.extractor.privacy import PrivacyFilter
from astra.extractor.feature_extractor import FeatureExtractor


class TestAstraPrivacyFilter(unittest.TestCase):
    """Test suite for PrivacyFilter rules."""

    def test_forbidden_text_fields_rejected(self):
        for field in FORBIDDEN_TEXT_FIELDS:
            self.assertFalse(
                PrivacyFilter.is_safe_field(field),
                f"Field '{field}' should be rejected by privacy filter!",
            )

    def test_sanitize_record_removes_text(self):
        raw_record = {
            "date": "2026-08-26",
            "history_days_available": 15,
            "title": "Secret Note Title",
            "content": "Private note body text",
            "notes": "User notes",
            "focus_mins_7d_avg": 45.0,
            "target_total_focus_mins": 60,
        }
        sanitized = PrivacyFilter.sanitize_record(raw_record)
        self.assertNotIn("title", sanitized)
        self.assertNotIn("content", sanitized)
        self.assertNotIn("notes", sanitized)
        self.assertIn("date", sanitized)
        self.assertIn("focus_mins_7d_avg", sanitized)
        self.assertIn("target_total_focus_mins", sanitized)

    def test_validate_dataset_schema_raises_on_forbidden_col(self):
        bad_schema = ["date", "target_total_focus_mins", "notes"]
        with self.assertRaises(ValueError):
            PrivacyFilter.validate_dataset_schema(bad_schema)


class TestAstraFeatureExtractor(unittest.TestCase):
    """Test suite for FeatureExtractor engine."""

    def setUp(self):
        self.db_conn = DatabaseConnection(":memory:")
        self.prod_repo = ProductivityRepository(self.db_conn)
        self.coding_repo = CodingRepository(self.db_conn)
        self.extractor = FeatureExtractor(self.db_conn)

    def tearDown(self):
        self.extractor.close()
        self.prod_repo.close()
        self.coding_repo.close()
        self.db_conn.close()

    def test_empty_database_returns_empty_grid(self):
        records = self.extractor.extract_daily_grid()
        self.assertEqual(len(records), 0)

    def test_target_calculation_and_temporal_boundary(self):
        """Verify target_total_focus_mins calculation and strict anti-leakage history boundary."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-01 10:30:00"),
            )
            cursor.execute(
                "INSERT INTO coding_sessions (duration_minutes, session_type, start_at) VALUES (?, ?, ?)",
                (50, "Coding", "2026-08-01 14:00:00"),
            )
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (30, "Work", "2026-08-02 11:00:00"),
            )

        records = self.extractor.extract_daily_grid()
        self.assertEqual(len(records), 2)
        day1, day2 = records[0], records[1]

        self.assertEqual(day1["date"], "2026-08-01")
        self.assertEqual(day2["date"], "2026-08-02")
        # Day 1 Target: 25 (Pomo Work) + 50 (Coding) = 75 mins
        self.assertEqual(day1[TARGET_COLUMN], 75)
        # Day 2 Target: 30 mins
        self.assertEqual(day2[TARGET_COLUMN], 30)
        # Anti-Leakage: Day 2's focus_mins_t_minus_1 must equal Day 1's focus (75 mins)
        self.assertEqual(day2["focus_mins_t_minus_1"], 75.0)

    def test_minimum_history_days_available(self):
        """Verify history_days_available calculation and filtering threshold."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-01 10:00:00"),
            )
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-20 10:00:00"),
            )

        records = self.extractor.extract_daily_grid()
        self.assertEqual(len(records), 20)
        self.assertEqual(records[0]["history_days_available"], 0)
        self.assertEqual(records[13]["history_days_available"], 13)
        self.assertEqual(records[14]["history_days_available"], 14)

        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "test_dataset.csv"
            meta_path = Path(tmp_dir) / "test_meta.json"
            _, _, count = self.extractor.export_dataset(
                csv_path=csv_path, metadata_path=meta_path, filter_min_history=True,
            )
            self.assertEqual(count, 6)  # Days 14..19 = 6 rows
            self.assertTrue(csv_path.exists())
            self.assertTrue(meta_path.exists())

    def test_no_text_or_pii_in_dataset_columns(self):
        """Verify that exported CSV header contains only approved columns."""
        for col in ALL_DATASET_COLUMNS:
            self.assertTrue(
                PrivacyFilter.is_safe_field(col),
                f"Exported column '{col}' violates privacy constraints!",
            )

    # ------------------------------------------------------------------
    # AUDIT-DRIVEN TESTS
    # ------------------------------------------------------------------

    def test_break_sessions_excluded_from_target(self):
        """Break session types must not count toward target_total_focus_mins."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-10 10:00:00"),
            )
            cursor.execute(
                "INSERT INTO coding_sessions (duration_minutes, session_type, start_at) VALUES (?, ?, ?)",
                (30, "Coding", "2026-08-10 11:00:00"),
            )
            # Break sessions — must NOT count toward target
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (5, "Short Break", "2026-08-10 10:30:00"),
            )
            cursor.execute(
                "INSERT INTO coding_sessions (duration_minutes, session_type, start_at) VALUES (?, ?, ?)",
                (10, "Short Break", "2026-08-10 12:00:00"),
            )

        records = self.extractor.extract_daily_grid()
        r = records[0]
        # 25 (Pomo Work) + 30 (Coding) = 55; breaks (5 + 10) must be excluded
        self.assertEqual(r[TARGET_COLUMN], 55, "Break sessions incorrectly included in target!")

    def test_inactive_days_contribute_zero_to_rolling_averages(self):
        """Days within the history window with no activity must contribute 0, not be skipped."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (70, "Work", "2026-08-08 10:00:00"),  # t-7 relative to Aug 15
            )
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (50, "Work", "2026-08-15 10:00:00"),  # target day t
            )

        records = self.extractor.extract_daily_grid()
        aug15 = next(r for r in records if r["date"] == "2026-08-15")

        # [Aug 8..Aug 14]: Aug 8=70, Aug 9-14=0  -> 70/7 = 10.0
        self.assertAlmostEqual(aug15["focus_mins_7d_avg"], round(70 / 7, 2))
        # Target = Aug 15 only = 50
        self.assertEqual(aug15[TARGET_COLUMN], 50)

    def test_days_since_workout_is_minus_one_when_none_logged(self):
        """When no workout has ever been logged, days_since_last_workout must be -1 (not 999)."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-15 10:00:00"),
            )

        records = self.extractor.extract_daily_grid()
        self.assertEqual(
            records[0]["days_since_last_workout"],
            -1,
            "Sentinel for no-workout-ever must be -1, not 999",
        )

    def test_attendance_rate_defaults_to_100_when_no_logs(self):
        """attendance_rate_14d defaults to 100.0 when no attendance logs exist in the window."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-15 10:00:00"),
            )

        records = self.extractor.extract_daily_grid()
        self.assertAlmostEqual(
            records[0]["attendance_rate_14d"],
            100.0,
            msg="attendance_rate_14d should default to 100.0 when no logs exist",
        )

    def test_assignment_created_on_target_day_excluded(self):
        """Assignments created on target day t must not appear in pending_assignments_due_next_3d."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute("INSERT INTO courses (name, credit_hours) VALUES (?, ?)", ("Math", 3))
            # Created BEFORE t -> must count
            cursor.execute(
                "INSERT INTO assignments (course_id, title, status, created_at, due_date) VALUES (?, ?, ?, ?, ?)",
                (1, "A1", "Pending", "2026-08-14 09:00:00", "2026-08-16 23:59:00"),
            )
            # Created ON t -> must NOT count (not known before prediction time)
            cursor.execute(
                "INSERT INTO assignments (course_id, title, status, created_at, due_date) VALUES (?, ?, ?, ?, ?)",
                (1, "A2", "Pending", "2026-08-15 09:00:00", "2026-08-16 23:59:00"),
            )
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-01 10:00:00"),
            )
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-15 10:00:00"),
            )

        records = self.extractor.extract_daily_grid()
        aug15 = next(r for r in records if r["date"] == "2026-08-15")
        self.assertEqual(
            aug15["pending_assignments_due_next_3d"],
            1,
            "Assignment created on target day t should not be counted",
        )

    def test_midnight_boundary_session_attribution(self):
        """Sessions at 23:59 on t-1 and 00:01 on t must be attributed to the correct day."""
        with self.db_conn.get_cursor() as cursor:
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (25, "Work", "2026-08-14 23:59:00"),
            )
            cursor.execute(
                "INSERT INTO pomodoro_sessions (duration_minutes, session_type, completed_at) VALUES (?, ?, ?)",
                (30, "Work", "2026-08-15 00:01:00"),
            )

        records = self.extractor.extract_daily_grid()
        aug14 = next(r for r in records if r["date"] == "2026-08-14")
        aug15 = next(r for r in records if r["date"] == "2026-08-15")

        self.assertEqual(aug14[TARGET_COLUMN], 25, "23:59 session must target Aug 14")
        self.assertEqual(aug15[TARGET_COLUMN], 30, "00:01 session must target Aug 15")
        self.assertEqual(
            aug15["focus_mins_t_minus_1"],
            25.0,
            "Aug 15 focus_mins_t_minus_1 must reflect Aug 14 activity",
        )

    def test_history_days_available_not_in_feature_columns(self):
        """history_days_available is a qualifier — must NOT be in FEATURE_COLUMNS."""
        self.assertNotIn(
            "history_days_available",
            FEATURE_COLUMNS,
            "history_days_available must be in QUALIFIER_COLUMNS only",
        )
        self.assertIn(
            "history_days_available",
            QUALIFIER_COLUMNS,
            "history_days_available must be present in QUALIFIER_COLUMNS",
        )

    def test_active_habit_streaks_not_in_feature_columns(self):
        """active_habit_streaks_total was removed due to snapshot leakage — must NOT be in FEATURE_COLUMNS."""
        self.assertNotIn(
            "active_habit_streaks_total",
            FEATURE_COLUMNS,
            "active_habit_streaks_total must not be in FEATURE_COLUMNS (snapshot leakage)",
        )


if __name__ == "__main__":
    unittest.main()
