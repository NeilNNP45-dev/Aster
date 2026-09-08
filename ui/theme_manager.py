import json
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtWidgets import QApplication

from ui.theme_palette import (
    MIDNIGHT_PALETTE,
    PALETTE_ROLES,
    SUNLIT_PALETTE,
    Palette,
    copy_palette,
    is_valid_palette,
)


class ThemeManager(QObject):
    """Loads, applies, and persists Aster's application-wide theme."""

    theme_changed = Signal(str)

    SUNLIT = "sunlit"
    MIDNIGHT = "midnight"
    CUSTOM = "custom"

    _DISPLAY_NAMES = {
        SUNLIT: "Sunlit Candy",
        MIDNIGHT: "Midnight Candy",
        CUSTOM: "Custom Palette",
    }

    def __init__(self, app: QApplication, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._app = app
        self._settings = QSettings("Aster", "Aster")
        self._custom_palette = self._load_custom_palette()
        saved_theme = self._settings.value("appearance/theme", self.SUNLIT)
        self._theme = saved_theme if saved_theme in self._DISPLAY_NAMES else self.SUNLIT
        self.apply_theme(self._theme, persist=False, emit=False)

    @property
    def current_theme(self) -> str:
        return self._theme

    @classmethod
    def display_name(cls, theme_name: str) -> str:
        return cls._DISPLAY_NAMES.get(theme_name, cls._DISPLAY_NAMES[cls.SUNLIT])

    @property
    def current_palette(self) -> Palette:
        if self._theme == self.MIDNIGHT:
            return copy_palette(MIDNIGHT_PALETTE)
        if self._theme == self.CUSTOM:
            return copy_palette(self._custom_palette)
        return copy_palette(SUNLIT_PALETTE)

    def palette_for(self, theme_name: str) -> Palette:
        if theme_name == self.MIDNIGHT:
            return copy_palette(MIDNIGHT_PALETTE)
        if theme_name == self.CUSTOM:
            return copy_palette(self._custom_palette)
        return copy_palette(SUNLIT_PALETTE)

    def apply_theme(self, theme_name: str, persist: bool = True, emit: bool = True):
        if theme_name not in self._DISPLAY_NAMES:
            theme_name = self.SUNLIT

        theme_dir = Path(__file__).parent.parent / "assets" / "themes"
        base_path = theme_dir / "dark.qss"
        override_path = None
        if theme_name == self.MIDNIGHT:
            override_path = theme_dir / "midnight.qss"
        elif theme_name == self.CUSTOM:
            override_path = theme_dir / "custom.qss"

        stylesheet = base_path.read_text(encoding="utf-8") if base_path.exists() else ""
        if override_path and override_path.exists():
            override = override_path.read_text(encoding="utf-8")
            if theme_name == self.CUSTOM:
                override = self._render_custom_stylesheet(override)
            stylesheet += "\n" + override

        self._app.setStyleSheet(stylesheet)
        self._theme = theme_name
        if persist:
            self._settings.setValue("appearance/theme", theme_name)
            self._settings.sync()
        if emit:
            self.theme_changed.emit(theme_name)

    def apply_custom_palette(self, palette: Palette, persist: bool = True):
        if not is_valid_palette(palette):
            return False
        self._custom_palette = {role: palette[role].upper() for role in PALETTE_ROLES}
        self.apply_theme(self.CUSTOM, persist=persist)
        self._settings.setValue("appearance/custom_palette", json.dumps(self._custom_palette))
        self._settings.sync()
        return True

    def reset_custom_palette(self, base_theme: str = SUNLIT):
        self._custom_palette = self.palette_for(base_theme)
        self._settings.setValue("appearance/custom_palette", json.dumps(self._custom_palette))
        self._settings.sync()
        self.apply_theme(self.CUSTOM)

    def _load_custom_palette(self) -> Palette:
        raw_palette = self._settings.value("appearance/custom_palette", "")
        try:
            saved_palette = json.loads(raw_palette) if raw_palette else {}
        except (TypeError, json.JSONDecodeError):
            saved_palette = {}
        if is_valid_palette(saved_palette):
            return {role: saved_palette[role].upper() for role in PALETTE_ROLES}
        return copy_palette(SUNLIT_PALETTE)

    def _render_custom_stylesheet(self, template: str) -> str:
        rendered = template
        for role, color in self._custom_palette.items():
            rendered = rendered.replace("{{" + role + "}}", color)
        return rendered
