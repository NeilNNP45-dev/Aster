from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QDialogButtonBox,
)

from database.models import TimetableEntry


class TimetableDialog(QDialog):
    """Modal dialog for creating a timetable entry."""

    def __init__(self, courses, parent=None):
        super().__init__(parent)
        self._courses = courses
        self.setWindowTitle("New Timetable Entry")
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

        self._day_combo = QComboBox()
        self._day_combo.setProperty("class", "form-combo")
        self._day_combo.addItems(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

        self._start_input = QLineEdit()
        self._start_input.setPlaceholderText("09:00")
        self._start_input.setProperty("class", "form-input")

        self._end_input = QLineEdit()
        self._end_input.setPlaceholderText("10:00")
        self._end_input.setProperty("class", "form-input")

        self._room_input = QLineEdit()
        self._room_input.setPlaceholderText("Room")
        self._room_input.setProperty("class", "form-input")

        self._location_input = QLineEdit()
        self._location_input.setPlaceholderText("Location")
        self._location_input.setProperty("class", "form-input")

        self._recurring_check = QCheckBox("Recurring")
        self._recurring_check.setChecked(True)

        form.addRow("Course", self._course_combo)
        form.addRow("Day", self._day_combo)
        form.addRow("Start Time", self._start_input)
        form.addRow("End Time", self._end_input)
        form.addRow("Room", self._room_input)
        form.addRow("Location", self._location_input)
        form.addRow("", self._recurring_check)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_timetable_entry(self) -> TimetableEntry | None:
        if self._course_combo.count() == 0:
            return None
        course_index = self._course_combo.currentIndex()
        return TimetableEntry(
            course_id=self._courses[course_index].id,
            day_of_week=self._day_combo.currentText(),
            start_time=self._start_input.text().strip() or "09:00",
            end_time=self._end_input.text().strip() or "10:00",
            room=self._room_input.text().strip(),
            location=self._location_input.text().strip(),
            recurring=self._recurring_check.isChecked(),
        )
