import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from studio.project import ROOT,load_project,probe
from studio.cli import check_art,preview
from studio.fast import render_fast


class StudioSceneTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'work')
        self.base=Path(self.temp.name)
        Image.new('RGBA',(300,180),(80,95,85,255)).save(self.base/'object.png')
        self.data={'version':1,'style':'minimal','width':480,'height':270,'fps':6,'scenes':[{'id':'object','type':'studio','duration':1,'image':'object.png','country':'US','motion_kind':'verified_static','title':'M4A1','callouts':[{'start':.2,'end':.8,'text':'ТЕСТ'}]}]}

    def tearDown(self):self.temp.cleanup()

    def config(self):
        path=self.base/'episode.json';path.write_text(json.dumps(self.data,ensure_ascii=False));return path

    def test_flat_image_cannot_claim_true_3d(self):
        self.data['scenes'][0]['motion_kind']='true_3d'
        with self.assertRaisesRegex(ValueError,'статичне фото'):
            load_project(self.config())

    def test_timed_callouts_cannot_overlap(self):
        self.data['scenes'][0]['callouts'].append({'start':.5,'end':.9,'text':'Другий факт'})
        with self.assertRaisesRegex(ValueError,'послідовно'):
            load_project(self.config())

    def test_fast_compiler_encodes_timed_overlay_and_supplied_video(self):
        self.data['title_motion']=True
        self.data['scenes'][0]['duration']=1
        self.data['scenes'].append({'id':'video','type':'studio','duration':1,'video':str(ROOT/'episodes/demo/assets/abstract.mp4'),'country':'CN','motion_kind':'verified_video','title':'ТЕСТ ВІДЕО'})
        p=load_project(self.config());check_art(p,False)
        out=self.base/'result.mp4'
        render_fast(p,out,preset='ultrafast',crf=24)
        info=probe(out);video=next(s for s in info['streams'] if s['codec_type']=='video')
        self.assertEqual(int(video['nb_frames']),12)
        self.assertEqual((video['width'],video['height']),(480,270))
        self.assertAlmostEqual(float(info['format']['duration']),2,delta=.05)


if __name__=='__main__':unittest.main()
