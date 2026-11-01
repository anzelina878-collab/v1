import unittest
from edit_rules import archive_allowed,check_archive_spacing,entrance_time
class EditRulesTest(unittest.TestCase):
 def test_source_continuation_cannot_evade_cooldown(self):
  with self.assertRaises(ValueError):check_archive_spacing([{'id':'a','kind':'archive','asset_id':'same-film','start':0,'end':8},{'id':'b','kind':'archive','asset_id':'same-film','start':68,'end':76}])
 def test_return_after_more_than_a_minute(self):
  self.assertTrue(archive_allowed({'film':8},'film',68.01))
 def test_card_never_restarts_after_settling(self):
  self.assertEqual([entrance_time(t) for t in [1.2,2,5,12]],[1.2]*4)
if __name__=='__main__':unittest.main()
