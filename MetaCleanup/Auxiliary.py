"""
Contains basic functions necessary for cleanup, such as the edit distance 
function and formatting functions.
"""
AUDIO_EXT = ['.mp3', '.flac']
IMG_EXT = ['.jpg', '.png', '.gif']

# edit_distance is a standard low-cost edit-distance function

def edit_distance(s1, s2):
	if len(s1) > len(s2):
		n = len(s1)
		m = len(s2)
		temp0 = s1
		s1 = s2
		s2 = temp0
	else:
		n = len(s2)
		m = len(s1)

	v1 = []
	v2 = [0]

	for i in range(n + 1):
		v1.append(i)

	for i in range(n):
		v2.append(0)

	for i in range(m):

		v2[0] = i + 1

		for j in range(n):

			delCost = v1[j + 1] + 1
			insCost = v2[j] + 1
			if s1[i] == s2[j]:
				subCost = v1[j]
			else:
				subCost = v1[j] + 1

			v2[j + 1] = min(delCost, insCost, subCost)

		temp1 = v1
		v1 = v2
		v2 = temp1

	return v1[n]

# edit_err defines the acceptable edit distance between two names for one to be reasonably assumed
# as a misspelling of the other

def edit_err(s):
	if len(s) <= 6:
		return 1
	elif len(s) <= 10:
		return 2
	else:
		return round(len(s)/5)

# edit_comp returns True if its two input strings are within an acceptable edit distance from each
# other, False otherwise

def edit_comp(s, t):
	return edit_distance(s.lower(), t.lower()) <= edit_err(s)

# list_tracks lists files in directory with audio file extensions

def list_tracks(dirlist):
	return [x for x in dirlist for ext in AUDIO_EXT if x.endswith(ext)]

# list_tracks lists files in directory with image file extensions

def list_images(dirlist):
	return [x for x in dirlist for ext in IMG_EXT if x.endswith(ext)]

# list_ext creates an ordered list that matches 1 to 1 the extension of each track

def list_ext(dirlist):
	exts = []
	for x in dirlist:
		for ext in AUDIO_EXT:
			if x.endswith(ext):
				exts.append(ext)
	return exts

# format_path_name eliminates characters from album and track names that are invalid for file and 
# directory names

def format_path_name(path_name):
	invalid = '"?>:\\</'
	if path_name.endswith(' ') or path_name.endswith('.'):
		path_name = path_name[:-1]
	for char in path_name:
		if char in invalid:
			path_name = path_name.replace(char, '')
	return path_name

# format_track_number adds a '0' in front of single digit track numbers, for file-naming purposes

def format_track_number(integer):
	if integer < 10:
		return '0' + str(integer)
	else:
		return str(integer)
