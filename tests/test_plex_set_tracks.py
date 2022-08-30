import plex-audio-subtitle-switcher
import pytest
from . import conftest as utils


def test_audiostream_info(audiostream):
    audiostream_info = plex-audio-subtitle-switcher.AudioStreamInfo(audiostream, 1)
    assert audiostream_info.allStreamsIndex == 1
    assert audiostream_info.audioChannelLayout == "5.1(side)"
    assert audiostream_info.audioStreamsIndex == 1
    assert audiostream_info.codec == "ac3"
    assert audiostream_info.languageCode == "eng"
    assert audiostream_info.title == "Dolby Digital-EX 5.1 @ 640 kbps"


def test_episode_to_string(episode):
    assert plex-audio-subtitle-switcher.episodeToString(episode) == \
        "S02E10 - Valar Morghulis"


def test_get_num_from_user(monkeypatch):
    utils.spoof_input(monkeypatch, ["7", "not_valid", "42"])
    assert int(plex-audio-subtitle-switcher.getNumFromUser("")) == 7
    assert int(plex-audio-subtitle-switcher.getNumFromUser("")) == 42


def test_get_yes_or_no(monkeypatch):
    utils.spoof_input(monkeypatch, ["y", "n", "not_valid", "y"])
    assert plex-audio-subtitle-switcher.getYesOrNoFromUser("") == "y"
    assert plex-audio-subtitle-switcher.getYesOrNoFromUser("") == "n"
    assert plex-audio-subtitle-switcher.getYesOrNoFromUser("") == "y"


def test_organized_streams(mediapart, audiostreams, subtitlestreams,
                           audiostream, subtitlestream):
    organized_streams = plex-audio-subtitle-switcher.OrganizedStreams(mediapart)

    # Test variables
    assert organized_streams.part.id == mediapart.id
    assert organized_streams.audioStreams == audiostreams
    assert organized_streams.subtitleStreams == subtitlestreams
    assert len(organized_streams.internalSubs) == 2
    assert len(organized_streams.externalSubs) == 1

    # Test functions
    assert organized_streams.allStreams() == audiostreams + subtitlestreams
    assert organized_streams.getIndexFromStream(audiostream) == 1
    assert organized_streams.getIndexFromStream(subtitlestream) == 3
    assert organized_streams.getStreamFromIndex(1) == audiostream
    assert organized_streams.getStreamFromIndex(3) == subtitlestream
    assert organized_streams.indexIsAudioStream(1)
    assert not organized_streams.indexIsAudioStream(3)
    assert not organized_streams.indexIsSubStream(1)
    assert not organized_streams.indexIsSubStream(6)
    assert organized_streams.indexIsSubStream(3)


def test_print_reset_subs(capsys, episode):
    plex-audio-subtitle-switcher.printResetSubSuccess(episode)
    captured = capsys.readouterr()
    assert captured.out == "Reset subtitles for 'S02E10 - Valar Morghulis'\n"


def test_match_audio(audiostream, mediapart2, mediapart3):
    # Test where titles & language codes match
    template = plex-audio-subtitle-switcher.AudioStreamInfo(audiostream, 1)
    matched_audio = plex-audio-subtitle-switcher.matchAudio(mediapart2, template)
    assert matched_audio.title == audiostream.title
    assert matched_audio.languageCode == audiostream.languageCode

    # Test where titles & language codes do not match
    matched_audio = plex-audio-subtitle-switcher.matchAudio(mediapart3, template)
    assert matched_audio.title != audiostream.title
    assert matched_audio.languageCode == audiostream.languageCode


def test_match_subtitles(subtitlestream, mediapart2, mediapart3):
    # Test where titles & language codes match
    template = plex-audio-subtitle-switcher.SubtitleStreamInfo(subtitlestream, 3, 1)
    matched_subtitle = plex-audio-subtitle-switcher.matchSubtitles(mediapart2, template)
    assert matched_subtitle.title == subtitlestream.title
    assert matched_subtitle.languageCode == subtitlestream.languageCode

    # Test where titles & language codes do not match
    matched_subtitle = plex-audio-subtitle-switcher.matchSubtitles(mediapart3, template)
    assert matched_subtitle.title != subtitlestream.title
    assert matched_subtitle.languageCode == subtitlestream.languageCode


def test_print_streams(capsys, episode):
    plex-audio-subtitle-switcher.printStreams(episode)
    captured = capsys.readouterr()
    streams = "\nAudio & subtitle settings for 'Game of Thrones S02E10 - " \
              "Valar Morghulis':\n\nAudio:\n\n\t[1*] | Title: " \
              "Dolby Digital-EX 5.1 @ 640 kbps | Language: eng | Codec: ac3 " \
              "| Channels: 5.1(side)\n\t[2] | Title: Dolby TrueHD Atmos 7.1 " \
              "@ 4382 kbps / 24-bit | Language: eng | Codec: truehd | " \
              "Channels: 7.1\n\n\t* = Currently enabled track.\n\nSubtitles:" \
              "\n\n\tInternal:\n\n\t[3*] | Title: English [for Dothraki " \
              "spoken parts] | Language: eng | Format: srt | Forced: False\n" \
              "\t[4] | Title: None | Language: eng | Format: srt | Forced: " \
              "False\n\n\tExternal:\n\n\t[5] | Title: None | Language: eng " \
              "| Format: srt | Forced: False\n\n\t* = Currently enabled " \
              "track.\n\n"
    assert captured.out == streams


def test_print_subtitles(capsys, mediapart):
    organized_streams = plex-audio-subtitle-switcher.OrganizedStreams(mediapart)
    result = plex-audio-subtitle-switcher.printSubtitles(organized_streams.internalSubs, 3)
    captured = capsys.readouterr()
    streams = "\t[3*] | Title: English [for Dothraki spoken parts] | " \
              "Language: eng | Format: srt | Forced: False\n\t[4] | Title: " \
              "None | Language: eng | Format: srt | Forced: False\n"
    assert captured.out == streams
    assert result == 5


def test_print_success(capsys, episode, audiostream, subtitlestream,
                       ext_subtitlestream):
    # Test audiostream
    plex-audio-subtitle-switcher.printSuccess(episode, audiostream)
    capture = capsys.readouterr()
    assert capture.out == "Set audio 'Dolby Digital-EX 5.1 @ 640 kbps' for " \
                          "'S02E10 - Valar Morghulis'\n"

    # Test subtitlestream
    plex-audio-subtitle-switcher.printSuccess(episode, subtitlestream)
    capture = capsys.readouterr()
    assert capture.out == "Set subtitle 'English [for Dothraki spoken " \
                          "parts]' for 'S02E10 - Valar Morghulis'\n"

    # Test stream without title
    plex-audio-subtitle-switcher.printSuccess(episode, ext_subtitlestream)
    capture = capsys.readouterr()
    assert capture.out == "Set subtitle 'eng' for 'S02E10 - Valar Morghulis'\n"


def test_seasons_to_string():
    assert plex-audio-subtitle-switcher.seasonsToString([2]) == "2"
    assert plex-audio-subtitle-switcher.seasonsToString([2, 5]) == "2 and 5"
    assert plex-audio-subtitle-switcher.seasonsToString([1, 3, 7]) == "1, 3, and 7"


def test_select_audio(monkeypatch, mediapart):
    utils.spoof_input(monkeypatch, ["3", "5", "10", "1"])
    streams = plex-audio-subtitle-switcher.OrganizedStreams(mediapart)
    index = plex-audio-subtitle-switcher.selectAudio(streams)
    assert index == 1   # First three choices should fail


def test_select_library(monkeypatch, plex, library, library2):
    utils.spoof_input(monkeypatch, ["TV Shows", "invalid", "Anime"])
    selected_library = plex-audio-subtitle-switcher.selectLibrary(plex)
    assert selected_library.uuid == library.uuid
    selected_library = plex-audio-subtitle-switcher.selectLibrary(plex)
    assert selected_library.uuid == library2.uuid


def test_select_seasons(monkeypatch, show):
    utils.spoof_input(monkeypatch, ["1, 2invalid, 4", "3, 15",
                                    "2", "5, 3, 6", "all"])
    seasonsList = plex-audio-subtitle-switcher.selectSeasons(show)
    assert seasonsList == [2]   # First 2 attempts should fail
    seasonsList = plex-audio-subtitle-switcher.selectSeasons(show)
    assert seasonsList == [5, 3, 6]
    seasonsList = plex-audio-subtitle-switcher.selectSeasons(show)
    assert seasonsList == [0, 1, 2, 3, 4, 5, 6, 7, 8]


def test_select_show(monkeypatch, library, show):
    utils.spoof_input(monkeypatch, ["invalid", "Game of Thrones"])
    selected_show = plex-audio-subtitle-switcher.selectShow(library)
    assert selected_show.title == show.title


def test_select_subtitles(monkeypatch, mediapart):
    utils.spoof_input(monkeypatch, ["2", "6", "3", "5", ""])
    streams = plex-audio-subtitle-switcher.OrganizedStreams(mediapart)
    index = plex-audio-subtitle-switcher.selectSubtitles(streams)
    assert index == 3   # First two should fail
    index = plex-audio-subtitle-switcher.selectSubtitles(streams)
    assert index == 5   # Test external subs
    index = plex-audio-subtitle-switcher.selectSubtitles(streams)
    assert index == -1


@pytest.mark.timeout(10)
def test_sign_in_locally(monkeypatch, plex):
    utils.spoof_input(monkeypatch, ['n'])
    local_plex = plex-audio-subtitle-switcher.signInLocally()
    assert plex.machineIdentifier == local_plex.machineIdentifier
    assert plex._baseurl == local_plex._baseurl
    assert plex._token == local_plex._token


@pytest.mark.timeout(10)
def test_sign_in_managed_user(monkeypatch, plex):
    utils.spoof_input(monkeypatch, ["Guest"])
    user_server = plex-audio-subtitle-switcher.signInManagedUser(plex)
    assert plex.machineIdentifier == user_server.machineIdentifier
    assert plex._baseurl == user_server._baseurl
    assert plex._token != user_server._token, "Not signed in as managed user."


def test_subtitlestream_info(subtitlestream):
    subtitlestream_info = plex-audio-subtitle-switcher.SubtitleStreamInfo(
        subtitlestream, 3, 1)
    assert subtitlestream_info.allStreamsIndex == 3
    assert subtitlestream_info.codec == "srt"
    assert not subtitlestream_info.forced
    assert subtitlestream_info.languageCode == "eng"
    assert subtitlestream_info.location == "Internal"
    assert subtitlestream_info.subtitleStreamsIndex == 1
    assert subtitlestream_info.title == "English [for Dothraki spoken parts]"
