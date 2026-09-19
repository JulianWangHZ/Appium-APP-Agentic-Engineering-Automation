# Screen code path: unknown (Flutter app, confirmed by live probe)
# Note: reaching home requires signup (login state does not persist) —
# the "signed in on the home screen" Given drives the full signup flow
Feature: Home
  As a signed-in user
  I want to browse and play content from the home screen
  So that I can quickly get back into my music

  Background:
    Given I am signed in on the home screen

  # ############################################
  # Jump back in
  # ############################################
  @home @regression @auto @jump_back_in
  Scenario: Scroll the "Jump back in" shelf
    When I scroll the "Jump back in" shelf
    Then a previously hidden "Jump back in" item is revealed

  # ############################################
  # Now playing / lyrics
  # ############################################
  @home @smoke @regression @auto @now_playing_lyrics
  Scenario: View lyrics of the now-playing track and return home
    When I open the now-playing track
    And I open the lyrics
    Then the lyrics are shown for the track "Enough is Enough"
    When I go back to the home screen
    Then the home screen is displayed

  # ############################################
  # Playlist
  # ############################################
  @home @regression @auto @open_playlist
  Scenario: Open a playlist, favorite it, and return home
    When I open the "american dream" playlist
    Then the "american dream" playlist view is displayed
    When I tap the favorite icon
    And I go back to the home screen
    Then the home screen is displayed
