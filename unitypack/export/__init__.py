import json, os
from .shared import listFiles, getAvailableFileName, NameExtension

class BundleExporter():
	def __init__(self, bundle, destFolder, adjust_path=True, no_sprite_texture=True, auto_start=True):
		'''
		bundle = unitypack.load(),
		destfolder = target dir,
		adjust_path = create no subfolder if only one object to extract
		no_sprite_texture = removes textures which holds sprites
		auto_start = starts export on creation
		'''

		self.assets = bundle.assets
		self.destFolder = destFolder

		if adjust_path:
			obj_types=[]
			for asset in self.assets:
				try:
					for _id,obj in asset.objects.items():
						if getattr(AssetExporter, obj.type, False):
							obj_types.append(obj.type)
				except:
					pass
					#print(str(asset))

			if obj_types in [['Sprite','Texture2D'],['Texture2D','Sprite']]:
				destFolder = os.path.dirname(destFolder)

		if auto_start:
			self.export()


	def export(self):
		for asset in self.assets:
			AssetExporter(asset,self.destFolder)

class AssetExporter():
	def __init__(self,asset, destFolder, auto_start=True, no_sprite_texture=True):
		'''
		Exports the data of all objects within the asset.
		destFolder ~ outdir
		auto_start ~ starts self.extract()
		no_sprite_texture = removes textures which holds sprites
		'''
		self.obj = asset.objects
		self._cache={}
		self.destFolder = destFolder
		self.no_sprite_texture = no_sprite_texture
		os.makedirs(destFolder,exist_ok=True)

		if auto_start:
			self.export()


	def export(self):
		self.texture2ds=[]
		self.used_texture2ds = []
		for _id,obj in self.obj.items():
			if self.no_sprite_texture and obj.type == 'Texture2D':
				self.texture2ds.append(obj.path_id)
				continue

			method = getattr(self, obj.type, False)
			if method:
				try:
					method(obj)
				except Exception as e:
					print('Error during the extraction of %s [%s]\n%s'%(self.destFolder,str(method),e))
			else:
				# unimplemanted type ~ save as raw data
				self.RawFile(obj)

		if self.no_sprite_texture:
			for _id in set(self.texture2ds)-set(self.used_texture2ds):
				self.Texture2D(self.obj[_id])
		

	####	EXTRACTION FUNCTIONS	#######################################################
	def AudioClip(self,obj):
		from .audio import ProcessAudioClip, StreamingAssetsConvertion
		ProcessAudioClip(obj.read(),self.destFolder)


	def BundleData(self,obj):
		data = obj.read()
		outputFile = getAvailableFileName(self.destFolder,data['m_Name'],"json")
		with open(outputFile, 'wb') as fh:
			fh.write(json.dumps(data['m_bundleList'], indent='\t', ensure_ascii=False).encode('utf8'))


	def BytesScriptableObjectMD5(self,obj):
		data = obj.read()
		outputFile = getAvailableFileName(self.destFolder,data['m_Name'],"asset")
		with open(outputFile, 'wb') as fh:
			fh.write(data['m_bytes'])


	def Font(self,obj):	#has to be fixed, invalid atm
		data = obj.read()
		byts = getattr(data,'data',getattr(data,'bytes',False))
		if not byts:
			return
		if type(byts)!=bytes:
			byts=byts.encode('utf8')
		extension = '.ttf'
		if list(byts[0:4]) == [79,84,84.79]:
			extension = '.otf'
		outputFile = getAvailableFileName(self.destFolder, data.name, extension)
		with open(outputFile, 'wb') as fh:
			fh.write(byts)


	def Mesh(self,obj):
		from .mesh import ProcessMesh
		ProcessMesh(obj.read(),self.destFolder)


	def MovieTexture(self,obj):
		data = obj.read()
		outputFile = getAvailableFileName(self.destFolder, data.name, "ogv")
		with open(outputFile, 'wb') as fh:
			fh.write(data.movie_data)


	def Sprite(self,obj):
		data =obj.read()
		outputFile = getAvailableFileName(self.destFolder, data.name, "png")
		self.used_texture2ds.append(data.rd['texture'])
		texture = self.getTexture(data.rd['texture'].object)
		data.image(texture).save(outputFile)


	def TextAsset(self, obj, extension='txt'):
		data = obj.read()
		outputFile = getAvailableFileName(self.destFolder, *NameExtension(data.name,extension))
		bts = getattr(data,'script',getattr(data,'bytes',False))
		with open(outputFile, 'wb') as fh:
			fh.write(bts if type(bts)==bytes else bts.encode('utf8'))


	def Texture2D(self,obj):
		data = obj.read()
		outputFile = getAvailableFileName(self.destFolder, data.name, "png")
		self.getTexture(obj,data).save(outputFile)


	def RawFile(self,obj):
		data=obj.read()
		name = getattr(data,'name',False)
		if not name:
			name=obj.type
		bts = getattr(data,'bytes',getattr(data,'data',False))

		if bts:
			#print(self.destFolder, name)
			outputfile = getAvailableFileName(self.destFolder,*NameExtension(name,'.dat'))
			if type(bts)==str:
				bts=bts.encode('utf8')
			open(outputfile,'wb').write(bts)

	####	SUPPORT FUNCTIONS	######################################
	def getTexture(self,obj,data=None):
		'''
		Extracts and exports the images of an object.
		Caching is used to reduce the total extraction time of sprites.
		'''
		_id = obj.path_id
		if _id in self._cache:
			return self._cache[_id]
		else:
			if not data:
				img = obj.read().image()
			else:
				img = data.image()
			self._cache[_id] = img
			return img