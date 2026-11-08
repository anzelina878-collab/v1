"""Rebuild native 30fps geometry banks without retiming short shots."""
from pathlib import Path
import subprocess,sys,json
BASE=Path(__file__).resolve().parents[1];STUDIO=BASE.parents[1]
for folder in sorted((BASE/'assets/models').iterdir()):
 if not (folder/'mesh.npz').exists():continue
 key=folder.name;start=60 if key in ['leopard-illustrative','k2-illustrative','pzh-illustrative','himars-illustrative'] else -25
 subprocess.run([sys.executable,str(STUDIO/'tools/software_turntable.py'),'--mesh',str(folder/'mesh.npz'),'--texture',str(folder/('M4A1_Base_Color.png' if key=='m4' else 'textures.npz')),'--output',str(folder/'spin.mp4'),'--duration','24','--fps','30','--width','1280','--height','720','--yaw-start',str(start),'--yaw-end',str(start+360)],check=True)
 subprocess.run(['ffmpeg','-y','-v','error','-ss','2','-i',str(folder/'spin.mp4'),'-frames:v','1',str(folder/'still.png')],check=True)
 # Full-frame still is also valid for comparison templates; no camera movement.
 from PIL import Image
 Image.open(folder/'still.png').save(folder/'still-object.png')
