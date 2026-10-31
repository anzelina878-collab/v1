"""Draw generic demo icons and an abstract clip. No real equipment specifications."""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/"episodes/demo/assets"
ASSETS.mkdir(parents=True, exist_ok=True)
INK = "#28372C"
OLIVE = "#81916B"
LIGHT = "#A6B48F"
BLUE = "#426D88"
F = ImageFont.truetype(str(ROOT/"fonts/DejaVuSans-Bold.ttf"), 26)


def draw_icon(kind):
    im = Image.new("RGBA", (900, 700))
    d = ImageDraw.Draw(im)
    if kind in {"bag", "bag_light"}:
        fill = OLIVE if kind == "bag" else BLUE
        d.rounded_rectangle((245, 120, 655, 620), 90, fill=INK)
        for x in (260, 560):
            d.rounded_rectangle((x, 50, x+82, 600), 30, fill="#3E4E3B")
            d.rounded_rectangle((x+15, 68, x+65, 565), 20, fill="#647357")
        d.rounded_rectangle((290, 95, 610, 640), 65, fill=fill, outline=INK, width=8)
        d.rounded_rectangle((340, 50, 560, 160), 40, outline=INK, width=21)
        d.rounded_rectangle((310, 125, 590, 270), 40, fill=LIGHT if kind == "bag" else "#6C93AB", outline=INK, width=6)
        d.rounded_rectangle((330, 350, 570, 585), 25, fill=fill, outline=INK, width=7)
        for y in (395, 450, 505):
            d.line((355, y, 545, y), fill="#465740", width=9)
        for x in (340, 530):
            d.rounded_rectangle((x, 220, x+35, 343), 6, fill="#465740")
            d.rounded_rectangle((x-8, 285, x+43, 326), 8, fill=INK)
        d.line((365, 170, 535, 170), fill="#CBD1BA", width=6)
    elif kind == "helmet":
        d.pieslice((170, 70, 740, 650), 180, 360, fill=OLIVE, outline=INK, width=9)
        d.rounded_rectangle((165, 330, 745, 417), 30, fill=LIGHT, outline=INK, width=8)
        d.rounded_rectangle((260, 353, 430, 397), 8, fill=INK)
        d.rounded_rectangle((475, 353, 645, 397), 8, fill=INK)
        for x in (285, 340, 500, 555, 610):
            d.rectangle((x, 362, x+25, 386), fill="#6C7C5D")
        d.line((270, 412, 310, 570, 445, 610, 580, 570, 640, 412), fill=INK, width=22)
        d.rounded_rectangle((414, 580, 477, 631), 7, fill=OLIVE, outline=INK, width=6)
        d.rounded_rectangle((420, 160, 490, 285), 8, fill=INK)
        d.rectangle((435, 182, 475, 260), fill="#ABB79B")
    elif kind == "radio":
        d.line((580, 210, 600, 45), fill=INK, width=25)
        d.rounded_rectangle((285, 170, 620, 640), 40, fill=INK)
        d.rounded_rectangle((310, 195, 595, 615), 28, fill="#56634C")
        d.rounded_rectangle((338, 230, 568, 365), 14, fill="#22352F")
        d.rounded_rectangle((357, 249, 550, 345), 8, fill="#AFBA89")
        for j, height in enumerate((15, 30, 45, 60)):
            d.rectangle((380+j*35, 325-height, 400+j*35, 325), fill=INK)
        for y in (412, 460, 508):
            for x in (350, 430, 510):
                d.rounded_rectangle((x, y, x+45, y+28), 7, fill=INK)
        d.ellipse((360, 110, 425, 190), fill=INK)
        d.ellipse((455, 125, 515, 190), fill=INK)
    elif kind == "pouch":
        d.rounded_rectangle((240, 140, 660, 590), 55, fill=OLIVE, outline=INK, width=9)
        d.rounded_rectangle((270, 170, 630, 560), 40, outline="#45563F", width=8)
        d.line((292, 205, 607, 205, 607, 520), fill=INK, width=13)
        # Neutral blue medical marker, not a protected red cross emblem.
        d.rounded_rectangle((335, 285, 565, 465), 18, fill="#D3DACA")
        d.ellipse((403, 328, 497, 422), fill=BLUE)
        d.line((420, 376, 440, 395, 480, 352), fill="white", width=12)
        d.rounded_rectangle((635, 260, 697, 390), 9, fill=INK)
    elif kind == "bottle":
        d.rounded_rectangle((340, 70, 560, 185), 20, fill=INK)
        d.rounded_rectangle((275, 170, 625, 635), 100, fill=OLIVE, outline=INK, width=8)
        d.rounded_rectangle((305, 280, 595, 520), 40, fill=LIGHT)
        d.line((333, 227, 333, 563), fill="#BFCAAE", width=13)
        d.line((335, 111, 565, 111), fill="#52634C", width=12)
    elif kind == "battery":
        d.rounded_rectangle((280, 150, 620, 610), 35, fill=INK)
        d.rounded_rectangle((305, 175, 595, 585), 20, fill=BLUE)
        d.rounded_rectangle((370, 98, 530, 170), 10, fill=INK)
        for y in (240, 330, 420):
            d.rounded_rectangle((350, y, 550, y+65), 8, fill="#A9C1C7")
        d.ellipse((432, 525, 468, 561), fill="#D8BC69")
    im.save(ASSETS/f"{kind}.png")


def main():
    for name in ("bag", "bag_light", "helmet", "radio", "pouch", "bottle", "battery"):
        draw_icon(name)
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "960x540", "-r", "24", "-i", "pipe:0", "-an", "-c:v", "libx264", "-threads", "2", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(ASSETS/"abstract.mp4")], stdin=subprocess.PIPE)
    for frame in range(96):
        im = Image.new("RGB", (960, 540), "#233D35")
        d = ImageDraw.Draw(im)
        for x in range(0, 960, 60):
            d.line((x, 0, x, 540), fill="#365247")
        for y in range(0, 540, 60):
            d.line((0, y, 960, y), fill="#365247")
        for j in range(8):
            x = 100+j*108
            y = 250+math.sin(frame/18+j)*60
            d.ellipse((x-20, y-20, x+20, y+20), outline="#ADBFA1", width=3)
            if j:
                d.line((x-108, 250+math.sin(frame/18+j-1)*60, x, y), fill="#6D9277", width=2)
        scan = frame/95*960
        d.rectangle((scan, 0, scan+3, 540), fill="#D6AD43")
        d.text((60, 60), "DEMO / ABSTRACT MOTION", font=F, fill="#DDE8D8")
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit("FFmpeg failed")
    print(ASSETS)


if __name__ == "__main__":
    main()
