from appium.webdriver.common.appiumby import AppiumBy

from core.base_screen import BaseScreen
from core.locator import Locator

# Locators traced to evidence/auth/signup.feature.md (iOS-only; Android TODO).
# The Flutter build exposes no Semantics identifiers — all locators are text-based.


class SignupScreen(BaseScreen):
    EMAIL_HEADER = Locator(
        name="email step header",
        ios=(AppiumBy.IOS_PREDICATE, 'label == "What\'s your email?"'),
    )
    PASSWORD_HEADER = Locator(
        name="password step header",
        ios=(AppiumBy.IOS_PREDICATE, "label == 'Create a password'"),
    )
    GENDER_HEADER = Locator(
        name="gender step header",
        ios=(AppiumBy.IOS_PREDICATE, 'label == "What\'s your gender?"'),
    )
    NAME_HEADER = Locator(
        name="name step header",
        ios=(AppiumBy.IOS_PREDICATE, 'label == "What\'s your name?"'),
    )
    # each step shows exactly one text field; the app gives it no identifier
    INPUT_FIELD = Locator(
        name="signup input field",
        ios=(AppiumBy.IOS_CLASS_CHAIN, "**/XCUIElementTypeTextField"),
    )
    NEXT = Locator(  # rendered as StaticText, not Button
        name="next button",
        ios=(AppiumBy.IOS_PREDICATE, "label == 'Next' AND visible == 1"),
    )
    CREATE_ACCOUNT = Locator(
        name="create an account button",
        ios=(AppiumBy.IOS_PREDICATE, "label == 'Create an account'"),
    )

    def submit_email(self, email: str) -> None:
        self.wait_visible(self.EMAIL_HEADER)
        self.type(self.INPUT_FIELD, email)
        self.tap_stable(self.NEXT)

    def submit_password(self, password: str) -> None:
        self.wait_visible(self.PASSWORD_HEADER)
        self.type(self.INPUT_FIELD, password, secret=True)
        self.tap_stable(self.NEXT)

    def keep_default_gender(self) -> None:
        self.wait_visible(self.GENDER_HEADER)
        self.tap_stable(self.NEXT)

    def stayed_on_email_step(self, settle: float = 3) -> bool:
        """True when tapping Next did NOT advance past the email step.
        Flutter reports enabled=true on the disabled Next — never assert enabled;
        give the app a settle window to (wrongly) navigate, then confirm."""
        if self.is_visible(self.PASSWORD_HEADER, timeout=settle):
            return False
        return self.is_visible(self.EMAIL_HEADER, timeout=2)

    def stayed_on_password_step(self, settle: float = 3) -> bool:
        """True when tapping Next did NOT advance past the password step."""
        if self.is_visible(self.GENDER_HEADER, timeout=settle):
            return False
        return self.is_visible(self.PASSWORD_HEADER, timeout=2)

    def create_account(self, display_name: str) -> None:
        self.wait_visible(self.NAME_HEADER)
        self.type(self.INPUT_FIELD, display_name)
        # the submit sits at the screen bottom, under the keyboard
        self.hide_keyboard()
        self.tap_stable(self.CREATE_ACCOUNT)
