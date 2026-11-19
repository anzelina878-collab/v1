"""The revision timeline is frozen in episode.json.
Create a new episode for new narration; do not regenerate from the superseded v1 plan.
"""
from pathlib import Path
import subprocess,sys
B=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(B/'check_episode.py')],check=True)
