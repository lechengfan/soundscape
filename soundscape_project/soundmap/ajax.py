from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

def findArtist(url):
	stop = len(url)
	for i in range(23, len(url)):
		if url[i] == '/':
			stop = i
			break
	return makePretty(url[23:stop])

def findTitle(url):
	start = 0
	for i in range(len(url) - 2, 0, -1):
		if url[i] == '/':
			start = i
			break
	return makePretty(url[start + 1:len(url) - 1])

def makePretty(url):
	url = url.replace('-', ' ')
	url = url.title()
	return url



@dajaxice_register
def getMarkerInfo(request):
	sampleUrl = "https://soundcloud.com/shumbody/folds-in-your-hands/"
	marker1 = {'artist':"2PAC", 'title':"Changes", 'lat':10, 'lng':20, 'url':"https://soundcloud.com/ghetto-records-2/2pac-changes"}
	marker2 = {'artist':"Borat", 'title':"Throw the Jew Down the Well", 'lat':48, 'lng':68, 'url':"https://soundcloud.com/user3843991/borat-throw-the-jew-down-the"}
	marker3 = {'artist':"Passion Pit", 'title':"It's Time", 'lat':42, 'lng':-71, 'url':"https://soundcloud.com/imaginedragons/imagine-dragons-its-time-2"}
	marker4 = {'artist':findArtist(sampleUrl), 'title':findTitle(sampleUrl), 'lat':37, 'lng':-120, 'url':sampleUrl}
	marker5 = {'artist':"Teriyaki Boyz", 'title':"Tokyo Drift", 'lat':35, 'lng':136, 'url':"https://soundcloud.com/jdm-music-2/teriyaki-boyz-tokyo-drift"}
	
	return simplejson.dumps({'m1':marker1,'m2':marker2, 'm3':marker3, 'm4':marker4, 'm5':marker5})