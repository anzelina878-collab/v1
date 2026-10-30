---
name: retro-engineering-shorts
description: "Create a pair of standalone Retro / PASTWORKS visual Shorts: real mechanisms, vertical edits without text, text-free covers, and separate SRT files."
---

# Retro / PASTWORKS: two visual Shorts

Read the [channel AGENTS.md](../../../AGENTS.md), [current rules](<../../../Данные проекта/research/current_production_rules.md>), and merged profile through `python3 Производство/scripts/channel.py resolve --channel retro-engineering`. This skill defines a separate Shorts format; do not transfer the long episode's introduction, duration, or three-horizontal-thumbnail requirements to it.

## Request and story pair

By default, a Shorts request means **two standalone videos** on the specified episode's topic. An explicit user count takes precedence. Configuring rules does not start production; a full long episode does not add Shorts without a request or `scope.shorts`. Limit script/plan-only requests to those materials.

Verify that sources belong to the channel and that the script and hash are current. Use the specified episode's facts, research, source footage, and narration. Shorts can be prepared before the long video is complete if the topic is specified and facts are checked. Do not select an arbitrary episode by file modification time.

Choose two different questions, each with a visible answer. A useful pair: 1 — unexpected action / hidden principle; 2 — limitation / unusual solution. These guide selection rather than requiring a breakdown story. Each has its own opening shot, development, climax, and ending. Do not split one explanation into “part 1” and “part 2,” retell the first in the second, or make a truncated trailer without an answer.

Before final scene alignment, record for each in `shorts_plan.md`: question, observable effect, answer, verified factual source, found visual evidence and ranges, distinction from the other Short, duration plan, first/last phrases, visual changes during seconds 5–15, and end → beginning join. If the key action cannot be shown, find another viewpoint or independent story. Attractive general views do not replace evidence.

## “Living Mechanics” style

Recognition comes from real materials and editing: a close detail of an old device, metal texture, motion from the first frame, transition from the whole to a working component, and a visible result. Preserve the profile's light archival grading, readable detail, and natural brightness. Lighting and shot size direct attention; no artificial flicker, shake, or decorative assortment of gears.

Use vertical 9:16, 1080×1920, 30 fps. The main component is prominent and stays clear of interface zones at the edges. Prefer suitable vertical sources or separately planned crops for each horizontal shot. Check the beginning, middle, and end of movement: cropping must not remove the tape, lever, part trajectory, or result. If the mechanism does not fit, find another angle; a full frame with neutral padding is allowed when otherwise the explanation is lost. Do not stretch machinery or generate extended edges.

**No added text in video:** no burned-in subtitles, headings, numbers, labels, CTA, PASTWORKS watermark, or text intro. Do not replace text with arrows, drawn diagrams, or cards. Markings physically present on real devices are allowed, but comprehension must not depend on reading them. Do not remove third-party attribution/watermarks to satisfy this rule; select a suitable source.

The visual causal chain should be understandable with sound off: what moved, what changed, and what resulted. Narration clarifies causes and facts not directly visible; do not promise that complex physics is fully explainable without speech. Do not pass off a test of a different device as this device's test. If a story needs a lengthy verbal caveat, prefer one more visually suited to Shorts.

## Hook, story, and pacing

The inherited Short target is 20–30 seconds, about 25. Use a complete excerpt from the supplied narration; do not speed up speech or rewrite the finished story to meet this target. An explicit user duration overrides the template.

From the first frame, show real unusual action or a prominent detail; the first spoken phrase immediately states the main conflict, before/after contrast, or unexpected question without preamble. Speech begins with the action. Within 1–2 seconds, viewers already see and hear the intrigue, confirmed by a strong visual focus.

Show the oddity → orient the viewer in the device → reveal component action → show the answer/limitation. Do not narrate invention history before the action. The last shot gives the result; do not end with “the answer is in the full video.” Metadata may link to the long episode if it exists; do not spend the ending on a subscription request.

By default, each shot lasts **2–3 seconds** (shorts.shot_duration_range_seconds from episode effective_settings), including first and last. Changes of angle, scale, working component, or visible result add information. Pay special attention to **seconds 5–15**: no lingering overall views or re-explaining what is already clear. Achieve changes every 2–3 seconds through real shots, without added text, infographics, or decorative effects. Cut on action and preserve orientation within the mechanism; do not speed it up or distort physical meaning for rhythm. If the action is unclear at this pace, choose a clearer segment or narrow the story. For Shorts, this range replaces the general 3–7 seconds in assets, editing, and checking skills. Use photos for necessary facts/details with calm directed motion; do not build the whole Short from similar overall photos. Adjacent nonoverlapping segments from one source are allowed under the channel's explanatory-sequence rule. No exact repeats or artificial action loops inside the file.

**Seamless loop:** after a standalone answer, end with a phrase that logically leads into the first phrase on replay. Choose last/first shots with compatible movement, composition, or causal connection; leave no final pause, fade, title card, or CTA. Check the speech, image, and background-audio transition. The loop occurs between playbacks: do not duplicate the beginning or repeat source ranges inside the file. The first viewing must provide the complete answer.

Within each Short, use an original photograph in at most one shot: a different crop, zoom, color, or file copy is not a new image. If a shot is missing, search for new real video/photos; after a documented exhaustive search, a rare archival-style illustrative reconstruction is allowed with provenance in internal manifest/search_log and no public “reconstruction” label in video, narration, cover, or description. Do not present a reconstruction as archival evidence or build the entire Short from such images.

Within each Short, repeated and overlapping original-video ranges are prohibited, including copies and processed versions; crop, speed, or color do not make a range new. Also replace different moments showing the same action with no new meaning.

If narration mentions a specific person, show that actual person synchronously in verified video or a portrait; a random face or mechanism shot is unsuitable. Check every mention against text and timeline. For repeated mentions, find another unique image of that person; the single-use photograph rule remains.

## Real footage, speech, and subtitles

Follow [retro-engineering-assets](../retro-engineering-assets/SKILL.md) for search and rights: Google → real video → photos; generation only as a documented last resort, including covers. Found materials must match the model and action. Save all sources and selected ranges in manifest/search_log.

Use only the supplied finished narration or a complete excerpt from it. Retain the original audio, exact used text, checked timing data, and cut ranges. Do not create new speech or change its speed. Music and SFX require the current project scope; do not inherit permissions from another project.

Prepare a separate UTF-8 SRT for each requested Short in the language of the supplied narration. Use verified timings of the actual selected speech; rebase cuts to the Short timeline, remove omitted words, and preserve audible order. Do not invent timestamps.

Split subtitles into short meaningful phrases, normally up to two lines; do not split names, numbers from units, or tightly related words. Check Ukrainian terms, cue starts/ends, overlaps, and duration bounds. Deliver SRT for separate upload and viewer activation: **do not burn it in or add a default-enabled subtitle track to MP4**. Other languages require a request.

## Testing the retention hypothesis

Using available analytics from newly published Shorts, compare the 20–30-second format with the previous 40–50-second format: stayed-to-watch share, average view duration and percentage, seconds 5–15, completions, and replay indicators. Account for topic, traffic source, and comparable time since publication; increased average percentage alone does not prove improved storytelling. A seamless loop is a hypothesis to test, not a promise of retention above 100%. Do not claim a confirmed effect without analytics. Configuring rules does not authorize publication or monitoring.

## Language-independent covers

One separate vertical 1080×1920 cover per Short, without added letters, numbers, logos, captioned frames, or CTA. Adapt the shared [cinematic thumbnail reference](../retro-engineering-thumbnails/references/styles.md) to vertical framing and the Short's standalone story; three horizontal variants are unnecessary. Both covers share “Living Mechanics”: a large accurate object/component, expressive lighting, visible unusual action or relationship between parts, and minimal distracting background.

Prefer a strong sharp frame from the Short itself; if necessary, use a found photo or truthful composite without invented machinery or false scale. The two videos need distinct visual hooks, not one frame with different colors. The cover promises action actually shown. It must communicate at small-screen size without reading, including device purpose through its real environment, action, or related object. If proposing a video frame for selection in YouTube, record its timestamp in the working plan; a separate JPG does not mean the platform will automatically apply it.

## Assembly, verification, and delivery

Synchronize shots with exact phrases and actions rather than spreading them across a paragraph. A whole paragraph in scene_text is not verification: show a component when described, the actual person when mentioned, and the result when discussed. Compare each window with actual speech and timestamps before rendering and in the finished video.

Work in `episode_dir` returned by channel.py. For an existing episode, update the requested scope without reinitializing it. A new Shorts request permits `init --stage shorts`; configuring this skill alone does not. Working directories: `shorts/short_01/` and `shorts/short_02/`, containing script, sources/links, timeline, speech/timestamps, `short.mp4`, `cover.jpg`, `metadata_uk.txt`, and `subtitles_uk.srt`. Shared episode sources may be reused through manifest references without copying.

Assemble using native `Производство/scripts/render_video.py` under [retro-engineering-edit](../retro-engineering-edit/SKILL.md), with timeline `format="shorts"`, width=1080, height=1920, fps=30, and profile color. The format marker activates shot-duration checks against effective_settings.shorts.shot_duration_range_seconds. The renderer finds episode production.json above the Shorts folder and applies settings_overrides; keep timelines and parts inside episode_dir. Horizontal defaults and the general 3–7-second range are overridden here. Prepare required offset/dynamic crops with native FFmpeg in production and record transformations in manifest; do not assume a standard center crop preserves the mechanism. Use H.264/yuv420p and AAC; duration matches complete speech with no hidden truncation.

Watch both videos fully with and without sound, and inspect covers at phone size. Check visual hooks, standalone answers, distinct stories, narration/image correspondence, absence of added text, smooth movement, mechanism-preserving crop, SRT synchronization, and encoded audio. Technical checks: 9:16, 1080×1920, playback, 20–30-second duration unless otherwise requested, and shots within effective_settings.shorts.shot_duration_range_seconds (default 2–3 seconds) in timeline and after fps rounding. Record actual minimum/maximum shot duration. Separately verify intrigue in the first 1–2 seconds and every visual change during seconds 5–15. Play each Short twice consecutively without a pause: final speech leads into the opening, image/audio joins do not jump or drop, and the answer is clear on the first viewing. Confirm two MP4s, two JPGs, two SRTs, and two metadata files. Record actual checks and limitations in `quality_report.md`; a contact sheet does not replace viewing.

In `production.json`, save `scope.shorts=true`, `shorts_count=2`, and `shorts_languages=["uk"]` (or the explicit request), and two `outputs.shorts.items` entries with `directory`, `video`, `cover`, and optional `audio: {"uk": "..."}`. Paths are relative to episode_dir; `directory` contains `metadata_uk.txt` and `subtitles_uk.srt` so delivery.py can find them. Mark done only after verifying the mandatory set; the exporter does not verify its completeness for the author.

After verification, run `python3 Производство/scripts/delivery.py --channel retro-engineering --number N` (or `--name NAME`). Directly in `result_dir/uk/`, deliver `шортс-01.mp4`, `шортс-02.mp4`, `обложка-шортс-01.jpg`, `обложка-шортс-02.jpg`, `субтитры-шортс-01.srt`, `субтитры-шортс-02.srt`, `мета-шортс-01.txt`, and `мета-шортс-02.txt`; separate audio only when included in requested delivery. Keep working materials in production until verification and export; then apply general cleanup rules and record that deleted inputs cannot be used for rebuilding. Publishing and setting platform covers are outside local delivery.

Mandatory user clarification, 9 October 2026: before final rendering, verify 100% of selected shots against exact phrases, sources, framing, and uniqueness; save pre_render_audit.json with status passed and script/timeline/manifest hashes. Unresolved defects block rendering. See current channel rules for the full procedure. The 20 October 2026 sound rules supersede the old +2 dB adjustment: follow effective_settings.sound and the sound skill, with relative music balance and sidechain ducking; no cumulative gain.

## Required materials

Read [AGENTS.md](../../../AGENTS.md) and episode effective_settings; request restrictions take precedence. Apply the [stage-specific channel rules](references/channel-rules.md). Read applicable sections of the [current production rules](<../../../Данные проекта/research/current_production_rules.md>).

For additions/targeted edits, preserve each Short's number in outputs.shorts.items[].number; if absent, use the short_02/02 folder number, then previous list order. Do not renumber existing videos. freeze.video protects delivered MP4s; a new Short is allowed with scope.shorts=true without replacing the long video. Do not automatically restore receipt-listed files deleted by the user.
