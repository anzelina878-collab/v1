# YouTube: thumbnails

For an existing episode, obtain effective_settings through `Производство/scripts/channel.py inspect`; perform only the requested scope.

For retro-engineering, since 9 October 2026, read the channel-specific retro-engineering-thumbnails skill: all three thumbnails are text-free under the permanent cinematic reference. The text/localization instructions below do not apply to Retro; count follows the current request and channel skill; dimensions and verification still apply.

Require current script.txt, selected titles, and channel visual rules. For each scope.thumbnail_languages language (otherwise merged-profile languages.delivery), choose three distinct emotional/visual angles on one topic. Save English briefs, exact localized text, line breaks, and title connections in locales/LANG/thumbnail_prompts.txt.

If the profile permits generation, use the imagegen skill and built-in image_gen for finished thumbnails, one call per variant. To localize a selected image, edit with local reference paths after inspecting the target file and replace the exact caption. Three common compositions may be reused across languages with the correct local text. Do not deliver a grid/prompts as separate finished files or use CLI/API without a user request.

Profile exception: with thumbnails.generation_allowed=false or generator=local_found_media_composite, do not use imagegen for creation, editing, or localization. Following the channel skill, assemble compositions from verified found photos with ordinary local tools; text and corrections are local too. The creative-editing instructions below apply only to channels permitting generation. Count, languages, actual files, and visual verification remain mandatory.

Illustration, era, person/machine, object, and palette follow the selected channel. Do not transfer ancient costumes to celebrities or machines. Use short mobile-readable text, a clear main object, and strong contrast, without invented facts or false “archival” documents. Real people and technology must be recognizable and fit the topic.

Save selected images in the project and inspect each: text, language-specific letters, faces/hands or machinery, important details, margins, and small-size readability. Fix only the defective variant using a profile-permitted method. Export 16:9 at thumbnails.width × height or higher; every locales/LANG has exactly three final thumbnail_01/02/03 files with actual extensions. Native FFmpeg may perform technical resizing/formatting for delivery; creative edits and captions use image_gen only when generation is allowed, otherwise local compositing/text.

For idea/prompt-only requests, do not generate finished images. After verification, remove unnecessary intermediate variants from the current episode. Record channel association and paths in production.json.
