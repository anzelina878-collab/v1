# Das Ende des Universums — visual revision V3

This revision responds to the request for more real archive material, purposeful 3D infographics and a denser opening. The supplied 26-minute German narration remains the timing reference.

- 207 shots; 28 in the opening 70 seconds.
- About 5 minutes 54 seconds of newly selected historical, observatory, instrument and research archive footage, distributed across the film; real SDO/ISS observations are additional.
- Original spatial explainers cover fusion, expansion, temperature gradients and conditional cosmic endings. Beautiful NASA/ESA/ESO stock remains in the edit.
- No numbered chapter bars, flat charts, decorative HUD or permanent technical labels.

The finished film is delivered as one MP4 in GitHub Releases. The user does not need Colab or to join any parts.

See [SOURCES.md](SOURCES.md) for provenance and attribution, and [SKILL.md](SKILL.md) for the updated reusable editing instructions. Some historical excerpts have lower native resolution; they are not represented as native HD.

## Rebuild

Provide the original narration privately as `narration.mp3`. Install Blender 4.x and ffmpeg. Run `python download_assets.py`, then `python render.py --audio narration.mp3 --output Universum_V3_1080p.mp4`. The original narration is not stored in this public repository. Frame interpolation and Blender versions can change encoded output; this project preserves editorial timing and source choices rather than promising byte-identical rendering on every machine.
