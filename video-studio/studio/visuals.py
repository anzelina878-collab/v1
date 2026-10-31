"""Pillow scene templates. Coordinates use a 1920x1080 design space."""
import math
from functools import lru_cache

from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H = 1920, 1080


def ease(value):
    x = max(0.0, min(1.0, value))
    return 1 - (1-x)**3


def star(draw, x, y, radius, fill, rotation=-math.pi/2):
    points = []
    for i in range(10):
        r = radius if i % 2 == 0 else radius*.382
        a = rotation+i*math.pi/5
        points.append((x+math.cos(a)*r, y+math.sin(a)*r))
    draw.polygon(points, fill=fill)


def country_flag(image, country, x, y, width=90, height=60):
    """Vector flags: independent of emoji support and platform fonts."""
    d = ImageDraw.Draw(image)
    if country == "US":
        d.rectangle((x, y, x+width, y+height), fill="white")
        for row in range(13):
            if row % 2 == 0:
                d.rectangle((x, y+row*height/13, x+width, y+(row+1)*height/13), fill="#B22234")
        cw, ch = width*.4, height*7/13
        d.rectangle((x, y, x+cw, y+ch), fill="#3C3B6E")
        for row in range(9):
            n = 6 if row % 2 == 0 else 5
            for column in range(n):
                sx = x+cw*(column+(0.5 if n == 6 else 1))/6
                star(d, sx, y+ch*(row+.5)/9, height*.025, "white")
    else:
        d.rectangle((x, y, x+width, y+height), fill="#DE2910")
        bx, by = x+width/6, y+height/4
        star(d, bx, by, height*.15, "#FFDE00")
        for sx, sy in ((10, 2), (12, 4), (12, 7), (10, 9)):
            px, py = x+width*sx/30, y+height*sy/20
            star(d, px, py, height*.05, "#FFDE00", math.atan2(by-py, bx-px))


@lru_cache(maxsize=96)
def font(path, size):
    return ImageFont.truetype(path, size)


@lru_cache(maxsize=64)
def asset(path):
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGBA")
        im.thumbnail((1800, 1500), Image.Resampling.LANCZOS)
        return im.copy()


class Painter:
    def __init__(self, project):
        self.p = project
        self.c = project["theme"]
        self.bg = self.background()

    def color(self, key):
        return self.c.get(key, key)

    def background(self):
        im = Image.new("RGB", (W, H), self.c["background"])
        if self.p.get("style") == "minimal":
            return im
        d = ImageDraw.Draw(im)
        for x in range(0, W, 80):
            d.line((x, 0, x, 760), fill=self.c["grid"], width=1)
        for y in range(0, 760, 80):
            d.line((0, y, W, y), fill=self.c["grid"], width=1)
        for x in range(-2400, 4400, 240):
            d.line((960+(x-960)*0.1, 660, x, H), fill=self.c["grid"], width=2)
        for y in [720, 760, 815, 890, 990]:
            d.line((0, y, W, y), fill=self.c["grid"], width=1)
        return im

    def text(self, im, value, box, size=42, color="ink", bold=False, align="left", min_size=18):
        value = str(value)
        if not value:
            return
        x, y, width, height = box
        d = ImageDraw.Draw(im)
        path = self.c["font_bold" if bold else "font"]
        # Wrap and shrink; fail visibly if the author exceeds the template capacity.
        for current in range(size, min_size-1, -2):
            f = font(path, current)
            lines = []
            for paragraph in value.split("\n"):
                line = ""
                for word in paragraph.split():
                    candidate = (line+" "+word).strip()
                    if d.textlength(candidate, font=f) <= width:
                        line = candidate
                    else:
                        if line:
                            lines.append(line)
                            line = ""
                        # Split long tokens rather than drawing outside the box.
                        for char in word:
                            if d.textlength(line+char, font=f) > width and line:
                                lines.append(line)
                                line = ""
                            line += char
                lines.append(line)
            line_h = int(current*1.35)
            if len(lines)*line_h <= height:
                break
        else:
            raise ValueError(f"Текст не вміщується у шаблон: {value[:90]!r}. Скоротіть його або розділіть сцену")
        for j, line in enumerate(lines):
            tx = x
            length = d.textlength(line, font=f)
            if align == "center":
                tx += (width-length)/2
            elif align == "right":
                tx += width-length
            d.text((tx, y+j*line_h), line, font=f, fill=self.color(color), stroke_width=0)

    def panel(self, im, box, color="panel", radius=20):
        ImageDraw.Draw(im).rounded_rectangle(box, radius=radius, fill=self.color(color))

    def tag(self, im, label, x, y, width=310, accent="blue"):
        self.panel(im, (x, y, x+width, y+54), "dark", radius=3)
        ImageDraw.Draw(im).rectangle((x, y, x+7, y+54), fill=self.color(accent))
        self.text(im, label, (x+22, y+12, width-38, 35), size=22, color="panel", bold=True)

    def picture(self, im, obj, box, t=2, accent="blue"):
        x, y, width, height = box
        progress = ease(t/0.65)
        if progress <= 0:
            return
        if obj.get("_image"):
            src = asset(obj["_image"])
            fitted = ImageOps.contain(src, (int(width), int(height)), Image.Resampling.LANCZOS)
            if progress < 1:
                fitted = fitted.copy()
                fitted.putalpha(fitted.getchannel("A").point(lambda a: int(a*progress)))
            px = int(x+(width-fitted.width)/2)
            py = int(y+(height-fitted.height)/2+24*(1-progress))
            # Small floor shadow remains separate from the image.
            shadow = Image.new("RGBA", (int(width), 80))
            sd = ImageDraw.Draw(shadow)
            sd.ellipse((width*.16, 20, width*.84, 52), fill=(20, 30, 20, int(28*progress)))
            shadow = shadow.filter(ImageFilter.GaussianBlur(14))
            im.paste(shadow, (int(x), int(y+height-32)), shadow)
            im.paste(fitted, (px, py), fitted)
        else:
            self.panel(im, (x+20, y+20, x+width-20, y+height-20))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((x+20, y+20, x+width-20, y+height-20), radius=20, outline=self.color(accent), width=2)
            self.text(im, "ДОДАЙТЕ\nЗОБРАЖЕННЯ", (x+60, y+height/2-60, width-120, 150), 38, "muted", align="center")

    def common(self, im, scene, index, time):
        if self.p.get("style") == "minimal":
            return
        d = ImageDraw.Draw(im)
        dark = scene["type"] == "footage"
        if dark:
            overlay = Image.new("RGBA", (W, H))
            od = ImageDraw.Draw(overlay)
            od.rectangle((0, 0, W, 118), fill=(15, 23, 20, 220))
            od.rectangle((0, 980, W, H), fill=(15, 23, 20, 220))
            im.paste(overlay, (0, 0), overlay)
        ink = "panel" if dark else "ink"
        muted = "panel" if dark else "muted"
        d.ellipse((80, 48, 96, 64), fill=self.color("yellow"))
        self.text(im, self.p.get("brand", "ПРЕДМЕТНО"), (113, 35, 700, 50), 29, ink, True)
        self.text(im, f"{index+1:02d} / {len(self.p['scenes']):02d}", (1610, 40, 230, 48), 25, muted, align="right")
        d.line((80, 110, 1840, 110), fill=self.color("muted" if dark else "grid"), width=2)
        footer = scene.get("source", self.p.get("footer", ""))
        self.text(im, footer, (80, 1004, 1760, 46), 22, muted)
        total = self.p["_frames"]/self.p["fps"]
        progress = max(0, min(1, time/total))
        d.rectangle((0, 1072, int(W*progress), H), fill=self.color("blue"))

    def heading(self, im, scene):
        self.text(im, scene.get("eyebrow", "РОЗБІР СПОРЯДЖЕННЯ"), (90, 148, 1700, 44), 24, "blue", True)
        self.text(im, scene.get("title", ""), (90, 202, 1730, 148), 66, bold=True)

    def render(self, scene, local, index, absolute, footage=None):
        im = footage.copy().convert("RGB") if footage is not None else self.bg.copy()
        kind = scene["type"]
        d = ImageDraw.Draw(im)
        if kind == "studio":
            # Dedicated minimalist scene. No old brand bar, grid, tables or permanent facts.
            if footage is None:
                im = Image.new("RGB", (W, H), self.c["background"])
                if scene.get("full_bleed") and scene.get("_image"):
                    im = ImageOps.fit(asset(scene["_image"]).convert("RGB"), (W,H), Image.Resampling.LANCZOS)
                else:
                    self.picture(im, scene, (140, 90, 1640, 720), local)
            if scene.get("_subject_only"):
                return im
            if local < scene.get("label_start", 0):
                return im
            if scene.get("full_bleed"):
                panel=Image.new('RGBA',(W,250),(242,243,240,235))
                im.paste(panel,(0,830),panel)
            country_flag(im, scene["country"], 90, 855)
            self.text(im, scene.get("title", ""), (90, 930, 1720, 115), 78, bold=True)
            for callout in scene.get("callouts", []):
                if callout["start"] <= local < callout["end"]:
                    self.tag(im, callout["text"], 1230, 100, 600)
            if scene.get("show_source"):
                self.text(im, scene.get("source", ""), (850, 1034, 980, 30), 18, "muted", align="right")
            return im
        if kind in {"intro", "outro", "section"}:
            self.text(im, scene.get("eyebrow", "ВІЗУАЛЬНИЙ РОЗБІР"), (180, 260, 1560, 60), 28, "blue", True, "center")
            self.text(im, scene.get("title", ""), (180, 370+int(30*(1-ease(local/.6))), 1560, 270), 112 if kind == "section" else 98, bold=True, align="center")
            d.rectangle((860, 695, 1060, 702), fill=self.color("yellow"))
            if local > .3:
                self.text(im, scene.get("subtitle", ""), (320, 754, 1280, 150), 36, "muted", align="center")
        elif kind == "item":
            self.tag(im, scene.get("category", "СПОРЯДЖЕННЯ"), 90, 155, 510)
            self.picture(im, scene, (100, 265, 1050, 590), local)
            self.text(im, scene.get("title", ""), (1200, 270, 620, 180), 66, bold=True)
            self.text(im, scene.get("subtitle", ""), (1200, 470, 620, 100), 31, "muted")
            for j, fact in enumerate(scene.get("facts", [])):
                if local >= .35+j*.6:
                    self.tag(im, fact, 1200+int(22*(1-ease((local-.35-j*.6)/.35))), 600+j*84, 615, "yellow" if j == 1 else "blue")
            if scene.get("note"):
                self.text(im, scene["note"], (110, 902, 1690, 65), 25, "muted")
        elif kind == "compare":
            self.heading(im, scene)
            for j, side in enumerate(scene["sides"]):
                x = 90+j*900
                self.panel(im, (x, 370, x+840, 940))
                accent = "blue" if j == 0 else "olive"
                self.tag(im, side.get("label", ""), x+30, 393, 780, accent)
                self.picture(im, side, (x+60, 475, 720, 290), local-j*.2, accent)
                self.text(im, side.get("title", ""), (x+35, 785, 770, 70), 39, bold=True, align="center")
                self.text(im, side.get("detail", ""), (x+50, 866, 740, 65), 26, "muted", align="center")
        elif kind == "bars":
            self.heading(im, scene)
            rows = scene["values"]
            row_h = min(100, 520/len(rows))
            self.text(im, scene.get("unit", ""), (650, 350, 1100, 50), 24, "muted")
            for j, row in enumerate(rows):
                y = 420+j*row_h
                self.text(im, row["label"], (95, y-3, 495, int(row_h)-12), 32, bold=True)
                d.rounded_rectangle((650, y, 1620, y+42), radius=5, fill=self.color("grid"))
                progress = ease((local-.2-j*.14)/.9)
                bar_w = 970*row["value"]/scene["maximum"]*progress
                if bar_w > 0:
                    d.rounded_rectangle((650, y, 650+bar_w, y+42), radius=min(5, bar_w/2), fill=self.color(row.get("color", "blue")))
                self.text(im, row.get("display", str(row["value"])), (1660, y-3, 160, 58), 34, bold=True)
            self.text(im, scene.get("note", ""), (95, 918, 1710, 65), 25, "muted")
        elif kind == "kit":
            self.heading(im, scene)
            items = scene["items"]
            cols = 3 if len(items) > 4 else 2
            cell_w = 1760/cols
            rows = math.ceil(len(items)/cols)
            cell_h = 570/rows
            for j, obj in enumerate(items):
                x = 80+(j%cols)*cell_w
                y = 360+(j//cols)*cell_h
                self.panel(im, (x+10, y+10, x+cell_w-10, y+cell_h-10))
                self.picture(im, obj, (x+40, y+22, cell_w-80, cell_h-105), local-j*.12)
                self.text(im, obj.get("label", ""), (x+30, y+cell_h-80, cell_w-60, 60), 29, bold=True, align="center")
        elif kind == "diagram":
            self.heading(im, scene)
            nodes = scene["nodes"]
            n = len(nodes)
            step = 1740/n
            if self.p.get('style') == 'minimal':
                for j,node in enumerate(nodes):
                    x=100+j*step
                    if local >= j*.45:
                        d.ellipse((x+25,470,x+45,490),fill=self.color('blue'))
                        self.text(im,node['title'],(x+25,545,step-95,160),46,bold=True)
                        self.text(im,node.get('detail',''),(x+25,730,step-95,100),28,'muted')
                    if j<n-1 and local >= (j+1)*.45:
                        ax=x+step-35
                        d.line((ax-50,620,ax+5,620),fill=self.color('muted'),width=3)
                        d.polygon([(ax+10,620),(ax-2,612),(ax-2,628)],fill=self.color('muted'))
                return im
            for j, node in enumerate(nodes):
                x = 100+j*step
                if j < n-1:
                    ax = x+step-25
                    d.line((ax-28, 595, ax+12, 595), fill=self.color("muted"), width=5)
                    d.polygon([(ax+14, 595), (ax-2, 584), (ax-2, 606)], fill=self.color("muted"))
                if local >= j*.45:
                    self.panel(im, (x, 435, x+step-70, 815))
                    d.ellipse((x+35, 470, x+109, 544), fill=self.color("blue"))
                    self.text(im, str(j+1), (x+35, 480, 74, 50), 30, "panel", True, "center")
                    self.text(im, node["title"], (x+30, 590, step-130, 100), 35, bold=True)
                    self.text(im, node.get("detail", ""), (x+30, 705, step-130, 85), 25, "muted")
            self.text(im, scene.get("note", ""), (100, 912, 1710, 70), 25, "muted")
        elif kind == "footage":
            if footage is None:
                d.rectangle((0, 0, W, H), fill=self.color("dark"))
            self.panel(im, (80, 745, 1370, 940), "dark", radius=5)
            self.text(im, scene.get("title", ""), (110, 770, 1220, 95), 52, "panel", True)
            self.text(im, scene.get("subtitle", ""), (110, 874, 1220, 55), 28, "panel")
        self.common(im, scene, index, absolute)
        # A short clean fade from the editorial background, not a generated transition.
        if kind != "footage" and local < .18:
            im = Image.blend(self.bg, im, ease(local/.18))
        return im


def output_size(image, width, height):
    if image.size == (width, height):
        return image
    # Letterbox custom aspect ratios; never stretch the design.
    fitted = ImageOps.contain(image, (width, height), Image.Resampling.LANCZOS)
    result = Image.new("RGB", (width, height), "#202923")
    result.paste(fitted, ((width-fitted.width)//2, (height-fitted.height)//2))
    return result
