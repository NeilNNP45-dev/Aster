from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame


class CollegePage(QWidget):
    """College & Academics feature page placeholder (Planned for Version 0.3)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CollegePage")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        title = QLabel("College & Academics")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Timetable, attendance tracking, assignments, and exam planning")
        subtitle.setProperty("class", "page-subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setProperty("class", "card")
        card_layout = QVBoxLayout(card)

        card_title = QLabel("Planned Features (Version 0.3)")
        card_title.setProperty("class", "card-title")
        card_desc = QLabel(
            "• Weekly Academic Timetable Schedule\n"
            "• Course Attendance Tracker with Percentage Targets\n"
            "• Assignment Deadline Tracker & Reminders\n"
            "• Exam Planner & CGPA Target Tracker"
        )
        card_desc.setProperty("class", "card-description")

        card_layout.addWidget(card_title)
        card_layout.addWidget(card_desc)

        layout.addWidget(card)
        layout.addStretch()
