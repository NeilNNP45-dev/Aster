"""Astra ML Configuration and Schema Definitions."""

from pathlib import Path

# Base Paths
ASTRA_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ASTRA_DIR.parent
DEFAULT_DATASET_DIR = ASTRA_DIR / "data" / "processed"
DEFAULT_CSV_PATH = DEFAULT_DATASET_DIR / "dataset_daily.csv"
DEFAULT_METADATA_PATH = DEFAULT_DATASET_DIR / "dataset_metadata.json"

# Minimum Required Historical Days for Training Validation
MIN_HISTORY_DAYS = 14

# Target Column Name
TARGET_COLUMN = "target_total_focus_mins"

# Data-quality / cold-start qualifier columns.
# These are exported to the CSV for filtering but must NOT be used as ML predictor features.
# Rationale: history_days_available encodes "days since first install", which is spurious
# as a productivity predictor and will cause the model to learn install-age rather than
# genuine behavioral patterns.
QUALIFIER_COLUMNS = [
    "history_days_available",
]

# Explicit Predictor Feature Columns (in order).
# All behavioral features use data strictly from before target day t (< t).
# Schedule features (>= t) use only forward-looking commitments that are known at prediction time.
#
# REMOVED from v1 FEATURE_COLUMNS:
#   active_habit_streaks_total — reads current DB snapshot (SUM(streak_count)) and applies
#     the same value to ALL historical rows. This is a confirmed temporal leakage issue: the
#     streak count at extraction time contaminates rows from months prior when the streak
#     did not exist. Reliable time-sliced streak history requires a streak-log table
#     (schema change), which is out of scope for v1.
FEATURE_COLUMNS = [
    # Temporal Context (Target Day t)
    "target_day_of_week",
    "target_is_weekend",
    "target_day_of_month",
    # Historical Focus (< t)
    "focus_mins_t_minus_1",
    "focus_mins_t_minus_2",
    "focus_mins_7d_avg",
    "focus_mins_14d_avg",
    "pomo_mins_7d_avg",
    "coding_mins_7d_avg",
    # Known Schedule Horizon (>= t)
    # These reference target day or future dates under the documented assumption that
    # timetable schedules are fixed/recurring and assignment/exam due dates are entered
    # in advance — i.e., this information is already known before prediction time.
    "scheduled_class_hours_target_day",
    "pending_assignments_due_next_3d",
    "exams_due_next_7d",
    # Academic History (< t)
    "attendance_rate_14d",
    # Productivity History (< t)
    "tasks_created_last_7d",
    "high_priority_pending_tasks",
    # Fitness History (< t)
    # days_since_last_workout = -1 means no workout has ever been logged (sentinel value).
    # The training pipeline must handle this via imputation before fitting any model.
    "workout_mins_7d_total",
    "workouts_count_7d",
    "days_since_last_workout",
]

# All columns exported to CSV (qualifier + features + target).
# Consumers should use only FEATURE_COLUMNS as model inputs, TARGET_COLUMN as the label,
# and QUALIFIER_COLUMNS for filtering only.
ALL_DATASET_COLUMNS = ["date"] + QUALIFIER_COLUMNS + FEATURE_COLUMNS + [TARGET_COLUMN]

# Forbidden Text / PII Columns - Enforced by Privacy Filter
FORBIDDEN_TEXT_FIELDS = {
    "title",
    "description",
    "content",
    "notes",
    "instructor_name",
    "room",
    "location",
    "repo_path",
    "github_full_name",
    "github_html_url",
    "weight_kg",
    "note",
}
