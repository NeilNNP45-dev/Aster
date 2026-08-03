-- 🌼 Aster Database Schema (Version 0.2)

PRAGMA foreign_keys = ON;

-- 1. Tasks Table (To-Do List)
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
    category TEXT DEFAULT 'General',
    due_date TEXT,
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK(is_completed IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 2. Daily Goals Table (Habit Checklist)
CREATE TABLE IF NOT EXISTS daily_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'General',
    is_completed INTEGER NOT NULL DEFAULT 0 CHECK(is_completed IN (0, 1)),
    reset_daily INTEGER NOT NULL DEFAULT 1 CHECK(reset_daily IN (0, 1)),
    streak_count INTEGER NOT NULL DEFAULT 0,
    last_completed_at TEXT
);

-- 3. Notes Table
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT DEFAULT '',
    category TEXT DEFAULT 'General',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 4. Pomodoro Sessions Log Table
CREATE TABLE IF NOT EXISTS pomodoro_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    duration_minutes INTEGER NOT NULL,
    session_type TEXT NOT NULL CHECK(session_type IN ('Work', 'Short Break', 'Long Break')),
    completed_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 5. College: Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT,
    instructor_name TEXT,
    credit_hours INTEGER NOT NULL DEFAULT 0,
    description TEXT DEFAULT '',
    color_tag TEXT DEFAULT '#7C3AED',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- 6. College: Timetable Entries Table
CREATE TABLE IF NOT EXISTS timetable_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    day_of_week TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    room TEXT DEFAULT '',
    location TEXT DEFAULT '',
    recurring INTEGER NOT NULL DEFAULT 1 CHECK(recurring IN (0, 1)),
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 7. College: Attendance Logs Table
CREATE TABLE IF NOT EXISTS attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused')),
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 8. College: Assignments Table
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    due_date TEXT,
    priority TEXT NOT NULL DEFAULT 'Medium' CHECK(priority IN ('High', 'Medium', 'Low')),
    status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'In Progress', 'Completed', 'Overdue')),
    estimated_minutes INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 9. College: Exams Table
CREATE TABLE IF NOT EXISTS exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    exam_type TEXT NOT NULL DEFAULT 'Exam',
    scheduled_at TEXT NOT NULL,
    location TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Planned' CHECK(status IN ('Planned', 'Upcoming', 'Completed', 'Canceled')),
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);
