from ghost35.fallback import fallback_whisper


def test_empty_command():
    assert "silence" in fallback_whisper("").lower()


def test_git_whisper():
    text = fallback_whisper("git commit -m 'test'")
    assert "commit" in text.lower() or "gravestone" in text.lower()


def test_destructive_warning():
    text = fallback_whisper("rm -rf /")
    assert "sharp" in text.lower() or "double-check" in text.lower()
