from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class FitnessPage(QWidget):
    """Fitness feature page placeholder (Planned for Version 0.5)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FitnessPage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Fitness & Health")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Workout logging, body weight tracking, and gym progress")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("Planned Features (Version 0.5)")
        card_title.setProperty("class", "card-title")
        card_desc = QLabel(
            "• Exercise & Workout Routine Log\n"
            "• Body Weight & Composition Tracker\n"
            "• Strength & Endurance Progress Over Time"
        )
        card_desc.setProperty("class", "card-description")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)

        layout.addWidget(card)
        layout.addStretch()
