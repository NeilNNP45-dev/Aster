from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame,
)

from database.models import TimetableEntry
from services.college.college_service import CollegeService
from ui.dialogs.timetable_dialog import TimetableDialog


class TimetableWidget(QWidget):
    def __init__(self, service: CollegeService, parent=None):
        super().__init__(parent)
        self._service = service
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QHBoxLayout()
        header.addStretch()
        self.add_btn = QPushButton("＋  Add Entry")
        self.add_btn.setProperty("class", "primary-btn")
        self.add_btn.clicked.connect(self._open_create_dialog)
        header.addWidget(self.add_btn)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(6)
        self._layout.addStretch()
        scroll.setWidget(self._container)
        layout.addWidget(scroll, 1)

    def refresh(self):
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        entries = self._service.get_timetable_entries()
        if not entries:
            empty = QLabel("No timetable entries yet.")
            empty.setProperty("class", "card-description")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, empty)
            return

        for entry in entries:
            row_frame = QFrame()
            row_frame.setProperty("class", "task-item")
            rl = QHBoxLayout(row_frame)
            rl.setContentsMargins(14, 10, 14, 10)
            d_lbl = QLabel(f"{entry.day_of_week} ({entry.start_time}–{entry.end_time})")
            d_lbl.setProperty("class", "task-title")
            loc_lbl = QLabel(entry.room or entry.location or 'No location')
            loc_lbl.setProperty("class", "task-due")
            rl.addWidget(d_lbl)
            rl.addStretch()
            rl.addWidget(loc_lbl)
            self._layout.insertWidget(self._layout.count() - 1, row_frame)

    def _open_create_dialog(self):
        courses = self._service.get_courses()
        if not courses:
            return
        dialog = TimetableDialog(courses, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            entry = dialog.get_timetable_entry()
            if entry:
                self._service.create_timetable_entry(
                    course_id=entry.course_id,
                    day_of_week=entry.day_of_week,
                    start_time=entry.start_time,
                    end_time=entry.end_time,
                    room=entry.room,
                    location=entry.location,
                    recurring=entry.recurring,
                    notes=entry.notes,
                )
                self.refresh()
