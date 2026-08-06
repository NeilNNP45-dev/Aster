from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QSpinBox, QTextEdit, QDialogButtonBox


class FitnessLogDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Workout")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._title = QLineEdit()
        self._title.setProperty("class", "form-input")
        self._title.setPlaceholderText("e.g. Morning run")

        self._type = QLineEdit()
        self._type.setProperty("class", "form-input")
        self._type.setPlaceholderText("e.g. Cardio")

        self._duration = QSpinBox()
        self._duration.setRange(0, 600)
        self._duration.setValue(30)

        self._calories = QSpinBox()
        self._calories.setRange(0, 5000)
        self._calories.setValue(0)

        self._notes = QTextEdit()
        self._notes.setProperty("class", "form-input")
        self._notes.setFixedHeight(90)

        form.addRow("Title", self._title)
        form.addRow("Type", self._type)
        form.addRow("Duration (min)", self._duration)
        form.addRow("Calories", self._calories)
        form.addRow("Notes", self._notes)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_workout(self):
        title = self._title.text().strip()
        if not title:
            return None
        return {
            "title": title,
            "workout_type": self._type.text().strip() or "Workout",
            "duration_minutes": self._duration.value(),
            "calories": self._calories.value(),
            "notes": self._notes.toPlainText().strip(),
        }
