from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QDialogButtonBox,
)

from database.models import AttendanceLog


class AttendanceDialog(QDialog):
    """Modal dialog for recording attendance."""

    def __init__(self, courses, parent=None):
        super().__init__(parent)
        self._courses = courses
        self.setWindowTitle("Record Attendance")
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

        self._date_input = QLineEdit()
        self._date_input.setPlaceholderText("YYYY-MM-DD")
        self._date_input.setProperty("class", "form-input")

        self._status_combo = QComboBox()
        self._status_combo.setProperty("class", "form-combo")
        self._status_combo.addItems(["Present", "Absent", "Late", "Excused"])

        self._notes_input = QTextEdit()
        self._notes_input.setPlaceholderText("Optional notes")
        self._notes_input.setFixedHeight(80)
        self._notes_input.setProperty("class", "form-input")

        form.addRow("Course", self._course_combo)
        form.addRow("Date", self._date_input)
        form.addRow("Status", self._status_combo)
        form.addRow("Notes", self._notes_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_attendance(self) -> AttendanceLog | None:
        if self._course_combo.count() == 0:
            return None
        course_index = self._course_combo.currentIndex()
        return AttendanceLog(
            course_id=self._courses[course_index].id,
            attendance_date=self._date_input.text().strip() or "",
            status=self._status_combo.currentText(),
            notes=self._notes_input.toPlainText().strip(),
        )
