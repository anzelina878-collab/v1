import json
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

from PIL import Image, ImageChops
from PIL import ImageStat

from studio.cli import check_art, preview, render, new_episode
from studio.project import ROOT, load_project, probe


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT/"work")
        self.base = Path(self.tmp.name)
        self.data = {
            "version": 1, "width": 320, "height": 240, "fps": 6,
            "scenes": [{"id": "one", "type": "intro", "duration": .5, "title": "Тест"}],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def config(self):
        p = self.base/"episode.json"
        p.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
        return p

    def audio(self, duration):
        p = self.base/"supplied.wav"
        with wave.open(str(p), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(16000)
            f.writeframes(b"\x00\x00"*round(duration*16000))
        self.data["audio"] = p.name

    def test_discontinuous_timeline_rejected(self):
        self.data["scenes"].append({"id": "two", "type": "section", "start": .4, "duration": 1})
        with self.assertRaisesRegex(ValueError, "без проміжків"):
            load_project(self.config())

    def test_rounding_does_not_drop_or_duplicate_scene_frames(self):
        self.data["fps"] = 24
        self.data["scenes"] = [{"id": str(i), "type": "intro", "duration": .13} for i in range(10)]
        p = load_project(self.config())
        intervals = [(s["_start_frame"], s["_end_frame"]) for s in p["scenes"]]
        self.assertEqual(sum(b-a for a, b in intervals), p["_frames"])
        self.assertTrue(all(intervals[i][1] == intervals[i+1][0] for i in range(9)))

    def test_missing_art_rejected_for_final_but_allowed_in_draft(self):
        self.data["scenes"] = [{"id": "object", "type": "item", "duration": 2, "title": "Шолом"}]
        p = load_project(self.config())
        with self.assertRaisesRegex(ValueError, "Потрібні зображення"):
            check_art(p, False)
        check_art(p, True)

    def test_strict_audio_mismatch_rejected(self):
        self.audio(1.5)
        self.data["audio_policy"] = "strict"
        with self.assertRaisesRegex(ValueError, "довша"):
            load_project(self.config())

    def test_bad_chart_scale_rejected(self):
        self.data["scenes"] = [{"id": "chart", "type": "bars", "duration": 1, "maximum": 5, "values": [{"label": "A", "value": 9}]}]
        with self.assertRaisesRegex(ValueError, "maximum менший"):
            load_project(self.config())

    def test_new_episode_never_replaces_existing_work(self):
        target = self.base/"new"
        new_episode(target)
        before = (target/"episode.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "вже існує"):
            new_episode(target)
        self.assertEqual(before, (target/"episode.json").read_bytes())

    def test_render_muxes_supplied_audio_and_holds_final_video_frame(self):
        self.audio(1.5)
        self.data["audio_policy"] = "pad_video"
        clip = str(ROOT/"episodes/demo/assets/abstract.mp4")
        self.data["scenes"].append({"id": "clip", "type": "footage", "duration": .5, "video": clip, "in": .2, "title": "Тест"})
        p = load_project(self.config())
        out = self.base/"result.mp4"
        render(p, out, crf=18, preset="ultrafast")
        media = probe(out)
        video = next(s for s in media["streams"] if s["codec_type"] == "video")
        self.assertTrue(any(s["codec_type"] == "audio" for s in media["streams"]))
        self.assertEqual((video["width"], video["height"]), (320, 240))
        self.assertEqual(int(video["nb_frames"]), 9)
        self.assertAlmostEqual(float(media["format"]["duration"]), 1.5, delta=.08)
        # The supplied clip has moving markers. Its center must stop moving during the audio tail.
        proc = subprocess.run(["ffmpeg", "-v", "error", "-i", str(out), "-vf", "select=eq(n\\,5)+eq(n\\,8)", "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"], capture_output=True, check=True)
        size = 320*240*3
        self.assertEqual(len(proc.stdout), size*2)
        first = Image.frombytes("RGB", (320, 240), proc.stdout[:size]).crop((30, 65, 290, 140))
        last = Image.frombytes("RGB", (320, 240), proc.stdout[size:]).crop((30, 65, 290, 140))
        diff = ImageChops.difference(first, last)
        self.assertLess(sum(ImageStat.Stat(diff).mean)/3, 3)

    def test_short_audio_padded_to_visual_duration(self):
        self.audio(.2)
        self.data["scenes"][0]["duration"] = 1
        p = load_project(self.config())
        out = self.base/"padded.mp4"
        render(p, out, preset="ultrafast")
        media = probe(out)
        audio = next(s for s in media["streams"] if s["codec_type"] == "audio")
        self.assertAlmostEqual(float(audio["duration"]), 1, delta=.1)

    def test_ukrainian_text_previews_and_overflow_fails(self):
        self.data["scenes"][0]["title"] = "Її спорядження: ґрунтовний огляд"
        p = load_project(self.config())
        out = self.base/"preview.png"
        preview(p, out, at=.3)
        with Image.open(out) as im:
            self.assertEqual(im.size, (320, 240))
        self.data["scenes"][0]["title"] = "Надто довгий текст "*1000
        with self.assertRaisesRegex(ValueError, "не вміщується"):
            preview(load_project(self.config()), self.base/"overflow.png", at=.3)


if __name__ == "__main__":
    unittest.main()
