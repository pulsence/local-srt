# local_srt

Root package. Exposes the public API via lazy loading so consumers pay no import cost for unused modules.

## Modules

| Module | Description |
| --- | --- |
| `__init__.py` | Lazy-loading `__getattr__` for all public exports |
| `__main__.py` | Enables `python -m local_srt` entry point |
| `api.py` | Public library API — `transcribe_file`, `transcribe_batch`, `load_model` |
| `cli.py` | `srtgen` CLI command — argparse, batch orchestration, event display |
| `core.py` | Internal transcription pipeline orchestration |
| `models.py` | `ResolvedConfig`, `SubtitleBlock`, `WordItem` dataclasses |
| `config.py` | `PRESETS`, `MODE_ALIASES`, `load_config_file`, `apply_overrides` |
| `events.py` | `EventEmitter`, `BaseEvent` subclasses, `EventLevel` |
| `batch.py` | `expand_inputs`, `default_output_for`, `preflight_one`, `iter_media_files_in_dir` |
| `audio.py` | `to_wav_16k_mono`, `detect_silences` |
| `subtitle_generation.py` | `chunk_segments_to_subtitles`, `chunk_words_to_subtitles`, `apply_silence_alignment`, `hygiene_and_polish` |
| `text_processing.py` | `normalize_spaces`, `wrap_text_lines`, `split_text_into_blocks`, `distribute_time` |
| `output_writers.py` | `write_srt`, `write_vtt`, `write_ass`, `write_txt`, `write_json_bundle` |
| `system.py` | `ffmpeg_ok`, `ffprobe_ok`, `run_cmd_text`, `probe_duration_seconds` |
| `whisper_wrapper.py` | `init_whisper_model_internal` — device selection, compute-type selection |
| `model_management.py` | `list_downloaded_models`, `download_model`, `delete_model`, `diagnose` |
| `logging_utils.py` | `format_duration` formatting helper |
| `configs/` | Example config files (`yt_config.json`, `podcast_config.json`) |

## Public Exports

Accessed via `from local_srt import ...`:

- **API functions:** `transcribe_file`, `transcribe_batch`, `load_model`
- **Result types:** `TranscriptionResult`, `BatchResult`
- **Models:** `ResolvedConfig`, `SubtitleBlock`, `WordItem`
- **Events:** `EventEmitter`, `LogEvent`, `WarnEvent`, `ErrorEvent`, `ProgressEvent`, `StageEvent`, `FileStartEvent`, `FileCompleteEvent`, `ModelLoadEvent`, `EventLevel`
- **Config:** `load_config_file`, `apply_overrides`, `PRESETS`, `MODE_ALIASES`

## Lazy Loading

`__init__.py` uses `__getattr__` to defer module imports until first access. This keeps CLI startup time low when only a subset of the library is used.
