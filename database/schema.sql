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
