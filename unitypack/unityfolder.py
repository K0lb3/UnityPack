#!/usr/bin/env python
import os
import unitypack
from unitypack.export import listFiles, BundleExporter, AssetExporter
from unitypack.asset import Asset
from shutil import copy2

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
			

	def export(self,typ=None,outdir_convention=None):
		if self.files:
			if typ:
				files = {fp:self.files[fp] for fp in self.types[typ]}
			else:
				files = self.files

			for fp,f in files.items():
				fin = os.path.join(self.indir, fp)
				fout = os.path.join(self.outdir, f['outpath'])
				if f['type'] == 'bundle':
					f = open(fin,'rb')
					b = unitypack.load(f)
					BundleExporter(b,destFolder=self.outdir)
					f.close()
				elif f['type'] == 'asset':
					f = open(fin,'rb')
					a = Asset.from_file(a)
					AssetExporter(a,destFolder=self.outdir)
					f.close()
				else:
					os.makedirs(os.path.dirname(fout),exist_ok=True)
					copy2(fin,fout)
		else:
			for fp in listFiles(self.indir):
				fin = os.path.join(self.indir, fp)
				if outdir_convention:
					fout =  os.path.join(self.outdir, outdir_convention(fp))
				else:
					fout = os.path.join(self.outdir, fp)
				typ = check_file_type(fin)
				if typ == 'bundle':
					f = open(fin,'rb')
					b = unitypack.load(f)
					BundleExporter(b,destFolder=fout)
					f.close()
				elif typ == 'asset':
					f = open(fin,'rb')
					a = Asset.from_file(a)
					AssetExporter(a,destFolder=fout)
					f.close()
				else:
					os.makedirs(os.path.dirname(fout),exist_ok=True)
					copy2(fin,fout)



def check_file_type(fp):
	f=open(fp,'rb')

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
	f.close()
	return ret