import unittest

from database.connection import DatabaseConnection
from database.repositories.coding_repository import CodingRepository
from services.coding.coding_timer_service import CodingTimerService


class TestCodingTimerService(unittest.TestCase):
    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.repo = CodingRepository(db_conn=self.conn)
        self.timer = CodingTimerService(repo=self.repo)

    def tearDown(self):
        if hasattr(self, "conn") and self.conn is not None:
            self.conn.close()


    def test_basic_timer_logs_session(self):
        # start a very short timer and simulate ticks
        self.timer.start(duration_seconds=2, project_id=None)
        # simulate two ticks
        self.timer._on_tick()
        self.timer._on_tick()
        # after completion, repository should have a session
        sessions = self.repo.get_sessions_by_project(None)
        self.assertTrue(len(sessions) >= 1)


if __name__ == "__main__":
    unittest.main()
