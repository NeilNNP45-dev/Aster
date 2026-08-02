from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
)


class SidebarWidget(QWidget):
    """Navigation Sidebar Widget for Aster."""

    page_changed = Signal(int)

    NAV_ITEMS = [
        ("🏠  Home", 0),
        ("✅  Productivity", 1),
        ("🎓  College", 2),
        ("💻  Coding", 3),
        ("💪  Fitness", 4),
        ("📊  Analytics", 5),
        ("⚙️  Settings", 6),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarWidget")
        self.setFixedWidth(220)
        self._button_group = QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(8)

        # Brand Header
        logo = QLabel("🌼 Aster")
        logo.setObjectName("SidebarLogo")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(logo)

        layout.addSpacing(16)

        # Navigation Buttons
        for text, index in self.NAV_ITEMS:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty("class", "nav-btn")

            self._button_group.addButton(btn, index)
            layout.addWidget(btn)

            if index == 0:
                btn.setChecked(True)

        self._button_group.idClicked.connect(self._on_button_clicked)

        layout.addStretch()

    def _on_button_clicked(self, page_index: int):
        self.page_changed.emit(page_index)

    def set_active_index(self, index: int):
        btn = self._button_group.button(index)
        if btn:
            btn.setChecked(True)
