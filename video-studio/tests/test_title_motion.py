import unittest
from PIL import Image,ImageChops
from studio.project import THEME,ROOT
from studio.visuals import Painter
try:
    import numpy as np
    from tools.gltf_mesh import matrix
except ImportError:
    np=None

class TitleMotionTests(unittest.TestCase):
    def painter(self,enabled):
        theme={**THEME,'font':str(ROOT/THEME['font']),'font_bold':str(ROOT/THEME['font_bold'])}
        return Painter({'style':'minimal','theme':theme,'title_motion':enabled})

    def test_reveal_finishes_and_retains_ukrainian_text(self):
        p=self.painter(True)
        def draw(t):
            im=Image.new('RGB',(1920,1080),'white')
            p.motion_text(im,'УКРАЇНА: СПОРЯДЖЕННЯ',(90,100,1500,150),t,78,bold=True)
            return im
        first,late,settled=draw(0),draw(1),draw(2)
        self.assertIsNotNone(ImageChops.difference(first,late).getbbox())
        self.assertIsNone(ImageChops.difference(late,settled).getbbox())
        self.assertIsNotNone(ImageChops.difference(late,Image.new('RGB',late.size,'white')).getbbox())

    def test_disabled_motion_preserves_existing_titles(self):
        p=self.painter(False);a=Image.new('RGB',(1920,1080),'white');b=a.copy()
        p.motion_text(a,'M249',(90,100,1500,150),0,78,bold=True)
        p.text(b,'M249',(90,100,1500,150),78,bold=True)
        self.assertIsNone(ImageChops.difference(a,b).getbbox())

    @unittest.skipIf(np is None,'optional 3D dependencies not installed')
    def test_gltf_transform_keeps_translation_rotation_and_scale(self):
        m=matrix({'translation':[3,4,5],'rotation':[0,0,2**-.5,2**-.5],'scale':[2,3,4]})
        np.testing.assert_allclose(m@np.array([1,0,0,1]),[3,6,5,1],atol=1e-7)

if __name__=='__main__':unittest.main()
