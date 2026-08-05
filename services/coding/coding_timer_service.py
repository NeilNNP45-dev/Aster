from typing import Optional
from datetime import datetime
from PySide6.QtCore import QObject, QTimer, Signal

from database.models import CodingSession
from database.repositories.coding_repository import CodingRepository


class CodingTimerState:
    IDLE = "Idle"
    CODING = "Coding"
    SHORT_BREAK = "Short Break"
    LONG_BREAK = "Long Break"


class CodingTimerService(QObject):
    """Simple Coding timer service modeled after PomodoroService.

    Emits:
        tick(seconds_remaining)
        state_changed(state_name)
        session_completed(session_dataclass)
    """

    tick = Signal(int)
    state_changed = Signal(str)
    session_completed = Signal(object)

    def __init__(self, repo: Optional[CodingRepository] = None, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._repo = repo or CodingRepository()
        self._state = CodingTimerState.IDLE
        self._seconds_remaining = 0
        self._initial_seconds = 0
        self._start_time = None

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

    @property
    def is_running(self) -> bool:
        return self._timer.isActive()

    def start(self, duration_seconds: int, project_id: Optional[int] = None):
        if self._timer.isActive():
            return
        self._initial_seconds = duration_seconds
        self._seconds_remaining = duration_seconds
        self._project_id = project_id
        self._start_time = datetime.now()
        self._state = CodingTimerState.CODING
        self.state_changed.emit(self._state)
        self._timer.start()

    def pause(self):
        self._timer.stop()

    def resume(self):
        if not self._timer.isActive() and self._state != CodingTimerState.IDLE:
            self._timer.start()

    def stop(self, log_session: bool = True):
        self._timer.stop()
        if log_session and self._seconds_remaining <= 0:
            # nothing to log
            pass
        if log_session and self._start_time is not None:
            # log a partial session
            end_time = datetime.now()
            elapsed = int((end_time - self._start_time).total_seconds())
            duration_minutes = max(1, round(elapsed / 60))
            try:
                session = CodingSession(
                    project_id=getattr(self, "_project_id", None),
                    start_at=self._start_time.isoformat(),
                    end_at=end_time.isoformat(),
                    duration_minutes=duration_minutes,
                    session_type="Coding",
                )
                self._repo.log_session(session)
                self.session_completed.emit(session)
            except Exception:
                pass

        self._state = CodingTimerState.IDLE
        self._seconds_remaining = 0
        self._initial_seconds = 0
        self._start_time = None
        self.state_changed.emit(self._state)

    def _on_tick(self):
        if self._seconds_remaining > 0:
            self._seconds_remaining -= 1
            self.tick.emit(self._seconds_remaining)

        if self._seconds_remaining > 0:
            return

        # session complete
        self._timer.stop()
        end_time = datetime.now()
        if self._start_time is not None:
            elapsed = int((end_time - self._start_time).total_seconds())
        else:
            elapsed = self._initial_seconds

        duration_minutes = max(1, round(elapsed / 60))
        try:
            session = CodingSession(
                project_id=getattr(self, "_project_id", None),
                start_at=self._start_time.isoformat() if self._start_time is not None else end_time.isoformat(),
                end_at=end_time.isoformat(),
                duration_minutes=duration_minutes,
                session_type="Coding",
            )
            self._repo.log_session(session)
            self.session_completed.emit(session)
        except Exception:
            pass
        self._state = CodingTimerState.IDLE
        self.state_changed.emit(self._state)
        self.tick.emit(0)
