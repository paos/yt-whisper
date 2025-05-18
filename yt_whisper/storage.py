"""
Module for handling storage-related functionality including database paths.
"""

import sqlite3
from pathlib import Path

from platformdirs import user_data_dir


def get_database_path(db_name: str = "logs.db") -> Path:
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
    # Get the platform-specific application data directory
    app_dir = Path(user_data_dir("yt-whisper"))

    # Create the directory if it doesn't exist
    app_dir.mkdir(parents=True, exist_ok=True)

    # Return the path to the database file
    return app_dir / db_name


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


def get_database_connection(db_name: str = "transcriptions.db") -> "sqlite3.Connection":
    """
    Get a connection to the SQLite database.

    Args:
        db_name: Name of the database file (default: "transcriptions.db")

    Returns:
        sqlite3.Connection: Connection to the database
    """
    db_path = get_database_path(db_name)
    return sqlite3.connect(str(db_path))
