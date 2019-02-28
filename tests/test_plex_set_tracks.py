import plex_set_tracks
import pytest
import requests
import utils


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
    requests.packages.urllib3.disable_warnings()
    user_server = plex_set_tracks.signInManagedUser(plex)
    assert plex.machineIdentifier == user_server.machineIdentifier
    assert plex._baseurl == user_server._baseurl
    assert plex._token != user_server._token, "Not signed in as managed user."
