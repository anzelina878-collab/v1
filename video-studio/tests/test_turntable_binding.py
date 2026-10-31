import json,tempfile,unittest
from pathlib import Path
from tools.apply_turntables import apply

class TurntableBindingTests(unittest.TestCase):
    def test_binding_does_not_hide_unavailable_models_or_static_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);(base/'clip.mp4').write_bytes(b'prepared by renderer')
            (base/'clip.3d.json').write_text(json.dumps({'motion_kind':'true_3d','yaw_start':0,'yaw_end':360}))
            registry={'objects':{'M4A1':{'status':'ready','video':'clip.mp4','license':'CC0','source_url':'https://opengameart.org/content/m4a1-assault-rifle'}}}
            scenes=[{'id':'one','type':'studio','image':'M4A1.png','title':'M4A1','country':'US'},
                    {'id':'two','type':'studio','image':'QBZ191.png','title':'QBZ-191','country':'CN'},
                    {'id':'three','type':'compare','sides':[{'image':'M4A1.png'},{'image':'QBZ191.png'}]}]
            data,report=apply({'scenes':scenes},registry,base)
            self.assertFalse(report['all_objects_animated']);self.assertEqual(len(report['unresolved']),3)
            self.assertEqual(data['scenes'][0]['video'],'clip.mp4');self.assertNotIn('image',data['scenes'][0])
            self.assertEqual(data['production_status'],'incomplete_3d_draft')
            self.assertIn('image',scenes[0])

    def test_partial_spin_is_not_accepted_as_full_circle(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);(base/'clip.mp4').write_bytes(b'clip')
            (base/'clip.3d.json').write_text(json.dumps({'motion_kind':'true_3d','yaw_start':-25,'yaw_end':25}))
            with self.assertRaisesRegex(ValueError,'full revolution'):
                apply({'scenes':[{'id':'one','type':'studio','image':'M4A1.png'}]}, {'objects':{'M4A1':{'status':'ready','video':'clip.mp4','license':'CC0','source_url':'source'}}},base)

if __name__=='__main__':unittest.main()
