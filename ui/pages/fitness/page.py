from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QDialog

from database.connection import DatabaseConnection
from services.fitness.fitness_service import FitnessService
from ui.dialogs.fitness_log_dialog import FitnessLogDialog
from ui.dialogs.weight_dialog import WeightDialog
from ui.pages.fitness.widgets import FitnessSummaryWidget, WorkoutListWidget, WeightListWidget


class FitnessPage(QWidget):
    """Fitness dashboard with workout and weight tracking."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FitnessPage")
        self._db = DatabaseConnection()
        self._service = FitnessService(db_conn=self._db)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Fitness & Health")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Workout logging, body weight tracking, and progress snapshots")
        subtitle.setProperty("class", "page-subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        workout_btn = QPushButton("Log Workout")
        workout_btn.setProperty("class", "primary-btn")
        workout_btn.clicked.connect(self._on_log_workout)
        weight_btn = QPushButton("Log Weight")
        weight_btn.setProperty("class", "secondary-btn")
        weight_btn.clicked.connect(self._on_log_weight)
        actions.addWidget(workout_btn)
        actions.addWidget(weight_btn)
        actions.addStretch()
        layout.addLayout(actions)

        summary_card = QFrame()
        summary_card.setProperty("class", "card")
        summary_layout = QVBoxLayout(summary_card)
        self._summary = FitnessSummaryWidget(self._service)
        summary_layout.addWidget(self._summary)
        layout.addWidget(summary_card)

        content_row = QHBoxLayout()
        content_row.setSpacing(16)
        workouts_card = QFrame()
        workouts_card.setProperty("class", "card")
        workouts_layout = QVBoxLayout(workouts_card)
        self._workouts = WorkoutListWidget(self._service)
        workouts_layout.addWidget(self._workouts)

        weights_card = QFrame()
        weights_card.setProperty("class", "card")
        weights_layout = QVBoxLayout(weights_card)
        self._weights = WeightListWidget(self._service)
        weights_layout.addWidget(self._weights)

        content_row.addWidget(workouts_card, 1)
        content_row.addWidget(weights_card, 1)
        layout.addLayout(content_row)
        layout.addStretch()

    def _on_log_workout(self):
        dlg = FitnessLogDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_workout()
            if data:
                self._service.log_workout(
                    title=data["title"],
                    workout_type=data["workout_type"],
                    duration_minutes=data["duration_minutes"],
                    calories=data["calories"],
                    notes=data["notes"],
                )
                self._workouts.refresh()

    def _on_log_weight(self):
        dlg = WeightDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_weight()
            if data:
                self._service.log_weight(weight_kg=data["weight_kg"], note=data["note"])
                self._weights.refresh()
                self._summary.refresh()
