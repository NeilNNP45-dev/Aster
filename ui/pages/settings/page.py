from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class SettingsPage(QWidget):
    """Settings page view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Configure dashboard preferences, themes, and profile options")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("Application Information")
        card_title.setProperty("class", "card-title")
        card_desc = QLabel(
            "• App Name: Aster\n"
            "• Theme: Sleek Dark Mode\n"
            "• Version: Pre-Alpha v0.1\n"
            "• Database: SQLite (local persistence)"
        )
        card_desc.setProperty("class", "card-description")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)

        layout.addWidget(card)
        layout.addStretch()
