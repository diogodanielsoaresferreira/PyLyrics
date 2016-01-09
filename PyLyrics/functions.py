import requests
from bs4 import BeautifulSoup, Comment, NavigableString
import sys, codecs, json

class Track(object):
	def __init__(self,trackName,album,artist):
		self.name = trackName
		self.album = album
		self.artist = artist
	def __repr__(self):
		return self.name.encode('utf-8')
	def link(self):
		return 'http://lyrics.wikia.com/{0}:{1}'.format(self.artist.replace(' ', '-'),self.name.replace(' ','-'))
	def getLyrics(self):
		return PyLyrics.getLyrics(self.artist,self.name)
class Artist(object):
	def __init__(self, name):
		self.name = name 
	def getAlbums(self):
		return PyLyrics.getAlbums(self.name)
	def __repr__(self):
		return self.name.encode('utf-8')
class Album(object):
	def __init__(self, name, link,singer):
		self.year = name.split(' ')[-1]
		self.name = name.replace(self.year,' ').rstrip()
		self.url = link 
		self.singer = singer
	def link(self):
		return self.url 
	def __repr__(self):
		if sys.version_info[0] == 2:
				return self.name.encode('utf-8','replace')
		return	self.name
	def artist(self):
		return self.singer
	def tracks(self):
		return PyLyrics.getTracks(self)

class PyLyrics:
	@staticmethod
	def getAlbums(singer):
		singer = singer.replace(' ', '_')
		s = BeautifulSoup(requests.get('http://lyrics.wikia.com/{0}'.format(singer)).text, "html.parser")
		spans = s.findAll('span',{'class':'mw-headline'})
		
		als = []
		
		for tag in spans:
			try:
				a = tag.findAll('a')[0]
				als.append(Album(a.text,'http://lyrics.wikia.com' + a['href'],singer))
			except:
				pass
		
		if als == []:
			raise ValueError("Unknown Artist Name given")
			return None
		return als

	@staticmethod
	def saveAlbums(singer):
		f = open(singer+" albums.txt", 'w')
		albums=PyLyrics.getAlbums(singer)
		f.write(singer+" albums\n\n")
		for line in albums:
			f.write(line.name+" "+line.year+"\n")
		f.close()


	@staticmethod
	def getTracks(album):

		soup = BeautifulSoup(requests.get(album.url).text, "html.parser")
		albumtracks=soup.ol.getText().split('\n')
		allt=[]

		for t in albumtracks:
			if t=="":
				break
			allt.append(Track(t[1:], album, album.singer))

		return allt

	@staticmethod
	def saveTracks(album):
		f = open(album.name+" tracks.txt", 'w')
		tracks=PyLyrics.getTracks(album)
		f.write(album.name+" tracks\n\n")
		for line in tracks:
			f.write(line.name+"\n")
		f.close()

	@staticmethod
	def getLyrics(singer, song):
		#Replace spaces with _
		singer = singer.replace(' ', '_')
		song = song.replace(' ', '_')
		r = requests.get('http://lyrics.wikia.com/{0}:{1}'.format(singer,song))
		s = BeautifulSoup(r.text, "html.parser")
		#Get main lyrics holder
		lyrics = s.find("div",{'class':'lyricbox'})
		if lyrics is None:
			raise ValueError("Song or Singer does not exist or the API does not have Lyrics")
			return None
		#Remove Scripts
		[s.extract() for s in lyrics('script')]

		#Remove Comments
		comments = lyrics.findAll(text=lambda text:isinstance(text, Comment))
		[comment.extract() for comment in comments]

		#Remove unecessary tags
		for tag in ['div','i','b','a']:
			for match in lyrics.findAll(tag):
				match.replaceWithChildren()
		#Get output as a string and remove non unicode characters and replace <br> with newlines
		output = str(lyrics).encode('utf-8', errors='replace')[22:-6:].decode("utf-8").replace('\n','').replace('<br/>','\n')
		try:
			return output
		except:
			return output.encode('utf-8')

	@staticmethod
	def saveLyrics(singer, song):
		f = open(singer+'-'+song+'.txt', 'w')
		lyrics=PyLyrics.getLyrics(singer,song)
		f.write(singer+"-"+song+"\n\n")
		for line in lyrics:
			f.write(line)
		f.close()

def main():
	albums = PyLyrics.getAlbums('OneRepublic')
	print (albums)
	tracks = PyLyrics.getTracks(albums[-1])
	print (tracks[7].getLyrics())


if __name__=='__main__':
	main()
