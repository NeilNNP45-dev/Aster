from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy,
)

from database.models import Course
from services.college.college_service import CollegeService
from ui.dialogs.course_dialog import CourseDialog


class CourseItemWidget(QFrame):
    def __init__(self, course: Course, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.course = course
        self._on_edit = on_edit
        self._on_delete = on_delete
        self.setProperty("class", "task-item")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        title_lbl = QLabel(self.course.name)
        title_lbl.setProperty("class", "task-title")
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        meta_lbl = QLabel(f"{self.course.code or 'No code'} • {self.course.credit_hours} cr")
        meta_lbl.setProperty("class", "task-due")

        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(24, 24)
        edit_btn.setProperty("class", "task-delete-btn")
        edit_btn.clicked.connect(lambda: self._on_edit(self.course))

        del_btn = QPushButton("✕")
        del_btn.setFixedSize(24, 24)
        del_btn.setProperty("class", "task-delete-btn")
        del_btn.clicked.connect(lambda: self._on_delete(self.course.id))

        layout.addWidget(title_lbl)
        layout.addWidget(meta_lbl)
        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)


class CoursesWidget(QWidget):
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
        self.add_btn = QPushButton("＋  Add Course")
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
            empty = QLabel("No courses yet. Add your first course to get started.")
            empty.setProperty("class", "card-description")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.insertWidget(0, empty)
            return

        for course in courses:
            widget = CourseItemWidget(course, self._on_edit, self._on_delete)
            self._layout.insertWidget(self._layout.count() - 1, widget)

    def _open_create_dialog(self):
        dialog = CourseDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            course = dialog.get_course()
            if course:
                self._service.create_course(
                    name=course.name,
                    code=course.code,
                    instructor_name=course.instructor_name,
                    credit_hours=course.credit_hours,
                    description=course.description,
                )
                self.refresh()

    def _on_edit(self, course: Course):
        pass

    def _on_delete(self, course_id):
        if course_id is not None:
            self._service.delete_course(course_id)
            self.refresh()
