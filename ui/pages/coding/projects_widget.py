from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem

from PySide6.QtWidgets import QDialog
from ui.dialogs.project_dialog import ProjectDialog


class ProjectsWidget(QWidget):
    project_added = Signal()
    def __init__(self, services, parent=None):
        super().__init__(parent)
        self._services = services
        self._repo = services.get("repo")
        self._project_service = services.get("project_service")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Projects")
        title.setProperty("class", "card-title")
        layout.addWidget(title)
        self._list = QListWidget()
        self._list.setProperty("class", "note-list")
        layout.addWidget(self._list)
        add_btn = QPushButton("＋ Add Project")
        add_btn.setProperty("class", "primary-btn")
        add_btn.clicked.connect(self._on_add)
        layout.addWidget(add_btn)
        self.refresh()

    def refresh(self):
        self._list.clear()
        projects = self._project_service.list_projects()
        for p in projects:
            item = QListWidgetItem(f"{p.name} ({p.language})")
            item.setData(1, p.id)
            self._list.addItem(item)

    def _on_add(self):
        dlg = ProjectDialog(self)
        if dlg.exec() == QDialog.Accepted:
            proj = dlg.get_project()
            if proj:
                # map dialog -> CodingProject
                from database.models import CodingProject

                cp = CodingProject(name=proj.name, repo_path=proj.repo_path, github_full_name=proj.github_full_name)
                self._project_service.add_project(cp)
                self.refresh()
                self.project_added.emit()
