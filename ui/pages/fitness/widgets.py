from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QFrame


class FitnessSummaryWidget(QWidget):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        title = QLabel("Fitness Summary")
        title.setProperty("class", "card-title")
        layout.addWidget(title)

        self._summary = QLabel("")
        self._summary.setProperty("class", "card-description")
        self._summary.setWordWrap(True)
        layout.addWidget(self._summary)
        self.refresh()

    def refresh(self):
        latest_weight = self._service.get_latest_weight()
        trend = self._service.get_weight_trend()
        if latest_weight and trend:
            self._summary.setText(
                f"Latest weight: {latest_weight.weight_kg:.1f} kg\n"
                f"Trend: {trend['trend']} ({trend['delta']:+.1f} kg from previous entry)"
            )
        elif latest_weight:
            self._summary.setText(f"Latest weight: {latest_weight.weight_kg:.1f} kg")
        else:
            self._summary.setText("No weight logs yet.")


class WorkoutListWidget(QWidget):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Recent Workouts")
        title.setProperty("class", "card-title")
        layout.addWidget(title)
        self._list = QListWidget()
        self._list.setProperty("class", "note-list")
        layout.addWidget(self._list)
        self.refresh()

    def refresh(self):
        self._list.clear()
        workouts = self._service.list_workouts()
        for workout in workouts:
            text = f"{workout.title} • {workout.workout_type} • {workout.duration_minutes} min"
            item = QListWidgetItem(text)
            item.setData(1, workout.id)
            self._list.addItem(item)


class WeightListWidget(QWidget):
    def __init__(self, service, parent=None):
        super().__init__(parent)
        self._service = service
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        title = QLabel("Weight Log")
        title.setProperty("class", "card-title")
        layout.addWidget(title)
        self._list = QListWidget()
        self._list.setProperty("class", "note-list")
        layout.addWidget(self._list)
        self.refresh()

    def refresh(self):
        self._list.clear()
        weights = self._service.list_weights()
        for entry in weights:
            text = f"{entry.weight_kg:.1f} kg • {entry.recorded_at or 'Unknown date'}"
            item = QListWidgetItem(text)
            item.setData(1, entry.id)
            self._list.addItem(item)
