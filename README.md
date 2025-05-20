# yt-whisper

[![PyPI](https://img.shields.io/pypi/v/yt-whisper.svg)](https://pypi.org/project/yt-whisper/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/yourusername/yt-whisper/blob/master/LICENSE)

Download and transcribe YouTube videos using OpenAI's Whisper.

## Features

- Transcribe YouTube videos from URLs
- Store transcripts in SQLite
- Search by title, author, or description
- Simple CLI interface

## Quick Start

1. Install with pip (Python 3.10+ required):
   ```bash
   pip install yt-whisper
   ```

2. Install FFmpeg (required for audio processing):
   ```bash
   # On macOS
   brew install ffmpeg

   # On Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # On Windows (using Chocolatey)
   choco install ffmpeg
   ```

3. Transcribe your first video:
   ```bash
   yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID
   ```

4. Search your transcripts:
   ```bash
   yt-whisper search "search term"
   ```

That's it! Your transcripts are automatically stored and organized in a local SQLite database.

## CLI Reference

### Transcribe Videos

Download and transcribe a YouTube video:
```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID
```

Force re-download and re-transcription:
```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --force
```

Use a specific Whisper model (tiny, base, small, medium, large):
```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --model small
```

### Retrieve Transcripts

Get a transcript by video ID:
```bash
yt-whisper get VIDEO_ID
```

Save transcript to a file:
```bash
yt-whisper get VIDEO_ID --output transcript.txt
```

### Search and List

List recent transcripts:
```bash
yt-whisper list
```

Search through all transcripts:
```bash
yt-whisper search "search query"
```

## Advanced Usage

### Database Location

#### CLI Usage
When using the command-line interface, the database is stored in a platform-specific location:
- **Linux**: `~/.local/share/yt-whisper/logs.db`
- **macOS**: `~/Library/Application Support/yt-whisper/logs.db`
- **Windows**: `C:\Users\<user>\AppData\Local\yt-whisper\logs.db`

You can specify a custom database path with the `--db-path` option:
```bash
yt-whisper transcribe URL --db-path ./custom.db
```

#### Library Usage
When using yt-whisper as a Python library, the default database path follows the same platform-specific locations as the CLI. However, you can override this by passing a custom path to any function that interacts with the database:

```python
# Using default database location
result = download_and_transcribe("https://www.youtube.com/watch?v=VIDEO_ID")

# Using a custom database location
result = download_and_transcribe(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    db_path="./custom.db"
)

# Getting a transcript with a custom database path
transcript = get_transcript("VIDEO_ID", db_path="./custom.db")
```

All database-related functions accept an optional `db_path` parameter that allows you to specify a custom location for the database file.

### Additional Options

Specify language (faster and more accurate if known):
```bash
yt-whisper transcribe URL --language en
```

## Dependencies
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video downloading
- [openai-whisper](https://github.com/openai/whisper) - Speech-to-text transcription
- FFmpeg - Audio processing

## Usage

## Python API

You can also use yt-whisper as a Python library:

```python
from yt_whisper import download_and_transcribe

# Basic usage
result = download_and_transcribe("https://www.youtube.com/watch?v=VIDEO_ID")

# Access the results
print(f"Title: {result['title']}")
print(f"Channel: {result['channel']}")
print(f"Author: {result['author']}")
print(f"Duration: {result['duration']} seconds")
print(f"Transcription: {result['transcription']}")

# Access raw metadata
print(f"Raw metadata: {result['metadata']}")
```

### Database Access

```python
from yt_whisper.db import save_to_db, get_transcript

# Get a transcript
transcript = get_transcript("VIDEO_ID")
if transcript:
    print(transcript['title'])
    print(transcript['transcription'])
```

## Requirements

- Python 3.10 or higher
- FFmpeg (installed via system package manager)

## Development

To contribute to this tool, first checkout the code:

```bash
git clone https://github.com/paos/yt-whisper.git
cd yt-whisper
```

Create a new virtual environment:

```bash
uv venv --python 3.10
source venv/bin/activate
```

Install the dependencies and development dependencies:

```bash
uv run pip install -e '.[test]'
```

Run the tests:

```bash
uv run pytest
```

### Code Quality

To contribute to this tool, first checkout the code:

```bash
git clone https://github.com/yourusername/yt-whisper.git
cd yt-whisper
```

Create a new virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the dependencies and development dependencies:

```bash
pip install -e '.[test]'
```

Run the tests:

```bash
pytest
```

### Code Quality

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting, configured as a pre-commit hook. To set up pre-commit:

```bash
pip install pre-commit
pre-commit install
```

To manually run the pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

## yt-whisper --help

```
Usage: yt-whisper [OPTIONS] COMMAND [ARGS]...

  YT-Whisper: Download and transcribe YouTube videos using Whisper.

  This tool allows you to download the audio from YouTube videos and
  transcribe them using OpenAI's Whisper, saving the results to a local
  SQLite database.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  get        Get a transcript from the database.
  list       List transcripts in the database.
  search     Search for transcripts containing the given query.
  transcribe  Download and transcribe a YouTube video.
```
