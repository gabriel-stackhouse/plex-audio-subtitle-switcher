import configparser
import plex_set_tracks
import pytest

# Get info from config file
config = configparser.ConfigParser()
config.read('config.ini')
PLEX_URL = config['LOGIN']['PLEX_URL']
PLEX_TOKEN = config['LOGIN']['PLEX_TOKEN']


@pytest.fixture(scope='session')
def plex():
    assert len(PLEX_URL) > 0, "Plex URL is not specified in config file."
    assert len(PLEX_TOKEN) > 0, "Plex token is not specified in config file."
    return plex_set_tracks.signInLocally()


@pytest.fixture(scope='session')
def tvshows(plex):
    return plex.library.get("TV Shows")


@pytest.fixture(scope='session')
def show(tvshows):
    return tvshows.get("Game of Thrones")
