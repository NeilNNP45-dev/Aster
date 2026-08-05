from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox

class ProjectDialog(QDialog):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self._project = project
        self.setWindowTitle("New Coding Project")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._name = QLineEdit()
        self._name.setProperty("class", "form-input")
        self._name.setPlaceholderText("e.g. Project Tracker")
        self._repo_path = QLineEdit()
        self._repo_path.setProperty("class", "form-input")
        self._repo_path.setPlaceholderText("e.g. C:/Users/you/code/project")
        self._github = QLineEdit()
        self._github.setProperty("class", "form-input")
        self._github.setPlaceholderText("e.g. owner/repo")
        form.addRow("Name", self._name)
        form.addRow("Repo Path", self._repo_path)
        form.addRow("GitHub (owner/repo)", self._github)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_project(self):
        if not self._name.text().strip():
            return None
        from database.models import CodingProject

        return CodingProject(name=self._name.text().strip(), repo_path=self._repo_path.text().strip(), github_full_name=self._github.text().strip() or None)
