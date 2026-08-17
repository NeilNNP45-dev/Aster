from dataclasses import dataclass
from typing import Optional


@dataclass
class Task:
    """Task data entity for To-Do list."""
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    priority: str = "Medium"  # 'High', 'Medium', 'Low'
    category: str = "General"
    due_date: Optional[str] = None
    is_completed: bool = False
    created_at: Optional[str] = None


@dataclass
class DailyGoal:
    """Daily goal & habit tracking entity."""
    id: Optional[int] = None
    title: str = ""
    category: str = "General"
    is_completed: bool = False
    reset_daily: bool = True
    streak_count: int = 0
    last_completed_at: Optional[str] = None


@dataclass
class Note:
    """Note document entity."""
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    category: str = "General"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class PomodoroSession:
    """Log entity for completed Pomodoro focus sessions."""
    id: Optional[int] = None
    duration_minutes: int = 25
    session_type: str = "Work"  # 'Work', 'Short Break', 'Long Break'
    completed_at: Optional[str] = None


@dataclass
class Course:
    """Academic course entity for the College module."""
    id: Optional[int] = None
    name: str = ""
    code: str = ""
    instructor_name: str = ""
    credit_hours: int = 0
    description: str = ""
    color_tag: str = "#7C3AED"
    is_active: bool = True
    created_at: Optional[str] = None


@dataclass
class TimetableEntry:
    """Weekly timetable entry for a course."""
    id: Optional[int] = None
    course_id: int = 0
    day_of_week: str = "Monday"
    start_time: str = "09:00"
    end_time: str = "10:00"
    room: str = ""
    location: str = ""
    recurring: bool = True
    notes: str = ""
    created_at: Optional[str] = None


@dataclass
class AttendanceLog:
    """Attendance record for a course on a specific date."""
    id: Optional[int] = None
    course_id: int = 0
    attendance_date: str = ""
    status: str = "Present"
    notes: str = ""
    created_at: Optional[str] = None


@dataclass
class Assignment:
    """College assignment entity."""
    id: Optional[int] = None
    course_id: int = 0
    title: str = ""
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "Medium"
    status: str = "Pending"
    estimated_minutes: int = 0
    created_at: Optional[str] = None


@dataclass
class Exam:
    """College exam entity."""
    id: Optional[int] = None
    course_id: int = 0
    title: str = ""
    exam_type: str = "Exam"
    scheduled_at: str = ""
    location: str = ""
    status: str = "Planned"
    notes: str = ""
    created_at: Optional[str] = None


@dataclass
class CodingProject:
    """Coding project entity."""
    id: Optional[int] = None
    name: str = ""
    repo_path: Optional[str] = None
    github_full_name: Optional[str] = None
    github_html_url: Optional[str] = None
    description: str = ""
    language: str = ""
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class CodingSession:
    """Coding timer session log."""
    id: Optional[int] = None
    project_id: Optional[int] = None
    start_at: str = ""
    end_at: Optional[str] = None
    duration_minutes: int = 0
    session_type: str = "Coding"  # 'Coding', 'Short Break', 'Long Break'
    notes: str = ""
    created_at: Optional[str] = None


@dataclass
class CodingGoal:
    """Daily coding goal (habit-like)."""
    id: Optional[int] = None
    title: str = ""
    project_id: Optional[int] = None
    is_completed: bool = False
    reset_daily: bool = True
    streak_count: int = 0
    last_completed_at: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class WorkoutEntry:
    """Fitness workout log entry."""
    id: Optional[int] = None
    title: str = ""
    workout_type: str = "Workout"
    duration_minutes: int = 0
    calories: int = 0
    notes: str = ""
    performed_at: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class WeightEntry:
    """Daily body weight record."""
    id: Optional[int] = None
    weight_kg: float = 0.0
    note: str = ""
    recorded_at: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class DomainSummary:
    """Aggregated metrics summary across all domains."""
    total_focus_minutes: int = 0
    tasks_completed: int = 0
    tasks_total: int = 0
    goals_completed: int = 0
    goals_total: int = 0
    active_streaks: int = 0
    classes_attended: int = 0
    classes_total: int = 0
    assignments_completed: int = 0
    assignments_total: int = 0
    coding_minutes: int = 0
    active_projects: int = 0
    workouts_completed: int = 0
    workout_minutes: int = 0
    calories_burned: int = 0
    latest_weight_kg: Optional[float] = None


@dataclass
class FocusTimeStats:
    """Daily focus time breakdown."""
    date_str: str = ""
    pomodoro_minutes: int = 0
    coding_minutes: int = 0
    total_minutes: int = 0


@dataclass
class AnalyticsOverview:
    """Combined analytics data for a specific time period."""
    start_date: str = ""
    end_date: str = ""
    total_focus_hours: float = 0.0
    task_completion_rate: float = 0.0
    attendance_rate: float = 0.0
    summary: Optional[DomainSummary] = None


@dataclass
class ReportSummary:
    """Structured report document representation."""
    report_type: str = "Weekly"  # 'Weekly', 'Monthly'
    period_label: str = ""
    start_date: str = ""
    end_date: str = ""
    summary_text: str = ""
    highlights: Optional[list] = None
    productivity_notes: str = ""
    college_notes: str = ""
    coding_notes: str = ""
    fitness_notes: str = ""
    generated_at: str = ""

