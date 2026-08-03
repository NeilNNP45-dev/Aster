from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QSpinBox, QTextEdit, QDialogButtonBox,
)

from database.models import Course


class CourseDialog(QDialog):
    """Modal dialog for creating or editing a course."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Course")
        self.setMinimumWidth(420)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(10)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("e.g. Data Structures")
        self._name_input.setProperty("class", "form-input")

        self._code_input = QLineEdit()
        self._code_input.setPlaceholderText("e.g. CS201")
        self._code_input.setProperty("class", "form-input")

        self._instructor_input = QLineEdit()
        self._instructor_input.setPlaceholderText("Instructor name")
        self._instructor_input.setProperty("class", "form-input")

        self._credit_input = QSpinBox()
        self._credit_input.setRange(0, 10)
        self._credit_input.setValue(3)

        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Optional description")
        self._desc_input.setFixedHeight(80)
        self._desc_input.setProperty("class", "form-input")

        form.addRow("Course Name *", self._name_input)
        form.addRow("Course Code", self._code_input)
        form.addRow("Instructor", self._instructor_input)
        form.addRow("Credit Hours", self._credit_input)
        form.addRow("Description", self._desc_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_course(self) -> Course | None:
        title = self._name_input.text().strip()
        if not title:
            return None
        return Course(
            name=title,
            code=self._code_input.text().strip(),
            instructor_name=self._instructor_input.text().strip(),
            credit_hours=self._credit_input.value(),
            description=self._desc_input.toPlainText().strip(),
        )
