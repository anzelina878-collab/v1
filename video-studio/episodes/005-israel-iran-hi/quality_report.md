# Hindi Israel–Iran edition: verification

Status: technically verified; all planned and encoded scene samples visually reviewed.

- Full HD 1920×1080, 30 fps, 21:52, 39360 frames, 185 scenes.
- Complete video and audio decode: passed.
- Supplied voice preserved without narration edits, speed changes or replacements. Encoded/source audio correlation at zero offset: 0.999909191. Original audio and script checksums verified.
- 97 photo/card holds checked for unwanted movement after their entrance.
- 63 documentary/3D/map endings checked for freezes and empty black tails. Documentary excerpts are normal speed and never loop or use last-frame padding.
- 13 3D scenes compared against three exact native bank poses each: 720 directly rendered poses per 24-second revolution. No optical flow.
- All 11 chapter title regions checked in the actual encoded movie at the reviewed Hindi audio cue.
- All 185 scenes reviewed in eight planning sheets and eight encoded sheets; a 90-second encoded pilot was also checked. This is sampled visual review, not continuous full-length playback/listening.
- All active episode text is free of Cyrillic. Hindi shaping and font coverage checked. Original source-language labels/logos inside documentary footage remain documentary source material.
- Ukrainian original and approved source media preserved. No new generated voice, AI video, AI photos, or unverified inventory figures.
- Source archive includes actual licensed media, original model geometry/attributions, Hindi fonts, scene/timing data and rendering code. Fresh portable rendering is recorded separately in `output/qa/portable-source.json`.

Movie SHA-256: `9a6b3142c14b7834e22faafd7f6ff23c03231aef646bb01023e08f56a4129013`
Movie bytes: 160417588

Relevant source ledger: `SOURCES.md`. Prior documentary/date/model-family qualifiers are retained. Raw ASR contains recognition errors and is only a timing aid; it is not shown as subtitles.
