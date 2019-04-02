# Intro
A modified version of UnityPack with the goal of making the export and convertion of assets easier and more straightforward.

### Additions
* native ETC/ETC2 decompression added (by RichardGale)
* ATC decompression added (Windows only, via texgenpack)

* easier asset export via unitypack.unityfolder
1. AssetExporter (asset, dest) 
2. BundleExporter (bundle, dest)
3. UnityFolder (source, dest) - unpacks all assets from source to dest

* image and box (area in texture) added to Sprites

### Changes
* texture fixes (flip, channels of some formarts reordered)
* sprite and texture image property became a function (to avoid unnessary image creation)

### Planned
* awb and acb converter (to wav and mp3)


## Dependencies
* [python-lz4](https://github.com/python-lz4/python-lz4) (For UnityFS-compressed files)
* [modified decrunch](https://github.com/K0lb3/decrunch) (for various ETC and ETC2 support)

# UnityPack
* [original unitypack](https://github.com/HearthSim/UnityPack)
