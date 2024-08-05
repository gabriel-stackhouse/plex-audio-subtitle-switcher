## :warning: Archival Notice

All great things come to an end, and so too must this project. This script has filled a
much-needed void in Plex for myself and many others.  However, with the emergence of more 
mature solutions and my limited time to provide ongoing support, I believe it's the right
time to bring this project to a close.

I am truly humbled by the number of people who found use in a solution that, in all honesty,
I originally wrote just for myself.  As a programmer, there's no greater feeling than seeing
your code used and appreciated by others.  Thank you all for your incredible support of this 
project.

I highly recommend the excellent 
[Plex Auto Languages](https://github.com/RemiRigal/Plex-Auto-Languages)
project, which automatically updates languages on the fly, mimicking the Netflix experience. 
If you prefer a GUI, the equally excellent [PASTA](https://github.com/cglatot/pasta) is 
another great option.

Until next time!

Plex Audio & Subtitle Switcher
====================================
Batch Audio & Subtitle Switcher for Plex.

Overview
--------
A script that allows for changing the default audio & subtitle streams of a TV show on a season or 
series level. After choosing your preferred audio and subtitle tracks for an episode, this script 
will attempt to find similar tracks in the remaining episodes you've specified, switching to them 
if matches were found.

It is made with ease-of-use in mind - simply run the script and it'll walk you through the process.

Installing Dependencies
-----------------------
**Dependencies:** Python 3, [python-plexapi](https://github.com/pkkid/python-plexapi), 
[pyreadline](https://github.com/pyreadline/pyreadline) if running on Windows, and
[gnureadline](https://pypi.org/project/gnureadline/) if running on MacOS.

**Note:** As of this writing, the version of python-plexapi on the pip repository is out of date 
and unsupported by this script. So we must install the version directly from github. The command
below will do this automatically, so ensure that git is installed before running it.

Install on Windows:

    python setup.py
    
Or on Linux/MacOS:

    python3 setup.py

Running the Script
------------------
**Note:** This script assumes that the chosen episodes, and the audio and subtitle tracks within 
them, are relatively similar. Results may vary if modifying episodes from a wide range of sources.

0. **Optional:** Open config.ini with a text editor and insert your Plex URL and API token in the 
spots indicated in the file. You will be prompted for this information if this step is not 
completed.

1. Run the script.  Windows: ```python plex-audio-subtitle-switcher.py``` or Linux/MacOS: 
```python3 plex-audio-subtitle-switcher.py```.

2. Choose whether to connect to your Plex server locally (via your Plex URL and an API token), or 
online (via your Plex username and password).

3. Continue following the prompts in the script.

How it Works
------------
When the script is run, the user first chooses their preferred audio and subtitle tracks in one 
episode. After that, it will check each audio/subtitle track in each remaining episode and look for 
matches to their original choices.  Here's how a track is chosen:

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

So, if a track's title and language codes are equal to the original episode's, that track is 
considered a match. E.g., an English subtitle track titled "English Titles/Signs" will always match 
with another English track with the same title.

If there are no tracks with equal titles and language codes, the track with the most hits from the 
middle column will be called a match (tie goes to the first track in the video).  Lastly, no audio 
or subtitle tracks with different language codes can be considered a match.

Running Unit Tests
------------------
To run tests for plex-audio-subtitle-switcher, you must have a Plex library that contains all seasons of Game of
Thrones. Additionally, 'S02E10 - Valar Morghulis', must have at least one external subtitle.

First, install all additional dependencies:

    pip install setup/requirements-dev.txt

Next, you must provide a few environment variables:

* PLEXAPI_AUTH_MYPLEX_USERNAME: Your Plex username
* PLEXAPI_AUTH_MYPLEX_PASSWORD: Your Plex password
* PLEXAPI_AUTH_SERVER_NAME: Your Plex server name

Finally, run the tests:

    pytest -rxXs tests
    
Optionally, skip testing online sign-in (saves about 20 seconds):

    pytest -rxXs tests --ignore=tests/test_online_sign_in.py
