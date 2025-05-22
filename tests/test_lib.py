import unittest
from unittest.mock import patch, MagicMock
import subprocess

import os # Added for os.path.join and os.path.exists mocking

# Assuming yt_whisper.lib is accessible in the PYTHONPATH
# If not, you might need to adjust sys.path or how you import
from yt_whisper.lib import is_ffmpeg_available, download_audio
from yt_dlp.utils import DownloadError # Assuming this can be imported; or mock it

# If direct import of DownloadError is an issue, use a dummy class for tests:
# class DownloadError(Exception):
#     """Dummy DownloadError for testing if yt_dlp.utils is not available."""
#     pass


class TestLibFFmpeg(unittest.TestCase):

    @patch('subprocess.run')
    def test_ffmpeg_available(self, mock_run):
        # Configure the mock to simulate FFmpeg being found
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # Call is_ffmpeg_available()
        self.assertTrue(is_ffmpeg_available())

        # Ensure subprocess.run was called correctly
        mock_run.assert_called_once_with(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    @patch('subprocess.run')
    def test_ffmpeg_not_available_file_not_found(self, mock_run):
        # Configure the mock to raise FileNotFoundError
        mock_run.side_effect = FileNotFoundError

        # Call is_ffmpeg_available()
        self.assertFalse(is_ffmpeg_available())

    @patch('subprocess.run')
    def test_ffmpeg_returns_non_zero_exit_code(self, mock_run):
        # Configure the mock to simulate FFmpeg command failing
        # This can happen if check=True is not handled by the mock's spec
        # or if the CalledProcessError is raised by the function itself.
        # For this test, let's assume is_ffmpeg_available catches CalledProcessError
        # if ffmpeg -version itself fails for some reason other than not being found.

        # Option 1: Mocking CalledProcessError directly if check=True is part of the test
        # mock_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=['ffmpeg', '-version'])

        # Option 2: Mocking a process that has a non-zero return code,
        # and is_ffmpeg_available handles this gracefully (as it does by returning False).
        mock_process = MagicMock()
        mock_process.returncode = 1
        # If the function expects check=True to raise an error for non-zero,
        # then side_effecting with CalledProcessError is more direct.
        # However, the current implementation of is_ffmpeg_available returns False
        # if subprocess.run itself throws CalledProcessError.
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=['ffmpeg', '-version']
        )
        
        self.assertFalse(is_ffmpeg_available())

    @patch('subprocess.run')
    def test_ffmpeg_called_process_error_on_run(self, mock_run):
        # This test explicitly checks the handling of CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(cmd="ffmpeg -version", returncode=127)
        self.assertFalse(is_ffmpeg_available())


class TestLibDownloadAudio(unittest.TestCase):

    @patch('os.path.exists')
    @patch('yt_dlp.YoutubeDL')
    def test_download_audio_handles_download_error(self, mock_youtube_dl, mock_path_exists):
        # Simulate that files do not exist to trigger download
        mock_path_exists.return_value = False

        # Configure the YoutubeDL mock
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.download.side_effect = DownloadError("Test download error")
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

        # Assert that DownloadError is raised and the message is printed
        with self.assertRaises(DownloadError):
            download_audio("some_id", "some_temp_dir")
        
        # To check printed output, you'd typically redirect stdout or use capsys with pytest
        # For unittest, it's a bit more involved, so we'll skip direct output check here
        # but assume the print statement in download_audio was executed.

    @patch('os.path.exists')
    @patch('yt_dlp.YoutubeDL')
    def test_download_audio_handles_generic_exception(self, mock_youtube_dl, mock_path_exists):
        # Simulate that files do not exist to trigger download
        mock_path_exists.return_value = False

        # Configure the YoutubeDL mock
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.download.side_effect = Exception("Some generic download error")
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

        # Assert that the generic Exception is raised
        with self.assertRaises(Exception) as context:
            download_audio("some_id", "some_temp_dir")
        self.assertTrue("Some generic download error" in str(context.exception))

    @patch('os.path.join')
    @patch('os.path.exists')
    @patch('yt_dlp.YoutubeDL')
    def test_download_audio_successful_execution(self, mock_youtube_dl, mock_path_exists, mock_path_join):
        # Simulate that files do not exist to trigger download
        mock_path_exists.return_value = False
        
        # Define expected file paths
        expected_audio_file = "/tmp/dummy_dir/ytw_audio_test_id.mp3"
        expected_metadata_file = "/tmp/dummy_dir/ytw_audio_test_id.info.json"

        # Configure os.path.join to return deterministic paths
        def side_effect_join(path, filename):
            if "ytw_audio_test_id.mp3" in filename:
                return expected_audio_file
            if "ytw_audio_test_id.info.json" in filename:
                return expected_metadata_file
            return os.path.normpath(os.path.join(path, filename)) # Fallback to actual join for other cases

        mock_path_join.side_effect = side_effect_join
        
        # Configure the YoutubeDL mock
        mock_ydl_instance = MagicMock()
        mock_youtube_dl.return_value.__enter__.return_value = mock_ydl_instance

        # Call the function
        audio_file, metadata_file = download_audio("test_id", "/tmp/dummy_dir")

        # Assertions
        mock_path_exists.assert_any_call(expected_audio_file) # Check if existence of output file was checked
        mock_youtube_dl.assert_called_once() # Check if YoutubeDL was instantiated
        mock_ydl_instance.download.assert_called_once_with(["https://www.youtube.com/watch?v=test_id"])
        
        self.assertEqual(audio_file, expected_audio_file)
        self.assertEqual(metadata_file, expected_metadata_file)

    @patch('os.path.exists')
    def test_download_audio_uses_existing_file(self, mock_path_exists):
        # Simulate that the audio file already exists
        mock_path_exists.return_value = True

        expected_audio_file = os.path.join("some_temp_dir", "ytw_audio_some_id.mp3")
        expected_metadata_file = os.path.join("some_temp_dir", "ytw_audio_some_id.info.json")

        # Call the function
        # We don't need to mock YoutubeDL here as it shouldn't be called if the file exists
        audio_file, metadata_file = download_audio("some_id", "some_temp_dir", force=False)

        # Assertions
        mock_path_exists.assert_called_once_with(expected_audio_file)
        self.assertEqual(audio_file, expected_audio_file)
        self.assertEqual(metadata_file, expected_metadata_file)


if __name__ == '__main__':
    unittest.main()
