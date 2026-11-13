"""Optional font build; provided merged fonts work without fontTools at render time."""
from pathlib import Path
from fontTools.merge import Merger
base=Path(__file__).resolve().parents[1]/"fonts"
for weight in ["Regular","Bold"]:
 font=Merger().merge([str(base/f"NotoSansDevanagari-{weight}.ttf"),str(base/f"NotoSans-{weight}.ttf")]);font.save(base/f"ArsenalHindi-{weight}.ttf")
