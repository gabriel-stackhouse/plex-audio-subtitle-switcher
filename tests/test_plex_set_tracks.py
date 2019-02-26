import plex_set_tracks


def test_get_num(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: "28")
    assert int(plex_set_tracks.getNumFromUser("")) == 28


def test_get_yes_or_no(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda x: "y")
    assert plex_set_tracks.getYesOrNoFromUser("") == "y"
    monkeypatch.setattr('builtins.input', lambda x: "n")
    assert plex_set_tracks.getYesOrNoFromUser("") == "n"
