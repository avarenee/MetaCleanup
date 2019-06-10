"""
Contains basic functions necessary for cleanup, such as the edit distance 
function and formatting functions.
"""

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

# filter_by_extension filters the list of objects in the directory to compatible file types

def filter_by_extension(dirlist, type):
	if type == "audio":
		return list(filter(lambda x : x.endswith('.mp3') or x.endswith('.flac'), dirlist))
	if type == "image":
		dirlist = list(filter(lambda x : x.endswith('.jpg') or x.endswith('.png') or x.endswith('.gif'), dirlist))

# format_search formats a search query to be a valid url

def format_search(query):
	return query.replace(' ', '+')

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

# album_to_dict uses data to create a dictionary representation of an album

def album_to_dict(artist, album, tracks, year, genre, cover):
	album_dict = {"Artist" : artist, "Title" : album, "Tracks" : tracks, "Year" : year, "Genre" : genre, "Cover" : cover}
	return album_dict 

# add_all adds all items in a list to another

def add_all(items, item_list):
	for item in items:
		if item not in item_list:
			item_list += [item]
	return item_list

# format_track_number adds a '0' in front of single digit track numbers, for file-naming purposes

def format_track_number(integer):
	if integer < 10:
		return '0' + str(integer)
	else:
		return str(integer)
