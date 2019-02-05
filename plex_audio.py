from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
from plexapi.client import PlexClient
from plexapi.exceptions import NotFound
from plexapi.exceptions import BadRequest
import getpass

###################################################################################################
## Plex Connection Info (Optional - will prompt for info if left blank)
###################################################################################################

PLEX_URL='http://192.168.1.50:32400'			# URL to Plex server (optional). Ex. http://192.168.1.50:32400
PLEX_TOKEN = 'kboUyRzgTANGM2BnXmr3'		# Plex authentication token (optional). Info here: https://bit.ly/2p7RtOu

###################################################################################################
## Helper Functions
###################################################################################################

def getNumFromUser(prompt):
	while True:
		givenNum = input(prompt)
		try:
			num = int(givenNum)
		except ValueError:
			print("Error: '%s' is not an integer." % (givenNum))
			continue
		return num
		
def getYesOrNoFromUser(prompt):
	isValidInput = False
	while isValidInput == False:
		givenInput = input(prompt).lower()
		if givenInput == 'y' or givenInput == 'n':
			isValidInput = True
		else:
			print("Error: Invalid input")
	return givenInput
		
def getSeasonsFromUser(show):
	allSeasonsValid = False
	while allSeasonsValid == False:
	
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
		givenSeasons = givenSeasons.replace(" ", "")	# Remove spaces
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
		if curSeasonIsValid == True:	# If we got through all seasons successfully, they are all valid
			allSeasonsValid = True
	
	# Return valid seasons to modify
	return givenSeasonsList
			
def printStreams(episode):
	
	# Get audio & subtitle streams
	episode.reload()
	part = episode.media[0].parts[0]	# TODO - modify to support multiple files per episode (for part in parts: [don't worry about media list])
	audioStreams = part.audioStreams()
	subtitleStreams = part.subtitleStreams()

	# Print audio streams
	# print("\nAudio & subtitle settings for '%s %s - %s':\n" % (episode.show().title, episode.seasonEpisode.upper(), episode.title))
	print("Audio:\n")
	for stream in audioStreams:
		selected = ""
		if stream.selected == True:
			selected = "*"
		print("\t[%d%s] | Title: %s | Language: %s | Codec: %s | Channels: %s" % (
			stream.index, selected, stream.title, stream.languageCode, stream.codec, stream.audioChannelLayout))
	
	# Print subtitle streams
	if len(subtitleStreams) > 0:
		print("\nSubtitles:\n")
		for stream in subtitleStreams:
			selected = ""
			if stream.selected == True:
				selected = "*"
			print("\t[%d%s] | Title: %s | Language: %s | Format: %s | Location: %s" % (	# TODO - access 'forced' flag
				stream.index, selected, stream.title, stream.languageCode, stream.codec, "Internal" if stream.index >= 0 else "External"))
	
	print("")	# Final new line 
				
def signIn():

	# Sign in locally or online?
	localSignIn = getYesOrNoFromUser("Connect to server locally? (Must choose yes if signing in as managed user) [Y/n]: ")

	# Connect to Plex server
	if localSignIn == 'y':
		
		# Connect to Plex server locally
		global PLEX_URL
		global PLEX_TOKEN
		isSignedIn = False
		while isSignedIn == False:
			if PLEX_URL == '' or PLEX_TOKEN == '':
				PLEX_URL = input("Input server URL [Ex. http://192.168.1.50:32400]: ")
				PLEX_TOKEN = input("Input Plex access token [Info here: https://bit.ly/2p7RtOu]: ")
			print("Signing in...")
			try:
				plex = PlexServer(PLEX_URL, PLEX_TOKEN)
			except:
				print("Error: Connection failed. Is your login info correct?")
				continue
			account = plex.myPlexAccount()
			isSignedIn = True

		# Give option to sign in as Managed User if server has them
		if account.subscriptionActive == True and account.homeSize > 1:
		
			# Sign in as managed user?
			useManagedUser = getYesOrNoFromUser("Sign in as managed user? [Y/n]: ")
			
			# If yes, sign in as managed user
			if useManagedUser == 'y':
			
				# Get all home users
				homeUsers = []
				for user in account.users():
					if user.home == True:
						homeUsers.append(user.title)
			
				# Which user?
				isValidUser = False
				while isValidUser == False:
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
					if isValidUser == False:
						print("Error: User does not exist.")
						
				# Sign in with managed user
				print("Signing in as '%s'..." % (givenManagedUser))
				managedUser = account.user(givenManagedUser)
				plex = PlexServer(PLEX_URL, managedUser.get_token(plex.machineIdentifier))

	# Not signing in locally, so connect to Plex server using MyPlex		
	else:
		isSignedIn = False
		while isSignedIn == False:
		
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

movie = plex.library.section('Movies').get('Love Actually')
printStreams(movie)
input("halt...")



# Choose library
allLibraries = plex.library.sections()
gotLibrary = False
while gotLibrary == False:	# Iterate until valid library is chosen

	# Get library from user
	print("Which library is the show in? [", end="")
	isFirstLibrary = True
	for lib in allLibraries:	# Display all TV library options
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
library = plex.library.section(givenLibrary.lower())	# Got valid library

# Get show to adjust from user
inLibrary = False
while inLibrary == False:
	givenShow = input("Which show should we adjust? (Type 'list' to list all shows): ")
	
	# If 'list' is typed, print shows in library
	if givenShow.lower() == "list":
		showsList = library.search(libtype="show")
		for show in showsList:
			print(show.title)
	
	# Otherwise, get show
	else:
		try:
			show = library.get(givenShow)
			inLibrary = True	# Found show if we got here
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
		print("%s %s%s" % ("," if len(seasonsToModify) > 2 else "", "and " if i == len(seasonsToModify) - 1 else "", season), end="")
	i+=1
print(" of '%s'." % (show.title))

# Print audio & subtitle streams for first episode 
episode = show.season(int(seasonsToModify[0])).episodes()[0]	# First episode (TODO -- fix season 0)
printStreams(episode)

# Display settings for another episode?
displayingEpisodes = True
while displayingEpisodes == True:

	displayEpisode = getYesOrNoFromUser("Display settings for another episode? [Y/n]: ")
	if displayEpisode == 'y':
		
		# Get season/episode number
		seasonNum = getNumFromUser("Season number: ")
		episodeNum = getNumFromUser("Episode number: ")
		
		# Print episode settings
		try:
			episode = show.episode(season=seasonNum, episode=episodeNum)
		except (BadRequest, NotFound) :
			print("s%02de%02d of '%s' is not in your library." % (seasonNum, episodeNum, show.title))
		else:
			printStreams(episode)
	else:
		displayingEpisodes = False
		
# Get indexes of streams user would like to set as default
audioStreams = episode.media[0].parts[0].audioStreams()
subtitleStreams = episode.media[0].parts[0].subtitleStreams()
audioIndex = None
subtitleIndex = None
adjustAudio = getYesOrNoFromUser("Do you want to switch audio tracks? ")
if adjustAudio == 'y':
	audioIndex = getNumFromUser("Choose the number corresponding to the audio track you'd like to switch to: ")

adjustSubtitles = getYesOrNoFromUser("Do you want to switch subtitle tracks? ")
if adjustSubtitles == 'y':
	givenSubtitleIndex = input("Choose the number corresponding to the subtitle track you'd like to switch to (Leave blank for no subtitles): ").lower()
	if givenSubtitlesIndex != "":
		isInt = False 
		while isInt == False:
			try:
				subtitleIndex = int(subtitleIndex)
			except ValueError:
				print("Error: '%s' is not an integer." % (givenNum))
			else:
				isInt = True
	else:
		subtitleIndex = 0
		
print("AudioIndex: %d | SubtitleIndex: %d" % (audioIndex, subtitleIndex))







	
		
		
		
		
################################################################################################################
## TODO - remove this block
################################################################################################################

# episode = plex.library.section('Anime').get('Cowboy Bebop').episodes()[1]
# episode.reload()
# episodePart = episode.media[0].parts[0]
# audioStreams = episodePart.audioStreams()
# subtitleStreams = episodePart.subtitleStreams()

# print("Audio & subtitle settings for '%s %s - %s'\n" % ("Cowboy Bebop", episode.seasonEpisode, episode.title))
# print("Audio:\n")
# for stream in audioStreams:
	# print("Index: %d | Title: %s | Language: %s | Codec: %s | Channels: %s | Selected: %s" % (
		# stream.index, stream.title, stream.language, stream.codec, stream.audioChannelLayout, stream.selected))
# print("\nSubtitles:\n")
# for stream in subtitleStreams:
	# print("Index: %d | Title: %s | Language: %s | Format: %s | Selected: %s" % (
		# stream.index, stream.title, stream.language, stream.codec, stream.selected))
# print("")

# audioTrack = int(input("Select audio track [-1 for no change]: "))
# subtitleTrack = int(input("Select subtitle track [0 for no subtitles, -1 for no change]: "))

# if audioTrack >= 0:
	# for stream in audioStreams:
		# if audioTrack == stream.index:
			
			# # Build URL 
			# url = "/library/parts/%d?audioStreamID=%d&allParts=1" % (episodePart.id, stream.id)
			
			# # Send server query
			# plex.query(url, method=plex._session.put)	# holy dog shit this works!

# if subtitleTrack == 0:
	
	# # Build URL 
	# url = "/library/parts/%d?subtitleStreamID=%d&allParts=1" % (episodePart.id, 0)
	
	# # Send server query
	# plex.query(url, method=plex._session.put)
	
# elif subtitleTrack > 0:
	# for stream in subtitleStreams:
		# if subtitleTrack == stream.index:
			
			# # Build URL 
			# url = "/library/parts/%d?subtitleStreamID=%d&allParts=1" % (episodePart.id, stream.id)
			
			# # Send server query
			# plex.query(url, method=plex._session.put)
			
			
# input("Sent query (hopefully)...")
		
	
	
# TODO -- Adjust audio & subtitles	