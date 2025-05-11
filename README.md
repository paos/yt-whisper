# yt-whisper

[![PyPI](https://img.shields.io/pypi/v/yt-whisper.svg)](https://pypi.org/project/yt-whisper/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/yourusername/yt-whisper/blob/master/LICENSE)

Download and transcribe YouTube videos using Whisper, saving transcripts to a local SQLite database.

## Installation

Install this tool using `pip`:

```bash
pip install yt-whisper
```

### Dependencies

This tool requires:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading YouTube audio
- [whisper](https://github.com/openai/whisper) for transcription

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

# Download and transcribe a video (files are automatically cleaned up)
result = download_and_transcribe("https://www.youtube.com/watch?v=VIDEO_ID")

# Print information about the video
print(f"Title: {result['title']}")
print(f"Channel: {result['channel']}")
print(f"Author: {result['author']}")
print(f"Duration: {result['duration']} seconds")

# Print the transcription
print(result['transcription'])
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