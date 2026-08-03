import sys
import unittest

from PySide6.QtWidgets import QApplication

from services.productivity.pomodoro_service import PomodoroService, PomodoroState


class DummyRepo:
    def log_pomodoro_session(self, session):
        return session


class TestPomodoroService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_session_completed_signal_sees_updated_work_session_count(self):
        repo = DummyRepo()
        service = PomodoroService(repo=repo)
        seen_counts = []

        def on_completed(session_type, duration_minutes):
            seen_counts.append(service.work_sessions_completed)

        service.session_completed.connect(on_completed)
        service._state = PomodoroState.WORK
        service._seconds_remaining = 0

        service._on_tick()

        self.assertEqual(seen_counts, [1])
        self.assertEqual(service.work_sessions_completed, 1)


if __name__ == "__main__":
    unittest.main()
