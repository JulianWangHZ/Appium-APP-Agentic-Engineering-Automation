"""Reusable signup orchestration — the UI equivalent of an api/workflows entry.

Spans greeting → signup → onboarding to reach the home screen. Two consumers:
the signup happy-path When step, and the shared "signed in on the home screen"
Given used as a precondition by post-login features.
"""
from __future__ import annotations

from screens.catalog import Screens

DEFAULT_EMAIL = "qa.signup@example.com"
DEFAULT_PASSWORD = "SignupPass123"
DISPLAY_NAME = "QA Test"
ARTISTS = ("21 Savage", "Adele", "Cardi B")
PODCASTS = ("The Joe Rogan Experience", "StarTalk Radio", "Podcast P")


def complete_signup(
    screens: Screens,
    email: str = DEFAULT_EMAIL,
    password: str = DEFAULT_PASSWORD,
) -> None:
    """Drive the full signup flow; leaves the app on the home screen."""
    screens.greeting.start_signup()
    screens.signup.submit_email(email)
    screens.signup.submit_password(password)
    screens.signup.keep_default_gender()
    screens.signup.create_account(DISPLAY_NAME)
    screens.onboarding.choose_artists(*ARTISTS)
    screens.onboarding.choose_podcasts(*PODCASTS)
