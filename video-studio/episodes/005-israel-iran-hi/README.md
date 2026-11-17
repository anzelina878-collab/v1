# Israel vs Iran — Hindi edition

1920×1080, 30 fps. Separate language edition of episode 005. The Ukrainian original is preserved.

Install `video-studio/requirements.txt`, then run from this directory:

```sh
python build_episode.py
python check_episode.py
python render_episode.py --work /tmp/arsenal-hi005/compiled --preview
python render_episode.py --work /tmp/arsenal-hi005/compiled --output output/final_video_hi_v1.mp4
python check_episode.py --video output/final_video_hi_v1.mp4 --work /tmp/arsenal-hi005/compiled
```

The source ZIP contains actual media, geometry sources, licensing, fonts, and timing data. Ordinary rendering uses pre-rendered native 3D banks and does not need speech recognition, Blender, network access, or a GPU. Regenerating geographic terrain additionally needs preparation dependencies and the included `video-studio/tools/software_turntable.py`.

Archive footage runs at original speed without loops or frozen tails. Native object rotation uses the original 720-pose / 24-second banks. Photos are locked; information cards enter once and hold. Geographic terrain maps remain animated and use Hindi labels.

See `SOURCES.md` for the existing source/licensing ledger and `output/qa` for the technical and sampled visual review. Automated checks and contact sheets do not constitute continuous human viewing/listening.
