# timeline.json schema

```json
{
  "channel_id": "retro-engineering",
  "format": "long",
  "script_path": "script.txt",
  "pre_render_audit": "pre_render_audit.json",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "audio_language": "uk",
  "shots": [
    {
      "id": "shot_001",
      "start": 0.0,
      "end": 5.0,
      "asset_id": "asset_001",
      "scene_text": "The exact spoken text and why this material is shown",
      "motion": "zoom_in",
      "motion_amount": 0.04,
      "motion_easing": "smoothstep",
      "fit": "crop"
    }
  ]
}
```

start/end are seconds in the finished main video track. Each next shot's start equals the previous end; first start=0; final end matches narration. Align scene changes with words rather than dividing total duration into equal intervals. The renderer quantizes boundaries to the frame grid with up to one-frame error. For video, set kind=video in the registry, source_start in original-file seconds in the shot, and motion=none. Do not confuse source time with overall-video time.

Take shot durations from episode effective_settings: format="long" (or absent format for old timelines) uses assets.default_shot_duration_seconds, default 3–7 seconds; format="shorts" uses shorts.shot_duration_range_seconds, default 2–3 seconds. At 30 fps, these are 90–210 and 60–90 frames respectively. Check original boundaries and actual rounded frame counts, including first/last shots. Redistribute short remainders without trimming speech; explain long scenes with distinct meaningful shots.

The renderer searches upward from the timeline folder for the nearest production.json, checks channel_id, and applies settings_overrides through the shared channel.py mechanism. Keep all timelines, including Shorts and parts, inside episode_dir. Without production.json, project settings apply; do not move timelines outside to evade restrictions. Save request instructions in scope/settings_overrides beforehand.

An audit is required for every local render_video.py build, including plans without channel_id. Missing audits block rendering. pre_render_audit.json requires status="passed", hashes.script/timeline/manifest (SHA-256 for corresponding files), a complete shots list with unique shot_id and status="passed", and source_hashes for every actually used manifest file. source_hashes keys are absolute paths or paths relative to the audited timeline. Visually compare original sources, exact phrases, and crop before recording passed; computing hashes is not verification.

For partial builds, specify audit_parent_timeline and audit_shot_id. The entire parent plan must pass audit; selected shots' format, resolution, fps, color, sources, and durations must match the audited plan. Source/plan changes require rechecking. Do not rebuild finished episodes without an edit request.

## Local FFmpeg assembly

Working format: 16:9, 1920×1080, 30 fps, H.264/yuv420p, AAC 192k. Preview resolution may be changed in a copy of timeline.json. Preserve proportions: fit=crop fills the frame by cropping; fit=pad preserves the image with padding. For maps and documents, choose the option retaining necessary details.

Images: calm zoom_in/zoom_out or pan_left/pan_right, usually 2–5% scale change per shot, default 4% from settings. motion_easing=smoothstep starts/ends smoothly; linear is available for intentionally constant motion. A subpixel perspective transform, cubic interpolation, yuv444p, and subsequent downscaling replace old quantized zoompan cropping. These measures were technically tested on a synthetic marker; assess each real new asset's smoothness during playback. The local renderer allows up to 20%, but that is a technical limit, not a desired style. Prominent faces, text, and edge objects must stay in frame. Choose motion deliberately for each shot; motion=none is allowed. Video segments default to muted source audio; our narration remains the main track. Do not add music/SFX automatically.

The project's scripts/render_video.py performs repeatable processing through native FFmpeg. It does not find/download assets, invent scenes, generate images, or check legal rights. The agent must first prepare a meaningful editing plan and registry.

Commands from the project root:

```bash
python3 Производство/scripts/render_video.py render --timeline Производство/episodes/istoriya_001/timeline.json --manifest Производство/episodes/istoriya_001/assets/manifest.json --output Производство/episodes/istoriya_001/render/visual_master.mp4
python3 Производство/scripts/render_video.py mux --video Производство/episodes/istoriya_001/render/visual_master.mp4 --audio Производство/episodes/istoriya_001/locales/uk/audio.mp3 --output Производство/episodes/istoriya_001/video.mp4
```

These are technical examples; take languages and paths from episode effective_settings. Mux only the main language: scope.video_language, otherwise languages.primary or source. For Retro use locales/uk/audio.mp3; current delivery=[uk] excludes additional audio files. Historical episodes follow saved scope. Do not create separate additional-language videos. The script saves intermediate shots beside visual_master, reuses them while work is incomplete if inputs are unchanged, and does not overwrite finished output. For an edited plan, save a new result under a new name. Hard cuts, video trimming, and photo movement are implemented. Complex transitions and titles are not included in the current script.

If smooth transitions are needed, FFmpeg provides xfade; inputs must match resolution, pixel format, constant frame rate, and timebase. Overlap shortens the result: account for it in the plan instead of mechanically removing seconds from finished narration. Assemble large videos by scenes rather than keeping hundreds of decoders in one filter graph.

Use the supplied narration as the timeline reference. Verify actual audio/video lengths and synchronization. Investigate differences; do not conceal them through -shortest, speech trimming, or arbitrary track stretching. Only deliver languages and tracks actually requested.

Keep used assets, timeline, timestamps, and recovery data until successful verification and export. Then clean with release_episode_work.py under retro-engineering-check: episode sources, timeline, timestamps, render/, and duplicates are removed; final delivery and selected shared library assets remain. Record that rebuilding from deleted inputs is unavailable. Do not clean incomplete episodes.

Technical documentation: https://ffmpeg.org/ffmpeg-filters.html#perspective

All parts are converted to common limited-TV-range BT.709 before concatenation, preventing brightness-interpretation changes between JPEG, PNG, and video. After normalization, use locales/{primary-language}/audio.mp3, not audio_raw.mp3; Retro's current primary language is uk.

This example belongs to RETRO. Obtain an existing episode's episode_dir and effective_settings from channel.py inspect, not from the latest result folder. Take additional languages and tolerances from the current request.

## Channel color profile

Optional timeline.color_treatment is copied from the merged episode profile's video.color_treatment. For example, `{"preset":"retro_archive","saturation":0.55,"warmth":0.025}` mutes color and gently warms shadows/midtones while preserving brightness. Native FFmpeg uses hue and colorbalance; photos and videos receive the same treatment before final BT.709. Ranges: saturation 0–1, warmth 0–0.10; other presets are rejected. `none` or absent settings preserve normal color. The render cache includes the profile, so old unfiltered parts cannot substitute for the new build. Retro enables this profile; other channels do not inherit it automatically.
