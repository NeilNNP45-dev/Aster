from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QDialogButtonBox,
)

from database.models import DailyGoal


class GoalDialog(QDialog):
    """Modal dialog for creating a new daily goal/habit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Daily Goal")
        self.setMinimumWidth(360)
        self.setModal(True)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(10)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("e.g. Drink 2L of water")
        self._title_input.setProperty("class", "form-input")

        self._category_input = QLineEdit()
        self._category_input.setPlaceholderText("e.g. Health, Study, Fitness")
        self._category_input.setProperty("class", "form-input")

        self._reset_check = QCheckBox("Reset daily at midnight")
        self._reset_check.setChecked(True)

        form.addRow("Goal Title *", self._title_input)
        form.addRow("Category", self._category_input)
        form.addRow("", self._reset_check)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_goal(self) -> DailyGoal | None:
        """Return a DailyGoal dataclass built from dialog input, or None if invalid."""
        title = self._title_input.text().strip()
        if not title:
            return None
        return DailyGoal(
            title=title,
            category=self._category_input.text().strip() or "General",
            reset_daily=self._reset_check.isChecked(),
        )
