from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy,
)

from services.productivity.pomodoro_service import PomodoroService, PomodoroState
from database.repositories.productivity_repository import ProductivityRepository


def _fmt_time(seconds: int) -> str:
    m, s = divmod(max(0, seconds), 60)
    return f"{m:02d}:{s:02d}"


class PomodoroWidget(QWidget):
    """Pomodoro Focus Timer sub-view."""

    def __init__(self, repo: ProductivityRepository, parent=None):
        super().__init__(parent)
        self._repo = repo
        self._service = PomodoroService(repo=repo, parent=self)
        self._service.tick.connect(self._on_tick)
        self._service.state_changed.connect(self._on_state_changed)
        self._service.session_completed.connect(self._on_session_completed)
        self._build()
        self._refresh_buttons()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Timer display card ───────────────────────────────────────────────
        timer_card = QFrame()
        timer_card.setProperty("class", "card pomodoro-card")
        card_layout = QVBoxLayout(timer_card)
        card_layout.setContentsMargins(40, 32, 40, 32)
        card_layout.setSpacing(12)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # State label (Work / Short Break / Long Break)
        self._state_lbl = QLabel("Ready to focus?")
        self._state_lbl.setProperty("class", "pomodoro-state-label")
        self._state_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Countdown display
        self._timer_lbl = QLabel("25:00")
        self._timer_lbl.setProperty("class", "pomodoro-timer")
        self._timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Session mode selector
        mode_row = QHBoxLayout()
        mode_row.setSpacing(8)
        mode_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_btns: dict[str, QPushButton] = {}
        for label, state in [
            ("🎯  Focus", PomodoroState.WORK),
            ("☕  Short Break", PomodoroState.SHORT_BREAK),
            ("🛋  Long Break", PomodoroState.LONG_BREAK),
        ]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "pill-tab")
            btn.clicked.connect(lambda _, s=state: self._select_mode(s))
            self._mode_btns[state] = btn
            mode_row.addWidget(btn)
        self._mode_btns[PomodoroState.WORK].setChecked(True)

        # Control buttons
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(12)
        ctrl_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.play_btn = QPushButton("▶  Start")
        self.play_btn.setProperty("class", "primary-btn pomodoro-play-btn")
        self.play_btn.clicked.connect(self._toggle_play_pause)

        self.skip_btn = QPushButton("⏭  Skip")
        self.skip_btn.setProperty("class", "secondary-btn")
        self.skip_btn.clicked.connect(self._service.skip)

        self.reset_btn = QPushButton("↺  Reset")
        self.reset_btn.setProperty("class", "secondary-btn")
        self.reset_btn.clicked.connect(self._on_reset)

        ctrl_row.addWidget(self.play_btn)
        ctrl_row.addWidget(self.skip_btn)
        ctrl_row.addWidget(self.reset_btn)

        # Sessions completed indicator
        self._sessions_lbl = QLabel("Sessions completed today: 0")
        self._sessions_lbl.setProperty("class", "card-description")
        self._sessions_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self._state_lbl)
        card_layout.addWidget(self._timer_lbl)
        card_layout.addLayout(mode_row)
        card_layout.addSpacing(8)
        card_layout.addLayout(ctrl_row)
        card_layout.addSpacing(8)
        card_layout.addWidget(self._sessions_lbl)

        layout.addWidget(timer_card)
        layout.addSpacing(20)

        # ── Recent sessions log ──────────────────────────────────────────────
        log_title = QLabel("Session History")
        log_title.setProperty("class", "card-title")
        layout.addWidget(log_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setFixedHeight(180)
        self._log_container = QWidget()
        self._log_layout = QVBoxLayout(self._log_container)
        self._log_layout.setContentsMargins(0, 0, 0, 0)
        self._log_layout.setSpacing(4)
        self._log_layout.addStretch()
        scroll.setWidget(self._log_container)
        layout.addWidget(scroll)

        self._refresh_log()

    # ── Slots / Handlers ─────────────────────────────────────────────────────

    def _toggle_play_pause(self):
        if self._service.is_running:
            self._service.pause()
        else:
            self._service.resume()
        self._refresh_buttons()

    def _select_mode(self, state: PomodoroState):
        for s, btn in self._mode_btns.items():
            btn.setChecked(s == state)
        if not self._service.is_running:
            self._service.stop()
            self._service.start(state)
            self._service.pause()
            self._on_tick(from_service=False)
            self._refresh_buttons()

    def _on_reset(self):
        self._service.reset()
        self._refresh_buttons()

    def _on_tick(self, seconds: int = None, from_service: bool = True):
        if seconds is None:
            seconds = self._service.seconds_remaining
        self._timer_lbl.setText(_fmt_time(seconds))

    def _on_state_changed(self, state_name: str):
        labels = {
            "Work": "🎯  Focus Session",
            "Short Break": "☕  Short Break",
            "Long Break": "🛋  Long Break",
            "Idle": "Ready to focus?",
        }
        self._state_lbl.setText(labels.get(state_name, state_name))
        self._refresh_buttons()

    def _on_session_completed(self, session_type: str, duration_minutes: int):
        completed = self._service.work_sessions_completed
        self._sessions_lbl.setText(f"Sessions completed today: {completed}")
        self._refresh_log()

    def _refresh_buttons(self):
        if self._service.is_running:
            self.play_btn.setText("⏸  Pause")
        else:
            self.play_btn.setText("▶  Start" if self._service.state == PomodoroState.IDLE else "▶  Resume")

    def _refresh_log(self):
        while self._log_layout.count() > 1:
            item = self._log_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sessions = self._repo.get_recent_pomodoro_sessions(limit=10)
        if not sessions:
            lbl = QLabel("No sessions logged yet.")
            lbl.setProperty("class", "card-description")
            self._log_layout.insertWidget(0, lbl)
            return

        for s in sessions:
            row = QLabel(f"  {s.session_type}  ·  {s.duration_minutes} min  ·  {s.completed_at}")
            row.setProperty("class", "log-entry")
            self._log_layout.insertWidget(0, row)
