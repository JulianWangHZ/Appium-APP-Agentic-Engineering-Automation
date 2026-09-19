"""Framework self-tests: poll_until primitive."""
import pytest

from core.wait import poll_until


def test_returns_when_condition_becomes_true():
    calls = []

    def flaky():
        calls.append(1)
        return len(calls) >= 3

    poll_until(flaky, timeout=5, interval=0.01)
    assert len(calls) == 3


def test_swallows_exceptions_and_keeps_polling():
    calls = []

    def stale_then_ok():
        calls.append(1)
        if len(calls) < 3:
            raise RuntimeError("stale element")
        return True

    poll_until(stale_then_ok, timeout=5, interval=0.01)
    assert len(calls) == 3


def test_timeout_includes_message_and_last_error():
    def always_stale():
        raise RuntimeError("stale element")

    with pytest.raises(TimeoutError, match="button not visible.*stale element"):
        poll_until(always_stale, timeout=0.05, interval=0.01, message="button not visible")


def test_timeout_without_error_when_condition_just_false():
    with pytest.raises(TimeoutError, match="condition not met within"):
        poll_until(lambda: False, timeout=0.05, interval=0.01)
