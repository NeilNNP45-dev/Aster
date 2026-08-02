from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class AnalyticsPage(QWidget):
    """Analytics & Reports feature page placeholder (Planned for Version 0.6 & Luna v0.7)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnalyticsPage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Analytics & Luna AI")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Personalized insights, performance graphs, and AI recommendations")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("Planned Features (Versions 0.6 & 0.7)")
        card_title.setProperty("class", "card-title")
        card_desc = QLabel(
            "• Weekly & Monthly Multi-Domain Productivity Reports\n"
            "• Productivity, Study, and Fitness Trend Charts\n"
            "• Luna AI Analytics Assistant for Personalized Recommendations"
        )
        card_desc.setProperty("class", "card-description")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)

        layout.addWidget(card)
        layout.addStretch()
