---
name: retro-engineering-check
description: "Verify the selected channel's requested deliverables, profile-specific facts, video, audio, metadata, and thumbnails; clean up episode working files."
---

# YouTube: deliverable verification

For an existing episode, obtain effective_settings through `Производство/scripts/channel.py inspect`; perform only the requested scope.

## Inputs and verification boundaries

Read AGENTS.md, settings.json, and production.json if present. Verify the actual requested result. A script-only request does not require a full video package. A video/test-video request requires the profile's dubbing tracks, subject to current request restrictions, alongside the video in the channel's main language. Only an explicit user language restriction permits an exception; the agent must not reduce the set independently. Check full episodes against the list below. Report unavailable checks honestly; do not mark them passed.

## Full episode

- Verify the supplied narration against the actual final cut: beginning, middle, end, phrase completeness, duration and scene alignment. Check provided or manually aligned subtitles against audible speech. Missing timing or listening checks remain unverified.

## Shorts

Apply [Shorts verification](../retro-engineering-shorts/SKILL.md): 20–30 seconds; shots within effective_settings.shorts.shot_duration_range_seconds (default 2–3 seconds) in timeline and after fps rounding; intrigue visible and audible from the start; visual changes during seconds 5–15; a complete answer and seamless end → beginning transition. Watch each entire video with and without sound, then play it twice consecutively to check the join; record actual results. The general 3–7-second range above applies to long episodes. Verify separate SRTs, covers, and metadata for requested counts/languages; do not burn in text. Explicit requests take precedence.

## Corrections and delivery

Fix routine defects through the relevant skill without another question when within the current request. Redownload a damaged file; do not restart synthesis for a download defect. Correct only the affected thumbnail for an incorrect caption. Do not automatically add substantially new paid work to verification; for external problems, identify the exact cause and required action.

Distinguish actual viewing/listening from automated checks in the report; a static contact sheet does not prove absence of shake.

Save quality_report.md with checked files, actual durations, found/generated shot counts, image/audio/localization checks, corrected problems, and remaining limitations. Update production.json to reflect actual state. Link to finished materials and briefly report results. Mark a full episode done only when all required outputs truly exist and are ready; explicitly list missing items for partial results. Do not publish automatically.

## Cleanup after successful verification

Once all requested results are ready and quality_report.md is saved, export finished files through delivery.py and verify the delivery receipt. Before deletion, select references and templates genuinely useful for future production and move them into Данные проекта/research/ or Данные проекта/templates/. Do not retain the entire previous episode as a reference. A final file used as a reference may be linked to its sole copy in Результаты.

Then run `python3 Производство/scripts/release_episode_work.py --number N --apply` (or `--name NAME --apply`). Without --apply, it performs a preflight only. The script requires a nonempty stage list with successful done/completed/passed statuses, no blockers, and a completed overall status; unknown, blocked, failed, or other incomplete statuses prohibit cleanup. It then verifies final-delivery SHA-256 hashes and agreement between current selected outputs and the export, and removes working sources, old versions, raw speech, intermediate renders, and duplicate final files. The episode folder retains compact production.json, delivery_manifest.json, source records, retention_manifest.json, and quality_report.md. Settings, tools, selected references, and the shared library remain. Explicitly state in the report that rebuilding from old inputs is no longer possible; cleanup must not improve verification status or limitations.

Do not apply this cleanup to incomplete, stale, or blocked work: retain inputs, timestamps, request/job_id, and checkpoints needed for continuation. If the user deleted final delivery, do not restore it automatically or delete the last working copy; establish user intent first. An identically named episode from another channel does not satisfy a missing file.

After cleanup, verify the final set, selected references, and shared library remain intact; record actual freed space. Give the user links to finished files in Результаты.

For retro-engineering, audit 100% of shots before rendering under the current channel rules: exact phrase, depicted person/component/action, framing, no repeated original photographs or repeated/overlapping video ranges. Save pre_render_audit.json with each shot's individual status and hashes; timeline must contain pre_render_audit. An unresolved defect prohibits final rendering.

## Required materials

Read [AGENTS.md](../../../AGENTS.md) and episode effective_settings; request restrictions take precedence. Read applicable sections of the [current production rules](<../../../Данные проекта/research/current_production_rules.md>).

## Verification

Record decoding, inspection of control frames, continuous viewing, and listening to the final file separately. Leave unavailable checks unverified. A new thumbnail request or project configuration does not authorize changes to frozen video.

## Exporting individual stages and amendments

Follow “Production tool contract — 14 October 2026” in the current production rules. requested_stage describes the current request; scope defines restrictions; historical outputs are not a new request. Export preserves unaffected deliverables. For script-only requests, save outputs.script="script.txt": delivery is LANG/сценарий.txt. Audio, metadata, thumbnail, and Shorts languages come from their separate scope lists; an explicitly empty list means no corresponding output.

Save an amendment to a cleaned episode in its working folder and record new outputs for the current request. Do not delete or manually edit old delivery before export: delivery.py first checks it against its receipt, then adds verified changes. After export, storage_state becomes released_with_amendment_work; missing old inputs remain missing. After successfully checking and exporting new files, clean only working materials with the usual release_episode_work.py. An unexported amendment blocks cleanup. Do not automatically restore delivery deleted by the user.

After cleanup, retain research_notes.md for the long episode and nested Shorts: these are source records, not disposable media inputs. Beyond selected files, cleanup checks existing explicitly declared final outputs; an undelivered amendment prevents deletion. For standalone sound, check LANG/микс and its actual codec. For targeted thumbnail replacements, verify numbering and removal of the previous extension for that number only. Receipt and delivery are switched with rollback on receipt write/replacement failure; unexpected process termination between file operations is not confirmed export.

## Sound design verification

For requested sound/video work follow the 20 October 2026 sound rules and effective_settings.sound. Check the cue sheet and rights; synchronized Foley/graphic cues, sound continuity at each cut outside planned complete silence, narrative music changes, J/L cuts, risers/tails and selected complete 0.5–1 s silences without truncated speech. Measure the actual final encoded audio: −14…−13 LUFS and true peak ≤ −1 dBTP by default, including AAC inside MP4. Measure music/voice gaps on matching active speech windows (15–20 dB, target 18), plus ducking and pumping by listening. Clean narration −20…−18 LUFS applies before final mastering, not independently after master gain. Record actual listening on headphones, phone/small speaker and TV/comparable speakers separately, with unavailable checks unverified. Configuration-only work requires settings/rule consistency checks, not episode rendering or delivery.
