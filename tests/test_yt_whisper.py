# tests/test_yt_whisper.py
import os
import tempfile
import pytest
import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
import sqlite3

from yt_whisper.cli import cli
from yt_whisper.lib import extract_youtube_id
from yt_whisper.db import init_db, save_to_db, get_transcript


def test_extract_youtube_id():
    """Test YouTube ID extraction from different URL formats."""
    # Standard format
    assert extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Short format
    assert extract_youtube_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # Embed format
    assert extract_youtube_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    # With additional parameters
    assert extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s") == "dQw4w9WgXcQ"

    # Invalid URL
    assert extract_youtube_id("https://example.com") is None


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    # Initialize the database schema
    init_db(db_path)

    # Insert sample data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO videos
                   VALUES ('sample123',
                           'https://www.youtube.com/watch?v=sample123',
                           'Sample Video',
                           'Sample Channel',
                           'Sample Author',
                           '20240501',
                           300,
                           'Sample description',
                           'This is a sample transcription.',
                           '2024-05-01T12:00:00Z')
                   ''')
    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    os.unlink(db_path)


@patch('tempfile.TemporaryDirectory')
@patch('subprocess.run')
def test_download_and_transcribe(mock_subprocess_run, mock_temp_dir, monkeypatch):
    """Test the download_and_transcribe function."""
    from yt_whisper.lib import download_and_transcribe

    # Setup the mocks
    temp_dir = tempfile.mkdtemp()
    mock_temp_dir.return_value.__enter__.return_value = temp_dir

    # Create mock metadata file
    os.makedirs(temp_dir, exist_ok=True)
    metadata_path = os.path.join(temp_dir, "ytw_metadata_dQw4w9WgXcQ.info.json")
    with open(metadata_path, 'w') as f:
        f.write('''
        {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "channel": "Test Channel",
            "uploader": "Test Author",
            "upload_date": "20240501",
            "duration": 212,
            "description": "Test description"
        }
        ''')

    # Create mock transcript file
    transcript_path = os.path.join(temp_dir, "ytw_transcript_dQw4w9WgXcQ.txt")
    with open(transcript_path, 'w') as f:
        f.write("This is a test transcription.")

    # Mock the subprocess calls
    mock_subprocess_run.return_value = MagicMock(stdout="Test output")

    # Patch open to read our mock files
    original_open = open
    def mock_open_read(path, *args, **kwargs):
        if 'transcript' in path:
            return MagicMock(__enter__=lambda *args: MagicMock(
                read=lambda: "This is a test transcription."
            ))
        elif 'metadata' in path and 'info.json' in path:
            # Return a mock for metadata file to avoid recursion
            mock_file = MagicMock()
            mock_file.__enter__ = MagicMock(return_value=MagicMock(
                read=lambda: json.dumps({
                    "id": "dQw4w9WgXcQ",
                    "title": "Test Video",
                    "channel": "Test Channel",
                    "uploader": "Test Author",
                    "upload_date": "20240501",
                    "duration": 212,
                    "description": "Test description"
                })
            ))
            return mock_file
        else:
            # Use the original open for other files
            return original_open(path, *args, **kwargs)

    # Run the function
    with patch('builtins.open', mock_open_read, create=True):
        result = download_and_transcribe("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    # Verify the result
    assert result["id"] == "dQw4w9WgXcQ"
    assert result["title"] == "Test Video"
    assert result["channel"] == "Test Channel"
    assert result["author"] == "Test Author"
    assert result["transcription"] == "This is a test transcription."

    # Verify subprocess was called
    assert mock_subprocess_run.call_count >= 1


def test_get_transcript_command(temp_db):
    """Test the 'get' command with a real database."""
    runner = CliRunner()

    # Test the get command with a specific DB path
    result = runner.invoke(cli, ['get', 'sample123', '--db-path', temp_db])

    # Verify the output
    assert result.exit_code == 0
    assert 'Sample Video' in result.output
    assert 'Sample Channel' in result.output
    assert 'Sample Author' in result.output
    assert 'This is a sample transcription.' in result.output


@patch('yt_whisper.cli.download_and_transcribe')
@patch('yt_whisper.cli.save_to_db')
@patch('yt_whisper.cli.get_transcript')
def test_transcribe_command(mock_get_transcript, mock_save_to_db, mock_download_and_transcribe):
    """Test the 'transcribe' command."""
    runner = CliRunner()

    # Mock the get_transcript function to return None (video not in DB)
    mock_get_transcript.return_value = None

    # Mock the download_and_transcribe function
    mock_download_and_transcribe.return_value = {
        'id': 'dQw4w9WgXcQ',
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'title': 'Test Video',
        'channel': 'Test Channel',
        'author': 'Test Author',
        'duration': 213,
        'transcription': 'Test transcription',
        'created_at': '2024-05-11T12:00:00Z'
    }

    # Test the transcribe command
    result = runner.invoke(cli, ['transcribe', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'])

    # Verify the output
    assert result.exit_code == 0
    assert 'Successfully transcribed: Test Video' in result.output
    assert 'Channel: Test Channel' in result.output
    assert 'Author: Test Author' in result.output

    # Verify function calls
    mock_download_and_transcribe.assert_called_once_with(
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        False
    )
    mock_save_to_db.assert_called_once()


@patch('yt_whisper.cli.list_transcripts')
def test_list_command(mock_list_transcripts):
    """Test the 'list' command."""
    runner = CliRunner()

    # Mock the list_transcripts function
    mock_list_transcripts.return_value = [
        {
            'id': 'video1',
            'title': 'First Video',
            'channel': 'Channel 1',
            'author': 'Author 1',
            'created_at': '2024-05-11T12:00:00Z'
        },
        {
            'id': 'video2',
            'title': 'Second Video',
            'channel': 'Channel 2',
            'author': 'Author 2',
            'created_at': '2024-05-10T12:00:00Z'
        }
    ]

    # Test the list command
    result = runner.invoke(cli, ['list'])

    # Verify the output
    assert result.exit_code == 0
    assert 'First Video' in result.output
    assert 'Channel 1' in result.output
    assert 'Author 1' in result.output
    assert 'Second Video' in result.output
    assert 'Found 2 transcripts' in result.output

    # Verify function call
    mock_list_transcripts.assert_called_once_with(10, None)


def test_save_and_get_to_db(temp_db):
    """Test saving to and retrieving from the database."""
    # Test data
    test_data = {
        'id': 'testid123',
        'url': 'https://www.youtube.com/watch?v=testid123',
        'title': 'Test Title',
        'channel': 'Test Channel',
        'author': 'Test Author',
        'upload_date': '20240511',
        'duration': 120,
        'description': 'Test description',
        'transcription': 'Test transcription content',
        'created_at': '2024-05-11T12:00:00Z'
    }

    # Save to database
    save_to_db(test_data, temp_db)

    # Retrieve from database
    retrieved = get_transcript('testid123', temp_db)

    # Verify the data was stored and retrieved correctly
    assert retrieved['id'] == test_data['id']
    assert retrieved['title'] == test_data['title']
    assert retrieved['channel'] == test_data['channel']
    assert retrieved['author'] == test_data['author']
    assert retrieved['transcription'] == test_data['transcription']