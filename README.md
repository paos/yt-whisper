# yt-whisper

[![PyPI](https://img.shields.io/pypi/v/yt-whisper.svg)](https://pypi.org/project/yt-whisper/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/yourusername/yt-whisper/blob/master/LICENSE)

A command-line tool to download and transcribe YouTube videos using OpenAI's Whisper, with local storage of transcripts in SQLite.

## Quick Start

1. Install with pip:
   ```bash
   pip install yt-whisper
   ```

2. Install FFmpeg (required):
   ```bash
   # On macOS
   brew install ffmpeg

   # On Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg

   # On Windows (using Chocolatey)
   choco install ffmpeg
   ```

3. Start transcribing videos:
   ```bash
   yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID
   ```

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

By default, transcripts are stored in:
```
yt_whisper/data/youtube_transcripts.db
```

Specify a custom database path:
```bash
yt-whisper transcribe URL --db-path ./custom.db
```

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

# With custom parameters
result = download_and_transcribe(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    model_name="small",  # tiny, base, small, medium, large
    language="en",       # optional, auto-detected if None
    device="cuda",       # or "cpu"
    fp16=True           # use FP16 precision (faster with CUDA)
)

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

- Python 3.8 or higher
- FFmpeg (installed via system package manager)

## Development

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
