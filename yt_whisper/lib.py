# yt_whisper/lib.py
import json
import os
import re
import subprocess
import tempfile
from datetime import UTC, datetime


def extract_youtube_id(url: str) -> str | None:
    """Extract the YouTube video ID from a URL."""
    # Handle multiple URL formats
    patterns = [
        r"v=([^&]+)",  # Standard: youtube.com/watch?v=ID
        r"youtu.be/([^?&]+)",  # Short: youtu.be/ID
        r"youtube.com/embed/([^/?&]+)",  # Embed: youtube.com/embed/ID
        r"youtube.com/v/([^/?&]+)",  # Old embed: youtube.com/v/ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def download_audio(
    youtube_id: str, temp_dir: str, force: bool = False
) -> tuple[str, str]:
    """
    Download audio from YouTube video to a temporary directory.

    Args:
        youtube_id: The YouTube video ID
        temp_dir: Temporary directory path
        force: Whether to force re-download if file exists

    Returns:
        Tuple of (audio_file_path, metadata_file_path)
    """
    output_file = os.path.join(temp_dir, f"ytw_audio_{youtube_id}.mp3")
    metadata_file = os.path.join(temp_dir, f"ytw_audio_{youtube_id}.info.json")

    if os.path.exists(output_file) and not force:
        print(f"Using existing file: {output_file}")
    else:
        print(f"Downloading audio from YouTube (ID: {youtube_id})...")
        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format",
            "mp3",
            "-o",
            output_file,
            f"https://www.youtube.com/watch?v={youtube_id}",
            "--write-info-json",
            "-o",
            os.path.join(temp_dir, f"ytw_audio_{youtube_id}.%(ext)s"),
            "--write-info-json",
        ]

        subprocess.run(cmd, check=True)

    return output_file, metadata_file


def transcribe_audio(audio_file: str, temp_dir: str) -> tuple[str, str]:
    """
    Transcribe audio file using Whisper.

    Args:
        audio_file: Path to the audio file
        temp_dir: Temporary directory path

    Returns:
        Tuple of (transcription_text, transcription_file_path)
    """
    youtube_id = os.path.basename(audio_file).split("_")[-1].split(".")[0]
    output_file = os.path.join(temp_dir, f"ytw_transcript_{youtube_id}.txt")

    print(f"Running Whisper transcription on {audio_file}...")
    cmd = ["whisper", "-f", audio_file]

    with open(output_file, "w") as f:
        subprocess.run(cmd, stdout=f, check=True)

    with open(output_file) as f:
        transcription = f.read()

    return transcription, output_file


def extract_metadata(metadata_file: str) -> dict:
    """Extract video metadata from the info JSON file."""
    try:
        with open(metadata_file) as f:
            data = json.load(f)
        return {
            "title": data.get("title", "Unknown Title"),
            "channel": data.get("channel", "Unknown Channel"),
            "author": data.get("uploader", data.get("channel", "Unknown Author")),
            "upload_date": data.get("upload_date", "Unknown Date"),
            "duration": data.get("duration", 0),
            "description": data.get("description", ""),
        }
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error extracting metadata: {e}")
        return {
            "title": "Unknown Title",
            "channel": "Unknown Channel",
            "author": "Unknown Author",
            "upload_date": "Unknown Date",
            "duration": 0,
            "description": "",
        }


def download_and_transcribe(url: str, force: bool = False) -> dict:
    """
    Main function to download and transcribe a YouTube video.

    Args:
        url: YouTube URL
        force: Whether to force re-download if file exists

    Returns:
        Dictionary with video information and transcription
    """
    youtube_id = extract_youtube_id(url)

    if not youtube_id:
        raise ValueError(f"Could not extract YouTube ID from URL: {url}")

    # Create a temporary directory that is automatically cleaned up
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory: {temp_dir}")

        # Download audio and get metadata
        audio_file, metadata_file = download_audio(youtube_id, temp_dir, force)

        # Extract metadata
        metadata = extract_metadata(metadata_file)

        # Transcribe the audio
        transcription, transcription_file = transcribe_audio(audio_file, temp_dir)

        # Prepare the result
        result = {
            "id": youtube_id,
            "url": url,
            "title": metadata["title"],
            "channel": metadata["channel"],
            "author": metadata["author"],
            "upload_date": metadata["upload_date"],
            "duration": metadata["duration"],
            "description": metadata["description"],
            "transcription": transcription,
            "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # The temporary directory and all files in it will be automatically
        # deleted when exiting the context manager

    return result
