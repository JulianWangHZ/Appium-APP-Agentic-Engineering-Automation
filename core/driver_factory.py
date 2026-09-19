"""Creates Appium drivers from Settings. The only place that knows Appium options classes."""
from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

from config.settings import Settings

_OPTIONS = {
    "android": UiAutomator2Options,
    "ios": XCUITestOptions,
}


def create_driver(settings: Settings) -> webdriver.Remote:
    if settings.platform not in _OPTIONS:
        raise ValueError(f"Unsupported platform: {settings.platform!r} (expected android/ios)")
    options = _OPTIONS[settings.platform]().load_capabilities(settings.capabilities)
    driver = webdriver.Remote(settings.appium_server_url, options=options)
    driver.implicitly_wait(settings.implicit_wait)
    return driver
