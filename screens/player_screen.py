from appium.webdriver.common.appiumby import AppiumBy

from core.base_screen import BaseScreen
from core.locator import Locator

# Locators traced to evidence/home/home.feature.md (iOS-only; Android TODO)


def _predicate(name: str, expr: str) -> Locator:
    return Locator(name=name, ios=(AppiumBy.IOS_PREDICATE, expr))


class PlayerScreen(BaseScreen):
    PLAYING_TAB = _predicate("playing tab", "label == 'Playing' AND visible == 1")
    LYRICS_TAB = _predicate("lyrics tab", "label == 'Lyrics' AND visible == 1")

    def open_lyrics(self) -> None:
        """Tap the Lyrics tab at its CENTER — edge taps miss the StaticText."""
        element = self.find(self.LYRICS_TAB)
        rect = element.rect
        self.tap_by_coordinate(
            rect["x"] + rect["width"] // 2, rect["y"] + rect["height"] // 2)

    def lyrics_shown_for(self, track: str) -> bool:
        """On the lyrics view for this track: the Lyrics tab is active and the
        track title is visible in the player bar."""
        track_title = _predicate(f"player track title {track!r}", f"label == '{track}'")
        return self.is_visible(self.LYRICS_TAB, timeout=8) and self.is_visible(track_title)
