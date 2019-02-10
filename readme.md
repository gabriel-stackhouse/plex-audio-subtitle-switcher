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

0. *Optional:* Open plex_audio.py with a text editor and insert your Plex URL and API token in the 
spots indicated in the file. You will be prompted for this information if this step is not completed.

1. Run the script.  Windows: ```python ./plex_audio.py``` or Linux: ```python3 ./plex_audio.py```

2. Choose whether to connect to your Plex server locally (via your Plex URL and an API token), or 
online (via your Plex username and password).

3. Continue following the prompts in the script.

How it Works
------------
TODO -- fill out this section.

Planned Features
----------------
TODO -- fill out this section.
