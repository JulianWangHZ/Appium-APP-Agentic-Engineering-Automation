from pytest_bdd import parsers, scenarios, then, when

from flows.signup_flow import complete_signup
from screens.catalog import Screens

scenarios("auth/signup.feature")


@when(parsers.parse(
    'I sign up for a free account with email "{email}" and password "{password}"'))
def sign_up_free(screens: Screens, email: str, password: str):
    complete_signup(screens, email, password)


@then("I am signed in and the home screen is displayed")
def home_displayed(screens: Screens):
    screens.home.wait_loaded()


@when(parsers.parse('I begin signup with email "{email}"'))
def begin_signup(screens: Screens, email: str):
    screens.greeting.start_signup()
    screens.signup.submit_email(email)


@when(parsers.parse('I submit the password "{password}"'))
def submit_password(screens: Screens, password: str):
    screens.signup.submit_password(password)


@then("the signup flow stays on the email step")
def stays_on_email_step(screens: Screens):
    assert screens.signup.stayed_on_email_step(), (
        "signup advanced past the email step despite a too-short email"
    )


@then("the signup flow stays on the password step")
def stays_on_password_step(screens: Screens):
    assert screens.signup.stayed_on_password_step(), (
        "signup advanced past the password step despite a too-short password"
    )
