"""Lazy screen catalog — the single injection point for all Screen Objects.

One `screens` fixture serves every step; screens instantiate on first access
and are cached per scenario. Adding a screen = one cached_property here,
no conftest changes:

    @cached_property
    def player(self) -> PlayerScreen:
        return PlayerScreen(self._driver, self._settings)
"""
from __future__ import annotations

from functools import cached_property

from appium.webdriver.webdriver import WebDriver

from config.settings import Settings
from core.base_screen import BaseScreen
from screens.greeting_screen import GreetingScreen
from screens.home_screen import HomeScreen
from screens.onboarding_screen import OnboardingScreen
from screens.player_screen import PlayerScreen
from screens.playlist_screen import PlaylistScreen
from screens.signup_screen import SignupScreen


class Screens:
    def __init__(self, driver: WebDriver, settings: Settings):
        self._driver = driver
        self._settings = settings

    @cached_property
    def greeting(self) -> GreetingScreen:
        return GreetingScreen(self._driver, self._settings)

    @cached_property
    def signup(self) -> SignupScreen:
        return SignupScreen(self._driver, self._settings)

    @cached_property
    def onboarding(self) -> OnboardingScreen:
        return OnboardingScreen(self._driver, self._settings)

    @cached_property
    def home(self) -> HomeScreen:
        return HomeScreen(self._driver, self._settings)

    @cached_property
    def player(self) -> PlayerScreen:
        return PlayerScreen(self._driver, self._settings)

    @cached_property
    def playlist(self) -> PlaylistScreen:
        return PlaylistScreen(self._driver, self._settings)

    @cached_property
    def _nav(self) -> BaseScreen:
        return BaseScreen(self._driver, self._settings)

    def navigate_back(self) -> None:
        """Screen-neutral back: taps the app's shared top-left back/close icon,
        used to leave the player or a playlist detail back toward home."""
        self._nav.tap_top_left_back()
