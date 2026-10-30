---
name: retro-engineering-edit
description: "Assemble one video in the selected channel's primary language using native FFmpeg; animate photos smoothly and retain additional tracks as separate audio files."
---

# YouTube: editing

For an existing episode, obtain effective_settings through `Производство/scripts/channel.py inspect`; perform only the requested scope.

## Inputs

Require timeline.json, assets/manifest.json, local sources, the main audio track in the selected video language, and available requested additional tracks (their availability is not required for independent rendering of the main video). Read AGENTS.md, settings.json, and the [assembly guide](references/technical/ffmpeg.md). First check plan completeness and agreement with the current script; if a shot is missing, return to the selected channel's assets skill rather than substitute a random one.

## Assembly

Use the project's Производство/scripts/render_video.py, which calls installed FFmpeg. Render an intermediate silent render/visual_master.mp4; combine it with locales/{scope.video_language}/audio.mp3 or a verified sound/mixes/LANG/audio_mix.wav from outputs.sound into one video.mp4 when background sound is permitted by the profile/request. Preserve clean speech separately. When sound is requested, use the verified sound mix rather than silently falling back to clean speech. For speech-only video, master a separate copy to audio_postprocess targets; a narration premaster is not the final master. Verify final encoded LUFS/true peak after muxing under the sound rules. Do not add background sound to channels without permission. Without scope, use languages.primary or source. Match timeline language and selected audio. Retro currently has source=primary=uk, targets=[]: Ukrainian video only, without additional tracks. Continue old multilingual episodes under their saved scope. Requested additional languages are separate MP3s in delivery language folders; there is one final video.

Take resolution, fps, codecs, and format from effective_settings.video; episode restrictions override project settings. Mute found videos in the visual render. The sound stage may separately extract licensed, checked mechanism Foley without unwanted speech/music and place it in the verified mix; do not enable a clip’s entire source soundtrack. For photos, use smooth zoom in/out or pan with meaningful framing. The renderer uses a subpixel perspective transform with cubic interpolation, full chroma resolution, and smooth motion starts/ends; do not use the old zoompan with its jumping integer window. Take default motion_amount=0.04 and motion_easing=smoothstep from settings. Inspect movement during real-time playback, not only still frames; fix a shaky shot or keep it static. Use implemented hard cuts; do not claim complex transitions or titles are already implemented. Current FFmpeg lacks subtitles support: deliver SRT separately. Do not add music/SFX without request/profile permission.

For Shorts, set timeline `format="shorts"`: the renderer checks effective_settings.shorts.shot_duration_range_seconds (default 2–3 seconds); apply the [Shorts rules](../retro-engineering-shorts/SKILL.md). For long videos, effective_settings.assets.default_shot_duration_seconds defaults to 3–7 seconds inclusive, for both photos and video, including first and last shots. Check timeline boundaries and actual duration after fps rounding; the renderer loads the nearest parent production.json and applies settings_overrides over project settings just as inspect does. Keep timelines and parts inside episode_dir; outside it, general project settings apply. Split long scenes into distinct meaningful shots through the assets stage. Distribute a remainder shorter than the range minimum among neighboring shots while preserving the main track's end.

Duration and scene correspondence matter more than effects. Use the supplied narration and checked timing data. If audio and video disagree, investigate the cause; do not conceal it with -shortest, speech trimming, or track stretching.

The script refuses to overwrite finished files. For a requested edit, assemble a new intermediate result, verify it, and replace current video.mp4 only within that edit's scope. Reuse unchanged inputs and parts while work is incomplete. Preserve sources and recovery data until verification and export. After verifying the requested set, apply retro-engineering-check cleanup: remove working sources, timeline, timestamps, intermediate renders, and duplicates; retain final delivery, selected library assets, compact state, and source records. Rebuilding from deleted inputs is unavailable; explicitly record this in the report. Do not change the script or create new voice jobs for editing.

Pass the channel's optional video.color_treatment into timeline.color_treatment. Supported values are none (or absent) and retro_archive with saturation 0–1 and warmth 0–0.10. The filter applies to photos and video before common BT.709 conversion, preserves brightness, and adds no shake, grain, or flicker. If absent, color remains unchanged. Check the actual image, not just the profile entry.

## Outputs and readiness

One video.mp4 with narration in the channel's main language at the episode root; requested additional MP3s alongside it, including source when source≠primary; intermediate parts in render/. Check ffprobe, duration, and playback. retro-engineering-check performs final comprehensive verification and delivery checks.

Run tests/test_render_video.py after renderer changes or an identified problem; ordinary editing requires checking actual results, not repeating program tests instead.

For retro-engineering, audit 100% of shots before rendering under the current channel rules: exact phrase, depicted person/component/action, framing, no reused original photographs or repeated video ranges. Save pre_render_audit.json with each shot's status and hashes; timeline must include pre_render_audit. Unresolved defects prohibit final rendering.

## Required materials

Read [AGENTS.md](../../../AGENTS.md) and episode effective_settings; request restrictions take precedence. Apply the [stage-specific channel rules](references/channel-rules.md). Read applicable sections of the [current production rules](<../../../Данные проекта/research/current_production_rules.md>).

## Verification

Before final rendering, check actual movement, crop, semantic synchronization, and approved examples. Hashes and counts of unique sources do not establish compositional diversity. Recheck changed shots.

A verified WAV mix must actually contain PCM; normalize_audio.py writes 24-bit PCM for .wav. Separate mix delivery is controlled by scope.sound_mix_delivery, not by the presence of a working sound/mixes file. See current production rules for the export contract.
