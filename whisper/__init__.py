"""Minimal stub of the `whisper` package for tests."""

from . import audio


def load_model(*args, **kwargs):
    """Placeholder load_model function to be patched in tests."""
    raise NotImplementedError("whisper.load_model is not implemented in the stub")

__all__ = ["load_model", "audio"]
