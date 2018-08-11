import glob

def getFilenamesInFolder(folderName):
	mylist = [f for f in glob.glob(folderName+"*.txt")]
	return mylist

def readFile(path):
	f = open(path, 'r')
	content = f.read()
	f.close()
	return content