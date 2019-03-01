import configparser
import pytest
import requests
from plexapi.server import PlexServer
requests.packages.urllib3.disable_warnings()

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
    session = requests.Session()
    session.verify = False
    return PlexServer(PLEX_URL, PLEX_TOKEN, session=session)


@pytest.fixture(scope='session')
def account(plex):
    return plex.myPlexAccount()


@pytest.fixture(scope='session')
def tvshows(plex):
    return plex.library.section("TV Shows")


@pytest.fixture(scope='session')
def anime(plex):
    return plex.library.section("Anime")


@pytest.fixture(scope='session')
def show(tvshows):
    return tvshows.get("Game of Thrones")


@pytest.fixture(scope='session')
def seasons(show):
    return show.seasons()


@pytest.fixture(scope='session')
def episode(show):
    episode = show.episode(season=2, episode=9)
    episode.reload()
    return episode


@pytest.fixture(scope='session')
def mediapart(episode):
    return episode.media[0].parts[0]


@pytest.fixture(scope='session')
def audiostreams(mediapart):
    return mediapart.audioStreams()


@pytest.fixture(scope='session')
def audiostream(audiostreams):
    return audiostreams[0]


@pytest.fixture(scope='session')
def subtitlestreams(mediapart):
    return mediapart.subtitleStreams()


@pytest.fixture(scope='session')
def subtitlestream(subtitlestreams):
    return subtitlestreams[0]

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
