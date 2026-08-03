from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QDialogButtonBox,
)

from database.models import Assignment


class AssignmentDialog(QDialog):
    """Modal dialog for creating an assignment."""

    def __init__(self, courses, parent=None):
        super().__init__(parent)
        self._courses = courses
        self.setWindowTitle("New Assignment")
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

        self._due_input = QLineEdit()
        self._due_input.setPlaceholderText("YYYY-MM-DD")
        self._due_input.setProperty("class", "form-input")

        self._priority_combo = QComboBox()
        self._priority_combo.setProperty("class", "form-combo")
        self._priority_combo.addItems(["High", "Medium", "Low"])

        self._status_combo = QComboBox()
        self._status_combo.setProperty("class", "form-combo")
        self._status_combo.addItems(["Pending", "In Progress", "Completed", "Overdue"])

        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Optional description")
        self._desc_input.setFixedHeight(80)
        self._desc_input.setProperty("class", "form-input")

        form.addRow("Course", self._course_combo)
        form.addRow("Title *", self._title_input)
        form.addRow("Due Date", self._due_input)
        form.addRow("Priority", self._priority_combo)
        form.addRow("Status", self._status_combo)
        form.addRow("Description", self._desc_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_assignment(self) -> Assignment | None:
        if self._course_combo.count() == 0:
            return None
        title = self._title_input.text().strip()
        if not title:
            return None
        course_index = self._course_combo.currentIndex()
        return Assignment(
            course_id=self._courses[course_index].id,
            title=title,
            description=self._desc_input.toPlainText().strip(),
            due_date=self._due_input.text().strip() or None,
            priority=self._priority_combo.currentText(),
            status=self._status_combo.currentText(),
        )
