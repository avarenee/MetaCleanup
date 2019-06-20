"""
Contains functions used with the mutagen package
"""
import os
import mutagen

# load_by_ext takes a path to a track and returns the track as "loaded" in mutagen

def load_by_ext(path):
	if path.endswith('.flac'):
		return mutagen.flac.FLAC(path)
	if path.endswith('.mp3'):
		return mutagen.mp3.EasyMP3(path)

# load_tracks loads all tracks for an album

def load_tracks(root, dirlist):
	return [load_by_ext(os.path.join(root, path)) for path in dirlist]

# get_tags returns a list of all tag keys for an album 

def get_tags(dirlist):
	tags = []
	for track in dirlist:
		tags = [tag for tag in track.keys() if tag not in tags]
	return tags

# parse_tags returns a list of all unique tag values in an album for a specified tag key

def parse_tag(tag, files):
	metadata = []
	try:
		for file in files:
			for name in file[tag]:
				if name not in metadata:
					metadata.append(name)
	except KeyError:
		return []
	return metadata