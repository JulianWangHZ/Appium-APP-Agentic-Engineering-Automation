from appium.webdriver.common.appiumby import AppiumBy

from core.base_screen import BaseScreen
from core.locator import Locator

# Locators traced to evidence/home/home.feature.md (iOS-only; Android TODO)


def _predicate(name: str, expr: str) -> Locator:
    return Locator(name=name, ios=(AppiumBy.IOS_PREDICATE, expr))


class PlaylistScreen(BaseScreen):
    # "Album . 2023" metadata line — only on the detail view, distinguishes it
    # from the home tile that shares the playlist name
    DETAIL_META = _predicate("playlist metadata", "label BEGINSWITH 'Album'")

    def is_displayed(self, name: str) -> bool:
        title = _predicate(f"playlist title {name!r}", f"label == '{name}'")
        return self.is_visible(title, timeout=8) and self.is_visible(self.DETAIL_META)

    def tap_favorite(self) -> None:
        """Green heart in the action row below the header — unlabeled Image at
        (20, 417); coordinate tap toggles it green<->outline (dev should add id)."""
        self.tap_by_coordinate(30, 428)
