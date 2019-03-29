import fsb5
import subprocess
import os
import shutil
from .shared import LocalPath,tempPath,listFiles,getAvailableFileName
# from unitypack.utils import extract_audioclip_samples
####	PATHS
HCAtoWAVPath = os.path.join(LocalPath, *['external','vgmstream',"test.exe"])	#	hca to wav
ACBtoHCAPath = os.path.join(LocalPath, *['external','un-acb',"un-acb.exe"])	 #	stramingsasset audio to hca
LamePath = os.path.join(LocalPath, *['external','lame',"lame.exe"])	 #	.wav to .mp3

####	MAIN FUNCTIONS
def ProcessAudioClip(data,destFolder):
	# extract samples
	bindata=data.data
	index=0
	while bindata:
		fsb=fsb5.load(bindata)
		ext=fsb.get_sample_extension()
		bindata=bindata[fsb.raw_size:]
		for sampleName,sampleData in readSamplesFromFSB5(fsb):
			outputFile = getAvailableFileName(destFolder,data.name+"--"+sampleName,ext)
			with open(outputFile, 'wb') as fh:
				fh.write(sampleData)
		index+=1

###	AUDIO	-	STREAMINGASSETS	##################################################################################
def readSamplesFromFSB5(fsb):
	for sample in fsb.samples:
		try:
			yield sample.name,fsb.rebuild_sample(sample)
		except ValueError as e:
			print('FAILED to extract %r: %s'%(sample.name,e))


def extract_audioclip_samples(d) -> dict:
	"""
	Extract all the sample data from an AudioClip and
	convert it from FSB5 if needed.
	"""
	ret = {}

	if not d.data:
		# eg. StreamedResource not available
		return {}

	try:
		from fsb5 import FSB5
	except ImportError as e:
		raise RuntimeError("python-fsb5 is required to extract AudioClip")

	af = FSB5(d.data)
	for i, sample in enumerate(af.samples):
		if i > 0:
			filename = "%s-%i.%s" % (d.name, i, af.get_sample_extension())
		else:
			filename = "%s.%s" % (d.name, af.get_sample_extension())
		try:
			sample = af.rebuild_sample(sample)
		except ValueError as e:
			print("WARNING: Could not extract %r (%s)" % (d, e))
			continue
		ret[filename] = sample

	return ret


def StreamingAssetsConvertion(origFolder,destFolder=False):
	if destFolder==False:
		destFolder=origFolder

	os.makedirs(tempPath,exist_ok=True)
	for sasset in listFiles(origFolder,False):
		if sasset[-4:] !='.acb':
			continue
		print(sasset)
		try:
			#AWB to HCA
			ACBtoHCA(os.path.join(origFolder,sasset),tempPath)
			#HCA to WAV
			HCAPath =os.path.join(tempPath,sasset+'_')		#	extracted HCA file path
			FinDest	= os.path.join(destFolder,sasset[:-4])	#	final output
			os.makedirs(FinDest,exist_ok=True)
			for hca in os.listdir(HCAPath):
				HCAtoWAV(os.path.join(HCAPath,hca),os.path.join(HCAPath,hca[:-4]+'.wav'))
				WAVtoMP3(os.path.join(HCAPath,hca[:-4]+'.wav'),os.path.join(FinDest,hca[:-4]+'.mp3'))
					
			#Clean-Up
			shutil.rmtree(HCAPath, ignore_errors=False, onerror=None)
		except:
			pass

	#Clean-Up2
	if origFolder==destFolder:
		for sasset in listFiles(destFolder):
			if sasset[-4:] =='.acb' or sasset[-4:] == '.awb':
				os.remove(os.path.join(destFolder,sasset))
	#shutil.rmtree(tempPath, ignore_errors=False, onerror=None)

def ACBtoHCA(inFile,outFolder):
	process = subprocess.Popen([
		ACBtoHCAPath,
		inFile
		], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, cwd=outFolder)
	output, err = process.communicate()
	process.terminate()

def HCAtoWAV(inFile,outFile):
	process = subprocess.Popen([
		HCAtoWAVPath,
		"-o",outFile,
		inFile
		], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
	output, err = process.communicate()
	process.terminate()

def WAVtoMP3(inFile,outFile):
	process = subprocess.Popen([
		LamePath, 
		"--preset","176",#176 kbps
		inFile,
		outFile
		], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
	output, err = process.communicate()
	process.terminate()