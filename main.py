import requests
from bs4 import BeautifulSoup 
import matplotlib.pyplot as plt

MAIN_URL = 'https://www.imdb.com/title/'
FILENAME = 'movies.txt'


class Movie:
	def __init__(self):
		self.title = ''
		self.director = ''

	def setTitle(self, title):
		self.title = title

	def setDirector(self, director):
		self.director = director

	def setAll(self, title, director):
		self.title = title
		self.director = director

	def getAllInfo(self):
		return self.title+'#'+self.director+'\n'

	def getDirector(self):
		return self.director


def getPageContent(url):
	r = requests.get(url)
	if not r.status_code==200:
		print("Problem accessing page data.")
		return -1
	return r.text

def getMovieName(content):
	soup = BeautifulSoup(content, 'html.parser')
	AllH1 = soup.find_all('h1')
	title = [x for x in AllH1 if 'itemprop="name"' in str(x)]
	title = str(title[0])
	title = title.split(">")
	title = title[1].split("<")[0]
	return title

def getDirectorName(content):
	soup = BeautifulSoup(content, 'html.parser')
	AllSpans = soup.find_all('span')
	director = [x for x in AllSpans if 'itemprop="director"' in str(x)]
	if len(director)==0:
		return ''
	director = str(director[0]).split(">")[-4]
	director = director.split("<")[0]
	return director

def changeMovieURL(count, startString):
	if count<10:
		return startString+'000000'+str(count)
	if count>=10 and count<100:
		return startString+'00000'+str(count)
	if count>=100 and count<1000:
		return startString+'0000'+str(count)
	if count>=1000 and count<10000:
		return startString+'000'+str(count)
	if count>=10000 and count<100000:
		return startString+'00'+str(count)
	if count>=100000 and count<1000000:
		return startString+'0'+str(count)
	if count>=1000000 and count<10000000:
		return startString+str(count)


def writeResultsToFile(item):
	thefile = open(FILENAME, 'a')
	thefile.write(item)
	thefile.close()

def crawlTheWebsite():
	movies = []
	content = 0
	count = 1

	while count<1000:
		print("Crawling...")
		thisMovieUrl = changeMovieURL(count, 'tt')
		content = getPageContent(MAIN_URL+thisMovieUrl+'/')
		if not content==-1:
			title = getMovieName(content)
			director = getDirectorName(content)
			thisMovie = Movie()
			thisMovie.setAll(title, director)
			movies.append(thisMovie)
			writeResultsToFile(movies[-1].getAllInfo())
		count += 1
	return movies


def readTheFile():
	movies = []
	thefile = open(FILENAME, 'r')
	content = thefile.readlines()
	thefile.close()
	for item in content:
		x = item.strip()
		x = x.split("#")
		y = Movie()
		y.setAll(x[0], x[-1])
		movies.append(y)
	return movies

def drawBarChart(numOfMovies):
	x = []
	y = []
	for item in numOfMovies.keys():
		x.append(item)
		y.append(numOfMovies[item])
	plt.bar(x, y)
	plt.savefig("number_of_movies_for_each_director.pdf")
	plt.show()

def numberOfMoviesByADirector(movies):
	numOfMovies = {}
	for movie in movies:
		director = movie.getDirector()
		if director in numOfMovies.keys():
			numOfMovies[director] += 1
		else:
			numOfMovies[director] = 1
	drawBarChart(numOfMovies)
		

if __name__ == '__main__':
	choice = input("1. crawl the website 2. use the file (1/2) ")
	if choice=='1':
		movies = crawlTheWebsite()
	elif choice=='2':
		movies = readTheFile()
	numberOfMoviesByADirector(movies)
	


