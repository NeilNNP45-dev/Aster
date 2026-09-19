import sys
import unittest

from PySide6.QtWidgets import QApplication

from ui.pages.productivity.pomodoro_widget import PomodoroWidget


class DummyPomodoroRepo:
    def get_recent_pomodoro_sessions(self, limit=20):
        return []

    def log_pomodoro_session(self, session):
        return session


class TestPomodoroWidgetLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        self.widget = PomodoroWidget(DummyPomodoroRepo())
        self.widget.resize(900, 650)
        self.widget.show()
        self.app.processEvents()

    def tearDown(self):
        self.widget.close()
        self.widget.deleteLater()
        self.app.processEvents()

    def _in_widget(self, child):
        return child.rect().translated(child.mapTo(self.widget, child.rect().topLeft()))

    def test_timer_and_controls_have_separate_vertical_regions(self):
        timer_rect = self._in_widget(self.widget._timer_display)
        mode_rect = self._in_widget(self.widget._mode_frame)
        play_rect = self._in_widget(self.widget.play_btn)

        self.assertFalse(timer_rect.intersects(mode_rect))
        self.assertFalse(timer_rect.intersects(play_rect))
        self.assertGreaterEqual(self.widget._timer_lbl.height(), 120)

    def test_mode_buttons_and_secondary_controls_are_visible(self):
        for button in self.widget._mode_btns.values():
            self.assertTrue(button.isVisible())
            self.assertGreater(button.width(), 0)
            self.assertGreater(button.height(), 0)

        for button in (self.widget.skip_btn, self.widget.reset_btn):
            self.assertTrue(button.isVisible())
            self.assertGreater(button.width(), 0)
            self.assertGreater(button.height(), 0)


if __name__ == "__main__":
    unittest.main()
