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
