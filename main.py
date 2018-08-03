import requests
from bs4 import BeautifulSoup 


MAIN_URL = 'https://www.imdb.com/title/'

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

if __name__ == '__main__':
	names = []
	content = 0
	count = 1

	while not content==-1:
		thisMovieUrl = changeMovieURL(count, 'tt')
		content = getPageContent(MAIN_URL+thisMovieUrl+'/')
		if not content==-1:
			names.append(getMovieName(content))
			print(names[-1])
		count += 1


