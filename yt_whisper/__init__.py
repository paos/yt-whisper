# yt_whisper/__init__.py
from importlib.metadata import PackageNotFoundError, version

from .lib import download_and_transcribe

try:
    __version__ = version("yt-whisper")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.4.2"

__all__ = ["download_and_transcribe"]
