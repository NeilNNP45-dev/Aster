# 🌼 Aster Project Structure

## Purpose

This document describes the overall architecture and folder structure of Aster.

Aster is designed to be a long-term desktop application that grows over time. The project should remain clean, modular, and easy to maintain as new features are added.

The folder structure below should be followed unless there is a clear architectural reason to change it.

---

# Project Structure

```
Aster/
│
├── main.py                 # Application entry point
│
├── ui/                     # User interface components
│   ├── main_window.py
│   ├── pages/
│   │   ├── home/
│   │   ├── coding/
│   │   ├── college/
│   │   ├── productivity/
│   │   ├── fitness/
│   │   ├── analytics/
│   │   └── settings/
│   ├── widgets/
│   └── dialogs/
│
├── database/               # SQLite database and models
│   ├── connection.py
│   ├── schema.sql
│   ├── models.py
│   ├── repositories/
│   └── migrations/
│
├── services/               # Business logic and integrations
│   ├── github/
│   ├── timer/
│   ├── attendance/
│   ├── productivity/
│   ├── college/
│   ├── coding/
│   ├── fitness/
│   └── analytics/
│
├── assets/
│   ├── icons/
│   ├── images/
│   ├── fonts/
│   └── themes/
│
├── utils/                  # Shared helper functions
│
├── tests/                  # Automated tests
│
├── docs/                   # Documentation
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

# Folder Responsibilities

## ui/

Contains everything related to the graphical user interface.

This folder should only handle displaying information and responding to user interactions. Business logic should remain outside the UI whenever possible.

---

## database/

Responsible for storing and retrieving application data using SQLite.

This folder should not contain user interface code.

---

## services/

Contains the application's business logic.

Services perform tasks such as interacting with GitHub, managing timers, handling attendance calculations, or processing productivity data.

Services should remain independent of the graphical interface whenever possible.

---

## assets/

Stores non-code resources such as icons, images, fonts, and themes.

---

## utils/

Contains helper functions and reusable utilities that do not belong to a specific feature.

---

## tests/

Contains automated tests for the project.

---

## docs/

Contains project documentation, architecture decisions, coding standards, roadmaps, and other developer resources.

---

# Architectural Principles

* Keep user interface, business logic, and data management separate.
* Organize code by feature and responsibility.
* Prefer small, focused modules over large files.
* Design the project so new features can be added without major restructuring.
* Avoid unnecessary complexity.
* Prioritize readability and maintainability over clever implementations.

This document is expected to evolve alongside Aster as the project grows.

---

# Current UI and Theme Structure

The application currently exposes eight top-level pages through the sidebar:

1. Home
2. Productivity
3. College
4. Coding
5. Fitness
6. Analytics
7. Theme
8. Settings

The Theme page is intentionally separate from Settings. Settings contains application information, storage diagnostics, privacy details, and integration information. Theme contains preset selection, custom palette editing, color pickers, reset controls, and a live visual preview.

## Current Theme-Related Files

| Path | Responsibility |
|---|---|
| `ui/theme_manager.py` | Loads, applies, switches, and persists the active application theme. |
| `ui/theme_palette.py` | Defines semantic palette roles and the built-in Sunlit and Midnight palettes. |
| `ui/pages/theme/page.py` | Theme Studio page with preset selection, color controls, reset behavior, and preview controls. |
| `assets/themes/dark.qss` | Existing Sunlit Candy base stylesheet retained for compatibility. |
| `assets/themes/midnight.qss` | Midnight Candy dark-mode QSS override stylesheet. |
| `assets/themes/custom.qss` | Placeholder-based QSS template rendered from a user palette. |

Theme preferences are stored through Qt `QSettings`, not SQLite. This keeps appearance configuration independent from user productivity data and allows the selected theme to be loaded before the main window is created.

## Current Home and Productivity Support Files

The Home and Productivity areas use the existing UI, service, repository, and configuration boundaries:

| Path | Responsibility |
|---|---|
| `ui/pages/home/page.py` | Home greeting, summary metrics, daily-goal preview, progress indicator, and recent updates. |
| `ui/pages/productivity/page.py` | Productivity page shell and the four existing sub-tabs. |
| `ui/pages/productivity/pomodoro_widget.py` | Pomodoro focused-canvas UI, controls, settings entry point, and session history display. |
| `ui/dialogs/pomodoro_settings_dialog.py` | Dialog for validating and editing Pomodoro durations. |
| `services/productivity/pomodoro_service.py` | Pomodoro state machine, configurable durations, active-session safety, and completion logging. |
| `database/repositories/productivity_repository.py` | Persistence for tasks, daily goals, notes, and Pomodoro sessions, including date-based daily-goal streak handling. |
| `tests/test_home_widget_layout.py` | Qt smoke coverage for the adaptive Home daily-goal card. |
| `tests/test_pomodoro_widget_layout.py` | Qt smoke coverage for Pomodoro layout separation and control visibility. |

Pomodoro duration preferences are stored with Qt `QSettings` under the Productivity configuration namespace. They are intentionally kept outside the SQLite productivity tables because they are local timer preferences rather than user activity records.

## Relevant Current Tree

```text
ui/
├── main_window.py
├── theme_manager.py
├── theme_palette.py
├── pages/
│   ├── home/
│   ├── productivity/
│   ├── college/
│   ├── coding/
│   ├── fitness/
│   ├── analytics/
│   ├── theme/
│   │   └── page.py
│   └── settings/
└── widgets/

assets/themes/
├── dark.qss
├── midnight.qss
└── custom.qss
```
