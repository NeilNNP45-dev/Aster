import unittest

from database.connection import DatabaseConnection
from services.fitness.fitness_service import FitnessService


class TestFitnessService(unittest.TestCase):
    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.service = FitnessService(db_conn=self.conn)

    def tearDown(self):
        if hasattr(self, "conn") and self.conn is not None:
            self.conn.close()


    def test_log_workout_and_weight(self):
        workout = self.service.log_workout("Morning Run", workout_type="Cardio", duration_minutes=30, calories=250)
        self.assertIsNotNone(workout.id)
        self.assertEqual(workout.title, "Morning Run")

        weight = self.service.log_weight(72.5, note="Feeling good")
        self.assertIsNotNone(weight.id)
        self.assertEqual(weight.weight_kg, 72.5)

        self.assertEqual(len(self.service.list_workouts()), 1)
        self.assertEqual(len(self.service.list_weights()), 1)

    def test_weight_trend(self):
        self.service.log_weight(70.0)
        self.service.log_weight(69.5)
        trend = self.service.get_weight_trend()
        self.assertIsNotNone(trend)
        self.assertEqual(trend["trend"], "down")
