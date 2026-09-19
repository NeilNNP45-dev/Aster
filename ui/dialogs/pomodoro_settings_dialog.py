from PySide6.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLabel, QSpinBox, QVBoxLayout


class PomodoroSettingsDialog(QDialog):
    """Edit Pomodoro durations in minutes."""

    def __init__(self, durations, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pomodoro Settings")
        self.setMinimumWidth(360)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        description = QLabel(
            "Set the length of each session. Changes apply to the next session; "
            "an active or paused session keeps its current duration."
        )
        description.setWordWrap(True)
        description.setProperty("class", "card-description")
        layout.addWidget(description)

        form = QFormLayout()
        form.setSpacing(10)
        self._focus = self._duration_input(durations.focus_minutes)
        self._short_break = self._duration_input(durations.short_break_minutes)
        self._long_break = self._duration_input(durations.long_break_minutes)
        form.addRow("Focus / work (min)", self._focus)
        form.addRow("Short break (min)", self._short_break)
        form.addRow("Long break (min)", self._long_break)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _duration_input(value: int) -> QSpinBox:
        field = QSpinBox()
        field.setRange(1, 240)
        field.setValue(value)
        field.setSuffix(" min")
        return field

    def get_values(self) -> tuple[int, int, int]:
        return self._focus.value(), self._short_break.value(), self._long_break.value()
