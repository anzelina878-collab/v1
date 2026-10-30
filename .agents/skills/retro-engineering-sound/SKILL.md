---
name: retro-engineering-sound
description: Mix permitted RETRO / PASTWORKS music and effects with speech-relative balance while preserving Ukrainian speech intelligibility.
---

# RETRO sound

Read [AGENTS.md](../../../AGENTS.md), effective_settings, and episode scope. Read the applicable sound and verification rules in the [production standard](<../../../Данные проекта/research/current_production_rules.md>). Produce only sound permitted by the request or profile; an available library does not expand the request.

Use the user-supplied clean narration and verified timing data. Preserve the original recording. Select licensed music and effects only within the requested scope; retain sources and terms. No purchases without explicit authorization.

Apply effective_settings.sound: intelligible narration leads every scene. Prepare clean narration using sound.narration (−19 LUFS target, −20…−18 before mastering); preserve it separately. Set music relative to speech on matching active speech windows: 15–20 dB below voice during narration (target 18), with automatic sidechain ducking; use the general 12–18 dB reference outside speech as appropriate. The old fixed −33 LUFS/+2 dB rule is superseded; background_base_lufs/background_target_lufs are only a starting level. Do not accumulate gain or raise music to meet master loudness.

Create a cue sheet with time ranges, exact action/phrase, licensed source, music changes, Foley/SFX, J/L cuts, risers/tails, silence and level automation. Outside planned complete silence, support each cut with appropriate sound continuity or a light effect; sync permitted graphic appearances to light whoosh/swoosh/pop/click. This does not authorize text or infographics prohibited by the channel. Highlight visible actions with authentic synchronized Foley; isolate and license-check source audio rather than enabling a found clip's entire soundtrack. Shape music to opening, key ideas and climax, without masking speech or constant sonic density.

Plan selected complete 0.5–1 s silences before/after key phrases in natural speech gaps; mute all layers including reverb. Never cut words; adding time requires synchronized timeline/subtitle updates. Use J/L cuts and risers/reverb tails intentionally without crossing complete silences or disrupting Shorts replay.

Keep working mixes in the episode's sound/ directory and clean speech separately. Normalize the final mix through Производство/scripts/normalize_audio.py using the episode's audio_postprocess (default −14 LUFS, ceiling −1 dBTP); for clean narration used as a mixing input pass sound.narration.premaster_target_lufs instead. Standalone finished speech delivery uses audio_postprocess master targets; preserve a separate premaster when also needed for mixing. Voice premaster loudness is not an independent constraint on the voice after whole-mix gain. Final encoded master must measure within sound.mastering.accepted_lufs_range and at or below max_true_peak_dbtp. Re-measure after mux/encoding; lower the limiter ceiling and re-export from the source mix if codec peaks exceed the limit. After muxing, check the final AAC/MP3 for peaks, loops, clicks, synchronization, and speech balance. Metrics do not replace listening; record unavailable listening checks in quality_report.md. After verifying delivery, follow retro-engineering-check for cleanup.

For standalone sound requests: requested_stage="sound"; scope.sound_languages selects mix languages (an empty list excludes them); outputs.sound.mixes contains {"uk": "sound/mixes/uk/audio_mix.wav"}. Delivery is LANG/микс.wav (or the actual .mp3/.m4a); do not replace clean speech with a mix. In a full video episode, the mix is an editing input; deliver it separately only with scope.sound_mix_delivery=true. normalize_audio.py chooses encoding by extension: WAV → 24-bit PCM, MP3 → MP3, M4A → AAC; other extensions are rejected. For final mixes pass effective_settings.audio_postprocess explicitly through --lufs, --true-peak, and --lra; the script does not load the episode profile itself. With enabled=false, skip normalization. Verify format, duration, and full decoding, not just the filename.

## Automatic inclusion

Sound is authorized by default for subsequent requested video episodes and separately requested Shorts under enabled_for_video/enabled_for_shorts. Apply this skill without another reminder; explicit request restrictions and saved overrides take precedence. Record stage readiness and outputs.sound.mixes before the video is declared ready. This default does not itself request production or additional Shorts.
