#!/usr/bin/env python
import os
import unitypack
from .export import listFiles, BundleExporter, AssetExporter
from .asset import Asset
from shutil import copy2
from .SimpleMultiThread import MultiThreadHandler

class UnityFolder:
	FORMAT_ARGS = {
		"audio": ["AudioClip"],
		"fonts": ["Font"],
		"images": ["Texture2D","Sprite"],
		"models": ["Mesh"],
		"shaders": ["Shader"],
		"text": ["TextAsset"],
		"video": ["MovieTexture"],
	}

	def __init__(self, indir, outdir, debug = False):
		self.indir = indir
		self.outdir = outdir
		self.debug = debug
		self.files={}


	def list_files(self):
		self.files={}
		self.types={'bundle':[],'asset':[],'raw':[]}
		for fp in listFiles(self.indir):
			typ = check_file_type(os.path.join(self.indir,fp))
			self.types[typ].append(fp)
			self.files[fp]={'outpath':fp,'type':typ}
			

	def export(self,typ=None,outdir_convention=None, threads=8):
		'''
		typ ~ only bundle/asset/raw
		outdir_convetion ~ outdir renaming function
		threads ~ number of threads used, 0 - none for debugging
		'''
		if threads==0:
			self.export_debug(typ=typ,outdir_convention=outdir_convention)

		MTH = MultiThreadHandler()
		for fp in listFiles(self.indir):
			fin = os.path.join(self.indir, fp)
			if outdir_convention:
				fout =  os.path.join(self.outdir, outdir_convention(fp))
			else:
				fout = os.path.join(self.outdir, fp)
			MTH.queue.put((ExportFile,{'fp':fin,'fout':fout}))
		MTH.RunThreads()


	def export_debug(self,typ=None,outdir_convention=None):
		'''
		typ ~ only bundle/asset/raw
		outdir_convetion ~ outdir renaming function
		threads ~ number of threads used, 0 - none for debugging
		'''
		if self.files:
			if typ:
				files = {fp:self.files[fp] for fp in self.types[typ]}
			else:
				files = self.files

			for fp,f in files.items():
				fin = os.path.join(self.indir, fp)
				fout = os.path.join(self.outdir, f['outpath'])
				ExportFile(fin,fout,f['type'])
		else:
			for fp in listFiles(self.indir):
				fin = os.path.join(self.indir, fp)
				if outdir_convention:
					fout =  os.path.join(self.outdir, outdir_convention(fp))
				else:
					fout = os.path.join(self.outdir, fp)
				ExportFile(fin,fout)


def ExportFile(fp='',fout='',typ=False):
	'''
	fp = filepath or filestream,
	fout = dest file path,
	typ (optional) = bundle/asset/False~copy
	'''
	if type(fp)==str:
		f=open(fp,'rb')
	else:
		f=fp

	if not typ:
		typ=check_file_type(f)

	if typ == 'bundle':
		b = unitypack.load(f)
		BundleExporter(b,destFolder=fout)
	elif typ == 'asset':
		a = Asset.from_file(a)
		AssetExporter(a,destFolder=fout)
	else:
		os.makedirs(os.path.dirname(fout),exist_ok=True)
		if type(fp) == str:
			copy2(fp,fout)
		else:
			open(fout,'wb').write(fp.read())
			fp.seek(0)
	if type(fp)==str:
		f.close()


def check_file_type(fp):
	if type(fp)==str:
		f=open(fp,'rb')
	else:
		f=fp

	#	file type check
	firstChars = bytearray(f.read(12))
	f.seek(0)

	def IfFirstChars(text):
		return firstChars[:len(text)] == bytearray(text.encode())

	if IfFirstChars("UnityFS") or IfFirstChars("UnityWeb") or IfFirstChars("UnityRaw") or IfFirstChars("UnityArchive"):
		ret = 'bundle'
	else:
		try:
			asset = Asset.from_file(f)
			asset.objects
			ret = 'asset'
		except:
			ret = 'raw'

	if type(fp)==str:
		f.close()
	return ret