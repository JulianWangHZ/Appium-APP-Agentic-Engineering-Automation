"""Framework self-tests: cross-platform Locator resolution."""
import pytest
from appium.webdriver.common.appiumby import AppiumBy

from core.locator import Locator, by_a11y_id


def test_resolve_returns_platform_selector():
    loc = Locator(
        name="submit",
        android=(AppiumBy.ID, "com.app:id/submit"),
        ios=(AppiumBy.IOS_PREDICATE, "name == 'submit'"),
    )
    assert loc.resolve("android") == (AppiumBy.ID, "com.app:id/submit")
    assert loc.resolve("ios") == (AppiumBy.IOS_PREDICATE, "name == 'submit'")


def test_resolve_missing_platform_raises_with_locator_name():
    loc = Locator(name="submit", android=(AppiumBy.ID, "x"))
    with pytest.raises(ValueError, match="submit.*ios"):
        loc.resolve("ios")


def test_by_a11y_id_shares_selector_across_platforms():
    loc = by_a11y_id("submit", "submit_btn")
    assert loc.resolve("android") == (AppiumBy.ACCESSIBILITY_ID, "submit_btn")
    assert loc.resolve("android") == loc.resolve("ios")


def test_locator_is_immutable():
    loc = by_a11y_id("submit", "submit_btn")
    with pytest.raises(AttributeError):
        loc.name = "changed"
