from typing import Optional

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog, QComboBox, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from ui.theme_manager import ThemeManager
from ui.theme_palette import PALETTE_ROLES


class PaletteColorButton(QPushButton):
    """Clickable color swatch used by the Theme Studio."""

    def __init__(self, label: str, color: str, on_changed, parent=None):
        super().__init__(parent)
        self._label = label
        self._on_changed = on_changed
        self.setFixedHeight(44)
        self.clicked.connect(self._choose_color)
        self.set_color(color)

    def set_color(self, color: str):
        self._color = color.upper()
        qcolor = QColor(self._color)
        text_color = "#3C3040" if qcolor.lightnessF() > 0.62 else "#FFF8F0"
        self.setText(f"{self._label}  {self._color}")
        self.setStyleSheet(
            f"background-color: {self._color}; color: {text_color}; "
            "border: 1px solid rgba(0, 0, 0, 45%); border-radius: 8px; "
            "padding: 6px 10px; text-align: left;"
        )

    def _choose_color(self):
        selected = QColorDialog.getColor(QColor(self._color), self, f"Choose {self._label}")
        if selected.isValid():
            color = selected.name().upper()
            self.set_color(color)
            self._on_changed(color)


class ThemePage(QWidget):
    """Dedicated theme selection and custom palette studio."""

    _PALETTE_LABELS = {
        "background": "Background",
        "sidebar": "Sidebar",
        "surface": "Cards",
        "surface_alt": "Secondary",
        "border": "Borders",
        "primary": "Primary",
        "secondary": "Highlight",
        "success": "Success",
        "warning": "Warning",
        "danger": "Danger",
        "text": "Text",
        "muted_text": "Muted text",
        "selection": "Selection",
    }

    def __init__(self, theme_manager: ThemeManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("ThemePage")
        self._theme_manager = theme_manager
        self._palette_buttons = {}
        self._init_ui()
        self._theme_manager.theme_changed.connect(self._sync_controls)
        self._sync_controls(self._theme_manager.current_theme)

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 28, 28, 28)
        root_layout.setSpacing(16)

        title = QLabel("Theme Studio 🎨")
        title.setProperty("class", "page-header")
        subtitle = QLabel("Choose a preset or create a color palette that feels like yours")
        subtitle.setProperty("class", "page-subtitle")
        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setProperty("class", "theme-scroll")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(4, 4, 12, 4)
        content_layout.setSpacing(16)

        preset_card = QWidget()
        preset_card.setProperty("class", "card")
        preset_layout = QVBoxLayout(preset_card)
        preset_layout.setSpacing(10)

        preset_title = QLabel("Theme preset")
        preset_title.setProperty("class", "card-title")
        preset_layout.addWidget(preset_title)

        self._theme_combo = QComboBox()
        self._theme_combo.setProperty("class", "form-combo")
        self._theme_combo.addItem("☀️  Sunlit Candy", ThemeManager.SUNLIT)
        self._theme_combo.addItem("🌙  Midnight Candy", ThemeManager.MIDNIGHT)
        self._theme_combo.addItem("🎨  Custom Palette", ThemeManager.CUSTOM)
        self._theme_combo.currentIndexChanged.connect(self._on_theme_selected)
        preset_layout.addWidget(self._theme_combo)

        preset_note = QLabel("Presets are ready to use; Custom Palette lets you edit every color role.")
        preset_note.setProperty("class", "card-description")
        preset_note.setWordWrap(True)
        preset_layout.addWidget(preset_note)
        content_layout.addWidget(preset_card)

        palette_card = QWidget()
        palette_card.setProperty("class", "card")
        palette_layout = QVBoxLayout(palette_card)
        palette_layout.setSpacing(10)

        palette_title = QLabel("Custom palette")
        palette_title.setProperty("class", "card-title")
        palette_layout.addWidget(palette_title)

        palette_note = QLabel("Click any color to open the picker. Changes apply instantly and are saved locally.")
        palette_note.setProperty("class", "card-description")
        palette_note.setWordWrap(True)
        palette_layout.addWidget(palette_note)

        palette_grid = QGridLayout()
        palette_grid.setSpacing(8)
        palette = self._theme_manager.current_palette
        for index, role in enumerate(PALETTE_ROLES):
            button = PaletteColorButton(
                self._PALETTE_LABELS[role],
                palette[role],
                lambda color, selected_role=role: self._on_palette_color_changed(selected_role, color),
            )
            self._palette_buttons[role] = button
            palette_grid.addWidget(button, index // 2, index % 2)
        palette_layout.addLayout(palette_grid)

        reset_button = QPushButton("Reset custom palette to Sunlit Candy")
        reset_button.setProperty("class", "secondary-btn")
        reset_button.clicked.connect(self._reset_custom_palette)
        palette_layout.addWidget(reset_button)
        content_layout.addWidget(palette_card)

        preview_card = QWidget()
        preview_card.setProperty("class", "card")
        preview_layout = QVBoxLayout(preview_card)
        preview_title = QLabel("Preview")
        preview_title.setProperty("class", "card-title")
        preview_layout.addWidget(preview_title)
        preview_row = QHBoxLayout()
        preview_row.setSpacing(8)
        self._preview_primary = QPushButton("Primary action")
        self._preview_primary.setProperty("class", "primary-btn")
        self._preview_secondary = QPushButton("Secondary action")
        self._preview_secondary.setProperty("class", "secondary-btn")
        self._preview_badge = QLabel("Success")
        self._preview_badge.setProperty("class", "status-badge")
        preview_row.addWidget(self._preview_primary)
        preview_row.addWidget(self._preview_secondary)
        preview_row.addWidget(self._preview_badge)
        preview_row.addStretch()
        preview_layout.addLayout(preview_row)
        content_layout.addWidget(preview_card)
        content_layout.addStretch()

        scroll.setWidget(content)
        root_layout.addWidget(scroll, 1)

    def _on_theme_selected(self, index: int):
        if index >= 0:
            self._theme_manager.apply_theme(self._theme_combo.itemData(index))

    def _on_palette_color_changed(self, role: str, color: str):
        palette = self._theme_manager.current_palette
        palette[role] = color
        self._theme_manager.apply_custom_palette(palette)

    def _reset_custom_palette(self):
        self._theme_manager.reset_custom_palette(ThemeManager.SUNLIT)

    def _sync_controls(self, _theme_name: str):
        theme_name = self._theme_manager.current_theme
        self._theme_combo.blockSignals(True)
        self._theme_combo.setCurrentIndex(self._theme_combo.findData(theme_name))
        self._theme_combo.blockSignals(False)

        palette = self._theme_manager.current_palette
        for role, button in self._palette_buttons.items():
            button.set_color(palette[role])
