# yt_whisper/lib.py
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Any

import whisper
import yt_dlp
from yt_dlp.utils import DownloadError


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


def is_ffmpeg_available() -> bool:
    """Check if FFmpeg is installed and available in PATH."""
    try:
        # Run ffmpeg -version, capture output to prevent console printing
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,  # Raise CalledProcessError for non-zero exit codes
        )
        return result.returncode == 0
    except FileNotFoundError:
        # FFmpeg command not found
        return False
    except subprocess.CalledProcessError:
        # FFmpeg found but returned an error (e.g., -version not supported, though unlikely)
        return False


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
    temp_path = Path(temp_dir)
    output_file = temp_path / f"ytw_audio_{youtube_id}.mp3"
    metadata_file = temp_path / f"ytw_audio_{youtube_id}.info.json"

    if os.path.exists(str(output_file)) and not force:
        print(f"Using existing file: {output_file}")
        return str(output_file), str(metadata_file)

    print(f"Downloading audio from YouTube (ID: {youtube_id})...")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": str(temp_path / f"ytw_audio_{youtube_id}"),
        "writethumbnail": False,
        "writeinfojson": True,
        "quiet": False,
        "no_warnings": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={youtube_id}"])
    except DownloadError:
        # Specific error for download issues
        print(
            "Error: Failed to download video. "
            "Please check your network connection and the video URL."
        )
        raise
    except Exception as e:
        # Catch any other unexpected errors during download
        print(f"An unexpected error occurred during download: {e}")
        raise

    return str(output_file), str(metadata_file)


def transcribe_audio(
    audio_file: str,
    temp_dir: str,
    model_name: str = "base",
    language: str | None = None,
) -> tuple[str, str]:
    """
    Transcribe audio file using Whisper Python library.

    Args:
        audio_file: Path to the audio file
        temp_dir: Temporary directory path
        model_name: Name of the Whisper model to use
        language: Language code (e.g., 'en', 'es', 'fr'). If None, will auto-detect.

    Returns:
        Tuple of (transcription_text, transcription_file_path)
    """
    youtube_id = os.path.basename(audio_file).split("_")[-1].split(".")[0]
    output_file = os.path.join(temp_dir, f"ytw_transcript_{youtube_id}.txt")

    print(f"Loading Whisper model: {model_name}...")
    model = whisper.load_model(model_name)

    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file, language=language, fp16=False)
    transcription = result["text"]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcription)

    return transcription, output_file


def extract_metadata(metadata_file: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract video metadata from the info JSON file.

    Args:
        metadata_file: Path to the metadata JSON file

    Returns:
        Tuple of (extracted_metadata, raw_metadata)
    """
    try:
        with open(metadata_file, encoding="utf-8") as f:
            data = json.load(f)

        # Extract the fields we specifically need for our database structure
        # yt-dlp uses 'uploader' for the channel name and 'channel' might not be present
        uploader = data.get("uploader") or "Unknown Author"
        channel = data.get("channel") or uploader or "Unknown Channel"

        extracted = {
            "title": data.get("title", "Unknown Title"),
            "channel": channel,
            "author": uploader,
            "upload_date": data.get("upload_date", "Unknown Date"),
            "duration": data.get("duration", 0),
            "description": data.get("description", ""),
        }

        # Return both the extracted fields and the full raw metadata
        return extracted, data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error extracting metadata: {e}")
        empty_metadata = {
            "title": "Unknown Title",
            "channel": "Unknown Channel",
            "author": "Unknown Author",
            "upload_date": "Unknown Date",
            "duration": 0,
            "description": "",
        }
        return empty_metadata, {}


def download_and_transcribe(
    url: str,
    force: bool = False,
    model_name: str = "base",
    language: str | None = None,
) -> dict:
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
        metadata, raw_metadata = extract_metadata(metadata_file)

        # Transcribe the audio
        transcription, transcription_file = transcribe_audio(
            audio_file,
            temp_dir,
            model_name=model_name,
            language=language,
        )

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
            "metadata": raw_metadata,  # This is the complete raw metadata from YouTube
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # The temporary directory and all files in it will be automatically
        # deleted when exiting the context manager

    return result
