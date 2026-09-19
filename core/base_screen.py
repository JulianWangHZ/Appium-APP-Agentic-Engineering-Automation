"""BaseScreen: the App-wrapper layer — all Appium calls funnel through here.

Screens/steps never touch the raw driver. Implicit wait is 0; every read and
interaction is explicitly waited. Stale-safe patterns (tap_stable, wait_visible
with exception-swallowing poll) cover views that refresh mid-interaction
(animations, list reloads) — the element is found, then detached.
"""
from __future__ import annotations

import logging

from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import Settings
from core.locator import Locator
from core.wait import poll_until

logger = logging.getLogger("framework")

_STALE_SAFE = (StaleElementReferenceException, WebDriverException)


class BaseScreen:
    def __init__(self, driver: WebDriver, settings: Settings):
        self.driver = driver
        self.settings = settings
        self.platform = settings.platform
        self.timeout = settings.explicit_wait

    # ---- element access -------------------------------------------------
    def _wait(self, timeout: float | None = None) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout or self.timeout)

    def find(self, locator: Locator, timeout: float | None = None) -> WebElement:
        by, value = locator.resolve(self.platform)
        try:
            return self._wait(timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException as e:
            raise TimeoutException(
                f"Element {locator.name!r} not found within {timeout or self.timeout}s "
                f"({by}={value})"
            ) from e

    def _is_visible_now(self, locator: Locator) -> bool:
        """One-shot visibility check, no wait. Raises on stale — callers poll."""
        by, value = locator.resolve(self.platform)
        elements = self.driver.find_elements(by, value)
        return bool(elements) and elements[0].is_displayed()

    # ---- waits / assertions ---------------------------------------------
    # wait_* raise TimeoutError with the locator name — steps use them directly
    # as assertions; no separate expect layer needed under pytest.

    def wait_visible(self, locator: Locator, timeout: float | None = None) -> None:
        """Stale-safe: exceptions during re-render count as 'not yet', keep polling."""
        poll_until(
            lambda: self._is_visible_now(locator),
            timeout or self.timeout,
            message=f"{locator.name!r} not visible",
            swallow=_STALE_SAFE,
        )

    def wait_not_visible(self, locator: Locator, timeout: float | None = None) -> None:
        poll_until(
            lambda: not self._is_visible_now(locator),
            timeout or self.timeout,
            message=f"{locator.name!r} still visible",
            swallow=_STALE_SAFE,
        )

    def wait_enabled(self, locator: Locator, timeout: float | None = None) -> None:
        """Inputs may enable asynchronously after validation — visible ≠ enabled."""
        poll_until(
            lambda: self.find(locator, timeout=1).is_enabled(),
            timeout or self.timeout,
            message=f"{locator.name!r} not enabled",
            swallow=_STALE_SAFE,
        )

    def is_visible(self, locator: Locator, timeout: float = 5) -> bool:
        """Boolean probe for branching; for assertions prefer wait_visible."""
        try:
            self.wait_visible(locator, timeout)
            return True
        except TimeoutError:
            return False

    # ---- interactions ----------------------------------------------------
    def tap(self, locator: Locator) -> None:
        logger.info("tap: %s", locator.name)
        by, value = locator.resolve(self.platform)
        self._wait().until(EC.element_to_be_clickable((by, value))).click()

    def tap_stable(self, locator: Locator, timeout: float | None = None) -> None:
        """Stale-safe tap: element found then detached by a re-render → retry until
        the click itself succeeds (convergence signal is the successful click)."""

        def _try_click() -> bool:
            self.find(locator, timeout=1).click()
            return True

        logger.info("tap_stable: %s", locator.name)
        poll_until(
            _try_click,
            timeout or self.timeout,
            message=f"could not click {locator.name!r}",
            swallow=_STALE_SAFE,
        )

    def tap_by_coordinate(self, x: int, y: int) -> None:
        """Escape hatch for elements that reject element-level taps (custom-drawn controls)."""
        if self.platform == "android":
            self.driver.execute_script("mobile: clickGesture", {"x": x, "y": y})
        else:
            self.driver.execute_script("mobile: tap", {"x": x, "y": y})

    def tap_element_center(self, locator: Locator) -> None:
        """Coordinate-tap an element's center — bypasses enabled/actionability checks
        (some controls report enabled=false yet respond to taps)."""
        rect = self.find(locator).rect
        self.tap_by_coordinate(rect["x"] + rect["width"] // 2, rect["y"] + rect["height"] // 2)

    def type(self, locator: Locator, text: str, secret: bool = False) -> None:
        logger.info("type into %s: %s", locator.name, "***" if secret else text)
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def long_press(self, locator: Locator, duration_ms: int = 800) -> None:
        rect = self.find(locator).rect
        x, y = rect["x"] + rect["width"] // 2, rect["y"] + rect["height"] // 2
        if self.platform == "android":
            self.driver.execute_script(
                "mobile: longClickGesture", {"x": x, "y": y, "duration": duration_ms})
        else:
            self.driver.execute_script(
                "mobile: touchAndHold", {"x": x, "y": y, "duration": duration_ms / 1000})

    def tap_top_left_back(self) -> None:
        """Tap the app's shared top-left back/close icon. It is an unlabeled
        ~24×24 element (no accessibility id) present on pushed pages and the
        player; one coordinate hits both. Escape hatch — ask dev for an id."""
        self.tap_by_coordinate(28, 63)

    def hide_keyboard(self) -> None:
        if self.platform == "android":
            self.driver.execute_script("mobile: hideKeyboard", {})
        else:
            # iOS WDA: tapOutside is the reliable strategy (empty args flaky)
            self.driver.execute_script("mobile: hideKeyboard", {"strategy": "tapOutside"})

    # ---- reads -----------------------------------------------------------
    def text_of(self, locator: Locator) -> str:
        return self.find(locator).text

    # ---- scrolling -------------------------------------------------------
    def swipe_up(self, ratio: float = 0.5) -> None:
        size = self.driver.get_window_size()
        x = size["width"] // 2
        start_y = int(size["height"] * 0.7)
        end_y = int(size["height"] * (0.7 - ratio))
        self.driver.swipe(x, start_y, x, end_y, duration=400)

    def swipe_left_at(self, locator: Locator, ratio: float = 0.7) -> None:
        """Horizontal right-to-left swipe across the screen at an anchor's
        y-center — for horizontally-scrolling shelves. Spans most of the screen
        width (a within-one-card swipe is too short to page a carousel)."""
        y = self.find(locator).rect["y"] + self.find(locator).rect["height"] // 2
        width = self.driver.get_window_size()["width"]
        start_x = int(width * 0.9)
        end_x = int(width * (0.9 - ratio))
        self.driver.swipe(start_x, y, end_x, y, duration=500)

    def scroll_to(self, locator: Locator, max_swipes: int = 6) -> WebElement:
        for _ in range(max_swipes):
            if self.is_visible(locator, timeout=2):
                return self.find(locator)
            self.swipe_up(0.4)
        raise TimeoutException(f"Element {locator.name!r} not visible after {max_swipes} swipes")
