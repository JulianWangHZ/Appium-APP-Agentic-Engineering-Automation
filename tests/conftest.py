"""Shared steps and fixtures, reusable by every step-definition module.

Screens are injected through the single `screens` catalog fixture
(see screens/catalog.py) — steps take `screens: Screens` and use
`screens.signup`, `screens.home`, ... New screens never touch this file.

Given steps that arrange data via API pass it to later steps with target_fixture:

    @given("a registered user exists", target_fixture="user")
    def registered_user(api_client): ...
"""
from __future__ import annotations

import pytest
from pytest_bdd import given

from api.base_client import BaseApiClient
from config.settings import Settings
from core.app_session import AppSession
from flows.signup_flow import complete_signup
from screens.catalog import Screens


@pytest.fixture
def api_client(settings: Settings) -> BaseApiClient:
    """Switch to the matching domain-client subclass once one exists (one per domain)."""
    return BaseApiClient(settings)


@pytest.fixture
def app_session(driver, settings: Settings) -> AppSession:
    return AppSession(driver, settings)


@pytest.fixture
def screens(driver, settings: Settings) -> Screens:
    return Screens(driver, settings)


@given("the app is launched")
def app_is_launched(driver):
    """Driver creation launches the app; this step makes the precondition explicit."""


@given("the app is in logged-out state")
def app_logged_out(app_session: AppSession):
    app_session.reset_to_logged_out()


@given("the app is relaunched to the root screen")
def app_relaunched(app_session: AppSession):
    app_session.relaunch_to_root()


@given("I am signed in on the home screen")
def signed_in_on_home(app_session: AppSession, screens: Screens):
    """Post-login precondition, cheap when possible: if already logged in at a
    tab root (tab bar visible), just return to the Home tab — no re-signup.
    Otherwise (at greeting, or on a pushed detail page) relaunch and sign up
    (login state doesn't persist, so signup is the only path from greeting)."""
    if screens.home.tab_bar_visible():
        screens.home.go_to_home_tab()
    else:
        app_session.relaunch_to_root()
        complete_signup(screens)
    screens.home.wait_loaded()
