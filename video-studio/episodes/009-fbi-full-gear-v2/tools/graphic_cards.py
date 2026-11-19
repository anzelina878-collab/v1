"""Original light-studio information cards. One entrance, all items visible by .65s."""
from PIL import Image,ImageDraw
import math
NAVY='#293842';GOLD='#B99B52';GRAY='#AAB2B5'
def icon(d,cx,cy,label):
 c=NAVY;w=6
 def line(p):d.line(p,fill=c,width=w,joint='curve')
 def box(p,r=8):d.rounded_rectangle(p,radius=r,outline=c,width=w)
 if label=='ПОВІТРЯ':
  line([(cx-85,cy+5),(cx+85,cy+5)]);line([(cx,cy-65),(cx,cy+75)]);line([(cx-55,cy+50),(cx+55,cy+50)]);d.ellipse((cx-29,cy-23,cx+29,cy+32),outline=c,width=w);line([(cx-70,cy-60),(cx+70,cy-60)])
 elif label=='ВОДА':
  d.polygon([(cx-85,cy+8),(cx+85,cy+8),(cx+55,cy+57),(cx-55,cy+57)],outline=c,width=w);box((cx-43,cy-45,cx+43,cy+8),5);line([(cx,cy-45),(cx,cy-80)]);line([(cx-75,cy+77),(cx-38,cy+65),(cx,cy+77),(cx+38,cy+65),(cx+75,cy+77)])
 elif label=='РОБОТ':
  box((cx-77,cy+25,cx+77,cy+68),18);box((cx-45,cy-6,cx+31,cy+25),5);line([(cx+10,cy-6),(cx+30,cy-50),(cx+70,cy-72),(cx+84,cy-56)]);d.ellipse((cx-30,cy-58,cx+8,cy-20),outline=c,width=w)
 elif any(k in label for k in ['ДНК','CODIS','ЗРАЗОК']):
  for i in range(9):
   y=cy-75+i*18;x=math.sin(i*.65)*42;line([(cx+x,y),(cx-x,y)])
  for j in [-1,1]:line([(cx+j*math.sin(i*.12)*42,cy-75+i*18/.65*.12) for i in range(44)])
 elif any(k in label for k in ['БРОН','ЗАХИСТ','БЕЗПЕК','КОНТРОЛЬ','ПРАВОВ']):
  p=[(cx-64,cy-66),(cx,cy-86),(cx+64,cy-66),(cx+58,cy+24),(cx,cy+81),(cx-58,cy+24),(cx-64,cy-66)];line(p);line([(cx-30,cy),(cx-6,cy+25),(cx+35,cy-27)])
 elif any(k in label for k in ['ЗВ’ЯЗ','ПЕРЕДАЧ','НАПРЯМОК']):
  box((cx-41,cy-42,cx+41,cy+77));line([(cx+22,cy-42),(cx+22,cy-94)]);box((cx-26,cy-24,cx+26,cy+2),2)
  for j in range(3):line([(cx-24,cy+25+j*13),(cx+24,cy+25+j*13)])
 elif any(k in label for k in ['ФОТО','ФІКСАЦ','СПОСТЕРЕЖ']):
  box((cx-82,cy-42,cx+82,cy+65));box((cx-45,cy-63,cx+20,cy-42),3);d.ellipse((cx-38,cy-30,cx+38,cy+46),outline=c,width=w);d.ellipse((cx-23,cy-15,cx+23,cy+31),outline=c,width=3)
 elif any(k in label for k in ['ПІСТОЛЕТ','ЗБРО','ОЗБРО']):
  d.polygon([(cx-80,cy-40),(cx+69,cy-40),(cx+69,cy-8),(cx+5,cy-8),(cx+24,cy+70),(cx-23,cy+70),(cx-42,cy-8),(cx-80,cy-8)],fill=c);box((cx-2,cy-8,cx+40,cy+24),6)
 elif any(k in label for k in ['ПЛИТ','М’ЯКА','МАСА']):
  d.polygon([(cx-40,cy-78),(cx+40,cy-78),(cx+65,cy-43),(cx+65,cy+75),(cx-65,cy+75),(cx-65,cy-43)],outline=c,width=w);line([(cx-40,cy-12),(cx+40,cy-12)]);line([(cx-40,cy+12),(cx+40,cy+12)])
 elif any(k in label for k in ['ДОКУМ','ПОСВІД','ВИСНОВОК','ТОЧНІ','ПЕРЕВІР']):
  box((cx-60,cy-80,cx+60,cy+80),5)
  for j in range(4):line([(cx-33,cy-40+j*26),(cx+32,cy-40+j*26)])
 elif any(k in label for k in ['ПАКУВ','НАКОПИЧ','НОСІ','МАТЕРІАЛ','КОПІЯ']):
  box((cx-63,cy-75,cx+63,cy+75));line([(cx-63,cy-27),(cx+63,cy-27)]);box((cx-24,cy-57,cx+24,cy-37),3);d.ellipse((cx+27,cy+37,cx+42,cy+52),fill=GOLD)
 elif any(k in label for k in ['ТЕЛЕФОН','ШИФРУВ','ДОСТУП']):
  box((cx-46,cy-85,cx+46,cy+85),13);line([(cx-20,cy-65),(cx+20,cy-65)]);d.ellipse((cx-7,cy+59,cx+7,cy+73),outline=c,width=3)
 elif any(k in label for k in ['КОМП’ЮТЕР','ЕКСПЕРТИЗ','ДОСЛІДЖ','МЕТОД']):
  box((cx-84,cy-66,cx+84,cy+39));line([(cx,cy+40),(cx,cy+75)]);line([(cx-50,cy+76),(cx+50,cy+76)])
 elif any(k in label for k in ['КВАНТІКО','МАЯМІ','ГАНТСВІЛЛ','СЕРЕДОВИЩЕ']):
  d.ellipse((cx-56,cy-84,cx+56,cy+28),outline=c,width=w);line([(cx-50,cy),(cx,cy+85),(cx+50,cy)]);d.ellipse((cx-18,cy-48,cx+18,cy-12),outline=c,width=w)
 elif any(k in label for k in ['ВОДА','ПОВІТРЯ','СУХОДІЛ','ТРАНСПОРТ','ЕВАКУАЦ']):
  box((cx-85,cy-28,cx+85,cy+37));line([(cx-57,cy-28),(cx-32,cy-65),(cx+39,cy-65),(cx+65,cy-28)]);
  for x in [-50,50]:d.ellipse((cx+x-19,cy+22,cx+x+19,cy+60),fill=c)
 else:
  d.ellipse((cx-26,cy-80,cx+26,cy-28),outline=c,width=w);d.arc((cx-70,cy-12,cx+70,cy+120),180,360,fill=c,width=w);line([(cx-70,cy+53),(cx+70,cy+53)])
def frame(p,s,t):
 im=Image.new('RGB',(1920,1080),p.c['background']);d=ImageDraw.Draw(im)
 p.text(im,s['title'],(90,105,1740,180),72,bold=True,min_size=38);d.rectangle((90,309,240,314),fill=GOLD)
 nodes=s['nodes'];n=len(nodes);gap=30;cw=(1740-gap*(n-1))/n;y=405
 group=Image.new('RGBA',im.size);gd=ImageDraw.Draw(group)
 for i,label in enumerate(nodes):
  x=90+i*(cw+gap);gd.rounded_rectangle((x,y,x+cw,y+435),radius=15,fill='white',outline='#DBDFDC',width=2);gd.rectangle((x+30,y+30,x+92,y+36),fill=GOLD)
  p.text(group,f'{i+1:02}',(x+cw-98,y+19,65,43),24,'muted',align='right');icon(gd,x+cw/2,y+166,label)
  p.text(group,label,(x+28,y+292,cw-56,115),38,bold=True,align='center',min_size=23)
 progress=min(1,max(0,t/.65));e=1-(1-progress)**3
 if e<1:
  group.putalpha(group.getchannel('A').point(lambda v:round(v*e)))
 im.paste(group,(0,round((1-e)*32)),group);p.text(im,'АРСЕНАЛ 360°',(90,1000,1000,36),21,'muted')
 return im
