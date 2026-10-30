import subprocess,sys,unittest
from pathlib import Path
SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
class LegacyGuardTests(unittest.TestCase):
 def check_guard(self,name):
  result=subprocess.run([sys.executable,str(SCRIPTS/name)],capture_output=True,text=True)
  self.assertEqual(result.returncode,2,result.stdout+result.stderr)
 def test_legacy_selector_requires_explicit_opt_in(self):self.check_guard('build_visual_timeline.py')
 def test_legacy_renderer_requires_explicit_opt_in(self):self.check_guard('render_film.py')
 def test_legacy_verifier_cannot_certify_new_film(self):self.check_guard('verify_film.py')
