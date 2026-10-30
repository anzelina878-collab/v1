---
name: retro-engineering-thumbnails
description: "Create three cinematic, text-free Retro / PASTWORKS thumbnails following the approved reference: a prominent object, spatial depth, expressive lighting, and accurate engineering."
---

# Retro Engineering: thumbnails

Apply only to retro-engineering / PASTWORKS. Read the [channel rules](../../../AGENTS.md), merged profile through channel.py resolve, current script, research, and episode scope. Read the [visual style and reference](references/styles.md); this is the user's permanent style from 9 October 2026, replacing the earlier 3/6/9 selection.

## Composition

Prepare three distinct angles on one topic in a consistent cinematic, photorealistic style. Show a recognizable machine, mechanism, or structure prominently, with authentic materials and details, environmental depth, directional lighting, and clear scale. The image creates a clear visual question answered by the title and first 20–30 seconds. Choose angles suited to the topic: scale, hidden component, action, or result; no fixed numbering assignment is required.

All thumbnails have no added text, labels, arrows, logos, frames, or YouTube interface. The title stays in metadata. The three variants differ in composition and subject emphasis; changing the crop, filter, or brightness of one image does not make a new variant. For infrastructure, show structural scale; for a compact device, use an expressive object scene or internal component. Do not transplant VHS, rockets, or dams into unrelated topics merely to resemble the example.

The device's purpose must be clear at phone size without a caption: show it with a recognizable result, operating environment, or related object. For a pacemaker, convey its connection to the heart through a verified anatomical model or accurate device/lead placement. See references/styles.md for the complete criterion and episode 4 examples.

## Sources

First perform a thorough Google search for real photos and videos, then verify original sources, technical geometry, and usage terms. Prefer an expressive found scene; when combining real materials, create a coherent photorealistic composite without visible dividing strips. Do not invent construction, patents, tests, or explosions for clicks.

Built-in image_gen is allowed only as a last resort for a specific missing image after a thorough search. Read the imagegen skill before calling it; record the sought scene, checked sources, rejection reasons, and exception justification in search_log. Approval of a new style is not general permission to generate. The one-off authorization to generate covers for episodes 1–3 on 8 October 2026 does not extend to other episodes. Preserve illustration provenance internally under the profile.

## Verification and delivery

Apply the technical mechanics in [retro-engineering-thumbnails](references/technical-workflow.md) and the current root AGENTS.md. For Retro, the general skill's text and localization requirements are replaced by the no-text rule. Inspect each variant at full size and around 320×180: recognizable object and intrigue, plausible details, lighting that preserves important components, and meaningful differences between variants. Check for added text, third-party watermarks, and copied interface elements.

Long-video thumbnails use 16:9, merged-profile dimensions, and three separate thumbnail_01/02/03 files with their actual extensions in locales/LANG. Language-independent compositions may serve several requested locales; each receives three finished files. An explicit request for fewer or additional variants changes that episode's set; save all requested variants in outputs.thumbnails and scope, then export with delivery.py. Episode 4 requested five; the general default remains three.

Keep working files, prompts, inputs, sources, and checks in episode_dir under Производство/episodes/. After verifying the requested finished set, run delivery.py and link to clean deliverables in Результаты. Configuring rules does not start production or remake previous files.

For Shorts, apply [retro-engineering-shorts](../retro-engineering-shorts/SKILL.md): one vertical 9:16 text-free cover per video. Lighting, depth, and object recognition follow the shared reference; adapt composition to vertical framing and the Short's independent story.

## Required materials

Read [AGENTS.md](../../../AGENTS.md) and episode effective_settings; request restrictions take precedence. Read and follow the [technical procedure](references/technical-workflow.md) within the profile. Read applicable sections of the [current production rules](<../../../Данные проекта/research/current_production_rules.md>).

## Verification

Check the approved style, actual generation restrictions, and script promise. Editing one thumbnail does not change the others or frozen video.

Preserve variant numbers in targeted edits: thumbnail_03.png remains thumbnail 3 even when it is the only selected file. For an arbitrary filename, store the outputs.thumbnails.LANG item as {"number": 3, "path": "locales/LANG/new_cover.png"}. Preserve other variants; an extension change replaces only that number's previous encoding. If attribution changes, prepare metadata using its skill and record scope.metadata=true, the required scope.metadata_languages, and outputs.metadata. With requested_stage="thumbnails", this explicitly included output exports with the thumbnails; a missing selected file blocks delivery. See the current rules' tool contract for schema and restrictions.
