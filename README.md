# Intro
A modified version of UnityPack with the goal of making the export and conversion of assets easier and more straightforward.

### Additions
* native ETC/ETC2 decompression added (by RichardGale)
* ATC decompression added (Windows only, via texgenpack)

* easier asset export via unitypack.unityfolder
1. AssetExporter (asset, dest) 
2. BundleExporter (bundle, dest)
3. UnityFolder (source, dest) - unpacks all assets from source to dest

* image and box (area in texture) added to Sprites

### Changes
* texture fixes (flip, channels of some formats reordered)
* sprite and texture image property became a function (to avoid unnessary image creation)

### Planned
* awb and acb converter (to wav and mp3)


# UnityPack
* [original unitypack](https://github.com/HearthSim/UnityPack)
