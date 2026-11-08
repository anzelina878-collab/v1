"""Original national-flag drawings used by the episode renderer."""
from pathlib import Path
from PIL import Image,ImageDraw
import math
ROOT=Path(__file__).resolve().parents[1]/'assets/flags';ROOT.mkdir(parents=True,exist_ok=True)
im=Image.new('RGBA',(450,300),'white');d=ImageDraw.Draw(im);d.rectangle((0,0,149,299),fill='#002395');d.rectangle((300,0,449,299),fill='#ED2939');im.save(ROOT/'fr-flag.png')
im=Image.new('RGBA',(600,300),'#012169');d=ImageDraw.Draw(im);d.line((0,0,600,300),fill='white',width=60);d.line((0,300,600,0),fill='white',width=60)
d.polygon([(0,0),(0,20),(280,160),(300,150)],fill='#C8102E');d.polygon([(300,150),(320,140),(600,280),(600,300)],fill='#C8102E');d.polygon([(0,300),(40,300),(300,170),(300,150)],fill='#C8102E');d.polygon([(300,150),(300,130),(560,0),(600,0)],fill='#C8102E');d.rectangle((0,100,600,200),fill='white');d.rectangle((250,0,350,300),fill='white');d.rectangle((0,120,600,180),fill='#C8102E');d.rectangle((270,0,330,300),fill='#C8102E');im.save(ROOT/'gb-flag.png')
