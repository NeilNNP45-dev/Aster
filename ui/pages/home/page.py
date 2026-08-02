from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class HomePage(QWidget):
    """Home dashboard page view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        # Header
        title = QLabel("Welcome to Aster 🌼")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Your unified personal life dashboard")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Overview Card
        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("System Status")
        card_title.setProperty("class", "card-title")
        
        card_desc = QLabel(
            "Version 0.1 Application Foundation is active.\n"
            "All core navigation routes are established and ready for feature modules."
        )
        card_desc.setProperty("class", "card-description")

        badge = QLabel(" Pre-Alpha v0.1 ")
        badge.setProperty("class", "status-badge")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)
        card_layout.addWidget(badge)

        layout.addWidget(card)
        layout.addStretch()
