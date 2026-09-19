from pytest_bdd import parsers, scenarios, then, when

from screens.catalog import Screens

scenarios("home/home.feature")


# ---- Jump back in ----------------------------------------------------------

@when('I scroll the "Jump back in" shelf')
def scroll_jump_back_in(screens: Screens):
    screens.home.scroll_jump_back_in()


@then('a previously hidden "Jump back in" item is revealed')
def jump_back_in_revealed(screens: Screens):
    assert screens.home.jump_back_in_revealed(), (
        "no previously hidden item became visible after scrolling the shelf"
    )


# ---- Now playing / lyrics --------------------------------------------------

@when("I open the now-playing track")
def open_now_playing(screens: Screens):
    screens.home.open_now_playing()


@when("I open the lyrics")
def open_lyrics(screens: Screens):
    screens.player.open_lyrics()


@then(parsers.parse('the lyrics are shown for the track "{track}"'))
def lyrics_shown(screens: Screens, track: str):
    assert screens.player.lyrics_shown_for(track), (
        f"lyrics view for {track!r} not shown"
    )


@when("I go back to the home screen")
def go_back_home(screens: Screens):
    screens.navigate_back()


@then("the home screen is displayed")
def home_displayed(screens: Screens):
    assert screens.home.is_displayed(), "did not return to the home screen"


# ---- Playlist --------------------------------------------------------------

@when(parsers.parse('I open the "{name}" playlist'))
def open_playlist(screens: Screens, name: str):
    screens.home.open_playlist(name)


@when("I tap the favorite icon")
def tap_favorite(screens: Screens):
    screens.playlist.tap_favorite()


@then(parsers.parse('the "{name}" playlist view is displayed'))
def playlist_displayed(screens: Screens, name: str):
    assert screens.playlist.is_displayed(name), (
        f"the {name!r} playlist view is not displayed"
    )
