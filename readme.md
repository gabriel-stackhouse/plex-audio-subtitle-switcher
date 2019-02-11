Plex Batch Audio & Subtitle Switcher
====================================

Overview
--------
A script that allows for changing the default audio & subtitle streams of a TV show on a season or 
series level. After choosing your preferred audio and subtitle tracks for an episode, this script 
will attempt to find similar tracks in the remaining episodes you've specified, switching to them 
if matches were found.

It is made with ease-of-use in mind - simply run the script and it'll walk you through the process.

Installing Dependencies
-----------------------
**Dependencies:** Python 3, [python-plexapi](https://github.com/pkkid/python-plexapi), and 
[pyreadline](https://github.com/pyreadline/pyreadline), if running on Windows.

**Note:** As of this writing, the version of python-plexapi on the pip repository is out of date 
and unsupported by this script. So, we must install the version directly from github. Ensure that 
git is installed before you run the command below.

Install on Windows:

    pip install -r requirements.txt
    
Or on Linux:

    pip3 install -r requirements.txt

Running the Script
------------------
**Note:** This script assumes that the chosen episodes, and the audio and subtitle tracks within 
them, are relatively similar. Results may vary if modifying episodes from a wide range of sources.

0. **Optional:** Open plex_audio.py with a text editor and insert your Plex URL and API token in 
the spots indicated in the file. You will be prompted for this information if this step is not 
completed.

1. Run the script.  Windows: ```python ./plex_audio.py``` or Linux: ```python3 ./plex_audio.py```

2. Choose whether to connect to your Plex server locally (via your Plex URL and an API token), or 
online (via your Plex username and password).

3. Continue following the prompts in the script.

How it Works
------------
When the script is run, the user first chooses their preferred audio and subtitle tracks in one
episode. After that, it will check each audio/subtitle track in each remaining episode and look
for matches of their original choices.  Here's how a track is chosen:

**Audio:**

Always Matches | Sometimes Matches | Never Matches
-------------- | ----------------- | -------------
Title AND language codes are equal | Language codes are equal | Language codes are NOT equal
|| Codecs AND channel layout are equal ||
|| Indexes in files are equal ||

**Subtitles:**

Always Matches | Sometimes Matches | Never Matches
-------------- | ----------------- | -------------
Title AND language codes are equal | Language codes are equal | Language codes are NOT equal
|| Codecs are equal ||
|| Indexes in files are equal ||
|| Subtitle locations (internal vs. external) are equal ||
|| Subtitle forced flags are equal ||

So, if a track's title and language codes are equal to the original episode's, that track 
is considered a match. E.g., an English subtitle track titled "English Titles/Signs" will always 
match with another English track with the same title.

If there are no tracks with equal titles and language codes, the track with the most hits from
the middle column will be called a match (tie goes to the first track in the video).  Lastly, no
audio or subtitle tracks with different language codes can be considered a match.

Planned Feature Additions
-------------------------
A list of planned feature upgrades, in order of priority:

- [ ] Watcher to watch for new episodes of previously modified shows, switching their audio and 
subtitle tracks on the fly.

- [ ] Command-line arguments, so advanced users can bypass the prompts.

- [ ] Customizable matching conditions (if there is demand).
