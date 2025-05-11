# yt_whisper/cli.py
import os
import sys
import click
import json
from . import __version__
from .lib import download_and_transcribe, extract_youtube_id
from .db import save_to_db, get_transcript, list_transcripts, get_db_path


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    YT-Whisper: Download and transcribe YouTube videos using Whisper.
    
    This tool allows you to download the audio from YouTube videos
    and transcribe them using OpenAI's Whisper, saving the results
    to a local SQLite database.
    """
    pass


@cli.command()
@click.argument("url")
@click.option(
    "-f", "--force", 
    is_flag=True, 
    help="Force re-download and transcription even if already in database"
)
@click.option(
    "--no-save", 
    is_flag=True, 
    help="Don't save to database"
)
@click.option(
    "--db-path", 
    help="Custom path to SQLite database",
    default=None,
    type=click.Path(dir_okay=False)
)
def transcribe(url, force, no_save, db_path):
    """
    Download and transcribe a YouTube video.
    
    Example usage:
        yt-whisper transcribe https://www.youtube.com/watch?v=VIDEO_ID
    """
    try:
        # Validate URL
        youtube_id = extract_youtube_id(url)
        if not youtube_id:
            click.echo(f"Error: Could not extract YouTube ID from URL: {url}", err=True)
            sys.exit(1)
            
        # Check if already in database
        existing = get_transcript(youtube_id, db_path)
        if existing and not force:
            click.echo(f"Video already transcribed: {existing['title']}")
            click.echo(f"Channel: {existing['channel']}")
            click.echo(f"Author: {existing.get('author', 'Unknown')}")
            click.echo(f"To view the transcript, use: yt-whisper get {youtube_id}")
            click.echo(f"To force re-transcription, use the -f/--force flag")
            sys.exit(0)
            
        # Download and transcribe
        result = download_and_transcribe(url, force)
        
        # Print summary
        click.echo(f"Successfully transcribed: {result['title']}")
        click.echo(f"Channel: {result['channel']}")
        click.echo(f"Author: {result['author']}")
        click.echo(f"YouTube ID: {result['id']}")
        click.echo(f"Duration: {result['duration']} seconds")
        
        # Save to database unless --no-save flag is used
        if not no_save:
            save_to_db(result, db_path)
            db_file = db_path or get_db_path()
            click.echo(f"Saved to database: {db_file}")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("youtube_id")
@click.option(
    "--db-path", 
    help="Custom path to SQLite database",
    default=None
)
@click.option(
    "--output", 
    type=click.File('w'),
    help="Output file (default: stdout)"
)
def get(youtube_id, db_path, output):
    """
    Get a transcript from the database.
    
    Example usage:
        yt-whisper get VIDEO_ID
    """
    transcript = get_transcript(youtube_id, db_path)
    
    if not transcript:
        click.echo(f"Error: No transcript found for YouTube ID: {youtube_id}", err=True)
        sys.exit(1)
        
    if output:
        output.write(transcript["transcription"])
        click.echo(f"Transcript written to {output.name}")
    else:
        click.echo(f"Title: {transcript['title']}")
        click.echo(f"Channel: {transcript.get('channel', 'Unknown')}")
        click.echo(f"URL: https://www.youtube.com/watch?v={youtube_id}")
        click.echo("\nTranscription:")
        click.echo("-" * 40)
        click.echo(transcript["transcription"])


@cli.command()
@click.option(
    "--limit", 
    default=10,
    help="Maximum number of items to show"
)
@click.option(
    "--db-path", 
    help="Custom path to SQLite database",
    default=None
)
@click.option(
    "--json", 
    "output_json",
    is_flag=True,
    help="Output as JSON"
)
def list(limit, db_path, output_json):
    """
    List transcripts in the database.
    
    Example usage:
        yt-whisper list --limit 20
    """
    transcripts = list_transcripts(limit, db_path)
    
    if not transcripts:
        click.echo("No transcripts found in the database.")
        return
        
    if output_json:
        click.echo(json.dumps(transcripts, indent=2))
    else:
        click.echo(f"Found {len(transcripts)} transcripts:")
        click.echo("-" * 80)
        
        for t in transcripts:
            click.echo(f"ID: {t['id']} | Title: {t['title']}")
            click.echo(f"Channel: {t.get('channel', 'Unknown')} | Created: {t['created_at']}")
            click.echo("-" * 80)


@cli.command()
@click.argument("query")
@click.option(
    "--db-path", 
    help="Custom path to SQLite database",
    default=None
)
def search(query, db_path):
    """
    Search for transcripts containing the given query.
    
    Example usage:
        yt-whisper search "climate change"
    """
    if db_path is None:
        db_path = get_db_path()
    
    if not os.path.exists(db_path):
        click.echo("Database not found. No transcripts available.")
        return
        
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Simple full-text search
    cursor.execute("""
    SELECT id, title, channel, created_at 
    FROM videos 
    WHERE transcription LIKE ? OR title LIKE ?
    ORDER BY created_at DESC
    """, (f'%{query}%', f'%{query}%'))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        click.echo(f"No matches found for query: '{query}'")
        return
        
    click.echo(f"Found {len(rows)} matches for query: '{query}'")
    click.echo("-" * 80)
    
    for row in rows:
        row = dict(row)
        click.echo(f"ID: {row['id']} | Title: {row['title']}")
        click.echo(f"Channel: {row.get('channel', 'Unknown')} | Created: {row['created_at']}")
        click.echo(f"Watch: https://www.youtube.com/watch?v={row['id']}")
        click.echo("-" * 80)
        
    click.echo(f"To view a transcript, use: yt-whisper get VIDEO_ID")
