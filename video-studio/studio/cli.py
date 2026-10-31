import argparse
import hashlib
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

from .project import ROOT, load_project, probe, require_ffmpeg
from .visuals import Painter, output_size, W, H


def check_art(project, allow_placeholders):
    missing = []
    for scene in project["scenes"]:
        objects = [scene] if scene["type"] == "item" else scene.get("sides", []) + scene.get("items", [])
        for obj in objects:
            if not obj.get("_image"):
                missing.append(scene["id"])
            else:
                try:
                    with Image.open(obj["_image"]) as im:
                        im.verify()
                except Exception as error:
                    raise ValueError(f"{scene['id']}: пошкоджене зображення: {error}") from error
    if missing and not allow_placeholders:
        raise ValueError(f"Потрібні зображення у сценах: {', '.join(dict.fromkeys(missing))}. Для чорновика: --allow-placeholders")


def scene_at(project, frame):
    for i, scene in enumerate(project["scenes"]):
        if frame < scene["_end_frame"]:
            return i, scene, (frame-scene["_start_frame"])/project["fps"]
    scene = project["scenes"][-1]
    # Extra audio tail uses the final frame, including footage.
    return len(project["scenes"])-1, scene, (scene["_end_frame"]-scene["_start_frame"]-1)/project["fps"]


def video_filter(width, height, fit):
    if fit == "contain":
        return f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x202923"
    return f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"


class ClipReader:
    def __init__(self, scene, fps):
        self.last = None
        self.err = tempfile.TemporaryFile()
        cmd = ["ffmpeg", "-v", "error", "-threads", "1"]
        if scene.get("loop"):
            cmd += ["-stream_loop", "-1"]
        cmd += ["-ss", str(scene.get("in", 0)), "-i", scene["_video"], "-an", "-sn", "-vf", f"fps={fps},"+video_filter(W, H, scene.get("fit", "cover")), "-threads", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=self.err)

    def next(self):
        raw = self.proc.stdout.read(W*H*3)
        if len(raw) != W*H*3:
            self.err.seek(0)
            detail = self.err.read().decode(errors="replace")
            if detail:
                raise ValueError(f"Помилка відеовставки: {detail[-1000:]}")
            if self.last is None:
                raise ValueError("Не вдалося прочитати перший кадр відеовставки")
            return self.last
        self.last = Image.frombytes("RGB", (W, H), raw)
        return self.last

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        self.proc.stdout.close()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        self.err.close()


def clip_still(scene, local):
    position = scene.get("in", 0)+local
    if scene.get("loop"):
        position %= float(probe(scene["_video"])["format"]["duration"])
    cmd = ["ffmpeg", "-v", "error", "-ss", str(position), "-i", scene["_video"], "-frames:v", "1", "-vf", video_filter(W, H, scene.get("fit", "cover")), "-threads", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode or len(proc.stdout) != W*H*3:
        raise ValueError(f"Не вдалося створити прев'ю відеовставки: {proc.stderr.decode(errors='replace')[-500:]}")
    return Image.frombytes("RGB", (W, H), proc.stdout)


def safe_output(project, path):
    path = Path(path).resolve()
    inputs = {project["_path"], project.get("_audio", ""), project["theme"]["font"], project["theme"]["font_bold"]}
    for scene in project["scenes"]:
        for obj in [scene]+scene.get("sides", [])+scene.get("items", []):
            inputs.update(obj.get(k, "") for k in ("_image", "_video"))
    if str(path) in inputs:
        raise ValueError("Вихідний файл не може заміняти вхідні матеріали")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def preview(project, target, at=None):
    target = safe_output(project, target)
    painter = Painter(project)
    if at is not None:
        finite_at = float(at)
        if not math.isfinite(finite_at) or not 0 <= finite_at < project["_frames"]/project["fps"]:
            raise ValueError("Час прев'ю поза межами відео")
        index, scene, local = scene_at(project, round(finite_at*project["fps"]))
        clip = clip_still(scene, local) if scene["type"] == "footage" else None
        im = painter.render(scene, local, index, finite_at, clip)
        output_size(im, project["width"], project["height"]).save(target)
    else:
        count = len(project["scenes"])
        cols, cell_w, cell_h = 3, 640, 390
        sheet = Image.new("RGB", (cols*cell_w, math.ceil(count/cols)*cell_h), "#DDE2DB")
        draw = ImageDraw.Draw(sheet)
        for index, scene in enumerate(project["scenes"]):
            local = min(max(2, scene["duration"]*.55), scene["duration"]-1/project["fps"])
            clip = clip_still(scene, local) if scene["type"] == "footage" else None
            im = painter.render(scene, local, index, scene["start"]+local, clip)
            im = im.resize((640, 360), Image.Resampling.LANCZOS)
            x, y = index%cols*cell_w, index//cols*cell_h
            sheet.paste(im, (x, y))
            draw.text((x+12, y+366), f"{scene['start']:.2f}s  |  {scene['id']}  |  {scene['type']}", fill="#202923")
        sheet.save(target)
    print(f"Прев'ю: {target}")


def render(project, target, crf=20, preset="fast"):
    target = safe_output(project, target)
    if target.suffix.lower() != ".mp4":
        raise ValueError("Вихід відео має бути .mp4")
    painter = Painter(project)
    width, height, fps = project["width"], project["height"], project["fps"]
    (ROOT/"work").mkdir(exist_ok=True)
    reader = None
    encoder = None
    with tempfile.TemporaryDirectory(prefix="render-", dir=ROOT/"work") as scratch:
        silent = Path(scratch)/"video.mp4"
        # Render to scratch; the user's previous output survives failures.
        with (Path(scratch)/"ffmpeg.log").open("w+") as err:
            cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "pipe:0", "-an", "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", "-threads", "2", "-movflags", "+faststart", str(silent)]
            encoder = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=err)
            current = None
            clip = None
            try:
                for frame in range(project["_frames"]):
                    index, scene, local = scene_at(project, frame)
                    if index != current:
                        if reader:
                            reader.close()
                            reader = None
                        current, clip = index, None
                        print(f"[{index+1}/{len(project['scenes'])}] {scene['id']} ({scene['type']})", flush=True)
                        if scene["type"] == "footage":
                            reader = ClipReader(scene, fps)
                    if reader and frame < scene["_end_frame"]:
                        clip = reader.next()
                    im = painter.render(scene, local, index, frame/fps, clip)
                    im = output_size(im, width, height)
                    encoder.stdin.write(im.tobytes())
                encoder.stdin.close()
                code = encoder.wait()
                if code:
                    err.seek(0)
                    raise ValueError(f"FFmpeg: {err.read()[-1500:]}")
            except BaseException as error:
                if encoder.poll() is None:
                    encoder.terminate()
                try:
                    encoder.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    encoder.kill()
                    encoder.wait()
                err.seek(0)
                if isinstance(error, BrokenPipeError):
                    raise ValueError(f"FFmpeg зупинився: {err.read()[-1500:]}") from error
                raise
            finally:
                if reader:
                    reader.close()
                if encoder.stdin and not encoder.stdin.closed:
                    encoder.stdin.close()
        finished = Path(scratch)/"finished.mp4"
        if project.get("_audio"):
            cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(silent), "-i", project["_audio"], "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-af", "apad", "-t", str(project["_frames"]/fps), "-movflags", "+faststart", str(finished)]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode:
                raise ValueError(f"Помилка додавання озвучки: {proc.stderr[-1500:]}")
        else:
            finished = silent
        # Copy to a temporary neighbour before atomic replacement (may cross filesystems).
        import shutil
        with tempfile.NamedTemporaryFile(prefix=".studio-", suffix=".mp4", dir=target.parent, delete=False) as handle:
            pending = Path(handle.name)
        try:
            shutil.copyfile(finished, pending)
            pending.replace(target)
        finally:
            pending.unlink(missing_ok=True)
    manifest = {
        "project": Path(project["_path"]).name,
        "config_sha256": hashlib.sha256(Path(project["_path"]).read_bytes()).hexdigest(),
        "width": width, "height": height, "fps": fps,
        "frames": project["_frames"], "duration": project["_frames"]/fps,
        "audio_included": bool(project.get("_audio")),
        "scenes": [{"id": s["id"], "start": s["start"], "duration": s["duration"]} for s in project["scenes"]],
    }
    target.with_suffix(".render.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Готово: {target}")


def new_episode(destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Папка вже існує. Новий випуск має мати окрему папку")
    destination.mkdir(parents=True)
    for sub in ("assets", "audio", "output"):
        (destination/sub).mkdir()
    starter = {
        "version": 1, "brand": "ПРЕДМЕТНО", "title": "Новий випуск",
        "width": 1920, "height": 1080, "fps": 30, "audio": None,
        "audio_policy": "strict", "footer": "ЧОРНОВИК · додайте джерела",
        "scenes": [
            {"id": "opening", "type": "intro", "duration": 5, "eyebrow": "НАЗВА СЕРІЇ", "title": "Назва випуску", "subtitle": "Коротке візуальне питання"},
            {"id": "object", "type": "item", "duration": 8, "category": "КАТЕГОРІЯ", "title": "Назва предмета", "subtitle": "Один короткий опис", "facts": ["Перший факт", "Другий факт"]},
            {"id": "closing", "type": "outro", "duration": 4, "title": "Головний висновок", "subtitle": "Один підсумковий рядок"},
        ],
    }
    (destination/"episode.json").write_text(json.dumps(starter, ensure_ascii=False, indent=2), encoding="utf-8")
    (destination/"INPUTS.md").write_text("# Матеріали випуску\n\nТекст і озвучку надає користувач.\n\n- Текст: додайте окремим файлом.\n- Озвучка: audio/voice.wav або MP3, далі вкажіть audio у episode.json.\n- Зображення: assets/.\n- Таймінги: duration або start + duration для кожної сцени.\n- Джерела: поле source у кожній сцені.\n\nАвтоматичного розуміння сценарію чи вирівнювання голосу немає: план сцен і таймінги готуємо під новий випуск.\n", encoding="utf-8")
    print(f"Новий випуск: {destination/'episode.json'}")


def main():
    parser = argparse.ArgumentParser(description="Предметно — reusable visual video studio")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new", help="Створити папку нового випуску")
    new.add_argument("directory")
    for name in ("validate", "preview", "render", "timeline"):
        p = sub.add_parser(name)
        p.add_argument("project")
        p.add_argument("--allow-placeholders", action="store_true")
        if name in {"preview", "render"}:
            p.add_argument("--output", required=True)
        if name == "preview":
            p.add_argument("--at", type=float, help="Один кадр на вказаній секунді; без параметра — контактний аркуш")
        if name == "render":
            p.add_argument("--crf", type=int, default=20, choices=range(0, 52))
            p.add_argument("--preset", choices=["ultrafast", "veryfast", "fast", "medium", "slow"], default="fast")
    args = parser.parse_args()
    try:
        if args.command == "new":
            new_episode(args.directory)
            return
        require_ffmpeg()
        project = load_project(args.project)
        check_art(project, args.allow_placeholders)
        if args.command == "validate":
            print(f"OK · {len(project['scenes'])} сцен · {project['_frames']/project['fps']:.2f} с · {project['width']}×{project['height']} · {project['fps']} fps")
            if project.get("_audio_duration", 0) > project["_duration"]:
                print("Увага: фінальний кадр буде продовжено під довжину озвучки")
        elif args.command == "timeline":
            for scene in project["scenes"]:
                print(f"{scene['start']:8.3f} → {scene['start']+scene['duration']:8.3f}  {scene['id']:20} {scene['type']}")
        elif args.command == "preview":
            preview(project, args.output, args.at)
        elif args.command == "render":
            render(project, args.output, args.crf, args.preset)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"ПОМИЛКА: {error}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
