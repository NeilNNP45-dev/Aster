import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.theme_manager import ThemeManager


def main():
    """Application entry point for Aster."""
    app = QApplication(sys.argv)
    app.setApplicationName("Aster")
    app.setOrganizationName("Aster")

    theme_manager = ThemeManager(app)

    window = MainWindow(theme_manager=theme_manager)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
