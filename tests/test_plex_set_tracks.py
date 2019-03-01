import plex_set_tracks
import pytest
from . import conftest as utils


def test_get_num(monkeypatch):
    utils.spoof_input(monkeypatch, ["7", "not_valid", "42"])
    assert int(plex_set_tracks.getNumFromUser("")) == 7
    assert int(plex_set_tracks.getNumFromUser("")) == 42


def test_get_yes_or_no(monkeypatch):
    utils.spoof_input(monkeypatch, ["y", "n", "not_valid", "y"])
    assert plex_set_tracks.getYesOrNoFromUser("") == "y"
    assert plex_set_tracks.getYesOrNoFromUser("") == "n"
    assert plex_set_tracks.getYesOrNoFromUser("") == "y"


@pytest.mark.timeout(10)
def test_sign_in_locally(monkeypatch, plex):
    utils.spoof_input(monkeypatch, ['n'])
    local_plex = plex_set_tracks.signInLocally()
    assert plex.machineIdentifier == local_plex.machineIdentifier
    assert plex._baseurl == local_plex._baseurl
    assert plex._token == local_plex._token


@pytest.mark.timeout(10)
def test_sign_in_managed_user(monkeypatch, plex):
    utils.spoof_input(monkeypatch, ["Guest"])
    user_server = plex_set_tracks.signInManagedUser(plex)
    assert plex.machineIdentifier == user_server.machineIdentifier
    assert plex._baseurl == user_server._baseurl
    assert plex._token != user_server._token, "Not signed in as managed user."


def test_episode_to_string(episode):
    assert plex_set_tracks.episodeToString(episode) == "S02E09 - Blackwater"


def test_get_seasons_from_user(monkeypatch, show):
    utils.spoof_input(monkeypatch, ["1, 2invalid, 4", "3, 15",
                                    "2", "5, 3, 6", "all"])
    seasonsList = plex_set_tracks.getSeasonsFromUser(show)
    assert seasonsList == [2]   # First 2 attempts should fail
    seasonsList = plex_set_tracks.getSeasonsFromUser(show)
    assert seasonsList == [5, 3, 6]
    seasonsList = plex_set_tracks.getSeasonsFromUser(show)
    assert seasonsList == [0, 1, 2, 3, 4, 5, 6, 7]


def test_print_reset_subs(capsys, episode):
    plex_set_tracks.printResetSubSuccess(episode)
    captured = capsys.readouterr()
    assert captured.out == "Reset subtitles for 'S02E09 - Blackwater'\n"


def test_seasons_to_string():
    assert plex_set_tracks.seasonsToString([2]) == "2"
    assert plex_set_tracks.seasonsToString([2, 5]) == "2 and 5"
    assert plex_set_tracks.seasonsToString([1, 3, 7]) == "1, 3, and 7"
