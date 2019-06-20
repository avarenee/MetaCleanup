"""
Contains functions used with the Discogs API
"""
import os
import time
import discogs_client

import Auxiliary as aux
import MutagenTagging as tag

class DiscogsUtils():

	# initializes with the API key

	def __init__(self, d):
		self.d = d

	# similar_enough compares a result from get with the album to see if the metadata matches

	def similar_enough(self, album, result):
		artists = tag.parse_tag("artist", album.loaded_tracks)
		titles = tag.parse_tag("album", album.loaded_tracks)
		tracks = tag.parse_tag("title", album.loaded_tracks)
		years = tag.parse_tag("date", album.loaded_tracks)
		discogs_album = self.d.release(result.id)
		artists_match = any([aux.edit_comp(artist1.name, artist2) for artist1 in discogs_album.artists for artist2 in artists])
		titles_match = any([aux.edit_comp(discogs_album.title, title) for title in titles])
		if artists_match and titles_match:
			if len(tracks) == len(discogs_album.tracklist):
				album.imposed_track_order = [i for i in range(len(tracks))]
				return True
			else:
				tracks_match = True
				album.imposed_track_order = []
				for i in range(len(tracks)):
					index = i
					tracks_match = aux.edit_comp(tracks[i], discogs_album.tracklist[i].title)
					if not tracks_match:
						for j in range(len(discogs_album.tracklist)):
							tracks_match = aux.edit_comp(tracks[i], discogs_album.tracklist[j].title)
							if tracks_match:
								index = j
								break
					if not tracks_match:
						return False
					album.imposed_track_order.append(index)
				return True
		return False

	# get searches Discogs for the album and returns the release id

	def get(self, album):
		search_lib = []
		for artist in tag.parse_tag("artist", album.loaded_tracks):
			for title in tag.parse_tag("album", album.loaded_tracks):
				search_lib.append(artist + ' ' + title)
		search_lib.append(os.path.basename(album.path))
		for term in search_lib:
			results = self.d.search(term, type='release')
			i = 0
			while i < 10:
				for result in results:
					if self.similar_enough(album, result):
						return result.id
					i += 10
		return

	# TAG_DICT translates mutagen tags to Discogs data

	def TAG_DICT_STATIC(self, id_):
		return {"album" : self.d.release(id_).title,
				"albumartist" : [artist.name for artist in self.d.release(id_).artists],
				"date" : str(self.d.release(id_).year),
				"genre" : [genre for genre in self.d.release(id_).genres],
				"encodedby" : 'MetaCleanup'}

	def TAG_DICT_DYNAMIC(self, id_, no):
		while True:
			try:
				if self.d.release(id_).tracklist[no].artists != []:
					artist_tag = [artist.name for artist in self.d.release(id_).tracklist[no].artists]
				else:
					artist_tag = [artist.name for artist in self.d.release(id_).artists]
				return {"artist" : artist_tag,
						"title" : self.d.release(id_).tracklist[no].title,
						"tracknumber" : aux.format_track_number(no + 1)}
			except discogs_client.exceptions.HTTPError:
				print('Discogs needs cool-down time. Be patient!')
				time.sleep(2.0)


