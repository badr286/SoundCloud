from requests import get
from bs4 import BeautifulSoup as soup

def get_client_id():
	script_url = soup( get('https://soundcloud.com/').text, 'html.parser'  ).findAll('script')[-2]['src']
	script = get(script_url).text
	client_id = script.split(',client_id:')[1].split('"')[1]
	return client_id

class soundcloud:

	def __init__(self, client_id):
		self.client_id = get_client_id()

	def get_song_id(self, share_link):
		src = soup( get(share_link).text, 'html.parser')
		return src.find('meta',{'property':'twitter:app:url:iphone'})['content'].split(':')[-1]


	def get_song_json(self, tracks_ids):
		tracks_ids = ','.join(tracks_ids.split(' '))
		return get(f'https://api-v2.soundcloud.com/tracks?ids={tracks_ids}&client_id={self.client_id}').json()

	def get_song_stream(self, tracks_ids):
		songs_stream = self.get_song_json(tracks_ids)
		streams = []

		for song_stream in songs_stream:
			url = song_stream['media']['transcodings'][0]['url']+f'?client_id={self.client_id}'
			stream = get(url).json()['url']
			streams.append(stream)

		return streams

	def get_song_src(self, track_id):
		stream = self.get_song_stream(track_id)[0]
		m3u8 = get(stream).text.split(',')

		for i in m3u8:
			if 'END' in i:
				last_stream = i.split('/')
				break

		for j in range( len(last_stream) ):
			if last_stream[j] == 'media':
				last_stream[j+1] = '0'
				last_stream = '/'.join(last_stream).split('\n')[1]
				break

		return last_stream
