# ARSENAL 360 / शस्त्र 360 — India vs Pakistan, Hindi

Separate Hindi visual edition of Ukrainian episode 006. 1920×1080, 30 fps, 23:11.500. The supplied voice is preserved without rewriting or tempo adjustment. The Ukrainian edition is unchanged.

The light studio style, real equipment photographs, attributed documentary archives, real native 3D aircraft and terrain maps are preserved. Maps and visible editorial text are Hindi; model identifiers may use Latin letters. Information slides enter once and hold. Equipment photos stay locked; aircraft rotate smoothly at one revolution per 24 seconds. Archive footage plays at its real speed; source exhaustion switches to a relevant still, and reuse is spaced by more than 60 seconds after the previous appearance ends. No frozen or looped archive tails. `archive-cutaways.json` records replacements.

Eleven short chapter cards are timed to voiced category names / the first conclusion sentence. Final questions and channel identity are also localized. Corner source credits retain authorship and licence; geographic maps have no maker watermark.

## Rebuild from ZIP

Extract the whole `video-studio` folder. Use Python 3.11+, FFmpeg/FFprobe and Pillow with RAQM enabled (the merged Hindi/Latin fonts are included). From this episode folder:

```sh
pip install -r requirements-visual.txt
python build_episode.py
python check_episode.py
python render_episode.py --preview --work /tmp/arsenal006hi-render
python render_episode.py --pilot 90 --work /tmp/arsenal006hi-render --output output/pilot90.mp4
python render_episode.py --work /tmp/arsenal006hi-render --output output/final_video_hi_v1.mp4
python check_episode.py --video output/final_video_hi_v1.mp4 --work /tmp/arsenal006hi-render
python tools/check_encoded.py --workspace /tmp/arsenal006hi-render --video output/final_video_hi_v1.mp4
```

Actual media bytes, unchanged voice, fonts, frozen timing, model geometry/textures/licences, map terrain and source code are included in the ZIP. Ordinary rendering needs neither downloads nor speech recognition. GitHub source alone omits bulky working media; use the source ZIP.

To regenerate native map/model banks install `requirements-preparation.txt`; invoke `tools/map_banks.py --kind region --duration 24` (north/navy: 18 seconds), or `tools/render_model_banks.py`. Sources and licences accompany the files.

For a new episode create a separate directory, replace its input audio/script and explicitly review semantic timing, exact equipment and source windows; do not blindly stretch this episode or overwrite previous editions. The Hindi renderer is reusable, but the present alignment and translations are episode-specific.

See `quality_report.md` for completed checks and their limits, `SOURCES.md` for provenance, `chapters.hi.txt` for timecodes, and `INPUTS.json` for original input hashes.
