# Hindi timing

The user supplied the completed Hindi narration and referred to the translation already prepared in chat. The Ukrainian script is the preserved semantic source. `anchors.json` maps its paragraph IDs to reviewed Hindi speech onsets; unanchored interior boundaries interpolate between neighboring semantic anchors. The source and target retain the same paragraph order. `chapter-cues.json` records reviewed spoken category names or the actual first phrase where a printed heading is not narrated.

ASR JSONL files are raw editing aids and contain recognition errors, particularly proper names. They are not subtitles, do not alter the supplied voice, and are not used verbatim on screen. Weak initial recognition windows were checked with targeted re-recognition; the last portion was rerun with a full-context higher-beam transcription. On-screen text is manually localized in `translations.py`.
