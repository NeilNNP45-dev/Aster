import unittest
from database.connection import DatabaseConnection
from services.settings.settings_service import SettingsService


class TestSettingsService(unittest.TestCase):

    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.service = SettingsService(db_conn=self.conn)

    def tearDown(self):
        if hasattr(self, "service") and self.service is not None:
            self.service.close()

    def test_get_app_info(self):
        info = self.service.get_app_info()
        self.assertEqual(info.app_name, "Aster")
        self.assertEqual(info.version, "v0.6.0")

    def test_get_storage_info(self):
        storage = self.service.get_storage_info()
        self.assertIsNotNone(storage.db_filename)
        self.assertIn("Local", storage.privacy_mode)
        self.assertIn("WAL", storage.journal_mode)


if __name__ == "__main__":
    unittest.main()
