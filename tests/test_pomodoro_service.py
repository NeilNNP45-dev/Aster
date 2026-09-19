import sys
import unittest

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

from services.productivity.pomodoro_service import (
    PomodoroService,
    PomodoroSettings,
    PomodoroState,
)


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

    def test_durations_persist_and_are_used_for_new_sessions(self):
        settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "AsterTests", "pomodoro")
        settings.clear()
        store = PomodoroSettings(settings)
        service = PomodoroService(repo=DummyRepo(), settings=store)

        service.configure_durations(30, 7, 20)
        reloaded = PomodoroService(repo=DummyRepo(), settings=PomodoroSettings(settings))

        self.assertEqual(reloaded.durations.focus_minutes, 30)
        reloaded.start(PomodoroState.WORK)
        self.assertEqual(reloaded.seconds_remaining, 30 * 60)
        reloaded.stop()
        settings.clear()

    def test_changing_settings_does_not_change_active_session(self):
        settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, "AsterTests", "active")
        settings.clear()
        service = PomodoroService(repo=DummyRepo(), settings=PomodoroSettings(settings))
        service.start(PomodoroState.WORK)
        service._seconds_remaining = 123

        service.configure_durations(40, 10, 25)
        service.reset()

        self.assertEqual(service.seconds_remaining, 25 * 60)
        service.stop()
        settings.clear()


if __name__ == "__main__":
    unittest.main()
