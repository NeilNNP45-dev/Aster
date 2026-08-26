import unittest

from database.connection import DatabaseConnection
from services.college.college_service import CollegeService


class TestCollegeService(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseConnection(db_path=":memory:")
        self.service = CollegeService(db_conn=self.db)

    def tearDown(self):
        if hasattr(self, "db") and self.db is not None:
            self.db.close()


    def test_course_crud_and_attendance_summary(self):
        course = self.service.create_course(
            name="Algorithms",
            code="CS201",
            instructor_name="Dr. Lee",
            credit_hours=3,
        )

        self.assertIsNotNone(course.id)
        self.assertEqual(course.name, "Algorithms")

        self.service.record_attendance(course_id=course.id, attendance_date="2026-08-01", status="Present")
        self.service.record_attendance(course_id=course.id, attendance_date="2026-08-02", status="Absent")

        summary = self.service.get_attendance_summary(course_id=course.id)
        self.assertEqual(summary["total_records"], 2)
        self.assertEqual(summary["present_count"], 1)
        self.assertEqual(summary["absent_count"], 1)
        self.assertEqual(summary["percentage"], 50.0)

    def test_assignment_and_exam_creation(self):
        course = self.service.create_course(name="Physics", code="PH101")
        assignment = self.service.create_assignment(
            course_id=course.id,
            title="Lab Report",
            due_date="2026-08-07",
            priority="High",
        )
        exam = self.service.create_exam(
            course_id=course.id,
            title="Midterm",
            scheduled_at="2026-08-10 10:00",
            location="Room 3",
        )

        self.assertEqual(assignment.title, "Lab Report")
        self.assertEqual(exam.title, "Midterm")
        self.assertEqual(self.service.get_assignments(course_id=course.id)[0].title, "Lab Report")
        self.assertEqual(self.service.get_exams(course_id=course.id)[0].title, "Midterm")


if __name__ == "__main__":
    unittest.main()
