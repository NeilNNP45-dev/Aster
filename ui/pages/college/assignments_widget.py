from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame,
)

from services.college.college_service import CollegeService
from ui.dialogs.assignment_dialog import AssignmentDialog


class AssignmentsWidget(QWidget):
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
        self.add_btn = QPushButton("＋  Add Assignment")
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

        assignments = self._service.get_assignments()
        if not assignments:
            empty = QLabel("No assignments yet.")
            empty.setProperty("class", "card-description")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, empty)
            return

        for assignment in assignments:
            row_frame = QFrame()
            row_frame.setProperty("class", "task-item")
            rl = QHBoxLayout(row_frame)
            rl.setContentsMargins(14, 10, 14, 10)
            t_lbl = QLabel(assignment.title)
            t_lbl.setProperty("class", "task-title")
            m_lbl = QLabel(f"{assignment.due_date or 'No due date'} • {assignment.status}")
            m_lbl.setProperty("class", "task-due")
            rl.addWidget(t_lbl)
            rl.addStretch()
            rl.addWidget(m_lbl)
            self._layout.insertWidget(self._layout.count() - 1, row_frame)

    def _open_create_dialog(self):
        courses = self._service.get_courses()
        if not courses:
            return
        dialog = AssignmentDialog(courses, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            assignment = dialog.get_assignment()
            if assignment:
                self._service.create_assignment(
                    course_id=assignment.course_id,
                    title=assignment.title,
                    due_date=assignment.due_date,
                    priority=assignment.priority,
                    description=assignment.description,
                    status=assignment.status,
                )
                self.refresh()
