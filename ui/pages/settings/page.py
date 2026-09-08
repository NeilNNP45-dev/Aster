import webbrowser
from typing import Callable, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QGridLayout,
)

from services.settings.settings_service import SettingsService, StorageInfo
from ui.theme_manager import ThemeManager


class SettingPropertyRow(QWidget):
    """A clean key-value row for settings items."""

    def __init__(self, key: str, value: str, is_highlight: bool = False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)

        key_lbl = QLabel(key)
        key_lbl.setProperty("class", "setting-key")
        key_lbl.setFixedWidth(160)

        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "setting-val-highlight" if is_highlight else "setting-val")
        self.value_label.setWordWrap(True)

        layout.addWidget(key_lbl)
        layout.addWidget(self.value_label, 1)

    def set_value(self, value: str):
        self.value_label.setText(value)


class SettingsPage(QWidget):
    """User-focused application settings and diagnostics view."""

    def __init__(self, on_navigate: Optional[Callable[[int], None]] = None,
                 theme_manager: Optional[ThemeManager] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPage")
        self._on_navigate = on_navigate
        self._theme_manager = theme_manager
        self._settings_service = SettingsService()

        self._init_ui()
        self.refresh()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(28, 28, 28, 28)
        root_layout.setSpacing(20)

        title = QLabel("Settings")
        title.setProperty("class", "page-header")
        subtitle = QLabel("View application details, storage diagnostics, and system preferences")
        subtitle.setProperty("class", "page-subtitle")
        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        grid = QGridLayout()
        grid.setSpacing(16)

        app_card = QFrame()
        app_card.setProperty("class", "setting-card")
        app_layout = QVBoxLayout(app_card)
        app_layout.setSpacing(10)
        app_title = QLabel("Application Information")
        app_title.setProperty("class", "card-title")
        app_layout.addWidget(app_title)
        app_layout.addWidget(SettingPropertyRow("App Name:", "Aster"))
        app_layout.addWidget(SettingPropertyRow("Version:", "v0.6.0 (Analytics Suite)", is_highlight=True))
        app_layout.addWidget(SettingPropertyRow("Architecture:", "Layered Desktop (PySide6 / SQLite)"))
        docs_btn = QPushButton("🌐  Project Repository")
        docs_btn.setProperty("class", "secondary-btn")
        docs_btn.clicked.connect(self._open_repo_url)
        app_layout.addWidget(docs_btn)
        grid.addWidget(app_card, 0, 0)

        theme_card = QFrame()
        theme_card.setProperty("class", "setting-card")
        theme_layout = QVBoxLayout(theme_card)
        theme_layout.setSpacing(10)
        theme_title = QLabel("Appearance")
        theme_title.setProperty("class", "card-title")
        theme_layout.addWidget(theme_title)
        self._theme_row = SettingPropertyRow(
            "Active Theme:", self._active_theme_name(), is_highlight=True
        )
        theme_layout.addWidget(self._theme_row)
        theme_note = QLabel("Choose presets and customize colors from the Theme page.")
        theme_note.setProperty("class", "card-description")
        theme_note.setWordWrap(True)
        theme_layout.addWidget(theme_note)
        theme_btn = QPushButton("🎨  Open Theme Studio")
        theme_btn.setProperty("class", "secondary-btn")
        theme_btn.clicked.connect(lambda: self._trigger_navigate(6))
        theme_layout.addWidget(theme_btn)
        theme_layout.addStretch()
        grid.addWidget(theme_card, 0, 1)

        data_card = QFrame()
        data_card.setProperty("class", "setting-card")
        data_layout = QVBoxLayout(data_card)
        data_layout.setSpacing(10)
        data_title = QLabel("Data & Privacy")
        data_title.setProperty("class", "card-title")
        data_layout.addWidget(data_title)
        data_layout.addWidget(SettingPropertyRow("Privacy Policy:", "100% Local & Private", is_highlight=True))
        self._db_file_row = SettingPropertyRow("Database File:", "database/aster.db")
        self._db_size_row = SettingPropertyRow("Database Size:", "Calculating...")
        self._journal_row = SettingPropertyRow("Journal Mode:", "WAL (Write-Ahead Logging)")
        data_layout.addWidget(self._db_file_row)
        data_layout.addWidget(self._db_size_row)
        data_layout.addWidget(self._journal_row)
        grid.addWidget(data_card, 1, 0)

        integ_card = QFrame()
        integ_card.setProperty("class", "setting-card")
        integ_layout = QVBoxLayout(integ_card)
        integ_layout.setSpacing(10)
        integ_title = QLabel("Integrations")
        integ_title.setProperty("class", "card-title")
        integ_layout.addWidget(integ_title)
        integ_layout.addWidget(SettingPropertyRow("GitHub Sync:", "Session-only Auth Model"))
        integ_layout.addWidget(SettingPropertyRow("Token Storage:", "Requested on-demand, never saved to disk"))
        jump_coding_btn = QPushButton("💻  Jump to Coding Integration")
        jump_coding_btn.setProperty("class", "secondary-btn")
        jump_coding_btn.clicked.connect(lambda: self._trigger_navigate(3))
        integ_layout.addWidget(jump_coding_btn)
        integ_layout.addStretch()
        grid.addWidget(integ_card, 1, 1)

        root_layout.addLayout(grid)
        root_layout.addStretch()

        if self._theme_manager:
            self._theme_manager.theme_changed.connect(self._on_theme_changed)

    def refresh(self):
        storage: StorageInfo = self._settings_service.get_storage_info()
        self._db_size_row.set_value(storage.file_size_formatted)
        self._db_file_row.set_value(storage.db_filename)
        self._journal_row.set_value(storage.journal_mode)

    def _active_theme_name(self) -> str:
        if self._theme_manager:
            return self._theme_manager.display_name(self._theme_manager.current_theme)
        return "Sunlit Candy"

    def _on_theme_changed(self, _theme_name: str):
        self._theme_row.set_value(self._active_theme_name())

    def _open_repo_url(self):
        webbrowser.open("https://github.com/NeilNNP45-dev/Aster")

    def _trigger_navigate(self, page_index: int):
        if self._on_navigate:
            self._on_navigate(page_index)

    def closeEvent(self, event):
        if hasattr(self, "_settings_service") and self._settings_service:
            self._settings_service.close()
        super().closeEvent(event)
