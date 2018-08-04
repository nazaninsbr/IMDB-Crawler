import requests
from bs4 import BeautifulSoup 
import matplotlib.pyplot as plt
import copy
import networkx as nx

MAIN_URL = 'https://www.imdb.com/title/'
FILENAME = 'movies.txt'
MAX_MOVIE_COUNT = 100
MAX_UNAVAILABLE_COUNT = 20

class Movie:
	def __init__(self):
		self.title = ''
		self.director = ''
		self.actors = []

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

	def getTitle(self):
		return self.title

	def getActors(self):
		return self.actors

	def setActors(self, actors):
		self.actors = copy.deepcopy(actors)


class ActorsGraph:
	def __init__(self):
		self.G = nx.Graph()

	def addEdge(self, actors):
		if len(actors)<=1:
			for actor in actors:
				if actor not in self.G:
					self.G.add_node(actor)
			return
		for actor1 in actors:
			for actor2 in actors:
				if not(actor1==actor2):
					if actor1 not in self.G:
						self.G.add_node(actor1)
					if actor2 not in self.G:
						self.G.add_node(actor2)
					if self.nodes_connected(actor1, actor2) == True:
						self.G[actor1][actor2]["weight"] += 1;
					else:	
						self.G.add_edge(actor1, actor2, weight=1)

	def nodes_connected(self, u, v):
		return u in self.G.neighbors(v)

	def printGraph(self):
		elarge=[(u,v) for (u,v,d) in self.G.edges(data=True) if d['weight'] >2]
		esmall=[(u,v) for (u,v,d) in self.G.edges(data=True) if d['weight'] <=2]

		pos=nx.spring_layout(self.G) # positions for all nodes

		# nodes
		nx.draw_networkx_nodes(self.G,pos,node_size=400)

		# edges
		nx.draw_networkx_edges(self.G,pos,edgelist=elarge,
					width=3)
		nx.draw_networkx_edges(self.G,pos,edgelist=esmall,
					width=1,alpha=0.5,edge_color='b',style='dashed')
		labels = nx.get_edge_attributes(self.G,'weight')
		edge_labels=dict([((u,v,),d['weight']) for u,v,d in self.G.edges(data=True)])
		nx.draw_networkx_edge_labels(self.G,pos,edge_labels=edge_labels)
		# labels
		nx.draw_networkx_labels(self.G,pos,font_size=8,font_family='sans-serif')

		plt.axis('off')
		plt.savefig("actors_graph.pdf") # save as pdf
		plt.show() # display




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

def getMovieActors(content):
	soup = BeautifulSoup(content, 'html.parser')
	AllTds = soup.find_all('td')
	castTds = [x for x in AllTds if 'itemprop="actor"' in str(x)]
	castSpan = [x.find_all('span') for x in castTds]
	castNames = []
	for item in castSpan:
		for nestedItem in item:
			castNames.append(nestedItem.text)
	return castNames


def crawlTheWebsite():
	movies = []
	content = 0
	count = 1
	actorG = ActorsGraph()
	countNotFound = 0
	while count<MAX_MOVIE_COUNT and countNotFound<MAX_UNAVAILABLE_COUNT:
		print("Crawling...")
		thisMovieUrl = changeMovieURL(count, 'tt')
		content = getPageContent(MAIN_URL+thisMovieUrl+'/')
		if not content==-1:
			countNotFound = 0
			title = getMovieName(content)
			director = getDirectorName(content)
			actors = getMovieActors(content)
			actorG.addEdge(actors)
			thisMovie = Movie()
			thisMovie.setAll(title, director)
			thisMovie.setActors(actors)
			movies.append(thisMovie)
			writeResultsToFile(movies[-1].getAllInfo())
		else:
			countNotFound += 1
		count += 1
	return movies, actorG


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
		if item=='':
			continue
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
		movies, actorG = crawlTheWebsite()
		actorG.printGraph()
	elif choice=='2':
		movies = readTheFile()
	numberOfMoviesByADirector(movies)
	


