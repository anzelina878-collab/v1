# YouTube: finding and preparing visuals

For an existing episode, obtain effective_settings through `Производство/scripts/channel.py inspect`; perform only the requested scope.

## Inputs

Require the supplied script, finished narration and verified SRT/timings for final scene boundaries. Preliminary planning needs only the text. Determine language and duration from the actual supplied materials, preserving originals. Read settings and the visual profile, treating inherited engineering restrictions as pending adaptation.

## Scenes and assets

Check assets.generation_allowed and generated_fallback_allowed before generating visual assets. When disabled, find licensed alternatives and document gaps. Visual generation settings do not authorize changing the supplied narration.

Check timestamp completeness and agreement with audible speech. Divide the supplied story into meaningful scenes and shots. Use the actual narration as the timeline reference; preserve the original recording and do not cut on every word.

For each meaningful scene, begin with a broad Google query without site: or an allowed-domain list; inspect general, image, and video results. Then open suitable archives, museums, historical/creator sites, photo collections, YouTube, and stock libraries. Do not reduce the search to Pexels/Pixabay. Verify the original page, terms, and asset itself; a search result is not a verified source. Search in Russian, English, and the local language when needed. Save attempts, results, and rejection reasons. Every cut adds visual information. By default, show an exact image or video segment once; zoom/pan does not make a repeated photo a new source. Aim for ≥90% distinct shots; meaningful returns to a place/person with different angles/actions are allowed. Choose nonoverlapping segments with genuinely different content from a source video; separate uses across different scenes by at least 90 seconds. Adjacent nonoverlapping segments in one explanatory sequence are allowed with justification under current channel rules. A short test uses each source once. If variety is insufficient, keep searching or generate permitted missing visuals; do not fill time by cycling old shots.

Confirm the specific asset's usage terms, author, and required credit. If terms prohibit use or are unknown, independently find an alternative. Do not ask whether the first questionable video is acceptable. Research YouTube without bulk downloads; download only a selected permitted source or segment. A short edit does not establish rights.

If several meaningful search variations fail to cover the exact scene, use an appropriate object, place, or reconstruction; when necessary and only if the profile permits it, generate the missing image with built-in image_gen under the imagegen skill. For requested video production this is part of the stage, without separate approval for every scene. Save images in assets/generated/ and prompts in the registry. Do not present them as archival material. The channel defines the material's role: archive, modern location footage, object, diagram, or artistic reconstruction. Do not pass one type off as another.

## Outputs

assets/downloaded/, assets/generated/ only when generation is allowed, assets/search_log.json, assets/manifest.json, and timeline.json. Registry fields: unique ID, kind=image/video, path relative to manifest.json, source, author, usage basis, attribution, visual_role, style_fit with a brief rationale, and usage_status=approved after verification. For generation, include prompt and scene connection.

In timeline.json, use settings width/height/fps; shots include start/end in the main video track, asset_id, scene_text, motion, motion_amount, and fit; video also includes source_start in the original. First start=0, every next start equals the previous end, and final end matches audio. Record audio_language for the main video. Include format="long" or format="shorts", script_path, pre_render_audit, and each shot's unique id under the editing skill's schema. Every shot's end-start and fps-rounded duration must remain within its format range from effective_settings, including the first and last. If the final remainder falls below the minimum, redistribute neighboring boundaries; do not trim/stretch narration or pad with repetition/black frames. Explain long scenes through several meaningful sources/angles. Calm photo motion is typically 2–5%, default 4%, with motion_easing=smoothstep from settings; video uses motion=none. Choose fit=crop or pad by content.

Before handoff, check repeats by asset_id, file hashes, and overlapping source_start/end; record unique-shot share and justified returns. Assess style and phrase correspondence from images, not filenames alone.

Readiness: all time windows have suitable accessible files, sources and attribution are recorded, and no accidental gaps or anachronisms remain. Do not render final video here. The neighboring [retro-engineering-edit](../../retro-engineering-edit/SKILL.md) defines validated timeline schema and build commands.
