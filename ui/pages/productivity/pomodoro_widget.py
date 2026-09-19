from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy,
)

from services.productivity.pomodoro_service import PomodoroService, PomodoroState
from database.repositories.productivity_repository import ProductivityRepository
from ui.dialogs.pomodoro_settings_dialog import PomodoroSettingsDialog


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
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(16)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_card.setMinimumHeight(430)

        # Header: current state on the left, settings on the right.
        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        self.settings_btn = QPushButton("⚙  Timer Settings")
        self.settings_btn.setProperty("class", "secondary-btn pomodoro-settings-btn")
        self.settings_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.settings_btn.clicked.connect(self._open_settings)

        # State label (Work / Short Break / Long Break)
        self._state_lbl = QLabel("Ready to focus?")
        self._state_lbl.setProperty("class", "pomodoro-state-label")
        self._state_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._state_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        header_row.addWidget(self._state_lbl)
        header_row.addWidget(self.settings_btn)

        # Session mode selector
        self._mode_frame = QFrame()
        self._mode_frame.setProperty("class", "pomodoro-mode-selector")
        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(4, 4, 4, 4)
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
        self._mode_frame.setLayout(mode_row)

        # Countdown display. Keeping the timer in its own frame prevents the
        # mode selector and large glyphs from sharing the same visual space.
        self._timer_display = QFrame()
        self._timer_display.setProperty("class", "pomodoro-display")
        self._timer_display.setMinimumHeight(142)
        self._timer_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        timer_display_layout = QVBoxLayout(self._timer_display)
        timer_display_layout.setContentsMargins(16, 6, 16, 6)
        self._timer_lbl = QLabel("25:00")
        self._timer_lbl.setProperty("class", "pomodoro-timer")
        self._timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._timer_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        timer_display_layout.addWidget(self._timer_lbl)

        # Primary control is intentionally separated from secondary actions.
        self.play_btn = QPushButton("▶  Start")
        self.play_btn.setProperty("class", "primary-btn pomodoro-play-btn")
        self.play_btn.setMinimumWidth(190)
        self.play_btn.setMinimumHeight(44)
        self.play_btn.clicked.connect(self._toggle_play_pause)

        secondary_row = QHBoxLayout()
        secondary_row.setSpacing(10)
        secondary_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.skip_btn = QPushButton("⏭  Skip")
        self.skip_btn.setProperty("class", "secondary-btn")
        self.skip_btn.clicked.connect(self._service.skip)

        self.reset_btn = QPushButton("↺  Reset")
        self.reset_btn.setProperty("class", "secondary-btn")
        self.reset_btn.clicked.connect(self._on_reset)

        secondary_row.addWidget(self.skip_btn)
        secondary_row.addWidget(self.reset_btn)

        # Sessions completed indicator
        self._sessions_lbl = QLabel("Sessions completed today: 0")
        self._sessions_lbl.setProperty("class", "card-description")
        self._sessions_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addLayout(header_row)
        card_layout.addWidget(self._mode_frame)
        card_layout.addWidget(self._timer_display)
        card_layout.addWidget(self.play_btn, 0, Qt.AlignmentFlag.AlignCenter)
        card_layout.addLayout(secondary_row)
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

    def _open_settings(self):
        dialog = PomodoroSettingsDialog(self._service.durations, self)
        if dialog.exec() == PomodoroSettingsDialog.DialogCode.Accepted:
            self._service.configure_durations(*dialog.get_values())

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
