from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class CodingPage(QWidget):
    """Coding & Software Development feature page placeholder (Planned for Version 0.4)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CodingPage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Coding & Development")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Coding timer, project tracking, and GitHub contribution insights")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("Planned Features (Version 0.4)")
        card_title.setProperty("class", "card-title")
        card_desc = QLabel(
            "• Dedicated Coding Stopwatch & Session Logger\n"
            "• Active Software Project Tracker\n"
            "• Daily Coding Habit Goals\n"
            "• GitHub Commit & Contribution Tracking API Integration"
        )
        card_desc.setProperty("class", "card-description")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)

        layout.addWidget(card)
        layout.addStretch()
