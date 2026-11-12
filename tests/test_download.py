import hashlib
import io
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from srag.download import verified_download


class DownloadTests(TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "sample.csv"
        self.body = b"sample;csv\n1;2\n"
        self.checksum = hashlib.sha256(self.body).hexdigest()

    def test_verified_file_is_reused_without_network(self):
        self.path.write_bytes(self.body)
        opener = MagicMock()
        result = verified_download(self.path, expected_hash=self.checksum, opener=opener)
        self.assertEqual(result, "already_verified")
        opener.assert_not_called()

    def test_existing_different_file_is_preserved(self):
        self.path.write_bytes(b"keep")
        with self.assertRaisesRegex(ValueError, "preservado"):
            verified_download(self.path, expected_hash=self.checksum)
        self.assertEqual(self.path.read_bytes(), b"keep")

    def test_invalid_download_never_becomes_the_source(self):
        with self.assertRaisesRegex(ValueError, "Hash divergente"):
            verified_download(self.path, expected_hash="0" * 64,
                              opener=lambda *args, **kwargs: io.BytesIO(self.body))
        self.assertFalse(self.path.exists())
        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_successful_download_matches_expected_content(self):
        result = verified_download(self.path, expected_hash=self.checksum,
                                   opener=lambda *args, **kwargs: io.BytesIO(self.body))
        self.assertEqual(result, "downloaded_and_verified")
        self.assertEqual(self.path.read_bytes(), self.body)
