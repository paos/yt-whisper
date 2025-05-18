"""Migration utilities for yt-whisper."""

import shutil
from pathlib import Path

from platformdirs import user_data_dir


def get_database_path(db_name: str = "transcriptions.db") -> Path:
    """Get the platform-specific database path."""
    app_dir = Path(user_data_dir("yt-whisper"))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / db_name


def get_legacy_db_path() -> Path:
    """Get the path to the legacy database."""
    return Path.home() / ".yt-whisper" / "logs.db"


def needs_migration() -> bool:
    """Check if migration is needed."""
    legacy_path = get_legacy_db_path()
    if not legacy_path.exists():
        return False

    new_path = get_database_path("logs.db")
    return not new_path.exists()


def run_migration() -> bool:
    """Run the database migration if needed."""
    if not needs_migration():
        return False

    legacy_path = get_legacy_db_path()
    new_path = get_database_path("logs.db")

    print(f"Migrating database from: {legacy_path}")
    print(f"To new location: {new_path}")

    try:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(legacy_path), str(new_path))

        if not new_path.exists():
            raise Exception("Failed to verify database copy")

        print(f"Successfully migrated database to: {new_path}")
        print(f"Original database preserved at: {legacy_path}")
        return True

    except Exception as e:
        print(f"Error during database migration: {e}")
        print("The original database remains at:", legacy_path)
        return False
