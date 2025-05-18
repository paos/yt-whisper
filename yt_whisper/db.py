# yt_whisper/db.py
import json
import os
import sqlite3


def get_db_path() -> str:
    """
    Get the path to the database file.
    Returns the path to the platform-specific logs.db location.
    """
    from yt_whisper.storage import get_database_path

    return str(get_database_path("logs.db"))


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
        metadata TEXT,
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
            metadata = ?,
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
                json.dumps(data.get("metadata", {})),
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
            transcription, metadata, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                json.dumps(data.get("metadata", {})),
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
        result = dict(row)
        # Parse metadata JSON if it exists
        if result.get("metadata"):
            try:
                result["metadata"] = json.loads(result["metadata"])
            except json.JSONDecodeError:
                result["metadata"] = {}
        else:
            result["metadata"] = {}
        return result
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


def delete_video(youtube_id: str, db_path: str | None = None) -> bool:
    """
    Delete a video from the database.

    Args:
        youtube_id: The YouTube video ID to delete
        db_path: Optional custom path to the database file

    Returns:
        bool: True if a video was deleted, False otherwise
    """
    if db_path is None:
        db_path = get_db_path()

    if not os.path.exists(db_path):
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Try to delete the video
    cursor.execute("DELETE FROM videos WHERE id = ?", (youtube_id,))
    rows_affected = cursor.rowcount

    conn.commit()
    conn.close()

    return rows_affected > 0
