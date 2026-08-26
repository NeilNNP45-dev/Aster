from typing import List, Optional

from database.connection import DatabaseConnection
from database.models import Course, TimetableEntry, AttendanceLog, Assignment, Exam


class CollegeRepository:
    """Repository handling all CRUD database operations for College entities."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self.db = db_conn or DatabaseConnection()

    def close(self):
        if hasattr(self, "db") and self.db is not None:
            self.db.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


    def add_course(self, course: Course) -> Course:
        query = """
            INSERT INTO courses (name, code, instructor_name, credit_hours, description, color_tag, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    course.name,
                    course.code,
                    course.instructor_name,
                    course.credit_hours,
                    course.description,
                    course.color_tag,
                    1 if course.is_active else 0,
                ),
            )
            course.id = cursor.lastrowid
        return course

    def get_all_courses(self) -> List[Course]:
        query = "SELECT * FROM courses ORDER BY name ASC"
        courses = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                courses.append(
                    Course(
                        id=row["id"],
                        name=row["name"],
                        code=row["code"],
                        instructor_name=row["instructor_name"],
                        credit_hours=row["credit_hours"],
                        description=row["description"],
                        color_tag=row["color_tag"],
                        is_active=bool(row["is_active"]),
                        created_at=row["created_at"],
                    )
                )
        return courses

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        query = "SELECT * FROM courses WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (course_id,))
            row = cursor.fetchone()
            if row:
                return Course(
                    id=row["id"],
                    name=row["name"],
                    code=row["code"],
                    instructor_name=row["instructor_name"],
                    credit_hours=row["credit_hours"],
                    description=row["description"],
                    color_tag=row["color_tag"],
                    is_active=bool(row["is_active"]),
                    created_at=row["created_at"],
                )
        return None

    def update_course(self, course: Course) -> bool:
        if course.id is None:
            return False
        query = """
            UPDATE courses
            SET name = ?, code = ?, instructor_name = ?, credit_hours = ?, description = ?, color_tag = ?, is_active = ?
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    course.name,
                    course.code,
                    course.instructor_name,
                    course.credit_hours,
                    course.description,
                    course.color_tag,
                    1 if course.is_active else 0,
                    course.id,
                ),
            )
            return cursor.rowcount > 0

    def delete_course(self, course_id: int) -> bool:
        query = "DELETE FROM courses WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (course_id,))
            return cursor.rowcount > 0

    def add_timetable_entry(self, entry: TimetableEntry) -> TimetableEntry:
        query = """
            INSERT INTO timetable_entries (course_id, day_of_week, start_time, end_time, room, location, recurring, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    entry.course_id,
                    entry.day_of_week,
                    entry.start_time,
                    entry.end_time,
                    entry.room,
                    entry.location,
                    1 if entry.recurring else 0,
                    entry.notes,
                ),
            )
            entry.id = cursor.lastrowid
        return entry

    def get_timetable_entries(self, course_id: Optional[int] = None) -> List[TimetableEntry]:
        if course_id is not None:
            query = "SELECT * FROM timetable_entries WHERE course_id = ? ORDER BY day_of_week ASC, start_time ASC"
            params = (course_id,)
        else:
            query = "SELECT * FROM timetable_entries ORDER BY day_of_week ASC, start_time ASC"
            params = ()

        entries = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                entries.append(
                    TimetableEntry(
                        id=row["id"],
                        course_id=row["course_id"],
                        day_of_week=row["day_of_week"],
                        start_time=row["start_time"],
                        end_time=row["end_time"],
                        room=row["room"],
                        location=row["location"],
                        recurring=bool(row["recurring"]),
                        notes=row["notes"],
                        created_at=row["created_at"],
                    )
                )
        return entries

    def update_timetable_entry(self, entry: TimetableEntry) -> bool:
        if entry.id is None:
            return False
        query = """
            UPDATE timetable_entries
            SET course_id = ?, day_of_week = ?, start_time = ?, end_time = ?, room = ?, location = ?, recurring = ?, notes = ?
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    entry.course_id,
                    entry.day_of_week,
                    entry.start_time,
                    entry.end_time,
                    entry.room,
                    entry.location,
                    1 if entry.recurring else 0,
                    entry.notes,
                    entry.id,
                ),
            )
            return cursor.rowcount > 0

    def delete_timetable_entry(self, entry_id: int) -> bool:
        query = "DELETE FROM timetable_entries WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (entry_id,))
            return cursor.rowcount > 0

    def add_attendance_log(self, attendance: AttendanceLog) -> AttendanceLog:
        query = """
            INSERT INTO attendance_logs (course_id, attendance_date, status, notes)
            VALUES (?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (attendance.course_id, attendance.attendance_date, attendance.status, attendance.notes))
            attendance.id = cursor.lastrowid
        return attendance

    def get_attendance_logs(self, course_id: Optional[int] = None) -> List[AttendanceLog]:
        if course_id is not None:
            query = "SELECT * FROM attendance_logs WHERE course_id = ? ORDER BY attendance_date DESC"
            params = (course_id,)
        else:
            query = "SELECT * FROM attendance_logs ORDER BY attendance_date DESC"
            params = ()

        logs = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                logs.append(
                    AttendanceLog(
                        id=row["id"],
                        course_id=row["course_id"],
                        attendance_date=row["attendance_date"],
                        status=row["status"],
                        notes=row["notes"],
                        created_at=row["created_at"],
                    )
                )
        return logs

    def add_assignment(self, assignment: Assignment) -> Assignment:
        query = """
            INSERT INTO assignments (course_id, title, description, due_date, priority, status, estimated_minutes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    assignment.course_id,
                    assignment.title,
                    assignment.description,
                    assignment.due_date,
                    assignment.priority,
                    assignment.status,
                    assignment.estimated_minutes,
                ),
            )
            assignment.id = cursor.lastrowid
        return assignment

    def get_assignments(self, course_id: Optional[int] = None) -> List[Assignment]:
        if course_id is not None:
            query = "SELECT * FROM assignments WHERE course_id = ? ORDER BY due_date ASC, id ASC"
            params = (course_id,)
        else:
            query = "SELECT * FROM assignments ORDER BY due_date ASC, id ASC"
            params = ()

        assignments = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                assignments.append(
                    Assignment(
                        id=row["id"],
                        course_id=row["course_id"],
                        title=row["title"],
                        description=row["description"],
                        due_date=row["due_date"],
                        priority=row["priority"],
                        status=row["status"],
                        estimated_minutes=row["estimated_minutes"],
                        created_at=row["created_at"],
                    )
                )
        return assignments

    def update_assignment(self, assignment: Assignment) -> bool:
        if assignment.id is None:
            return False
        query = """
            UPDATE assignments
            SET course_id = ?, title = ?, description = ?, due_date = ?, priority = ?, status = ?, estimated_minutes = ?
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    assignment.course_id,
                    assignment.title,
                    assignment.description,
                    assignment.due_date,
                    assignment.priority,
                    assignment.status,
                    assignment.estimated_minutes,
                    assignment.id,
                ),
            )
            return cursor.rowcount > 0

    def delete_assignment(self, assignment_id: int) -> bool:
        query = "DELETE FROM assignments WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (assignment_id,))
            return cursor.rowcount > 0

    def add_exam(self, exam: Exam) -> Exam:
        query = """
            INSERT INTO exams (course_id, title, exam_type, scheduled_at, location, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    exam.course_id,
                    exam.title,
                    exam.exam_type,
                    exam.scheduled_at,
                    exam.location,
                    exam.status,
                    exam.notes,
                ),
            )
            exam.id = cursor.lastrowid
        return exam

    def get_exams(self, course_id: Optional[int] = None) -> List[Exam]:
        if course_id is not None:
            query = "SELECT * FROM exams WHERE course_id = ? ORDER BY scheduled_at ASC"
            params = (course_id,)
        else:
            query = "SELECT * FROM exams ORDER BY scheduled_at ASC"
            params = ()

        exams = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            for row in cursor.fetchall():
                exams.append(
                    Exam(
                        id=row["id"],
                        course_id=row["course_id"],
                        title=row["title"],
                        exam_type=row["exam_type"],
                        scheduled_at=row["scheduled_at"],
                        location=row["location"],
                        status=row["status"],
                        notes=row["notes"],
                        created_at=row["created_at"],
                    )
                )
        return exams

    def update_exam(self, exam: Exam) -> bool:
        if exam.id is None:
            return False
        query = """
            UPDATE exams
            SET course_id = ?, title = ?, exam_type = ?, scheduled_at = ?, location = ?, status = ?, notes = ?
            WHERE id = ?
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    exam.course_id,
                    exam.title,
                    exam.exam_type,
                    exam.scheduled_at,
                    exam.location,
                    exam.status,
                    exam.notes,
                    exam.id,
                ),
            )
            return cursor.rowcount > 0

    def delete_exam(self, exam_id: int) -> bool:
        query = "DELETE FROM exams WHERE id = ?"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (exam_id,))
            return cursor.rowcount > 0
