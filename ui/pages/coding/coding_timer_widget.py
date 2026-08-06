from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QDialog
from PySide6.QtCore import Qt

from services.coding.coding_timer_service import CodingTimerService
from ui.dialogs.session_note_dialog import SessionNoteDialog


class CodingTimerWidget(QWidget):
    def __init__(self, services, parent=None):
        super().__init__(parent)
        self._services = services
        self._timer_service: CodingTimerService = services.get("timer_service")
        self._project_service = services.get("project_service")
        self._build()
        self._connect()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        title = QLabel("Coding Timer")
        title.setProperty("class", "page-header")
        layout.addWidget(title)

        self._time_label = QLabel("00:00")
        self._time_label.setProperty("class", "pomodoro-timer")
        self._time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._time_label)
        self._project_combo = QComboBox()
        self._project_combo.setProperty("class", "form-combo")
        layout.addWidget(self._project_combo)
        btn_layout = QVBoxLayout()
        self._start_btn = QPushButton("Start")
        self._pause_btn = QPushButton("Pause")
        self._stop_btn = QPushButton("Stop")
        self._start_btn.setProperty("class", "primary-btn pomodoro-play-btn")
        self._pause_btn.setProperty("class", "secondary-btn")
        self._stop_btn.setProperty("class", "danger-btn")
        btn_layout.addWidget(self._start_btn)
        btn_layout.addWidget(self._pause_btn)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)
        self.refresh_projects()

    def _connect(self):
        self._start_btn.clicked.connect(self._on_start)
        self._pause_btn.clicked.connect(self._on_pause)
        self._stop_btn.clicked.connect(self._on_stop)
        if self._timer_service:
            self._timer_service.tick.connect(self._on_tick)
            self._timer_service.state_changed.connect(self._on_state_changed)
            self._timer_service.session_completed.connect(self._on_session_completed)

    def refresh_projects(self):
        self._project_combo.clear()
        projects = []
        if self._project_service:
            projects = self._project_service.list_projects()
        self._project_combo.addItem("(No Project)", None)
        for p in projects:
            self._project_combo.addItem(p.name, p.id)

    def _on_start(self):
        # start a 25-minute coding session by default
        project_id = self._project_combo.currentData()
        if self._timer_service:
            self._timer_service.start(duration_seconds=25 * 60, project_id=project_id)

    def _on_pause(self):
        if self._timer_service:
            self._timer_service.pause()

    def _on_stop(self):
        if self._timer_service:
            self._timer_service.stop(log_session=True)

    def _on_tick(self, seconds_remaining: int):
        mins, secs = divmod(max(0, seconds_remaining), 60)
        self._time_label.setText(f"{mins:02d}:{secs:02d}")

    def _on_state_changed(self, state: str):
        # could update UI affordances based on state
        pass

    def _on_session_completed(self, session):
        # prompt for optional notes and update session.record
        dlg = SessionNoteDialog(self)
        if dlg.exec() == QDialog.Accepted:
            notes = dlg.get_notes()
            if notes:
                # update session notes via repository
                try:
                    repo = self._services.get("repo")
                    session.notes = notes
                    repo.log_session(session)
                except Exception:
                    pass
