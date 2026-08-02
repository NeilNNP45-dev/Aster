from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget

from ui.widgets.sidebar import SidebarWidget
from ui.pages.home.page import HomePage
from ui.pages.productivity.page import ProductivityPage
from ui.pages.college.page import CollegePage
from ui.pages.coding.page import CodingPage
from ui.pages.fitness.page import FitnessPage
from ui.pages.analytics.page import AnalyticsPage
from ui.pages.settings.page import SettingsPage


class MainWindow(QMainWindow):
    """Main Application Window for Aster."""

    DEFAULT_WIDTH = 1000
    DEFAULT_HEIGHT = 800
    MIN_WIDTH = 900
    MIN_HEIGHT = 650

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aster")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        self._init_ui()
        self._center_window()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar navigation
        self.sidebar = SidebarWidget(central_widget)
        main_layout.addWidget(self.sidebar)

        # Stacked pages container
        self.stacked_widget = QStackedWidget(central_widget)
        self.stacked_widget.setObjectName("ContentArea")
        main_layout.addWidget(self.stacked_widget, 1)

        # Instantiate & register domain pages
        self.home_page = HomePage()
        self.productivity_page = ProductivityPage()
        self.college_page = CollegePage()
        self.coding_page = CodingPage()
        self.fitness_page = FitnessPage()
        self.analytics_page = AnalyticsPage()
        self.settings_page = SettingsPage()

        self.stacked_widget.addWidget(self.home_page)         # Index 0
        self.stacked_widget.addWidget(self.productivity_page) # Index 1
        self.stacked_widget.addWidget(self.college_page)      # Index 2
        self.stacked_widget.addWidget(self.coding_page)       # Index 3
        self.stacked_widget.addWidget(self.fitness_page)      # Index 4
        self.stacked_widget.addWidget(self.analytics_page)    # Index 5
        self.stacked_widget.addWidget(self.settings_page)     # Index 6

        # Connect sidebar navigation signal
        self.sidebar.page_changed.connect(self._switch_page)

    def _switch_page(self, index: int):
        if 0 <= index < self.stacked_widget.count():
            self.stacked_widget.setCurrentIndex(index)

    def _center_window(self):
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
