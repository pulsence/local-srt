# Transcription Pipeline

End-to-end data flow from raw media file to subtitle output.

## Stages

```text
Input File
    │
    ▼  Stage 1: Audio Extraction
ffmpeg → temp WAV (16kHz, mono, PCM)
    │
    ▼  Stage 2: Silence Detection (optional)
ffmpeg silencedetect → list[(start_s, end_s)]
    │
    ▼  Stage 3: Speech Recognition
faster-whisper.transcribe(wav, vad_filter=True, ...)
    → list of Segment(text, start, end, [words])
    │
    ▼  Stage 4: Word Extraction (word_timestamps only)
collect_words(segments) → list[WordItem]
    │
    ▼  Stage 5: Chunking
if word_timestamps:
    words_to_subtitles(words, cfg)
else:
    chunk_segments_to_subtitles(segments, cfg)
    → list[SubtitleBlock]
    │
    ▼  Stage 6: Silence Alignment (optional)
apply_silence_alignment(subtitles, silences, cfg)
    → list[SubtitleBlock] (adjusted boundaries)
    │
    ▼  Stage 7: Polish
hygiene_and_polish(subtitles, cfg)
    → list[SubtitleBlock] (gaps enforced, padding applied)
    │
    ▼  Stage 8: Output Writing
write_srt / write_vtt / write_ass / write_txt / write_json_bundle
    → Output file
    │
    ▼
TranscriptionResult(success, subtitles, segments, device_used, ...)
```

## Stage Details

### Stage 1: Audio Extraction

`audio.to_wav_16k_mono()` calls ffmpeg to transcode the input to a 16kHz, mono, 16-bit PCM WAV file in a temporary directory. faster-whisper requires WAV input; this handles any ffmpeg-supported format (MP3, MP4, MKV, M4A, FLAC, etc.).

### Stage 2: Silence Detection

If `cfg.use_silence_split=True`, `audio.detect_silences()` runs ffmpeg's `silencedetect` filter on the WAV file. Silence regions shorter than `cfg.silence_min_dur` or above `cfg.silence_threshold_db` are excluded. Overlapping regions are merged. The result is used later in Stage 6.

### Stage 3: Speech Recognition

`faster_whisper.WhisperModel.transcribe()` is called with:

- `vad_filter=cfg.vad_filter` — skips non-speech regions
- `word_timestamps=cfg.word_timestamps` — enables per-word timing
- `language=language` if specified

Returns an iterable of segment objects with `.text`, `.start`, `.end`, and optionally `.words`.

### Stage 4: Word Extraction

Only runs when `cfg.word_timestamps=True`. `collect_words()` iterates segment words and builds a `list[WordItem]` with per-word `(word, start, end)`.

### Stage 5: Chunking

Two paths depending on `cfg.word_timestamps`:

**Segment-level** (`chunk_segments_to_subtitles`):

- Groups consecutive segments until `max_chars × max_lines` would be exceeded or `max_dur` is reached
- Splits on punctuation hierarchy: strong → medium → weak (space)
- Produces `SubtitleBlock(start, end, lines)` from segment timing

**Word-level** (`words_to_subtitles`):

- Builds blocks word by word
- Timing distributed proportionally via `distribute_time()`
- Respects same character and duration limits

### Stage 6: Silence Alignment

`apply_silence_alignment()` scans detected silence regions near subtitle boundaries and nudges start/end times to fall within silence gaps. This produces visually cleaner cuts — subtitles appear and disappear during natural pauses.

### Stage 7: Polish

`hygiene_and_polish()` performs final cleanup:

- Enforces `cfg.min_gap` between consecutive cues
- Adds `cfg.pad` seconds of offset
- Clamps all durations to `[min_dur, max_dur]`

### Stage 8: Output Writing

`output_writers` provides one writer per format. All writers accept `list[SubtitleBlock]` and a `Path`. TXT uses raw whisper segments instead (no subtitle blocks).

## Error Handling

- ffmpeg unavailability → raises immediately (checked at start of `core.py`)
- Transcription errors → caught, set `TranscriptionResult.success=False`, `error` field populated
- Batch errors → `continue_on_error=True` skips failed files; `False` raises immediately
