import copy,hashlib,json,math,shutil,struct,tempfile,unittest,wave
from pathlib import Path
from PIL import Image
from studio.project import ROOT,load_project,probe
from studio.fast import render_fast
from tools.assemble_revision import assemble,compatible_clip

class RevisionAssemblyTests(unittest.TestCase):
    def test_reuses_verified_base_clip_preserves_voice_and_rejects_stale_assets(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'work') as temp:
            folder=Path(temp);Image.new('RGB',(320,180),'olive').save(folder/'object.png')
            with wave.open(str(folder/'voice.wav'),'wb') as w:
                w.setparams((1,2,16000,0,'NONE','not compressed'))
                w.writeframes(b''.join(struct.pack('<h',int(10000*math.sin(2*math.pi*440*i/16000))) for i in range(32000)))
            data={'version':1,'style':'minimal','width':480,'height':270,'fps':6,'audio':'voice.wav','audio_policy':'strict','scenes':[{'id':'one','type':'studio','duration':1,'country':'US','image':'object.png','title':'TEST','motion_kind':'verified_static'},{'id':'two','type':'studio','duration':1,'country':'US','image':'object.png','title':'TEST','motion_kind':'verified_static'}]}
            base=folder/'base.json';base.write_text(json.dumps(data));project=load_project(base)
            render_fast(project,folder/'base.mp4',preset='fast',crf=25)
            identity=hashlib.sha256(base.read_bytes()).hexdigest()[:16]
            shutil.copyfile(ROOT/'work'/'compiled'/identity/'0001'/'scene.mp4',folder/'archive.mp4')
            revision=copy.deepcopy(data);revision['scenes'][1]={'id':'two','type':'footage','duration':1,'video':'archive.mp4','archive_edit':{'source':'synthetic_pipeline_test_fixture'}}
            config=folder/'new.json';config.write_text(json.dumps(revision))
            target=folder/'result.mp4';assemble(base,config,target)
            info=probe(target);v=next(s for s in info['streams'] if s['codec_type']=='video')
            self.assertEqual(int(v['nb_frames']),12)
            self.assertTrue(any(s['codec_type']=='audio' for s in info['streams']))
            with self.assertRaisesRegex(ValueError,'frame count'):
                compatible_clip(target,project,13)
            Image.new('RGB',(320,180),'purple').save(folder/'object.png')
            with self.assertRaisesRegex(ValueError,'Base scene/assets changed'):
                assemble(base,config,folder/'stale.mp4')

if __name__=='__main__':unittest.main()
