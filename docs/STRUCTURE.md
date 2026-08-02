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
│   ├── database.py
│   ├── models.py
│   └── migrations/
│
├── services/               # Business logic and integrations
│   ├── github/
│   ├── timer/
│   ├── attendance/
│   ├── productivity/
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
