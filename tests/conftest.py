import configparser
import pytest
import requests
from plexapi.server import PlexServer

###################################################################################################
## Fixtures
###################################################################################################


@pytest.fixture(scope='session')
def plex():
    # Get info from config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    PLEX_URL = config['LOGIN']['PLEX_URL']
    PLEX_TOKEN = config['LOGIN']['PLEX_TOKEN']
    assert len(PLEX_URL) > 0, "Plex URL is not specified in config file."
    assert len(PLEX_TOKEN) > 0, "Plex token is not specified in config file."

    # Create PlexServer instance
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    session.verify = False
    return PlexServer(PLEX_URL, PLEX_TOKEN, session=session)


@pytest.fixture(scope='session')
def account(plex):
    return plex.myPlexAccount()


@pytest.fixture(scope='session')
def tvshows(plex):
    return plex.library.get("TV Shows")


@pytest.fixture(scope='session')
def show(tvshows):
    return tvshows.get("Game of Thrones")

###################################################################################################
## Helper Functions
###################################################################################################


def spoof_input(monkeypatch, input_list):
    """ Given a list of user input values, spoofs the input() function to to iterate over each item
        in the list with each successive call.

        Parameters:
            monkeypatch(MonkeyPatch): Monkeypatch from pytest.
            input_list(List<str>): List of input values to iterate over.
    """
    gen = (value for value in input_list)
    monkeypatch.setattr('builtins.input', lambda x: next(gen))
