import unittest
from database.connection import DatabaseConnection
from database.models import Task, DailyGoal, Note, PomodoroSession
from database.repositories.productivity_repository import ProductivityRepository


class TestDatabaseFoundation(unittest.TestCase):

    def setUp(self):
        # Use an isolated in-memory SQLite database for test execution
        self.db = DatabaseConnection(db_path=":memory:")
        self.repo = ProductivityRepository(db_conn=self.db)

    def tearDown(self):
        if hasattr(self, "db"):
            self.db.close()

    def test_schema_tables_exist(self):
        """Verify all 4 core productivity tables are created successfully."""
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row["name"] for row in cursor.fetchall()}
            
        expected_tables = {"tasks", "daily_goals", "notes", "pomodoro_sessions"}
        self.assertTrue(expected_tables.issubset(tables))

    def test_foreign_keys_enabled(self):
        """Verify foreign key enforcement is active."""
        with self.db.get_cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys;")
            fk_status = cursor.fetchone()[0]
            self.assertEqual(fk_status, 1)

    # ==================== TASKS TESTS ====================

    def test_task_crud(self):
        # 1. Create
        new_task = Task(title="Complete Phase 1 SQLite", description="Write schema and repository", priority="High", category="Coding")
        saved_task = self.repo.add_task(new_task)
        self.assertIsNotNone(saved_task.id)
        self.assertIsNotNone(saved_task.created_at)

        # 2. Read All & Read By ID
        tasks = self.repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Complete Phase 1 SQLite")

        fetched_task = self.repo.get_task_by_id(saved_task.id)
        self.assertIsNotNone(fetched_task)
        self.assertEqual(fetched_task.description, "Write schema and repository")

        # 3. Toggle Completion
        self.repo.toggle_task_completion(saved_task.id)
        updated_task = self.repo.get_task_by_id(saved_task.id)
        self.assertTrue(updated_task.is_completed)

        # 4. Update
        updated_task.title = "Complete Phase 1 SQLite & Verify Tests"
        self.assertTrue(self.repo.update_task(updated_task))
        refetched = self.repo.get_task_by_id(saved_task.id)
        self.assertEqual(refetched.title, "Complete Phase 1 SQLite & Verify Tests")

        # 5. Delete
        self.assertTrue(self.repo.delete_task(saved_task.id))
        self.assertEqual(len(self.repo.get_all_tasks()), 0)

    # ==================== DAILY GOALS TESTS ====================

    def test_daily_goals_crud(self):
        goal = DailyGoal(title="Drink 2L Water", category="Fitness", streak_count=3)
        saved_goal = self.repo.add_daily_goal(goal)
        self.assertIsNotNone(saved_goal.id)

        goals = self.repo.get_daily_goals()
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0].streak_count, 3)

        # Toggle completion & verify streak increments
        self.repo.toggle_goal_completion(saved_goal.id)
        updated_goals = self.repo.get_daily_goals()
        self.assertTrue(updated_goals[0].is_completed)
        self.assertEqual(updated_goals[0].streak_count, 4)

        # Delete
        self.assertTrue(self.repo.delete_daily_goal(saved_goal.id))
        self.assertEqual(len(self.repo.get_daily_goals()), 0)

    # ==================== NOTES TESTS ====================

    def test_notes_crud(self):
        note = Note(title="Architecture Meeting", content="Discuss SQLite repository design", category="Work")
        saved_note = self.repo.add_note(note)
        self.assertIsNotNone(saved_note.id)
        self.assertIsNotNone(saved_note.created_at)

        notes = self.repo.get_all_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].title, "Architecture Meeting")

        # Update note
        saved_note.content = "Discuss SQLite repository design and unit test coverage"
        self.assertTrue(self.repo.update_note(saved_note))
        updated_note = self.repo.get_note_by_id(saved_note.id)
        self.assertIn("unit test coverage", updated_note.content)

        # Delete
        self.assertTrue(self.repo.delete_note(saved_note.id))
        self.assertEqual(len(self.repo.get_all_notes()), 0)

    # ==================== POMODORO SESSIONS TESTS ====================

    def test_pomodoro_sessions(self):
        session = PomodoroSession(duration_minutes=25, session_type="Work")
        saved_session = self.repo.log_pomodoro_session(session)
        self.assertIsNotNone(saved_session.id)
        self.assertIsNotNone(saved_session.completed_at)

        recent_sessions = self.repo.get_recent_pomodoro_sessions(limit=10)
        self.assertEqual(len(recent_sessions), 1)
        self.assertEqual(recent_sessions[0].session_type, "Work")


if __name__ == "__main__":
    unittest.main()
