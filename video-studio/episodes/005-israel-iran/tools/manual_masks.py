"""Faithful, reviewed photographic silhouette; no synthetic equipment geometry."""
from pathlib import Path
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[1]
SHAHED_136=[(158,126),(166,119),(170,86),(179,85),(184,95),(187,116),(348,109),(351,96),(365,87),(356,58),(367,62),(377,87),(391,89),(403,96),(410,110),(581,114),(584,89),(595,87),(597,115),(609,122),(609,129),(593,141),(483,227),(440,257),(433,302),(426,379),(414,438),(403,463),(392,471),(381,470),(368,457),(358,438),(348,380),(338,269),(301,247),(239,204),(166,144),(159,132)]
def main():
 im=Image.open(BASE/'assets/photos/shahed136.jpg').convert('RGBA');assert im.size==(800,530)
 mask=Image.new('L',(im.width*4,im.height*4));ImageDraw.Draw(mask).polygon([(x*4,y*4) for x,y in SHAHED_136],fill=255);im.putalpha(mask.resize(im.size,Image.Resampling.LANCZOS));im.crop((145,48,625,484)).save(BASE/'assets/prepared/shahed136-manual.png')
if __name__=='__main__':main()
