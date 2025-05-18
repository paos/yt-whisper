"""
Module for handling storage-related functionality including database paths.
"""

import sqlite3
from pathlib import Path

# Import migration functions
from ._migration import run_migration as _run_migration

# Run migration check on import
if __name__ != "__main__":
    _run_migration()


def get_database_path(db_name: str = "transcriptions.db") -> Path:
    """
    Returns the path to the SQLite database file, creating the parent
    directory if needed.

    The path is platform-specific:
    - Linux:   ~/.local/share/yt-whisper/<db_name>
    - Windows: C:\\Users\\<user>\\AppData\\Local\\yt-whisper\\<db_name>
    - macOS:   ~/Library/Application Support/yt-whisper/<db_name>

    Args:
        db_name: Name of the database file (default: "transcriptions.db")

    Returns:
        Path: Path to the database file
    """
    from ._migration import get_database_path as _get_database_path

    return _get_database_path(db_name)


def get_database_file(filename: str) -> Path:
    """
    Get the full path to a database file in the app's data directory.

    Args:
        filename: The name of the database file (e.g., 'logs.db')

    Returns:
        Path: Full path to the database file
    """
    db_path = get_database_path(filename)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


if __name__ != "__main__":
    _run_migration()


def get_database_connection(db_name: str = "transcriptions.db") -> "sqlite3.Connection":
    """
    Get a connection to the SQLite database.

    Args:
        db_name: Name of the database file (default: "transcriptions.db")

    Returns:
        sqlite3.Connection: Connection to the database
    """
    import sqlite3

    db_path = get_database_path(db_name)
    return sqlite3.connect(str(db_path))
