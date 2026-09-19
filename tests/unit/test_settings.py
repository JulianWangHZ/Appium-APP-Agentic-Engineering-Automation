"""Framework self-tests: config loading and override priority."""
import pytest
from pydantic import ValidationError

from config.settings import get_settings


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_loads_android_staging(monkeypatch):
    monkeypatch.delenv("DEVICE_NAME", raising=False)
    monkeypatch.delenv("APP_PATH", raising=False)
    s = get_settings("android", "staging")
    assert s.platform == "android"
    assert s.capabilities["platformName"] == "Android"
    assert s.api_base_url.startswith("https://")


def test_app_id_extracted_and_not_sent_as_capability():
    s = get_settings("android", "staging")
    assert s.app_id
    assert "app_id" not in s.capabilities


def test_env_var_overrides_capabilities_yaml(monkeypatch):
    monkeypatch.delenv("ANDROID_APP_PATH", raising=False)  # .env may set it
    monkeypatch.setenv("DEVICE_NAME", "pixel-ci-01")
    monkeypatch.setenv("APP_PATH", "/builds/app.apk")
    s = get_settings("android", "staging")
    assert s.capabilities["appium:deviceName"] == "pixel-ci-01"
    assert s.capabilities["appium:app"] == "/builds/app.apk"


def test_udid_and_app_id_env_overrides(monkeypatch):
    monkeypatch.setenv("UDID", "ABC-123")
    monkeypatch.setenv("IOS_APP_ID", "com.example.other")
    s = get_settings("ios", "staging")
    assert s.capabilities["appium:udid"] == "ABC-123"
    assert s.app_id == "com.example.other"


def test_explicit_wait_env_override(monkeypatch):
    monkeypatch.setenv("EXPLICIT_WAIT", "30")
    s = get_settings("android", "staging")
    assert s.explicit_wait == 30


def test_platform_specific_app_path_beats_generic(monkeypatch):
    monkeypatch.setenv("APP_PATH", "/builds/generic.apk")
    monkeypatch.setenv("ANDROID_APP_PATH", "/builds/android.apk")
    s = get_settings("android", "staging")
    assert s.capabilities["appium:app"] == "/builds/android.apk"


def test_unknown_env_lists_available_options():
    with pytest.raises(FileNotFoundError, match="available.*staging"):
        get_settings("android", "nonexistent")


def test_settings_are_frozen():
    s = get_settings("ios", "staging")
    with pytest.raises(ValidationError):
        s.platform = "android"
