from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFrame, QSizePolicy, QScrollArea,
)

from database.models import Task
from database.repositories.productivity_repository import ProductivityRepository


class TaskItemWidget(QFrame):
    """A single task row inside the task list."""

    toggled = Signal(int)   # task_id
    deleted = Signal(int)   # task_id

    PRIORITY_COLORS = {
        "High": "#EF4444",
        "Medium": "#F59E0B",
        "Low":  "#22C55E",
    }

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self.setProperty("class", "task-item")
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)

        # Checkbox toggle button
        self.check_btn = QPushButton("✓" if self.task.is_completed else "")
        self.check_btn.setFixedSize(24, 24)
        self.check_btn.setProperty("class", "task-check-btn")
        if self.task.is_completed:
            self.check_btn.setProperty("class", "task-check-btn completed")
        self.check_btn.clicked.connect(lambda: self.toggled.emit(self.task.id))

        # Priority dot
        color = self.PRIORITY_COLORS.get(self.task.priority, "#9CA3AF")
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 12px;")
        dot.setFixedWidth(18)

        # Title
        title_lbl = QLabel(self.task.title)
        title_lbl.setProperty("class", "task-title")
        if self.task.is_completed:
            title_lbl.setStyleSheet("text-decoration: line-through; color: #6B7280;")
        title_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Due date (if any)
        if self.task.due_date:
            due_lbl = QLabel(f"📅 {self.task.due_date}")
            due_lbl.setProperty("class", "task-due")
            layout.addWidget(due_lbl)

        # Delete button
        del_btn = QPushButton("✕")
        del_btn.setFixedSize(22, 22)
        del_btn.setProperty("class", "task-delete-btn")
        del_btn.clicked.connect(lambda: self.deleted.emit(self.task.id))

        layout.addWidget(self.check_btn)
        layout.addWidget(dot)
        layout.addWidget(title_lbl)
        if self.task.due_date:
            due_lbl = QLabel(f"📅 {self.task.due_date}")
            due_lbl.setProperty("class", "task-due")
            layout.addWidget(due_lbl)
        layout.addWidget(del_btn)


class TasksWidget(QWidget):
    """Full Tasks sub-view with filter tabs, task list, and add button."""

    def __init__(self, repo: ProductivityRepository, parent=None):
        super().__init__(parent)
        self._repo = repo
        self._filter = "All"   # "All", "Active", "Completed"
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Filter row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        self._filter_btns = {}
        for label in ("All", "Active", "Completed"):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "pill-tab")
            btn.clicked.connect(lambda _, l=label: self._set_filter(l))
            self._filter_btns[label] = btn
            filter_row.addWidget(btn)
        self._filter_btns["All"].setChecked(True)
        filter_row.addStretch()

        # Add Task button
        self.add_btn = QPushButton("＋  Add Task")
        self.add_btn.setProperty("class", "primary-btn")
        filter_row.addWidget(self.add_btn)
        layout.addLayout(filter_row)

        # Task scroll list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()

        scroll.setWidget(self._list_container)
        layout.addWidget(scroll, 1)

    def _set_filter(self, label: str):
        self._filter = label
        for name, btn in self._filter_btns.items():
            btn.setChecked(name == label)
        self.refresh()

    def refresh(self):
        """Clear and reload task list from database based on active filter."""
        # Remove all existing task widgets (but keep the stretch at end)
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = self._repo.get_all_tasks()
        if self._filter == "Active":
            tasks = [t for t in tasks if not t.is_completed]
        elif self._filter == "Completed":
            tasks = [t for t in tasks if t.is_completed]

        if not tasks:
            empty_lbl = QLabel("No tasks to show. Click '＋ Add Task' to get started.")
            empty_lbl.setProperty("class", "card-description")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.insertWidget(0, empty_lbl)
            return

        for task in tasks:
            widget = TaskItemWidget(task)
            widget.toggled.connect(self._on_toggle)
            widget.deleted.connect(self._on_delete)
            self._list_layout.insertWidget(self._list_layout.count() - 1, widget)

    def _on_toggle(self, task_id: int):
        self._repo.toggle_task_completion(task_id)
        self.refresh()

    def _on_delete(self, task_id: int):
        self._repo.delete_task(task_id)
        self.refresh()
