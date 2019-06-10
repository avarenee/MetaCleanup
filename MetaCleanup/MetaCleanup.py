"""
*MetaCleanup v1.0*

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
is consistently and accurately tagged. HTML parsing is done with the 
requests_html module.

How to use: Let <dir> be a folder containing only album folders (folders with 
audio files all from the same album). Then, if you run: 

$ python3 MetaCleanup.py <dir>

This should clean up the metadata of all albums in <dir>

"""

import sys
import os
import requests
import requests_html
import mutagen.flac
import mutagen.mp3
import json
from collections import Counter
from shutil import move

# Project modules
import HTMLParsing as ref
import Auxiliary as aux

class Clean:

	def __init__(self, path, albums):
		self.path = path
		self.albums = albums

		# Create counts for final print-out statement

		self.trk_cnt = 0
		self.alb_cnt = 0
		self.dir_cnt = 0
		self.art_cnt = 0
		self.run()

    # get_album_info uses mutagen to create a dictionary with your album's metadata

	def get_album_info(self, temp_tracks, album_path):
		(artist, album, tracks, year, genre) = ([], [], {}, [], [])
		i = 1
		for track in temp_tracks:
			if track.endswith('.flac'):
				audiofile = mutagen.flac.FLAC(os.path.join(album_path, track))
			elif track.endswith('.mp3'):
				audiofile = mutagen.mp3.EasyMP3(os.path.join(album_path, track))
			else:
				print('Error: ' + track + ' is not a MetaCleanup supported file type.')
				pass
			artist = aux.add_all(audiofile['Artist'], artist)
			album = aux.add_all(audiofile['Album'], album)
			tracks[i] = audiofile['Title'][0]
			try:
				genre = aux.add_all(audiofile['Genre'], genre)
				year = aux.add_all(audiofile['Date'], year)
			except KeyError:
				pass
			except EasyID3KeyError:
				pass
			i += 1
		album_dict = aux.album_to_dict(artist, album, tracks, year, genre, '')
		return album_dict

	# discogs_get uses requests_html to search Discogs for your album, returns a dictionary with
	# data parsed from the album's 'master release' page

	def discogs_get(self, album_dir_name, album_dict):
		search_lib = [aux.format_search(album_dir_name)]
		for artist in album_dict['Artist']:
			for album in album_dict['Title']:
				search_lib.append(aux.format_search(artist + '+' + album))
		search_links = Counter()
		for search in search_lib:
			session = requests_html.HTMLSession()
			r = session.get(ref.discogs + ref.discogs_master + search)
			if r.ok:
				for link in r.html.links:
					if "/search/" not in link and "/seller/" not in link and "master" in link:
						search_links.update([link])
		master_urls = search_links.most_common(10)
		master_urls = [ref.discogs + i[0] for i in master_urls]
		for url in master_urls:
			if ref.similar_enough(album_dict, url):
				return ref.format_from_url(url)
		return

	# best_title_ind finds the track number of a track using Discogs data (this is for album 
	# folders which do not contain every track on the album, or which are not tagged with track
	# numbers)

	def best_title_ind(self, track, ind, tracklist):
		if track == tracklist[ind]:
			return ind
		elif aux.edit_distance(track.lower(), tracklist[ind].lower()) <= aux.edit_err(tracklist[ind].lower()):
			self.trk_cnt += 1
			return ind
		else:
			min_err = float("inf")
			for key in tracklist:
				err = aux.edit_distance(track.lower(), tracklist[key].lower())
				if err < min_err:
					min_err = err
					min_key = key
			self.trk_cnt += 1
			return min_key

	# add_art uses album art from Discogs to save the art as an image file to the album's directory

	def add_art(self, album_path, url):
		images_dir = os.listdir(album_path)
		images = aux.filter_by_extension(images_dir, "image")
		r = requests.get(url)
		if images == [] and r.ok:
			with open(album_path + 'cover.png', 'wb') as f:
				f.write(r.content)
			self.art_cnt += 1
		return

	def run(self):
		for album in self.albums:
			album_path = os.path.join(self.path, album)

			# obtain dictionary with album metadata

			temp_tracks = aux.filter_by_extension(os.listdir(album_path), "audio")
			print('Getting data for ' + album)
			album_dict = self.get_album_info(temp_tracks, album_path)

			# obtain dictionary using Discogs' master release page for the album

			verified_album_dict = self.discogs_get(album, album_dict)
			if verified_album_dict == None:
				print('Could not verify ' + album + ' with Discogs.\n')
				continue
			temp_trk_cnt = self.trk_cnt

			# re-name directory

			dir_rename = verified_album_dict["Artist"][0] + " - " + verified_album_dict["Title"][0]
			dir_rename = aux.format_path_name(dir_rename)
			if album != dir_rename:
				move(album_path, os.path.join(self.path, dir_rename))
				self.dir_cnt += 1
			album_path = os.path.join(self.path, dir_rename)
			track_total = len(verified_album_dict["Tracks"])
			print('Currently re-tagging ' + dir_rename)

            # re-tag each track

			for i in range(len(temp_tracks)): 
				if temp_tracks[i].endswith('.flac'):
					audiofile = mutagen.flac.FLAC(os.path.join(album_path, temp_tracks[i]))
					ext = '.flac'
				elif temp_tracks[i].endswith('.mp3'):
					audiofile = mutagen.mp3.EasyMP3(os.path.join(album_path, temp_tracks[i]))
					ext = '.mp3'
				else:
					print('Error: ' + temp_tracks[i] + ' is not a MetaCleanup supported file type.')
					pass
				ind = self.best_title_ind(album_dict["Tracks"][i + 1], i + 1, verified_album_dict["Tracks"])
				audiofile['Title'] = verified_album_dict["Tracks"][ind]
				audiofile['Artist'] = verified_album_dict["Artist"]
				audiofile['Album'] = verified_album_dict["Title"]
				audiofile['Genre'] = verified_album_dict["Genre"]
				try:
					audiofile['Date'] = verified_album_dict["Year"]
					audiofile['Tracknumber'] = str(ind)
					audiofile['Tracktotal'] = str(track_total)
				except KeyError:
					pass
				except EasyID3KeyError:
					pass
				audiofile.save(album_path + '/' + temp_tracks[i])

				# re-name each file

				file_rename = aux.format_track_number(i + 1) + ' - ' + aux.format_path_name(verified_album_dict["Tracks"][ind]) + ext
				move(os.path.join(album_path, temp_tracks[i]), os.path.join(album_path, file_rename))
			if album_dict["Artist"] != verified_album_dict["Artist"] or album_dict["Title"] != verified_album_dict["Title"] or temp_trk_cnt < self.trk_cnt:
				self.alb_cnt += 1

			# add art

			print('Adding art to ' + dir_rename + '\n')
			self.add_art(album_path, verified_album_dict["Cover"])

		print('Cleanup of your ' + os.path.basename(self.path) + ' folder complete!\n')
		print('Tagging fixed for ' + str(self.trk_cnt) + ' track(s) and ' + str(self.alb_cnt) + ' album(s).')
		print('Directory names for ' + str(self.dir_cnt) + ' album(s) changed.')
		print('Cover art added to ' + str(self.art_cnt) + ' album(s).')

		return

def main():
	path = sys.argv[1]
	albums = os.listdir(path)

	clean = Clean(path, albums)

if __name__ == '__main__':
	main()
