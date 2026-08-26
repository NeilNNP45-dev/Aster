import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from database.connection import DatabaseConnection
from database.repositories.coding_repository import CodingRepository
from services.coding.github_service import GitHubService
from ui.pages.coding.github_widget import GitHubWidget


class TestGitHubSecurityAndReliability(unittest.TestCase):

    def setUp(self):
        self.conn = DatabaseConnection(db_path=":memory:")
        self.repo = CodingRepository(db_conn=self.conn)
        self.service = GitHubService(repo=self.repo)

    def tearDown(self):
        if hasattr(self, "conn") and self.conn is not None:
            self.conn.close()

    def test_url_validation(self):
        """Verify strict URL validation for GitHub repository links."""
        # Valid URLs
        self.assertTrue(GitHubWidget._is_valid_github_url("https://github.com/owner/repo"))
        self.assertTrue(GitHubWidget._is_valid_github_url("https://GITHUB.COM/owner/repo"))
        self.assertTrue(GitHubWidget._is_valid_github_url("https://github.com/owner/repo/issues/1"))

        # Invalid URLs
        self.assertFalse(GitHubWidget._is_valid_github_url("http://github.com/owner/repo"))
        self.assertFalse(GitHubWidget._is_valid_github_url("https://malicious-github.com/owner/repo"))
        self.assertFalse(GitHubWidget._is_valid_github_url("https://github.com.attacker.com/owner/repo"))
        self.assertFalse(GitHubWidget._is_valid_github_url("javascript:alert(1)"))
        self.assertFalse(GitHubWidget._is_valid_github_url("file:///etc/passwd"))
        self.assertFalse(GitHubWidget._is_valid_github_url(""))
        self.assertFalse(GitHubWidget._is_valid_github_url(None))

    @patch("services.coding.github_service.urlopen")
    def test_fetch_repo_metadata_valid_json(self, mock_urlopen):
        """Verify normal metadata fetching with JSON response."""
        mock_response = MagicMock()
        mock_response.headers.get.return_value = "application/json; charset=utf-8"
        mock_response.read.side_effect = [
            json.dumps({"html_url": "https://github.com/owner/repo", "description": "Test"}).encode("utf-8"),
            b"",
        ]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        meta = self.service.fetch_repo_metadata("owner/repo", token="ghp_secret123")
        self.assertIsNotNone(meta)
        self.assertEqual(meta.get("html_url"), "https://github.com/owner/repo")

    @patch("services.coding.github_service.urlopen")
    def test_fetch_repo_metadata_non_json_content_type(self, mock_urlopen):
        """Verify non-JSON Content-Type is rejected."""
        mock_response = MagicMock()
        mock_response.headers.get.return_value = "text/html"
        mock_urlopen.return_value.__enter__.return_value = mock_response

        meta = self.service.fetch_repo_metadata("owner/repo")
        self.assertIsNone(meta)

    @patch("services.coding.github_service.urlopen")
    def test_fetch_repo_metadata_exceeding_max_size(self, mock_urlopen):
        """Verify responses exceeding maximum size limit (1 MB) are rejected."""
        mock_response = MagicMock()
        mock_response.headers.get.return_value = "application/json"
        # 1MB + 100 bytes chunk
        oversized_chunk = b"x" * (1024 * 1024 + 100)
        mock_response.read.side_effect = [oversized_chunk]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        meta = self.service.fetch_repo_metadata("owner/repo")
        self.assertIsNone(meta)

    @patch("services.coding.github_service.urlopen")
    def test_fetch_repo_metadata_malformed_json(self, mock_urlopen):
        """Verify malformed JSON is handled safely without crashing."""
        mock_response = MagicMock()
        mock_response.headers.get.return_value = "application/json"
        mock_response.read.side_effect = [b"{invalid_json:", b""]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        meta = self.service.fetch_repo_metadata("owner/repo")
        self.assertIsNone(meta)

    @patch("services.coding.github_service.urlopen")
    def test_fetch_repo_metadata_http_error(self, mock_urlopen):
        """Verify HTTP errors return None safely without raising or exposing tokens."""
        mock_urlopen.side_effect = HTTPError("https://api.github.com", 404, "Not Found", {}, None)

        meta = self.service.fetch_repo_metadata("owner/repo", token="ghp_secret_token")
        self.assertIsNone(meta)


if __name__ == "__main__":
    unittest.main()
