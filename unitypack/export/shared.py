import os
import threading

####	CONSTANTS
LocalPath=os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
LOCK = threading.Lock()

####	FUNCTIONS
def NameExtension(name,extension=''):
	return name.rsplit('.',1) if '.' in name else (name,extension)
	
def listFiles(directory='',full_path=False):
	return [
		val for sublist in [
			[
				os.path.join(dirpath, filename) if full_path else os.path.join(dirpath, filename)[len(directory)+1:]
				for filename in filenames
			]
			for (dirpath, dirnames, filenames) in os.walk(directory)
			if '.git' not in dirpath
		]
		for val in sublist
	]

def getAvailableFileName(path, filename="NONAME", extension=""):
	#preventing duplicates for now
	global LOCK
	LOCK.acquire(True)
	if path == "":
		filename = "."
	if filename == "":
		filename = "NONAME"
	finalPath = os.path.join(path, "{}{}".format(filename, ".{}".format(extension) if (extension != "") else ""))
	LOCK.release()
	return finalPath

def getAvailableFileName_ori(path, filename="NONAME", extension=""):
	global LOCK
	LOCK.acquire(True)
	if path == "":
		filename = "."
	if filename == "":
		filename = "NONAME"
	index = 1
	while True:
		indexString = " ({})".format(index) if (index != 1) else ""
		extensionString = ".{}".format(extension) if (extension != "") else ""
		finalFilename = "{}{}{}".format(filename, indexString, extensionString)

		finalPath = os.path.join(path, finalFilename)

		if not os.path.isfile(finalPath):
			LOCK.release()
			return finalPath
		else:
			index = index + 1