import sys
import unittest
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)


class TestFoundation(unittest.TestCase):

    def setUp(self):
        self.window = MainWindow()

    def test_window_properties(self):
        self.assertEqual(self.window.windowTitle(), "Aster")
        self.assertEqual(self.window.width(), 1000)
        self.assertEqual(self.window.height(), 800)

    def test_stacked_pages_count(self):
        self.assertEqual(self.window.stacked_widget.count(), 7)

    def test_navigation_switching(self):
        for index in range(7):
            self.window.sidebar.page_changed.emit(index)
            self.assertEqual(self.window.stacked_widget.currentIndex(), index)


if __name__ == "__main__":
    unittest.main()
