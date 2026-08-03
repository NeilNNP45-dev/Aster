from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QDialogButtonBox,
)

from database.models import Exam


class ExamDialog(QDialog):
    """Modal dialog for creating an exam."""

    def __init__(self, courses, parent=None):
        super().__init__(parent)
        self._courses = courses
        self.setWindowTitle("New Exam")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(10)

        self._course_combo = QComboBox()
        self._course_combo.setProperty("class", "form-combo")
        self._course_combo.addItems([course.name for course in self._courses])

        self._title_input = QLineEdit()
        self._title_input.setProperty("class", "form-input")

        self._type_input = QLineEdit()
        self._type_input.setText("Exam")
        self._type_input.setProperty("class", "form-input")

        self._scheduled_input = QLineEdit()
        self._scheduled_input.setPlaceholderText("YYYY-MM-DD HH:MM")
        self._scheduled_input.setProperty("class", "form-input")

        self._location_input = QLineEdit()
        self._location_input.setPlaceholderText("Location")
        self._location_input.setProperty("class", "form-input")

        self._status_combo = QComboBox()
        self._status_combo.setProperty("class", "form-combo")
        self._status_combo.addItems(["Planned", "Upcoming", "Completed", "Canceled"])

        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Optional notes")
        self._notes_input.setFixedHeight(80)
        self._notes_input.setProperty("class", "form-input")

        form.addRow("Course", self._course_combo)
        form.addRow("Title *", self._title_input)
        form.addRow("Exam Type", self._type_input)
        form.addRow("Scheduled At", self._scheduled_input)
        form.addRow("Location", self._location_input)
        form.addRow("Status", self._status_combo)
        form.addRow("Notes", self._notes_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_exam(self) -> Exam | None:
        if self._course_combo.count() == 0:
            return None
        title = self._title_input.text().strip()
        if not title:
            return None
        course_index = self._course_combo.currentIndex()
        return Exam(
            course_id=self._courses[course_index].id,
            title=title,
            exam_type=self._type_input.text().strip() or "Exam",
            scheduled_at=self._scheduled_input.text().strip() or "",
            location=self._location_input.text().strip(),
            status=self._status_combo.currentText(),
            notes=self._notes_input.toPlainText().strip(),
        )
