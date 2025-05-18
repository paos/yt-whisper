# yt-whisper

[![PyPI](https://img.shields.io/pypi/v/yt-whisper.svg)](https://pypi.org/project/yt-whisper/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/yourusername/yt-whisper/blob/master/LICENSE)

Download and transcribe YouTube videos using Whisper, saving transcripts to a local SQLite database.

## Installation

Install this tool using `pip`:

```bash
pip install yt-whisper
```

### Additional Setup

1. Install FFmpeg (required by Whisper):
   - On Ubuntu/Debian: `sudo apt update && sudo apt install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from [FFmpeg's website](https://ffmpeg.org/download.html)

2. For GPU acceleration (optional - will work fine without):
   - Install PyTorch with CUDA support: [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
   - Example for CUDA 11.8: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118`

### Dependencies

This tool requires:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) Python package for downloading YouTube audio
- [openai-whisper](https://github.com/openai/whisper) Python package for transcription
- FFmpeg (required by Whisper)

## Usage

### Basic Transcription

Download and transcribe a YouTube video:

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID
```

Force re-download and transcription:

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID -f
```

Use a larger model for better accuracy (but slower):

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --model small
```

Specify the language (faster and more accurate if known):

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --language en
```

Use CPU instead of CUDA (if available):

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --device cpu
```

Disable FP16 (useful for older GPUs):

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --no-fp16
```

The tool automatically uses a temporary directory that is cleaned up after processing.


### Retrieving Transcripts

Get a transcript from the database:

```bash
yt-whisper get VIDEO_ID
```

Save the transcript to a file:

```bash
yt-whisper get VIDEO_ID --output transcript.txt
```

### Managing Transcripts

List your recent transcripts:

```bash
yt-whisper list
```

List more transcripts:

```bash
yt-whisper list --limit 20
```

Output as JSON:

```bash
yt-whisper list --json
```

### Searching Transcripts

Search through your transcripts:

```bash
yt-whisper search "climate change"
```

## Database

Transcripts are stored in a SQLite database located in the package's data directory:
`yt_whisper/data/youtube_transcripts.db`

You can specify a custom database path with the `--db-path` option:

```bash
yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID --db-path ./my_database.db
```

## Using as a Python Library

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

Or interact with the database:

```python
from yt_whisper.db import save_to_db, get_transcript

# Get a transcript
transcript = get_transcript("VIDEO_ID")
if transcript:
    print(transcript['title'])
    print(transcript['transcription'])
```

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
