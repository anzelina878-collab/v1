# ARSENAL 360 / शस्त्र 360 — Hindi episode 1

Separate Hindi adaptation of the approved USA–China **soldier equipment** episode. Ukrainian originals are preserved. The supplied Hindi script and voice are immutable; they are neither rewritten nor sped up. Output is 1920×1080, 30 fps, 19:26.33.

## Render the supplied edit

Requirements: Python 3.11+, FFmpeg/ffprobe, `Pillow` with RAQM support, `numpy`. All required fonts and selected media are included in the source ZIP. No Blender, external footage library, ASR download, or raw M249 geometry is needed to render the prepared edit.

From the extracted `video-studio` directory:

```bash
python episodes/001-usa-china-hi/check_episode.py
python episodes/001-usa-china-hi/render_episode.py --work /tmp/arsenal-hi-render --preview
python episodes/001-usa-china-hi/render_episode.py --work /tmp/arsenal-hi-render --pilot 90 --output /tmp/arsenal-hi-pilot.mp4
python episodes/001-usa-china-hi/render_episode.py --work /tmp/arsenal-hi-render --output /tmp/final_video_hi_v1.mp4
python episodes/001-usa-china-hi/check_episode.py --video /tmp/final_video_hi_v1.mp4 --work /tmp/arsenal-hi-render
```

Optional independent workers: run `--worker 0` and `--worker 1` against the same work directory, wait for both to finish, then run the normal command to assemble. Do not run assembly while the workers are active. Cache keys include the renderer, scene configuration, fonts and source media; changes trigger rebuilding.

## Rebuild the timing plan

`python episodes/001-usa-china-hi/build_episode.py` reproduces `episode.json` from the preserved scripts, completed word alignment, reviewed paragraph correspondence and original edit. Audio-derived timing takes priority over approximate chapter hints in the supplied text. `chapters.hi.txt` contains the resulting chapter positions.

The script expands 186 Ukrainian spoken paragraphs into 226 Hindi paragraphs. `paragraph_translation_map.json` records their reviewed correspondence. `alignment/report.json` distinguishes exact ASR token agreement from editorial review: imperfect ASR spelling is not a reason to rewrite supplied narration. Eight reviewed gaps additionally use teacher-forced cross-attention word alignment of the exact supplied text, with per-window probability diagnostics in `alignment/refinements.json`. These forced tokens do not inflate the independent ASR agreement metric. Optional re-transcription/refinement requires `faster-whisper`; rendering does not.

For another language episode, create another directory, preserve both supplied inputs and their hashes, review its paragraph correspondence and on-screen translations, align its own audio, then rebuild, preview and verify. Do not replace this episode's audio without retiming.

## Visual policy

Approved light studio composition, real cutout photographs, comparisons, archival selections, section transitions and the closing viewer question are preserved. Hindi typography uses RAQM-shaped Devanagari and licensed merged Noto fonts; model designations remain Latin. Photographs stay locked. Cards enter once and hold. Native M4A1/M249 360° banks rotate at 15°/s, a full turn in 24 seconds.

Archives use the original selected source intervals at normal speed and retain original source marks. When the Hindi clause runs longer, the last source frame is held rather than replaying or slowing the archive; the QA report separately counts moving footage and held tails. Source episode 1 already contains nearby excerpts of the same source; this adaptation preserves those selections rather than claiming the spacing rules of later episodes.

## Sources and licensing

See `SOURCES.md`, `assets/rights-manifest.json`, `assets/archive-manifest.json`, `assets/photo_provenance`, and the original source notes in `inputs/`. Attribution and license terms remain attached to the source files. Chinese news excerpts are contextual editorial quotations, **not unrestricted public-domain stock**. The Hindi adaptation preserves the same selected reporting excerpts and source identification.

M4A1: nisu/OpenGameArt, CC0. The converted M4A1 mesh, base-color texture and source page are included; `tools/software_turntable.py` can regenerate its native bank with optional `numba`. M249: NoBE Aubé/Blendkit Royalty Free; the source package contains the rendered video bank, not redistributable raw geometry. The production renderer accepts those prepared video banks directly. Photographs and their source originals/provenance are included under their recorded licenses. Noto fonts and modifications retain the SIL Open Font License in `fonts/`.

## Verification scope

`output/qa/` records plan checks, full export decode, actual audio correlation, static-photo/card checks, sampled encoded-frame review, and a fresh source ZIP reconstruction. These are separate checks. A continuous human watch/listen is not claimed. `INPUTS.json` records SHA-256 of the exact user inputs. Metadata is prepared for the separate Hindi channel; this package does not publish to YouTube.
