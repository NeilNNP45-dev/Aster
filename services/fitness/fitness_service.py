from typing import List, Optional

from database.connection import DatabaseConnection
from database.models import WeightEntry, WorkoutEntry
from database.repositories.fitness_repository import FitnessRepository


class FitnessService:
    """Business logic for the Fitness module."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None):
        self._repo = FitnessRepository(db_conn=db_conn)

    def log_workout(self, title: str, workout_type: str = "Workout", duration_minutes: int = 0,
                    calories: int = 0, notes: str = "", performed_at: Optional[str] = None) -> WorkoutEntry:
        workout = WorkoutEntry(
            title=title,
            workout_type=workout_type,
            duration_minutes=duration_minutes,
            calories=calories,
            notes=notes,
            performed_at=performed_at,
        )
        return self._repo.add_workout(workout)

    def list_workouts(self) -> List[WorkoutEntry]:
        return self._repo.list_workouts()

    def log_weight(self, weight_kg: float, note: str = "", recorded_at: Optional[str] = None) -> WeightEntry:
        entry = WeightEntry(weight_kg=weight_kg, note=note, recorded_at=recorded_at)
        return self._repo.add_weight(entry)

    def list_weights(self) -> List[WeightEntry]:
        return self._repo.list_weights()

    def get_latest_weight(self) -> Optional[WeightEntry]:
        weights = self.list_weights()
        return weights[0] if weights else None

    def get_weight_trend(self) -> Optional[dict]:
        weights = self.list_weights()
        if len(weights) < 2:
            return None
        latest = weights[0]
        previous = weights[1]
        delta = round(latest.weight_kg - previous.weight_kg, 2)
        return {
            "latest": latest.weight_kg,
            "previous": previous.weight_kg,
            "delta": delta,
            "trend": "up" if delta > 0 else "down" if delta < 0 else "stable",
        }
