from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame,
)

from services.college.college_service import CollegeService
from ui.dialogs.attendance_dialog import AttendanceDialog


class AttendanceWidget(QWidget):
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
        self.add_btn = QPushButton("＋  Add Attendance")
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

        courses = self._service.get_courses()
        if not courses:
            empty = QLabel("Add a course first to log attendance.")
            empty.setProperty("class", "card-description")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, empty)
            return

        for course in courses:
            summary = self._service.get_attendance_summary(course.id)
            row = QLabel(f"{course.name}: {summary['percentage']}% ({summary['present_count']}/{summary['total_records']})")
            row.setProperty("class", "card-description")
            self._layout.insertWidget(self._layout.count() - 1, row)

    def _open_create_dialog(self):
        courses = self._service.get_courses()
        if not courses:
            return
        dialog = AttendanceDialog(courses, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            attendance = dialog.get_attendance()
            if attendance:
                self._service.record_attendance(
                    course_id=attendance.course_id,
                    attendance_date=attendance.attendance_date,
                    status=attendance.status,
                    notes=attendance.notes,
                )
                self.refresh()
