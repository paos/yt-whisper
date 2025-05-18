"""Tests for the storage module."""

import sys
import tempfile
from pathlib import Path
from unittest import TestCase, mock

# Import the functions we'll test
from yt_whisper.storage import get_database_connection, get_database_path


class TestStorage(TestCase):
    """Test storage module functionality."""

    def test_get_database_path_default(self) -> None:
        """Test getting the default database path."""
        db_path = get_database_path()
        assert db_path.name == "transcriptions.db"
        assert "yt-whisper" in str(db_path)
        assert db_path.parent.exists()

    def test_get_database_path_custom_name(self) -> None:
        """Test getting a database path with a custom name."""
        db_name = "test_db.sqlite"
        db_path = get_database_path(db_name)
        assert db_path.name == db_name
        assert "yt-whisper" in str(db_path)
        assert db_path.parent.exists()

    def test_get_database_connection(self) -> None:
        """Test getting a database connection."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = Path(tmp_file.name)

        try:
            # Test creating a new database
            with get_database_connection(str(db_path)) as conn:
                cursor = conn.cursor()
                # Test if we can create a table and insert data
                cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
                cursor.execute("INSERT INTO test (name) VALUES ('test')")
                conn.commit()

                # Verify the data was inserted
                cursor.execute("SELECT name FROM test WHERE id = 1")
                result = cursor.fetchone()
                assert result[0] == "test"
        finally:
            # Clean up
            if db_path.exists():
                db_path.unlink()

    def test_platform_specific_paths(self) -> None:
        """Test that paths are platform-specific."""
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = str(Path(temp_dir) / "test" / "path" / "yt-whisper")

            # Patch the user_data_dir function to return our test path
            with mock.patch("platformdirs.user_data_dir", return_value=test_path):
                # Clear module cache to ensure we get fresh imports
                modules_to_clear = ["yt_whisper._migration", "yt_whisper.storage"]
                for module in modules_to_clear:
                    if module in sys.modules:
                        del sys.modules[module]

                # Import after patching
                from yt_whisper.storage import get_database_path

                db_path = get_database_path()

                # The path should start with our test path
                assert str(db_path).startswith(test_path)
                # The filename should be the default
                assert db_path.name == "transcriptions.db"
                # The parent directory should be the test path
                assert str(db_path.parent) == test_path
                # The parent directory should exist (created by get_database_path)
                assert db_path.parent.exists()
                # The database file itself shouldn't exist yet
                assert not db_path.exists()
