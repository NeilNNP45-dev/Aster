from copy import deepcopy
from typing import Dict


Palette = Dict[str, str]


PALETTE_ROLES = (
    "background",
    "sidebar",
    "surface",
    "surface_alt",
    "border",
    "primary",
    "secondary",
    "success",
    "warning",
    "danger",
    "text",
    "muted_text",
    "selection",
)


SUNLIT_PALETTE: Palette = {
    "background": "#FFF8F0",
    "sidebar": "#FFF0F5",
    "surface": "#FFFFFF",
    "surface_alt": "#FFF0D6",
    "border": "#F0DAD2",
    "primary": "#FF7F6E",
    "secondary": "#F7A8C4",
    "success": "#8ED8B5",
    "warning": "#FFD76A",
    "danger": "#D95767",
    "text": "#3C3040",
    "muted_text": "#8A6E7B",
    "selection": "#FFC9D8",
}


MIDNIGHT_PALETTE: Palette = {
    "background": "#171A22",
    "sidebar": "#202532",
    "surface": "#1D222C",
    "surface_alt": "#30394B",
    "border": "#2F3849",
    "primary": "#FF806F",
    "secondary": "#F39AB9",
    "success": "#87D5AE",
    "warning": "#F7C95B",
    "danger": "#FF9CA7",
    "text": "#F9F5F2",
    "muted_text": "#B7BAC8",
    "selection": "#4A3038",
}


def copy_palette(palette: Palette) -> Palette:
    return deepcopy(palette)


def is_valid_palette(palette: object) -> bool:
    if not isinstance(palette, dict):
        return False
    return all(isinstance(palette.get(role), str) for role in PALETTE_ROLES)

