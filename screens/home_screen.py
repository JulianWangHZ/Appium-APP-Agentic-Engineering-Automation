from appium.webdriver.common.appiumby import AppiumBy

from core.base_screen import BaseScreen
from core.locator import Locator

# Locators traced to evidence/auth/signup.feature.md and
# evidence/home/home.feature.md (iOS-only; Android TODO)


def _predicate(name: str, expr: str) -> Locator:
    return Locator(name=name, ios=(AppiumBy.IOS_PREDICATE, expr))


class HomeScreen(BaseScreen):
    # greeting text is time-of-day dependent ("Good morning/afternoon/evening")
    GREETING = _predicate("home greeting", "label BEGINSWITH 'Good' AND visible == 1")
    MUSIC_CHIP = _predicate("music filter chip", "label == 'Music' AND visible == 1")
    # tab label is "Home\nTab 1 of 3" — BEGINSWITH, never ==
    HOME_TAB = _predicate(
        "home tab", "label BEGINSWITH 'Home' AND type == 'XCUIElementTypeButton'")

    # Jump back in shelf (horizontal): anchor card visible initially, reveal
    # target off-screen until swiped left
    JUMP_BACK_IN_ANCHOR = _predicate(
        "jump back in first card", "label CONTAINS 'Future, Jack Harllow'")
    JUMP_BACK_IN_REVEAL = _predicate(
        "jump back in revealed card", "label CONTAINS 'For All The Dogs'")

    # now-playing mini-player: title+artist are one multiline label
    # ("Enough is Enough\nPost Malone") — BEGINSWITH, never ==
    NOW_PLAYING = _predicate("now-playing track", "label BEGINSWITH 'Enough is Enough'")

    def wait_loaded(self, timeout: float = 15) -> None:
        """Signup/login is only complete once home is fully rendered:
        greeting + content chips + tab bar, not just any single text."""
        self.wait_visible(self.GREETING, timeout)
        self.wait_visible(self.MUSIC_CHIP, timeout)
        self.wait_visible(self.HOME_TAB, timeout)

    def is_displayed(self, timeout: float = 5) -> bool:
        return self.is_visible(self.GREETING, timeout)

    def tab_bar_visible(self, timeout: float = 3) -> bool:
        """The bottom tab bar shows only on root-tab screens (home/search/
        library), never on pushed detail pages — a reliable 'logged in and at a
        tab root' signal."""
        return self.is_visible(self.HOME_TAB, timeout)

    def go_to_home_tab(self) -> None:
        """Return to a clean home root from any root-tab screen."""
        self.tap_stable(self.HOME_TAB)

    def scroll_jump_back_in(self) -> None:
        """Swipe the shelf left; asserts the reveal target was off-screen first
        so a passing test proves the scroll actually revealed it."""
        assert not self.is_visible(self.JUMP_BACK_IN_REVEAL, timeout=2), (
            "reveal target already visible before scrolling — test proves nothing"
        )
        self.swipe_left_at(self.JUMP_BACK_IN_ANCHOR)

    def jump_back_in_revealed(self, timeout: float = 5) -> bool:
        return self.is_visible(self.JUMP_BACK_IN_REVEAL, timeout)

    def open_now_playing(self) -> None:
        self.tap_stable(self.NOW_PLAYING)

    def open_playlist(self, name: str) -> None:
        self.tap_stable(_predicate(f"playlist tile {name!r}", f"label == '{name}'"))
