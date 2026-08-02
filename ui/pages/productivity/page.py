from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class ProductivityPage(QWidget):
    """Productivity feature page placeholder (Planned for Version 0.2)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProductivityPage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("Productivity")
        title.setProperty("class", "page-header")
        subtitle = QLabel("To-do lists, daily goals, notes, and Pomodoro timer")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("Planned Features (Version 0.2)")
        card_title.setProperty("class", "card-title")
        card_desc = QLabel(
            "• Interactive To-Do List & Task Prioritization\n"
            "• Daily Goals & Habit Tracker\n"
            "• Markdown Notes & Quick Journaling\n"
            "• Customizable Pomodoro Focus Timer"
        )
        card_desc.setProperty("class", "card-description")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)

        layout.addWidget(card)
        layout.addStretch()
