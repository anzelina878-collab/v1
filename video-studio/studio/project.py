import copy
import json
import math
import shutil
import subprocess
from pathlib import Path

KINDS = {"intro", "section", "item", "compare", "bars", "kit", "diagram", "footage", "outro"}
THEME = {
    "background": "#F2F3F0", "ink": "#202923", "muted": "#68736C",
    "blue": "#28608C", "yellow": "#D6AD43", "olive": "#6A7952",
    "grid": "#E3E7E0", "panel": "#FFFFFF", "dark": "#202923",
    "font": "fonts/DejaVuSans.ttf", "font_bold": "fonts/DejaVuSans-Bold.ttf",
}
ROOT = Path(__file__).resolve().parents[1]


def probe(path):
    proc = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True)
    if proc.returncode:
        raise ValueError(f"Не вдалося прочитати медіа: {path}\n{proc.stderr[-500:]}")
    return json.loads(proc.stdout)


def finite(value, label, minimum=0):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
        raise ValueError(f"{label}: очікується число >= {minimum}")
    return float(value)


def load_project(filename, require_assets=True):
    path = Path(filename).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise ValueError("Потрібна версія конфігурації 1")
    data = copy.deepcopy(data)
    data["_base"] = str(path.parent)
    data["_path"] = str(path)
    data["theme"] = {**THEME, **data.get("theme", {})}
    width, height = data.get("width", 1920), data.get("height", 1080)
    for value, name in [(width, "width"), (height, "height")]:
        if type(value) is not int or value < 240 or value > 7680 or value % 2:
            raise ValueError(f"{name}: парне ціле число від 240 до 7680")
    data["width"], data["height"] = width, height
    fps = data.setdefault("fps", 30)
    if type(fps) is not int or not 1 <= fps <= 60:
        raise ValueError("fps: ціле число від 1 до 60")
    for key in ("font", "font_bold"):
        p = Path(data["theme"][key])
        if not p.is_absolute():
            local = path.parent / p
            p = local if local.exists() else ROOT / p
        if not p.is_file():
            raise ValueError(f"Не знайдено шрифт {p}")
        data["theme"][key] = str(p)
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("scenes: потрібна непорожня послідовність сцен")
    cursor = 0
    ids = set()
    for i, scene in enumerate(scenes):
        sid = scene.setdefault("id", f"scene-{i+1:03}")
        if not isinstance(sid, str) or not sid or sid in ids:
            raise ValueError(f"Неунікальний або порожній id сцени: {sid}")
        ids.add(sid)
        kind = scene.get("type")
        if kind not in KINDS:
            raise ValueError(f"{sid}: невідомий тип {kind}")
        duration = finite(scene.get("duration"), f"{sid}.duration", 1/fps)
        start = finite(scene.get("start", cursor), f"{sid}.start")
        if abs(start - cursor) > 0.001:
            raise ValueError(f"{sid}: start={start:.3f}; очікується {cursor:.3f}. Сцени мають іти без проміжків та перекриття")
        scene["start"], scene["duration"] = start, duration
        scene["_start_frame"] = round(start * fps)
        scene["_end_frame"] = round((start + duration) * fps)
        if scene["_end_frame"] <= scene["_start_frame"]:
            raise ValueError(f"{sid}: тривалість менша за кадр")
        cursor = start + duration
        if kind == "item" and len(scene.get("facts", [])) > 3:
            raise ValueError(f"{sid}: максимум 3 факти на картці")
        if kind == "compare" and len(scene.get("sides", [])) != 2:
            raise ValueError(f"{sid}: compare потребує рівно дві сторони")
        if kind == "bars":
            values = scene.get("values", [])
            if not 1 <= len(values) <= 6:
                raise ValueError(f"{sid}: потрібно від 1 до 6 стовпчиків")
            for v in values:
                finite(v.get("value"), f"{sid}.value")
            maximum = finite(scene.get("maximum", max(v["value"] for v in values)), f"{sid}.maximum", 0.001)
            if maximum < max(v["value"] for v in values):
                raise ValueError(f"{sid}: maximum менший за значення")
            scene["maximum"] = maximum
        if kind == "kit" and not 1 <= len(scene.get("items", [])) <= 6:
            raise ValueError(f"{sid}: kit потребує від 1 до 6 предметів")
        if kind == "diagram" and not 2 <= len(scene.get("nodes", [])) <= 4:
            raise ValueError(f"{sid}: diagram потребує від 2 до 4 вузлів")
        if kind == "footage" and not scene.get("video"):
            raise ValueError(f"{sid}: потрібне поле video")
        if kind == "footage":
            finite(scene.get("in", 0), f"{sid}.in")
            if scene.get("fit", "cover") not in {"cover", "contain"}:
                raise ValueError(f"{sid}: fit має бути cover або contain")
        objects = [scene] + scene.get("sides", []) + scene.get("items", [])
        for obj in objects:
            for key in ("image", "video"):
                if obj.get(key):
                    asset = (path.parent / obj[key]).resolve()
                    obj["_"+key] = str(asset)
                    if require_assets and not asset.is_file():
                        raise ValueError(f"{sid}: не знайдено {key}: {asset}")
        if kind == "footage" and require_assets:
            media = probe(scene["_video"])
            if not any(s.get("codec_type") == "video" for s in media.get("streams", [])):
                raise ValueError(f"{sid}: файл не має відеопотоку")
            clip_duration = float(media["format"].get("duration", 0))
            if scene.get("in", 0) >= clip_duration:
                raise ValueError(f"{sid}: in виходить за межі відео")
            if not scene.get("loop", False) and scene.get("in", 0) + duration > clip_duration + 0.05:
                raise ValueError(f"{sid}: відео закоротке; скоротіть сцену або встановіть loop: true")
    data["_duration"] = cursor
    data["_frames"] = round(cursor*fps)
    policy = data.setdefault("audio_policy", "pad_video")
    if policy not in {"pad_video", "strict"}:
        raise ValueError("audio_policy: pad_video або strict")
    if data.get("audio"):
        audio = (path.parent / data["audio"]).resolve()
        if not audio.is_file():
            raise ValueError(f"Не знайдено озвучку: {audio}")
        media = probe(audio)
        if not any(s.get("codec_type") == "audio" for s in media.get("streams", [])):
            raise ValueError("Файл озвучки не містить аудіопотоку")
        length = float(media["format"]["duration"])
        data["_audio"], data["_audio_duration"] = str(audio), length
        if length > cursor + 1/fps:
            if policy == "strict":
                raise ValueError(f"Озвучка {length:.2f} с довша за відеоряд {cursor:.2f} с")
            # Hold the final rendered frame. Never invent extra narration/scenes.
            data["_frames"] = max(data["_frames"], math.ceil(length*fps))
    return data


def require_ffmpeg():
    for cmd in ("ffmpeg", "ffprobe"):
        if not shutil.which(cmd):
            raise ValueError(f"Не знайдено {cmd}. Встановіть FFmpeg і додайте до PATH")
