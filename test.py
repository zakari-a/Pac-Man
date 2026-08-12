from fontTools.ttLib import TTFont
font = TTFont("/home/zael-has/Desktop/Pac-Man/src/assets/PressStart2P-Regular.ttf")
cmap = font.getBestCmap()
supported_chars = [chr(code) for code in cmap.keys()]
print(supported_chars)
# print("".join(supported_chars))