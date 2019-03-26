import logging
from PIL import Image, ImageOps
from .object import Object, field
from .ETC2ImagePlugin import ETC2Decoder
from .enums import TextureFormat

IMPLEMENTED_FORMATS = (
	TextureFormat.Alpha8,
	TextureFormat.ARGB4444,
	TextureFormat.RGBA4444,
	TextureFormat.RGB565,
	TextureFormat.RGB24,
	TextureFormat.RGBA32,
	TextureFormat.ARGB32,
	TextureFormat.DXT1,
	TextureFormat.DXT1Crunched,
	TextureFormat.DXT5,
	TextureFormat.DXT5Crunched,
	TextureFormat.BC7,
	TextureFormat.ETC_RGB4,
	TextureFormat.ETC2_RGB,
	TextureFormat.ETC2_RGBA1,
	TextureFormat.ETC2_RGBA8,
	TextureFormat.ETC_RGB4_3DS,
	TextureFormat.ETC_RGBA8_3DS,
	TextureFormat.ETC_RGB4Crunched,
	TextureFormat.ETC2_RGBA8Crunched,
)


class Sprite(Object):
	border = field("m_Border")
	extrude = field("m_Extrude")
	offset = field("m_Offset")
	rd = field("m_RD")
	rect = field("m_Rect")
	pixels_per_unit = field("m_PixelsToUnits")


class Material(Object):
	global_illumination_flags = field("m_LightmapFlags")
	render_queue = field("m_CustomRenderQueue")
	shader = field("m_Shader")
	shader_keywords = field("m_ShaderKeywords")

	@property
	def saved_properties(self):
		def _unpack_prop(value):
			for vk, vv in value:
				if isinstance(vk, str):  # Unity 5.6+
					yield vk, vv
				else:  # Unity <= 5.4
					yield vk["name"], vv
		return {k: dict(_unpack_prop(v)) for k, v in self._obj["m_SavedProperties"].items()}


class StreamingInfo(Object):
	offset = field("offset")
	size = field("size")
	path = field("path")

	def get_data(self):
		if not self.asset:
			logging.warning("No data available for StreamingInfo")
			return b""
		self.asset._buf.seek(self.asset._buf_ofs + self.offset)
		return self.asset._buf.read(self.size)


class Texture(Object):
	height = field("m_Height")
	width = field("m_Width")


class Texture2D(Texture):
	data = field("image data")
	lightmap_format = field("m_LightmapFormat")
	texture_settings = field("m_TextureSettings")
	color_space = field("m_ColorSpace")
	is_readable = field("m_IsReadable")
	read_allowed = field("m_ReadAllowed")
	format = field("m_TextureFormat", TextureFormat)
	texture_dimension = field("m_TextureDimension")
	mipmap = field("m_MipMap")
	complete_image_size = field("m_CompleteImageSize")
	stream_data = field("m_StreamData", default=False)

	def __repr__(self):
		return "<%s %s (%s %ix%i)>" % (
			self.__class__.__name__, self.name, self.format.name, self.width, self.height
		)

	@property
	def image_data(self):
		if self.stream_data and self.stream_data.asset:
			if not hasattr(self, "_data"):
				self._data = self.stream_data.get_data()
			return  self._data
		return self.data

	@property
	def image(self):
		from PIL import Image

		if self.format not in IMPLEMENTED_FORMATS:
			raise NotImplementedError("Unimplemented format %r" % (self.format))

		mode = "RGB" if self.format.pixel_format in ("RGB", "RGB16") else "RGBA"
		size = (self.width, self.height)
		data = self.image_data

		# Pillow wants bytes, not bytearrays
		from decrunch import File as CrunchFile
		if self.format in (TextureFormat.DXT1Crunched, TextureFormat.DXT5Crunched, TextureFormat.ETC_RGB4Crunched, TextureFormat.ETC2_RGBA8Crunched):
			data = CrunchFile(data).decode_level(0)
		data = bytes(data)

		if not data and size == (0, 0):
			return None

		# Image from bytes
		if self.format in (TextureFormat.DXT1, TextureFormat.DXT1Crunched):
			codec = "bcn"
			args = (1, )
		elif self.format in (TextureFormat.DXT5, TextureFormat.DXT5Crunched):
			codec = "bcn"
			args = (3, )
		elif self.format == TextureFormat.BC7:
			codec = "bcn"
			args = (7, )
		elif self.format in (TextureFormat.ETC_RGB4, TextureFormat.ETC2_RGB, TextureFormat.ETC2_RGBA1, TextureFormat.ETC2_RGBA8, TextureFormat.ETC2_RGBA8Crunched):
			codec = "etc2"
			args = (self.format, self.format.pixel_format, )
		else:
			codec = "raw"
			args = (self.format.pixel_format, )

		image = Image.frombytes(mode, size, data, codec, args)

		# Apply Fix	~	1. flip image, 2. secondary format fix
		channels = ImageOps.flip(image).split()
		if self.format in [
				TextureFormat.RGB565,	#  7
				TextureFormat.RGBA4444	# 13
				]:
			channels = tuple(reversed(channels))

		elif self.format in [
				TextureFormat.ARGB4444	# 2
				]:
			channels = (channels[2],channels[1],channels[0],channels[3])

		if len(channels) == 3:
			return Image.merge("RGB", channels)
		else:
			return Image.merge("RGBA", channels)