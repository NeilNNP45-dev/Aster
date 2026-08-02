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
