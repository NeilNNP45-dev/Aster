from enum import Enum, auto
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal

from database.models import PomodoroSession
from database.repositories.productivity_repository import ProductivityRepository


class PomodoroState(Enum):
    IDLE = auto()
    WORK = auto()
    SHORT_BREAK = auto()
    LONG_BREAK = auto()


# Default session durations in seconds
SESSION_DURATIONS = {
    PomodoroState.WORK: 25 * 60,
    PomodoroState.SHORT_BREAK: 5 * 60,
    PomodoroState.LONG_BREAK: 15 * 60,
}

WORK_SESSIONS_BEFORE_LONG_BREAK = 4


class PomodoroService(QObject):
    """
    Pomodoro Focus Timer state machine built on QTimer.

    Signals:
        tick(seconds_remaining): Emitted every second when running.
        state_changed(state_name): Emitted when session type changes.
        session_completed(session_type, duration_minutes): Emitted when a session ends.
    """

    tick = Signal(int)                     # seconds remaining
    state_changed = Signal(str)            # state name string
    session_completed = Signal(str, int)   # (session_type, duration_minutes)

    def __init__(self, repo: Optional[ProductivityRepository] = None, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._repo = repo or ProductivityRepository()
        self._state = PomodoroState.IDLE
        self._seconds_remaining = 0
        self._work_sessions_completed = 0

        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1 second tick
        self._timer.timeout.connect(self._on_tick)

    # ── Public Properties ────────────────────────────────────────────────────

    @property
    def state(self) -> PomodoroState:
        return self._state

    @property
    def seconds_remaining(self) -> int:
        return self._seconds_remaining

    @property
    def is_running(self) -> bool:
        return self._timer.isActive()

    @property
    def work_sessions_completed(self) -> int:
        return self._work_sessions_completed

    # ── Public Control Methods ───────────────────────────────────────────────

    def start(self, state: Optional[PomodoroState] = None):
        """Start a session. If state is None and timer is paused, resume."""
        if self._timer.isActive():
            return  # Already running

        if state is not None:
            # Starting a fresh session
            self._state = state
            self._seconds_remaining = SESSION_DURATIONS[state]
            self.state_changed.emit(self._state_name())

        if self._state == PomodoroState.IDLE:
            self._state = PomodoroState.WORK
            self._seconds_remaining = SESSION_DURATIONS[PomodoroState.WORK]
            self.state_changed.emit(self._state_name())

        self._timer.start()

    def pause(self):
        """Pause the running timer without resetting."""
        self._timer.stop()

    def resume(self):
        """Resume a paused timer."""
        if not self._timer.isActive() and self._state != PomodoroState.IDLE:
            self._timer.start()

    def reset(self):
        """Stop and reset the current session back to the start of the same state."""
        self._timer.stop()
        if self._state != PomodoroState.IDLE:
            self._seconds_remaining = SESSION_DURATIONS.get(self._state, 0)
            self.tick.emit(self._seconds_remaining)

    def stop(self):
        """Stop timer and return to IDLE state."""
        self._timer.stop()
        self._state = PomodoroState.IDLE
        self._seconds_remaining = 0
        self.state_changed.emit("Idle")

    def skip(self):
        """Skip current session and advance to the next one without logging."""
        self._timer.stop()
        self._advance_state(log_session=False)

    # ── Private Methods ──────────────────────────────────────────────────────

    def _on_tick(self):
        """Called every second by QTimer."""
        if self._seconds_remaining > 0:
            self._seconds_remaining -= 1
            self.tick.emit(self._seconds_remaining)
        else:
            # Session naturally completed
            self._timer.stop()
            self._advance_state(log_session=True)

    def _advance_state(self, log_session: bool = True):
        """Log current session (if requested) and transition to the next state."""
        completed_state = self._state

        if log_session and completed_state in (PomodoroState.WORK, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK):
            duration_minutes = SESSION_DURATIONS[completed_state] // 60
            session_type = self._state_name(completed_state)
            self._log_session(session_type, duration_minutes)
            self.session_completed.emit(session_type, duration_minutes)

        # Determine next state
        if completed_state == PomodoroState.WORK:
            self._work_sessions_completed += 1
            if self._work_sessions_completed % WORK_SESSIONS_BEFORE_LONG_BREAK == 0:
                next_state = PomodoroState.LONG_BREAK
            else:
                next_state = PomodoroState.SHORT_BREAK
        else:
            # After any break, go back to Work
            next_state = PomodoroState.WORK

        self._state = next_state
        self._seconds_remaining = SESSION_DURATIONS[next_state]
        self.state_changed.emit(self._state_name())
        self.tick.emit(self._seconds_remaining)

    def _log_session(self, session_type: str, duration_minutes: int):
        """Persist a completed session to the database."""
        try:
            session = PomodoroSession(
                duration_minutes=duration_minutes,
                session_type=session_type,
            )
            self._repo.log_pomodoro_session(session)
        except Exception:
            # Never crash the UI timer due to a logging failure
            pass

    @staticmethod
    def _state_name(state: Optional[PomodoroState] = None) -> str:
        """Return a human-readable display name for a given state."""
        if state is None:
            return ""
        return {
            PomodoroState.IDLE: "Idle",
            PomodoroState.WORK: "Work",
            PomodoroState.SHORT_BREAK: "Short Break",
            PomodoroState.LONG_BREAK: "Long Break",
        }.get(state, "Unknown")
