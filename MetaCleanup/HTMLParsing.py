"""
URLs used for cross-referencing metadata, as well as functions that use the
request_html library
"""
import requests_html
import json

import Auxiliary as aux

# urls used

discogs = 'https://www.discogs.com'
discogs_artist = '/search/?type=artist&q='
discogs_release = '/search/?type=release&q='
discogs_master = '/search/?type=master&q='

# similar_enough aims to tell which album out of the search results is the one to obtain tagging 
# data from

def similar_enough(album_dict, url):
	session = requests_html.HTMLSession()
	r = session.get(url)
	master = r.html.find('#master_schema', first = True)
	master_text = master.text
	try:
		master_dict = json.JSONDecoder().decode(master_text)
		artist = master_dict['byArtist']['name'].lower()
		if artist[-1] == ")" and artist[-3] == "(":
			artist = artist[:-4]
		if artist[-1] == ")" and artist[-4] == "(":
			artist = artist[:-5]
		album = master_dict['name'].lower()
		result = aux.edit_distance(album_dict["Artist"][0].lower(), artist) <= aux.edit_err(artist) and aux.edit_distance(album_dict["Title"][0].lower(), album) <= aux.edit_err(album)
		return result
	except AttributeError:
		return False
	except KeyError:
		return False
	except json.decoder.JSONDecodeError as e:
		return False

# format_from_url creates a dictionary using the JSON object of the album's master release page

def format_from_url(url):
	session = requests_html.HTMLSession()
	r = session.get(url)
	try:
		master = r.html.find('#master_schema', first = True)
		master_dict = json.JSONDecoder().decode(master.text)
		album_art = master_dict['image']
		artist = master_dict['byArtist']['name']
		if artist[-1] == ")" and artist[-3] == "(":
			artist = artist[:-4]
		if artist[-1] == ")" and artist[-4] == "(":
			artist = artist[:-5]
		album = master_dict['name']
		tracks = {}
		i = 1
		for track in master_dict['tracks']:
			tracks[i] = track['name']
			i += 1
		year = str(master_dict['datePublished'])
		genre = master_dict['genre']
		return aux.album_to_dict([artist], [album], tracks, [year], genre, album_art)
	except AttributeError:
		return
	except KeyError:
		return
