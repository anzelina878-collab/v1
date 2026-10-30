#!/usr/bin/env python3
"""Transcribe supplied speech; preserve original audio and authored script."""
import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('audio', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--model', default='small')
    parser.add_argument('--language', default='ru')
    parser.add_argument('--threads', type=int, default=4)
    args = parser.parse_args()
    if not args.audio.is_file():
        parser.error('Audio input does not exist')
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    outputs = [out / name for name in ['recognition.json', 'recognition.srt']]
    if any(p.exists() for p in outputs):
        parser.error('Recognition outputs already exist; choose a new output directory')
    from faster_whisper import WhisperModel
    model = WhisperModel(args.model, device='cpu', compute_type='int8',
                         cpu_threads=args.threads, download_root='/workspace/media-models')
    segments, info = model.transcribe(str(args.audio), language=args.language,
                                     beam_size=5, word_timestamps=True, vad_filter=True)
    rows = []
    for segment in segments:
        rows.append({'id': segment.id, 'start': segment.start, 'end': segment.end,
                     'text': segment.text, 'avg_logprob': segment.avg_logprob,
                     'no_speech_prob': segment.no_speech_prob,
                     'words': [{'start': w.start, 'end': w.end, 'word': w.word,
                                'probability': w.probability} for w in (segment.words or [])]})
        print(f'{segment.end:.1f}s / {info.duration:.1f}s', flush=True)
    if not rows:
        raise RuntimeError('No speech recognized; no success claimed')
    def stamp(seconds):
        ms = round(seconds * 1000)
        return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    data = {'status': 'machine_transcript_requires_review', 'model': args.model,
            'language': info.language, 'duration': info.duration, 'segments': rows}
    payloads = [json.dumps(data, ensure_ascii=False, indent=2) + '\n',
                '\n'.join(f"{i}\n{stamp(row['start'])} --> {stamp(row['end'])}\n{row['text'].strip()}\n"
                          for i, row in enumerate(rows, 1))]
    for target, payload in zip(outputs, payloads):
        tmp = target.with_suffix(target.suffix + '.tmp')
        tmp.write_text(payload, encoding='utf-8')
        os.replace(tmp, target)
    print('Machine transcription saved. Verify against the authored script before editing.')


if __name__ == '__main__':
    main()
