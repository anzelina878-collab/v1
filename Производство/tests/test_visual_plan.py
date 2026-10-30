import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_visual_plan import validate_plan

class EditorialRegressionTests(unittest.TestCase):
 def setUp(self):
  self.plan={'schema_version':1,'channel_id':'chelovek-bez-litsa','duration_seconds':6,'shots':[{'id':'s1','start':0,'end':6,'asset_id':'a1','narration_quote':'Он написал программу для расчёта','visual_purpose':'Объяснить этап расчёта','editorial_review':'pending'}]}
  self.manifest={'assets':[{'id':'a1','kind':'stock_video','source_url':'https://example.org/test-fixture','usage_basis':'test fixture, not a production asset','tags':[]}]}
 def errors(self,**kw):return validate_plan(self.plan,self.manifest,**kw)['errors']
 def test_algorithm_does_not_authorize_soldering(self):
  self.manifest['assets'][0]['tags']=['soldering'];self.assertTrue(any('irrelevant_soldering' in e for e in self.errors()))
 def test_literal_soldering_can_be_used(self):
  self.manifest['assets'][0]['tags']=['soldering'];self.plan['shots'][0]['narration_quote']='Он паял повреждённую плату';self.assertEqual(self.errors(),[])
 def test_negation_is_not_a_repair_scene(self):
  self.manifest['assets'][0]['tags']=['soldering'];self.plan['shots'][0]['narration_quote']='Он не паял плату';self.assertTrue(any('irrelevant_soldering' in e for e in self.errors()))
 def test_programming_does_not_authorize_board_repair(self):
  self.manifest['assets'][0]['tags']=['pcb_repair'];self.assertTrue(any('irrelevant_pcb_repair' in e for e in self.errors()))
 def test_image_cannot_be_labeled_as_ai_video(self):
  self.manifest['assets'][0].update(kind='ai_video',generation_medium='video',generator='fixture',path='still.png');self.assertTrue(any('photo_is_not_ai_video' in e for e in self.errors()))
 def test_real_portrait_needs_identity_source(self):
  self.manifest['assets'][0].update(kind='real_photo',person_id='person1',verified_identity=False);self.assertTrue(any('portrait_identity' in e for e in self.errors()))
 def test_numbers_need_verified_claim(self):
  self.manifest['assets'][0].update(kind='motion_graphics',numeric_values=[30_000_000],claim_ids=['money1']);self.assertTrue(any('unverified_graphic_claim' in e for e in self.errors(claims=[{'id':'money1','verified':False}])))
 def test_verified_graphic_is_accepted(self):
  self.manifest['assets'][0].update(kind='motion_graphics',numeric_values=[30_000_000],claim_ids=['money1']);self.assertEqual(self.errors(claims=[{'id':'money1','verified':True,'source_url':'https://example.org/fact-fixture'}]),[])
 def test_quote_must_exist_in_supplied_narration(self):
  self.assertTrue(any('quote_not_in_narration' in e for e in self.errors(transcript='Он ушёл домой')))
 def test_timeline_must_not_have_a_gap(self):
  self.plan['shots'][0]['start']=1;self.assertTrue(any('timeline_gap_or_overlap' in e for e in self.errors()))

if __name__=='__main__':unittest.main()
