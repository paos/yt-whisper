import yt_whisper


def test_download_and_transcribe_same_function():
    import yt_whisper.lib as lib
    assert yt_whisper.download_and_transcribe is lib.download_and_transcribe


def test_download_and_transcribe_invocation(monkeypatch):
    called = {}

    def fake_download_and_transcribe(url: str, force: bool = False, model_name: str = "base", language: str | None = None):
        called['params'] = (url, force, model_name, language)
        return {'id': 'dummy'}

    monkeypatch.setattr("yt_whisper.lib.download_and_transcribe", fake_download_and_transcribe)
    monkeypatch.setattr(yt_whisper, "download_and_transcribe", fake_download_and_transcribe)
    result = yt_whisper.download_and_transcribe("https://example.com", force=True, model_name="tiny", language="en")
    assert result == {'id': 'dummy'}
    assert called['params'] == ("https://example.com", True, "tiny", "en")
