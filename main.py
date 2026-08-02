import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def load_stylesheet(app: QApplication):
    """Load and apply the dark mode QSS stylesheet."""
    theme_path = Path(__file__).parent / "assets" / "themes" / "dark.qss"
    if theme_path.exists():
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    """Application entry point for Aster."""
    app = QApplication(sys.argv)
    app.setApplicationName("Aster")
    app.setOrganizationName("Aster")

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
