# Screen code path: unknown (Flutter app, to be confirmed by live probe)
# Note: credentials below are disposable test data for the clone app —
# the backend enforces no uniqueness; real secrets would belong in .env
Feature: Signup
  As a new user
  I want to sign up for a free account
  So that I can start using the app

  Background:
    Given the app is launched
    And the app is relaunched to the root screen

  # ############################################
  # Sign up free
  # ############################################
  @signup @smoke @regression @auto @valid_account
  Scenario: Sign up for a free account with valid credentials
    When I sign up for a free account with email "qa.signup@example.com" and password "SignupPass123"
    Then I am signed in and the home screen is displayed

  # ############################################
  # Email validation
  # ############################################
  @signup @regression @auto @email_below_minimum
  Scenario: Cannot proceed with an email shorter than 6 characters
    When I begin signup with email "aaaaa"
    Then the signup flow stays on the email step

  # ############################################
  # Password validation
  # ############################################
  @signup @regression @auto @password_below_minimum
  Scenario: Cannot proceed with a password below the 8-character minimum
    When I begin signup with email "qa.signup@example.com"
    And I submit the password "1234567"
    Then the signup flow stays on the password step
