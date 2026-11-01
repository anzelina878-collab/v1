"""Regression checks for the user's concrete revision requirements."""
import json,unittest
from pathlib import Path
from edit_rules import check_archive_spacing
B=Path(__file__).resolve().parents[1]
class RevisionV2Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=json.loads((B/'episode.v2.json').read_text());cls.a={x['id']:x for x in json.loads((B/'assets/manifest.v2.json').read_text())}
 def test_hook_has_continuous_fast_speech_bound_coverage(self):
  scenes=[s for s in self.p['scenes'] if s['start']<90];self.assertGreaterEqual(len(scenes),30);self.assertEqual(scenes[0]['start'],0)
  for s in scenes:self.assertLessEqual(s['duration'],4);self.assertNotEqual(s['kind'],'graphic')
  for a,b in zip(scenes,scenes[1:]):self.assertAlmostEqual(a['end'],b['start'])
  self.assertGreaterEqual(scenes[-1]['end'],90)
 def test_video_names_are_present_and_first_ship_is_identified(self):
  self.assertIn('GERALD R. FORD',self.p['scenes'][0]['title'])
  for s in self.p['scenes']:
   if s['kind']=='archive':self.assertTrue(s['title'].strip());self.assertTrue(self.a[s['asset_id']].get('video_source'))
 def test_reuse_policy_survives_hook_and_new_cc_sources(self):self.assertTrue(check_archive_spacing(self.p['scenes']))
 def test_same_voice_timeline_and_real_geometry_not_warped_photos(self):
  old=json.loads((B/'episode.json').read_text());self.assertEqual(self.p['audio'],old['audio']);self.assertEqual(self.p['duration'],old['duration'])
  models={s['asset_id'] for s in self.p['scenes'] if s['kind']=='turntable'};self.assertGreaterEqual(len(models),12)
  for key in models:self.assertIn('true_3d',self.a[key]['kind']);self.assertTrue(self.a[key].get('model_source'));self.assertTrue(self.a[key].get('model_license'))
if __name__=='__main__':unittest.main()
