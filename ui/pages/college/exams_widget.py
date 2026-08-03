from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame,
)

from services.college.college_service import CollegeService
from ui.dialogs.exam_dialog import ExamDialog


class ExamsWidget(QWidget):
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
        self.add_btn = QPushButton("＋  Add Exam")
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

        exams = self._service.get_exams()
        if not exams:
            empty = QLabel("No exams yet.")
            empty.setProperty("class", "card-description")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, empty)
            return

        for exam in exams:
            row = QLabel(f"{exam.title} • {exam.scheduled_at} • {exam.location or 'No location'}")
            row.setProperty("class", "card-description")
            self._layout.insertWidget(self._layout.count() - 1, row)

    def _open_create_dialog(self):
        courses = self._service.get_courses()
        if not courses:
            return
        dialog = ExamDialog(courses, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            exam = dialog.get_exam()
            if exam:
                self._service.create_exam(
                    course_id=exam.course_id,
                    title=exam.title,
                    scheduled_at=exam.scheduled_at,
                    location=exam.location,
                    exam_type=exam.exam_type,
                    status=exam.status,
                    notes=exam.notes,
                )
                self.refresh()
