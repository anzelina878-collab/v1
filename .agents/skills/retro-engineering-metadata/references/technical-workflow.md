# YouTube: metadata

For an existing episode, obtain effective_settings through `Производство/scripts/channel.py inspect`; perform only the requested scope.

Require current script.txt, plan.md, final assets/manifest.json, and the selected channel's editorial metadata rules. Create locales/LANG/metadata.txt for each language in scope.metadata_languages; if absent, use merged-profile languages.delivery; an empty list excludes metadata. Do not promise finished voiceover before it is ready.

Each file contains a recommended title and two alternatives (within metadata.title_max_characters, preferably 55–90 characters when natural), a description, and separate comma-separated tags (within tags_target_max_characters). For long video, follow current channel formatting: first paragraph — question and content; second — specific questions about the mechanism and limitations; third — viewer question and CTA; then “Розділи:” with timestamps, one line of three hashtags, and a separate required-attribution block for each used asset. Verify timestamps against final editing and synchronized subtitles/speech data; start at 00:00, keep ascending order and actual semantic boundaries. Preserve author, source, license link, and modification information. Write technical working instructions in English; published fields use the version's language.

Localize meaning and search phrases naturally. Do not assign an es/pt region without user instruction. Titles and covers must promise the same verified material the script explains. Do not add facts, numbers, quotations, or sensational claims for clicks. Specialized sources (Scripture, filmography, technical documents) are determined by the channel and actual script.

Check lengths, diacritics, names/models, sources, and all required fields. Finalize attribution after asset selection; if metadata is prepared before searching, mark attribution incomplete. Metadata does not start script translation, voiceover, or thumbnail generation.
