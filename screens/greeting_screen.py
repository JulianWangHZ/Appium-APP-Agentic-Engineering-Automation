from appium.webdriver.common.appiumby import AppiumBy

from core.base_screen import BaseScreen
from core.locator import Locator

# Locators traced to evidence/auth/signup.feature.md (iOS-only; Android TODO)


class GreetingScreen(BaseScreen):
    # label carries a stray U+064F diacritic ("ُSign up free") — CONTAINS, never ==
    SIGN_UP_FREE = Locator(
        name="sign up free button",
        ios=(AppiumBy.IOS_PREDICATE,
             "label CONTAINS 'Sign up free' AND type == 'XCUIElementTypeButton'"),
    )

    def start_signup(self) -> None:
        self.tap_stable(self.SIGN_UP_FREE)
