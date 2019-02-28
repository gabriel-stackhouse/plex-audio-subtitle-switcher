import configparser
import pytest
import requests
from plexapi.server import PlexServer

# Get info from config file
config = configparser.ConfigParser()
config.read('config.ini')
PLEX_URL = config['LOGIN']['PLEX_URL']
PLEX_TOKEN = config['LOGIN']['PLEX_TOKEN']


@pytest.fixture(scope='session')
def plex():
    assert len(PLEX_URL) > 0, "Plex URL is not specified in config file."
    assert len(PLEX_TOKEN) > 0, "Plex token is not specified in config file."
    requests.packages.urllib3.disable_warnings()
    session = requests.Session()
    session.verify = False
    return PlexServer(PLEX_URL, PLEX_TOKEN, session=session)


@pytest.fixture(scope='session')
def tvshows(plex):
    return plex.library.get("TV Shows")


@pytest.fixture(scope='session')
def show(tvshows):
    return tvshows.get("Game of Thrones")
