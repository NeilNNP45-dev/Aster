from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDialogButtonBox,
)

from database.models import Task


class TaskDialog(QDialog):
    """Modal dialog for creating or editing a task."""

    def __init__(self, parent=None, task: Task | None = None):
        super().__init__(parent)
        self._task = task
        self.setWindowTitle("Edit Task" if task else "New Task")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        description = QLabel(
            "Create a finite, one-time outcome. Examples: “Submit assignment” or “Finish Chapter 3”."
        )
        description.setWordWrap(True)
        description.setProperty("class", "card-description")
        layout.addWidget(description)

        form = QFormLayout()
        form.setSpacing(10)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("e.g. Submit assignment")
        self._title_input.setProperty("class", "form-input")

        self._desc_input = QTextEdit()
        self._desc_input.setPlaceholderText("Description (optional)…")
        self._desc_input.setFixedHeight(80)
        self._desc_input.setProperty("class", "form-input")

        self._priority_combo = QComboBox()
        self._priority_combo.addItems(["High", "Medium", "Low"])
        self._priority_combo.setCurrentIndex(1)
        self._priority_combo.setProperty("class", "form-combo")

        self._category_input = QLineEdit()
        self._category_input.setPlaceholderText("e.g. Work, Study, Personal")
        self._category_input.setProperty("class", "form-input")

        self._due_date_input = QLineEdit()
        self._due_date_input.setPlaceholderText("YYYY-MM-DD (optional)")
        self._due_date_input.setProperty("class", "form-input")

        form.addRow("Title *", self._title_input)
        form.addRow("Description", self._desc_input)
        form.addRow("Priority", self._priority_combo)
        form.addRow("Category", self._category_input)
        form.addRow("Due Date", self._due_date_input)
        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if self._task:
            self._title_input.setText(self._task.title or "")
            self._desc_input.setPlainText(self._task.description or "")
            priority_index = self._priority_combo.findText(self._task.priority or "Medium")
            self._priority_combo.setCurrentIndex(priority_index if priority_index >= 0 else 1)
            self._category_input.setText(self._task.category or "")
            self._due_date_input.setText(self._task.due_date or "")

    def get_task(self) -> Task | None:
        """Return a Task dataclass built from dialog input, or None if invalid."""
        title = self._title_input.text().strip()
        if not title:
            return None
        return Task(
            id=self._task.id if self._task else None,
            title=title,
            description=self._desc_input.toPlainText().strip(),
            priority=self._priority_combo.currentText(),
            category=self._category_input.text().strip() or "General",
            due_date=self._due_date_input.text().strip() or None,
            is_completed=self._task.is_completed if self._task else False,
            created_at=self._task.created_at if self._task else None,
        )
