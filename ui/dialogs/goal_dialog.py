from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QDialogButtonBox,
)

from database.models import DailyGoal


class GoalDialog(QDialog):
    """Modal dialog for creating a new daily goal/habit.

    Accepts optional overrides so the same dialog can be reused for coding goals.
    """

    def __init__(
        self,
        parent=None,
        dialog_title: str = "New Daily Goal",
        title_placeholder: str = "e.g. Drink 2L of water",
        category_placeholder: str = "e.g. Health, Study, Fitness",
        reset_label: str = "Reset daily at midnight",
    ):
        super().__init__(parent)
        self.setWindowTitle(dialog_title)
        self.setMinimumWidth(360)
        self.setModal(True)
        self._dialog_title = dialog_title
        self._title_placeholder = title_placeholder
        self._category_placeholder = category_placeholder
        self._reset_label = reset_label
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        form = QFormLayout()
        form.setSpacing(10)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText(self._title_placeholder)
        self._title_input.setProperty("class", "form-input")

        self._category_input = QLineEdit()
        self._category_input.setPlaceholderText(self._category_placeholder)
        self._category_input.setProperty("class", "form-input")

        self._reset_check = QCheckBox(self._reset_label)
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
