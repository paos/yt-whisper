# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-05-19

### Added
- change search functionality to title, author channel and description fields



## [1.0.0] - 2025-05-19

### Changed
- **BREAKING**: Updated Python version requirement to 3.10
- Improved database path documentation


## [0.4.0] - 2025-05-18

### Changed
- **BREAKING**: Moved database location to platform-specific directories:
  - Linux: `~/.local/share/yt-whisper/`
  - Windows: `%LOCALAPPDATA%\yt-whisper\`
  - macOS: `~/Library/Application Support/yt-whisper/`
- Added automatic migration of existing database from `~/.yt-whisper/logs.db` to the new location
- Updated `platformdirs` to handle cross-platform paths

### Added
- New `delete` command to remove specific video transcripts from the database
- Confirmation prompt for deletion (can be skipped with `-y/--yes` flag)
- Support for custom database path in the delete command

## [0.3.0] - 2025-05-17

### Changed
- **BREAKING**: Switched from using the Whisper binary to the official OpenAI Whisper Python library
- Updated minimum Python version to 3.12
- Improved error handling and progress reporting

### Added
- Support for different Whisper model sizes (`--model` option): tiny, base, small, medium, large
- Language specification support (`--language` option)
- Device selection (`--device` option) for CPU/CUDA
- FP16 precision control (`--fp16/--no-fp16` flags)
- Better progress reporting during model loading and transcription
- Added GPU support through PyTorch (optional dependency)
- Added comprehensive documentation in README

### Removed
- Dependency on external Whisper binary

### Fixed
- Fixed issues with temporary file handling
- Improved error messages for better debugging

## [0.2.0] - YYYY-MM-DD

### Added
- Initial release with basic functionality
- Support for downloading and transcribing YouTube videos
- SQLite database integration for storing transcripts
- Command-line interface with subcommands
