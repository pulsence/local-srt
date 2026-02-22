# local_srt.core

Internal transcription orchestration. Not part of the public API — called by `api.py`.

## Key Function

### `transcribe_file_internal`

Executes the full transcription pipeline for a single file:

1. Validate ffmpeg availability
2. Convert input to 16kHz mono WAV (temp file)
3. Probe media duration via ffprobe
4. Detect silence regions (if `use_silence_split=True`)
5. Run faster-whisper transcription with `vad_filter`
6. Collect word-level timing (if `word_timestamps=True`)
7. Chunk segments into subtitle blocks
8. Apply silence alignment
9. Polish timing (min_gap enforcement, padding)
10. Write output in the selected format
11. Return `CoreTranscriptionResult`

## `CoreTranscriptionResult`

Internal result type used by `core.py` before wrapping in the public `TranscriptionResult`.

| Field | Description |
| --- | --- |
| `subtitles` | Final `SubtitleBlock` list |
| `segments` | Raw whisper segment objects |
| `device_used` | Actual device string |
| `compute_type_used` | Actual compute type string |

## Temp File Management

Core creates a temporary directory for the intermediate WAV file and cleans it up after writing output, even on error.
