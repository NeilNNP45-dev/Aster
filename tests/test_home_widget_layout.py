import sys
import unittest
from unittest.mock import patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from database.models import DailyGoal
from services.home.home_service import HomeSummary
from ui.pages.home.page import HomePage


class DummyHomeService:
    def __init__(self, summary):
        self.summary = summary

    def get_home_summary(self):
        return self.summary

    def toggle_habit_completion(self, goal_id):
        return True

    def close(self):
        pass


class TestHomeWidgetLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def _build_page(self, summary):
        service = DummyHomeService(summary)
        with patch("ui.pages.home.page.HomeService", return_value=service):
            page = HomePage()
        page.resize(1100, 700)
        page.show()
        self.app.processEvents()
        return page

    def test_empty_goals_card_is_compact_and_progress_is_zero(self):
        page = self._build_page(HomeSummary())
        try:
            self.assertEqual(page._habits_progress_lbl.text(), "0 / 0 complete")
            self.assertEqual(page._habits_progress_bar.maximum(), 1)
            self.assertEqual(page._habits_progress_bar.value(), 0)
            self.assertLess(page._habits_card.height(), 260)
        finally:
            page.close()

    def test_progress_and_preview_height_follow_goal_count(self):
        goals = [DailyGoal(id=index, title=f"Goal {index}") for index in range(2)]
        page = self._build_page(
            HomeSummary(completed_habits_count=1, total_habits_count=2, today_habits=goals)
        )
        try:
            self.assertEqual(page._habits_progress_lbl.text(), "1 / 2 complete")
            self.assertEqual(page._habits_progress_bar.maximum(), 2)
            self.assertEqual(page._habits_progress_bar.value(), 1)
            self.assertLess(page._habits_scroll.height(), 220)
        finally:
            page.close()

    def test_many_goals_are_bounded_and_scrollable(self):
        goals = [DailyGoal(id=index, title=f"Goal {index}") for index in range(8)]
        page = self._build_page(
            HomeSummary(total_habits_count=8, today_habits=goals)
        )
        try:
            self.assertEqual(page._habits_scroll.height(), 220)
            self.assertEqual(
                page._habits_scroll.verticalScrollBarPolicy(),
                Qt.ScrollBarPolicy.ScrollBarAsNeeded,
            )
        finally:
            page.close()


if __name__ == "__main__":
    unittest.main()
