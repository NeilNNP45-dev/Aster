from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox

class ProjectDialog(QDialog):
    def __init__(self, project=None, parent=None):
        super().__init__(parent)
        self._project = project
        self.setWindowTitle("Edit Coding Project" if project else "New Coding Project")
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

        if self._project:
            self._name.setText(self._project.name or "")
            self._repo_path.setText(self._project.repo_path or "")
            self._github.setText(self._project.github_full_name or "")

    def get_project(self):
        if not self._name.text().strip():
            return None
        from database.models import CodingProject

        return CodingProject(
            id=self._project.id if self._project else None,
            name=self._name.text().strip(),
            repo_path=self._repo_path.text().strip(),
            github_full_name=self._github.text().strip() or None,
            github_html_url=self._project.github_html_url if self._project else None,
            description=self._project.description if self._project else "",
            language=self._project.language if self._project else "",
            is_active=self._project.is_active if self._project else True,
            created_at=self._project.created_at if self._project else None,
            updated_at=self._project.updated_at if self._project else None,
        )
