from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QButtonGroup,
)

from database.connection import DatabaseConnection
from database.repositories.analytics_repository import AnalyticsRepository
from services.analytics.analytics_service import AnalyticsService
from ui.pages.analytics.overview_widget import OverviewWidget
from ui.pages.analytics.trends_widget import TrendsWidget
from ui.pages.analytics.reports_widget import ReportsWidget


class AnalyticsPage(QWidget):
    """
    Analytics & Reports feature page:
      0 – Overview (Multi-domain summary cards)
      1 – Trends & Charts (Daily focus timeline)
      2 – Weekly & Monthly Reports (Structured report generator)
    """

    _TABS = ["📊  Overview", "📈  Trends & Charts", "📅  Reports"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnalyticsPage")

        self._db = DatabaseConnection()
        self._repo = AnalyticsRepository(db_conn=self._db)
        self._service = AnalyticsService(repo=self._repo)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        title = QLabel("Analytics & Insights 📊")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Personalized insights, focus trends, and activity reports across all domains")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Pill Sub-Tab Navigation
        tab_row = QHBoxLayout()
        tab_row.setSpacing(6)
        self._tab_group = QButtonGroup(self)
        self._tab_group.setExclusive(True)

        for i, label in enumerate(self._TABS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("class", "pill-tab")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self._tab_group.addButton(btn, i)
            tab_row.addWidget(btn)

        self._tab_group.button(0).setChecked(True)
        tab_row.addStretch()
        layout.addLayout(tab_row)

        # Sub-view Stacked Widget
        self._stack = QStackedWidget()

        self._overview_view = OverviewWidget(self._service)
        self._trends_view = TrendsWidget(self._service)
        self._reports_view = ReportsWidget(self._service)

        self._stack.addWidget(self._overview_view)  # 0
        self._stack.addWidget(self._trends_view)    # 1
        self._stack.addWidget(self._reports_view)   # 2

        self._tab_group.idClicked.connect(self._on_tab_changed)
        layout.addWidget(self._stack, 1)

    def _on_tab_changed(self, index: int):
        self._stack.setCurrentIndex(index)
        current_widget = self._stack.widget(index)
        if hasattr(current_widget, "refresh"):
            current_widget.refresh()

