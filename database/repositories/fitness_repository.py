from datetime import datetime
from typing import List, Optional

from database.connection import DatabaseConnection
from database.models import WeightEntry, WorkoutEntry


class FitnessRepository:
    """Repository for Fitness module persistence."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self.db = db_conn or DatabaseConnection()

    def add_workout(self, workout: WorkoutEntry) -> WorkoutEntry:
        query = """
            INSERT INTO fitness_workouts (title, workout_type, duration_minutes, calories, notes, performed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (
                    workout.title,
                    workout.workout_type,
                    workout.duration_minutes,
                    workout.calories,
                    workout.notes,
                    workout.performed_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
            workout.id = cursor.lastrowid
        return workout

    def list_workouts(self) -> List[WorkoutEntry]:
        query = "SELECT * FROM fitness_workouts ORDER BY id DESC"
        workouts: List[WorkoutEntry] = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                workouts.append(
                    WorkoutEntry(
                        id=row["id"],
                        title=row["title"],
                        workout_type=row["workout_type"],
                        duration_minutes=row["duration_minutes"],
                        calories=row["calories"],
                        notes=row["notes"],
                        performed_at=row["performed_at"],
                        created_at=row["created_at"],
                    )
                )
        return workouts

    def add_weight(self, entry: WeightEntry) -> WeightEntry:
        query = """
            INSERT INTO fitness_weights (weight_kg, note, recorded_at)
            VALUES (?, ?, ?)
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(
                query,
                (entry.weight_kg, entry.note, entry.recorded_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            entry.id = cursor.lastrowid
        return entry

    def list_weights(self) -> List[WeightEntry]:
        query = "SELECT * FROM fitness_weights ORDER BY id DESC"
        weights: List[WeightEntry] = []
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                weights.append(
                    WeightEntry(
                        id=row["id"],
                        weight_kg=row["weight_kg"],
                        note=row["note"],
                        recorded_at=row["recorded_at"],
                        created_at=row["created_at"],
                    )
                )
        return weights
