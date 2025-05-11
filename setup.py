# setup.py
import os

from setuptools import find_packages, setup

VERSION = "0.1.0"


def get_long_description() -> str:
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="yt-whisper",
    version=VERSION,
    description="Download and transcribe YouTube videos using Whisper",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Your Name",
    url="https://github.com/yourusername/yt-whisper",
    project_urls={
        "Issues": "https://github.com/yourusername/yt-whisper/issues",
        "CI": "https://github.com/yourusername/yt-whisper/actions",
        "Changelog": "https://github.com/yourusername/yt-whisper/releases",
    },
    license="Apache License, Version 2.0",
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        yt-whisper=yt_whisper.cli:cli
    """,
    install_requires=[
        "click",
        "yt-dlp",
    ],
    extras_require={
        "test": ["pytest"],
    },
    python_requires=">=3.7",
)
