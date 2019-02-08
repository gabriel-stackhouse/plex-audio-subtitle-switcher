from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
from plexapi.client import PlexClient
from plexapi.exceptions import NotFound
from plexapi.exceptions import BadRequest
from plexapi.media import AudioStream
from plexapi.media import SubtitleStream
import getpass
import sys
import requests

###################################################################################################
## Plex Connection Info (Optional - will prompt for info if left blank)
###################################################################################################

PLEX_URL='https://192.168.1.50:32400'            # URL to Plex server (optional). Ex. https://192.168.1.50:32400
PLEX_TOKEN = 'kboUyRzgTANGM2BnXmr3'     # Plex authentication token (optional). Info here: https://bit.ly/2p7RtOu

###################################################################################################
## Classes
###################################################################################################

class AudioStreamInfo:
    """ Container class to hold info about an AudioStream
    
        Attributes:
            allStreamsIndex (int): Index of this :class:`~plexapi.media.AudioStream` in combined
                AudioStream + SubtitleStream list.
            audioChannelLayout (str): Audio channel layout (ex: 5.1(side)).
            audioStreamsIndex (int): Index of this :class:`~plexapi.media.AudioStream` 
                in MediaPart.audioStreams()
            codec (str): Codec of the stream (ex: srt, ac3, mpeg4).
            languageCode (str): Ascii code for language (ex: eng, tha).
            title (str): Title of the audio stream.
    """
    def __init__(self, audioStream, audioStreamsIndex):
        
        # Initialize variables
        self.allStreamsIndex = audioStreamsIndex
        self.audioChannelLayout = audioStream.audioChannelLayout
        self.audioStreamsIndex = audioStreamsIndex
        self.codec = audioStream.codec
        self.languageCode = audioStream.languageCode
        self.title = audioStream.title
        
class OrganizedStreams:
    """ Container class that stores AudioStreams and SubtitleStreams while allowing for
        additional organizational functionality.
    
        Attributes:
            audioStreams (list<:class:`~plexapi.media.AudioStream`>): List of all AudioStreams 
                in MediaPart
            externalSubs (list<:class:`~plexapi.media.SubtitleStream`>): List of all SubtitleStreams
                that are located in the MediaPart externally
            internalSubs (list<:class:`~plexapi.media.SubtitleStream`>): List of all SubtitleStreams
                that are located in the MediaPart internally
            part (:class:`~plexapi.media.MediaPart`): MediaPart that these streams belong to
            subtitleStreams (list<:class:`~plexapi.media.SubtitleStream`>): List of all
                SubtitleStreams in MediaPart
    """
    def __init__(self, mediaPart):
    
        # Store all streams
        self.part = mediaPart
        self.audioStreams = mediaPart.audioStreams()
        self.subtitleStreams = mediaPart.subtitleStreams()
        
        # Separate internal & external subtitles
        self.internalSubs = []
        self.externalSubs = []
        for stream in self.subtitleStreams:
            if stream.index >= 0:
                self.internalSubs.append(stream)
            else:
                self.externalSubs.append(stream)
                
    def allStreams(self):
        """ Return a list of all :class:`~plexapi.media.AudioStream` and 
            :class:`~plexapi.media.SubtitleStream`> in MediaPart."""
        return self.audioStreams + self.subtitleStreams
    
    def getIndexFromStream(self, givenStream):
        """ Return 1-index of given :class:`~plexapi.media.AudioStream` or 
            :class:`~plexapi.media.SubtitleStream`. """
        streams = self.allStreams()
        count = 1
        for stream in streams:
            if givenStream.id == stream.id:
                return count
            count += 1
        raise Exception("AudioStream or SubtitleStream not found.")
        
    def getStreamFromIndex(self, givenIndex):
        """ Return :class:`~plexapi.media.AudioStream` or 
            :class:`~plexapi.media.SubtitleStream` from a given index (1-index) """
        streams = self.allStreams()
        if givenIndex > len(streams) or givenIndex < 1:
            raise IndexError("Given index is out of range.")
        return streams[givenIndex - 1]
        
    def indexIsAudioStream(self, givenIndex):
        """ Return True if givenIndex is the index of an :class:`~plexapi.media.AudioStream`,
            False otherwise.
        """
        return givenIndex > 0 and givenIndex <= len(self.audioStreams)
        
    def indexIsSubStream(self, givenIndex):
        """ Return True if givenIndex is the index of a :class:`~plexapi.media.SubtitleStream`,
            False otherwise. """
        return givenIndex > len(self.audioStreams) and givenIndex <= \
            len(self.audioStreams) + len(self.subtitleStreams)
            
class SubtitleStreamInfo:
    """ Container class to hold info about a SubtitleStream
    
        Attributes:
            allStreamsIndex (int): Index of this :class:`~plexapi.media.SubtitleStream` in combined
                AudioStream + SubtitleStream list.
            codec (str): Codec of the stream (ex: srt, ac3, mpeg4).
            forced (bool): True if stream is a forced subtitle.
            languageCode (str): Ascii code for language (ex: eng, tha).
            location (str): "Internal" if subtitle is embedded in the video, "External" if it is not.
            subtitleStreamsIndex (int): Index of this :class:`~plexapi.media.SubtitleStream` 
                in MediaPart.subtitleStreams().
            title (str): Title of the subtitle stream.
    """
    def __init__(self, subtitleStream, allStreamsIndex, subtitleStreamsIndex):
        
        # Initialize variables
        self.allStreamsIndex = allStreamsIndex
        self.codec = subtitleStream.codec
        self.forced = subtitleStream.forced
        self.languageCode = subtitleStream.languageCode
        self.location = "Internal" if subtitleStream.index >= 0 else "External"
        self.subtitleStreamsIndex = subtitleStreamsIndex
        self.title = subtitleStream.title

###################################################################################################
## Helper Functions
###################################################################################################

def episodeToString(episode):
    """ Returns a string representation of an episode in the following format:
        "SXXEXX - Title"
        
        Parameters:
            episode(:class:`plexapi.video.Episode`): The episode that will be
                represented with a string.
    """
    return "%s - %s" % (episode.seasonEpisode.upper(), episode.title)
    
def getNumFromUser(prompt):
    """ Prompts for an integer from the user, only returning when a valid integer
        was entered.
        
        Parameters:
            prompt(str): The prompt the user will be given before receiving input.
    """
    while True:
        givenNum = input(prompt)
        try:
            num = int(givenNum)
        except ValueError:
            print("Error: '%s' is not an integer." % (givenNum))
            continue
        return num
        
def getSeasonsFromUser(show):
    """ Gets seasons of a show to be adjusted from the user, then checks if all
        seasons are valid and in the user's library. Continuously prompts user 
        until all seasons are valid.
        
        Parameters:
            show(:class:`~plexapi.video.Show`): The show the user will be choosing
                seasons from.
    """
    allSeasonsValid = False
    while not allSeasonsValid:
    
        # Get seasons users has in library
        seasonNums = []
        for season in show.seasons():
            if season.title == "Specials":
                seasonNums.append(0)
            else:
                seasonNums.append(int(season.title[7:]))

        # Display season numbers 
        print("You have the following seasons of '%s': [" % (show.title), end="")
        isFirstSeason = True
        for season in seasonNums:
            if isFirstSeason == True:
                print("%d" % (season), end="")
                isFirstSeason = False
            else:
                print("|%d" % (season), end="")
        print("]")

        # Choose seasons to modify
        givenSeasons = input("Which season(s) should we adjust? [Comma-separated, 'all' for entire series]: ")
        
        # If 'all' is typed, return all seasons
        if givenSeasons == "all":
            return seasonNums
        
        # Otherwise, check each season for validity
        givenSeasons = givenSeasons.replace(" ", "")    # Remove spaces
        givenSeasonsList = givenSeasons.split(',')
        for curSeason in givenSeasonsList:
            
            # First check if it's an integer
            curSeasonIsValid = False
            try:
                seasonInt = int(curSeason)
            except ValueError:
                print("Error: '%s' is not an integer." % (curSeason))
                break
            
            # Now check if they have said season in their library
            for season in seasonNums:
                if seasonInt == season:
                    curSeasonIsValid = True
                    break
            if curSeasonIsValid == False:
                print("Error: Season %d of '%s' is not in your library." % (seasonInt, show.title))
                break
        if curSeasonIsValid == True:    # If we got through all seasons successfully, they are all valid
            allSeasonsValid = True
    
    # Return valid seasons to modify
    return givenSeasonsList
    
def getYesOrNoFromUser(prompt):
    """ Prompts user for a 'y' or 'n' response, then validates. 
    
        Parameters:
            prompt(str): The prompt the user will be given before receiving input.
    """
    isValidInput = False
    while not isValidInput:
        givenInput = input(prompt).lower()
        if givenInput == 'y' or givenInput == 'n':
            isValidInput = True
        else:
            print("Error: Invalid input")
    return givenInput
    
def matchAudio(episodePart, template):
    """ Returns the :class:`~plexapi.media.AudioStream` from the given MediaPart that is
        the closest match to the given template.
        
        Parameters:
            episodePart(:class:`~plexapi.media.MediaPart`): MediaPart whose AudioStreams will
                be parsed to find the closest match.
            template(AudioStreamInfo): Info of an AudioStream that will act as a template
                for matching a stream from episodePart.
    """
    
    # Get episode streams
    episodeStreams = OrganizedStreams(episodePart)
    audioStreams = episodeStreams.audioStreams
    
    # Initialize variables
    winningIndex = -1   # Index of AudioStream in the lead (1-indexed)
    winningScore = -1   # Score of AudioStream in the lead
    curIndex = 1        # Current index being scored 
    
    for stream in audioStreams:
        
        # If title and language code match, AudioStream automatically matches
        if (stream.title and stream.title == template.title and 
                stream.languageCode == template.languageCode):
            return stream
            
        # Languages must be the same to even be considered for a match
        if stream.languageCode == template.languageCode:
            
            # Start scoring match
            curScore = 0
            
            # Audio codec and channel layout
            if (stream.codec == template.codec and 
                    stream.audioChannelLayout == template.audioChannelLayout):
                curScore += 1
            
            # Index in AudioStreams list
            if curIndex == template.audioStreamsIndex:
                curScore += 1
                
            # Check if AudioStream is winning
            if curScore > winningScore:
                winningScore = curScore
                winningIndex = curIndex
                
        # Increment counter
        curIndex += 1
        
    if winningScore >= 0:
        return audioStreams[winningIndex - 1]   # Must subtract one because array is 0-indexed
    
def matchSubtitles(episodePart, template):
    """ Returns the :class:`~plexapi.media.SubtitleStream` from the given MediaPart that is
        the closest match to the given template.
        
        Parameters:
            episodePart(:class:`~plexapi.media.MediaPart`): MediaPart whose AudioStreams will
                be parsed to find the closest match.
            template(SubtitleStreamInfo): Info of a SubtitleStream that will act as a template
                for matching a stream from episodePart.
    """
    
    # Get episode streams
    episodeStreams = OrganizedStreams(episodePart)
    subtitleStreams = episodeStreams.subtitleStreams
    
    # Initialize variables
    winningIndex = -1   # Index of AudioStream in the lead (1-indexed)
    winningScore = -1   # Score of AudioStream in the lead
    curIndex = 1        # Current index being scored
    
    for stream in subtitleStreams:
    
        # If title and language code match, SubtitleStream automatically matches
        if (stream.title and stream.title == template.title and 
                stream.languageCode == template.languageCode and
                stream.forced == template.forced):
            return stream
            
        # Languages must be the same to even be considered for a match
        if stream.languageCode == template.languageCode:
            
            # Start scoring match
            curScore = 0
            
            # Codec
            if stream.codec == template.codec:
                curScore += 1
            
            # Internal vs. external
            location = "Internal" if stream.index >= 0 else "External"
            if location == template.location:
                curScore += 1
                
            # Forced
            if stream.forced == template.forced:
                curScore += 1
                
            # Index in SubtitleStreams list
            if curIndex == template.subtitleStreamsIndex:
                curScore += 1
            
            # Check if SubtitleStream is winning
            if curScore > winningScore:
                winningScore = curScore
                winningIndex = curIndex
            
        # Increment counter
        curIndex += 1
        
    if winningScore >= 0:
        return subtitleStreams[winningIndex - 1]   # Must subtract one because array is 0-indexed
    
def printResetSubSuccess(episode):
    """ Prints a success message when subtitles are reset.
    
        Parameters:
            episode(:class:`plexapi.video.Episode`): The episode whose subtitles are reset.
    """
    print("Reset subtitles for '%s'" % episodeToString(episode))
    
def printSuccess(episode, newStream):
    """ Prints stream set successfully.
        
        Parameters:
            episode(:class:`~plexapi.video.Episode`): Episode in which audio was set.
            newStream(:class:`~plexapi.media.AudioStream`): The AudioStream that was applied.
    """
    if newStream.title:
        descriptor = "'%s' " % newStream.title
    elif newStream.language:
        descriptor = "'%s' " % newStream.languageCode
    else:
        descriptor = ""
    if isinstance(newStream, AudioStream):
        streamType = "audio"
    elif isinstance(newStream, SubtitleStream):
        streamType = "subtitle"
    print("Set %s %sfor '%s'" % (streamType, descriptor, episodeToString(episode)))
    
def printStreams(episode):
    """ Given an episode, prints all AudioStreams and SubtitleStreams.
    
        Parameters:
            episode(:class:`~plexapi.video.Episode`): The episode whose MediaPartStreams will be printed.
    """
    # Get audio & subtitle streams
    episode.reload()
    part = episode.media[0].parts[0]
    streams = OrganizedStreams(part)
        
    # Print audio streams
    count = 1
    print("\nAudio & subtitle settings for '%s %s':\n" % (episode.show().title, episodeToString(episode)))
    print("Audio:\n")
    for stream in streams.audioStreams:
        selected = ""
        if stream.selected == True:
            selected = "*"
        print("\t[%d%s] | Title: %s | Language: %s | Codec: %s | Channels: %s" % (
            count, selected, stream.title, stream.languageCode, stream.codec, stream.audioChannelLayout))
        count += 1
    print("\n\t* = Currently enabled track.\n")
    
    # Print subtitle streams
    if len(streams.subtitleStreams) > 0:
        print("Subtitles:\n")
        
        # Internal subtitles
        if len(streams.internalSubs) > 0 and len(streams.externalSubs) > 0:
            print("\tInternal:\n")
        count = printSubtitles(streams.internalSubs, startIndex=count)
        
        # External subtitles
        if len(streams.internalSubs) > 0 and len(streams.externalSubs) > 0:
            print("\n\tExternal:\n")
        printSubtitles(streams.externalSubs, startIndex=count)
        
        print("\n\t* = Currently enabled track.\n")
    
def printSubtitles(streams, startIndex=1):
    """ Given a list of SubtitleStreams, print their info. Index starts at startIndex, and
        function returns the last index used + 1.
    
        Parameters:
            streams(list<:class:`~plexapi.media.SubtitleStream`>): SubtitleStreams to be printsd
            startIndex(int): Index to start at (default = 1)
    """
    count = startIndex
    for stream in streams:
        selected = ""
        if stream.selected == True:
            selected = "*"
        print("\t[%d%s] | Title: %s | Language: %s | Format: %s | Forced: %s" % (
            count, selected, stream.title, stream.languageCode, stream.codec, stream.forced))
        count += 1
    return count

def signIn():
    """ Prompts user for Plex server info, then returns a :class:`~plexapi.server.PlexServer` instance."""
    
    # Sign in locally or online?
    localSignIn = getYesOrNoFromUser(
        "Connect to server locally? (Must choose yes if signing in as managed user) [Y/n]: ")

    # Connect to Plex server
    if localSignIn == 'y':
        
        # Connect to Plex server locally
        global PLEX_URL
        global PLEX_TOKEN
        isSignedIn = False
        while not isSignedIn:
            if PLEX_URL == '' or PLEX_TOKEN == '':
                PLEX_URL = input("Input server URL [Ex. http://192.168.1.50:32400]: ")
                PLEX_TOKEN = input("Input Plex access token [Info here: https://bit.ly/2p7RtOu]: ")
            print("Signing in...")
            try:
                requests.packages.urllib3.disable_warnings()
                session = requests.Session()
                session.verify = False
                plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=session)
            except:
                print("Error: Connection failed. Is your login info correct?")
                sys.exit()
            account = plex.myPlexAccount()
            isSignedIn = True

        # Give option to sign in as Managed User if server has them
        if account.subscriptionActive and account.homeSize > 1:
        
            # Sign in as managed user?
            useManagedUser = getYesOrNoFromUser("Sign in as managed user? [Y/n]: ")
            
            # If yes, sign in as managed user
            if useManagedUser == 'y':
            
                # Get all home users
                homeUsers = []
                for user in account.users():
                    if user.home:
                        homeUsers.append(user.title)
            
                # Which user?
                isValidUser = False
                while not isValidUser:
                    print("Managed user name [", end="")
                    firstUser = True
                    for user in homeUsers:
                        if firstUser == True:
                            print(user, end="")
                            firstUser = False
                        else:
                            print("|%s" % (user), end="")
                    givenManagedUser = input("]: ")
                    
                    # Check if valid user
                    for user in homeUsers:
                        if user.lower() == givenManagedUser.lower():
                            isValidUser = True
                            break
                    if not isValidUser:
                        print("Error: User does not exist.")
                        
                # Sign in with managed user
                print("Signing in as '%s'..." % (givenManagedUser))
                managedUser = account.user(givenManagedUser)
                plex = PlexServer(PLEX_URL, managedUser.get_token(plex.machineIdentifier))

    # Not signing in locally, so connect to Plex server using MyPlex        
    else:
        isSignedIn = False
        while not isSignedIn:
        
            # Get login info from user
            username = input("Plex username: ")
            password = getpass.getpass("Plex password: ")
            serverName = input("Plex server name: ")
            
            # Sign in via MyPlex
            print("Signing in (this may take awhile)...")
            try:
                account = MyPlexAccount(username, password)
            except:
                print("Error: Login failed. Are your credentials correct?")
                continue
            plex = account.resource(serverName).connect(ssl=True)
            isSignedIn = True
            
    # Signed in. Return server instance.
    print("Signed into server '%s'." % (plex.friendlyName))
    return plex

###################################################################################################
## Start Script
###################################################################################################

# Get Plex server instance
plex = signIn()

# Begin program loop
changingStreams = True
while changingStreams:

    # Choose library
    allLibraries = plex.library.sections()
    gotLibrary = False
    while not gotLibrary:  # Iterate until valid library is chosen

        # Get library from user
        print("Which library is the show in? [", end="")
        isFirstLibrary = True
        for lib in allLibraries:    # Display all TV library options
            if lib.type == "show" and isFirstLibrary == True:
                print(lib.title, end="")
                isFirstLibrary = False
            elif lib.type == "show":
                print("|%s" % (lib.title), end="")
        givenLibrary = input("]: ")

        # Check input 
        for lib in allLibraries:
            if lib.type == "show" and lib.title.lower() == givenLibrary.lower():
                gotLibrary = True
                break
        if gotLibrary == False:
            print("Error: '%s' is not a TV library." % (givenLibrary))
    library = plex.library.section(givenLibrary.lower())    # Got valid library


    # Get show to adjust from user
    inLibrary = False
    while not inLibrary:
        givenShow = input("Which show should we adjust? (Type 'list' to see all shows): ")
        
        # If 'list' is typed, print shows in library
        if givenShow.lower() == "list":
            showsList = library.search(libtype="show")
            for show in showsList:
                print(show.title)
        
        # Otherwise, get show
        else:
            try:
                show = library.get(givenShow)
                inLibrary = True    # Found show if we got here
            except NotFound:
                print("Error: '%s' is not in library '%s'." % (givenShow, library.title))

                
    # Get seasons of show to modify from user
    seasonsToModify = getSeasonsFromUser(show)


    # Print all seasons we'll modify
    print("Adjusting audio & subtitle settings for Season%s " % ("s" if len(seasonsToModify) > 1 else ""), end="")
    isFirstSeason = True
    i = 0
    for season in seasonsToModify:
        if isFirstSeason == True:
            print(season, end="")
            isFirstSeason = False 
        else:
            # Who gave the grammar nazi a software degree?
            print("%s %s%s" % ("," if len(seasonsToModify) > 2 else "", 
                "and " if i == len(seasonsToModify) - 1 else "", season), end="")
        i+=1
    print(" of '%s'." % (show.title))


    # Print audio & subtitle streams for first episode 
    episode = show.season(int(seasonsToModify[0])).episodes()[0]
    printStreams(episode)


    # Display settings for another episode?
    displayingEpisodes = True
    while displayingEpisodes:   # Continuously display episodes until user chooses not to

        # Display another episode?
        displayEpisode = getYesOrNoFromUser("Display settings for another episode? [Y/n]: ")
        if displayEpisode == 'y':
            
            # Get season/episode number
            seasonNum = getNumFromUser("Season number: ")
            episodeNum = getNumFromUser("Episode number: ")
            
            # Print episode settings
            try:
                episode = show.episode(season=seasonNum, episode=episodeNum)
            except (BadRequest, NotFound) :
                print("S%02dE%02d of '%s' is not in your library." % (seasonNum, episodeNum, show.title))
            else:
                printStreams(episode)
        
        else:   # User done displaying episodes
            displayingEpisodes = False

            
    # Get audio and subtitle streams of displayed episode
    episodePart = episode.media[0].parts[0]         # The episode file
    episodeStreams = OrganizedStreams(episodePart)  # Audio & subtitle streams


    # Get index of new audio stream from user
    audioIndex = None
    adjustAudio = getYesOrNoFromUser("Do you want to switch audio tracks? [Y/n]: ")
    if adjustAudio == 'y':
        isAudioStream = False
        
        # Begin validation loop
        while not isAudioStream:
            
            # Get index from user
            audioIndex = getNumFromUser("Choose the number for the audio track you'd like to switch to: ")
            
            # Validate index
            if episodeStreams.indexIsAudioStream(audioIndex):
                isAudioStream = True
            else:
                print("Error: Number does not correspond to an audio track.")

                
    # Get index of new subtitle stream from user
    subIndex = None
    adjustSubtitles = getYesOrNoFromUser("Do you want to switch subtitle tracks? [Y/n]: ")
    if adjustSubtitles == 'y':
        
        # Begin valiation loop
        isSubtitleStream = False
        while not isSubtitleStream:
            
            # Get sub index from user
            givenSubIndex = input("Choose the number for the subtitle track you'd like " +
                "to switch to, or leave blank to disable subtitles: ").lower()
            
            # If left blank, subtitles are disabled (0 index)
            if givenSubIndex == "":
                subIndex = 0
                isSubtitleStream = True
            
            # Else, check if it's a valid subtitle stream
            else:
            
                # Ensure user entered an integer
                try:
                    subIndex = int(givenSubIndex)
                except ValueError:
                    print("Error: '%s' is not an integer." % (givenSubIndex)) 
                else:
                    
                    # Validate
                    if episodeStreams.indexIsSubStream(subIndex) == True:
                        isSubtitleStream = True
                    else:
                        print("Error: Number does not correspond to a subtitle track.")


    # Final prompt
    #   TODO -- Show user seasons that will be adjusted and streams they will be matched to.
    #           Then ask if they'd like to continue.

                        
    # Adjust audio
    if adjustAudio == 'y':
        
        # Set audio settings for chosen episode 
        newAudio = episodeStreams.getStreamFromIndex(audioIndex)
        episodePart.setDefaultAudioStream(newAudio)
        
        # Create template for matching future episodes
        audioTemplate = AudioStreamInfo(newAudio, audioIndex)
        
        # Print result
        printSuccess(episode, newAudio)
        
    # Adjust subtitles
    if adjustSubtitles == 'y':
        
        # Set subtitle settings for chosen episode
        if subIndex == 0:
        
            # Reset subtitles
            episodePart.resetDefaultSubtitleStream()
            printResetSubSuccess(episode)
            
        else:
        
            # Set subtitle settings for the chosen episode
            newSubtitle = episodeStreams.getStreamFromIndex(subIndex)
            episodePart.setDefaultSubtitleStream(newSubtitle)
            
            # Create template for matching future episodes 
            subtitleTemplate = SubtitleStreamInfo(newSubtitle, subIndex,
                subIndex - len(episodeStreams.audioStreams))
            
            # Print result
            printSuccess(episode, newSubtitle)


    # Batch adjust audio & subtitle settings
    if adjustAudio == 'y' or adjustSubtitles == 'y':    # Skip loop if no adjustments will be made
        for seasonNum in seasonsToModify:    # Each season 
            season = show.season(int(seasonNum))
            
            for episode in season.episodes():    # Each episode in each season
                episode.reload()
                
                for part in episode.media[0].parts:    # Each MediaPart (file) for each episode

                    # Skip re-adjusting file we already modified
                    if part.id == episodePart.id:
                        continue
                        
                    # Set audio settings for MediaPart
                    if adjustAudio == 'y':
                        newAudio = matchAudio(part, audioTemplate)
                        if newAudio:
                        
                            # Set audio as default
                            part.setDefaultAudioStream(newAudio)
                            
                            # Print result
                            printSuccess(episode, newAudio)
                            
                        else:
                            print("No audio matches found for '%s'" % episodeToString(episode))
                            
                    # Reset subtitles if user chose to
                    if adjustSubtitles == 'y' and subIndex == 0:
                        part.resetDefaultSubtitleStream()
                        printResetSubSuccess(episode)
                    
                    # Set subtitle settings for MediaPart
                    elif adjustSubtitles == 'y' and subIndex > 0:
                        newSubtitle = matchSubtitles(part, subtitleTemplate)
                        if newSubtitle:
                            
                            # Set subtitle as default
                            part.setDefaultSubtitleStream(newSubtitle)
                            
                            # Print result
                            printSuccess(episode, newSubtitle)
                            
                        else:
                            print("No subtitle matches found for '%s'" % episodeToString(episode))
    
    # Completed!
    newShow = getYesOrNoFromUser("Audio & subtitle streams set! Modify another show? [Y/n]: ")
    if newShow == 'n':
        changingStreams = False