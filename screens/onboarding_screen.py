from appium.webdriver.common.appiumby import AppiumBy

from core.base_screen import BaseScreen
from core.locator import Locator

# Locators traced to evidence/auth/signup.feature.md (iOS-only; Android TODO)


def _cell(label: str) -> Locator:
    """Artist/podcast tile, located by its visible label."""
    return Locator(
        name=f"onboarding cell {label!r}",
        ios=(AppiumBy.IOS_PREDICATE, f"label == '{label}' AND visible == 1"),
    )


class OnboardingScreen(BaseScreen):
    ARTISTS_HEADER = Locator(
        name="choose artists header",
        ios=(AppiumBy.IOS_PREDICATE, "label == 'Choose 3 or more artists you like'"),
    )
    PODCASTS_HEADER = Locator(
        name="choose podcasts header",
        ios=(AppiumBy.IOS_PREDICATE, "label == 'Now choose some podcasts.'"),
    )
    DONE = Locator(
        name="done button",
        ios=(AppiumBy.ACCESSIBILITY_ID, "Done"),
        android=(AppiumBy.ACCESSIBILITY_ID, "Done"),
    )

    def choose_artists(self, *names: str) -> None:
        self.wait_visible(self.ARTISTS_HEADER)
        for name in names:
            self.tap_stable(_cell(name))
        self.tap_stable(self.DONE)

    def choose_podcasts(self, *names: str) -> None:
        self.wait_visible(self.PODCASTS_HEADER)
        for name in names:
            self.tap_stable(_cell(name))
        self.tap_stable(self.DONE)
