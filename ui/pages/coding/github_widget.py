from urllib.parse import urlparse
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QInputDialog
import webbrowser


class GitHubWidget(QWidget):
    def __init__(self, services, parent=None):
        super().__init__(parent)
        self._services = services
        self._repo = services.get("repo")
        self._github_service = services.get("github_service")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("GitHub Integration")
        title.setProperty("class", "card-title")
        layout.addWidget(title)
        self._project_combo = QComboBox()
        self._project_combo.setProperty("class", "form-combo")
        layout.addWidget(self._project_combo)
        self._github_label = QLabel("GitHub repo identifier")
        self._github_label.setProperty("class", "card-description")
        layout.addWidget(self._github_label)
        self._github_input = QLineEdit()
        self._github_input.setProperty("class", "form-input")
        self._github_input.setPlaceholderText("owner/repo or GitHub URL")
        layout.addWidget(self._github_input)
        self._hint = QLabel(
            "Tip: leave blank to reuse the saved project repo, or enter a new GitHub URL/owner-repo.")
        self._hint.setProperty("class", "card-description")
        self._hint.setWordWrap(True)
        layout.addWidget(self._hint)
        self._desc = QLabel("")
        self._desc.setWordWrap(True)
        self._desc.setProperty("class", "card-description")
        layout.addWidget(self._desc)
        self._sync_btn = QPushButton("Sync Selected Project")
        self._sync_btn.setProperty("class", "primary-btn")
        self._sync_btn.clicked.connect(self._on_sync)
        layout.addWidget(self._sync_btn)
        self._open_btn = QPushButton("Open Repository")
        self._open_btn.setProperty("class", "secondary-btn")
        self._open_btn.clicked.connect(self._on_open)
        self._open_btn.setEnabled(False)
        layout.addWidget(self._open_btn)
        self._status = QLabel("")
        self._status.setProperty("class", "status-badge")
        layout.addWidget(self._status)
        self.refresh()

        # update selected project preview when selection changes
        self._project_combo.currentIndexChanged.connect(self._on_selection_changed)
        self._project_combo.currentIndexChanged.connect(self._sync_input_with_selection)

    @staticmethod
    def _is_valid_github_url(url: str) -> bool:
        if not url:
            return False
        try:
            parsed = urlparse(url.strip())
            return parsed.scheme.lower() == "https" and (parsed.hostname or "").lower() == "github.com"
        except Exception:
            return False

    def refresh(self):
        self._project_combo.clear()
        if not self._repo:
            return
        projects = self._repo.list_projects()
        for p in projects:
            display = p.name
            if p.github_full_name:
                display += f" — {p.github_full_name}"
            self._project_combo.addItem(display, p.id)

    def _on_sync(self):
        project_id = self._project_combo.currentData()
        if project_id is None:
            self._status.setText("No project selected")
            return
        token, ok = QInputDialog.getText(
            self,
            "GitHub Token (optional)",
            "Personal Access Token (leave blank for unauthenticated):",
            QLineEdit.Password,
        )
        if not ok:
            return
        token = token.strip() or None
        if not self._github_service:
            # try to construct one from repo
            from services.coding.github_service import GitHubService

            self._github_service = GitHubService(repo=self._repo)

        # find project's current full name; if missing ask user
        proj_list = self._repo.list_projects()
        target = next((p for p in proj_list if p.id == project_id), None)
        if not target:
            self._status.setText("Project not found")
            return

        full_name = self._github_input.text().strip() or target.github_full_name
        if not full_name:
            full_name, ok2 = QInputDialog.getText(
                self,
                "Repository Full Name",
                "Enter GitHub repository identifier (owner/repo or URL):",
            )
            if not ok2 or not full_name.strip():
                self._status.setText("No repository specified")
                return
            full_name = full_name.strip()

        ok_sync = self._github_service.sync_project_metadata(project_id, full_name, token)
        if ok_sync:
            self._status.setText("Sync successful")
        else:
            self._status.setText(
                "Sync failed: use a valid owner/repo identifier or URL, and optionally provide a PAT if rate-limited"
            )
        if ok_sync:
            self.refresh()
            # after refresh, enable open button if url exists
            proj = next((p for p in self._repo.list_projects() if p.id == project_id), None)
            if proj and self._is_valid_github_url(proj.github_html_url):
                self._open_btn.setEnabled(True)
                self._desc.setText(proj.description or "")

    def _on_open(self):
        project_id = self._project_combo.currentData()
        if project_id is None:
            return
        proj = next((p for p in self._repo.list_projects() if p.id == project_id), None)
        if proj and proj.github_html_url:
            url = proj.github_html_url.strip()
            if self._is_valid_github_url(url):
                webbrowser.open(url)
            else:
                self._status.setText("Invalid or unsupported repository URL")

    def _sync_input_with_selection(self, idx: int):
        project_id = self._project_combo.currentData()
        if project_id is None:
            self._github_input.clear()
            return
        proj = next((p for p in self._repo.list_projects() if p.id == project_id), None)
        if proj and proj.github_full_name:
            self._github_input.setText(proj.github_full_name)
        else:
            self._github_input.clear()

    def _on_selection_changed(self, idx: int):
        project_id = self._project_combo.currentData()
        if project_id is None:
            self._open_btn.setEnabled(False)
            self._desc.setText("")
            return
        proj = next((p for p in self._repo.list_projects() if p.id == project_id), None)
        if proj:
            self._desc.setText(proj.description or "")
            self._open_btn.setEnabled(self._is_valid_github_url(proj.github_html_url))
        else:
            self._open_btn.setEnabled(False)
            self._desc.setText("")

