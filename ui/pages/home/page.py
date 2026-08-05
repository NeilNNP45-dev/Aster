from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame


class HomePage(QWidget):
    """Home dashboard page view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomePage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(20)

        # Header
        title = QLabel("Welcome to Aster 🌼")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Your unified personal life dashboard")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Dashboard cards
        cards = QHBoxLayout()
        cards.setSpacing(16)

        overview_card = QFrame()
        overview_card.setProperty("class", "card")
        overview_layout = QVBoxLayout(overview_card)
        overview_title = QLabel("Workspace Overview")
        overview_title.setProperty("class", "card-title")
        overview_desc = QLabel(
            "Aster helps you manage productivity, coding, academics, fitness, and analytics from one place.\n"
            "Use the sidebar to jump between modules and keep your workflow focused."
        )
        overview_desc.setProperty("class", "card-description")
        overview_badge = QLabel("Version 0.4 — Coding + GitHub Ready")
        overview_badge.setProperty("class", "status-badge")
        overview_layout.addWidget(overview_title)
        overview_layout.addWidget(overview_desc)
        overview_layout.addWidget(overview_badge)

        quick_card = QFrame()
        quick_card.setProperty("class", "card")
        quick_layout = QVBoxLayout(quick_card)
        quick_title = QLabel("Quick Start")
        quick_title.setProperty("class", "card-title")
        quick_layout.addWidget(quick_title)
        quick_layout.addWidget(QLabel("• Create tasks and goals in Productivity"))
        quick_layout.addWidget(QLabel("• Track coding projects, timer sessions, and GitHub metadata"))
        quick_layout.addWidget(QLabel("• Log study schedules in College and keep attendance"))
        quick_layout.addWidget(QLabel("• Monitor your trends in Analytics"))
        for child in quick_card.findChildren(QLabel):
            if child is not quick_title:
                child.setProperty("class", "card-description")

        cards.addWidget(overview_card, 2)
        cards.addWidget(quick_card, 1)

        layout.addLayout(cards)

        # Feature highlight card
        highlight_card = QFrame()
        highlight_card.setProperty("class", "card")
        highlight_layout = QVBoxLayout(highlight_card)
        highlight_title = QLabel("What’s new")
        highlight_title.setProperty("class", "card-title")
        highlight_text = QLabel(
            "GitHub sync now supports owner/repo IDs, URLs, and private repos with a PAT.\n"
            "Projects are stored locally and kept out of source control via database/aster.db."
        )
        highlight_text.setProperty("class", "card-description")
        highlight_layout.addWidget(highlight_title)
        highlight_layout.addWidget(highlight_text)

        layout.addWidget(highlight_card)
        layout.addStretch()
