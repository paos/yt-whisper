# Suggested Improvement Tasks for yt-whisper

## 1. Full-Text Search in Transcripts

*   **Description:** Modify the `search` command and underlying database logic to include searching within the actual transcript text, not just metadata (title, author, channel, description).
*   **Goal:** Allow users to find videos based on the content of their transcriptions, making the tool much more powerful for research and information retrieval.
*   **Details:** This would likely involve utilizing SQLite's full-text search capabilities (e.g., FTS5 extension) for efficient searching of the `transcription` column in the `videos` table. The `search` command in `cli.py` would need to be updated to query this FTS table.

## 2. Add Multiple Export Formats

*   **Description:** Enhance the `get` command (or create a new `export` command) to allow exporting transcripts into various common formats such as SRT (SubRip Subtitle), VTT (Web Video Text Tracks), in addition to the existing plain text output.
*   **Goal:** Provide users with flexible output options suitable for different use cases, like creating video subtitles, importing into other video editing software, or simple text analysis.
*   **Details:** This will involve creating functions to format the transcript data (text and timestamps, if Whisper provides them at a granular enough level, otherwise segment-level timestamps) into the specific structures required by SRT and VTT files. The `get` command in `cli.py` would need an option like `--format <type>` (e.g., `--format srt`).

## 3. Implement Batch Transcription

*   **Description:** Add a new CLI command (e.g., `transcribe-batch`) that accepts multiple YouTube URLs. This could be from a text file (one URL per line) or by allowing multiple URLs to be passed as arguments to the command.
*   **Goal:** Improve efficiency for users who need to transcribe a list of videos, automating what would otherwise be a manual, repetitive process.
*   **Details:** The new command in `cli.py` would iterate through the provided URLs, calling the existing `download_and_transcribe` function from `lib.py` for each. It should provide clear progress feedback to the user (e.g., "Transcribing video X of Y...") and handle errors gracefully for individual videos without stopping the entire batch.

## 4. Add Support for a Configuration File

*   **Description:** Implement support for a user-specific configuration file (e.g., located at `~/.config/yt-whisper/config.toml` or a local `yt-whisper.toml`) where users can define default values for options like the Whisper model, database path, default language, etc.
*   **Goal:** Make the tool more convenient for users by allowing them to set their preferred defaults once, rather than specifying them with CLI arguments for every command execution. CLI arguments should override settings from the configuration file.
*   **Details:** This involves choosing a configuration file format (TOML or YAML are good choices), adding a library like `tomli` (for TOML) or `PyYAML` (for YAML) to parse the file. Logic would be needed in `cli.py` or a shared utility module to load settings from the config file and merge them with CLI-provided options, giving precedence to the latter.

## 5. Improve `list` Command Output Options

*   **Description:** Extend the `list` command to support more structured output formats beyond the current default text and JSON. A key format to add would be CSV (Comma Separated Values).
*   **Goal:** Allow users to easily export the list of their transcribed videos for use in spreadsheets, data analysis tools, or for simple record-keeping.
*   **Details:** This would involve adding a `--format` option to the `list` command in `cli.py` (e.g., `yt-whisper list --format csv`). Based on this option, the command would format the data fetched by `db.list_transcripts` into the chosen format. For CSV, this would mean ensuring proper quoting and delimiter usage.
