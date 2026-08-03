from typing import Dict, List, Optional

from database.connection import DatabaseConnection
from database.models import Assignment, AttendanceLog, Course, Exam, TimetableEntry
from database.repositories.college_repository import CollegeRepository


class CollegeService:
    """Business logic for the College module."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self._repo = CollegeRepository(db_conn=db_conn)

    def create_course(self, name: str, code: Optional[str] = None, instructor_name: Optional[str] = None,
                      credit_hours: int = 0, description: Optional[str] = None,
                      color_tag: Optional[str] = None) -> Course:
        course = Course(
            name=name,
            code=code or "",
            instructor_name=instructor_name or "",
            credit_hours=credit_hours,
            description=description or "",
            color_tag=color_tag or "#7C3AED",
            is_active=True,
        )
        return self._repo.add_course(course)

    def get_courses(self) -> List[Course]:
        return self._repo.get_all_courses()

    def update_course(self, course: Course) -> bool:
        return self._repo.update_course(course)

    def delete_course(self, course_id: int) -> bool:
        return self._repo.delete_course(course_id)

    def create_timetable_entry(self, course_id: int, day_of_week: str, start_time: str, end_time: str,
                               room: Optional[str] = None, location: Optional[str] = None,
                               recurring: bool = True, notes: Optional[str] = None) -> TimetableEntry:
        entry = TimetableEntry(
            course_id=course_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            room=room or "",
            location=location or "",
            recurring=recurring,
            notes=notes or "",
        )
        return self._repo.add_timetable_entry(entry)

    def get_timetable_entries(self, course_id: Optional[int] = None) -> List[TimetableEntry]:
        return self._repo.get_timetable_entries(course_id=course_id)

    def record_attendance(self, course_id: int, attendance_date: str, status: str, notes: Optional[str] = None) -> AttendanceLog:
        attendance = AttendanceLog(course_id=course_id, attendance_date=attendance_date, status=status, notes=notes or "")
        return self._repo.add_attendance_log(attendance)

    def get_attendance_logs(self, course_id: Optional[int] = None) -> List[AttendanceLog]:
        return self._repo.get_attendance_logs(course_id=course_id)

    def get_attendance_summary(self, course_id: int) -> Dict[str, float]:
        logs = self.get_attendance_logs(course_id=course_id)
        total = len(logs)
        present_count = sum(1 for log in logs if log.status == "Present")
        absent_count = sum(1 for log in logs if log.status == "Absent")
        late_count = sum(1 for log in logs if log.status == "Late")
        excused_count = sum(1 for log in logs if log.status == "Excused")

        if total == 0:
            percentage = 0.0
        else:
            percentage = round((present_count / total) * 100, 2)

        return {
            "total_records": total,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "excused_count": excused_count,
            "percentage": percentage,
        }

    def create_assignment(self, course_id: int, title: str, due_date: Optional[str] = None,
                          priority: str = "Medium", description: Optional[str] = None,
                          status: str = "Pending", estimated_minutes: int = 0) -> Assignment:
        assignment = Assignment(
            course_id=course_id,
            title=title,
            description=description or "",
            due_date=due_date,
            priority=priority,
            status=status,
            estimated_minutes=estimated_minutes,
        )
        return self._repo.add_assignment(assignment)

    def get_assignments(self, course_id: Optional[int] = None) -> List[Assignment]:
        return self._repo.get_assignments(course_id=course_id)

    def update_assignment(self, assignment: Assignment) -> bool:
        return self._repo.update_assignment(assignment)

    def delete_assignment(self, assignment_id: int) -> bool:
        return self._repo.delete_assignment(assignment_id)

    def create_exam(self, course_id: int, title: str, scheduled_at: str, location: Optional[str] = None,
                    exam_type: str = "Exam", status: str = "Planned", notes: Optional[str] = None) -> Exam:
        exam = Exam(
            course_id=course_id,
            title=title,
            exam_type=exam_type,
            scheduled_at=scheduled_at,
            location=location or "",
            status=status,
            notes=notes or "",
        )
        return self._repo.add_exam(exam)

    def get_exams(self, course_id: Optional[int] = None) -> List[Exam]:
        return self._repo.get_exams(course_id=course_id)

    def update_exam(self, exam: Exam) -> bool:
        return self._repo.update_exam(exam)

    def delete_exam(self, exam_id: int) -> bool:
        return self._repo.delete_exam(exam_id)
