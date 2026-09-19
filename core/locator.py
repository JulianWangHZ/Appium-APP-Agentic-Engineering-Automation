"""Cross-platform locator.

One logical element, one Locator, per-platform selectors. Screens never
hold raw (by, value) tuples, so the same screen class drives both platforms.

Strategy priority: accessibility id > id > platform-native (uiautomator/predicate) > xpath.

For dynamic locators (selectors needing interpolation), use a factory function
returning a Locator; include the argument in `name` for debuggability:

    def cell_with_title(title: str) -> Locator:
        return Locator(
            name=f"cell {title!r}",
            android=(AppiumBy.ANDROID_UIAUTOMATOR,
                     f'new UiSelector().description("{title}")'),
            ios=(AppiumBy.IOS_PREDICATE, f"label == '{title}'"),
        )
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from appium.webdriver.common.appiumby import AppiumBy

Platform = Literal["android", "ios"]


@dataclass(frozen=True)
class Locator:
    name: str  # human-readable, used in logs and error messages
    android: tuple[str, str] | None = None
    ios: tuple[str, str] | None = None

    def resolve(self, platform: Platform) -> tuple[str, str]:
        selector = getattr(self, platform, None)
        if selector is None:
            raise ValueError(f"Locator {self.name!r} has no selector for platform {platform!r}")
        return selector


def by_a11y_id(name: str, value: str) -> Locator:
    """Same accessibility id on both platforms — the preferred case."""
    selector = (AppiumBy.ACCESSIBILITY_ID, value)
    return Locator(name=name, android=selector, ios=selector)
