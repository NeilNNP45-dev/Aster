from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDoubleSpinBox, QTextEdit, QDialogButtonBox


class WeightDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Log Weight")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._weight = QDoubleSpinBox()
        self._weight.setRange(20.0, 300.0)
        self._weight.setDecimals(1)
        self._weight.setValue(70.0)

        self._notes = QTextEdit()
        self._notes.setProperty("class", "form-input")
        self._notes.setFixedHeight(80)

        form.addRow("Weight (kg)", self._weight)
        form.addRow("Notes", self._notes)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_weight(self):
        return {
            "weight_kg": self._weight.value(),
            "note": self._notes.toPlainText().strip(),
        }
