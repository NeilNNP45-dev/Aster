from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
from PySide6.QtWidgets import QDialog
from ui.dialogs.goal_dialog import GoalDialog


class CodingGoalsWidget(QWidget):
    def __init__(self, services, parent=None):
        super().__init__(parent)
        self._services = services
        self._goals_service = services.get("goals_service")
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Coding Goals")
        title.setProperty("class", "card-title")
        layout.addWidget(title)
        self._list = QListWidget()
        self._list.setProperty("class", "note-list")
        layout.addWidget(self._list)
        add_btn = QPushButton("＋ Add Goal")
        add_btn.setProperty("class", "primary-btn")
        add_btn.clicked.connect(self._on_add)
        layout.addWidget(add_btn)
        self.refresh()

    def refresh(self):
        self._list.clear()
        goals = self._goals_service.list_goals()
        for g in goals:
            item = QListWidgetItem(f"{g.title} {'✓' if g.is_completed else ''}")
            item.setData(1, g.id)
            self._list.addItem(item)

    def _on_add(self):
        from ui.dialogs.goal_dialog import GoalDialog

        dlg = GoalDialog(
            self,
            dialog_title="New Coding Goal",
            title_placeholder="e.g. Solve two algorithm problems",
            category_placeholder="e.g. Algorithms, Project, Refactor",
            reset_label="Reset daily (if applicable)",
        )
        if dlg.exec() == QDialog.Accepted:
            daily = dlg.get_goal()
            if daily:
                from database.models import CodingGoal

                cg = CodingGoal(title=daily.title, reset_daily=daily.reset_daily)
                self._goals_service.add_goal(cg)
                self.refresh()
