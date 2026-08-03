from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QButtonGroup, QStackedWidget,
)

from database.connection import DatabaseConnection
from services.college.college_service import CollegeService
from ui.pages.college.courses_widget import CoursesWidget
from ui.pages.college.timetable_widget import TimetableWidget
from ui.pages.college.attendance_widget import AttendanceWidget
from ui.pages.college.assignments_widget import AssignmentsWidget
from ui.pages.college.exams_widget import ExamsWidget


class CollegePage(QWidget):
    """College & Academics page with simple CRUD-oriented sub-views."""

    _TABS = ["📚  Courses", "🗓️  Timetable", "✅  Attendance", "📝  Assignments", "🧪  Exams"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CollegePage")

        self._db = DatabaseConnection()
        self._service = CollegeService(db_conn=self._db)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("College & Academics")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Manage your courses, schedule, attendance, tasks, and exams")
        subtitle.setProperty("class", "page-subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        tab_row = QHBoxLayout()
        tab_row.setSpacing(6)
        self._tab_group = QButtonGroup(self)
        self._tab_group.setExclusive(True)

        for i, label in enumerate(self._TABS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "pill-tab")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._tab_group.addButton(btn, i)
            tab_row.addWidget(btn)

        self._tab_group.button(0).setChecked(True)
        tab_row.addStretch()
        layout.addLayout(tab_row)

        self._stack = QStackedWidget()
        self._courses_view = CoursesWidget(self._service)
        self._timetable_view = TimetableWidget(self._service)
        self._attendance_view = AttendanceWidget(self._service)
        self._assignments_view = AssignmentsWidget(self._service)
        self._exams_view = ExamsWidget(self._service)

        self._stack.addWidget(self._courses_view)
        self._stack.addWidget(self._timetable_view)
        self._stack.addWidget(self._attendance_view)
        self._stack.addWidget(self._assignments_view)
        self._stack.addWidget(self._exams_view)

        self._tab_group.idClicked.connect(self._stack.setCurrentIndex)

        layout.addWidget(self._stack, 1)
