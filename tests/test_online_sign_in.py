import os
import plex_set_tracks
import requests
import pytest
from . import conftest as utils


@pytest.mark.timeout(45)
def test_sign_in_online(monkeypatch, plex):
    # Get login info from environment variables
    username = os.environ.get("PLEXAPI_AUTH_MYPLEX_USERNAME")
    password = os.environ.get("PLEXAPI_AUTH_MYPLEX_PASSWORD")
    server_name = os.environ.get("PLEXAPI_AUTH_SERVER_NAME")
    assert username, "Username environment variable not set."
    assert password, "Password environment variable not set."
    assert server_name, "Server name environment variable not set."

    # Spoof input and getpass to use login info
    utils.spoof_input(monkeypatch, [username, server_name])
    monkeypatch.setattr('getpass.getpass', lambda x: password)
    requests.packages.urllib3.disable_warnings()

    # Test signing in online
    online_plex = plex_set_tracks.signInOnline()
    assert plex.machineIdentifier == online_plex.machineIdentifier
    assert plex.friendlyName == online_plex.friendlyName
    assert plex.account().username == online_plex.account().username
