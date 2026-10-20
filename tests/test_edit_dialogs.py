import sys
import unittest

try:
    from PySide6.QtWidgets import QApplication
    _PYSIDE_AVAILABLE = True
except ModuleNotFoundError:
    _PYSIDE_AVAILABLE = False

if _PYSIDE_AVAILABLE:
    from database.models import CodingProject, Course, DailyGoal, Task
    from ui.dialogs.course_dialog import CourseDialog
    from ui.dialogs.goal_dialog import GoalDialog
    from ui.dialogs.project_dialog import ProjectDialog
    from ui.dialogs.task_dialog import TaskDialog


@unittest.skipUnless(_PYSIDE_AVAILABLE, "PySide6 not installed")
class TestEditDialogs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_task_dialog_prefills_and_preserves_identity(self):
        existing = Task(
            id=7,
            title="Old task",
            description="desc",
            priority="High",
            category="Study",
            due_date="2026-10-30",
            is_completed=True,
            created_at="2026-10-20 10:00:00",
        )
        dialog = TaskDialog(task=existing)
        try:
            self.assertEqual(dialog.windowTitle(), "Edit Task")
            dialog._title_input.setText("Updated task")
            updated = dialog.get_task()
            self.assertEqual(updated.id, 7)
            self.assertEqual(updated.title, "Updated task")
            self.assertTrue(updated.is_completed)
            self.assertEqual(updated.created_at, existing.created_at)
        finally:
            dialog.close()

    def test_goal_dialog_prefills_and_preserves_streak(self):
        existing = DailyGoal(
            id=2,
            title="Read 20 pages",
            category="Study",
            is_completed=True,
            reset_daily=False,
            streak_count=5,
            last_completed_at="2026-10-19 20:00:00",
        )
        dialog = GoalDialog(goal=existing)
        try:
            self.assertEqual(dialog.windowTitle(), "Edit Daily Goal")
            dialog._title_input.setText("Read 30 pages")
            updated = dialog.get_goal()
            self.assertEqual(updated.id, 2)
            self.assertEqual(updated.title, "Read 30 pages")
            self.assertEqual(updated.streak_count, 5)
            self.assertFalse(updated.reset_daily)
        finally:
            dialog.close()

    def test_course_and_project_dialogs_prefill_existing_values(self):
        existing_course = Course(id=10, name="Math", code="MTH101", instructor_name="Dr. A", credit_hours=4)
        course_dialog = CourseDialog(course=existing_course)
        try:
            self.assertEqual(course_dialog.windowTitle(), "Edit Course")
            self.assertEqual(course_dialog._name_input.text(), "Math")
            updated_course = course_dialog.get_course()
            self.assertEqual(updated_course.id, 10)
        finally:
            course_dialog.close()

        existing_project = CodingProject(id=4, name="Aster", repo_path="/tmp/aster", github_full_name="owner/repo")
        project_dialog = ProjectDialog(project=existing_project)
        try:
            self.assertEqual(project_dialog.windowTitle(), "Edit Coding Project")
            self.assertEqual(project_dialog._name.text(), "Aster")
            updated_project = project_dialog.get_project()
            self.assertEqual(updated_project.id, 4)
            self.assertEqual(updated_project.github_full_name, "owner/repo")
        finally:
            project_dialog.close()


if __name__ == "__main__":
    unittest.main()
