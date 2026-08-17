from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QProgressBar,
    QComboBox,
    QScrollArea,
)
from services.analytics.analytics_service import AnalyticsService


class TrendsWidget(QWidget):
    """Visual Trends and Daily Focus breakdown widget."""

    PERIOD_MAP = {
        "This Week (Mon-Sun)": "this_week",
        "Last Week": "last_week",
        "Last 30 Days": "last_30_days",
    }

    def __init__(self, service: AnalyticsService, parent=None):
        super().__init__(parent)
        self.service = service
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Top controls
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("View Range:"))
        self.period_combo = QComboBox()
        self.period_combo.setProperty("class", "form-combo")
        self.period_combo.addItems(list(self.PERIOD_MAP.keys()))
        self.period_combo.currentTextChanged.connect(self.refresh)

        ctrl_row.addWidget(self.period_combo)
        ctrl_row.addStretch()
        layout.addLayout(ctrl_row)

        # Daily Focus Timeline Card
        self.timeline_card = QFrame()
        self.timeline_card.setProperty("class", "card")
        self.timeline_layout = QVBoxLayout(self.timeline_card)

        t_title = QLabel("📈 Daily Focus Breakdown (Pomodoro + Coding)")
        t_title.setProperty("class", "card-title")
        self.timeline_layout.addWidget(t_title)

        # Scrollable container for daily bars
        self.bars_container = QWidget()
        self.bars_layout = QVBoxLayout(self.bars_container)
        self.bars_layout.setSpacing(10)
        self.bars_layout.setContentsMargins(0, 8, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.bars_container)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.timeline_layout.addWidget(scroll)
        layout.addWidget(self.timeline_card, 1)

        self.refresh()

    def refresh(self):
        # Clear existing bars
        while self.bars_layout.count():
            item = self.bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        period_key = self.PERIOD_MAP.get(self.period_combo.currentText(), "this_week")
        daily_stats = self.service.get_daily_focus(period_key)

        if not daily_stats:
            no_data = QLabel("No daily focus entries found for this range.")
            no_data.setProperty("class", "card-description")
            self.bars_layout.addWidget(no_data)
            return

        # Find max minutes for scaling progress bar
        max_mins = max([s.total_minutes for s in daily_stats] + [60])  # Minimum 60 min scale

        for stat in daily_stats:
            dt = datetime.strptime(stat.date_str, "%Y-%m-%d")
            day_name = dt.strftime("%a (%b %d)")  # e.g., Mon (Aug 17)

            row_frame = QFrame()
            row_frame.setProperty("class", "trend-row")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(12, 10, 12, 10)
            row_layout.setSpacing(14)

            day_label = QLabel(day_name)
            day_label.setFixedWidth(110)
            day_label.setProperty("class", "card-title")

            pbar = QProgressBar()
            pbar.setProperty("class", "trend-progress")
            pbar.setRange(0, max_mins)
            pbar.setValue(stat.total_minutes)
            pbar.setTextVisible(False)
            pbar.setFixedHeight(14)

            # Details breakdown tag
            detail_parts = []
            if stat.pomodoro_minutes > 0:
                detail_parts.append(f"🍅 {stat.pomodoro_minutes}m")
            if stat.coding_minutes > 0:
                detail_parts.append(f"💻 {stat.coding_minutes}m")
            detail_str = "  ".join(detail_parts) if detail_parts else "0m"

            detail_label = QLabel(detail_str)
            detail_label.setFixedWidth(110)
            detail_label.setProperty("class", "card-description")

            total_label = QLabel(f"{stat.total_minutes} mins")
            total_label.setFixedWidth(70)
            total_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_label.setProperty("class", "card-title")

            row_layout.addWidget(day_label)
            row_layout.addWidget(pbar, 1)
            row_layout.addWidget(detail_label)
            row_layout.addWidget(total_label)

            self.bars_layout.addWidget(row_frame)

        self.bars_layout.addStretch()

