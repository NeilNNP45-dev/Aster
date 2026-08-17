from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QComboBox,
    QScrollArea,
    QApplication,
)
from services.analytics.analytics_service import AnalyticsService


class ReportsWidget(QWidget):
    """Weekly and Monthly structured report generator widget."""

    def __init__(self, service: AnalyticsService, parent=None):
        super().__init__(parent)
        self.service = service
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Controls Row
        ctrl_row = QHBoxLayout()

        self.type_combo = QComboBox()
        self.type_combo.setProperty("class", "form-combo")
        self.type_combo.addItems(["Weekly Report", "Monthly Report"])
        self.type_combo.currentTextChanged.connect(self.refresh)

        copy_btn = QPushButton("📋 Copy Summary to Clipboard")
        copy_btn.setProperty("class", "secondary-btn")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(self._copy_to_clipboard)

        ctrl_row.addWidget(QLabel("Report Type:"))
        ctrl_row.addWidget(self.type_combo)
        ctrl_row.addStretch()
        ctrl_row.addWidget(copy_btn)

        layout.addLayout(ctrl_row)

        # Scrollable Report Document Panel
        self.report_card = QFrame()
        self.report_card.setProperty("class", "report-card")
        self.report_layout = QVBoxLayout(self.report_card)
        self.report_layout.setSpacing(16)

        # Header Title
        self.header_title = QLabel("Performance Report")
        self.header_title.setProperty("class", "report-header")

        self.period_subtitle = QLabel("")
        self.period_subtitle.setProperty("class", "page-subtitle")

        self.report_layout.addWidget(self.header_title)
        self.report_layout.addWidget(self.period_subtitle)

        # Section 1: Key Highlights
        self.highlights_box = QFrame()
        self.highlights_box.setProperty("class", "card")
        hl_layout = QVBoxLayout(self.highlights_box)
        hl_title = QLabel("🌟 Key Highlights")
        hl_title.setProperty("class", "card-title")
        self.highlights_lbl = QLabel("")
        self.highlights_lbl.setProperty("class", "report-text")
        hl_layout.addWidget(hl_title)
        hl_layout.addWidget(self.highlights_lbl)

        self.report_layout.addWidget(self.highlights_box)

        # Section 2: Domain Breakdown Text Panels
        sections = [
            ("✅ Productivity & Habits", "prod_text"),
            ("🎓 College & Academics", "college_text"),
            ("💻 Coding & Projects", "coding_text"),
            ("💪 Fitness & Health", "fitness_text"),
        ]

        self.sec_labels = {}
        for title, key in sections:
            sec_card = QFrame()
            sec_card.setProperty("class", "card")
            sl = QVBoxLayout(sec_card)
            st = QLabel(title)
            st.setProperty("class", "card-title")
            st_text = QLabel("")
            st_text.setProperty("class", "report-text")

            sl.addWidget(st)
            sl.addWidget(st_text)
            self.report_layout.addWidget(sec_card)
            self.sec_labels[key] = st_text

        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.report_card)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        layout.addWidget(scroll, 1)

        self.refresh()

    def refresh(self):
        report_type = "Weekly" if "Weekly" in self.type_combo.currentText() else "Monthly"
        self._current_report = self.service.generate_report(report_type)

        self.header_title.setText(self._current_report.summary_text)
        self.period_subtitle.setText(f"Generated at {self._current_report.generated_at}")

        # Highlights
        hl_text = "\n".join(self._current_report.highlights or [])
        self.highlights_lbl.setText(hl_text)

        # Domains
        self.sec_labels["prod_text"].setText(self._current_report.productivity_notes)
        self.sec_labels["college_text"].setText(self._current_report.college_notes)
        self.sec_labels["coding_text"].setText(self._current_report.coding_notes)
        self.sec_labels["fitness_text"].setText(self._current_report.fitness_notes)

    def _copy_to_clipboard(self):
        if hasattr(self, "_current_report"):
            rep = self._current_report
            text = (
                f"=== {rep.summary_text} ===\n\n"
                f"Highlights:\n" + "\n".join(rep.highlights or []) + "\n\n"
                f"Productivity:\n{rep.productivity_notes}\n\n"
                f"College:\n{rep.college_notes}\n\n"
                f"Coding:\n{rep.coding_notes}\n\n"
                f"Fitness:\n{rep.fitness_notes}\n"
            )
            QApplication.clipboard().setText(text)
