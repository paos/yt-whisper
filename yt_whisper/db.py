# yt_whisper/db.py
import os
import pathlib
import sqlite3


def get_db_path() -> str:
    """
    Get the path to the database file.
    Returns a path relative to the package source directory.
    """
    # Get the directory where this module is located
    module_dir = pathlib.Path(__file__).parent

    # Create a data directory in the package directory
    data_dir = module_dir / "data"

    # Create directory if it doesn't exist
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)

    return str(data_dir / "youtube_transcripts.db")


def init_db(db_path: str | None = None) -> None:
    """Initialize the database if it doesn't exist."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create videos table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        channel TEXT,
        author TEXT,
        upload_date TEXT,
        duration INTEGER,
        description TEXT,
        transcription TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def save_to_db(data: dict, db_path: str | None = None) -> None:
    """Save video data to the database."""
    if db_path is None:
        db_path = get_db_path()

    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Initialize the database if needed
    init_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if the video already exists in the database
    cursor.execute("SELECT id FROM videos WHERE id = ?", (data["id"],))
    existing = cursor.fetchone()

    if existing:
        # Update existing record
        cursor.execute(
            """
        UPDATE videos SET
            url = ?,
            title = ?,
            channel = ?,
            author = ?,
            upload_date = ?,
            duration = ?,
            description = ?,
            transcription = ?,
            created_at = ?
        WHERE id = ?
        """,
            (
                data["url"],
                data["title"],
                data.get("channel", ""),
                data.get("author", ""),
                data.get("upload_date", ""),
                data.get("duration", 0),
                data.get("description", ""),
                data["transcription"],
                data["created_at"],
                data["id"],
            ),
        )
        print(f"Updated existing record for video ID: {data['id']}")
    else:
        # Insert new record
        cursor.execute(
            """
        INSERT INTO videos (
            id, url, title, channel, author, upload_date, duration, description,
            transcription, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["id"],
                data["url"],
                data["title"],
                data.get("channel", ""),
                data.get("author", ""),
                data.get("upload_date", ""),
                data.get("duration", 0),
                data.get("description", ""),
                data["transcription"],
                data["created_at"],
            ),
        )
        print(f"Inserted new record for video ID: {data['id']}")

    conn.commit()
    conn.close()


def get_transcript(youtube_id: str, db_path: str | None = None) -> dict | None:
    """Get transcript for a YouTube video from the database."""
    if db_path is None:
        db_path = get_db_path()

    if not os.path.exists(db_path):
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM videos WHERE id = ?", (youtube_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return dict(row)
    else:
        return None


def list_transcripts(limit: int = 10, db_path: str | None = None) -> list:
    """List transcripts in the database."""
    if db_path is None:
        db_path = get_db_path()

    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
    SELECT id, title, channel, author, created_at
    FROM videos
    ORDER BY created_at DESC
    LIMIT ?
    """,
        (limit,),
    )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
