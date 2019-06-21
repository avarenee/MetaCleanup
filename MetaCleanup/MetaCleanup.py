"""
*MetaCleanup v1.05*

by avarenee

What it does: Corrects errant metadata in music files by cross-referencing 
databases and websearches

Motivation: Music download files are often poorly tagged, and such tagging 
destroys your organization abilities within your media player of choice. Going
through and correcting tags by hand is a tedious process that can take hours 
out of your day. MetaCleanup aims to automate this process, by verifying and 
consistently formatting metadata for .mp3 and .flac files.

How it works: MetaCleanup parses audio file metadata with Mutagen and 
cross-references the information with the database Discogs, ensuring the file 
is consistently and accurately tagged.

Update for v1.05:

How to use: Let <dir> be a folder containing only album folders (folders with 
audio files all from the same album). Then, if you run: 

$ python3 MetaCleanup.py <dir>

This should clean up the metadata of all albums in <dir>.
"""

import os
import sys
import time
import requests
import mutagen.mp3
import mutagen.flac
import discogs_client

# Project modules
import Auxiliary as aux
import MutagenTagging as tag
import DiscogsParsing as dis

class Counts(object):

	def __init__(self):
		self.track_count = 0
		self.album_count = 0
		self.directory_count = 0
		self.art_count = 0

class Album(object):

	def __init__(self, path):
		self.path = path
		self.tracks = aux.list_tracks(os.listdir(self.path))
		self.loaded_tracks = tag.load_tracks(self.path, self.tracks)
		self.tags = tag.get_tags(self.loaded_tracks)
		self.images = aux.list_images(os.listdir(self.path))
		self.ext = aux.list_ext(self.tracks)
		self.imposed_track_order = []
		self.encoded = tag.parse_tag("encodedby", self.loaded_tracks) == 'MetaCleanup'
		self.counts = Counts()

class Clean:

	def __init__(self, music_folder, discogs_object):
		self.music_folder = music_folder
		self.discogs_object = discogs_object
		self.albums = os.listdir(self.music_folder)
		self.counts = Counts()
		self.run()
		

	# dir_replace replaces the directory name for the album folder with "Artist - Title" from the
	# associated Discogs release 

	def dir_replace(self, album, release_name):
		os.rename(os.path.join(self.music_folder, album.path), os.path.join(self.music_folder, album.path + 'temp'))
		os.rename(os.path.join(self.music_folder, album.path + 'temp'), os.path.join(self.music_folder, release_name))
		album.path = os.path.join(self.music_folder, release_name)
		album.counts.directory_count += 1
		return

	# file_replace replaces the filename for the track with "Track Number - Track Title" from the
	# associated Discogs release 

	def file_replace(self, album, track_name, index):
		os.rename(os.path.join(album.path, album.tracks[index]), os.path.join(album.path, 'temp' + album.tracks[index]))
		os.rename(os.path.join(album.path, 'temp' + album.tracks[index]), os.path.join(album.path, track_name))
		return

	# add_art uses album art from Discogs to save the art as an image file to the album's directory

	def add_art(self, album, release):
		if album.images == [] and release.images != []:
			r = requests.get(release.images[0]['uri'])
			if r.ok:
				with open(os.path.join(album.path, 'cover.png'), 'wb') as f:
					f.write(r.content)
				album.counts.art_count += 1
		return

	# update_counts increments the amount of data changed overall by the amount of data changed for
	# one album

	def update_counts(self, counter1, counter2):
		counter1.track_count += counter2.track_count
		counter1.album_count += counter2.album_count
		counter1.directory_count += counter2.directory_count
		counter1.art_count += counter2.art_count
		return

	def run(self):
		for album_dir in self.albums: 
			album = Album(os.path.join(self.music_folder, album_dir))
			if album.encoded:
				continue
			discogs_utils = dis.DiscogsUtils(self.discogs_object)
			print('Searching Discogs for {0}'.format(album_dir))
			release_no = discogs_utils.get(album)
			if not release_no:
				print('Could not find {0} on Discogs.'.format(album_dir))
				continue
			release = discogs_utils.d.release(release_no)
			release_name = ', '.join([artist.name for artist in release.artists]) + ' - ' + release.title
			release_name = aux.format_path_name(release_name)
			self.dir_replace(album, release_name)
			print('Re-tagging {0}'.format(release_name))
			tag_dict = discogs_utils.TAG_DICT_STATIC(release_no)
			for i in range(len(album.tracks)):
				dynamic = discogs_utils.TAG_DICT_DYNAMIC(release_no, album.imposed_track_order[i])
				tag_dict.update(dynamic)
				track_name = tag_dict["tracknumber"] + ' - ' + tag_dict["title"] + album.ext[i]
				track_name = aux.format_path_name(track_name)
				for tag in tag_dict:
					album.loaded_tracks[i][tag] = tag_dict[tag]
				self.file_replace(album, track_name, i)
				album.loaded_tracks[i].save(os.path.join(album.path, track_name))
				album.counts.track_count += 1
				print('Tagging of track {0} successful!'.format(str(i + 1)))
				time.sleep(2.0)
			album.counts.album_count += 1
			print('Adding art\n')
			self.add_art(album, release)
			self.update_counts(self.counts, album.counts)
			time.sleep(5.0)

		print('Cleanup of your {0} folder complete!\n'.format(os.path.basename(self.music_folder)))
		print('Tagging fixed for {0} track(s) and {1} album(s).'.format(str(self.counts.track_count), str(self.counts.album_count)))
		print('Directory names for {0} album(s) changed.'.format(str(self.counts.directory_count)))
		print('Cover art added to {0} album(s).'.format(str(self.counts.art_count)))

		return

def main():
	music_folder = sys.argv[1]

	d = discogs_client.Client('MetaCleanup')
	d.set_consumer_key('ekYnBgTuKKglYnzQqCkr', 'PUWUCDgGtNtwAyRVInsPniFgqdIOQEWm')

	print('You must authorize this application in order to use it.')
	print('Please visit the following url: \n {0}'.format(d.get_authorize_url()[2]))
	print('After authorizing the application, you should receive a token.')
	token = input('Enter the token in the command line: ')
	d.get_access_token(token)

	print('\nStarting MetaCleanup\n')

	clean = Clean(music_folder, d)

if __name__ == '__main__':
	main()
