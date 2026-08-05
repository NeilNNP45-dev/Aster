from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QTextEdit, QDialogButtonBox

class SessionNoteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._notes = QTextEdit()
        self._notes.setProperty("class", "form-input")
        form.addRow("Notes", self._notes)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_notes(self) -> str:
        return self._notes.toPlainText().strip()
