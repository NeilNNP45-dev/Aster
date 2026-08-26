# 🌼 Aster

Aster is a personal life dashboard built in Python for students and developers who want to manage different parts of their daily life from one place.

It brings together **productivity, academics, coding, fitness, and analytics** in a single desktop application designed to grow alongside its user.

> 🚧 Aster is actively developed and currently at **v0.6.0 — Analytics & Productivity Suite**.

---

## 🚀 How to Run

### Requirements

- Python **3.13**
- Git
- Windows is currently the primary development environment

### Clone the Repository

```bash
git clone https://github.com/NeilNNP45-dev/Aster.git
cd Aster
```

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Virtual Environment

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run Aster directly through the virtual environment's Python executable instead.

**Windows Command Prompt**

```cmd
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Current external dependency:

```text
PySide6==6.8.2.1
```

### Run Aster

```bash
python main.py
```

Aster will create and use its local SQLite database as needed.

### 🔐 Privacy Note

Aster is designed as a **local-first application**.

Your Aster database is stored locally on your machine and is not part of the Git repository. SQLite database files and their sidecar files are ignored by Git.

GitHub authentication, when used, is session-only and is not stored in the database.

If you are testing Aster for the project, **do not share your `database/aster.db` file**, as it may contain your personal application data.

---

## ✨ Features

### ✅ Productivity

- Task management
- Daily goals and habit tracking
- Daily habit streaks
- Notes
- Pomodoro focus timer
- Automatic daily goal reset
- Persistent local data storage

### 🎓 College

- Course management
- Timetable
- Attendance tracking
- Assignment tracking
- Exam planning

### 💻 Coding

- Coding project management
- Coding sessions and timer
- Daily coding goals
- GitHub project metadata integration
- Session-only GitHub Personal Access Token authentication

### 💪 Fitness

- Workout logging
- Workout duration tracking
- Calories burned tracking
- Weight logging

### 📊 Analytics

Aster's analytics system brings activity from multiple areas of the application into a unified overview.

Current analytics include:

- Focus time
- Task completion
- Attendance
- Productivity summaries
- Coding activity
- Fitness activity
- Daily focus breakdowns
- Domain-level summaries
- Weekly reports and trends

---

## 🏠 Home Dashboard

The Home page provides a central overview of current activity.

It includes:

- Dynamic time-based greeting
- Current date
- Live productivity metrics
- Today's habit progress
- Today's focus time
- Active coding project count
- Quick actions for common workflows
- Interactive daily habit preview
- Recent version and feature information

The Home page communicates with the application through service-layer APIs rather than directly querying the database.

---

## ⚙️ Settings

The Settings page provides a central place for application and environment information.

Current information includes:

- Application version
- Application status
- Architecture information
- Active theme
- Local storage model
- SQLite database information
- Database size
- GitHub integration policy
- Session-only credential handling
- Project documentation access

---

## 🔐 Privacy & Security

Aster follows a **local-first architecture** designed to keep personal application data on the user's device.

### Local Data

Application data is stored locally using SQLite.

Aster does not require a cloud database or online account to operate.

The local database may contain information such as:

- Tasks
- Goals
- Notes
- Academic records
- Coding sessions
- Fitness records
- Analytics data

Database files and SQLite sidecar files are excluded from version control.

### GitHub Authentication

GitHub Personal Access Tokens are:

- Entered only when required
- Masked in the UI
- Kept in session memory
- Never stored in the SQLite database
- Never committed to source control
- Not intentionally included in logs or error messages

### Repository URL Protection

GitHub repository URLs opened by Aster are validated before being passed to the system browser.

Only supported HTTPS GitHub URLs are accepted.

### API Response Protection

The GitHub integration applies:

- Response size limits
- Content-Type validation
- Explicit network and JSON error handling
- Credential-safe error handling

---

## 🧱 Architecture

Aster follows a layered architecture that separates the user interface, application logic, database access, and persistent storage.

```text
┌───────────────────────────────┐
│             UI                │
│     PySide6 Pages & Widgets   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│           Services            │
│       Application Logic       │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│         Repositories          │
│       Database Access         │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│            SQLite             │
│       Local Application DB    │
└───────────────────────────────┘
```

### Architectural Principles

Aster aims to maintain:

- Clear separation of concerns
- UI → Service → Repository → Database boundaries
- Repository-owned SQL operations
- Reusable domain services
- Minimal external dependencies
- Explicit data ownership between modules
- Readable and maintainable code

---

## 🧪 Testing

Aster includes an automated Python `unittest` suite covering repositories, services, analytics, integrations, UI behavior, and security-related functionality.

Current milestone verification:

**40 tests  
0 failures  
0 errors  
0 ResourceWarnings**

Run the test suite with:

```powershell
.\.venv\Scripts\python.exe -W default -m unittest discover -s tests
```

Testing is treated as part of the development workflow rather than something added only before a release.

---

## 🤖 Development Approach

Aster is developed using an **AI-assisted, agentic development workflow**.

AI coding agents are used for activities including:

- Repository inspection
- Architecture analysis
- Implementation planning
- Code generation
- Refactoring
- Test generation
- Debugging
- Security reviews
- Documentation assistance

AI is not treated as an autonomous author of the project.

Architecture, requirements, feature scope, implementation decisions, testing, manual verification, security review, and final changes are directed and validated by the project developer.

The project is also intentionally being used as a learning environment. As Aster evolves, more components are being designed, reasoned about, and implemented directly to build a deeper understanding of the systems behind the application.

---

## 🌱 Roadmap

### ✅ Completed

- [x] Core PySide6 desktop application
- [x] SQLite persistence
- [x] Productivity module
- [x] College module
- [x] Coding module
- [x] Fitness module
- [x] GitHub integration
- [x] Analytics engine
- [x] Weekly analytics and reporting
- [x] Automatic daily goal reset
- [x] Home dashboard redesign
- [x] Settings redesign
- [x] Security hardening
- [x] Automated test coverage for core functionality

### 🔨 Current Milestone

#### v0.6.0 — Analytics & Productivity Suite

The current milestone focuses on bringing Aster's different modules together through unified analytics and a more useful dashboard experience.

### 🌼 Planned

#### v0.7 — Astra

Astra is Aster's planned intelligent analytics assistant.

The current direction is to explore building a **locally focused model** capable of interpreting Aster's aggregate analytics and producing useful insights without requiring personal activity data to be sent to an external AI service by default.

Planned research includes:

- Building a suitable training dataset
- Feature engineering
- Model experimentation
- Performance evaluation
- Local inference
- Analytics integration
- Privacy-preserving context handling

Astra is currently a **research and development project**, not a completed Aster feature.

### 🔭 Future Ideas

Potential future areas include:

- Additional analytics
- More advanced local intelligence
- Improved customization
- Expanded academic planning
- Additional integrations
- More extensive testing and observability

The roadmap will evolve as Aster develops.

---

## 📁 Project Structure

A simplified view of the current architecture:

```text
Aster/
│
├── assets/
│   └── themes/
│
├── database/
│   ├── connection.py
│   ├── models.py
│   ├── repositories/
│   └── schema.sql
│
├── services/
│   ├── analytics/
│   ├── coding/
│   ├── college/
│   ├── fitness/
│   ├── home/
│   ├── productivity/
│   └── settings/
│
├── ui/
│   ├── pages/
│   │   ├── home/
│   │   ├── productivity/
│   │   ├── college/
│   │   ├── coding/
│   │   ├── fitness/
│   │   ├── analytics/
│   │   └── settings/
│   └── main_window.py
│
├── tests/
│
├── main.py
├── requirements.txt
└── README.md
```

The structure may change as the application grows.

---

## 🌱 Project Philosophy

Aster is being built incrementally rather than as a single large application.

The goal is to:

1. Build useful features.
2. Understand the architecture behind them.
3. Test them.
4. Find weaknesses.
5. Improve the design.
6. Repeat.

The project is intentionally evolving alongside its developer's engineering journey.

Aster is not intended to be a finished product yet.

It is a growing software project, a learning environment, and a foundation for experimenting with more advanced systems such as **Astra**.

---

## 📜 License

This project is licensed under the **MIT License**.
